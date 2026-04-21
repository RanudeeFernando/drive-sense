from raspberry_pi.cloud_db.firestore_client import get_db
from raspberry_pi.data_models.parking_slot import ParkingSlot
from raspberry_pi.data_models.vehicle_type import VehicleType
from raspberry_pi.local_storage.slot_memory_store import SlotMemoryStore


class SlotRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("slots")
        self.memory_store = SlotMemoryStore()

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

    def find_available_slot(self, vehicle_type: VehicleType):
        """
        Firestore first.
        If Firestore fails, fall back to local CSV memory.
        """
        try:
            docs = (
                self.collection
                .where("slot_type", "==", vehicle_type.value)
                .where("is_occupied", "==", False)
                .limit(1)
                .stream()
            )

            found_slot = None
            for doc in docs:
                found_slot = self._doc_to_slot(doc)
                break

            # Only sync from Firestore if Firestore actually has slot data
            self._sync_slots_from_firestore()

            if found_slot is not None:
                return found_slot

            # If Firestore returned no matching slot, fall back to current CSV content
            return self.memory_store.find_available_slot(vehicle_type)

        except Exception:
            return self.memory_store.find_available_slot(vehicle_type)

    def get_slot_by_id(self, slot_id: int):
        """
        Firestore first.
        If Firestore fails, fall back to local CSV memory.
        """
        try:
            doc = self.collection.document(str(slot_id)).get()
            if doc.exists:
                slot = self._doc_to_slot(doc)
                self.memory_store.upsert_slot(slot)
                return slot

            
            return self.memory_store.get_slot_by_id(slot_id)

        except Exception:
            return self.memory_store.get_slot_by_id(slot_id)

    def reserve_slot(self, slot_id: int) -> bool:
        """
        Try Firestore first.
        Always keep local CSV updated.
        If Firestore fails, fall back to local CSV memory.
        """
        try:
            doc_ref = self.collection.document(str(slot_id))
            doc = doc_ref.get()

            if not doc.exists:
                return self.memory_store.reserve_slot(slot_id)

            data = doc.to_dict()
            if data.get("is_occupied", False):
                return False

            doc_ref.update({"is_occupied": True})

            slot = self.get_slot_by_id(slot_id)
            if slot is not None:
                slot.set_slot_status(True)
                self.memory_store.upsert_slot(slot)

            return True

        except Exception:
            return self.memory_store.reserve_slot(slot_id)

    def release_slot(self, slot_id: int) -> bool:
        """
        Try Firestore first.
        Always keep local CSV updated.
        If Firestore fails, fall back to local CSV memory.
        """
        try:
            doc_ref = self.collection.document(str(slot_id))
            doc = doc_ref.get()

            if not doc.exists:
                return self.memory_store.release_slot(slot_id)

            data = doc.to_dict()
            if not data.get("is_occupied", False):
                return False

            doc_ref.update({"is_occupied": False})

            slot = self.get_slot_by_id(slot_id)
            if slot is not None:
                slot.set_slot_status(False)
                self.memory_store.upsert_slot(slot)

            return True

        except Exception:
            return self.memory_store.release_slot(slot_id)

    def get_all_slots(self):
        """
        Firestore first.
        If Firestore fails, fall back to local CSV memory.

        IMPORTANT:
        Do not overwrite CSV with an empty Firestore result.
        """
        try:
            docs = self.collection.stream()
            slots = [self._doc_to_slot(doc) for doc in docs]

            
            if len(slots) > 0:
                self.memory_store.seed_from_slots(slots)
                return slots

            
            existing_csv_slots = self.memory_store.get_all_slots()
            if len(existing_csv_slots) > 0:
                return existing_csv_slots

        
            return []

        except Exception:
            return self.memory_store.get_all_slots()

    def _sync_slots_from_firestore(self) -> None:
        """
        Best-effort sync of all Firestore slots into local CSV memory.
        Do not wipe CSV if Firestore returns zero rows.
        """
        try:
            docs = self.collection.stream()
            slots = [self._doc_to_slot(doc) for doc in docs]

            if len(slots) > 0:
                self.memory_store.seed_from_slots(slots)

        except Exception:
            pass