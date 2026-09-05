"""Estimate independent planar motion for multiple elderly tracks."""

from beidou_gazebo.elderly_motion_estimator import WindowedMotionEstimator
from beidou_interfaces.msg import (
    ElderlyMotionArray,
    ElderlyMotionStamped,
    ElderlyPositionArray,
)
import rclpy
from rclpy.node import Node

DEFAULT_ELDERLY_IDS = ('elder', 'elder_01', 'elder_02', 'elder_03', 'elder_04')


def stamp_to_seconds(stamp):
    return float(stamp.sec) + float(stamp.nanosec) * 1e-9


class MultiElderlyMotionTracker:
    """Maintain one isolated windowed estimator per stable elderly ID."""

    def __init__(self, elderly_ids, estimator_kwargs=None):
        self.estimator_kwargs = dict(estimator_kwargs or {})
        self.estimators = {}
        self.frames = {}
        self.input_valid = {}
        for elderly_id in elderly_ids:
            self.ensure_id(elderly_id)

    def ensure_id(self, elderly_id):
        if elderly_id and elderly_id not in self.estimators:
            self.estimators[elderly_id] = WindowedMotionEstimator(
                **self.estimator_kwargs
            )
            self.frames[elderly_id] = 'map'
            self.input_valid[elderly_id] = False

    def update(self, elderly_id, stamp, x, y, frame_id='map', valid=True):
        self.ensure_id(elderly_id)
        if not elderly_id:
            return False
        if not valid or frame_id != 'map':
            self.input_valid[elderly_id] = False
            return False
        accepted = self.estimators[elderly_id].add_sample(stamp, x, y)
        self.input_valid[elderly_id] = accepted
        if accepted:
            self.frames[elderly_id] = frame_id
        return accepted

    def mark_missing_invalid(self, observed_ids):
        observed = set(observed_ids)
        for elderly_id in self.estimators:
            if elderly_id not in observed:
                self.input_valid[elderly_id] = False

    def estimate(self, elderly_id, now):
        estimate = self.estimators[elderly_id].estimate(now)
        if not self.input_valid[elderly_id] or not estimate.valid:
            return type(estimate)(heading=estimate.heading, valid=False)
        return estimate


class MultiElderlyMotionEstimator(Node):
    """Convert a position array into independent motion estimates."""

    def __init__(self):
        super().__init__('multi_elderly_motion_estimator')
        defaults = (
            ('window_duration', 0.8), ('minimum_samples', 5),
            ('minimum_span', 0.4), ('jump_distance', 0.5),
            ('jump_speed', 1.5), ('heading_speed_threshold', 0.05),
            ('data_timeout', 0.5), ('publish_frequency', 20.0),
        )
        for name, value in defaults:
            self.declare_parameter(name, value)
        self.declare_parameter('elderly_ids', list(DEFAULT_ELDERLY_IDS))
        publish_frequency = self._positive('publish_frequency')
        minimum_samples = int(self.get_parameter('minimum_samples').value)
        if minimum_samples < 2:
            raise ValueError('minimum_samples must be at least 2')
        elderly_ids = tuple(dict.fromkeys(
            str(value) for value in self.get_parameter('elderly_ids').value
        ))
        if not elderly_ids:
            raise ValueError('elderly_ids must contain at least one ID')
        self.tracker = MultiElderlyMotionTracker(elderly_ids, {
            'window_duration': self._positive('window_duration'),
            'minimum_samples': minimum_samples,
            'minimum_span': self._positive('minimum_span'),
            'jump_distance': self._positive('jump_distance'),
            'jump_speed': self._positive('jump_speed'),
            'heading_speed_threshold': self._positive('heading_speed_threshold'),
            'timeout': self._positive('data_timeout'),
        })
        self.motion_publisher = self.create_publisher(
            ElderlyMotionArray, '/elderly/motions', 10
        )
        self.create_subscription(
            ElderlyPositionArray, '/elderly/positions',
            self._positions_callback, 20
        )
        self.create_timer(1.0 / publish_frequency, self._publish_motions)

    def _positive(self, name):
        value = float(self.get_parameter(name).value)
        if value <= 0.0:
            raise ValueError(f'{name} must be positive')
        return value

    def _positions_callback(self, message):
        now_seconds = self.get_clock().now().nanoseconds * 1e-9
        array_stamp = stamp_to_seconds(message.header.stamp)
        observed_ids = []
        for position in message.positions:
            elderly_id = position.elderly_id
            if not elderly_id:
                continue
            observed_ids.append(elderly_id)
            stamp = stamp_to_seconds(position.header.stamp)
            if stamp <= 0.0:
                stamp = array_stamp if array_stamp > 0.0 else now_seconds
            self.tracker.update(
                elderly_id, stamp, position.pose.position.x,
                position.pose.position.y,
                position.header.frame_id or message.header.frame_id or 'map',
                position.valid,
            )
        self.tracker.mark_missing_invalid(observed_ids)

    def _publish_motions(self):
        now = self.get_clock().now()
        output = ElderlyMotionArray()
        output.header.stamp = now.to_msg()
        output.header.frame_id = 'map'
        for elderly_id in self.tracker.estimators:
            estimate = self.tracker.estimate(elderly_id, now.nanoseconds * 1e-9)
            motion = ElderlyMotionStamped()
            motion.header.stamp = output.header.stamp
            motion.header.frame_id = self.tracker.frames[elderly_id]
            motion.elderly_id = elderly_id
            motion.vx = estimate.vx
            motion.vy = estimate.vy
            motion.speed = estimate.speed
            motion.heading = estimate.heading
            motion.valid = estimate.valid
            output.motions.append(motion)
        self.motion_publisher.publish(output)


def main(args=None):
    rclpy.init(args=args)
    node = MultiElderlyMotionEstimator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
