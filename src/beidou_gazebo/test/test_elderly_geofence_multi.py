"""Unit tests for independent dual-layer elderly risk classification."""

from beidou_gazebo.elderly_geofence import ObstacleZone
from beidou_gazebo.elderly_geofence_multi import (
    MultiElderlyRiskTracker,
    STATE_DANGER,
    STATE_SAFE,
    STATE_UNKNOWN,
    STATE_WARNING,
)
import pytest


ZONE = ObstacleZone('test_zone', ((0.0, 0.0), (1.0, 0.0),
                                  (1.0, 1.0), (0.0, 1.0)))


def tracker(ids=('elder_01',)):
    return MultiElderlyRiskTracker(ids, [ZONE])


def update(t, elderly_id, x, y, stamp=1.0, motion=True):
    t.update_position(elderly_id, x, y, stamp, True, 'map')
    t.update_motion(elderly_id, stamp, motion)


def test_far_position_is_safe():
    t = tracker()
    update(t, 'elder_01', 3.0, 3.0)
    state, distance, valid = t.evaluate('elder_01', 1.1)
    assert state == STATE_SAFE
    assert distance > 1.2
    assert valid is True


def test_warning_and_danger_entries():
    t = tracker()
    update(t, 'elder_01', 2.0, 0.5)
    assert t.evaluate('elder_01', 1.1)[0] == STATE_WARNING
    update(t, 'elder_01', 1.4, 0.5, 2.0)
    assert t.evaluate('elder_01', 2.1)[0] == STATE_DANGER


def test_danger_holds_until_danger_exit_then_warning():
    t = tracker()
    update(t, 'elder_01', 1.4, 0.5)
    assert t.evaluate('elder_01', 1.1)[0] == STATE_DANGER
    update(t, 'elder_01', 1.6, 0.5, 2.0)
    assert t.evaluate('elder_01', 2.1)[0] == STATE_DANGER
    update(t, 'elder_01', 1.8, 0.5, 3.0)
    assert t.evaluate('elder_01', 3.1)[0] == STATE_WARNING


def test_danger_exits_to_safe_beyond_warning_exit():
    t = tracker()
    update(t, 'elder_01', 1.4, 0.5)
    assert t.evaluate('elder_01', 1.1)[0] == STATE_DANGER
    update(t, 'elder_01', 2.3, 0.5, 2.0)
    assert t.evaluate('elder_01', 2.1)[0] == STATE_SAFE


def test_warning_holds_until_warning_exit():
    t = tracker()
    update(t, 'elder_01', 2.0, 0.5)
    assert t.evaluate('elder_01', 1.1)[0] == STATE_WARNING
    update(t, 'elder_01', 2.1, 0.5, 2.0)
    assert t.evaluate('elder_01', 2.1)[0] == STATE_WARNING
    update(t, 'elder_01', 2.3, 0.5, 3.0)
    assert t.evaluate('elder_01', 3.1)[0] == STATE_SAFE


def test_invalid_position_or_motion_is_unknown():
    t = tracker()
    t.update_position('elder_01', 3.0, 3.0, 1.0, False, 'map')
    t.update_motion('elder_01', 1.0, True)
    assert t.evaluate('elder_01', 1.1)[0] == STATE_UNKNOWN
    update(t, 'elder_01', 3.0, 3.0, 2.0, motion=False)
    assert t.evaluate('elder_01', 2.1)[0] == STATE_UNKNOWN


def test_timeout_is_unknown():
    t = tracker()
    update(t, 'elder_01', 3.0, 3.0, 1.0)
    state, distance, valid = t.evaluate('elder_01', 2.01)
    assert state == STATE_UNKNOWN
    assert distance != distance  # NaN sentinel
    assert valid is False


def test_five_tracks_are_independent():
    t = tracker(('elder', 'elder_01', 'elder_02', 'elder_03', 'elder_04'))
    update(t, 'elder', 3.0, 3.0)
    update(t, 'elder_01', 2.0, 0.5)
    update(t, 'elder_02', 1.4, 0.5)
    update(t, 'elder_03', 3.0, 3.0)
    update(t, 'elder_04', 3.0, 3.0, motion=False)
    states = [t.evaluate(elderly_id, 1.1)[0]
              for elderly_id in t.elderly_ids]
    assert states == [STATE_SAFE, STATE_WARNING, STATE_DANGER,
                      STATE_SAFE, STATE_UNKNOWN]
