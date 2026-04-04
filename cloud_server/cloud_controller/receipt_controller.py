from datetime import datetime

from cloud_server.repositories.ticket_repository import TicketRepository
from cloud_server.repositories.slot_repository import SlotRepository


class ReceiptController:
    def __init__(self):
        self.ticket_repository = TicketRepository()
        self.slot_repository = SlotRepository()

        # You can adjust these rates later
        self.rates = {
            "bike": 50.0,
            "car": 100.0,
            "lorry": 150.0,
            "heavy_vehicle": 150.0
        }

    def calculate_duration_hours(self, entry_time_str: str, exit_time: datetime):
        entry_time = datetime.fromisoformat(entry_time_str)
        duration_seconds = (exit_time - entry_time).total_seconds()
        duration_hours = duration_seconds / 3600

        # Optional: round up minimum billing to 1 hour
        if duration_hours <= 0:
            return 1.0

        return round(duration_hours, 2)

    def calculate_amount(self, vehicle_type: str, duration_hours: float):
        rate = self.rates.get(vehicle_type, 100.0)
        return round(rate * duration_hours, 2)

    def process_receipt(self, ticket_id: str):
        # Step 1: get ticket from Firestore
        ticket = self.ticket_repository.get_ticket(ticket_id)

        if not ticket:
            return {
                "status": "failed",
                "message": "Ticket not found",
                "ticket_id": ticket_id
            }

        # Step 2: prevent double closing
        if ticket.get("status") == "closed":
            return {
                "status": "failed",
                "message": "Ticket is already closed",
                "ticket_id": ticket_id
            }

        entry_time_str = ticket.get("entry_time")
        vehicle_type = ticket.get("vehicle_type")
        slot_id = ticket.get("slot_id")

        if not entry_time_str or not vehicle_type or not slot_id:
            return {
                "status": "failed",
                "message": "Ticket data is incomplete",
                "ticket_id": ticket_id
            }

        # Step 3: calculate receipt values
        exit_time = datetime.now()
        duration_hours = self.calculate_duration_hours(entry_time_str, exit_time)
        amount = self.calculate_amount(vehicle_type, duration_hours)

        # Step 4: update ticket in Firestore
        self.ticket_repository.close_ticket(ticket_id, duration_hours, amount)

        # Step 5: release related slot
        all_slots = self.slot_repository.get_all_slots()
        matching_slot = None

        for slot in all_slots:
            if slot.get("slot_id") == slot_id:
                matching_slot = slot
                break

        if matching_slot:
            self.slot_repository.release_slot(matching_slot["id"])

        # Step 6: return receipt response
        return {
            "status": "success",
            "message": "Receipt generated successfully",
            "ticket_id": ticket_id,
            "vehicle_type": vehicle_type,
            "slot_id": slot_id,
            "entry_time": entry_time_str,
            "exit_time": exit_time.isoformat(),
            "duration_hours": duration_hours,
            "amount": amount
        }