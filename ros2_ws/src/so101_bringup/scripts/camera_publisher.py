import mujoco
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class CameraPublisher:
    def __init__(self, node, model, data, width=320, height=240):
        self.node = node
        self.data = data
        self.renderer = mujoco.Renderer(
            model, width=width, height=height
        )

        self.publishers = {
            name: node.create_publisher(
                Image,
                f"/camera/{name}/image_raw",
                qos_profile_sensor_data,
            )
            for name in ("top", "wrist")
        }

    def publish(self):
        stamp = self.node.get_clock().now().to_msg()

        for name, publisher in self.publishers.items():
            self.renderer.update_scene(self.data, camera=name)
            image = self.renderer.render()

            msg = Image()
            msg.header.stamp = stamp
            msg.header.frame_id = f"{name}_camera_optical_frame"
            msg.height = image.shape[0]
            msg.width = image.shape[1]
            msg.encoding = "rgb8"
            msg.is_bigendian = 0
            msg.step = image.shape[1] * 3
            msg.data = image.tobytes()

            publisher.publish(msg)

    def close(self):
        self.renderer.close()
