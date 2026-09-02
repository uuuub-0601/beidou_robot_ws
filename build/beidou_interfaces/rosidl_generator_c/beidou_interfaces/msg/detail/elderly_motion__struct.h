// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from beidou_interfaces:msg/ElderlyMotion.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "beidou_interfaces/msg/elderly_motion.h"


#ifndef BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__STRUCT_H_
#define BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"

/// Struct defined in msg/ElderlyMotion in the package beidou_interfaces.
typedef struct beidou_interfaces__msg__ElderlyMotion
{
  std_msgs__msg__Header header;
  double vx;
  double vy;
  double speed;
  double heading;
  bool valid;
} beidou_interfaces__msg__ElderlyMotion;

// Struct for a sequence of beidou_interfaces__msg__ElderlyMotion.
typedef struct beidou_interfaces__msg__ElderlyMotion__Sequence
{
  beidou_interfaces__msg__ElderlyMotion * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} beidou_interfaces__msg__ElderlyMotion__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__STRUCT_H_
