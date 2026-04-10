from datetime import datetime
import random

from raspberry_pi.cloud_db.firestore_client import get_db
from raspberry_pi.data_models.ticket import Ticket
from raspberry_pi.data_models.parking_slot import ParkingSlot
from raspberry_pi.data_models.vehicle_type import VehicleType
from raspberry_pi.local_storage.ticket_memory_store import TicketMemoryStore
from raspberry_pi.repositories.slot_repository import SlotRepository


class TicketRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("tickets")
        self.slot_repository = SlotRepository()
        self.memory_store = TicketMemoryStore()

    @staticmethod
    def _build_fallback_slot(slot_id: int, vehicle_type: VehicleType) -> ParkingSlot:
        return ParkingSlot(
            slot_id=slot_id,
            slot_type=vehicle_type,
            slot_length=0.0,
            slot_width=0.0,
            is_occupied=False
        )

    def generate_pin_code(self) -> str:
        while True:
            pin = f"{random.randint(0, 9999):04d}"
            existing_ticket = self.get_active_ticket_by_pin(pin)
            if existing_ticket is None:
                return pin

    def _doc_to_ticket(self, doc) -> Ticket:
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

    def generate_ticket(self, parking_slot: ParkingSlot, vehicle_type: VehicleType) -> dict:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        ticket_id = f"DST-{timestamp}"
        pin_code = self.generate_pin_code()
        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

        try:
            doc_ref = self.collection.document(ticket_id)
            doc_ref.set(ticket.to_dict())
        except Exception:
            pass

        self.memory_store.upsert_ticket(ticket)

        return {
            "ticket_id": ticket_id,
            "pin_code": pin_code,
            "entry_time": entry_time,
            "slot_id": parking_slot.get_slot_id(),
            "vehicle_type": vehicle_type.value
        }

    def get_ticket_by_id(self, ticket_id: str):
        try:
            doc = self.collection.document(ticket_id).get()
            if doc.exists:
                ticket = self._doc_to_ticket(doc)
                self.memory_store.upsert_ticket(ticket)
                return ticket
            return None
        except Exception:
            return self.memory_store.get_ticket_by_id(ticket_id)

    def get_active_ticket_by_slot_id(self, slot_id: int):
        try:
            docs = (
                self.collection
                .where("slot_id", "==", slot_id)
                .where("status", "==", "active")
                .limit(1)
                .stream()
            )

            found_ticket = None
            for doc in docs:
                found_ticket = self._doc_to_ticket(doc)
                break

            self._sync_tickets_from_firestore()
            return found_ticket

        except Exception:
            return self.memory_store.get_active_ticket_by_slot_id(slot_id)

    def get_active_ticket_by_pin(self, pin_code: str):
        try:
            docs = (
                self.collection
                .where("pin_code", "==", pin_code)
                .where("status", "==", "active")
                .limit(1)
                .stream()
            )

            found_ticket = None
            for doc in docs:
                found_ticket = self._doc_to_ticket(doc)
                break

            self._sync_tickets_from_firestore()
            return found_ticket

        except Exception:
            return self.memory_store.get_active_ticket_by_pin(pin_code)

    def update_ticket_on_exit(
        self,
        ticket_id: str,
        exit_time: datetime,
        duration_minutes: float,
        price: float
    ) -> bool:
        exit_time_str = exit_time.strftime("%Y-%m-%d %H:%M:%S")

        firestore_success = False

        try:
            doc_ref = self.collection.document(ticket_id)
            doc = doc_ref.get()

            if doc.exists:
                doc_ref.update({
                    "exit_time": exit_time_str,
                    "duration_minutes": round(duration_minutes, 2),
                    "price": price,
                    "status": "closed",
                    "pin_status": "expired"
                })
                firestore_success = True
        except Exception:
            pass

        memory_success = self.memory_store.update_ticket_on_exit(
            ticket_id=ticket_id,
            exit_time=exit_time_str,
            duration_minutes=duration_minutes,
            price=price
        )

        return firestore_success or memory_success

    def get_all_tickets(self):
        try:
            docs = self.collection.order_by("entry_time", direction="DESCENDING").stream()
            tickets = [self._doc_to_ticket(doc) for doc in docs]
            self.memory_store.seed_from_tickets(tickets)
            return tickets
        except Exception:
            return self.memory_store.get_all_tickets()

    def _sync_tickets_from_firestore(self) -> None:
        try:
            docs = self.collection.stream()
            tickets = [self._doc_to_ticket(doc) for doc in docs]
            self.memory_store.seed_from_tickets(tickets)
        except Exception:
            pass