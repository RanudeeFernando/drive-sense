import csv
import random
import time
from sensors.sensor import Sensor

class UltrasonicSensor(Sensor):
    def __init__(self, sensor_id: int=2):
        super().__init__(sensor_id)

    def detect_entry_vehicle(self) -> bool:
        print("📡 Checking for vehicle...")
        time.sleep(1)

        distance = self.get_distance()
        print(f"📏Vehicle detcted from a  {distance} cm distance:")

    
        if distance < 21:
            print("🚗 Vehicle Detected!")
            return True
        else:
            return False

    def detect_exit_vehicle(self):
        return True  # simulate always detecting for now

    def get_distance(self):
        # simulate distance in cm
        return random.randint(1, 20)


