// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from beidou_interfaces:msg/ElderlyMotion.idl
// generated code does not contain a copyright notice
#ifndef BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "beidou_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "beidou_interfaces/msg/detail/elderly_motion__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_beidou_interfaces
bool cdr_serialize_beidou_interfaces__msg__ElderlyMotion(
  const beidou_interfaces__msg__ElderlyMotion * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_beidou_interfaces
bool cdr_deserialize_beidou_interfaces__msg__ElderlyMotion(
  eprosima::fastcdr::Cdr &,
  beidou_interfaces__msg__ElderlyMotion * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_beidou_interfaces
size_t get_serialized_size_beidou_interfaces__msg__ElderlyMotion(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_beidou_interfaces
size_t max_serialized_size_beidou_interfaces__msg__ElderlyMotion(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_beidou_interfaces
bool cdr_serialize_key_beidou_interfaces__msg__ElderlyMotion(
  const beidou_interfaces__msg__ElderlyMotion * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_beidou_interfaces
size_t get_serialized_size_key_beidou_interfaces__msg__ElderlyMotion(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_beidou_interfaces
size_t max_serialized_size_key_beidou_interfaces__msg__ElderlyMotion(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_beidou_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, beidou_interfaces, msg, ElderlyMotion)();

#ifdef __cplusplus
}
#endif

#endif  // BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
