"""Tests for elderly walker routing and continuous velocity commands."""

import math

from beidou_gazebo.elderly_walker import advance_waypoint
from beidou_gazebo.elderly_walker import calculate_walking_command
from beidou_gazebo.elderly_walker import normalize_angle
from beidou_gazebo.elderly_walker import quaternion_to_yaw
from beidou_gazebo.elderly_walker import walking_speed_is_valid
import pytest


WAYPOINTS = ((3.0, 3.0), (5.0, 3.0), (5.0, 5.0), (3.0, 5.0))


def command(speed=0.4, yaw=0.0, target=(5.0, 3.0)):
    return calculate_walking_command(
        3.0,
        3.0,
        yaw,
        target[0],
        target[1],
        speed,
        0.8,
        1.5,
        0.15,
    )


def test_straight_route_uses_configured_walking_speed():
    linear, angular, error = command(speed=0.4)
    assert linear == pytest.approx(0.4)
    assert angular == pytest.approx(0.0)
    assert error == pytest.approx(0.0)


def test_walking_speed_parameter_changes_command():
    slow, _, _ = command(speed=0.3)
    fast, _, _ = command(speed=0.5)
    assert slow == pytest.approx(0.3)
    assert fast == pytest.approx(0.5)


@pytest.mark.parametrize('speed', [0.0, 0.2, 0.3, 0.4, 1.0])
def test_runtime_walking_speed_range(speed):
    assert walking_speed_is_valid(speed) is True


@pytest.mark.parametrize('speed', [-0.01, 1.01, '0.3'])
def test_invalid_runtime_walking_speed_is_rejected(speed):
    assert walking_speed_is_valid(speed) is False


def test_reaching_waypoint_advances_and_route_wraps():
    assert advance_waypoint(3.05, 3.0, WAYPOINTS, 0, 0.1) == 1
    assert advance_waypoint(3.0, 5.05, WAYPOINTS, 3, 0.1) == 0


def test_corner_keeps_moving_and_turns_toward_next_segment():
    linear, angular, error = command(yaw=0.0, target=(3.0, 5.0))
    assert 0.0 < linear < 0.4
    assert angular == pytest.approx(0.8)
    assert error == pytest.approx(math.pi / 2.0)


@pytest.mark.parametrize(
    ('angle', 'expected'),
    [(3.0 * math.pi, math.pi), (-3.0 * math.pi, -math.pi)],
)
def test_angle_normalization(angle, expected):
    assert normalize_angle(angle) == pytest.approx(expected)


def test_quaternion_yaw_extraction():
    half_angle = math.pi / 4.0
    yaw = quaternion_to_yaw(
        0.0,
        0.0,
        math.sin(half_angle),
        math.cos(half_angle),
    )
    assert yaw == pytest.approx(math.pi / 2.0)
