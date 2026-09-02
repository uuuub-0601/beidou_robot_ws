"""Publish a live RViz text marker for the elderly geofence state."""

from geometry_msgs.msg import PoseStamped
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String
from visualization_msgs.msg import Marker


class ElderlyRvizStatus(Node):
    """Display the current geofence state beside the elderly position."""

    _COLORS = {
        'SAFE': (0.1, 1.0, 0.1),
        'WARNING': (1.0, 0.85, 0.1),
        'DANGER': (1.0, 0.1, 0.1),
        'UNKNOWN': (0.8, 0.8, 0.8),
    }

    def __init__(self):
        super().__init__('elderly_rviz_status')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('height', 0.9)
        self.declare_parameter('text_size', 0.5)
        self.map_frame = str(self.get_parameter('map_frame').value)
        self.height = float(self.get_parameter('height').value)
        self.text_size = float(self.get_parameter('text_size').value)
        if self.height < 0.0:
            raise ValueError('height must be nonnegative')
        if self.text_size <= 0.0:
            raise ValueError('text_size must be positive')
        self.position = None
        self.state = 'UNKNOWN'
        self.marker_publisher = self.create_publisher(
            Marker, '/elderly_geofence_status_marker', 10
        )
        state_qos = QoSProfile(
            depth=1, reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.create_subscription(
            PoseStamped, '/elderly_position', self._position_callback, 10
        )
        self.create_subscription(
            String, '/elderly_geofence_state', self._state_callback, state_qos
        )
        self.create_timer(0.1, self._publish_marker)

    def _position_callback(self, message):
        self.position = message
        self._publish_marker()

    def _state_callback(self, message):
        state = str(message.data).strip().upper()
        self.state = state if state in self._COLORS else 'UNKNOWN'
        self._publish_marker()

    def _publish_marker(self):
        marker = Marker()
        marker.header.frame_id = self.map_frame
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'elderly_geofence_status'
        marker.id = 0
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.z = self.text_size
        marker.color.r, marker.color.g, marker.color.b = self._COLORS[self.state]
        marker.color.a = 1.0
        marker.text = self.state
        if self.position is not None:
            marker.pose.position.x = self.position.pose.position.x
            marker.pose.position.y = self.position.pose.position.y
            marker.pose.position.z = self.position.pose.position.z + self.height
        else:
            marker.pose.position.z = self.height
        self.marker_publisher.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = ElderlyRvizStatus()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
