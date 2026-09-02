"""Launch motion estimation and dynamic Nav2 companion following."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _float_parameter(name):
    return ParameterValue(LaunchConfiguration(name), value_type=float)


def generate_launch_description():
    """Create the Companion 2.0 prototype nodes."""
    defaults = {
        'window_duration': '0.8',
        'minimum_span': '0.4',
        'jump_distance': '0.5',
        'jump_speed': '1.5',
        'heading_speed_threshold': '0.05',
        'data_timeout': '0.5',
        'motion_publish_frequency': '20.0',
        'back_distance': '2.0',
        'side_offset': '0.0',
        'prediction_horizon': '0.6',
        'minimum_companion_distance': '1.4',
        'maximum_companion_distance': '2.0',
        'target_tolerance': '0.25',
        'speed_margin': '0.05',
        'catchup_gain': '0.35',
        'stopped_speed_threshold': '0.05',
        'minimum_active_speed': '0.03',
        'maximum_robot_speed': '0.5',
        'speed_limit_acceleration': '0.5',
        'speed_limit_deceleration': '0.5',
        'target_update_frequency': '5.0',
        'goal_update_distance_threshold': '0.10',
        'goal_update_yaw_threshold': '0.12',
        'visualization_frequency': '5.0',
        'minimum_action_retry_interval': '2.0',
    }
    arguments = [
        DeclareLaunchArgument(name, default_value=value)
        for name, value in defaults.items()
    ]
    arguments.append(
        DeclareLaunchArgument('use_sim_time', default_value='true')
    )

    estimator_names = (
        'window_duration',
        'minimum_span',
        'jump_distance',
        'jump_speed',
        'heading_speed_threshold',
        'data_timeout',
    )
    motion_estimator = Node(
        package='beidou_gazebo',
        executable='elderly_motion_estimator',
        name='elderly_motion_estimator',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            **{
                name: _float_parameter(name)
                for name in estimator_names
            },
            'minimum_samples': 5,
            'publish_frequency': _float_parameter(
                'motion_publish_frequency'
            ),
        }],
    )
    companion_names = tuple(
        name
        for name in defaults
        if name not in estimator_names
        and name != 'motion_publish_frequency'
    )
    companion = Node(
        package='beidou_gazebo',
        executable='elderly_companion_v2',
        name='elderly_companion_v2',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            **{
                name: _float_parameter(name)
                for name in companion_names
            },
            'map_frame': 'map',
            'robot_frame': 'base_link',
            'action_name': '/navigate_to_pose',
            'goal_update_topic': '/goal_update',
            'speed_limit_topic': '/speed_limit',
        }],
    )
    return LaunchDescription(arguments + [motion_estimator, companion])
