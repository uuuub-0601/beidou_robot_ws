import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ubbbb/beidou_robot_ws/install/beidou_gazebo'
