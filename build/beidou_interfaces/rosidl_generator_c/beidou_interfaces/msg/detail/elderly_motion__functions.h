// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from beidou_interfaces:msg/ElderlyMotion.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "beidou_interfaces/msg/elderly_motion.h"


#ifndef BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__FUNCTIONS_H_
#define BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/action_type_support_struct.h"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_runtime_c/service_type_support_struct.h"
#include "rosidl_runtime_c/type_description/type_description__struct.h"
#include "rosidl_runtime_c/type_description/type_source__struct.h"
#include "rosidl_runtime_c/type_hash.h"
#include "rosidl_runtime_c/visibility_control.h"
#include "beidou_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "beidou_interfaces/msg/detail/elderly_motion__struct.h"

/// Initialize msg/ElderlyMotion message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * beidou_interfaces__msg__ElderlyMotion
 * )) before or use
 * beidou_interfaces__msg__ElderlyMotion__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
bool
beidou_interfaces__msg__ElderlyMotion__init(beidou_interfaces__msg__ElderlyMotion * msg);

/// Finalize msg/ElderlyMotion message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
void
beidou_interfaces__msg__ElderlyMotion__fini(beidou_interfaces__msg__ElderlyMotion * msg);

/// Create msg/ElderlyMotion message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * beidou_interfaces__msg__ElderlyMotion__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
beidou_interfaces__msg__ElderlyMotion *
beidou_interfaces__msg__ElderlyMotion__create(void);

/// Destroy msg/ElderlyMotion message.
/**
 * It calls
 * beidou_interfaces__msg__ElderlyMotion__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
void
beidou_interfaces__msg__ElderlyMotion__destroy(beidou_interfaces__msg__ElderlyMotion * msg);

/// Check for msg/ElderlyMotion message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
bool
beidou_interfaces__msg__ElderlyMotion__are_equal(const beidou_interfaces__msg__ElderlyMotion * lhs, const beidou_interfaces__msg__ElderlyMotion * rhs);

/// Copy a msg/ElderlyMotion message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
bool
beidou_interfaces__msg__ElderlyMotion__copy(
  const beidou_interfaces__msg__ElderlyMotion * input,
  beidou_interfaces__msg__ElderlyMotion * output);

/// Retrieve pointer to the hash of the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
const rosidl_type_hash_t *
beidou_interfaces__msg__ElderlyMotion__get_type_hash(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
const rosidl_runtime_c__type_description__TypeDescription *
beidou_interfaces__msg__ElderlyMotion__get_type_description(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the single raw source text that defined this type.
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
const rosidl_runtime_c__type_description__TypeSource *
beidou_interfaces__msg__ElderlyMotion__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the recursive raw sources that defined the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
const rosidl_runtime_c__type_description__TypeSource__Sequence *
beidou_interfaces__msg__ElderlyMotion__get_type_description_sources(
  const rosidl_message_type_support_t * type_support);

/// Initialize array of msg/ElderlyMotion messages.
/**
 * It allocates the memory for the number of elements and calls
 * beidou_interfaces__msg__ElderlyMotion__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
bool
beidou_interfaces__msg__ElderlyMotion__Sequence__init(beidou_interfaces__msg__ElderlyMotion__Sequence * array, size_t size);

/// Finalize array of msg/ElderlyMotion messages.
/**
 * It calls
 * beidou_interfaces__msg__ElderlyMotion__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
void
beidou_interfaces__msg__ElderlyMotion__Sequence__fini(beidou_interfaces__msg__ElderlyMotion__Sequence * array);

/// Create array of msg/ElderlyMotion messages.
/**
 * It allocates the memory for the array and calls
 * beidou_interfaces__msg__ElderlyMotion__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
beidou_interfaces__msg__ElderlyMotion__Sequence *
beidou_interfaces__msg__ElderlyMotion__Sequence__create(size_t size);

/// Destroy array of msg/ElderlyMotion messages.
/**
 * It calls
 * beidou_interfaces__msg__ElderlyMotion__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
void
beidou_interfaces__msg__ElderlyMotion__Sequence__destroy(beidou_interfaces__msg__ElderlyMotion__Sequence * array);

/// Check for msg/ElderlyMotion message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
bool
beidou_interfaces__msg__ElderlyMotion__Sequence__are_equal(const beidou_interfaces__msg__ElderlyMotion__Sequence * lhs, const beidou_interfaces__msg__ElderlyMotion__Sequence * rhs);

/// Copy an array of msg/ElderlyMotion messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_beidou_interfaces
bool
beidou_interfaces__msg__ElderlyMotion__Sequence__copy(
  const beidou_interfaces__msg__ElderlyMotion__Sequence * input,
  beidou_interfaces__msg__ElderlyMotion__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__FUNCTIONS_H_
