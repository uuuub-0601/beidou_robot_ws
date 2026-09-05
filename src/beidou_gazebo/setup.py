from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'beidou_gazebo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "worlds"), glob("worlds/*.sdf")),
        (os.path.join("share", package_name, "models", "simple_robot"), glob("models/simple_robot/*")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join('share', package_name, 'behavior_trees'),
            glob('behavior_trees/*.xml')),
        (os.path.join('share', package_name, 'docs'),
            glob('docs/*.md') + glob('docs/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubbbb',
    maintainer_email='3483931481@qq.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'beidou_position_publisher = '
            'beidou_gazebo.beidou_position_publisher:main',
            'multi_beidou_position_publisher = '
            'beidou_gazebo.multi_beidou_position_publisher:main',
            'elderly_geofence = '
            'beidou_gazebo.elderly_geofence:main',
            'elderly_guard_navigation = '
            'beidou_gazebo.elderly_guard_navigation:main',
            'elderly_companion_navigation = '
            'beidou_gazebo.elderly_companion_navigation:main',
            'elderly_voice_alarm = '
            'beidou_gazebo.elderly_voice_alarm:main',
            'elderly_voice_alert = '
            'beidou_gazebo.elderly_voice_alert:main',
            'elderly_walker = '
            'beidou_gazebo.elderly_walker:main',
            'elderly_motion_estimator = '
            'beidou_gazebo.elderly_motion_estimator:main',
            'multi_elderly_motion_estimator = '
            'beidou_gazebo.multi_elderly_motion_estimator:main',
            'elderly_geofence_multi = '
            'beidou_gazebo.elderly_geofence_multi:main',
            'elderly_safety_manager = '
            'beidou_gazebo.elderly_safety_manager:main',
            'elderly_companion_v2 = '
            'beidou_gazebo.elderly_companion_v2:main',
            'elderly_rviz_status = '
            'beidou_gazebo.elderly_rviz_status:main',
            'elderly_navigation_handoff = '
            'beidou_gazebo.elderly_navigation_handoff:main',
            'piper_chinese_tts = '
            'beidou_gazebo.piper_chinese_tts:main',
        ],
    },
)
