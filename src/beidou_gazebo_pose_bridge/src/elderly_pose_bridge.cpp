#include <memory>
#include <stdexcept>
#include <string>
#include <utility>

#include <geometry_msgs/msg/transform_stamped.hpp>
#include <gz/msgs/pose_v.pb.h>
#include <gz/transport/Node.hh>
#include <rclcpp/rclcpp.hpp>
#include <tf2_msgs/msg/tf_message.hpp>

class ElderlyPoseBridge : public rclcpp::Node
{
public:
  ElderlyPoseBridge()
  : Node("elderly_pose_bridge")
  {
    const auto gz_topic = declare_parameter<std::string>(
      "gz_topic", "/world/elderly_home/pose/info");
    const auto ros_topic = declare_parameter<std::string>(
      "ros_topic", "/world/elderly_home/pose/named");
    publisher_ = create_publisher<tf2_msgs::msg::TFMessage>(ros_topic, 10);

    const bool subscribed = gz_node_.Subscribe(
      gz_topic, &ElderlyPoseBridge::on_pose, this);
    if (!subscribed) {
      throw std::runtime_error("Unable to subscribe to " + gz_topic);
    }
    RCLCPP_INFO(
      get_logger(), "Bridging named Gazebo poses from %s to %s",
      gz_topic.c_str(), ros_topic.c_str());
  }

private:
  void on_pose(const gz::msgs::Pose_V & message)
  {
    tf2_msgs::msg::TFMessage output;
    output.transforms.reserve(message.pose_size());
    for (const auto & pose : message.pose()) {
      geometry_msgs::msg::TransformStamped transform;
      if (message.has_header() && message.header().has_stamp()) {
        transform.header.stamp.sec = message.header().stamp().sec();
        transform.header.stamp.nanosec = message.header().stamp().nsec();
      }
      transform.header.frame_id = "gazebo_world";
      transform.child_frame_id = pose.name();
      transform.transform.translation.x = pose.position().x();
      transform.transform.translation.y = pose.position().y();
      transform.transform.translation.z = pose.position().z();
      transform.transform.rotation.x = pose.orientation().x();
      transform.transform.rotation.y = pose.orientation().y();
      transform.transform.rotation.z = pose.orientation().z();
      transform.transform.rotation.w = pose.orientation().w();
      output.transforms.push_back(std::move(transform));
    }
    publisher_->publish(std::move(output));
  }

  gz::transport::Node gz_node_;
  rclcpp::Publisher<tf2_msgs::msg::TFMessage>::SharedPtr publisher_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  try {
    rclcpp::spin(std::make_shared<ElderlyPoseBridge>());
  } catch (const std::exception & error) {
    RCLCPP_FATAL(
      rclcpp::get_logger("elderly_pose_bridge"), "%s", error.what());
    rclcpp::shutdown();
    return 1;
  }
  rclcpp::shutdown();
  return 0;
}
