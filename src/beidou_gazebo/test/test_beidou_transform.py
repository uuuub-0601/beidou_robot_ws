"""Regression tests for simulated Beidou coordinate conversion."""

import math

from beidou_gazebo.beidou_position_publisher import find_named_transform
from beidou_gazebo.beidou_position_publisher import (
    transform_gazebo_pose_to_map,
)
from builtin_interfaces.msg import Time
from geometry_msgs.msg import TransformStamped
from tf2_msgs.msg import TFMessage


def make_transform(name, x, y, yaw):
    transform = TransformStamped()
    transform.header.frame_id = 'gazebo_world'
    transform.child_frame_id = name
    transform.transform.translation.x = x
    transform.transform.translation.y = y
    transform.transform.rotation.z = math.sin(yaw / 2.0)
    transform.transform.rotation.w = math.cos(yaw / 2.0)
    return transform


def map_to_robot(yaw):
    transform = make_transform('base_link', 0.0, 0.0, yaw)
    transform.header.frame_id = 'map'
    return transform


def assert_position(output, x, y):
    assert math.isclose(output.pose.position.x, x, abs_tol=1e-9)
    assert math.isclose(output.pose.position.y, y, abs_tol=1e-9)


def test_yaw_zero():
    output = transform_gazebo_pose_to_map(
        make_transform('elder', 6.0, 5.0, 0.0),
        make_transform('elderly_robot', -7.0, -7.0, 0.0),
        map_to_robot(0.0),
        Time(sec=10),
    )
    assert_position(output, 13.0, 12.0)


def test_robot_rotation_does_not_move_elderly_world_position():
    output = transform_gazebo_pose_to_map(
        make_transform('elder', 6.0, 5.0, 0.0),
        make_transform(
            'elderly_robot', -7.0, -7.0, math.pi / 2.0
        ),
        map_to_robot(math.pi / 2.0),
        Time(sec=11),
    )
    assert_position(output, 13.0, 12.0)


def test_robot_rotation_and_elderly_world_x_movement():
    output = transform_gazebo_pose_to_map(
        make_transform('elder', 7.0, 5.0, 0.0),
        make_transform(
            'elderly_robot', -7.0, -7.0, math.pi / 2.0
        ),
        map_to_robot(math.pi / 2.0),
        Time(sec=12),
    )
    assert_position(output, 14.0, 12.0)


def test_models_are_selected_by_name_not_position():
    robot = make_transform('elderly_robot', -7.0, -7.0, 0.0)
    elderly = make_transform('elder', 6.0, 5.0, 0.0)
    message = TFMessage(transforms=[robot, elderly])
    assert find_named_transform(message, 'elder') is elderly
    assert find_named_transform(message, 'elderly_robot') is robot
