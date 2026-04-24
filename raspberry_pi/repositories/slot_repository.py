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
        """
        Converts a Firestore document into a ParkingSlot object.
        Maps database fields to the domain model.
        """
        data = doc.to_dict()
        return ParkingSlot(
            slot_id=int(data["slot_id"]),
            slot_type=VehicleType(data["slot_type"]),
            is_occupied=bool(data["is_occupied"])
        )

    def find_available_slot(self, vehicle_type: VehicleType):
        """
        CSV first for runtime operation.
        If local CSV has a free slot, use it immediately.
        Firestore is only used for sync/bootstrap, not as the first dependency.
        """
        local_slot = self.memory_store.find_available_slot(vehicle_type)
        if local_slot is not None:
            print(f"DEBUG[SlotRepository]: found available slot {local_slot.get_slot_id()} in CSV")
            return local_slot

        print("DEBUG[SlotRepository]: no available slot in CSV, trying Firestore")
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

            if found_slot is not None:
                self.memory_store.upsert_slot(found_slot, is_synced=True)
                print(f"DEBUG[SlotRepository]: recovered available slot {found_slot.get_slot_id()} from Firestore")

            return found_slot

        except Exception as e:
            print(f"DEBUG[SlotRepository]: Firestore find_available_slot failed: {e}")
            return None

    def get_slot_by_id(self, slot_id: int):
        """
        Retrieves a parking slot by ID.
        Checks local CSV first, then Firestore if not found locally.
        """
        local_slot = self.memory_store.get_slot_by_id(slot_id)
        if local_slot is not None:
            return local_slot

        try:
            doc = self.collection.document(str(slot_id)).get()
            if doc.exists:
                slot = self._doc_to_slot(doc)
                self.memory_store.upsert_slot(slot, is_synced=True)
                return slot
            return None

        except Exception as e:
            print(f"DEBUG[SlotRepository]: Firestore get_slot_by_id failed for {slot_id}: {e}")
            return None

    def reserve_slot(self, slot_id: int) -> bool:
        """
        Marks a slot as occupied.
        Updates local CSV first and then syncs the change to Firestore.
        """
        local_success = self.memory_store.reserve_slot(slot_id, is_synced=False)
        if not local_success:
            print(f"DEBUG[SlotRepository]: local reserve failed for slot {slot_id}")
            return False

        print(f"DEBUG[SlotRepository]: locally reserved slot {slot_id}, trying Firestore sync")

        try:
            doc_ref = self.collection.document(str(slot_id))
            doc = doc_ref.get()

            if doc.exists:
                doc_ref.update({"is_occupied": True})
            else:
                slot = self.memory_store.get_slot_by_id(slot_id)
                if slot is not None:
                    doc_ref.set(slot.to_dict(), merge=True)

            self.memory_store.mark_slot_synced(slot_id)
            print(f"DEBUG[SlotRepository]: Firestore sync success for reserved slot {slot_id}")

        except Exception as e:
            print(f"DEBUG[SlotRepository]: Firestore reserve sync failed for slot {slot_id}: {e}")

        return True

    def release_slot(self, slot_id: int) -> bool:
        """
        Marks a slot as free.
        Updates local CSV first and then syncs the change to Firestore.
        """
        local_success = self.memory_store.release_slot(slot_id, is_synced=False)
        if not local_success:
            print(f"DEBUG[SlotRepository]: local release failed for slot {slot_id}")
            return False

        print(f"DEBUG[SlotRepository]: locally released slot {slot_id}, trying Firestore sync")

        try:
            doc_ref = self.collection.document(str(slot_id))
            doc = doc_ref.get()

            if doc.exists:
                doc_ref.update({"is_occupied": False})
            else:
                slot = self.memory_store.get_slot_by_id(slot_id)
                if slot is not None:
                    doc_ref.set(slot.to_dict(), merge=True)

            self.memory_store.mark_slot_synced(slot_id)
            print(f"DEBUG[SlotRepository]: Firestore sync success for released slot {slot_id}")

        except Exception as e:
            print(f"DEBUG[SlotRepository]: Firestore release sync failed for slot {slot_id}: {e}")

        return True

    def get_all_slots(self):
        """
        Retrieves all parking slots.
        Uses local CSV if available, otherwise bootstraps from Firestore.
        """
        local_slots = self.memory_store.get_all_slots()
        if len(local_slots) > 0:
            print(f"DEBUG[SlotRepository]: returning {len(local_slots)} slots from CSV")
            return local_slots

        print("DEBUG[SlotRepository]: CSV empty, trying Firestore bootstrap for slots")
        try:
            docs = self.collection.stream()
            slots = [self._doc_to_slot(doc) for doc in docs]

            if len(slots) > 0:
                self.memory_store.seed_from_slots(slots)
                print(f"DEBUG[SlotRepository]: bootstrapped {len(slots)} slots from Firestore")
                return slots

            print("DEBUG[SlotRepository]: Firestore returned no slot documents")
            return []

        except Exception as e:
            print(f"DEBUG[SlotRepository]: Firestore bootstrap failed: {e}")
            return []

    def sync_unsynced_slots_to_firestore(self) -> int:
        """
        Syncs all locally modified (unsynced) slots to Firestore.
        Returns the number of successfully synced slots.
        """
        synced_count = 0
        unsynced_slots = self.memory_store.get_unsynced_slots()

        if len(unsynced_slots) > 0:
            print(f"DEBUG[SlotRepository]: found {len(unsynced_slots)} unsynced slots")

        for slot in unsynced_slots:
            try:
                doc_ref = self.collection.document(str(slot.get_slot_id()))
                doc_ref.set(slot.to_dict(), merge=True)
                self.memory_store.mark_slot_synced(slot.get_slot_id())
                synced_count += 1
                print(f"DEBUG[SlotRepository]: synced slot {slot.get_slot_id()} to Firestore")
            except Exception as e:
                print(f"DEBUG[SlotRepository]: failed syncing slot {slot.get_slot_id()}: {e}")

        return synced_count

    def bootstrap_from_firestore(self) -> int:
        """
        Loads all slots from Firestore into local CSV storage.
        Used for initial setup or recovery.
        """
        try:
            docs = self.collection.stream()
            slots = [self._doc_to_slot(doc) for doc in docs]

            if len(slots) > 0:
                self.memory_store.seed_from_slots(slots)
                return len(slots)

            return 0

        except Exception as e:
            print(f"DEBUG[SlotRepository]: bootstrap_from_firestore failed: {e}")
            return 0
