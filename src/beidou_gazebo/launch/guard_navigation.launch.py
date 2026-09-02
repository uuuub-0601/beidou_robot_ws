"""Launch one-shot elderly guard navigation."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    arguments = [
        DeclareLaunchArgument('guard_distance', default_value='1.2'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
    ]
    guard_navigation = Node(
        package='beidou_gazebo',
        executable='elderly_guard_navigation',
        name='elderly_guard_navigation',
        output='screen',
        parameters=[
            {
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'guard_distance': ParameterValue(
                    LaunchConfiguration('guard_distance'),
                    value_type=float,
                ),
                'map_frame': 'map',
                'robot_frame': 'base_link',
                'action_name': '/navigate_to_pose',
            },
        ],
    )
    return LaunchDescription(arguments + [guard_navigation])
