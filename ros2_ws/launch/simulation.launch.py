from pathlib import Path
import subprocess
import sys

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    workspace = Path(__file__).resolve().parent.parent

    bridge_script = workspace / "so101_joint_state_bridge.py"

    description_dir = Path(
        get_package_share_directory("so_arm101_description")
    )

    xacro_file = (
        description_dir / "urdf/so_arm101.urdf.xacro"
    )

    robot_description = subprocess.check_output(
        [
            "xacro",
            str(xacro_file),
            "color:=0.93 0.93 0.93 1.0",
        ],
        text=True,
    )

    return LaunchDescription([
        # MuJoCo simulation and ROS 2 bridge
        ExecuteProcess(
            cmd=[sys.executable, str(bridge_script)],
            additional_env={"MUJOCO_GL": "egl"},
            output="screen",
        ),

        # SO-101 URDF and TF publisher
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[
                {"robot_description": robot_description}
            ],
            output="screen",
        ),

        # Foxglove WebSocket server
        Node(
            package="foxglove_bridge",
            executable="foxglove_bridge",
            parameters=[
                {
                    "port": 18765,
                    "address": "127.0.0.1",
                }
            ],
            output="screen",
        ),
    ])
