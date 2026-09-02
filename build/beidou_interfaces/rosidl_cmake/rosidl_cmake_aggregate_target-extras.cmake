# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target beidou_interfaces::beidou_interfaces
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${beidou_interfaces_TARGETS}.
if(beidou_interfaces_TARGETS AND NOT TARGET beidou_interfaces::beidou_interfaces)
  add_library(beidou_interfaces::beidou_interfaces INTERFACE IMPORTED)
  set_target_properties(beidou_interfaces::beidou_interfaces PROPERTIES
    INTERFACE_LINK_LIBRARIES "${beidou_interfaces_TARGETS}")
endif()
