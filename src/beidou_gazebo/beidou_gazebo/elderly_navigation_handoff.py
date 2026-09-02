"""Arbitrate the sole NavigateToPose owner between Companion and Guard."""

from enum import Enum
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String


class HandoffState(str, Enum):
    FOLLOW = 'FOLLOW'
    TRANSITION = 'TRANSITION'
    GUARD = 'GUARD'
    RETURN_TO_FOLLOW = 'RETURN_TO_FOLLOW'
    UNKNOWN_HOLD = 'UNKNOWN_HOLD'


class ElderlyNavigationHandoff(Node):
    def __init__(self):
        super().__init__('elderly_navigation_handoff')
        self.declare_parameter('safe_recovery_time', 3.0)
        self.declare_parameter('transition_timeout', 5.0)
        self.declare_parameter('guard_goal_timeout', 30.0)
        self.safe_recovery_time = float(self.get_parameter('safe_recovery_time').value)
        self.transition_timeout = float(self.get_parameter('transition_timeout').value)
        self.guard_goal_timeout = float(self.get_parameter('guard_goal_timeout').value)
        if self.safe_recovery_time < 0 or self.transition_timeout <= 0 or self.guard_goal_timeout <= 0:
            raise ValueError('handoff timing parameters are invalid')

        durable = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                             durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.mode_pub = self.create_publisher(String, '/elderly_navigation_mode', durable)
        self.create_subscription(String, '/elderly_geofence_state', self._geofence_cb, durable)
        self.create_subscription(String, '/elderly_companion_handoff_state', self._companion_cb, durable)
        self.create_subscription(String, '/elderly_guard_handoff_state', self._guard_cb, durable)
        self.state = HandoffState.FOLLOW
        self.geofence = 'UNKNOWN'
        self.previous_valid_geofence = None
        self.companion = 'ACTIVE'
        self.guard = 'IDLE'
        self.transition_started = None
        self.guard_started = None
        self.safe_started = None
        self._publish_mode()
        self.create_timer(0.1, self._tick)

    def _now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def _publish_mode(self):
        self.mode_pub.publish(String(data=self.state.value))

    def _set_state(self, state):
        if state != self.state:
            self.state = state
            self.get_logger().info(f'[HANDOFF] mode -> {state.value}')
            self._publish_mode()

    def _geofence_cb(self, msg):
        value = str(msg.data).strip().upper()
        if value not in ('SAFE', 'WARNING', 'DANGER', 'UNKNOWN'):
            return
        old = self.geofence
        self.geofence = value
        if value in ('SAFE', 'WARNING', 'DANGER'):
            if value == 'DANGER' and old in ('SAFE', 'WARNING'):
                if self.state == HandoffState.FOLLOW:
                    self.transition_started = self._now()
                    self._set_state(HandoffState.TRANSITION)
            self.previous_valid_geofence = value
        if self.state == HandoffState.GUARD and value == 'SAFE':
            if self.safe_started is None:
                self.safe_started = self._now()
        elif value != 'SAFE':
            self.safe_started = None

    def _companion_cb(self, msg):
        self.companion = str(msg.data).strip().upper()

    def _guard_cb(self, msg):
        self.guard = str(msg.data).strip().upper()

    def _tick(self):
        now = self._now()
        if self.state == HandoffState.TRANSITION:
            if self.companion == 'PAUSED':
                self.transition_started = None
                self.guard_started = now
                self._set_state(HandoffState.GUARD)
            elif self.transition_started is not None and now - self.transition_started > self.transition_timeout:
                self.get_logger().error('[HANDOFF] Companion pause timeout; holding TRANSITION')
        elif self.state == HandoffState.GUARD:
            if (self.guard_started is not None and self.guard not in ('GOAL_SENT', 'GUARDING')
                    and now - self.guard_started > self.guard_goal_timeout):
                self.get_logger().error('[HANDOFF] Guard goal timeout; retaining GUARD')
                self.guard_started = now
            if self.geofence == 'SAFE' and self.safe_started is not None and now - self.safe_started >= self.safe_recovery_time:
                self._set_state(HandoffState.RETURN_TO_FOLLOW)
        elif self.state == HandoffState.RETURN_TO_FOLLOW:
            if self.guard in ('RELEASED', 'IDLE', 'FAILED'):
                self.safe_started = None
                self._set_state(HandoffState.FOLLOW)


def main(args=None):
    rclpy.init(args=args)
    node = ElderlyNavigationHandoff()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
