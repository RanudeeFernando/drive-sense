from sensors.sensor import Sensor


class LightSensor(Sensor):
    def __init__(self, sensor_id, threshold=300):
        super().__init__(sensor_id)
        self.threshold = threshold

    def detect_light_level(self):
        return 250

    def is_dark(self):
        return self.detect_light_level() < self.threshold