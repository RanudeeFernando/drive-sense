# cloud_server/cloud_controller/slot_release_controller.py
import csv

class SlotReleaseController:
    def __init__(self, slot):
        self.slot = slot

    def get_slot_from_distance(self, distance: float):
        with open("cloud_server/data/slots.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                start = float(row["distance_start"])
                end = float(row["distance_end"])
                if start <= distance <= end:
                    return int(row["slot_id"])
        return None

    def process_slot_release(self, distance: float):
        print(f"📡 Received exit distance: {distance} cm")
        slot_id = self.get_slot_from_distance(distance)
        
        if slot_id is not None:
            # release the slot
            success = self.slot.release_slot(slot_id)
            if success:
                return {"status": "success", "slot_id": slot_id, "message": "Slot released successfully"}
            else:
                return {"status": "failed", "message": "Slot could not be released"}
        else:
            print("❌ Distance mapped to no known slot!")
            return {"status": "failed", "message": "Invalid distance mapping"}
