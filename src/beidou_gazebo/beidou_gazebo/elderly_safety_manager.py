"""Manage independent multi-elderly safety events without robot control."""

from dataclasses import dataclass
import math

from beidou_interfaces.msg import ElderlyEvent, ElderlyPositionArray, ElderlyRiskArray
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from tf2_ros import Buffer, TransformException, TransformListener

STATE_SAFE = 'SAFE'
STATE_WARNING = 'WARNING'
STATE_DANGER = 'DANGER'
STATE_UNKNOWN = 'UNKNOWN'

MANAGER_STANDBY = 'STANDBY'
MANAGER_MONITORING = 'MONITORING'
MANAGER_EVENT_SELECTED = 'EVENT_SELECTED'

EVENT_WARNING_ENTER = 'WARNING_ENTER'
EVENT_DANGER_ENTER = 'DANGER_ENTER'
EVENT_WARNING_EXIT = 'WARNING_EXIT'
EVENT_DANGER_EXIT = 'DANGER_EXIT'


@dataclass
class ElderlyEventState:
    """State and active hazard episode for one elderly ID."""

    state: str = STATE_UNKNOWN
    event_id: str = ''
    event_entry_state: str = ''
    event_counter: int = 0
    danger_entry_time: float = math.inf
    last_distance: float = math.nan
    elderly_x: float = math.nan
    elderly_y: float = math.nan
    position_valid: bool = False
    position_stamp: float = 0.0
    position_frame: str = ''
    robot_distance: float = math.inf


@dataclass(frozen=True)
class EventRecord:
    """A one-shot state transition event."""

    event_id: str
    elderly_id: str
    event_type: str
    priority: str
    state: str
    distance_to_danger: float
    stamp: float


class SafetyEventManager:
    """Convert risk edges into one-shot events and select one active target."""

    def __init__(self, elderly_ids, map_frame='map'):
        self.elderly_ids = tuple(dict.fromkeys(str(i) for i in elderly_ids))
        self.tracks = {i: ElderlyEventState() for i in self.elderly_ids}
        self.manager_state = MANAGER_STANDBY
        self.received_risks = False
        self.map_frame = str(map_frame)
        self.robot_x = math.nan
        self.robot_y = math.nan
        self.robot_pose_valid = False

    def update_position(self, elderly_id, x, y, stamp, valid=True,
                        frame_id='map'):
        self.ensure_id(elderly_id)
        if elderly_id:
            track = self.tracks[elderly_id]
            track.elderly_x = float(x)
            track.elderly_y = float(y)
            track.position_stamp = float(stamp)
            track.position_valid = bool(valid)
            track.position_frame = str(frame_id)

    def set_robot_pose(self, x, y, valid=True):
        self.robot_x, self.robot_y = float(x), float(y)
        self.robot_pose_valid = (
            bool(valid) and math.isfinite(self.robot_x)
            and math.isfinite(self.robot_y)
        )

    def robot_distance(self, elderly_id):
        track = self.tracks[elderly_id]
        if (not self.robot_pose_valid or not track.position_valid or
                track.position_frame != self.map_frame or
                not math.isfinite(track.elderly_x) or
                not math.isfinite(track.elderly_y)):
            return math.inf
        return math.hypot(track.elderly_x - self.robot_x,
                          track.elderly_y - self.robot_y)

    def ensure_id(self, elderly_id):
        if elderly_id and elderly_id not in self.tracks:
            self.tracks[elderly_id] = ElderlyEventState()
            self.elderly_ids += (elderly_id,)

    @staticmethod
    def _priority(state):
        if state == STATE_DANGER:
            return 'HIGH'
        if state == STATE_WARNING:
            return 'MEDIUM'
        return 'LOW'

    def _new_event_id(self, elderly_id, state, track):
        track.event_counter += 1
        track.event_entry_state = state
        return f'{elderly_id}-{state}-{track.event_counter:04d}'

    def process(self, risks, stamp):
        """Process one risk array; return only newly created edge events."""
        self.received_risks = True
        observed = set()
        events = []
        for risk in risks:
            elderly_id = str(risk['elderly_id'])
            if not elderly_id:
                continue
            self.ensure_id(elderly_id)
            observed.add(elderly_id)
            events.extend(self._transition(elderly_id, str(risk['state']),
                                           float(risk['distance_to_danger']),
                                           float(stamp)))
        for elderly_id in self.elderly_ids:
            if elderly_id not in observed:
                events.extend(self._transition(elderly_id, STATE_UNKNOWN,
                                               math.nan, float(stamp)))
        self._select_current()
        return events

    def _transition(self, elderly_id, new_state, distance, stamp):
        track = self.tracks[elderly_id]
        previous = track.state
        track.last_distance = distance
        track.robot_distance = self.robot_distance(elderly_id)
        events = []
        old_hazard = previous in (STATE_WARNING, STATE_DANGER)
        new_hazard = new_state in (STATE_WARNING, STATE_DANGER)
        if new_state == previous:
            return events
        if new_state == STATE_WARNING:
            if (previous == STATE_SAFE or
                    (previous == STATE_UNKNOWN and not track.event_id)):
                track.event_id = self._new_event_id(elderly_id, new_state, track)
                events.append(self._event(track, elderly_id, EVENT_WARNING_ENTER,
                                           new_state, distance, stamp))
            elif previous == STATE_DANGER:
                events.append(self._event(track, elderly_id, EVENT_DANGER_EXIT,
                                           new_state, distance, stamp))
            track.state = new_state
        elif new_state == STATE_DANGER:
            if not track.event_id:
                track.event_id = self._new_event_id(elderly_id, new_state, track)
                events.append(self._event(track, elderly_id, EVENT_DANGER_ENTER,
                                           new_state, distance, stamp))
            elif previous == STATE_WARNING:
                events.append(self._event(track, elderly_id, EVENT_DANGER_ENTER,
                                           new_state, distance, stamp))
            if previous != STATE_DANGER:
                track.danger_entry_time = stamp
            track.state = new_state
        elif new_state == STATE_SAFE:
            if previous == STATE_DANGER:
                events.append(self._event(track, elderly_id, EVENT_DANGER_EXIT,
                                           new_state, distance, stamp))
            elif previous == STATE_WARNING:
                events.append(self._event(track, elderly_id, EVENT_WARNING_EXIT,
                                           new_state, distance, stamp))
            elif previous == STATE_UNKNOWN and track.event_id:
                exit_type = (EVENT_DANGER_EXIT
                             if track.event_entry_state == STATE_DANGER
                             else EVENT_WARNING_EXIT)
                events.append(self._event(track, elderly_id, exit_type,
                                           new_state, distance, stamp))
            track.state = new_state
            track.event_id = ''
            track.event_entry_state = ''
            track.danger_entry_time = math.inf
        else:
            # UNKNOWN never emits an exit and retains any active episode.
            track.state = STATE_UNKNOWN
        return events

    def _event(self, track, elderly_id, event_type, state, distance, stamp):
        priority = ('HIGH' if event_type in
                    (EVENT_DANGER_ENTER, EVENT_DANGER_EXIT)
                    else 'MEDIUM' if event_type in
                    (EVENT_WARNING_ENTER, EVENT_WARNING_EXIT) else 'LOW')
        return EventRecord(track.event_id, elderly_id, event_type,
                           priority, state, distance, stamp)

    def _select_current(self):
        for elderly_id in self.tracks:
            self.tracks[elderly_id].robot_distance = self.robot_distance(
                elderly_id
            )
        active = [
            (elderly_id, track) for elderly_id, track in self.tracks.items()
            if track.state in (STATE_WARNING, STATE_DANGER)
        ]
        if not active:
            self.manager_state = (MANAGER_MONITORING if self.received_risks
                                   else MANAGER_STANDBY)
            return None
        danger = [(i, t) for i, t in active if t.state == STATE_DANGER]
        candidates = danger or active
        selected = min(candidates, key=lambda item: (
            item[1].danger_entry_time if item[1].state == STATE_DANGER else math.inf,
            (item[1].robot_distance if item[1].state == STATE_DANGER
             else math.inf),
            item[0],
        ))
        self.manager_state = MANAGER_EVENT_SELECTED
        return selected[0]

    def current_event(self):
        """Return selected (elderly ID, event ID, state), or None."""
        selected = self._select_current()
        if selected is None:
            return None
        track = self.tracks[selected]
        return selected, track.event_id, track.state


class ElderlySafetyManager(Node):
    """ROS wrapper publishing one-shot events and current selection state."""

    def __init__(self):
        super().__init__('elderly_safety_manager')
        self.declare_parameter('publish_frequency', 5.0)
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('robot_frame', 'base_link')
        self.declare_parameter(
            'elderly_ids',
            ['elder', 'elder_01', 'elder_02', 'elder_03', 'elder_04'],
        )
        frequency = float(self.get_parameter('publish_frequency').value)
        if frequency <= 0.0:
            raise ValueError('publish_frequency must be positive')
        ids = self.get_parameter('elderly_ids').value
        self.map_frame = str(self.get_parameter('map_frame').value)
        self.robot_frame = str(self.get_parameter('robot_frame').value)
        self.manager = SafetyEventManager(ids, self.map_frame)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.event_pub = self.create_publisher(ElderlyEvent, '/elderly/events', 10)
        self.current_pub = self.create_publisher(String, '/elderly/current_event', 10)
        self.state_pub = self.create_publisher(
            String, '/elderly/safety_manager_state', 10
        )
        self.create_subscription(ElderlyRiskArray, '/elderly/risks',
                                 self._risk_callback, 20)
        self.create_subscription(ElderlyPositionArray, '/elderly/positions',
                                 self._position_callback, 20)
        self.create_timer(1.0 / frequency, self._publish_status)

    def _risk_callback(self, message):
        stamp = message.header.stamp.sec + message.header.stamp.nanosec * 1e-9
        if stamp <= 0.0:
            stamp = self.get_clock().now().nanoseconds * 1e-9
        risks = ({'elderly_id': risk.elderly_id, 'state': risk.state,
                  'distance_to_danger': risk.distance_to_danger}
                 for risk in message.risks)
        for event in self.manager.process(risks, stamp):
            output = ElderlyEvent()
            output.header.stamp = message.header.stamp
            if output.header.stamp.sec == 0 and output.header.stamp.nanosec == 0:
                output.header.stamp = self.get_clock().now().to_msg()
            output.header.frame_id = 'map'
            output.event_id = event.event_id
            output.elderly_id = event.elderly_id
            output.event_type = event.event_type
            output.priority = event.priority
            output.state = event.state
            output.distance_to_danger = event.distance_to_danger
            self.event_pub.publish(output)

    def _position_callback(self, message):
        array_stamp = message.header.stamp.sec + message.header.stamp.nanosec * 1e-9
        now = self.get_clock().now().nanoseconds * 1e-9
        for position in message.positions:
            stamp = position.header.stamp.sec + position.header.stamp.nanosec * 1e-9
            if stamp <= 0.0:
                stamp = array_stamp if array_stamp > 0.0 else now
            self.manager.update_position(
                position.elderly_id, position.pose.position.x,
                position.pose.position.y, stamp, position.valid,
                position.header.frame_id or message.header.frame_id,
            )

    def _update_robot_pose(self):
        try:
            transform = self.tf_buffer.lookup_transform(
                self.map_frame, self.robot_frame, rclpy.time.Time()
            )
            self.manager.set_robot_pose(
                transform.transform.translation.x,
                transform.transform.translation.y,
                True,
            )
        except TransformException:
            self.manager.set_robot_pose(math.nan, math.nan, False)

    def _publish_status(self):
        self._update_robot_pose()
        current = self.manager.current_event()
        if current:
            elderly_id, event_id, state = current
            distance = self.manager.tracks[elderly_id].robot_distance
            text = (f'event_id={event_id} elderly_id={elderly_id} '
                    f'state={state} robot_distance={distance}')
        else:
            text = ''
        self.current_pub.publish(String(data=text))
        self.state_pub.publish(String(data=self.manager.manager_state))


def main(args=None):
    rclpy.init(args=args)
    node = ElderlySafetyManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
