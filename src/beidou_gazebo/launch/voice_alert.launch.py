"""Launch only the independent elderly voice-alert node."""

from beidou_gazebo.piper_chinese_tts import DEFAULT_AUDIO_COMMAND
from beidou_gazebo.piper_chinese_tts import DEFAULT_MODEL_PATH
from beidou_gazebo.piper_chinese_tts import DEFAULT_PIPER_COMMAND
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('piper_command', default_value=DEFAULT_PIPER_COMMAND),
        DeclareLaunchArgument('piper_model', default_value=DEFAULT_MODEL_PATH),
        DeclareLaunchArgument('audio_command', default_value=DEFAULT_AUDIO_COMMAND),
        Node(
            package='beidou_gazebo',
            executable='elderly_voice_alert',
            name='elderly_voice_alert',
            output='screen',
            parameters=[{
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'piper_command': LaunchConfiguration('piper_command'),
                'piper_model': LaunchConfiguration('piper_model'),
                'audio_command': LaunchConfiguration('audio_command'),
            }],
        ),
    ])
