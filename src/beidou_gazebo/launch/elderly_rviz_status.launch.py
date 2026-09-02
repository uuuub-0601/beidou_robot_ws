"""Launch the independent RViz elderly geofence status marker node."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """Create only the RViz status marker node."""
    arguments = [
        DeclareLaunchArgument('map_frame', default_value='map'),
        DeclareLaunchArgument('height', default_value='0.9'),
        DeclareLaunchArgument('text_size', default_value='0.5'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
    ]
    status = Node(
        package='beidou_gazebo', executable='elderly_rviz_status',
        name='elderly_rviz_status', output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'map_frame': LaunchConfiguration('map_frame'),
            'height': ParameterValue(LaunchConfiguration('height'), value_type=float),
            'text_size': ParameterValue(LaunchConfiguration('text_size'), value_type=float),
        }],
    )
    return LaunchDescription(arguments + [status])
