#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "beidou_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__beidou_interfaces__msg__ElderlyMotion() -> *const std::ffi::c_void;
}

#[link(name = "beidou_interfaces__rosidl_generator_c")]
extern "C" {
    fn beidou_interfaces__msg__ElderlyMotion__init(msg: *mut ElderlyMotion) -> bool;
    fn beidou_interfaces__msg__ElderlyMotion__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ElderlyMotion>, size: usize) -> bool;
    fn beidou_interfaces__msg__ElderlyMotion__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ElderlyMotion>);
    fn beidou_interfaces__msg__ElderlyMotion__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ElderlyMotion>, out_seq: *mut rosidl_runtime_rs::Sequence<ElderlyMotion>) -> bool;
}

// Corresponds to beidou_interfaces__msg__ElderlyMotion
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ElderlyMotion {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub vx: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub vy: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub speed: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub heading: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub valid: bool,

}



impl Default for ElderlyMotion {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !beidou_interfaces__msg__ElderlyMotion__init(&mut msg as *mut _) {
        panic!("Call to beidou_interfaces__msg__ElderlyMotion__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ElderlyMotion {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { beidou_interfaces__msg__ElderlyMotion__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { beidou_interfaces__msg__ElderlyMotion__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { beidou_interfaces__msg__ElderlyMotion__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ElderlyMotion {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ElderlyMotion where Self: Sized {
  const TYPE_NAME: &'static str = "beidou_interfaces/msg/ElderlyMotion";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__beidou_interfaces__msg__ElderlyMotion() }
  }
}


