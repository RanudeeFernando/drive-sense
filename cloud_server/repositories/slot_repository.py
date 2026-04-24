# cloud_server/repositories/slot_repository.py
from cloud_server.cloud_db.firestore_client import get_db
from cloud_server.data_models.parking_slot import ParkingSlot
from cloud_server.data_models.vehicle_type import VehicleType

# class SlotRepository:
#     def __init__(self):
#         self.db = get_db()
#         self.collection = self.db.collection("slots")

    # @staticmethod
    # def _doc_to_slot(doc) -> ParkingSlot:
    #     data = doc.to_dict()
    #     return ParkingSlot(
    #         slot_id=int(data["slot_id"]),
    #         slot_type=VehicleType(data["slot_type"]),
    #         slot_length=float(data["slot_length"]),
    #         slot_width=float(data["slot_width"]),
    #         is_occupied=bool(data["is_occupied"])
    #     )

    # def find_available_slot(self, vehicle_type: VehicleType):
    #     """Return the first available ParkingSlot matching the given vehicle type."""
    #     docs = (
    #         self.collection
    #         .where("slot_type", "==", vehicle_type.value)
    #         .where("is_occupied", "==", False)
    #         .limit(1)
    #         .stream()
    #     )
    #
    #     for doc in docs:
    #         return self._doc_to_slot(doc)
    #     return None

    # def get_slot_by_id(self, slot_id: int):
    #     """Return a ParkingSlot by slot_id."""
    #     doc = self.collection.document(str(slot_id)).get()
    #     if doc.exists:
    #         return self._doc_to_slot(doc)
    #     return None
    #
    # def reserve_slot(self, slot_id: int) -> bool:
    #     doc_ref = self.collection.document(str(slot_id))
    #     doc = doc_ref.get()
    #
    #     if not doc.exists:
    #         return False
    #
    #     doc_ref.update({"is_occupied": True})
    #     return True
    #
    # def release_slot(self, slot_id: int) -> bool:
    #     doc_ref = self.collection.document(str(slot_id))
    #     doc = doc_ref.get()
    #
    #     data = doc.to_dict()
    #     if not data.get("is_occupied", False):
    #         return False
    #
    #     doc_ref.update({"is_occupied": False})
    #     return True

    # def get_slot_from_distance(self, distance: float):
    #     """
    #     Return the ParkingSlot that matches the measured distance.
    #     """
    #     docs = (
    #         self.collection
    #         .where("distance_start", "<=", distance)
    #         .stream()
    #     )
    #
    #     for doc in docs:
    #         data = doc.to_dict()
    #         if data["distance_start"] <= distance <= data["distance_end"]:
    #             return self._doc_to_slot(doc)
    #
    #     return None

    # def get_all_slots(self):
    #     docs = self.collection.stream()
    #     return [self._doc_to_slot(doc) for doc in docs]