from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Ticket:
    ticket_id: int
    slot_id: int
    vehicle_type: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    total_minutes: Optional[int] = None
    price: float = 0.0

    def get_ticket_id(self):
        return self.ticket_id

    def set_ticket_id(self, ticket_id):
        self.ticket_id = ticket_id

    def get_slot_id(self):
        return self.slot_id

    def set_slot_id(self, slot_id):
        self.slot_id = slot_id

    def get_vehicle_type(self):
        return self.vehicle_type

    def set_vehicle_type(self, vehicle_type):
        self.vehicle_type = vehicle_type

    def get_entry_time(self):
        return self.entry_time

    def set_entry_time(self, entry_time):
        self.entry_time = entry_time

    def get_exit_time(self):
        return self.exit_time

    def set_exit_time(self, exit_time):
        self.exit_time = exit_time

    def generate_ticket(self):
        return {
            "ticket_id": self.ticket_id,
            "slot_id": self.slot_id,
            "vehicle_type": self.vehicle_type,
            "entry_time": str(self.entry_time),
        }