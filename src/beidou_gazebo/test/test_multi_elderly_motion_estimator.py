"""Tests for independent multi-elderly motion tracking."""
import math
from beidou_gazebo.multi_elderly_motion_estimator import MultiElderlyMotionTracker
import pytest


def feed_track(tracker, elderly_id, vx, vy):
    for index in range(21):
        stamp = index * 0.05
        assert tracker.update(elderly_id, stamp, vx * stamp, vy * stamp)
    return tracker.estimate(elderly_id, 1.0)


def test_stationary_track_is_valid_with_zero_speed():
    estimate = feed_track(MultiElderlyMotionTracker(['elder_01']), 'elder_01', 0.0, 0.0)
    assert estimate.valid is True
    assert estimate.speed == pytest.approx(0.0, abs=1e-9)


def test_positive_x_motion_has_zero_heading():
    estimate = feed_track(MultiElderlyMotionTracker(['elder_01']), 'elder_01', 0.3, 0.0)
    assert estimate.valid is True
    assert estimate.vx == pytest.approx(0.3, abs=1e-6)
    assert estimate.vy == pytest.approx(0.0, abs=1e-6)
    assert estimate.heading == pytest.approx(0.0, abs=1e-6)


def test_positive_y_motion_has_pi_over_two_heading():
    estimate = feed_track(MultiElderlyMotionTracker(['elder_01']), 'elder_01', 0.0, 0.3)
    assert estimate.valid is True
    assert estimate.vx == pytest.approx(0.0, abs=1e-6)
    assert estimate.vy == pytest.approx(0.3, abs=1e-6)
    assert estimate.heading == pytest.approx(math.pi / 2.0, abs=1e-6)


def test_non_increasing_time_invalidates_only_that_track():
    tracker = MultiElderlyMotionTracker(['elder_01', 'elder_02'])
    feed_track(tracker, 'elder_01', 0.3, 0.0)
    feed_track(tracker, 'elder_02', 0.0, 0.0)
    assert tracker.update('elder_01', 1.0, 0.3, 0.0) is False
    assert tracker.estimate('elder_01', 1.0).valid is False
    assert tracker.estimate('elder_02', 1.0).valid is True


def test_multiple_tracks_do_not_share_motion_history():
    tracker = MultiElderlyMotionTracker(['elder_01', 'elder_02', 'elder_03'])
    moving = feed_track(tracker, 'elder_01', 0.25, 0.0)
    still_x = feed_track(tracker, 'elder_02', 0.0, 0.0)
    still_y = feed_track(tracker, 'elder_03', 0.0, 0.0)
    assert moving.speed == pytest.approx(0.25, abs=1e-6)
    assert still_x.speed == pytest.approx(0.0, abs=1e-9)
    assert still_y.speed == pytest.approx(0.0, abs=1e-9)


def test_timeout_invalidates_stale_track():
    tracker = MultiElderlyMotionTracker(['elder_01'])
    feed_track(tracker, 'elder_01', 0.3, 0.0)
    estimate = tracker.estimate('elder_01', 1.51)
    assert estimate.valid is False
    assert estimate.speed == 0.0
