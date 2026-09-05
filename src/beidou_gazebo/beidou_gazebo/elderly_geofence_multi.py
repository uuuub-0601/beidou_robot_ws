"""Independent dual-layer electronic-fence risk for multiple elderly tracks."""

from dataclasses import dataclass
import math

from beidou_gazebo.elderly_geofence import (
    distance_to_polygon,
    load_obstacles,
    STATE_DANGER,
    STATE_SAFE,
    STATE_UNKNOWN,
    STATE_WARNING,
)
from beidou_interfaces.msg import ElderlyPositionArray, ElderlyMotionArray
from beidou_interfaces.msg import ElderlyRisk, ElderlyRiskArray
import rclpy
from rclpy.node import Node


DEFAULT_ELDERLY_IDS = (
    'elder', 'elder_01', 'elder_02', 'elder_03', 'elder_04'
)


@dataclass
class TrackData:
    """Latest independently received position and motion validity data."""

    x: float = math.nan
    y: float = math.nan
    position_stamp: float = 0.0
    position_valid: bool = False
    position_frame: str = ''
    motion_stamp: float = 0.0
    motion_valid: bool = False
    state: str = STATE_UNKNOWN


def stamp_to_seconds(stamp):
    """Convert a ROS time message to seconds."""
    return float(stamp.sec) + float(stamp.nanosec) * 1e-9


def classify_distance(distance, previous, danger_distance=0.5,
                      warning_distance=1.0, danger_exit=0.7,
                      warning_exit=1.2):
    """Apply independent WARNING/DANGER entry and exit hysteresis."""
    if not math.isfinite(distance):
        return STATE_UNKNOWN
    if previous == STATE_DANGER:
        if distance <= danger_exit:
            return STATE_DANGER
        if distance <= warning_exit:
            return STATE_WARNING
        return STATE_SAFE
    if previous == STATE_WARNING:
        if distance <= danger_distance:
            return STATE_DANGER
        if distance <= warning_exit:
            return STATE_WARNING
        return STATE_SAFE
    if distance <= danger_distance:
        return STATE_DANGER
    if distance <= warning_distance:
        return STATE_WARNING
    return STATE_SAFE


class MultiElderlyRiskTracker:
    """Store tracks and classify each elderly person independently."""

    def __init__(self, elderly_ids, obstacles, timeout=1.0,
                 map_frame='map', danger_distance=0.5,
                 warning_distance=1.0, danger_exit=0.7,
                 warning_exit=1.2):
        self.elderly_ids = tuple(dict.fromkeys(elderly_ids))
        self.obstacles = tuple(obstacles)
        self.timeout = float(timeout)
        self.map_frame = map_frame
        self.danger_distance = float(danger_distance)
        self.warning_distance = float(warning_distance)
        self.danger_exit = float(danger_exit)
        self.warning_exit = float(warning_exit)
        self.tracks = {elderly_id: TrackData()
                       for elderly_id in self.elderly_ids}

    def ensure_id(self, elderly_id):
        """Add a newly observed stable ID without affecting other tracks."""
        if elderly_id and elderly_id not in self.tracks:
            self.tracks[elderly_id] = TrackData()
            self.elderly_ids += (elderly_id,)

    def update_position(self, elderly_id, x, y, stamp, valid=True,
                        frame_id='map'):
        """Store one position measurement."""
        self.ensure_id(elderly_id)
        if not elderly_id:
            return
        track = self.tracks[elderly_id]
        track.x, track.y = float(x), float(y)
        track.position_stamp = float(stamp)
        track.position_valid = bool(valid)
        track.position_frame = frame_id

    def update_motion(self, elderly_id, stamp, valid):
        """Store one motion validity measurement."""
        self.ensure_id(elderly_id)
        if elderly_id:
            track = self.tracks[elderly_id]
            track.motion_stamp = float(stamp)
            track.motion_valid = bool(valid)

    def evaluate(self, elderly_id, now):
        """Return (state, distance, valid) for one track."""
        track = self.tracks[elderly_id]
        current = float(now)
        position_fresh = (
            track.position_valid and track.position_frame == self.map_frame
            and math.isfinite(track.x) and math.isfinite(track.y)
            and track.position_stamp > 0.0
            and current - track.position_stamp <= self.timeout
        )
        motion_fresh = (
            track.motion_valid and track.motion_stamp > 0.0
            and current - track.motion_stamp <= self.timeout
        )
        if not position_fresh or not motion_fresh:
            track.state = STATE_UNKNOWN
            return STATE_UNKNOWN, math.nan, False
        distance = min(
            distance_to_polygon(track.x, track.y, zone.polygon)
            for zone in self.obstacles
        )
        track.state = classify_distance(
            distance, track.state, self.danger_distance,
            self.warning_distance, self.danger_exit, self.warning_exit,
        )
        return track.state, distance, track.state != STATE_UNKNOWN


class ElderlyGeofenceMulti(Node):
    """Publish independent SAFE/WARNING/DANGER/UNKNOWN risk states."""

    def __init__(self):
        super().__init__('elderly_geofence_multi')
        self.declare_parameter('obstacle_config', '')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('position_timeout', 1.0)
        self.declare_parameter('danger_distance', 0.5)
        self.declare_parameter('warning_distance', 1.0)
        self.declare_parameter('danger_exit_distance', 0.7)
        self.declare_parameter('warning_exit_distance', 1.2)
        self.declare_parameter('publish_frequency', 5.0)
        self.declare_parameter('elderly_ids', list(DEFAULT_ELDERLY_IDS))
        config = str(self.get_parameter('obstacle_config').value) or None
        map_frame = str(self.get_parameter('map_frame').value)
        self.tracker = MultiElderlyRiskTracker(
            (str(value) for value in self.get_parameter('elderly_ids').value),
            load_obstacles(config),
            timeout=float(self.get_parameter('position_timeout').value),
            map_frame=map_frame,
            danger_distance=float(self.get_parameter('danger_distance').value),
            warning_distance=float(self.get_parameter('warning_distance').value),
            danger_exit=float(self.get_parameter('danger_exit_distance').value),
            warning_exit=float(self.get_parameter('warning_exit_distance').value),
        )
        frequency = float(self.get_parameter('publish_frequency').value)
        if frequency <= 0.0:
            raise ValueError('publish_frequency must be positive')
        self.risk_pub = self.create_publisher(ElderlyRiskArray,
                                              '/elderly/risks', 10)
        self.create_subscription(ElderlyPositionArray, '/elderly/positions',
                                 self._position_callback, 20)
        self.create_subscription(ElderlyMotionArray, '/elderly/motions',
                                 self._motion_callback, 20)
        self.create_timer(1.0 / frequency, self._publish_risks)

    def _position_callback(self, message):
        array_stamp = stamp_to_seconds(message.header.stamp)
        for position in message.positions:
            stamp = stamp_to_seconds(position.header.stamp)
            if stamp <= 0.0:
                stamp = array_stamp
            self.tracker.update_position(
                position.elderly_id, position.pose.position.x,
                position.pose.position.y, stamp, position.valid,
                position.header.frame_id or message.header.frame_id,
            )

    def _motion_callback(self, message):
        array_stamp = stamp_to_seconds(message.header.stamp)
        for motion in message.motions:
            stamp = stamp_to_seconds(motion.header.stamp)
            if stamp <= 0.0:
                stamp = array_stamp
            self.tracker.update_motion(motion.elderly_id, stamp,
                                       motion.valid)

    def _publish_risks(self):
        now = self.get_clock().now()
        now_seconds = now.nanoseconds * 1e-9
        output = ElderlyRiskArray()
        output.header.stamp = now.to_msg()
        output.header.frame_id = self.tracker.map_frame
        for elderly_id in self.tracker.elderly_ids:
            state, distance, valid = self.tracker.evaluate(
                elderly_id, now_seconds)
            risk = ElderlyRisk()
            risk.header.stamp = output.header.stamp
            risk.header.frame_id = self.tracker.map_frame
            risk.elderly_id = elderly_id
            risk.state = state
            risk.distance_to_danger = distance
            risk.valid = valid
            output.risks.append(risk)
        self.risk_pub.publish(output)


def main(args=None):
    rclpy.init(args=args)
    node = ElderlyGeofenceMulti()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
