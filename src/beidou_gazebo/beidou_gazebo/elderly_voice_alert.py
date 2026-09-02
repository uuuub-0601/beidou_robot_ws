"""Non-blocking voice alert for electronic-fence DANGER transitions."""

import os
import signal
import subprocess
import sys

from beidou_gazebo.piper_chinese_tts import DEFAULT_AUDIO_COMMAND
from beidou_gazebo.piper_chinese_tts import DEFAULT_MODEL_PATH
from beidou_gazebo.piper_chinese_tts import DEFAULT_PIPER_COMMAND
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String


STATE_IDLE = 'IDLE'
STATE_ALERTING = 'ALERTING'
STATE_DANGER = 'DANGER'


class ElderlyVoiceAlert(Node):
    """Speak once on each entry into DANGER, without blocking ROS callbacks."""

    def __init__(self):
        super().__init__('elderly_voice_alert')
        self.declare_parameter(
            'alert_text', '警告，您已进入危险区域，请立即离开。'
        )
        self.declare_parameter('piper_command', DEFAULT_PIPER_COMMAND)
        self.declare_parameter('piper_model', DEFAULT_MODEL_PATH)
        self.declare_parameter('audio_command', DEFAULT_AUDIO_COMMAND)

        self.alert_text = str(self.get_parameter('alert_text').value)
        self.piper_command = str(self.get_parameter('piper_command').value)
        self.piper_model = str(self.get_parameter('piper_model').value)
        self.audio_command = str(self.get_parameter('audio_command').value)
        self._in_danger = False
        self._process = None

        qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.state_pub = self.create_publisher(
            String, '/elderly_voice_alert_state', qos
        )
        self.create_subscription(
            String, '/elderly_geofence_state', self._state_callback, 10
        )
        self.create_timer(0.1, self._poll_speech)
        self._publish_state(STATE_IDLE)

        piper = os.path.expanduser(self.piper_command)
        model = os.path.expanduser(self.piper_model)
        if not (os.path.isfile(piper) and os.access(piper, os.X_OK)):
            self.get_logger().error(
                f'[VOICE ALERT] Piper executable not found: {piper}'
            )
        elif not os.path.isfile(model + '.json'):
            self.get_logger().error(
                f'[VOICE ALERT] Piper model config not found: {model}.json'
            )
        else:
            self.get_logger().info(
                f'[VOICE ALERT] Ready: Piper Mandarin model {model}'
            )

    def _publish_state(self, state):
        self.state_pub.publish(String(data=state))

    def _state_callback(self, message):
        state = message.data.strip().upper()
        if state == STATE_DANGER:
            if self._in_danger:
                return
            self._in_danger = True
            self.get_logger().warning('[VOICE ALERT] DANGER detected')
            self._start_speech()
            return

        # SAFE, WARNING, and UNKNOWN all re-arm the next DANGER transition.
        if self._in_danger:
            self._in_danger = False
            if self._process is not None and self._process.poll() is None:
                self._terminate_process()
                self.get_logger().info('[VOICE ALERT] Alert stopped')
            self._process = None
        self._publish_state(STATE_IDLE)

    def _start_speech(self):
        piper = os.path.expanduser(self.piper_command)
        model = os.path.expanduser(self.piper_model)
        audio = os.path.expanduser(self.audio_command)
        if not (os.path.isfile(piper) and os.access(piper, os.X_OK)):
            self._publish_state(STATE_IDLE)
            return
        command = [
            sys.executable, '-m', 'beidou_gazebo.piper_chinese_tts',
            '--piper-command', piper,
            '--model', model,
            '--audio-command', audio,
            self.alert_text,
        ]
        try:
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as error:
            self.get_logger().error(f'[VOICE ALERT] Playback failed: {error}')
            self._process = None
            self._publish_state(STATE_IDLE)
            return
        self._publish_state(STATE_ALERTING)
        self.get_logger().info('[VOICE ALERT] Playing warning')

    def _poll_speech(self):
        if self._process is None:
            return
        return_code = self._process.poll()
        if return_code is None:
            return
        self._process = None
        if self._in_danger:
            self._publish_state(STATE_IDLE)
        if return_code != 0:
            self.get_logger().error(
                f'[VOICE ALERT] TTS exited with code {return_code}'
            )

    def _terminate_process(self):
        """Stop Piper and its aplay child without blocking ROS."""
        if self._process is None or self._process.poll() is not None:
            return
        try:
            os.killpg(self._process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

    def destroy_node(self):
        if self._process is not None and self._process.poll() is None:
            self._terminate_process()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ElderlyVoiceAlert()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
