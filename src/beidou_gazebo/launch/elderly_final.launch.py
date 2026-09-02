import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_share = get_package_share_directory("beidou_gazebo")
    ros_gz_sim_share = get_package_share_directory("ros_gz_sim")
    world = os.path.join(package_share, "worlds", "elderly_final.sdf")
    gazebo = IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(ros_gz_sim_share, "launch", "gz_sim.launch.py")), launch_arguments={"gz_args": f"-r {world}"}.items())
    scan_bridge = Node(package="ros_gz_bridge", executable="parameter_bridge", name="scan_bridge", arguments=["/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan"], output="screen")
    cmd_vel_bridge = Node(package="ros_gz_bridge", executable="parameter_bridge", name="cmd_vel_bridge", arguments=["/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist"], output="screen")
    odom_bridge = Node(package="ros_gz_bridge", executable="parameter_bridge", name="odom_bridge", arguments=["/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry"], output="screen")
    tf_bridge = Node(package="ros_gz_bridge", executable="parameter_bridge", name="tf_bridge", arguments=["/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V"], output="screen")
    clock_bridge = Node(package="ros_gz_bridge", executable="parameter_bridge", name="clock_bridge", arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"], output="screen")
    lidar_tf = Node(package="tf2_ros", executable="static_transform_publisher", name="lidar_static_tf", arguments=["--x", "0", "--y", "0", "--z", "0.65", "--roll", "0", "--pitch", "0", "--yaw", "0", "--frame-id", "base_link", "--child-frame-id", "lidar_link"], output="screen")
    return LaunchDescription([gazebo, scan_bridge, cmd_vel_bridge, odom_bridge, tf_bridge, clock_bridge, lidar_tf])
