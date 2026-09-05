"""Unit tests for Stage 5A safety event management."""

from beidou_gazebo.elderly_safety_manager import (
    EVENT_DANGER_ENTER,
    EVENT_DANGER_EXIT,
    EVENT_WARNING_ENTER,
    EVENT_WARNING_EXIT,
    MANAGER_EVENT_SELECTED,
    MANAGER_MONITORING,
    STATE_DANGER,
    STATE_SAFE,
    STATE_UNKNOWN,
    STATE_WARNING,
    SafetyEventManager,
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
