from datetime import datetime
from cloud_server.cloud.firestore_client import get_db
from cloud_server.data_models.vehicle_type import VehicleType, PARKING_RATES


class Receipt:
    def __init__(self, exit_time: str = "", price: float = 0.0):
        self._exit_time = exit_time
        self._price = price

    def get_exit_time(self) -> str:
        return self._exit_time

    def set_exit_time(self, exit_time: str) -> None:
        self._exit_time = exit_time

    def get_price(self) -> float:
        return self._price

    def set_price(self, price: float) -> None:
        self._price = price

    def generate_receipt(self, ticket_id: str, slot_id: int,
                         vehicle_type: str, entry_time) -> str:
        db = get_db()

        # Store receipt document in Firestore (auto-generated ID)
        db.collection("receipts").add({
            "ticket_id": ticket_id,
            "slot_id": str(slot_id),
            "vehicle_type": str(vehicle_type),
            "entry_time": str(entry_time),
            "exit_time": self._exit_time,
            "total_amount": round(self._price, 2)
        })

        return (f"--- RECEIPT ---\n"
                f"Ticket ID: {ticket_id}\n"
                f"Slot ID: {slot_id}\n"
                f"Vehicle Type: {vehicle_type}\n"
                f"Entry Time: {entry_time}\n"
                f"Exit Time: {self._exit_time}\n"
                f"Total Amount: Rs.{self._price:.2f}\n"
                f"---------------")

    def calculate_price(self, vehicle_type: str, duration_hours: float) -> float:
        # Look up rate from centralised PARKING_RATES in vehicle_type.py
        try:
            rate = PARKING_RATES[VehicleType(vehicle_type.lower())]
        except (ValueError, KeyError):
            rate = 100  # default fallback
        self._price = rate * duration_hours
        return self._price