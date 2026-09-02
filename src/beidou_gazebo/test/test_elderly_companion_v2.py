"""Tests for Companion 2.0 target and speed calculations."""

import math

from beidou_gazebo.elderly_companion_v2 import calculate_dynamic_follow_target
from beidou_gazebo.elderly_companion_v2 import companion_state
from beidou_gazebo.elderly_companion_v2 import desired_speed_limit
from beidou_gazebo.elderly_companion_v2 import follow_target_changed
from beidou_gazebo.elderly_companion_v2 import rate_limit
from beidou_gazebo.elderly_companion_v2 import retry_interval_elapsed
from beidou_gazebo.elderly_companion_v2 import STATE_APPROACHING
from beidou_gazebo.elderly_companion_v2 import STATE_FOLLOWING
from geometry_msgs.msg import PoseStamped
import pytest


def make_pose(x, y, yaw):
    pose = PoseStamped()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def test_dynamic_target_is_behind_and_left_for_eastbound_motion():
    x, y, yaw = calculate_dynamic_follow_target(
        5.0,
        3.0,
        0.3,
        0.0,
        0.0,
        1.4,
        0.4,
        0.6,
    )
    assert x == pytest.approx(3.78)
    assert y == pytest.approx(3.4)
    assert yaw == pytest.approx(0.0)


def test_dynamic_target_rotates_with_heading():
    x, y, yaw = calculate_dynamic_follow_target(
        5.0,
        5.0,
        0.0,
        0.4,
        math.pi / 2.0,
        1.4,
        0.4,
        0.6,
    )
    assert x == pytest.approx(4.6)
    assert y == pytest.approx(3.84)
    assert yaw == pytest.approx(math.pi / 2.0)


@pytest.mark.parametrize(
    ('elderly_speed', 'expected'),
    [(0.2, 0.25), (0.3, 0.35), (0.4, 0.45)],
)
def test_speed_limit_tracks_elderly_speed(elderly_speed, expected):
    limit = desired_speed_limit(
        elderly_speed,
        0.25,
        0.25,
        0.05,
        0.35,
        0.03,
        0.5,
    )
    assert limit == pytest.approx(expected)


def test_speed_limit_saturates_at_existing_dwb_maximum():
    limit = desired_speed_limit(0.4, 3.0, 0.25, 0.05, 0.35, 0.03, 0.5)
    assert limit == pytest.approx(0.5)


def test_stopped_elderly_uses_low_cap_while_robot_finishes_target():
    limit = desired_speed_limit(0.0, 0.1, 0.25, 0.0, 0.35, 0.03, 0.5)
    assert limit == pytest.approx(0.03)


def test_stopped_elderly_in_companion_range_disables_catchup_speed():
    limit = desired_speed_limit(
        0.0,
        2.0,
        0.25,
        0.05,
        0.35,
        0.03,
        0.5,
        companion_distance_satisfied=True,
        stopped_speed_threshold=0.05,
    )
    assert limit == pytest.approx(0.03)


def test_speed_limit_changes_gradually():
    assert rate_limit(0.2, 0.5, 0.2, 0.5, 0.5) == pytest.approx(0.3)
    assert rate_limit(0.4, 0.2, 0.2, 0.5, 0.5) == pytest.approx(0.3)


def test_state_changes_only_inside_companion_range():
    assert companion_state(17.0, 1.0, 2.0) == STATE_APPROACHING
    assert companion_state(1.5, 1.0, 2.0) == STATE_FOLLOWING
    assert companion_state(0.7, 1.0, 2.0) == STATE_APPROACHING


def test_outer_action_retry_is_rate_limited():
    assert retry_interval_elapsed(10.0, None, 2.0) is True
    assert retry_interval_elapsed(11.9, 10.0, 2.0) is False
    assert retry_interval_elapsed(12.0, 10.0, 2.0) is True


def test_retry_recovers_when_simulation_clock_resets():
    assert retry_interval_elapsed(1.0, 20.0, 2.0) is True


def test_first_follow_target_always_updates_active_goal():
    assert follow_target_changed(make_pose(1.0, 2.0, 0.0), None, 0.1, 0.12)


def test_small_follow_target_jitter_does_not_update_active_goal():
    previous = make_pose(1.0, 2.0, 0.0)
    target = make_pose(1.05, 2.04, 0.05)
    assert not follow_target_changed(target, previous, 0.1, 0.12)


def test_follow_target_translation_updates_active_goal():
    previous = make_pose(1.0, 2.0, 0.0)
    target = make_pose(1.11, 2.0, 0.0)
    assert follow_target_changed(target, previous, 0.1, 0.12)


def test_follow_target_turn_updates_active_goal():
    previous = make_pose(1.0, 2.0, math.pi - 0.04)
    target = make_pose(1.0, 2.0, -math.pi + 0.10)
    assert follow_target_changed(target, previous, 0.1, 0.12)
