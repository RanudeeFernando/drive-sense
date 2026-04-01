import csv
import random
import time
from sensors.sensor import Sensor

class UltrasonicSensor(Sensor):
    def __init__(self, sensor_id: int=2):
        super().__init__(sensor_id)

    def detect_slot_occupancy(self) -> bool:
        print("📡 Checking for vehicle...")
        time.sleep(1)
        return True

    def detect_exit_vehicle(self):
        return True  # simulate always detecting for now

    def get_distance(self):
        # simulate distance in cm
        return random.randint(1, 20)

    def get_slot_from_distance(self, distance):
        with open("data/slots.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                start = float(row["distance_start"])
                end = float(row["distance_end"])
                if start <= distance <= end:
                    return int(row["slot_id"])
        return None
