"""Tests for elderly guard navigation calculations and state changes."""

import math

from beidou_gazebo.elderly_guard_navigation import calculate_guard_goal
from beidou_gazebo.elderly_guard_navigation import GuardStateMachine
from beidou_gazebo.elderly_guard_navigation import (
    is_out_of_bounds_transition,
)
from beidou_gazebo.elderly_guard_navigation import STATE_ALERT
from beidou_gazebo.elderly_guard_navigation import STATE_GUARDING
from beidou_gazebo.elderly_guard_navigation import STATE_NAVIGATING
from beidou_gazebo.elderly_guard_navigation import (
    STATE_NAVIGATION_FAILED,
)
from beidou_gazebo.elderly_guard_navigation import STATE_SAFE
import pytest


def make_alert_state_machine():
    machine = GuardStateMachine()
    assert machine.update_geofence(True) is False
    assert machine.update_geofence(False) is True
    assert machine.state == STATE_ALERT
    return machine


def test_safe_to_alert():
    machine = make_alert_state_machine()
    assert machine.state == STATE_ALERT


def test_alert_to_navigating():
    machine = make_alert_state_machine()
    machine.goal_accepted()
    assert machine.state == STATE_NAVIGATING


def test_navigating_to_guarding():
    machine = make_alert_state_machine()
    machine.goal_accepted()
    machine.goal_succeeded()
    assert machine.state == STATE_GUARDING


def test_navigating_to_navigation_failed():
    machine = make_alert_state_machine()
    machine.goal_accepted()
    machine.goal_failed()
    assert machine.state == STATE_NAVIGATION_FAILED


def test_continuous_out_of_bounds_does_not_retrigger_goal():
    machine = make_alert_state_machine()
    assert machine.update_geofence(False) is False
    machine.goal_accepted()
    assert machine.update_geofence(False) is False
    assert machine.state == STATE_NAVIGATING


def test_returning_inside_restores_safe():
    machine = make_alert_state_machine()
    machine.goal_accepted()
    machine.goal_succeeded()
    assert machine.update_geofence(True) is False
    assert machine.state == STATE_SAFE


def test_guard_goal_is_on_robot_side_and_faces_elderly():
    goal_x, goal_y, yaw = calculate_guard_goal(
        0.0, 0.0, 10.0, 0.0, 1.2
    )
    assert goal_x == pytest.approx(8.8)
    assert goal_y == pytest.approx(0.0)
    assert yaw == pytest.approx(0.0)


@pytest.mark.parametrize(
    ('robot_x', 'robot_y', 'elderly_x', 'elderly_y'),
    [(0.0, 0.0, 10.0, 10.0), (10.0, 0.0, 0.0, 10.0)],
)
def test_guard_goal_keeps_requested_distance(
    robot_x, robot_y, elderly_x, elderly_y
):
    goal_x, goal_y, _ = calculate_guard_goal(
        robot_x, robot_y, elderly_x, elderly_y, 1.2
    )
    distance = math.hypot(goal_x - elderly_x, goal_y - elderly_y)
    assert distance == pytest.approx(1.2)


def test_coincident_positions_have_deterministic_fallback():
    goal_x, goal_y, yaw = calculate_guard_goal(
        5.0, 6.0, 5.0, 6.0, 1.2
    )
    assert goal_x == pytest.approx(3.8)
    assert goal_y == pytest.approx(6.0)
    assert yaw == pytest.approx(0.0)


@pytest.mark.parametrize(
    ('previous', 'current', 'expected'),
    [
        (True, False, True),
        (True, True, False),
        (False, False, False),
        (False, True, False),
        (None, False, False),
    ],
)
def test_only_safe_to_out_of_bounds_is_a_trigger(
    previous, current, expected
):
    assert is_out_of_bounds_transition(previous, current) is expected
