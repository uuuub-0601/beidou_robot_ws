"""Tests for companion goal geometry and replanning decisions."""

import math

from beidou_gazebo.elderly_companion_navigation import (
    calculate_companion_goal,
)
from beidou_gazebo.elderly_companion_navigation import (
    companion_replan_reason,
)
import pytest


def replan_reason(
    robot=(0.0, 0.0),
    elderly=(1.5, 0.0),
    last_elderly=None,
    navigation_active=False,
):
    return companion_replan_reason(
        robot[0],
        robot[1],
        elderly[0],
        elderly[1],
        1.5,
        0.5,
        0.8,
        last_elderly,
        navigation_active,
    )


def test_companion_goal_keeps_distance_and_faces_elderly():
    goal_x, goal_y, yaw = calculate_companion_goal(
        0.0,
        0.0,
        5.0,
        0.0,
        1.5,
    )
    assert math.hypot(goal_x - 5.0, goal_y) == pytest.approx(1.5)
    assert goal_x == pytest.approx(3.5)
    assert yaw == pytest.approx(0.0)


def test_coincident_positions_use_deterministic_fallback():
    goal_x, goal_y, yaw = calculate_companion_goal(
        2.0,
        3.0,
        2.0,
        3.0,
        1.5,
    )
    assert goal_x == pytest.approx(0.5)
    assert goal_y == pytest.approx(3.0)
    assert yaw == pytest.approx(0.0)


def test_static_elderly_at_companion_distance_needs_no_goal():
    assert replan_reason() is None


def test_static_elderly_does_not_replan_an_active_goal():
    assert replan_reason(
        elderly=(5.0, 0.0),
        last_elderly=(5.0, 0.0),
        navigation_active=True,
    ) is None


@pytest.mark.parametrize('distance', [0.5, 2.1])
def test_distance_deviation_triggers_goal(distance):
    assert replan_reason(elderly=(distance, 0.0)) == (
        'companion distance deviation'
    )


def test_small_elderly_movement_does_not_replan():
    assert replan_reason(
        elderly=(1.5, 0.0),
        last_elderly=(1.0, 0.0),
        navigation_active=True,
    ) is None


def test_elderly_movement_at_threshold_replans_active_goal():
    assert replan_reason(
        elderly=(1.5, 0.0),
        last_elderly=(0.7, 0.0),
        navigation_active=True,
    ) == 'elderly moved beyond replan threshold'


def test_elderly_movement_does_not_replan_when_navigation_is_idle():
    assert replan_reason(
        elderly=(1.5, 0.0),
        last_elderly=(0.7, 0.0),
        navigation_active=False,
    ) is None
