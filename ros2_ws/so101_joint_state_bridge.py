from pathlib import Path
import math

import mujoco
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from camera_publisher import CameraPublisher
from trajectory_msgs.msg import JointTrajectory


SCENE = (
    Path(__file__).resolve().parents[1]
    / "assets/robots/so101/so_arm101_description/mjcf/workspace.xml"
)

JOINT_NAMES = (
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_flex_joint",
    "wrist_flex_joint",
    "wrist_roll_joint",
    "gripper_joint",
)


class SO101Bridge(Node):
    def __init__(self):
        super().__init__("so101_mujoco_bridge")

        self.model = mujoco.MjModel.from_xml_path(str(SCENE))
        self.data = mujoco.MjData(self.model)
        mujoco.mj_forward(self.model, self.data)

        self.joint_ids = [
            mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_JOINT, name
            )
            for name in JOINT_NAMES
        ]

        self.actuator_ids = [
            mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, name
            )
            for name in JOINT_NAMES
        ]

        if any(i < 0 for i in self.joint_ids + self.actuator_ids):
            raise RuntimeError("SO-101 joint or actuator not found")

        for jid, aid in zip(self.joint_ids, self.actuator_ids):
            self.data.ctrl[aid] = self.data.qpos[
                self.model.jnt_qposadr[jid]
            ]

        self.publisher = self.create_publisher(
            JointState, "/joint_states", 10
        )

        self.subscription = self.create_subscription(
            JointTrajectory,
            "/so101_controller/joint_trajectory",
            self.on_command,
            10,
        )

        self.active = None
        self.period = 0.1
        self.steps = max(
            1, round(self.period / self.model.opt.timestep)
        )

        self.camera_publisher = CameraPublisher(
            self, self.model, self.data
        )
        self.camera_ticks = 0
        self.timer = self.create_timer(self.period, self.update)

        self.get_logger().info(
            "SO-101 MuJoCo bridge started (simulation only)"
        )

    def on_command(self, msg):
        if (
            len(msg.points) != 1
            or len(msg.joint_names) != len(JOINT_NAMES)
            or set(msg.joint_names) != set(JOINT_NAMES)
        ):
            self.get_logger().warning(
                "Expected one point and all six joint names"
            )
            return

        point = msg.points[0]
        if len(point.positions) != len(JOINT_NAMES):
            self.get_logger().warning("Invalid position count")
            return

        duration = (
            point.time_from_start.sec
            + point.time_from_start.nanosec / 1e9
        )
        if not 0.2 <= duration <= 10.0:
            self.get_logger().warning(
                "Duration must be between 0.2 and 10 seconds"
            )
            return

        requested = dict(zip(msg.joint_names, point.positions))
        targets = []

        for name, jid, aid in zip(
            JOINT_NAMES, self.joint_ids, self.actuator_ids
        ):
            target = float(requested[name])

            if not math.isfinite(target):
                self.get_logger().warning("Non-finite target")
                return

            if self.model.actuator_ctrllimited[aid]:
                low, high = self.model.actuator_ctrlrange[aid]
                if not low <= target <= high:
                    self.get_logger().warning(
                        f"Actuator limit exceeded: {name}"
                    )
                    return

            if self.model.jnt_limited[jid]:
                low, high = self.model.jnt_range[jid]
                if not low <= target <= high:
                    self.get_logger().warning(
                        f"Joint limit exceeded: {name}"
                    )
                    return

            targets.append(target)

        starts = [
            float(self.data.ctrl[aid])
            for aid in self.actuator_ids
        ]

        self.active = (
            starts,
            targets,
            float(self.data.time),
            duration,
        )
        self.get_logger().info("Trajectory accepted")

    def update(self):
        for _ in range(self.steps):
            if self.active is not None:
                starts, targets, start_time, duration = self.active

                progress = min(
                    1.0,
                    max(0.0, (self.data.time - start_time) / duration),
                )
                smooth = progress * progress * (3 - 2 * progress)

                for aid, start, target in zip(
                    self.actuator_ids, starts, targets
                ):
                    self.data.ctrl[aid] = (
                        start + (target - start) * smooth
                    )

                if progress >= 1.0:
                    self.active = None

            mujoco.mj_step(self.model, self.data)

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINT_NAMES)
        msg.position = [
            float(self.data.qpos[self.model.jnt_qposadr[jid]])
            for jid in self.joint_ids
        ]
        msg.velocity = [
            float(self.data.qvel[self.model.jnt_dofadr[jid]])
            for jid in self.joint_ids
        ]

        self.publisher.publish(msg)
        self.camera_ticks += 1
        if self.camera_ticks % 2 == 0:
            self.camera_publisher.publish()


def main():
    rclpy.init()
    node = None
    try:
        node = SO101Bridge()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.camera_publisher.close()
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
