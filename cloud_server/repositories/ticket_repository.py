
from datetime import datetime
import random

from cloud_server.cloud_db.firestore_client import get_db
from raspberry_pi.data_models.ticket import Ticket
from raspberry_pi.data_models.parking_slot import ParkingSlot
from raspberry_pi.data_models.vehicle_type import VehicleType
from cloud_server.repositories.slot_repository import SlotRepository


class TicketRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("tickets")
        self.slot_repository = SlotRepository()

    @staticmethod
    def _build_fallback_slot(slot_id: int, vehicle_type: VehicleType) -> ParkingSlot:
        return ParkingSlot(
            slot_id=slot_id,
            slot_type=vehicle_type,
            is_occupied=False
        )



    def _doc_to_ticket(self, doc) -> Ticket:
        """
        Converts a database document into a Ticket object.

        Reads ticket data from Firestore and maps it into a Ticket model,
        including fallback slot handling if the slot is missing.
        """
        data = doc.to_dict()

        slot_id = int(data["slot_id"])
        vehicle_type = VehicleType(data["vehicle_type"])

        parking_slot = self.slot_repository.get_slot_by_id(slot_id)

        if parking_slot is None:
            parking_slot = self._build_fallback_slot(slot_id, vehicle_type)

        return Ticket(
            ticket_id=data["ticket_id"],
            parking_slot=parking_slot,
            vehicle_type=vehicle_type,
            entry_time=data["entry_time"],
            exit_time=data.get("exit_time", ""),
            duration_minutes=float(data.get("duration_minutes", 0)),
            price=float(data.get("price", 0)),
            status=data.get("status", "active"),
            pin_code=data.get("pin_code", ""),
            pin_status=data.get("pin_status", "active")
        )



    def get_all_tickets(self):
        """Returns all tickets from Firestore, ordered by entry time descending"""
        docs = self.collection.order_by("entry_time", direction="DESCENDING").stream()
        return [self._doc_to_ticket(doc) for doc in docs]