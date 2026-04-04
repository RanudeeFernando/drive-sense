from datetime import datetime
import uuid

from cloud_server.repositories.slot_repository import SlotRepository
from cloud_server.repositories.ticket_repository import TicketRepository


class TicketingController:
    def __init__(self):
        self.slot_repository = SlotRepository()
        self.ticket_repository = TicketRepository()

    def generate_ticket_id(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        short_uuid = str(uuid.uuid4())[:6].upper()
        return f"TICKET-{timestamp}-{short_uuid}"

    def process_ticket(self, vehicle_type):
        available_slot = self.slot_repository.get_available_slot_by_type(vehicle_type)

        if not available_slot:
            return {
                "status": "failed",
                "message": f"No available {vehicle_type} slots",
                "ticket_id": None,
                "slot_id": None
            }

        slot_doc_id = available_slot["id"]
        slot_id = available_slot.get("slot_id", slot_doc_id)

        self.slot_repository.reserve_slot(slot_doc_id)

        ticket_id = self.generate_ticket_id()
        self.ticket_repository.create_ticket(
            ticket_id=ticket_id,
            vehicle_type=vehicle_type,
            slot_id=slot_id
        )

        return {
            "status": "success",
            "message": f"{vehicle_type} allocated to slot {slot_id}",
            "ticket_id": ticket_id,
            "slot_id": slot_id
        }