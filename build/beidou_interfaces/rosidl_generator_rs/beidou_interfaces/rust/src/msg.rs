#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to beidou_interfaces__msg__ElderlyMotion

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ElderlyMotion {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::ElderlyMotion::default())
  }
}

impl rosidl_runtime_rs::Message for ElderlyMotion {
  type RmwMsg = super::msg::rmw::ElderlyMotion;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        vx: msg.vx,
        vy: msg.vy,
        speed: msg.speed,
        heading: msg.heading,
        valid: msg.valid,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
      vx: msg.vx,
      vy: msg.vy,
      speed: msg.speed,
      heading: msg.heading,
      valid: msg.valid,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      vx: msg.vx,
      vy: msg.vy,
      speed: msg.speed,
      heading: msg.heading,
      valid: msg.valid,
    }
  }
}


