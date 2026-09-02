"""Launch only the simulated elderly Beidou data path."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bridge = Node(
        package='beidou_gazebo_pose_bridge',
        executable='elderly_pose_bridge',
        name='elderly_pose_bridge',
        output='screen',
        parameters=[
            {'gz_topic': LaunchConfiguration('gazebo_pose_topic')},
            {'ros_topic': LaunchConfiguration('named_pose_topic')},
        ],
    )
    publisher = Node(
        package='beidou_gazebo',
        executable='beidou_position_publisher',
        name='elderly_beidou_position',
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'pose_topic': LaunchConfiguration('named_pose_topic')},
            {'elder_model_name': 'elder'},
            {'robot_model_name': 'elderly_robot'},
            {'map_frame': 'map'},
            {'robot_frame': 'base_link'},
        ],
    )
    return LaunchDescription([
        DeclareLaunchArgument(
            'gazebo_pose_topic',
            default_value='/world/elderly_final/pose/info',
            description='Gazebo Pose_V topic containing named model poses',
        ),
        DeclareLaunchArgument(
            'named_pose_topic',
            default_value='/world/elderly_final/pose/named',
            description='ROS TFMessage topic emitted by the pose bridge',
        ),
        bridge,
        publisher,
    ])
