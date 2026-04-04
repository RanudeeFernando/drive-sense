from cloud_server.cloud.firestore_client import get_db
from cloud_server.data_models.vehicle_type import VehicleType


class ParkingSlot:
    def __init__(self, slot_id: int = 1, slot_type: str = "car",
                 slot_length: float = 5, slot_width: float = 2):
        self._slot_id = slot_id
        self._slot_type = slot_type
        self._slot_length = slot_length
        self._slot_width = slot_width
        self._is_occupied = False

    def set_slot_id(self, slot_id: int) -> None:
        self._slot_id = slot_id

    def get_slot_id(self) -> int:
        return self._slot_id

    def set_slot_type(self, slot_type: str) -> None:
        self._slot_type = slot_type

    def get_slot_type(self) -> str:
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

    def find_available_slot(self, vehicle_type: VehicleType):
        """Return the first unoccupied slot_id matching the vehicle type, or None."""
        db = get_db()
        slots = (
            db.collection("slots")
            .where("slot_type", "==", str(vehicle_type.value))
            .where("is_occupied", "==", False)
            .limit(1)
            .stream()
        )
        for slot in slots:
            return slot.get("slot_id")
        return None

    def reserve_slot(self, slot_id) -> None:
        """Mark a slot as occupied in Firestore."""
        db = get_db()
        db.collection("slots").document(str(slot_id)).update({"is_occupied": True})
        print(f"Slot {slot_id} reserved")

    def release_slot(self, slot_id: int) -> bool:
        """Mark a slot as free in Firestore."""
        db = get_db()
        db.collection("slots").document(str(slot_id)).update({"is_occupied": False})
        print(f"Slot {slot_id} released")
        return True