// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from beidou_interfaces:msg/ElderlyMotion.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "beidou_interfaces/msg/elderly_motion.hpp"


#ifndef BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__BUILDER_HPP_
#define BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "beidou_interfaces/msg/detail/elderly_motion__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace beidou_interfaces
{

namespace msg
{

namespace builder
{

class Init_ElderlyMotion_valid
{
public:
  explicit Init_ElderlyMotion_valid(::beidou_interfaces::msg::ElderlyMotion & msg)
  : msg_(msg)
  {}
  ::beidou_interfaces::msg::ElderlyMotion valid(::beidou_interfaces::msg::ElderlyMotion::_valid_type arg)
  {
    msg_.valid = std::move(arg);
    return std::move(msg_);
  }

private:
  ::beidou_interfaces::msg::ElderlyMotion msg_;
};

class Init_ElderlyMotion_heading
{
public:
  explicit Init_ElderlyMotion_heading(::beidou_interfaces::msg::ElderlyMotion & msg)
  : msg_(msg)
  {}
  Init_ElderlyMotion_valid heading(::beidou_interfaces::msg::ElderlyMotion::_heading_type arg)
  {
    msg_.heading = std::move(arg);
    return Init_ElderlyMotion_valid(msg_);
  }

private:
  ::beidou_interfaces::msg::ElderlyMotion msg_;
};

class Init_ElderlyMotion_speed
{
public:
  explicit Init_ElderlyMotion_speed(::beidou_interfaces::msg::ElderlyMotion & msg)
  : msg_(msg)
  {}
  Init_ElderlyMotion_heading speed(::beidou_interfaces::msg::ElderlyMotion::_speed_type arg)
  {
    msg_.speed = std::move(arg);
    return Init_ElderlyMotion_heading(msg_);
  }

private:
  ::beidou_interfaces::msg::ElderlyMotion msg_;
};

class Init_ElderlyMotion_vy
{
public:
  explicit Init_ElderlyMotion_vy(::beidou_interfaces::msg::ElderlyMotion & msg)
  : msg_(msg)
  {}
  Init_ElderlyMotion_speed vy(::beidou_interfaces::msg::ElderlyMotion::_vy_type arg)
  {
    msg_.vy = std::move(arg);
    return Init_ElderlyMotion_speed(msg_);
  }

private:
  ::beidou_interfaces::msg::ElderlyMotion msg_;
};

class Init_ElderlyMotion_vx
{
public:
  explicit Init_ElderlyMotion_vx(::beidou_interfaces::msg::ElderlyMotion & msg)
  : msg_(msg)
  {}
  Init_ElderlyMotion_vy vx(::beidou_interfaces::msg::ElderlyMotion::_vx_type arg)
  {
    msg_.vx = std::move(arg);
    return Init_ElderlyMotion_vy(msg_);
  }

private:
  ::beidou_interfaces::msg::ElderlyMotion msg_;
};

class Init_ElderlyMotion_header
{
public:
  Init_ElderlyMotion_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ElderlyMotion_vx header(::beidou_interfaces::msg::ElderlyMotion::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ElderlyMotion_vx(msg_);
  }

private:
  ::beidou_interfaces::msg::ElderlyMotion msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::beidou_interfaces::msg::ElderlyMotion>()
{
  return beidou_interfaces::msg::builder::Init_ElderlyMotion_header();
}

}  // namespace beidou_interfaces

#endif  // BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__BUILDER_HPP_
