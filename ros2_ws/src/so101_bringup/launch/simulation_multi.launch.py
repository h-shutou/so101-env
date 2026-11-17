from pathlib import Path
import subprocess

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.actions import Node


def generate_launch_description():
    description_dir = Path(
        get_package_share_directory("so_arm101_description")
    )

    xacro_file = description_dir / "urdf/so_arm101.urdf.xacro"

    robot_description = subprocess.check_output(
        [
            "xacro",
            str(xacro_file),
            "color:=0.93 0.93 0.93 1.0",
        ],
        text=True,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "foxglove_port",
            default_value="18765",
        ),
        Node(
            package="so101_bringup",
            executable="so101_joint_state_bridge.py",
            additional_env={"MUJOCO_GL": "egl"},
            output="screen",
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[
                {"robot_description": robot_description}
            ],
            output="screen",
        ),
        Node(
            package="foxglove_bridge",
            executable="foxglove_bridge",
            parameters=[
                {
                    "port": ParameterValue(LaunchConfiguration("foxglove_port"), value_type=int),
                    "address": "127.0.0.1",
                }
            ],
            output="screen",
        ),
    ])
