// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from beidou_interfaces:msg/ElderlyMotion.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "beidou_interfaces/msg/elderly_motion.hpp"


#ifndef BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__TRAITS_HPP_
#define BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "beidou_interfaces/msg/detail/elderly_motion__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace beidou_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const ElderlyMotion & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: vx
  {
    out << "vx: ";
    rosidl_generator_traits::value_to_yaml(msg.vx, out);
    out << ", ";
  }

  // member: vy
  {
    out << "vy: ";
    rosidl_generator_traits::value_to_yaml(msg.vy, out);
    out << ", ";
  }

  // member: speed
  {
    out << "speed: ";
    rosidl_generator_traits::value_to_yaml(msg.speed, out);
    out << ", ";
  }

  // member: heading
  {
    out << "heading: ";
    rosidl_generator_traits::value_to_yaml(msg.heading, out);
    out << ", ";
  }

  // member: valid
  {
    out << "valid: ";
    rosidl_generator_traits::value_to_yaml(msg.valid, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ElderlyMotion & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: vx
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "vx: ";
    rosidl_generator_traits::value_to_yaml(msg.vx, out);
    out << "\n";
  }

  // member: vy
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "vy: ";
    rosidl_generator_traits::value_to_yaml(msg.vy, out);
    out << "\n";
  }

  // member: speed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "speed: ";
    rosidl_generator_traits::value_to_yaml(msg.speed, out);
    out << "\n";
  }

  // member: heading
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "heading: ";
    rosidl_generator_traits::value_to_yaml(msg.heading, out);
    out << "\n";
  }

  // member: valid
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "valid: ";
    rosidl_generator_traits::value_to_yaml(msg.valid, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ElderlyMotion & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace beidou_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use beidou_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const beidou_interfaces::msg::ElderlyMotion & msg,
  std::ostream & out, size_t indentation = 0)
{
  beidou_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use beidou_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const beidou_interfaces::msg::ElderlyMotion & msg)
{
  return beidou_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<beidou_interfaces::msg::ElderlyMotion>()
{
  return "beidou_interfaces::msg::ElderlyMotion";
}

template<>
inline const char * name<beidou_interfaces::msg::ElderlyMotion>()
{
  return "beidou_interfaces/msg/ElderlyMotion";
}

template<>
struct has_fixed_size<beidou_interfaces::msg::ElderlyMotion>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<beidou_interfaces::msg::ElderlyMotion>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<beidou_interfaces::msg::ElderlyMotion>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // BEIDOU_INTERFACES__MSG__DETAIL__ELDERLY_MOTION__TRAITS_HPP_
