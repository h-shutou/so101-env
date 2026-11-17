import math
import mujoco


def set_joint_target(sim, joint_name, target):
    if not math.isfinite(target):
        raise ValueError("Target must be finite")

    actuator_id = mujoco.mj_name2id(
        sim.model,
        mujoco.mjtObj.mjOBJ_ACTUATOR,
        joint_name,
    )

    if actuator_id < 0:
        raise ValueError(f"Unknown actuator: {joint_name}")

    low, high = sim.model.actuator_ctrlrange[actuator_id]

    if not low <= target <= high:
        raise ValueError(
            f"{joint_name}: target {target} "
            f"outside [{low}, {high}]"
        )

    sim.data.ctrl[actuator_id] = target


def get_joint_position(sim, joint_name):
    joint_id = mujoco.mj_name2id(
        sim.model,
        mujoco.mjtObj.mjOBJ_JOINT,
        joint_name,
    )

    if joint_id < 0:
        raise ValueError(f"Unknown joint: {joint_name}")

    address = sim.model.jnt_qposadr[joint_id]
    return float(sim.data.qpos[address])
