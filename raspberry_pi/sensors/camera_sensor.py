import os
import cv2
import time
from sensors.sensor import Sensor

class CameraSensor(Sensor):
    def __init__(self, sensor_id: int = 1, camera_index: int = 0):
        super().__init__(sensor_id, "camera sensor")
        self.camera_index = camera_index

    def capture_image(self) -> str | None:
        folder = "captured_images"
        os.makedirs(folder, exist_ok=True)

        cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            print("Cannot open USB camera")
            return None

        time.sleep(0.5)

        ret, frame = cap.read()

        if not ret:
            print("Failed to capture image")
            cap.release()
            return None

        timestamp = int(time.time())
        filename = f"vehicle_{timestamp}.jpg"
        filepath = os.path.join(folder, filename)

        cv2.imwrite(filepath, frame)
        print(f"Captured image: {filename}")

        cap.release()
        return filepath
