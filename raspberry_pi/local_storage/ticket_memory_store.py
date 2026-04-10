import csv
import os
from typing import Optional, List

from raspberry_pi.data_models.ticket import Ticket
from raspberry_pi.data_models.parking_slot import ParkingSlot
from raspberry_pi.data_models.vehicle_type import VehicleType


class TicketMemoryStore:
    def __init__(self, csv_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_storage_dir = os.path.join(base_dir, "local_storage")

        os.makedirs(local_storage_dir, exist_ok=True)

        self.csv_path = csv_path or os.path.join(local_storage_dir, "tickets_memory.csv")
        self.fieldnames = [
            "ticket_id",
            "slot_id",
            "vehicle_type",
            "entry_time",
            "exit_time",
            "duration_minutes",
            "price",
            "status",
            "pin_code",
            "pin_status"
        ]

        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()

    def _build_slot(self, slot_id: int, vehicle_type: VehicleType) -> ParkingSlot:
        return ParkingSlot(
            slot_id=slot_id,
            slot_type=vehicle_type,
            slot_length=0.0,
            slot_width=0.0,
            is_occupied=False
        )

    def _row_to_ticket(self, row: dict) -> Ticket:
        vehicle_type = VehicleType(row["vehicle_type"])
        slot = self._build_slot(int(row["slot_id"]), vehicle_type)

        return Ticket(
            ticket_id=row["ticket_id"],
            parking_slot=slot,
            vehicle_type=vehicle_type,
            entry_time=row["entry_time"],
            exit_time=row.get("exit_time", ""),
            duration_minutes=float(row.get("duration_minutes", 0) or 0),
            price=float(row.get("price", 0) or 0),
            status=row.get("status", "active"),
            pin_code=row.get("pin_code", ""),
            pin_status=row.get("pin_status", "active")
        )

    def _ticket_to_row(self, ticket: Ticket) -> dict:
        return {
            "ticket_id": ticket.get_ticket_id(),
            "slot_id": str(ticket.get_slot_id()),
            "vehicle_type": ticket.get_vehicle_type().value,
            "entry_time": ticket.get_entry_time(),
            "exit_time": ticket.get_exit_time(),
            "duration_minutes": str(ticket.get_duration_minutes()),
            "price": str(ticket.get_price()),
            "status": ticket.get_status(),
            "pin_code": ticket.get_pin_code(),
            "pin_status": ticket.get_pin_status()
        }

    def get_all_tickets(self) -> List[Ticket]:
        self._ensure_file_exists()

        tickets = []
        with open(self.csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                tickets.append(self._row_to_ticket(row))

        return tickets

    def overwrite_all_tickets(self, tickets: List[Ticket]) -> None:
        self._ensure_file_exists()

        with open(self.csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            for ticket in tickets:
                writer.writerow(self._ticket_to_row(ticket))

    def upsert_ticket(self, ticket: Ticket) -> None:
        tickets = self.get_all_tickets()
        updated = False

        for index, existing_ticket in enumerate(tickets):
            if existing_ticket.get_ticket_id() == ticket.get_ticket_id():
                tickets[index] = ticket
                updated = True
                break

        if not updated:
            tickets.append(ticket)

        self.overwrite_all_tickets(tickets)

    def get_ticket_by_id(self, ticket_id: str):
        tickets = self.get_all_tickets()
        for ticket in tickets:
            if ticket.get_ticket_id() == ticket_id:
                return ticket
        return None

    def get_active_ticket_by_slot_id(self, slot_id: int):
        tickets = self.get_all_tickets()
        for ticket in tickets:
            if ticket.get_slot_id() == slot_id and ticket.get_status() == "active":
                return ticket
        return None

    def get_active_ticket_by_pin(self, pin_code: str):
        tickets = self.get_all_tickets()
        for ticket in tickets:
            if ticket.get_pin_code() == pin_code and ticket.get_status() == "active":
                return ticket
        return None

    def generate_ticket(self, parking_slot: ParkingSlot, vehicle_type: VehicleType, ticket_id: str, pin_code: str, entry_time: str) -> dict:
        ticket = Ticket(
            ticket_id=ticket_id,
            parking_slot=parking_slot,
            vehicle_type=vehicle_type,
            entry_time=entry_time,
            exit_time="",
            duration_minutes=0,
            price=0,
            status="active",
            pin_code=pin_code,
            pin_status="active"
        )

        self.upsert_ticket(ticket)

        return {
            "ticket_id": ticket_id,
            "pin_code": pin_code,
            "entry_time": entry_time,
            "slot_id": parking_slot.get_slot_id(),
            "vehicle_type": vehicle_type.value
        }

    def update_ticket_on_exit(
        self,
        ticket_id: str,
        exit_time: str,
        duration_minutes: float,
        price: float
    ) -> bool:
        tickets = self.get_all_tickets()

        for ticket in tickets:
            if ticket.get_ticket_id() == ticket_id:
                ticket.set_exit_time(exit_time)
                ticket.set_duration_minutes(round(duration_minutes, 2))
                ticket.set_price(price)
                ticket.set_status("closed")
                ticket.set_pin_status("expired")
                self.overwrite_all_tickets(tickets)
                return True

        return False

    def seed_from_tickets(self, tickets: List[Ticket]) -> None:
        self.overwrite_all_tickets(tickets)