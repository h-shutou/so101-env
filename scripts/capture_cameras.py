import argparse

from simulation.environment import SO101Simulation
from simulation.camera import capture_cameras


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="results/cameras",
    )
    parser.add_argument(
        "--camera",
        choices=("top", "wrist"),
        action="append",
    )
    args = parser.parse_args()

    sim = SO101Simulation()

    cameras = args.camera or ("top", "wrist")

    paths = capture_cameras(
        sim.model,
        sim.data,
        output_dir=args.output_dir,
        cameras=cameras,
    )

    for path in paths:
        print(f"Saved: {path}")

    print("Camera capture passed!")


if __name__ == "__main__":
    main()
