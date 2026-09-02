// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from beidou_interfaces:msg/ElderlyMotion.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "beidou_interfaces/msg/detail/elderly_motion__rosidl_typesupport_introspection_c.h"
#include "beidou_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "beidou_interfaces/msg/detail/elderly_motion__functions.h"
#include "beidou_interfaces/msg/detail/elderly_motion__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  beidou_interfaces__msg__ElderlyMotion__init(message_memory);
}

void beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_fini_function(void * message_memory)
{
  beidou_interfaces__msg__ElderlyMotion__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_message_member_array[6] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(beidou_interfaces__msg__ElderlyMotion, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "vx",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(beidou_interfaces__msg__ElderlyMotion, vx),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "vy",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(beidou_interfaces__msg__ElderlyMotion, vy),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "speed",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(beidou_interfaces__msg__ElderlyMotion, speed),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "heading",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(beidou_interfaces__msg__ElderlyMotion, heading),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "valid",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(beidou_interfaces__msg__ElderlyMotion, valid),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_message_members = {
  "beidou_interfaces__msg",  // message namespace
  "ElderlyMotion",  // message name
  6,  // number of fields
  sizeof(beidou_interfaces__msg__ElderlyMotion),
  false,  // has_any_key_member_
  beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_message_member_array,  // message members
  beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_init_function,  // function to initialize message memory (memory has to be allocated)
  beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_message_type_support_handle = {
  0,
  &beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_message_members,
  get_message_typesupport_handle_function,
  &beidou_interfaces__msg__ElderlyMotion__get_type_hash,
  &beidou_interfaces__msg__ElderlyMotion__get_type_description,
  &beidou_interfaces__msg__ElderlyMotion__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_beidou_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, beidou_interfaces, msg, ElderlyMotion)() {
  beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  if (!beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_message_type_support_handle.typesupport_identifier) {
    beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &beidou_interfaces__msg__ElderlyMotion__rosidl_typesupport_introspection_c__ElderlyMotion_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
