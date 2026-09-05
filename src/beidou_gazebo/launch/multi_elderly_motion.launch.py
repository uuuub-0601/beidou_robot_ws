"""Launch only the multi-elderly motion estimator."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        Node(
            package='beidou_gazebo',
            executable='multi_elderly_motion_estimator',
            name='multi_elderly_motion_estimator',
            output='screen',
            parameters=[{
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'elderly_ids': [
                    'elder', 'elder_01', 'elder_02', 'elder_03', 'elder_04',
                ],
            }],
        ),
    ])
