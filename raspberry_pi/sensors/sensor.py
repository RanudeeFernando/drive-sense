class Sensor:
    def __init__(self, sensor_id: int, name: str):
        self._sensor_id = sensor_id
        self._name = name

    def get_sensor_id(self) -> int:
        return self._sensor_id

    def get_sensor_name(self) -> str:
        return self._name