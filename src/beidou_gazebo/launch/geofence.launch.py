"""Launch the per-obstacle elderly electronic fence node."""

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """Create the per-obstacle geofence node."""
    package_share = get_package_share_directory('beidou_gazebo')
    default_config = os.path.join(package_share, 'config', 'elderly_geofence.yaml')  # noqa: E501
    arguments = [
        DeclareLaunchArgument('obstacle_config', default_value=default_config),
        DeclareLaunchArgument('danger_distance', default_value='0.5'),
        DeclareLaunchArgument('warning_distance', default_value='1.0'),
        DeclareLaunchArgument('hysteresis', default_value='0.1'),
        DeclareLaunchArgument('position_timeout', default_value='1.0'),
        DeclareLaunchArgument('map_frame', default_value='map'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
    ]
    geofence = Node(
        package='beidou_gazebo', executable='elderly_geofence',
        name='elderly_geofence', output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'obstacle_config': LaunchConfiguration('obstacle_config'),
            'map_frame': LaunchConfiguration('map_frame'),
            'danger_distance': ParameterValue(LaunchConfiguration('danger_distance'), value_type=float),  # noqa: E501
            'warning_distance': ParameterValue(LaunchConfiguration('warning_distance'), value_type=float),  # noqa: E501
            'hysteresis': ParameterValue(LaunchConfiguration('hysteresis'), value_type=float),  # noqa: E501
            'position_timeout': ParameterValue(LaunchConfiguration('position_timeout'), value_type=float),  # noqa: E501
        }],
    )
    return LaunchDescription(arguments + [geofence])
