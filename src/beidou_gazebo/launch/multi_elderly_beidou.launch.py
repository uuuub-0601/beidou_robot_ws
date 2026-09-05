"""Launch the multi-elderly simulated Beidou data publisher only."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'pose_topic',
            default_value='/world/elderly_final/pose/named',
            description='Named TFMessage topic emitted by elderly_pose_bridge',
        ),
        Node(
            package='beidou_gazebo',
            executable='multi_beidou_position_publisher',
            name='multi_beidou_position_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'pose_topic': LaunchConfiguration('pose_topic'),
                'robot_model_name': 'elderly_robot',
                'map_frame': 'map',
                'robot_frame': 'base_link',
                'elderly_ids': [
                    'elder', 'elder_01', 'elder_02', 'elder_03', 'elder_04',
                ],
            }],
        ),
    ])
