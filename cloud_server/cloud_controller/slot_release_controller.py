# cloud_server/cloud_controller/slot_release_controller.py
from cloud_server.cloud.firestore_client import get_db


class SlotReleaseController:
    def __init__(self, slot):
        self.slot = slot

    def get_slot_from_distance(self, distance: float):
        """Find which slot ID corresponds to the measured exit distance."""
        db = get_db()
        # Firestore can only filter on one inequality per query,
        # so we filter by distance_start and check distance_end in Python
        slots = (
            db.collection("slots")
            .where("distance_start", "<=", distance)
            .stream()
        )
        for doc in slots:
            data = doc.to_dict()
            if data["distance_start"] <= distance <= data["distance_end"]:
                return int(data["slot_id"])
        return None

    def process_slot_release(self, distance: float):
        print(f"Received exit distance: {distance} cm")
        slot_id = self.get_slot_from_distance(distance)

        if slot_id is not None:
            success = self.slot.release_slot(slot_id)
            if success:
                return {"status": "success", "slot_id": slot_id, "message": "Slot released successfully"}
            else:
                return {"status": "failed", "message": "Slot could not be released"}
        else:
            print("Distance mapped to no known slot!")
            return {"status": "failed", "message": "Invalid distance mapping"}
