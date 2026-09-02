import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    package_share = get_package_share_directory("beidou_gazebo")
    slam_toolbox_share = get_package_share_directory("slam_toolbox")
    slam_params = os.path.join(package_share, "config", "slam_params.yaml")

    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                slam_toolbox_share,
                "launch",
                "online_async_launch.py",
            )
        ),
        launch_arguments={
            "slam_params_file": slam_params,
            "use_sim_time": "true",
            "autostart": "true",
            "use_lifecycle_manager": "false",
        }.items(),
    )

    return LaunchDescription([slam_toolbox])
