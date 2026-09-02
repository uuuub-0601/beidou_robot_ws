"""Keep the robot near the elderly person while the geofence is safe."""

from copy import deepcopy
import math

from action_msgs.msg import GoalStatus, GoalStatusArray
from geometry_msgs.msg import Point, PoseStamped
from nav2_msgs.action import NavigateToPose
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    qos_profile_action_status_default,
    QoSProfile,
    ReliabilityPolicy,
)
from std_msgs.msg import Bool, String
from tf2_ros import Buffer, TransformException, TransformListener
from visualization_msgs.msg import Marker, MarkerArray


MODE_COMPANION = 'COMPANION MODE'
MODE_IDLE = 'IDLE'
MODE_PAUSED = 'PAUSED - OUT OF BOUNDS'

ACTIVE_ACTION_STATUSES = {
    GoalStatus.STATUS_ACCEPTED,
    GoalStatus.STATUS_EXECUTING,
    GoalStatus.STATUS_CANCELING,
}


def calculate_companion_goal(
    robot_x,
    robot_y,
    elderly_x,
    elderly_y,
    companion_distance,
):
    """Return a goal on the robot side that faces the elderly person."""
    delta_x = robot_x - elderly_x
    delta_y = robot_y - elderly_y
    separation = math.hypot(delta_x, delta_y)
    if separation < 1e-6:
        unit_x, unit_y = -1.0, 0.0
    else:
        unit_x = delta_x / separation
        unit_y = delta_y / separation

    goal_x = elderly_x + companion_distance * unit_x
    goal_y = elderly_y + companion_distance * unit_y
    yaw = math.atan2(elderly_y - goal_y, elderly_x - goal_x)
    return goal_x, goal_y, yaw


def companion_replan_reason(
    robot_x,
    robot_y,
    elderly_x,
    elderly_y,
    companion_distance,
    distance_tolerance,
    replan_distance,
    last_goal_elderly_position,
    navigation_active,
):
    """Explain why a companion goal is needed, or return None."""
    if navigation_active and last_goal_elderly_position is not None:
        moved = math.hypot(
            elderly_x - last_goal_elderly_position[0],
            elderly_y - last_goal_elderly_position[1],
        )
        if moved >= replan_distance:
            return 'elderly moved beyond replan threshold'
        return None

    actual_distance = math.hypot(
        robot_x - elderly_x,
        robot_y - elderly_y,
    )
    distance_deviation = abs(actual_distance - companion_distance)
    if distance_deviation >= distance_tolerance:
        return 'companion distance deviation'
    return None


def goal_uuid(goal_info):
    """Convert a ROS goal UUID to a hashable byte sequence."""
    return bytes(goal_info.goal_id.uuid)


class ElderlyCompanionNavigation(Node):
    """Send rate-limited Nav2 companion goals only inside the geofence."""

    def __init__(self):
        """Initialize subscriptions, Nav2 client, and control timers."""
        super().__init__('elderly_companion_navigation')
        parameters = (
            ('companion_distance', 1.5),
            ('replan_distance', 0.8),
            ('distance_tolerance', 0.5),
            ('minimum_goal_interval', 3.0),
            ('safe_recovery_delay', 3.0),
            ('guard_handoff_delay', 1.0),
            ('control_frequency', 2.0),
            ('map_frame', 'map'),
            ('robot_frame', 'base_link'),
            ('action_name', '/navigate_to_pose'),
        )
        for name, default in parameters:
            self.declare_parameter(name, default)

        self.companion_distance = float(
            self.get_parameter('companion_distance').value
        )
        self.replan_distance = float(
            self.get_parameter('replan_distance').value
        )
        self.distance_tolerance = float(
            self.get_parameter('distance_tolerance').value
        )
        self.minimum_goal_interval = float(
            self.get_parameter('minimum_goal_interval').value
        )
        self.safe_recovery_delay = float(
            self.get_parameter('safe_recovery_delay').value
        )
        self.guard_handoff_delay = float(
            self.get_parameter('guard_handoff_delay').value
        )
        control_frequency = float(
            self.get_parameter('control_frequency').value
        )
        self.map_frame = str(self.get_parameter('map_frame').value)
        self.robot_frame = str(self.get_parameter('robot_frame').value)
        self.action_name = str(self.get_parameter('action_name').value)
        self._validate_parameters(control_frequency)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.navigation_client = ActionClient(
            self,
            NavigateToPose,
            self.action_name,
        )

        durable_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.visualization_pub = self.create_publisher(
            MarkerArray,
            '/elderly_companion_visualization',
            durable_qos,
        )
        self.state_pub = self.create_publisher(
            String,
            '/elderly_companion_state',
            durable_qos,
        )
        self.create_subscription(
            PoseStamped,
            '/elderly_position',
            self._position_callback,
            10,
        )
        self.create_subscription(
            Bool,
            '/elderly_geofence_status',
            self._geofence_callback,
            10,
        )
        status_topic = self.action_name.rstrip('/') + '/_action/status'
        self.create_subscription(
            GoalStatusArray,
            status_topic,
            self._action_status_callback,
            qos_profile_action_status_default,
        )

        self.latest_elderly_pose = None
        self.elderly_safe = None
        self.safe_since = None
        self.out_of_bounds_since = None
        self.last_goal_time = None
        self.last_goal_elderly_position = None
        self.companion_goal_pose = None
        self.goal_sequence = 0
        self.pending_goal_generation = None
        self.current_goal_generation = None
        self.current_goal_handle = None
        self.cancel_requested_generations = set()
        self.owned_goal_ids = set()
        self.external_active_goal_ids = set()
        self.navigation_active = False
        self.mode = MODE_IDLE
        self.last_wait_reason = None
        self.last_published_mode = None

        self.create_timer(
            1.0 / control_frequency,
            self._control_tick,
        )
        self.create_timer(1.0, self._publish_visualization)
        self._publish_mode(force=True)

    def _validate_parameters(self, control_frequency):
        if not 1.0 <= self.companion_distance <= 2.5:
            raise ValueError(
                'companion_distance must be between 1.0 and 2.5 m'
            )
        positive_parameters = {
            'replan_distance': self.replan_distance,
            'distance_tolerance': self.distance_tolerance,
            'minimum_goal_interval': self.minimum_goal_interval,
            'safe_recovery_delay': self.safe_recovery_delay,
            'guard_handoff_delay': self.guard_handoff_delay,
            'control_frequency': control_frequency,
        }
        invalid = [
            name
            for name, value in positive_parameters.items()
            if value <= 0.0
        ]
        if invalid:
            names = ', '.join(invalid)
            raise ValueError(f'parameters must be positive: {names}')

    def _position_callback(self, message):
        self.latest_elderly_pose = message

    def _geofence_callback(self, message):
        safe = bool(message.data)
        previous_safe = self.elderly_safe
        self.elderly_safe = safe
        if safe:
            self.out_of_bounds_since = None
            if previous_safe is not True:
                self.safe_since = self.get_clock().now()
                self._set_mode(MODE_IDLE)
                self.get_logger().info(
                    '[COMPANION] SAFE received; waiting for stability'
                )
        else:
            self.safe_since = None
            if previous_safe is not False:
                self.out_of_bounds_since = self.get_clock().now()
            self.companion_goal_pose = None
            self._set_mode(MODE_PAUSED)
            if previous_safe is not False:
                self.get_logger().warning(
                    '[COMPANION] OUT_OF_BOUNDS; yielding to Guard'
                )
        self._publish_visualization()

    def _action_status_callback(self, message):
        active_ids = {
            goal_uuid(status.goal_info)
            for status in message.status_list
            if status.status in ACTIVE_ACTION_STATUSES
        }
        self.external_active_goal_ids = active_ids - self.owned_goal_ids
        if (
            self.external_active_goal_ids
            and self.elderly_safe is True
            and self.current_goal_handle is not None
            and self.pending_goal_generation is None
        ):
            self._cancel_current_goal('external navigation goal is active')

    def _control_tick(self):
        if self.elderly_safe is not True:
            if self.elderly_safe is False:
                self._cancel_after_guard_handoff()
                return self._wait(
                    MODE_PAUSED,
                    'yielding navigation priority to Guard',
                )
            return self._wait(MODE_IDLE, 'geofence state is not available')
        if self.latest_elderly_pose is None:
            return self._wait(MODE_IDLE, 'waiting for elderly position')
        if self.latest_elderly_pose.header.frame_id != self.map_frame:
            return self._wait(
                MODE_IDLE,
                'elderly position is not in the map frame',
            )
        if not self._safe_is_stable():
            return self._wait(MODE_IDLE, 'waiting for SAFE stability')
        if self.external_active_goal_ids:
            return self._wait(
                MODE_IDLE,
                'waiting for external navigation goal to finish',
            )
        if self.pending_goal_generation is not None:
            return self._wait(MODE_COMPANION, 'goal request is pending')
        if not self.navigation_client.server_is_ready():
            return self._wait(MODE_IDLE, 'waiting for Nav2 NavigateToPose')

        try:
            transform = self.tf_buffer.lookup_transform(
                self.map_frame,
                self.robot_frame,
                rclpy.time.Time(),
            )
        except TransformException as error:
            return self._wait(MODE_IDLE, f'waiting for robot TF: {error}')

        robot_x = transform.transform.translation.x
        robot_y = transform.transform.translation.y
        elderly_x = self.latest_elderly_pose.pose.position.x
        elderly_y = self.latest_elderly_pose.pose.position.y
        reason = companion_replan_reason(
            robot_x,
            robot_y,
            elderly_x,
            elderly_y,
            self.companion_distance,
            self.distance_tolerance,
            self.replan_distance,
            self.last_goal_elderly_position,
            self.navigation_active,
        )
        if reason is None:
            mode = MODE_COMPANION if self.navigation_active else MODE_IDLE
            return self._wait(mode, 'companion distance is acceptable')
        if not self._minimum_interval_elapsed():
            mode = MODE_COMPANION if self.navigation_active else MODE_IDLE
            return self._wait(mode, 'minimum goal interval is active')

        goal_x, goal_y, yaw = calculate_companion_goal(
            robot_x,
            robot_y,
            elderly_x,
            elderly_y,
            self.companion_distance,
        )
        self.companion_goal_pose = self._make_goal_pose(
            goal_x,
            goal_y,
            yaw,
        )
        self._send_goal(reason, elderly_x, elderly_y)

    def _safe_is_stable(self):
        if self.safe_since is None:
            return False
        elapsed = self.get_clock().now() - self.safe_since
        return elapsed.nanoseconds >= int(self.safe_recovery_delay * 1e9)

    def _minimum_interval_elapsed(self):
        if self.last_goal_time is None:
            return True
        elapsed = self.get_clock().now() - self.last_goal_time
        return elapsed.nanoseconds >= int(self.minimum_goal_interval * 1e9)

    def _cancel_after_guard_handoff(self):
        if self.current_goal_handle is None:
            return
        if self.external_active_goal_ids:
            return
        if self.out_of_bounds_since is None:
            return
        elapsed = self.get_clock().now() - self.out_of_bounds_since
        if elapsed.nanoseconds < int(self.guard_handoff_delay * 1e9):
            return
        self._cancel_current_goal(
            'no Guard goal appeared during the handoff window'
        )

    def _send_goal(self, reason, elderly_x, elderly_y):
        goal = NavigateToPose.Goal()
        goal.pose = self.companion_goal_pose
        self.goal_sequence += 1
        generation = self.goal_sequence
        self.pending_goal_generation = generation
        self.last_goal_time = self.get_clock().now()
        self.last_goal_elderly_position = (elderly_x, elderly_y)
        self.last_wait_reason = None
        self._set_mode(MODE_COMPANION)
        self.get_logger().info(
            f'[COMPANION] Sending goal #{generation}: {reason}; '
            f'x={goal.pose.pose.position.x:.3f}, '
            f'y={goal.pose.pose.position.y:.3f}'
        )
        self._publish_visualization()
        try:
            future = self.navigation_client.send_goal_async(goal)
            future.add_done_callback(
                lambda done, value=generation: self._goal_response(
                    done,
                    value,
                )
            )
        except Exception as error:
            self.pending_goal_generation = None
            self.get_logger().error(
                f'[COMPANION] Failed to send goal: {error}'
            )

    def _goal_response(self, future, generation):
        if self.pending_goal_generation == generation:
            self.pending_goal_generation = None
        try:
            goal_handle = future.result()
        except Exception as error:
            self.get_logger().error(
                f'[COMPANION] Goal response failed: {error}'
            )
            return
        if not goal_handle.accepted:
            self.get_logger().warning(
                f'[COMPANION] Goal #{generation} was rejected'
            )
            return

        identifier = bytes(goal_handle.goal_id.uuid)
        self.owned_goal_ids.add(identifier)
        self.external_active_goal_ids.discard(identifier)
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda done, value=generation: self._goal_result(done, value)
        )

        if self.elderly_safe is not True:
            self.current_goal_generation = generation
            self.current_goal_handle = goal_handle
            self.navigation_active = True
            return

        self.current_goal_generation = generation
        self.current_goal_handle = goal_handle
        self.navigation_active = True
        self._set_mode(MODE_COMPANION)
        self.get_logger().info(
            f'[COMPANION] Goal #{generation} accepted by Nav2'
        )

    def _goal_result(self, future, generation):
        try:
            wrapped_result = future.result()
            status = wrapped_result.status
        except Exception as error:
            self.get_logger().error(
                f'[COMPANION] Goal #{generation} result failed: {error}'
            )
            status = GoalStatus.STATUS_UNKNOWN

        self.cancel_requested_generations.discard(generation)
        if generation != self.current_goal_generation:
            return
        self.current_goal_generation = None
        self.current_goal_handle = None
        self.navigation_active = False
        if self.elderly_safe is True:
            self._set_mode(MODE_IDLE)
        else:
            self._set_mode(MODE_PAUSED)
        self.get_logger().info(
            f'[COMPANION] Goal #{generation} finished with status={status}'
        )

    def _cancel_current_goal(self, reason):
        generation = self.current_goal_generation
        if self.current_goal_handle is None or generation is None:
            return
        if generation in self.cancel_requested_generations:
            return
        self.cancel_requested_generations.add(generation)
        self.get_logger().info(
            f'[COMPANION] Canceling goal #{generation}: {reason}'
        )
        future = self.current_goal_handle.cancel_goal_async()
        future.add_done_callback(
            lambda done, value=generation: self._cancel_response(
                done,
                value,
            )
        )

    def _cancel_response(self, future, generation):
        try:
            response = future.result()
            accepted = bool(response.goals_canceling)
        except Exception as error:
            self.get_logger().error(
                f'[COMPANION] Goal #{generation} cancel failed: {error}'
            )
            return
        if accepted:
            self.get_logger().info(
                f'[COMPANION] Goal #{generation} cancellation accepted'
            )
        else:
            self.get_logger().warning(
                f'[COMPANION] Goal #{generation} was no longer cancelable'
            )

    def _make_goal_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = self.map_frame
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)
        return pose

    def _wait(self, mode, reason):
        self._set_mode(mode)
        if reason != self.last_wait_reason:
            self.get_logger().info(f'[COMPANION] {reason}')
            self.last_wait_reason = reason

    def _set_mode(self, mode):
        if mode != self.mode:
            self.mode = mode
            self._publish_mode()

    def _publish_mode(self, force=False):
        if force or self.mode != self.last_published_mode:
            self.state_pub.publish(String(data=self.mode))
            self.last_published_mode = self.mode

    def _publish_visualization(self):
        self._publish_mode(force=True)
        stamp = self.get_clock().now().to_msg()
        markers = []
        elderly_x = elderly_y = None
        if self.latest_elderly_pose is not None:
            elderly_marker = Marker()
            elderly_marker.header.frame_id = self.map_frame
            elderly_marker.header.stamp = stamp
            elderly_marker.ns = 'elderly_companion'
            elderly_marker.id = 0
            elderly_marker.type = Marker.SPHERE
            elderly_marker.action = Marker.ADD
            elderly_marker.pose = deepcopy(self.latest_elderly_pose.pose)
            elderly_marker.pose.position.z = 0.65
            elderly_marker.scale.x = 0.55
            elderly_marker.scale.y = 0.55
            elderly_marker.scale.z = 0.55
            elderly_marker.color.g = 1.0 if self.elderly_safe else 0.2
            elderly_marker.color.r = 0.1 if self.elderly_safe else 1.0
            elderly_marker.color.a = 1.0
            markers.append(elderly_marker)
            elderly_x = self.latest_elderly_pose.pose.position.x
            elderly_y = self.latest_elderly_pose.pose.position.y

        markers.append(self._make_goal_marker(stamp))
        robot_point = self._robot_point()
        markers.append(
            self._make_relationship_marker(
                stamp,
                robot_point,
                elderly_x,
                elderly_y,
            )
        )
        markers.append(
            self._make_text_marker(
                stamp,
                robot_point,
                elderly_x,
                elderly_y,
            )
        )
        self.visualization_pub.publish(MarkerArray(markers=markers))

    def _make_goal_marker(self, stamp):
        marker = Marker()
        marker.header.frame_id = self.map_frame
        marker.header.stamp = stamp
        marker.ns = 'elderly_companion'
        marker.id = 1
        if self.companion_goal_pose is None:
            marker.action = Marker.DELETE
            return marker
        marker.type = Marker.ARROW
        marker.action = Marker.ADD
        marker.pose = deepcopy(self.companion_goal_pose.pose)
        marker.pose.position.z = 0.3
        marker.scale.x = 0.8
        marker.scale.y = 0.25
        marker.scale.z = 0.25
        marker.color.r = 0.1
        marker.color.g = 0.75
        marker.color.b = 1.0
        marker.color.a = 1.0
        return marker

    def _robot_point(self):
        try:
            transform = self.tf_buffer.lookup_transform(
                self.map_frame,
                self.robot_frame,
                rclpy.time.Time(),
            )
        except TransformException:
            return None
        return Point(
            x=transform.transform.translation.x,
            y=transform.transform.translation.y,
            z=0.35,
        )

    def _make_relationship_marker(
        self,
        stamp,
        robot_point,
        elderly_x,
        elderly_y,
    ):
        marker = Marker()
        marker.header.frame_id = self.map_frame
        marker.header.stamp = stamp
        marker.ns = 'elderly_companion'
        marker.id = 2
        if robot_point is None or elderly_x is None:
            marker.action = Marker.DELETE
            return marker
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.08
        marker.points = [
            robot_point,
            Point(x=elderly_x, y=elderly_y, z=0.35),
        ]
        marker.color.r = 0.2
        marker.color.g = 0.9
        marker.color.b = 0.8
        marker.color.a = 1.0
        return marker

    def _make_text_marker(
        self,
        stamp,
        robot_point,
        elderly_x,
        elderly_y,
    ):
        marker = Marker()
        marker.header.frame_id = self.map_frame
        marker.header.stamp = stamp
        marker.ns = 'elderly_companion'
        marker.id = 3
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD
        if elderly_x is not None:
            marker.pose.position.x = elderly_x
            marker.pose.position.y = elderly_y
        elif robot_point is not None:
            marker.pose.position.x = robot_point.x
            marker.pose.position.y = robot_point.y
        marker.pose.position.z = 1.8
        marker.pose.orientation.w = 1.0
        marker.scale.z = 0.5
        marker.color.a = 1.0
        marker.text = self.mode
        if self.mode == MODE_COMPANION:
            marker.color.g = 1.0
            marker.color.b = 0.7
        elif self.mode == MODE_PAUSED:
            marker.color.r = 1.0
            marker.color.g = 0.35
        else:
            marker.color.r = 1.0
            marker.color.g = 1.0
            marker.color.b = 1.0
        return marker


def main(args=None):
    """Run the elderly companion navigation node."""
    rclpy.init(args=args)
    node = ElderlyCompanionNavigation()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.destroy_node()
        except KeyboardInterrupt:
            pass
        if rclpy.ok():
            rclpy.shutdown()
