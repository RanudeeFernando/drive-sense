from datetime import datetime
from cloud_server.cloud.firestore_client import get_db
from cloud_server.data_models.parking_slot import ParkingSlot
from cloud_server.data_models.vehicle_type import VehicleType


class Ticket:
    def __init__(self, ticket_id: str = "", parking_slot: ParkingSlot = None,
                 vehicle_type: str = "car", entry_time: str = ""):
        self._ticket_id = ticket_id
        self._parking_slot = parking_slot
        self._vehicle_type = vehicle_type
        self._entry_time = entry_time

    def get_ticket_id(self) -> str:
        return self._ticket_id

    def set_ticket_id(self, ticket_id: str) -> None:
        self._ticket_id = ticket_id

    def get_parking_slot(self) -> ParkingSlot:
        return self._parking_slot

    def set_parking_slot(self, parking_slot: ParkingSlot) -> None:
        self._parking_slot = parking_slot

    def get_vehicle_type(self) -> str:
        return self._vehicle_type

    def set_vehicle_type(self, vehicle_type: str) -> None:
        self._vehicle_type = vehicle_type

    def get_entry_time(self) -> str:
        return self._entry_time

    def set_entry_time(self, entry_time: str) -> None:
        self._entry_time = entry_time

    def generate_ticket(self, slot_id, vehicle_type: VehicleType) -> str:
        db = get_db()

        # Timestamp-based ID — unique, human-readable, chronologically sortable
        ticket_id = f"DST-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db.collection("tickets").document(ticket_id).set({
            "ticket_id": ticket_id,
            "slot_id": str(slot_id),
            "vehicle_type": str(vehicle_type.value),
            "entry_time": entry_time,
            "exit_time": ""
        })

        print(f"Ticket {ticket_id} generated for slot {slot_id}")
        return ticket_id