"""Unit tests for Stage 5A/5B safety event management."""

import math

from beidou_gazebo.elderly_safety_manager import (
    EVENT_DANGER_ENTER,
    EVENT_DANGER_EXIT,
    EVENT_WARNING_ENTER,
    EVENT_WARNING_EXIT,
    MANAGER_EVENT_SELECTED,
    MANAGER_ARRIVED_NEAR_ELDERLY,
    MANAGER_GO_TO_ELDERLY,
    MANAGER_NAVIGATION_FAILED,
    MANAGER_MONITORING,
    STATE_DANGER,
    STATE_SAFE,
    STATE_UNKNOWN,
    STATE_WARNING,
    SafetyEventManager,
    NavigationCoordinator,
    compute_approach_pose,
)


def process(manager, elderly_id, state, distance, stamp):
    risks = []
    for current_id in manager.elderly_ids:
        track = manager.tracks[current_id]
        risks.append({
            'elderly_id': current_id,
            'state': state if current_id == elderly_id else track.state,
            'distance_to_danger': (
                distance if current_id == elderly_id else track.last_distance
            ),
        })
    return manager.process(risks, stamp)


def test_warning_enter_is_one_shot_and_exits():
    manager = SafetyEventManager(['elder_01'])
    events = process(manager, 'elder_01', STATE_SAFE, 2.0, 1.0)
    assert events == []
    events = process(manager, 'elder_01', STATE_WARNING, 0.9, 2.0)
    assert len(events) == 1 and events[0].event_type == EVENT_WARNING_ENTER
    event_id = events[0].event_id
    assert process(manager, 'elder_01', STATE_WARNING, 0.9, 3.0) == []
    events = process(manager, 'elder_01', STATE_SAFE, 1.3, 4.0)
    assert events[0].event_type == EVENT_WARNING_EXIT
    assert events[0].event_id == event_id


def test_danger_enter_priority_and_one_shot():
    manager = SafetyEventManager(['elder_01'])
    process(manager, 'elder_01', STATE_SAFE, 2.0, 1.0)
    events = process(manager, 'elder_01', STATE_DANGER, 0.0, 2.0)
    assert events[0].event_type == EVENT_DANGER_ENTER
    assert events[0].priority == 'HIGH'
    assert process(manager, 'elder_01', STATE_DANGER, 0.0, 3.0) == []


def test_danger_to_warning_emits_exit_without_safe():
    manager = SafetyEventManager(['elder_01'])
    process(manager, 'elder_01', STATE_SAFE, 2.0, 1.0)
    process(manager, 'elder_01', STATE_DANGER, 0.0, 2.0)
    events = process(manager, 'elder_01', STATE_WARNING, 0.6, 3.0)
    assert events[0].event_type == EVENT_DANGER_EXIT
    assert manager.tracks['elder_01'].state == STATE_WARNING


def test_danger_unknown_does_not_emit_exit():
    manager = SafetyEventManager(['elder_01'])
    process(manager, 'elder_01', STATE_SAFE, 2.0, 1.0)
    process(manager, 'elder_01', STATE_DANGER, 0.0, 2.0)
    assert process(manager, 'elder_01', STATE_UNKNOWN, float('nan'), 3.0) == []
    assert manager.tracks['elder_01'].event_id


def test_unknown_recovery_closes_episode_and_reentry_gets_new_id():
    manager = SafetyEventManager(['elder_01'])
    process(manager, 'elder_01', STATE_SAFE, 2.0, 1.0)
    first = process(manager, 'elder_01', STATE_DANGER, 0.0, 2.0)[0]
    process(manager, 'elder_01', STATE_UNKNOWN, float('nan'), 3.0)
    events = process(manager, 'elder_01', STATE_SAFE, 2.0, 4.0)
    assert events[0].event_type == EVENT_DANGER_EXIT
    second = process(manager, 'elder_01', STATE_DANGER, 0.0, 5.0)[0]
    assert second.event_id != first.event_id


def test_danger_priority_over_warning_and_earliest_danger_wins():
    manager = SafetyEventManager(['elder_01', 'elder_02', 'elder_03'])
    process(manager, 'elder_01', STATE_SAFE, 2.0, 1.0)
    process(manager, 'elder_02', STATE_SAFE, 2.0, 1.0)
    process(manager, 'elder_03', STATE_SAFE, 2.0, 1.0)
    process(manager, 'elder_01', STATE_WARNING, 0.9, 2.0)
    process(manager, 'elder_02', STATE_DANGER, 0.0, 3.0)
    process(manager, 'elder_03', STATE_DANGER, 0.0, 4.0)
    assert manager.current_event()[0] == 'elder_02'
    assert manager.manager_state == MANAGER_EVENT_SELECTED


def test_danger_tie_breaks_by_id_and_unknown_is_not_selected():
    manager = SafetyEventManager(['elder_02', 'elder_01', 'elder_03'])
    process(manager, 'elder_01', STATE_DANGER, 0.0, 1.0)
    process(manager, 'elder_02', STATE_DANGER, 0.0, 1.0)
    process(manager, 'elder_03', STATE_UNKNOWN, float('nan'), 1.0)
    assert manager.current_event()[0] == 'elder_01'


def test_all_safe_or_unknown_returns_monitoring():
    manager = SafetyEventManager(['elder_01', 'elder_02'])
    process(manager, 'elder_01', STATE_SAFE, 2.0, 1.0)
    process(manager, 'elder_02', STATE_UNKNOWN, float('nan'), 1.0)
    assert manager.current_event() is None
    assert manager.manager_state == MANAGER_MONITORING


def set_danger(manager, elderly_id, stamp):
    """Set one ID to DANGER while preserving a complete risk array."""
    risks = []
    for current_id in manager.elderly_ids:
        track = manager.tracks[current_id]
        risks.append({
            'elderly_id': current_id,
            'state': STATE_DANGER if current_id == elderly_id else track.state,
            'distance_to_danger': 0.0 if current_id == elderly_id
            else track.last_distance,
        })
    return manager.process(risks, stamp)


def test_equal_entry_time_prefers_nearer_robot_distance():
    manager = SafetyEventManager(['elder_01', 'elder_02'])
    manager.set_robot_pose(0.0, 0.0)
    for elderly_id, point in (('elder_01', (1.0, 0.0)),
                              ('elder_02', (5.0, 0.0))):
        manager.update_position(elderly_id, *point, 1.0, True, 'map')
    set_danger(manager, 'elder_01', 10.0)
    set_danger(manager, 'elder_02', 10.0)
    assert manager.current_event()[0] == 'elder_01'
    assert manager.tracks['elder_01'].robot_distance == 1.0


def test_equal_entry_time_uses_nearest_when_second_is_closer():
    manager = SafetyEventManager(['elder_01', 'elder_02'])
    manager.set_robot_pose(0.0, 0.0)
    manager.update_position('elder_01', 5.0, 0.0, 1.0, True, 'map')
    manager.update_position('elder_02', 1.0, 0.0, 1.0, True, 'map')
    set_danger(manager, 'elder_01', 10.0)
    set_danger(manager, 'elder_02', 10.0)
    assert manager.current_event()[0] == 'elder_02'


def test_earlier_danger_entry_beats_nearer_distance():
    manager = SafetyEventManager(['elder_01', 'elder_02'])
    manager.set_robot_pose(0.0, 0.0)
    manager.update_position('elder_01', 5.0, 0.0, 1.0, True, 'map')
    manager.update_position('elder_02', 1.0, 0.0, 1.0, True, 'map')
    set_danger(manager, 'elder_01', 10.0)
    set_danger(manager, 'elder_02', 20.0)
    assert manager.current_event()[0] == 'elder_01'


def test_equal_entry_and_distance_uses_id_tiebreak():
    manager = SafetyEventManager(['elder_02', 'elder_01'])
    manager.set_robot_pose(0.0, 0.0)
    manager.update_position('elder_01', 1.0, 0.0, 1.0, True, 'map')
    manager.update_position('elder_02', -1.0, 0.0, 1.0, True, 'map')
    set_danger(manager, 'elder_02', 10.0)
    set_danger(manager, 'elder_01', 10.0)
    assert manager.current_event()[0] == 'elder_01'


def test_invalid_robot_pose_falls_back_to_id_order():
    manager = SafetyEventManager(['elder_02', 'elder_01'])
    manager.set_robot_pose(0.0, 0.0, False)
    set_danger(manager, 'elder_02', 10.0)
    set_danger(manager, 'elder_01', 10.0)
    assert manager.current_event()[0] == 'elder_01'
    assert math.isinf(manager.tracks['elder_01'].robot_distance)


def test_non_map_position_is_not_used_for_distance():
    manager = SafetyEventManager(['elder_01'])
    manager.set_robot_pose(0.0, 0.0)
    manager.update_position('elder_01', 1.0, 0.0, 1.0, True, 'odom')
    set_danger(manager, 'elder_01', 10.0)
    assert math.isinf(manager.tracks['elder_01'].robot_distance)


def test_approach_pose_is_between_robot_and_elderly_and_faces_elderly():
    approach = compute_approach_pose(0.0, 0.0, 5.0, 0.0, 1.3)
    assert approach.x == 3.7
    assert approach.y == 0.0
    assert approach.yaw == 0.0


def test_navigation_coordinator_sends_one_goal_and_reaches():
    coordinator = NavigationCoordinator()
    assert coordinator.can_start('elder_01-DANGER-0001', 'elder_01',
                                 STATE_DANGER)
    assert coordinator.begin('elder_01-DANGER-0001', 'elder_01')
    assert coordinator.state == MANAGER_GO_TO_ELDERLY
    assert not coordinator.can_start('elder_01-DANGER-0001', 'elder_01',
                                     STATE_DANGER)
    assert coordinator.goal_sent_count == 1
    coordinator.result(True)
    assert coordinator.state == MANAGER_ARRIVED_NEAR_ELDERLY


def test_navigation_failure_is_terminal_without_retry():
    coordinator = NavigationCoordinator()
    coordinator.begin('elder_01-DANGER-0001', 'elder_01')
    coordinator.result(False)
    assert coordinator.state == MANAGER_NAVIGATION_FAILED
    assert not coordinator.can_start('elder_01-DANGER-0001', 'elder_01',
                                     STATE_DANGER)


def test_navigation_cancel_clears_active_goal():
    coordinator = NavigationCoordinator()
    coordinator.begin('elder_01-DANGER-0001', 'elder_01')
    assert coordinator.cancel()
    assert coordinator.active_event_id == ''
    assert coordinator.state == MANAGER_MONITORING
