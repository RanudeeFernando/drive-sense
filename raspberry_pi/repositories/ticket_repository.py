
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
            is_occupied=False,
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
            pin_status=data.get("pin_status", "active"),
        )

    def generate_ticket(self, parking_slot: ParkingSlot, vehicle_type: VehicleType) -> dict:
        """
        CSV first, then Firestore sync.
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        ticket_id = f"DST-{timestamp}"
        pin_code = self.generate_pin_code()
        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"DEBUG[TicketRepository]: generating ticket {ticket_id}")

        # 1. local first
        result = self.memory_store.generate_ticket(
            parking_slot=parking_slot,
            vehicle_type=vehicle_type,
            ticket_id=ticket_id,
            pin_code=pin_code,
            entry_time=entry_time,
            is_synced=False,
        )

        # 2. try Firestore sync
        try:
            ticket = self.memory_store.get_ticket_by_id(ticket_id)
            if ticket is not None:
                doc_ref = self.collection.document(ticket_id)
                doc_ref.set(ticket.to_dict())
                self.memory_store.mark_ticket_synced(ticket_id)
                print(f"DEBUG[TicketRepository]: Firestore sync success for ticket {ticket_id}")

        except Exception as e:
            print(f"DEBUG[TicketRepository]: Firestore ticket sync failed for {ticket_id}: {e}")

        return result

    def get_ticket_by_id(self, ticket_id: str):
        """
        CSV first, Firestore second.
        """
        local_ticket = self.memory_store.get_ticket_by_id(ticket_id)
        if local_ticket is not None:
            return local_ticket

        try:
            doc = self.collection.document(ticket_id).get()
            if doc.exists:
                ticket = self._doc_to_ticket(doc)
                self.memory_store.upsert_ticket(ticket, is_synced=True)
                return ticket
            return None

        except Exception as e:
            print(f"DEBUG[TicketRepository]: Firestore get_ticket_by_id failed for {ticket_id}: {e}")
            return None

    def update_ticket_on_exit(
        self,
        ticket_id: str,
        exit_time: datetime,
        duration_minutes: float,
        price: float,
    ) -> bool:
        """
        CSV first, then Firestore sync.
        """
        exit_time_str = exit_time.strftime("%Y-%m-%d %H:%M:%S")

        local_success = self.memory_store.update_ticket_on_exit(
            ticket_id=ticket_id,
            exit_time=exit_time_str,
            duration_minutes=duration_minutes,
            price=price,
            is_synced=False,
        )

        if not local_success:
            print(f"DEBUG[TicketRepository]: local exit update failed for ticket {ticket_id}")
            return False

        print(f"DEBUG[TicketRepository]: locally updated exit for ticket {ticket_id}, trying Firestore sync")

        try:
            ticket = self.memory_store.get_ticket_by_id(ticket_id)
            if ticket is not None:
                doc_ref = self.collection.document(ticket_id)
                doc_ref.set(ticket.to_dict(), merge=True)
                self.memory_store.mark_ticket_synced(ticket_id)
                print(f"DEBUG[TicketRepository]: Firestore exit sync success for ticket {ticket_id}")

        except Exception as e:
            print(f"DEBUG[TicketRepository]: Firestore exit sync failed for ticket {ticket_id}: {e}")

        return True

    def get_all_tickets(self):
        """
        CSV first if already populated.
        Firestore only used for bootstrap.
        """
        local_tickets = self.memory_store.get_all_tickets()
        if len(local_tickets) > 0:
            print(f"DEBUG[TicketRepository]: returning {len(local_tickets)} tickets from CSV")
            return local_tickets

        print("DEBUG[TicketRepository]: CSV empty, trying Firestore bootstrap for tickets")
        try:
            docs = self.collection.order_by("entry_time", direction="DESCENDING").stream()
            tickets = [self._doc_to_ticket(doc) for doc in docs]

            if len(tickets) > 0:
                self.memory_store.seed_from_tickets(tickets)
                print(f"DEBUG[TicketRepository]: bootstrapped {len(tickets)} tickets from Firestore")
                return tickets

            print("DEBUG[TicketRepository]: Firestore returned no ticket documents")
            return []

        except Exception as e:
            print(f"DEBUG[TicketRepository]: Firestore bootstrap failed: {e}")
            return []

    def sync_unsynced_tickets_to_firestore(self) -> int:
        synced_count = 0
        unsynced_tickets = self.memory_store.get_unsynced_tickets()

        if len(unsynced_tickets) > 0:
            print(f"DEBUG[TicketRepository]: found {len(unsynced_tickets)} unsynced tickets")

        for ticket in unsynced_tickets:
            try:
                doc_ref = self.collection.document(ticket.get_ticket_id())
                doc_ref.set(ticket.to_dict(), merge=True)
                self.memory_store.mark_ticket_synced(ticket.get_ticket_id())
                synced_count += 1
                print(f"DEBUG[TicketRepository]: synced ticket {ticket.get_ticket_id()} to Firestore")
            except Exception as e:
                print(f"DEBUG[TicketRepository]: failed syncing ticket {ticket.get_ticket_id()}: {e}")

        return synced_count

    def bootstrap_from_firestore(self) -> int:
        """
        Optional manual bootstrap helper.
        """
        try:
            docs = self.collection.order_by("entry_time", direction="DESCENDING").stream()
            tickets = [self._doc_to_ticket(doc) for doc in docs]

            if len(tickets) > 0:
                self.memory_store.seed_from_tickets(tickets)
                return len(tickets)

            return 0

        except Exception as e:
            print(f"DEBUG[TicketRepository]: bootstrap_from_firestore failed: {e}")
            return 0

