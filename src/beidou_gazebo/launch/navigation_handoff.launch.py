"""Launch only the navigation-control handoff node."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    args = [
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('safe_recovery_time', default_value='3.0'),
        DeclareLaunchArgument('transition_timeout', default_value='5.0'),
        DeclareLaunchArgument('guard_goal_timeout', default_value='30.0'),
    ]
    node = Node(
        package='beidou_gazebo',
        executable='elderly_navigation_handoff',
        name='elderly_navigation_handoff',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'safe_recovery_time': ParameterValue(LaunchConfiguration('safe_recovery_time'), value_type=float),
            'transition_timeout': ParameterValue(LaunchConfiguration('transition_timeout'), value_type=float),
            'guard_goal_timeout': ParameterValue(LaunchConfiguration('guard_goal_timeout'), value_type=float),
        }],
    )
    return LaunchDescription(args + [node])
