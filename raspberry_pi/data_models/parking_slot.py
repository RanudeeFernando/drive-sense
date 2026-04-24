from raspberry_pi.data_models.vehicle_type import VehicleType


class ParkingSlot:
    """
    Represents a parking slot with its dimensions, type, and occupancy status.
    Provides getter and setter methods to manage slot properties.
    """
    def __init__(
        self,
        slot_id: int,
        slot_type: VehicleType,
        slot_length: float,
        slot_width: float,
        is_occupied: bool = False
    ):
        self._slot_id = slot_id
        self._slot_type = slot_type
        self._slot_length = slot_length
        self._slot_width = slot_width
        self._is_occupied = is_occupied

    def set_slot_id(self, slot_id: int) -> None:
        self._slot_id = slot_id

    def get_slot_id(self) -> int:
        return self._slot_id

    def set_slot_type(self, slot_type: VehicleType) -> None:
        self._slot_type = slot_type

    def get_slot_type(self) -> VehicleType:
        return self._slot_type

    def set_slot_length(self, slot_length: float) -> None:
        self._slot_length = slot_length

    def get_slot_length(self) -> float:
        return self._slot_length

    def set_slot_width(self, slot_width: float) -> None:
        self._slot_width = slot_width

    def get_slot_width(self) -> float:
        return self._slot_width

    def set_slot_status(self, status: bool) -> None:
        self._is_occupied = status

    def get_slot_status(self) -> bool:
        return self._is_occupied

    def to_dict(self) -> dict:
        return {
            "slot_id": self._slot_id,
            "slot_type": self._slot_type.value,
            "slot_length": self._slot_length,
            "slot_width": self._slot_width,
            "is_occupied": self._is_occupied,
        }