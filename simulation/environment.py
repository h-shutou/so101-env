from pathlib import Path
import mujoco

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENE = (
    ROOT / "assets/robots/so101/"
    "so_arm101_description/mjcf/workspace.xml"
)


class SO101Simulation:
    def __init__(self, scene_path=DEFAULT_SCENE):
        self.model = mujoco.MjModel.from_xml_path(
            str(scene_path)
        )
        self.data = mujoco.MjData(self.model)
        self.reset()

    def reset(self):
        mujoco.mj_resetData(self.model, self.data)
        mujoco.mj_forward(self.model, self.data)

    def step(self, steps=1):
        if steps < 1:
            raise ValueError("steps must be >= 1")
        for _ in range(steps):
            mujoco.mj_step(self.model, self.data)

    def status(self):
        return {
            "time": float(self.data.time),
            "joints": self.model.njnt,
            "actuators": self.model.nu,
            "cameras": self.model.ncam,
        }
