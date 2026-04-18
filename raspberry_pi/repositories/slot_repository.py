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
            is_occupied=bool(data["is_occupied"]),
        )

    def find_available_slot(self, vehicle_type: VehicleType):
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

            self._sync_slots_from_firestore()
            return found_slot

        except Exception:
            return self.memory_store.find_available_slot(vehicle_type)

    def get_slot_by_id(self, slot_id: int):
        try:
            doc = self.collection.document(str(slot_id)).get()
            if doc.exists:
                slot = self._doc_to_slot(doc)
                self.memory_store.upsert_slot(slot, is_synced=True)
                return slot
            return None

        except Exception:
            return self.memory_store.get_slot_by_id(slot_id)

    def reserve_slot(self, slot_id: int) -> bool:
        try:
            doc_ref = self.collection.document(str(slot_id))
            doc = doc_ref.get()

            if not doc.exists:
                return False

            data = doc.to_dict()
            if data.get("is_occupied", False):
                return False

            doc_ref.update({"is_occupied": True})

            slot = self.get_slot_by_id(slot_id)
            if slot is not None:
                slot.set_slot_status(True)
                self.memory_store.upsert_slot(slot, is_synced=True)

            return True

        except Exception:
            return self.memory_store.reserve_slot(slot_id, is_synced=False)

    def release_slot(self, slot_id: int) -> bool:
        try:
            doc_ref = self.collection.document(str(slot_id))
            doc = doc_ref.get()

            if not doc.exists:
                return False

            data = doc.to_dict()
            if not data.get("is_occupied", False):
                return False

            doc_ref.update({"is_occupied": False})

            slot = self.get_slot_by_id(slot_id)
            if slot is not None:
                slot.set_slot_status(False)
                self.memory_store.upsert_slot(slot, is_synced=True)

            return True

        except Exception:
            return self.memory_store.release_slot(slot_id, is_synced=False)

    def get_all_slots(self):
        try:
            docs = self.collection.stream()
            slots = [self._doc_to_slot(doc) for doc in docs]
            self.memory_store.seed_from_slots(slots)
            return slots

        except Exception:
            return self.memory_store.get_all_slots()

    def sync_unsynced_slots_to_firestore(self) -> int:
        synced_count = 0
        unsynced_slots = self.memory_store.get_unsynced_slots()

        for slot in unsynced_slots:
            doc_ref = self.collection.document(str(slot.get_slot_id()))
            doc_ref.set(slot.to_dict(), merge=True)
            self.memory_store.mark_slot_synced(slot.get_slot_id())
            synced_count += 1

        return synced_count

    def _sync_slots_from_firestore(self) -> None:
        try:
            docs = self.collection.stream()
            slots = [self._doc_to_slot(doc) for doc in docs]
            self.memory_store.seed_from_slots(slots)
        except Exception:
            pass