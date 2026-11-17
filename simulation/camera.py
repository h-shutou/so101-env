from pathlib import Path

import mujoco
from PIL import Image


def capture_cameras(
    model,
    data,
    output_dir="results/cameras",
    cameras=("top", "wrist"),
    width=640,
    height=480,
):
    output_dir = Path(output_dir)

    for name in cameras:
        camera_id = mujoco.mj_name2id(
            model, mujoco.mjtObj.mjOBJ_CAMERA, name
        )
        if camera_id < 0:
            raise ValueError(f"Camera not found: {name}")

    output_dir.mkdir(parents=True, exist_ok=True)

    mujoco.mj_forward(model, data)

    renderer = mujoco.Renderer(
        model, height=height, width=width
    )

    saved = []

    try:
        for name in cameras:
            renderer.update_scene(data, camera=name)
            image = renderer.render().copy()

            path = output_dir / f"{name}.png"
            Image.fromarray(image).save(path)
            saved.append(path)
    finally:
        renderer.close()

    return saved
