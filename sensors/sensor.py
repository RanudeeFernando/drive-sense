class Sensor:
    def __init__(self, sensor_id: int):
        self._sensor_id = sensor_id

    def get_sensor_id(self) -> int:
        return self._sensor_id

    def set_sensor_id(self, sensor_id: int) -> None:
        self._sensor_id = sensor_id
