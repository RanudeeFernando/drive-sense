
from cloud_server.cloud_db.firestore_client import get_db
from raspberry_pi.data_models.parking_slot import ParkingSlot
from raspberry_pi.data_models.vehicle_type import VehicleType

class SlotRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("slots")

    @staticmethod
    def _doc_to_slot(doc) -> ParkingSlot:
        data = doc.to_dict()
        return ParkingSlot(
            slot_id=int(data["slot_id"]),
            slot_type=VehicleType(data["slot_type"]),
            slot_length=float(data["slot_length"]),
            slot_width=float(data["slot_width"]),
            is_occupied=bool(data["is_occupied"])
        )



    def get_slot_by_id(self, slot_id: int):
        """Return a ParkingSlot by slot_id."""
        doc = self.collection.document(str(slot_id)).get()
        if doc.exists:
            return self._doc_to_slot(doc)
        return None



    def get_all_slots(self):
        """Return all ParkingSlots from Firestore."""
        docs = self.collection.stream()
        return [self._doc_to_slot(doc) for doc in docs]