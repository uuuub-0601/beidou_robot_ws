"""Launch only the multi-elderly dual-layer geofence node."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory('beidou_gazebo')
    default_config = os.path.join(
        package_share, 'config', 'elderly_geofence.yaml'
    )
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('obstacle_config', default_value=default_config),
        Node(
            package='beidou_gazebo',
            executable='elderly_geofence_multi',
            name='elderly_geofence_multi',
            output='screen',
            parameters=[{
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'obstacle_config': LaunchConfiguration('obstacle_config'),
                'elderly_ids': [
                    'elder', 'elder_01', 'elder_02', 'elder_03', 'elder_04',
                ],
            }],
        ),
    ])
