cmake_minimum_required(VERSION 3.8)
project(so101_bringup)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/so101_joint_state_bridge.py
  DESTINATION lib/${PROJECT_NAME}
)

install(
  FILES scripts/camera_publisher.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
