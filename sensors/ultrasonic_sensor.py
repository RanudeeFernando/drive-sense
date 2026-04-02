from sensors.sensor import Sensor
import random

class UltrasonicSensor(Sensor):
    def __init__(self, sensor_id, trig_pin=None, echo_pin=None, mock_mode=True):
        super().__init__(sensor_id)
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.mock_mode = mock_mode

    def get_distance(self):
        if self.mock_mode:
            # Simulate a car randomly passing by in mock mode
            # 10% chance of a car being close (under 10cm)
            if random.random() < 0.1:
                return random.uniform(2.0, 9.0)
            return random.uniform(50.0, 200.0)
        else:
            # Hardware integration placeholder for real RPi GPIO
            return 35.0

    def detect_slot_occupancy(self, threshold=10.0):
        dist = self.get_distance()
        return dist < threshold