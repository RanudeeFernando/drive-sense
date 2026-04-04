from cloud_server.cloud.firestore_database import FirestoreDatabase


class SlotRepository:
    def __init__(self):
        self.db = FirestoreDatabase().get_client()
        self.collection = self.db.collection("slots")

    def get_all_slots(self):
        docs = self.collection.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    def get_available_slot_by_type(self, vehicle_type):
        docs = (
            self.collection
            .where("slot_type", "==", vehicle_type)
            .where("occupied", "==", False)
            .stream()
        )
        slots = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        return slots[0] if slots else None

    def reserve_slot(self, slot_id):
        self.collection.document(slot_id).update({
            "occupied": True,
            "status": "occupied"
        })

    def release_slot(self, slot_id):
        self.collection.document(slot_id).update({
            "occupied": False,
            "status": "available"
        })

    def find_slot_by_distance(self, distance):
        docs = self.collection.stream()
        for doc in docs:
            data = doc.to_dict()
            start = data.get("distance_start")
            end = data.get("distance_end")
            if start is not None and end is not None and start <= distance <= end:
                return {"id": doc.id, **data}
        return None