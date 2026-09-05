"""Publish structured simulated Beidou positions for elderly models."""

from copy import deepcopy

from beidou_gazebo.beidou_position_publisher import (
    find_named_transform,
    transform_gazebo_pose_to_map,
)
from beidou_interfaces.msg import ElderlyPosition, ElderlyPositionArray
import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
from tf2_ros import Buffer, TransformException, TransformListener


DEFAULT_ELDERLY_IDS = (
    'elder', 'elder_01', 'elder_02', 'elder_03', 'elder_04'
)


def _stamp_from_transforms(message, model_names):
    """Return the Gazebo simulation stamp carried by the pose message."""
    names = set(model_names)
    for transform in message.transforms:
        if transform.child_frame_id not in names:
            continue
        stamp = transform.header.stamp
        if stamp.sec or stamp.nanosec:
            return deepcopy(stamp)
    return None


class MultiBeidouPositionPublisher(Node):
    """Convert all configured Gazebo elderly poses into map-frame tracks."""

    def __init__(self):
        super().__init__('multi_beidou_position_publisher')
        self.declare_parameter('pose_topic', '/world/elderly_final/pose/named')
        self.declare_parameter('robot_model_name', 'elderly_robot')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('robot_frame', 'base_link')
        self.declare_parameter('elderly_ids', list(DEFAULT_ELDERLY_IDS))

        self.pose_topic = str(self.get_parameter('pose_topic').value)
        self.robot_model_name = str(
            self.get_parameter('robot_model_name').value
        )
        self.map_frame = str(self.get_parameter('map_frame').value)
        self.robot_frame = str(self.get_parameter('robot_frame').value)
        configured_ids = self.get_parameter('elderly_ids').value
        self.elderly_ids = tuple(
            dict.fromkeys(str(value) for value in configured_ids)
        )
        if not self.elderly_ids:
            raise ValueError(
                'elderly_ids must contain at least one model name'
            )

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.gazebo_buffer = Buffer()
        self.position_pub = self.create_publisher(
            ElderlyPositionArray, '/elderly/positions', 10
        )
        self.create_subscription(
            TFMessage, self.pose_topic, self._callback, 10
        )

    def _callback(self, message):
        robot_world = find_named_transform(message, self.robot_model_name)
        measurement_stamp = _stamp_from_transforms(message, self.elderly_ids)
        if measurement_stamp is None:
            measurement_stamp = self.get_clock().now().to_msg()

        map_to_robot = None
        if robot_world is not None:
            try:
                map_to_robot = self.tf_buffer.lookup_transform(
                    self.map_frame, self.robot_frame, rclpy.time.Time()
                )
            except TransformException:
                map_to_robot = None

        output = ElderlyPositionArray()
        output.header.stamp = measurement_stamp
        output.header.frame_id = self.map_frame
        for elderly_id in self.elderly_ids:
            track = ElderlyPosition()
            track.header.stamp = measurement_stamp
            track.header.frame_id = self.map_frame
            track.elderly_id = elderly_id
            elderly_world = find_named_transform(message, elderly_id)
            if (elderly_world is not None and robot_world is not None
                    and map_to_robot is not None):
                try:
                    pose = transform_gazebo_pose_to_map(
                        elderly_world,
                        robot_world,
                        map_to_robot,
                        measurement_stamp,
                        self.gazebo_buffer,
                    )
                    track.pose = pose.pose
                    track.valid = True
                except (TransformException, RuntimeError, ValueError):
                    track.valid = False
            output.positions.append(track)
        self.position_pub.publish(output)


def main(args=None):
    rclpy.init(args=args)
    node = MultiBeidouPositionPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
