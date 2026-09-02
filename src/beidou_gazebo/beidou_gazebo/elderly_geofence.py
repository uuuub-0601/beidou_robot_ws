"""Per-obstacle electronic fences for the elderly map position."""

import json
from dataclasses import dataclass  # noqa: I100
import math  # noqa: I100
import os

from ament_index_python.packages import get_package_share_directory

from geometry_msgs.msg import Point, PoseStamped

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from std_msgs.msg import Bool, String

from visualization_msgs.msg import Marker, MarkerArray

STATE_SAFE = 'SAFE'
STATE_WARNING = 'WARNING'
STATE_DANGER = 'DANGER'
STATE_UNKNOWN = 'UNKNOWN'
RISK_ORDER = {STATE_SAFE: 0, STATE_WARNING: 1, STATE_DANGER: 2}


@dataclass(frozen=True)
class ObstacleZone:
    """One collision footprint represented by a planar polygon."""

    zone_id: str
    polygon: tuple


def is_inside_geofence(x, y, xmin, xmax, ymin, ymax):
    """Retain the old helper for callers that still import it."""
    return xmin <= x <= xmax and ymin <= y <= ymax


def point_in_polygon(x, y, polygon):
    """Return whether a point is inside or on a polygon boundary."""
    inside = False
    if len(polygon) < 3:
        return False
    for index, (x1, y1) in enumerate(polygon):
        x2, y2 = polygon[(index + 1) % len(polygon)]
        cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
        length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if length_sq and abs(cross) <= 1e-9:
            dot = (x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)
            if 0.0 <= dot <= length_sq:
                return True
        if (y1 > y) != (y2 > y):
            crossing_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < crossing_x:
                inside = not inside
    return inside


def point_to_segment_distance(x, y, start, end):
    """Return the Euclidean distance from a point to a line segment."""
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    length_sq = dx * dx + dy * dy
    if length_sq <= 1e-12:
        return math.hypot(x - x1, y - y1)
    projection = ((x - x1) * dx + (y - y1) * dy) / length_sq
    projection = max(0.0, min(1.0, projection))
    return math.hypot(x - x1 - projection * dx, y - y1 - projection * dy)


def distance_to_polygon(x, y, polygon):
    """Return zero inside a polygon, otherwise distance to its boundary."""
    if point_in_polygon(x, y, polygon):
        return 0.0
    return min(point_to_segment_distance(
        x, y, polygon[index], polygon[(index + 1) % len(polygon)]
    ) for index in range(len(polygon)))


def classify_zone(distance, danger_distance, warning_distance):
    """Classify a zone from its true Euclidean boundary distance."""
    if distance <= danger_distance:
        return STATE_DANGER
    if distance <= warning_distance:
        return STATE_WARNING
    return STATE_SAFE


def position_is_fresh(age, timeout):
    """Return whether the last position is within the timeout window."""
    return math.isfinite(age) and age <= timeout


def aggregate_zone_results(zones):
    """Aggregate per-zone dictionaries into one structured result."""
    active = [zone for zone in zones if zone['state'] != STATE_SAFE]
    state = max(
        (zone['state'] for zone in zones),
        key=lambda value: RISK_ORDER[value],
        default=STATE_SAFE,
    )
    primary = min(active, key=lambda zone: zone['distance'], default=None)
    return {
        'state': state,
        'zone_ids': [zone['zone_id'] for zone in active],
        'primary_zone_id': primary['zone_id'] if primary else '',
        'nearest_distance': min(
            (zone['distance'] for zone in zones), default=float('inf')
        ),
        'zones': zones,
    }


def _default_obstacles():
    """Return verified elderly_final collision footprints."""
    return (
        ObstacleZone('final_flowerbed', ((-3.75, 1.25), (-1.25, 1.25), (-1.25, 2.75), (-3.75, 2.75))),  # noqa: E501
        ObstacleZone('final_bench_west', ((-4.8, -2.45), (-3.2, -2.45), (-3.2, -1.95), (-4.8, -1.95))),  # noqa: E501
        ObstacleZone('final_bench_east', ((-0.8, -2.45), (0.8, -2.45), (0.8, -1.95), (-0.8, -1.95))),  # noqa: E501
        ObstacleZone('final_table', ((-1.6, -0.6), (-0.4, -0.6), (-0.4, 0.6), (-1.6, 0.6))),  # noqa: E501
        ObstacleZone('final_partition', ((6.9, -2.4), (7.5, -2.4), (7.5, 0.4), (6.9, 0.4))),  # noqa: E501
        ObstacleZone('wall_left', ((-10.15, -8.0), (-9.85, -8.0), (-9.85, 8.0), (-10.15, 8.0))),  # noqa: E501
        ObstacleZone('wall_right', ((9.85, -8.0), (10.15, -8.0), (10.15, 8.0), (9.85, 8.0))),  # noqa: E501
        ObstacleZone('wall_back', ((-10.0, 7.85), (10.0, 7.85), (10.0, 8.15), (-10.0, 8.15))),  # noqa: E501
        ObstacleZone('wall_front', ((-10.0, -8.15), (10.0, -8.15), (10.0, -7.85), (-10.0, -7.85))),  # noqa: E501
    )


def load_obstacles(path=None):
    """Load polygon zones from YAML, using verified defaults as fallback."""
    if path is None:
        path = os.path.join(
            get_package_share_directory('beidou_gazebo'), 'config',
            'elderly_geofence.yaml',
        )
    try:
        import yaml
        with open(path, encoding='utf-8') as config_file:
            data = yaml.safe_load(config_file) or {}
        configured = data.get('obstacles', {})
        if not configured:
            configured = data.get('elderly_geofence', {}).get('ros__parameters', {}).get('obstacles', {})  # noqa: E501
        zones = []
        for zone_id, value in configured.items():
            polygon = tuple(
                (float(point[0]), float(point[1]))
                for point in value.get('polygon', [])
            )
            if len(polygon) < 3:
                raise ValueError(f'zone {zone_id} needs at least 3 points')
            zones.append(ObstacleZone(str(zone_id), polygon))
        if zones:
            return tuple(zones)
    except (OSError, ImportError, TypeError, ValueError, KeyError):
        if path and not str(path).endswith('elderly_geofence.yaml'):
            raise
    return _default_obstacles()


class ElderlyGeofence(Node):
    """Classify elderly map positions against independent obstacle zones."""

    def __init__(self):
        """Initialize parameters, publishers, subscriptions, and markers."""
        super().__init__('elderly_geofence')
        for name, default in (
            ('danger_distance', 0.5), ('warning_distance', 1.0),
            ('hysteresis', 0.1), ('position_timeout', 1.0),
        ):
            self.declare_parameter(name, default)
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('obstacle_config', '')
        self.danger_distance = float(self.get_parameter('danger_distance').value)  # noqa: E501
        self.warning_distance = float(self.get_parameter('warning_distance').value)  # noqa: E501
        self.hysteresis = float(self.get_parameter('hysteresis').value)
        self.position_timeout = float(self.get_parameter('position_timeout').value)  # noqa: E501
        self.map_frame = str(self.get_parameter('map_frame').value)
        self.obstacles = load_obstacles(str(self.get_parameter('obstacle_config').value) or None)  # noqa: E501
        if (self.danger_distance < 0.0 or self.warning_distance < self.danger_distance or  # noqa: E501
                self.hysteresis < 0.0 or self.position_timeout <= 0.0):
            raise ValueError('invalid geofence distance or timeout parameters')

        durable = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                             durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.status_pub = self.create_publisher(Bool, '/elderly_geofence_status', 10)  # noqa: E501
        self.state_pub = self.create_publisher(String, '/elderly_geofence_state', durable)  # noqa: E501
        self.outside_pub = self.create_publisher(Bool, '/elderly_geofence_outside', durable)  # noqa: E501
        self.details_pub = self.create_publisher(String, '/elderly_geofence_details', durable)  # noqa: E501
        self.marker_pub = self.create_publisher(Marker, '/elderly_geofence_marker', durable)  # noqa: E501
        self.marker_array_pub = self.create_publisher(MarkerArray, '/elderly_geofence_markers', durable)  # noqa: E501
        self.create_subscription(PoseStamped, '/elderly_position', self._position_callback, 10)  # noqa: E501
        self._last_zone_states = {zone.zone_id: STATE_SAFE for zone in self.obstacles}  # noqa: E501
        self._last_position_time = None
        self._last_position = None
        self._last_log_marker = None
        self.create_timer(0.2, self._watchdog)
        self._publish_markers()
        self._publish_unknown('waiting for elderly position')

    def _position_callback(self, message):
        if message.header.frame_id != self.map_frame:
            self._publish_unknown(f'expected frame {self.map_frame}, got {message.header.frame_id or "<empty>"}')  # noqa: E501
            return
        x, y = float(message.pose.position.x), float(message.pose.position.y)
        if not math.isfinite(x) or not math.isfinite(y):
            self._publish_unknown('elderly position contains non-finite data')
            return
        self._last_position = (x, y)
        self._last_position_time = self.get_clock().now()
        zones = []
        for zone in self.obstacles:
            distance = distance_to_polygon(x, y, zone.polygon)
            state = self._classify_with_hysteresis(zone.zone_id, distance)
            zones.append({'zone_id': zone.zone_id, 'state': state, 'distance': distance})  # noqa: E501
        self._publish_result(zones)

    def _classify_with_hysteresis(self, zone_id, distance):
        previous = self._last_zone_states[zone_id]
        state = classify_zone(distance, self.danger_distance, self.warning_distance)  # noqa: E501
        if previous == STATE_DANGER and distance <= self.danger_distance + self.hysteresis:  # noqa: E501
            state = STATE_DANGER
        elif (previous == STATE_WARNING and
              self.danger_distance < distance <= self.warning_distance + self.hysteresis):  # noqa: E501
            state = STATE_WARNING
        self._last_zone_states[zone_id] = state
        return state

    def _publish_result(self, zones):
        result = aggregate_zone_results(zones)
        # Compatibility Bool is false only for DANGER; detailed state is String.  # noqa: E501
        self.status_pub.publish(Bool(data=result['state'] != STATE_DANGER))
        self.outside_pub.publish(Bool(data=any(zone['distance'] <= 0.0 for zone in zones)))  # noqa: E501
        self.state_pub.publish(String(data=result['state']))
        self.details_pub.publish(String(data=json.dumps(result, separators=(',', ':'))))  # noqa: E501
        self._publish_markers()
        self._log_state_change(result['state'], result['zone_ids'])

    def _publish_unknown(self, reason):
        self._last_position_time = None
        self.status_pub.publish(Bool(data=False))
        self.outside_pub.publish(Bool(data=False))
        self.state_pub.publish(String(data=STATE_UNKNOWN))
        self.details_pub.publish(String(data=json.dumps({
            'state': STATE_UNKNOWN, 'zone_ids': [], 'primary_zone_id': '',
            'nearest_distance': None, 'zones': [], 'reason': reason,
        }, separators=(',', ':'))))
        self._publish_markers()
        if reason != self._last_log_marker:
            self.get_logger().warning(f'[GEOFENCE] {reason}')
            self._last_log_marker = reason

    def _watchdog(self):
        if self._last_position_time is None:
            return
        age = (self.get_clock().now() - self._last_position_time).nanoseconds * 1e-9  # noqa: E501
        if not position_is_fresh(age, self.position_timeout):
            self._publish_unknown(f'elderly position timed out after {age:.2f} s')  # noqa: E501

    def _log_state_change(self, state, zone_ids):
        marker = (state, tuple(zone_ids))
        if marker == self._last_log_marker:
            return
        self._last_log_marker = marker
        if state == STATE_SAFE:
            self.get_logger().info('[GEOFENCE] Elderly is SAFE')
        else:
            self.get_logger().warning(f'[GEOFENCE] {state}; zones={", ".join(zone_ids)}')  # noqa: E501

    @staticmethod
    def _line_points(polygon, z=0.05):
        return [Point(x=x, y=y, z=z) for x, y in (*polygon, polygon[0])]

    def _make_marker(self, zone_id, marker_id, polygon, color, marker_type=Marker.LINE_STRIP):  # noqa: E501
        marker = Marker()
        marker.header.frame_id = self.map_frame
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = f'elderly_geofence/{zone_id}'
        marker.id = marker_id
        marker.type = marker_type
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.06
        marker.color.r, marker.color.g, marker.color.b, marker.color.a = (*color, 1.0)  # noqa: E501
        marker.points = self._line_points(polygon) if polygon else []
        return marker

    def _publish_markers(self):
        markers, marker_id = [], 0
        for zone in self.obstacles:
            xs, ys = zip(*zone.polygon)
            for distance, color in ((self.warning_distance, (1.0, 0.65, 0.0)), (self.danger_distance, (1.0, 0.0, 0.0))):  # noqa: E501
                expanded = ((min(xs)-distance, min(ys)-distance), (max(xs)+distance, min(ys)-distance), (max(xs)+distance, max(ys)+distance), (min(xs)-distance, max(ys)+distance))  # noqa: E501
                markers.append(self._make_marker(
                    zone.zone_id, marker_id, expanded, color))
                marker_id += 1
            markers.append(self._make_marker(
                zone.zone_id, marker_id, zone.polygon, (0.2, 0.8, 0.2)))
            marker_id += 1
        if self._last_position is not None:
            marker = self._make_marker('elderly_position', marker_id, (), (0.1, 0.8, 1.0), Marker.SPHERE)  # noqa: E501
            marker.pose.position.x, marker.pose.position.y = self._last_position  # noqa: E501
            marker.scale.x = marker.scale.y = marker.scale.z = 0.35
            marker.points = []
            markers.append(marker)
        self.marker_array_pub.publish(MarkerArray(markers=markers))
        if markers:
            self.marker_pub.publish(markers[0])


def main(args=None):
    """Run the elderly electronic fence node."""
    rclpy.init(args=args)
    node = ElderlyGeofence()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
