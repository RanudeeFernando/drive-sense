class Sensor:
    """
    Base class for all sensors in the system.
    Stores common attributes like sensor ID and sensor name.
    """
    def __init__(self, sensor_id: int, name: str):
        self._sensor_id = sensor_id
        self._name = name

    def get_sensor_id(self) -> int:
        return self._sensor_id

    def get_sensor_name(self) -> str:
        return self._name