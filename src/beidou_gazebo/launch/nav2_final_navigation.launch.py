import fcntl
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import EmitEvent
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


_NAV2_PROCESS_NAMES = (
    'map_server',
    'amcl',
    'planner_server',
    'controller_server',
    'behavior_server',
    'bt_navigator',
    'lifecycle_manager',
)
_NAV2_EXECUTABLES = set(_NAV2_PROCESS_NAMES)
_nav2_lock_handle = None


def _find_existing_nav2_processes():
    processes = []
    for entry in os.scandir('/proc'):
        if not entry.name.isdigit():
            continue
        try:
            with open(
                os.path.join(entry.path, 'cmdline'), 'rb'
            ) as command_file:
                command = command_file.read().split(b'\0')
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if not command or not command[0]:
            continue
        executable_path = command[0].decode(errors='replace')
        executable = os.path.basename(executable_path)
        if executable in _NAV2_EXECUTABLES and '/nav2_' in executable_path:
            processes.append((entry.name, executable))
    return processes


def _acquire_single_instance_lock():
    global _nav2_lock_handle

    lock_path = f'/tmp/beidou_gazebo_nav2_{os.getuid()}.lock'
    lock_handle = open(lock_path, 'a+', encoding='ascii')
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        lock_handle.seek(0)
        owner = lock_handle.read().strip() or 'unknown'
        lock_handle.close()
        raise RuntimeError(
            'beidou_gazebo Nav2 is already running '
            f'(launch PID {owner}); refusing to start duplicate nodes'
        ) from error

    existing = _find_existing_nav2_processes()
    if existing:
        fcntl.flock(lock_handle, fcntl.LOCK_UN)
        lock_handle.close()
        details = ', '.join(
            f'PID {pid} ({name})' for pid, name in existing
        )
        raise RuntimeError(
            'Nav2 processes exist without the single-instance lock: '
            f'{details}. Stop the stale launch before starting Nav2.'
        )

    lock_handle.seek(0)
    lock_handle.truncate()
    lock_handle.write(str(os.getpid()))
    lock_handle.flush()
    _nav2_lock_handle = lock_handle


def _shutdown_if_process_exits(node, node_name):
    return RegisterEventHandler(
        OnProcessExit(
            target_action=node,
            on_exit=[
                EmitEvent(
                    event=Shutdown(
                        reason=f'Required Nav2 process {node_name} exited'
                    )
                )
            ],
        )
    )


def generate_launch_description():
    _acquire_single_instance_lock()

    package_share = get_package_share_directory('beidou_gazebo')
    default_params = os.path.join(package_share, 'config', 'nav2_final_params.yaml')
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = DeclareLaunchArgument(
        'params_file', default_value=default_params
    )
    sim_time = DeclareLaunchArgument('use_sim_time', default_value='true')
    common_params = [
        LaunchConfiguration('params_file'),
        {'use_sim_time': use_sim_time},
    ]

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=common_params,
    )
    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=common_params,
    )
    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=common_params,
    )
    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=common_params,
        remappings=[('cmd_vel', '/cmd_vel'), ('cmd_vel_nav', '/cmd_vel')],
    )
    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=common_params,
        remappings=[('cmd_vel', '/cmd_vel'), ('cmd_vel_nav', '/cmd_vel')],
    )
    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=common_params,
    )
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager',
        output='screen',
        parameters=common_params,
    )

    nodes = [
        map_server,
        amcl,
        planner_server,
        controller_server,
        behavior_server,
        bt_navigator,
        lifecycle_manager,
    ]
    exit_handlers = [
        _shutdown_if_process_exits(node, name)
        for node, name in zip(nodes, _NAV2_PROCESS_NAMES)
    ]

    return LaunchDescription(
        [params_file, sim_time, *nodes, *exit_handlers]
    )
