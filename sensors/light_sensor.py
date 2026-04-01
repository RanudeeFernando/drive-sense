import random

from sensors.sensor import Sensor

class LightSensor(Sensor):
    def __init__(self, sensor_id: int = 3):
        super().__init__(sensor_id)
        
    def detect_light_level(self) -> float:
        # Simulate resistance value (LDR)
        return random.randint(1, 30)