// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from beidou_interfaces:msg/ElderlyMotion.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "beidou_interfaces/msg/elderly_motion.hpp"


#ifndef BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__STRUCT_HPP_
#define BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__beidou_interfaces__msg__ElderlyMotion __attribute__((deprecated))
#else
# define DEPRECATED__beidou_interfaces__msg__ElderlyMotion __declspec(deprecated)
#endif

namespace beidou_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ElderlyMotion_
{
  using Type = ElderlyMotion_<ContainerAllocator>;

  explicit ElderlyMotion_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->vx = 0.0;
      this->vy = 0.0;
      this->speed = 0.0;
      this->heading = 0.0;
      this->valid = false;
    }
  }

  explicit ElderlyMotion_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->vx = 0.0;
      this->vy = 0.0;
      this->speed = 0.0;
      this->heading = 0.0;
      this->valid = false;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _vx_type =
    double;
  _vx_type vx;
  using _vy_type =
    double;
  _vy_type vy;
  using _speed_type =
    double;
  _speed_type speed;
  using _heading_type =
    double;
  _heading_type heading;
  using _valid_type =
    bool;
  _valid_type valid;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__vx(
    const double & _arg)
  {
    this->vx = _arg;
    return *this;
  }
  Type & set__vy(
    const double & _arg)
  {
    this->vy = _arg;
    return *this;
  }
  Type & set__speed(
    const double & _arg)
  {
    this->speed = _arg;
    return *this;
  }
  Type & set__heading(
    const double & _arg)
  {
    this->heading = _arg;
    return *this;
  }
  Type & set__valid(
    const bool & _arg)
  {
    this->valid = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    beidou_interfaces::msg::ElderlyMotion_<ContainerAllocator> *;
  using ConstRawPtr =
    const beidou_interfaces::msg::ElderlyMotion_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<beidou_interfaces::msg::ElderlyMotion_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<beidou_interfaces::msg::ElderlyMotion_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      beidou_interfaces::msg::ElderlyMotion_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<beidou_interfaces::msg::ElderlyMotion_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      beidou_interfaces::msg::ElderlyMotion_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<beidou_interfaces::msg::ElderlyMotion_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<beidou_interfaces::msg::ElderlyMotion_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<beidou_interfaces::msg::ElderlyMotion_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__beidou_interfaces__msg__ElderlyMotion
    std::shared_ptr<beidou_interfaces::msg::ElderlyMotion_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__beidou_interfaces__msg__ElderlyMotion
    std::shared_ptr<beidou_interfaces::msg::ElderlyMotion_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ElderlyMotion_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->vx != other.vx) {
      return false;
    }
    if (this->vy != other.vy) {
      return false;
    }
    if (this->speed != other.speed) {
      return false;
    }
    if (this->heading != other.heading) {
      return false;
    }
    if (this->valid != other.valid) {
      return false;
    }
    return true;
  }
  bool operator!=(const ElderlyMotion_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ElderlyMotion_

// alias to use template instance with default allocator
using ElderlyMotion =
  beidou_interfaces::msg::ElderlyMotion_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace beidou_interfaces

#endif  // BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__STRUCT_HPP_
