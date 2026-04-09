import os
import shutil
# import cv2
import time
from sensors.sensor import Sensor

class CameraSensor(Sensor):
    def __init__(self, sensor_id: int = 1, camera_index: int = 0):
        super().__init__(sensor_id, "camera sensor")
        self.camera_index = camera_index

    def capture_image(self) -> str | None:
        # folder = "captured_images"
        # os.makedirs(folder, exist_ok=True)

        # cap = cv2.VideoCapture(self.camera_index)

        # if not cap.isOpened():
        #     print("Cannot open USB camera")
        #     return None

        # time.sleep(0.5)

        # ret, frame = cap.read()

        # if not ret:
        #     print("Failed to capture image")
        #     cap.release()
        #     return None

        # timestamp = int(time.time())
        # filename = f"vehicle_{timestamp}.jpg"
        # filepath = os.path.join(folder, filename)

        # cv2.imwrite(filepath, frame)
        # print(f"Captured image: {filename}")

        # cap.release()
        filepath = "C:\\Users\\Binara Mendis\\Desktop\\DRIVE SENSE\\drive-sense\\raspberry_pi\\sensors\\captured_images\\WhatsApp Image 2026-04-07 at 8.46.02 PM.jpeg"
        
        return filepath
    
    def move_to_class_folder(self, vehicle_type, img_path):
        vehicle_type = vehicle_type.lower()

        if vehicle_type not in ["car", "bike", "lorry"]:
            vehicle_type = "unknown"

        folder_path = os.path.join("captured_images", vehicle_type)
        os.makedirs(folder_path, exist_ok=True)

        new_path = os.path.join(folder_path, os.path.basename(img_path))

        # MOVE the file (important)
        shutil.move(img_path, new_path)

        return new_path


        

    
