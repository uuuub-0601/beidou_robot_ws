"""Publish simulated elderly Beidou position in the map frame."""

from geometry_msgs.msg import PoseStamped, TransformStamped
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_msgs.msg import TFMessage
from tf2_ros import Buffer, TransformException, TransformListener
from visualization_msgs.msg import Marker


GAZEBO_WORLD_FRAME = 'gazebo_world'
GAZEBO_ROBOT_FRAME = 'gazebo_robot_reference'


def find_named_transform(message, model_name):
    """Return a Gazebo model transform by name, independent of order."""
    return next(
        (
            transform
            for transform in message.transforms
            if transform.child_frame_id == model_name
        ),
        None,
    )


def transform_gazebo_pose_to_map(
    elderly_world,
    robot_world,
    map_to_robot,
    stamp,
    gazebo_buffer=None,
):
    """Transform a Gazebo world pose through the robot into map."""
    buffer = gazebo_buffer or Buffer()
    buffer.clear()

    world_to_robot = TransformStamped()
    world_to_robot.header.stamp = robot_world.header.stamp
    world_to_robot.header.frame_id = GAZEBO_WORLD_FRAME
    world_to_robot.child_frame_id = GAZEBO_ROBOT_FRAME
    world_to_robot.transform.translation.x = (
        robot_world.transform.translation.x
    )
    world_to_robot.transform.translation.y = (
        robot_world.transform.translation.y
    )
    # Nav2 uses a planar base_link. The Gazebo model origin is 0.22 m high,
    # so only its planar origin and orientation coincide with base_link.
    world_to_robot.transform.translation.z = 0.0
    world_to_robot.transform.rotation = robot_world.transform.rotation
    buffer.set_transform_static(world_to_robot, 'beidou_gazebo_pose')

    robot_to_world = buffer.lookup_transform(
        GAZEBO_ROBOT_FRAME,
        GAZEBO_WORLD_FRAME,
        rclpy.time.Time(),
    )
    elderly_pose = PoseStamped()
    elderly_pose.header.stamp = elderly_world.header.stamp
    elderly_pose.header.frame_id = GAZEBO_WORLD_FRAME
    elderly_pose.pose.position.x = elderly_world.transform.translation.x
    elderly_pose.pose.position.y = elderly_world.transform.translation.y
    elderly_pose.pose.position.z = elderly_world.transform.translation.z
    elderly_pose.pose.orientation = elderly_world.transform.rotation

    elderly_robot = do_transform_pose_stamped(
        elderly_pose, robot_to_world
    )
    elderly_robot.header.frame_id = map_to_robot.child_frame_id
    elderly_map = do_transform_pose_stamped(elderly_robot, map_to_robot)
    elderly_map.header.stamp = stamp
    elderly_map.header.frame_id = map_to_robot.header.frame_id
    return elderly_map


class BeidouPositionPublisher(Node):
    def __init__(self):
        super().__init__('elderly_beidou_position')
        parameters = [
            ('pose_topic', '/world/elderly_home/pose/named'),
            ('elder_model_name', 'elder'),
            ('robot_model_name', 'elderly_robot'),
            ('map_frame', 'map'),
            ('robot_frame', 'base_link'),
            ('publish_marker', True),
        ]
        for name, value in parameters:
            self.declare_parameter(name, value)

        topic = self.get_parameter('pose_topic').value
        self.elder_model_name = str(
            self.get_parameter('elder_model_name').value
        )
        self.robot_model_name = str(
            self.get_parameter('robot_model_name').value
        )
        self.map_frame = str(self.get_parameter('map_frame').value)
        self.robot_frame = str(self.get_parameter('robot_frame').value)
        self.publish_marker = bool(
            self.get_parameter('publish_marker').value
        )
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.gazebo_buffer = Buffer()
        self.position_pub = self.create_publisher(
            PoseStamped, '/elderly_position', 10
        )
        self.status_pub = self.create_publisher(
            Bool, '/elderly_position_status', 10
        )
        self.marker_pub = self.create_publisher(
            Marker, '/elderly_position_marker', 10
        )
        self.create_subscription(TFMessage, topic, self._callback, 10)

    def _callback(self, message):
        elderly_world = find_named_transform(
            message, self.elder_model_name
        )
        robot_world = find_named_transform(
            message, self.robot_model_name
        )
        if elderly_world is None or robot_world is None:
            return self._invalid()

        try:
            map_to_robot = self.tf_buffer.lookup_transform(
                self.map_frame, self.robot_frame, rclpy.time.Time()
            )
            output = transform_gazebo_pose_to_map(
                elderly_world,
                robot_world,
                map_to_robot,
                self.get_clock().now().to_msg(),
                self.gazebo_buffer,
            )
        except TransformException:
            return self._invalid()

        self.position_pub.publish(output)
        self.status_pub.publish(Bool(data=True))
        if self.publish_marker:
            self._publish_marker(output)

    def _publish_marker(self, output):
        marker = Marker()
        marker.header = output.header
        marker.ns = 'elderly_beidou'
        marker.id = 0
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose = output.pose
        marker.pose.position.z = max(0.4, output.pose.position.z)
        marker.scale.x = marker.scale.y = marker.scale.z = 0.55
        marker.color.r = 0.95
        marker.color.g = 0.15
        marker.color.b = 0.1
        marker.color.a = 1.0
        self.marker_pub.publish(marker)

    def _invalid(self):
        self.status_pub.publish(Bool(data=False))


def main(args=None):
    rclpy.init(args=args)
    node = BeidouPositionPublisher()
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
