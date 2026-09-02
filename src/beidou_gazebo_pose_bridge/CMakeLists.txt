cmake_minimum_required(VERSION 3.8)
project(beidou_gazebo_pose_bridge)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(gz_msgs_vendor REQUIRED)
find_package(gz_transport_vendor REQUIRED)
find_package(gz-msgs10 REQUIRED)
find_package(gz-transport13 REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tf2_msgs REQUIRED)

add_executable(elderly_pose_bridge src/elderly_pose_bridge.cpp)
ament_target_dependencies(
  elderly_pose_bridge
  geometry_msgs
  rclcpp
  tf2_msgs
)
target_link_libraries(
  elderly_pose_bridge
  gz-msgs10::core
  gz-transport13::core
)

install(TARGETS elderly_pose_bridge DESTINATION lib/${PROJECT_NAME})

ament_package()
