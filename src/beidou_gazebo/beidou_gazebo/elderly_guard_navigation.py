"""Guard navigation gated by the single navigation-control handoff."""

from copy import deepcopy
import math

from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid
from nav2_msgs.action import NavigateToPose
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String
from tf2_ros import Buffer, TransformException, TransformListener
from visualization_msgs.msg import Marker, MarkerArray


STATE_SAFE = 'SAFE'
STATE_ALERT = 'ALERT'
STATE_NAVIGATING = 'NAVIGATING'
STATE_GUARDING = 'GUARDING'
STATE_NAVIGATION_FAILED = 'NAVIGATION_FAILED'


def is_out_of_bounds_transition(previous_safe, current_safe):
    return previous_safe is True and current_safe is False


class GuardStateMachine:
    """Backward-compatible pure state helper used by existing tests."""
    def __init__(self):
        self.state = STATE_SAFE
        self.elderly_safe = None

    def update_geofence(self, safe):
        previous = self.elderly_safe
        self.elderly_safe = bool(safe)
        if safe:
            self.state = STATE_SAFE
            return False
        if previous is True:
            self.state = STATE_ALERT
            return True
        if previous is None:
            self.state = STATE_ALERT
        return False

    def goal_accepted(self):
        if self.elderly_safe is False:
            self.state = STATE_NAVIGATING

    def goal_succeeded(self):
        self.state = STATE_GUARDING if self.elderly_safe is False else STATE_SAFE

    def goal_failed(self):
        self.state = STATE_NAVIGATION_FAILED if self.elderly_safe is False else STATE_SAFE


STATE_TEXT = {
    STATE_SAFE: 'STATUS: SAFE',
    STATE_ALERT: 'WARNING: ELDERLY OUT OF BOUNDS',
    STATE_NAVIGATING: 'STATUS: ROBOT NAVIGATING',
    STATE_GUARDING: 'STATUS: GUARDING ELDERLY',
    STATE_NAVIGATION_FAILED: 'STATUS: NAVIGATION FAILED',
}


def calculate_guard_goal(robot_x, robot_y, elderly_x, elderly_y, distance):
    """Place a guard goal near the elderly person, on the robot side."""
    delta_x = robot_x - elderly_x
    delta_y = robot_y - elderly_y
    separation = math.hypot(delta_x, delta_y)
    if separation < 1e-6:
        unit_x, unit_y = -1.0, 0.0
    else:
        unit_x = delta_x / separation
        unit_y = delta_y / separation
    goal_x = elderly_x + distance * unit_x
    goal_y = elderly_y + distance * unit_y
    yaw = math.atan2(elderly_y - goal_y, elderly_x - goal_x)
    return goal_x, goal_y, yaw


class ElderlyGuardNavigation(Node):
    """Send guarded Nav2 goals only while the handoff mode is GUARD."""

    def __init__(self):
        super().__init__('elderly_guard_navigation')
        for name, value in (
            ('guard_distance', 1.2), ('map_frame', 'map'),
            ('robot_frame', 'base_link'), ('action_name', '/navigate_to_pose'),
            ('robot_radius', 0.35), ('obstacle_threshold', 50),
        ):
            self.declare_parameter(name, value)
        self.guard_distance = float(self.get_parameter('guard_distance').value)
        self.map_frame = str(self.get_parameter('map_frame').value)
        self.robot_frame = str(self.get_parameter('robot_frame').value)
        self.action_name = str(self.get_parameter('action_name').value)
        self.robot_radius = float(self.get_parameter('robot_radius').value)
        self.obstacle_threshold = int(self.get_parameter('obstacle_threshold').value)
        if not 1.0 <= self.guard_distance <= 1.5:
            raise ValueError('guard_distance must be between 1.0 and 1.5 m')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.navigation_client = ActionClient(self, NavigateToPose, self.action_name)
        durable = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                             durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.marker_pub = self.create_publisher(MarkerArray, '/elderly_guard_markers', durable)
        self.visualization_pub = self.create_publisher(MarkerArray, '/elderly_guard_visualization', durable)
        self.state_pub = self.create_publisher(String, '/elderly_guard_state', durable)
        self.handoff_pub = self.create_publisher(String, '/elderly_guard_handoff_state', durable)
        self.create_subscription(PoseStamped, '/elderly_position', self._position_callback, 10)
        self.create_subscription(String, '/elderly_geofence_state', self._geofence_callback, durable)
        self.create_subscription(String, '/elderly_navigation_mode', self._mode_callback, durable)
        self.create_subscription(OccupancyGrid, '/map', self._map_callback, 10)

        self.latest_elderly_pose = None
        self.latest_geofence_state = 'UNKNOWN'
        self.guard_state = STATE_SAFE
        self.navigation_mode = 'FOLLOW'
        self.map_msg = None
        self.guard_goal_pose = None
        self.pending_navigation = False
        self.navigation_in_progress = False
        self.goal_pending = False
        self.goal_handle = None
        self.release_requested = False
        self.guard_goal_issued = False
        self.cancel_pending = False
        self.last_published_state = None
        self.last_handoff_state = None
        self.wait_reason = None
        self.create_timer(0.2, self._try_send_navigation_goal)
        self.create_timer(1.0, self._publish_visualization)
        self._publish_guard_state(force=True)
        self._publish_handoff_state('IDLE')

    def _position_callback(self, message):
        self.latest_elderly_pose = message
        self._publish_visualization()

    def _map_callback(self, message):
        self.map_msg = message

    def _geofence_callback(self, message):
        self.latest_geofence_state = str(message.data).strip().upper()
        if (self.navigation_mode == 'GUARD' and
                self.latest_geofence_state in ('DANGER', 'WARNING') and
                not self.guard_goal_issued and
                not self.navigation_in_progress and not self.goal_pending):
            self.pending_navigation = True
            self._publish_guard_state(force=True)

    def _mode_callback(self, message):
        mode = str(message.data).strip().upper()
        if mode not in ('FOLLOW', 'TRANSITION', 'GUARD', 'RETURN_TO_FOLLOW'):
            return
        if mode == self.navigation_mode:
            return
        self.navigation_mode = mode
        if mode == 'GUARD':
            self.release_requested = False
            self.cancel_pending = False
            self.guard_goal_issued = False
            self._publish_handoff_state('READY')
            if (self.latest_geofence_state in ('DANGER', 'WARNING') and
                    self.latest_elderly_pose is not None):
                self.pending_navigation = True
        elif mode == 'RETURN_TO_FOLLOW':
            self.pending_navigation = False
            self.release_requested = True
            self._publish_guard_state(force=True)
            self._cancel_goal_if_needed()
        else:
            self.pending_navigation = False
        self._publish_visualization()

    def _cancel_goal_if_needed(self):
        if self.goal_handle is not None and not self.cancel_pending:
            self.cancel_pending = True
            try:
                future = self.goal_handle.cancel_goal_async()
                future.add_done_callback(self._cancel_response)
            except Exception as error:
                self.get_logger().warning(f'[GUARD] cancel request failed: {error}')
        elif self.goal_handle is None and not self.goal_pending:
            self._publish_handoff_state('RELEASED')

    def _cancel_response(self, future):
        try:
            future.result()
        except Exception as error:
            self.get_logger().warning(f'[GUARD] cancel response failed: {error}')
        if self.goal_handle is None and not self.goal_pending:
            self._publish_handoff_state('RELEASED')

    def _try_send_navigation_goal(self):
        if (self.navigation_mode != 'GUARD' or self.release_requested or
                not self.pending_navigation or self.navigation_in_progress or
                self.goal_pending):
            return
        if self.latest_elderly_pose is None:
            return self._log_wait_once('waiting for elderly position')
        if self.latest_elderly_pose.header.frame_id != self.map_frame:
            return self._log_wait_once('elderly position frame mismatch')
        if not self.navigation_client.server_is_ready():
            return self._log_wait_once('waiting for Nav2 NavigateToPose')
        try:
            transform = self.tf_buffer.lookup_transform(
                self.map_frame, self.robot_frame, rclpy.time.Time())
        except TransformException as error:
            return self._log_wait_once(f'waiting for robot TF: {error}')
        elderly = self.latest_elderly_pose.pose.position
        robot_x = transform.transform.translation.x
        robot_y = transform.transform.translation.y
        candidates = self._guard_candidates(robot_x, robot_y, elderly.x, elderly.y)
        selected = next((candidate for candidate in candidates
                         if self._goal_is_safe(candidate[0], candidate[1])), None)
        if selected is None:
            return self._log_wait_once('no feasible guard goal in map')
        goal_x, goal_y, yaw = selected
        self.guard_goal_pose = self._make_goal_pose(goal_x, goal_y, yaw)
        goal = NavigateToPose.Goal()
        goal.pose = self.guard_goal_pose
        self.pending_navigation = False
        self.guard_goal_issued = True
        self.goal_pending = True
        self._publish_handoff_state('READY')
        try:
            future = self.navigation_client.send_goal_async(goal)
            future.add_done_callback(self._goal_response_callback)
        except Exception as error:
            self.goal_pending = False
            self._navigation_failed(str(error))

    def _guard_candidates(self, robot_x, robot_y, elderly_x, elderly_y):
        base = calculate_guard_goal(robot_x, robot_y, elderly_x, elderly_y, self.guard_distance)
        dx, dy = robot_x - elderly_x, robot_y - elderly_y
        separation = math.hypot(dx, dy) or 1.0
        ux, uy = dx / separation, dy / separation
        lx, ly = -uy, ux
        points = [(base[0], base[1], base[2]),
                  (elderly_x + self.guard_distance * lx,
                   elderly_y + self.guard_distance * ly,
                   math.atan2(-ly, -lx)),
                  (elderly_x - self.guard_distance * lx,
                   elderly_y - self.guard_distance * ly,
                   math.atan2(ly, lx)),
                  (elderly_x - self.guard_distance * ux,
                   elderly_y - self.guard_distance * uy,
                   math.atan2(uy, ux))]
        return points

    def _goal_is_safe(self, x, y):
        if not (math.isfinite(x) and math.isfinite(y)):
            return False
        if self.map_msg is None:
            # Nav2 remains the final planner/check; without a map don't invent
            # a conflicting goal, but allow operation in map-less test setups.
            return True
        info = self.map_msg.info
        if info.width <= 0 or info.height <= 0 or info.resolution <= 0:
            return False
        radius_cells = max(0, int(math.ceil(self.robot_radius / info.resolution)))
        cx = int(math.floor((x - info.origin.position.x) / info.resolution))
        cy = int(math.floor((y - info.origin.position.y) / info.resolution))
        for ix in range(cx - radius_cells, cx + radius_cells + 1):
            for iy in range(cy - radius_cells, cy + radius_cells + 1):
                if ix < 0 or iy < 0 or ix >= info.width or iy >= info.height:
                    return False
                if math.hypot(ix - cx, iy - cy) * info.resolution > self.robot_radius:
                    continue
                value = self.map_msg.data[iy * info.width + ix]
                if value < 0 or value >= self.obstacle_threshold:
                    return False
        return True

    def _goal_response_callback(self, future):
        self.goal_pending = False
        try:
            handle = future.result()
        except Exception as error:
            return self._navigation_failed(str(error))
        if not handle.accepted:
            return self._navigation_failed('goal was rejected by Nav2')
        self.goal_handle = handle
        self.navigation_in_progress = True
        self._publish_guard_state(force=True)
        self._publish_handoff_state('GOAL_SENT')
        if self.navigation_mode != 'GUARD' or self.release_requested:
            self._cancel_goal_if_needed()
        result_future = handle.get_result_async()
        result_future.add_done_callback(self._result_callback)

    def _result_callback(self, future):
        try:
            result = future.result()
        except Exception as error:
            return self._navigation_failed(str(error))
        self.navigation_in_progress = False
        self.goal_handle = None
        self.cancel_pending = False
        if self.release_requested or self.navigation_mode == 'RETURN_TO_FOLLOW':
            self._publish_handoff_state('RELEASED')
            self._publish_guard_state(force=True)
            return
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self._set_guard_state(STATE_GUARDING)
            self._publish_handoff_state('GUARDING')
        else:
            detail = getattr(result.result, 'error_msg', '') or f'action status={result.status}'
            self._navigation_failed(detail)

    def _navigation_failed(self, detail):
        self.goal_pending = False
        self.navigation_in_progress = False
        self.goal_handle = None
        self.cancel_pending = False
        self._set_guard_state(STATE_NAVIGATION_FAILED)
        self._publish_handoff_state('FAILED')
        self.get_logger().error(f'[GUARD] Navigation failed: {detail}')

    def _set_guard_state(self, state):
        self.guard_state = state
        if state != self.last_published_state:
            self.state_pub.publish(String(data=state))
            self.last_published_state = state

    def _publish_guard_state(self, force=False):
        state = (STATE_NAVIGATING if self.navigation_in_progress else
                 self.guard_state if self.navigation_mode == 'GUARD' else STATE_SAFE)
        if force or state != self.last_published_state:
            self.state_pub.publish(String(data=state))
            self.last_published_state = state

    def _publish_handoff_state(self, state):
        if state != self.last_handoff_state:
            self.handoff_pub.publish(String(data=state))
            self.last_handoff_state = state

    def _log_wait_once(self, reason):
        if reason != self.wait_reason:
            self.get_logger().info(f'[GUARD] {reason}')
            self.wait_reason = reason

    def _make_goal_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = self.map_frame
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)
        return pose

    def _publish_visualization(self):
        self._publish_guard_state(force=True)
        if self.latest_elderly_pose is None:
            return
        stamp = self.get_clock().now().to_msg()
        elderly_marker = Marker()
        elderly_marker.header.frame_id = self.map_frame
        elderly_marker.header.stamp = stamp
        elderly_marker.ns = 'elderly_guard'
        elderly_marker.id = 0
        elderly_marker.type = Marker.SPHERE
        elderly_marker.action = Marker.ADD
        elderly_marker.pose = deepcopy(self.latest_elderly_pose.pose)
        elderly_marker.pose.position.z = 0.6
        elderly_marker.scale.x = elderly_marker.scale.y = elderly_marker.scale.z = 0.6
        elderly_marker.color.g = 1.0 if self.latest_geofence_state == 'SAFE' else 0.0
        elderly_marker.color.r = 0.0 if self.latest_geofence_state == 'SAFE' else 1.0
        elderly_marker.color.a = 1.0
        markers = [elderly_marker]
        if self.guard_goal_pose is not None:
            goal_marker = Marker()
            goal_marker.header.frame_id = self.map_frame
            goal_marker.header.stamp = stamp
            goal_marker.ns = 'elderly_guard'
            goal_marker.id = 1
            goal_marker.type = Marker.ARROW
            goal_marker.action = Marker.ADD
            goal_marker.pose = deepcopy(self.guard_goal_pose.pose)
            goal_marker.pose.position.z = 0.35
            goal_marker.scale.x = 0.9
            goal_marker.scale.y = goal_marker.scale.z = 0.3
            goal_marker.color.g = goal_marker.color.b = goal_marker.color.a = 1.0
            markers.append(goal_marker)
        text = Marker()
        text.header.frame_id = self.map_frame
        text.header.stamp = stamp
        text.ns = 'elderly_guard'
        text.id = 2
        text.type = Marker.TEXT_VIEW_FACING
        text.action = Marker.ADD
        text.pose.position.x = self.latest_elderly_pose.pose.position.x
        text.pose.position.y = self.latest_elderly_pose.pose.position.y
        text.pose.position.z = 1.8
        text.pose.orientation.w = 1.0
        text.scale.z = 0.6
        text.color.a = 1.0
        text.text = STATE_TEXT.get(self.last_published_state, 'STATUS: SAFE')
        markers.append(text)
        message = MarkerArray(markers=markers)
        self.marker_pub.publish(message)
        self.visualization_pub.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = ElderlyGuardNavigation()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
