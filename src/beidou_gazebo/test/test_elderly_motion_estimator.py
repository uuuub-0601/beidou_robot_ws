"""Tests for filtered elderly motion estimation."""

import math

from beidou_gazebo.elderly_motion_estimator import WindowedMotionEstimator
import pytest


def feed_line(estimator, speed, start=0.0, duration=1.0, step=0.05):
    """Feed a straight x-axis trajectory."""
    count = int(duration / step) + 1
    for index in range(count):
        stamp = start + index * step
        estimator.add_sample(stamp, speed * stamp, 0.0)
    return start + (count - 1) * step


def test_startup_is_invalid_until_window_has_enough_data():
    estimator = WindowedMotionEstimator(minimum_span=0.4)
    for index in range(4):
        estimator.add_sample(index * 0.05, index * 0.02, 0.0)
    assert estimator.estimate(0.15).valid is False


@pytest.mark.parametrize('speed', [0.2, 0.3, 0.4])
def test_windowed_fit_estimates_constant_speed(speed):
    estimator = WindowedMotionEstimator()
    final_stamp = feed_line(estimator, speed)
    estimate = estimator.estimate(final_stamp)
    assert estimate.valid is True
    assert estimate.vx == pytest.approx(speed, abs=1e-6)
    assert estimate.vy == pytest.approx(0.0, abs=1e-6)
    assert estimate.speed == pytest.approx(speed, abs=1e-6)
    assert estimate.heading == pytest.approx(0.0, abs=1e-6)


def test_regression_filters_position_noise():
    estimator = WindowedMotionEstimator()
    for index in range(21):
        stamp = index * 0.05
        noise = 0.006 if index % 2 else -0.006
        estimator.add_sample(stamp, 0.3 * stamp + noise, 0.0)
    assert estimator.estimate(1.0).speed == pytest.approx(0.3, abs=0.01)


def test_position_jump_is_rejected():
    estimator = WindowedMotionEstimator()
    feed_line(estimator, 0.3, duration=0.6)
    accepted = estimator.add_sample(0.65, 5.0, 5.0)
    assert accepted is False
    assert estimator.rejected_samples == 1
    assert estimator.estimate(0.65).speed == pytest.approx(0.3, abs=1e-6)


def test_timeout_sets_invalid_without_inventing_velocity():
    estimator = WindowedMotionEstimator(timeout=0.5)
    final_stamp = feed_line(estimator, 0.3)
    estimate = estimator.estimate(final_stamp + 0.51)
    assert estimate.valid is False
    assert estimate.vx == 0.0
    assert estimate.vy == 0.0
    assert estimate.speed == 0.0


def test_heading_freezes_after_motion_stops():
    estimator = WindowedMotionEstimator(heading_speed_threshold=0.05)
    for index in range(21):
        stamp = index * 0.05
        estimator.add_sample(stamp, 0.0, 0.3 * stamp)
    moving = estimator.estimate(1.0)
    assert moving.heading == pytest.approx(math.pi / 2.0)

    stop_y = 0.3
    for index in range(1, 22):
        stamp = 1.0 + index * 0.05
        estimator.add_sample(stamp, 0.0, stop_y)
    stopped = estimator.estimate(2.05)
    assert stopped.valid is True
    assert stopped.speed == pytest.approx(0.0, abs=1e-6)
    assert stopped.heading == pytest.approx(math.pi / 2.0)


def test_high_rate_frame_jitter_does_not_break_window_estimation():
    estimator = WindowedMotionEstimator()
    for index in range(61):
        stamp = index * 0.02
        jitter = 0.02 if index % 2 else -0.02
        estimator.add_sample(stamp, 0.3 * stamp + jitter, 0.0)
    estimate = estimator.estimate(1.2)
    assert estimate.valid is True
    assert estimate.speed == pytest.approx(0.3, abs=0.01)


def test_consistent_samples_rebase_after_persistent_position_jump():
    estimator = WindowedMotionEstimator()
    feed_line(estimator, 0.3, duration=0.6)
    assert estimator.add_sample(0.65, 5.0, 5.0) is False
    assert estimator.add_sample(0.70, 5.015, 5.0) is True
    for index in range(1, 22):
        stamp = 0.70 + index * 0.05
        estimator.add_sample(stamp, 5.015 + 0.3 * index * 0.05, 5.0)
    estimate = estimator.estimate(1.75)
    assert estimate.valid is True
    assert estimate.speed == pytest.approx(0.3, abs=1e-6)
