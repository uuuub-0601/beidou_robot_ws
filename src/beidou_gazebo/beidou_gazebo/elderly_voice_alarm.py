"""Play a Chinese warning on an electronic-fence exit transition."""

import subprocess
import sys

from beidou_gazebo.piper_chinese_tts import DEFAULT_AUDIO_COMMAND
from beidou_gazebo.piper_chinese_tts import DEFAULT_MODEL_PATH
from beidou_gazebo.piper_chinese_tts import DEFAULT_PIPER_COMMAND
from beidou_gazebo.piper_chinese_tts import dependency_errors
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Bool, String


STATE_SAFE = 'SAFE'
STATE_ALARM_TRIGGERED = 'ALARM_TRIGGERED'
STATE_DEPENDENCY_MISSING = 'DEPENDENCY_MISSING'
STATE_PLAYBACK_ERROR = 'PLAYBACK_ERROR'


class GeofenceExitDetector:
    """Detect only known SAFE to OUT_OF_BOUNDS transitions."""

    def __init__(self):
        self.previous_safe = None

    def update(self, current_safe):
        """Update the geofence state and return whether to alarm."""
        should_alarm = self.previous_safe is True and not current_safe
        self.previous_safe = current_safe
        return should_alarm


class ElderlyVoiceAlarm(Node):
    """Subscribe to geofence state and speak once for every exit edge."""

    def __init__(self):
        super().__init__('elderly_voice_alarm')
        self.declare_parameter(
            'alarm_text',
            '警告，您已离开安全活动区域，请尽快返回安全区域。',
        )
        self.declare_parameter('piper_command', DEFAULT_PIPER_COMMAND)
        self.declare_parameter('piper_model', DEFAULT_MODEL_PATH)
        self.declare_parameter('audio_command', DEFAULT_AUDIO_COMMAND)

        self.alarm_text = str(self.get_parameter('alarm_text').value)
        self.piper_command = str(
            self.get_parameter('piper_command').value
        )
        self.piper_model = str(
            self.get_parameter('piper_model').value
        )
        self.audio_command = str(
            self.get_parameter('audio_command').value
        )
        self.detector = GeofenceExitDetector()
        self._speech_processes = []

        state_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.state_pub = self.create_publisher(
            String, '/elderly_voice_alarm_state', state_qos
        )
        self.create_subscription(
            Bool,
            '/elderly_geofence_status',
            self._geofence_callback,
            10,
        )
        self.create_timer(0.25, self._check_playback)

        errors = self._dependency_errors()
        if errors:
            self.get_logger().error(
                '[VOICE ALARM] Piper Chinese TTS is unavailable: '
                + '; '.join(errors)
            )
            self._publish_state(STATE_DEPENDENCY_MISSING)
        else:
            self.get_logger().info(
                '[VOICE ALARM] Ready; waiting for a SAFE to '
                'OUT_OF_BOUNDS transition.'
            )

    def _publish_state(self, state):
        self.state_pub.publish(String(data=state))

    def _dependency_errors(self):
        return dependency_errors(
            self.piper_command,
            self.piper_model,
            self.audio_command,
        )

    def _geofence_callback(self, message):
        current_safe = bool(message.data)
        previous_safe = self.detector.previous_safe
        should_alarm = self.detector.update(current_safe)

        if current_safe:
            self._publish_state(STATE_SAFE)
            if previous_safe is False:
                self.get_logger().info(
                    '[VOICE ALARM] Elderly person returned to safe area.'
                )
            return

        if not should_alarm:
            return

        self.get_logger().warning(
            '[VOICE ALARM] Elderly person is out of bounds.'
        )
        self._play_alarm()

    def _play_alarm(self):
        errors = self._dependency_errors()
        if errors:
            self.get_logger().error(
                '[VOICE ALARM] Alarm not played because Piper Chinese TTS '
                'is unavailable: ' + '; '.join(errors)
            )
            self._publish_state(STATE_DEPENDENCY_MISSING)
            return

        command = [
            sys.executable,
            '-m',
            'beidou_gazebo.piper_chinese_tts',
            '--piper-command',
            self.piper_command,
            '--model',
            self.piper_model,
            '--audio-command',
            self.audio_command,
            self.alarm_text,
        ]
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as error:
            self.get_logger().error(
                f'[VOICE ALARM] Playback failed: {error}'
            )
            self._publish_state(STATE_PLAYBACK_ERROR)
            return

        self._speech_processes.append(process)
        self._publish_state(STATE_ALARM_TRIGGERED)
        self.get_logger().info('[VOICE ALARM] Alarm triggered.')

    def _check_playback(self):
        active_processes = []
        for process in self._speech_processes:
            return_code = process.poll()
            if return_code is None:
                active_processes.append(process)
            elif return_code != 0:
                self.get_logger().error(
                    '[VOICE ALARM] Playback process exited with code '
                    f'{return_code}.'
                )
                self._publish_state(STATE_PLAYBACK_ERROR)
        self._speech_processes = active_processes


def main(args=None):
    rclpy.init(args=args)
    node = ElderlyVoiceAlarm()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
