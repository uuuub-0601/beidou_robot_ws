"""Launch continuous Gazebo-native motion for the elderly model."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _float_parameter(name):
    return ParameterValue(LaunchConfiguration(name), value_type=float)


def generate_launch_description():
    """Create the pose feedback bridge, velocity bridge, and walker."""
    defaults = {
        'walking_speed': '0.3',
        'turn_speed': '0.8',
        'turn_gain': '1.5',
        'minimum_speed_ratio': '0.15',
        'waypoint_tolerance': '0.15',
        'control_frequency': '20.0',
        'pose_timeout': '1.0',
    }
    arguments = [
        DeclareLaunchArgument(name, default_value=value)
        for name, value in defaults.items()
    ]
    arguments.append(
        DeclareLaunchArgument('use_sim_time', default_value='true')
    )
    arguments.extend([
        DeclareLaunchArgument(
            'gazebo_pose_topic',
            default_value='/world/elderly_final/pose/info',
            description='Gazebo Pose_V topic containing named model poses',
        ),
        DeclareLaunchArgument(
            'walker_pose_topic',
            default_value='/elderly_walker/gazebo_pose',
            description='ROS pose topic consumed by the walker',
        ),
    ])

    pose_bridge = Node(
        package='beidou_gazebo_pose_bridge',
        executable='elderly_pose_bridge',
        name='elderly_walker_pose_bridge',
        output='screen',
        parameters=[
            {'gz_topic': LaunchConfiguration('gazebo_pose_topic')},
            {'ros_topic': LaunchConfiguration('walker_pose_topic')},
        ],
    )
    velocity_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='elderly_walker_velocity_bridge',
        arguments=[
            '/model/elder/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'
        ],
        remappings=[
            ('/model/elder/cmd_vel', '/elderly_walker/cmd_vel'),
        ],
        output='screen',
    )
    walker = Node(
        package='beidou_gazebo',
        executable='elderly_walker',
        name='elderly_walker',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            **{
                name: _float_parameter(name)
                for name in defaults
            },
            'elder_model_name': 'elder',
            'pose_topic': LaunchConfiguration('walker_pose_topic'),
            'waypoints': [
                # Approach the flowerbed from the open north side. The
                # vertical excursion at its centre crosses WARNING and
                # DANGER without turning at an obstacle corner.
                0.0, 4.5,
                -2.5, 4.5,
                -2.5, 3.15,
                -2.5, 4.5,
            ],
        }],
    )
    return LaunchDescription(
        arguments + [pose_bridge, velocity_bridge, walker]
    )
