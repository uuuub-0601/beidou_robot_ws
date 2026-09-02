// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from beidou_interfaces:msg/ElderlyMotion.idl
// generated code does not contain a copyright notice
#include "beidou_interfaces/msg/detail/elderly_motion__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"

bool
beidou_interfaces__msg__ElderlyMotion__init(beidou_interfaces__msg__ElderlyMotion * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    beidou_interfaces__msg__ElderlyMotion__fini(msg);
    return false;
  }
  // vx
  // vy
  // speed
  // heading
  // valid
  return true;
}

void
beidou_interfaces__msg__ElderlyMotion__fini(beidou_interfaces__msg__ElderlyMotion * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // vx
  // vy
  // speed
  // heading
  // valid
}

bool
beidou_interfaces__msg__ElderlyMotion__are_equal(const beidou_interfaces__msg__ElderlyMotion * lhs, const beidou_interfaces__msg__ElderlyMotion * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // vx
  if (lhs->vx != rhs->vx) {
    return false;
  }
  // vy
  if (lhs->vy != rhs->vy) {
    return false;
  }
  // speed
  if (lhs->speed != rhs->speed) {
    return false;
  }
  // heading
  if (lhs->heading != rhs->heading) {
    return false;
  }
  // valid
  if (lhs->valid != rhs->valid) {
    return false;
  }
  return true;
}

bool
beidou_interfaces__msg__ElderlyMotion__copy(
  const beidou_interfaces__msg__ElderlyMotion * input,
  beidou_interfaces__msg__ElderlyMotion * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // vx
  output->vx = input->vx;
  // vy
  output->vy = input->vy;
  // speed
  output->speed = input->speed;
  // heading
  output->heading = input->heading;
  // valid
  output->valid = input->valid;
  return true;
}

beidou_interfaces__msg__ElderlyMotion *
beidou_interfaces__msg__ElderlyMotion__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  beidou_interfaces__msg__ElderlyMotion * msg = (beidou_interfaces__msg__ElderlyMotion *)allocator.allocate(sizeof(beidou_interfaces__msg__ElderlyMotion), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(beidou_interfaces__msg__ElderlyMotion));
  bool success = beidou_interfaces__msg__ElderlyMotion__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
beidou_interfaces__msg__ElderlyMotion__destroy(beidou_interfaces__msg__ElderlyMotion * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    beidou_interfaces__msg__ElderlyMotion__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
beidou_interfaces__msg__ElderlyMotion__Sequence__init(beidou_interfaces__msg__ElderlyMotion__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  beidou_interfaces__msg__ElderlyMotion * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(beidou_interfaces__msg__ElderlyMotion)) {
      return false;
    }
    data = (beidou_interfaces__msg__ElderlyMotion *)allocator.zero_allocate(size, sizeof(beidou_interfaces__msg__ElderlyMotion), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = beidou_interfaces__msg__ElderlyMotion__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        beidou_interfaces__msg__ElderlyMotion__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
beidou_interfaces__msg__ElderlyMotion__Sequence__fini(beidou_interfaces__msg__ElderlyMotion__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      beidou_interfaces__msg__ElderlyMotion__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

beidou_interfaces__msg__ElderlyMotion__Sequence *
beidou_interfaces__msg__ElderlyMotion__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  beidou_interfaces__msg__ElderlyMotion__Sequence * array = (beidou_interfaces__msg__ElderlyMotion__Sequence *)allocator.allocate(sizeof(beidou_interfaces__msg__ElderlyMotion__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = beidou_interfaces__msg__ElderlyMotion__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
beidou_interfaces__msg__ElderlyMotion__Sequence__destroy(beidou_interfaces__msg__ElderlyMotion__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    beidou_interfaces__msg__ElderlyMotion__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
beidou_interfaces__msg__ElderlyMotion__Sequence__are_equal(const beidou_interfaces__msg__ElderlyMotion__Sequence * lhs, const beidou_interfaces__msg__ElderlyMotion__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!beidou_interfaces__msg__ElderlyMotion__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
beidou_interfaces__msg__ElderlyMotion__Sequence__copy(
  const beidou_interfaces__msg__ElderlyMotion__Sequence * input,
  beidou_interfaces__msg__ElderlyMotion__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(beidou_interfaces__msg__ElderlyMotion)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(beidou_interfaces__msg__ElderlyMotion);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    beidou_interfaces__msg__ElderlyMotion * data =
      (beidou_interfaces__msg__ElderlyMotion *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!beidou_interfaces__msg__ElderlyMotion__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          beidou_interfaces__msg__ElderlyMotion__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!beidou_interfaces__msg__ElderlyMotion__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
