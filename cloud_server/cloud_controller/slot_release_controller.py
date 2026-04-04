from cloud_server.repositories.slot_repository import SlotRepository


class SlotReleaseController:
    def __init__(self):
        self.slot_repository = SlotRepository()

    def process_slot_release(self, distance: float):
        # Step 1: Find slot based on distance range
        slot = self.slot_repository.find_slot_by_distance(distance)

        if not slot:
            return {
                "status": "failed",
                "message": "No matching slot found for given distance",
                "slot_id": None
            }

        slot_doc_id = slot["id"]
        slot_id = slot.get("slot_id", slot_doc_id)

        # Step 2: Release slot in Firestore
        self.slot_repository.release_slot(slot_doc_id)

        return {
            "status": "success",
            "message": f"Slot {slot_id} released successfully",
            "slot_id": slot_id
        }