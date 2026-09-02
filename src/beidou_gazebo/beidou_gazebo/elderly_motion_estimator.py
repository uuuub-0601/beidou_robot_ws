"""Estimate filtered elderly planar motion from Beidou positions."""

from collections import deque
from dataclasses import dataclass
import math

from beidou_interfaces.msg import ElderlyMotion
from geometry_msgs.msg import PoseStamped
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, String


@dataclass(frozen=True)
class MotionEstimate:
    """Planar velocity estimate and its validity."""

    vx: float = 0.0
    vy: float = 0.0
    speed: float = 0.0
    heading: float = 0.0
    valid: bool = False


class WindowedMotionEstimator:
    """Fit velocity over a time window while rejecting position jumps."""

    def __init__(
        self,
        window_duration=0.8,
        minimum_samples=5,
        minimum_span=0.4,
        jump_distance=0.5,
        jump_speed=1.5,
        heading_speed_threshold=0.05,
        timeout=0.5,
    ):
        self.window_duration = float(window_duration)
        self.minimum_samples = int(minimum_samples)
        self.minimum_span = float(minimum_span)
        self.jump_distance = float(jump_distance)
        self.jump_speed = float(jump_speed)
        self.heading_speed_threshold = float(heading_speed_threshold)
        self.timeout = float(timeout)
        self.samples = deque()
        self.last_heading = 0.0
        self.last_estimate = MotionEstimate()
        self.rejected_samples = 0
        self.pending_rebase = None
        self.jump_speed_minimum_interval = 0.1

    def add_sample(self, stamp, x, y):
        """Add a timestamped point and return whether it was accepted."""
        stamp = float(stamp)
        x = float(x)
        y = float(y)
        if self.samples:
            last_stamp, last_x, last_y = self.samples[-1]
            elapsed = stamp - last_stamp
            if elapsed <= 0.0:
                self.rejected_samples += 1
                return False
            displacement = math.hypot(x - last_x, y - last_y)
            sample_speed = displacement / elapsed
            speed_jump = (
                elapsed >= self.jump_speed_minimum_interval
                and sample_speed > self.jump_speed
            )
            if displacement > self.jump_distance or speed_jump:
                candidate = (stamp, x, y)
                if self._can_rebase(candidate):
                    self.samples.clear()
                    self.pending_rebase = None
                else:
                    self.pending_rebase = candidate
                    self.rejected_samples += 1
                    return False
            else:
                self.pending_rebase = None

        self.samples.append((stamp, x, y))
        cutoff = stamp - self.window_duration
        while len(self.samples) > 1 and self.samples[0][0] < cutoff:
            self.samples.popleft()
        self.last_estimate = self._fit()
        return True

    def _can_rebase(self, candidate):
        if self.pending_rebase is None:
            return False
        stamp, x, y = candidate
        previous_stamp, previous_x, previous_y = self.pending_rebase
        elapsed = stamp - previous_stamp
        if elapsed <= 0.0 or elapsed > self.timeout:
            return False
        displacement = math.hypot(x - previous_x, y - previous_y)
        return (
            displacement <= self.jump_distance
            and displacement / elapsed <= self.jump_speed
        )

    def estimate(self, now):
        """Return the latest estimate, invalidating stale input."""
        if not self.samples or float(now) - self.samples[-1][0] > self.timeout:
            return MotionEstimate(heading=self.last_heading, valid=False)
        return self.last_estimate

    def _fit(self):
        if len(self.samples) < self.minimum_samples:
            return MotionEstimate(heading=self.last_heading, valid=False)
        span = self.samples[-1][0] - self.samples[0][0]
        if span < self.minimum_span:
            return MotionEstimate(heading=self.last_heading, valid=False)

        count = len(self.samples)
        mean_time = sum(sample[0] for sample in self.samples) / count
        denominator = sum(
            (sample[0] - mean_time) ** 2 for sample in self.samples
        )
        if denominator <= 1e-12:
            return MotionEstimate(heading=self.last_heading, valid=False)
        mean_x = sum(sample[1] for sample in self.samples) / count
        mean_y = sum(sample[2] for sample in self.samples) / count
        vx = sum(
            (sample[0] - mean_time) * (sample[1] - mean_x)
            for sample in self.samples
        ) / denominator
        vy = sum(
            (sample[0] - mean_time) * (sample[2] - mean_y)
            for sample in self.samples
        ) / denominator
        speed = math.hypot(vx, vy)
        if speed >= self.heading_speed_threshold:
            self.last_heading = math.atan2(vy, vx)
        return MotionEstimate(vx, vy, speed, self.last_heading, True)


class ElderlyMotionEstimator(Node):
    """Publish filtered elderly velocity without changing Beidou data."""

    def __init__(self):
        super().__init__('elderly_motion_estimator')
        defaults = (
            ('window_duration', 0.8),
            ('minimum_samples', 5),
            ('minimum_span', 0.4),
            ('jump_distance', 0.5),
            ('jump_speed', 1.5),
            ('heading_speed_threshold', 0.05),
            ('data_timeout', 0.5),
            ('publish_frequency', 20.0),
        )
        for name, value in defaults:
            self.declare_parameter(name, value)

        publish_frequency = float(
            self.get_parameter('publish_frequency').value
        )
        if publish_frequency <= 0.0:
            raise ValueError('publish_frequency must be positive')
        self.estimator = WindowedMotionEstimator(
            window_duration=self._positive('window_duration'),
            minimum_samples=int(self.get_parameter('minimum_samples').value),
            minimum_span=self._positive('minimum_span'),
            jump_distance=self._positive('jump_distance'),
            jump_speed=self._positive('jump_speed'),
            heading_speed_threshold=self._positive(
                'heading_speed_threshold'
            ),
            timeout=self._positive('data_timeout'),
        )
        if self.estimator.minimum_samples < 2:
            raise ValueError('minimum_samples must be at least 2')

        self.latest_frame = 'map'
        self.motion_publisher = self.create_publisher(
            ElderlyMotion, '/elderly_motion', 10
        )
        self.speed_publisher = self.create_publisher(
            Float64, '/elderly_speed', 10
        )
        self.state_publisher = self.create_publisher(
            String, '/elderly_motion_state', 10
        )
        self.create_subscription(
            PoseStamped,
            '/elderly_position',
            self._position_callback,
            20,
        )
        self.create_timer(1.0 / publish_frequency, self._publish_motion)

    def _positive(self, name):
        value = float(self.get_parameter(name).value)
        if value <= 0.0:
            raise ValueError(f'{name} must be positive')
        return value

    def _position_callback(self, message):
        stamp = (
            float(message.header.stamp.sec)
            + float(message.header.stamp.nanosec) * 1e-9
        )
        if stamp <= 0.0:
            stamp = self.get_clock().now().nanoseconds * 1e-9
        accepted = self.estimator.add_sample(
            stamp,
            message.pose.position.x,
            message.pose.position.y,
        )
        if accepted:
            self.latest_frame = message.header.frame_id or 'map'

    def _publish_motion(self):
        now = self.get_clock().now()
        estimate = self.estimator.estimate(now.nanoseconds * 1e-9)
        message = ElderlyMotion()
        message.header.stamp = now.to_msg()
        message.header.frame_id = self.latest_frame
        message.vx = estimate.vx
        message.vy = estimate.vy
        message.speed = estimate.speed
        message.heading = estimate.heading
        message.valid = estimate.valid
        self.motion_publisher.publish(message)
        self.speed_publisher.publish(Float64(data=estimate.speed))
        if not estimate.valid:
            state = 'INVALID'
        elif estimate.speed >= self.estimator.heading_speed_threshold:
            state = 'MOVING'
        else:
            state = 'STATIONARY'
        self.state_publisher.publish(String(data=state))


def main(args=None):
    rclpy.init(args=args)
    node = ElderlyMotionEstimator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
