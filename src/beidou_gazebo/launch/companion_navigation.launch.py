"""Launch rate-limited elderly companion navigation."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _float_parameter(name):
    return ParameterValue(
        LaunchConfiguration(name),
        value_type=float,
    )


def generate_launch_description():
    """Describe the configurable companion navigation node."""
    defaults = {
        'companion_distance': '1.5',
        'replan_distance': '0.8',
        'distance_tolerance': '0.5',
        'minimum_goal_interval': '3.0',
        'safe_recovery_delay': '3.0',
        'guard_handoff_delay': '1.0',
        'control_frequency': '2.0',
    }
    arguments = [
        DeclareLaunchArgument(name, default_value=value)
        for name, value in defaults.items()
    ]
    arguments.append(
        DeclareLaunchArgument('use_sim_time', default_value='true')
    )
    companion_navigation = Node(
        package='beidou_gazebo',
        executable='elderly_companion_navigation',
        name='elderly_companion_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            **{
                name: _float_parameter(name)
                for name in defaults
            },
            'map_frame': 'map',
            'robot_frame': 'base_link',
            'action_name': '/navigate_to_pose',
        }],
    )
    return LaunchDescription(arguments + [companion_navigation])
