import os
import random
from sensors.sensor import Sensor

class CameraSensor(Sensor):
    def __init__(self, sensor_id: int =1):
        super().__init__(sensor_id)

    def capture_image(self) -> str:
        folder = "test"
        images = [f for f in os.listdir(folder) if f.endswith((".jpg", ".jpeg", ".png"))]
        image = random.choice(images)
        path = os.path.join(folder, image)
        print(f"📸 Captured: {image}")
        return path