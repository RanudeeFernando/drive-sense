
from datetime import datetime
import random

from cloud_server.cloud_db.firestore_client import get_db
from cloud_server.data_models.ticket import Ticket
from cloud_server.data_models.parking_slot import ParkingSlot
from cloud_server.data_models.vehicle_type import VehicleType
# from cloud_server.repositories.slot_repository import SlotRepository


# class TicketRepository:
#     def __init__(self):
#         self.db = get_db()
#         self.collection = self.db.collection("tickets")
#         self.slot_repository = SlotRepository()

    # @staticmethod
    # def _build_fallback_slot(slot_id: int, vehicle_type: VehicleType) -> ParkingSlot:
    #     return ParkingSlot(
    #         slot_id=slot_id,
    #         slot_type=vehicle_type,
    #         slot_length=0.0,
    #         slot_width=0.0,
    #         is_occupied=False
    #     )

    # def generate_pin_code(self) -> str:
    #     while True:
    #         pin = f"{random.randint(0, 9999):04d}"
    #         existing_ticket = self.get_active_ticket_by_pin(pin)
    #         if existing_ticket is None:
    #             return pin

    # def _doc_to_ticket(self, doc) -> Ticket:
    #     data = doc.to_dict()
    #
    #     slot_id = int(data["slot_id"])
    #     vehicle_type = VehicleType(data["vehicle_type"])
    #
    #     parking_slot = self.slot_repository.get_slot_by_id(slot_id)
    #
    #     if parking_slot is None:
    #         parking_slot = self._build_fallback_slot(slot_id, vehicle_type)
    #
    #     return Ticket(
    #         ticket_id=data["ticket_id"],
    #         parking_slot=parking_slot,
    #         vehicle_type=vehicle_type,
    #         entry_time=data["entry_time"],
    #         exit_time=data.get("exit_time", ""),
    #         duration_minutes=float(data.get("duration_minutes", 0)),
    #         price=float(data.get("price", 0)),
    #         status=data.get("status", "active"),
    #         pin_code=data.get("pin_code", ""),
    #         pin_status=data.get("pin_status", "active")
    #     )

    # def generate_ticket(self, parking_slot: ParkingSlot, vehicle_type: VehicleType) -> dict:
    #     timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    #     ticket_id = f"DST-{timestamp}"
    #     doc_ref = self.collection.document(ticket_id)
    #
    #     pin_code = self.generate_pin_code()
    #     entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #
    #     ticket = Ticket(
    #         ticket_id=ticket_id,
    #         parking_slot=parking_slot,
    #         vehicle_type=vehicle_type,
    #         entry_time=entry_time,
    #         exit_time="",
    #         duration_minutes=0,
    #         price=0,
    #         status="active",
    #         pin_code=pin_code,
    #         pin_status="active"
    #     )
    #
    #     doc_ref.set(ticket.to_dict())
    #
    #     return {
    #         "ticket_id": ticket_id,
    #         "pin_code": pin_code,
    #         "entry_time": entry_time,
    #         "slot_id": parking_slot.get_slot_id(),
    #         "vehicle_type": vehicle_type.value
    #     }

    # def get_ticket_by_id(self, ticket_id: str):
    #     doc = self.collection.document(ticket_id).get()
    #     if doc.exists:
    #         return self._doc_to_ticket(doc)
    #     return None

    # def get_active_ticket_by_slot_id(self, slot_id: int):
    #     docs = (
    #         self.collection
    #         .where("slot_id", "==", slot_id)
    #         .where("status", "==", "active")
    #         .limit(1)
    #         .stream()
    #     )
    #
    #     for doc in docs:
    #         return self._doc_to_ticket(doc)
    #     return None

    # def get_active_ticket_by_pin(self, pin_code: str):
    #     docs = (
    #         self.collection
    #         .where("pin_code", "==", pin_code)
    #         .where("status", "==", "active")
    #         .limit(1)
    #         .stream()
    #     )
    #
    #     for doc in docs:
    #         return self._doc_to_ticket(doc)
    #     return None

    # def update_ticket_on_exit(
    #     self,
    #     ticket_id: str,
    #     exit_time: datetime,
    #     duration_minutes: float,
    #     price: float
    # ) -> bool:
    #     doc_ref = self.collection.document(ticket_id)
    #     doc = doc_ref.get()
    #
    #     if not doc.exists:
    #         return False
    #
    #     doc_ref.update({
    #         "exit_time": exit_time.strftime("%Y-%m-%d %H:%M:%S"),
    #         "duration_minutes": round(duration_minutes, 2),
    #         "price": price,
    #         "status": "closed",
    #         "pin_status": "expired"
    #     })
    #     return True

    # def get_all_tickets(self):
    #     docs = self.collection.order_by("entry_time", direction="DESCENDING").stream()
    #     return [self._doc_to_ticket(doc) for doc in docs]