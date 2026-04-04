# cloud_server/services/slot_manager_service.py
from cloud_server.data_models.vehicle_type import VehicleType

class SlotManagerService:
    def __init__(self, slot_repository):
        self.slot_repository = slot_repository

    def find_available_slot(self, vehicle_type: VehicleType):
        return self.slot_repository.find_available_slot(vehicle_type)

    def reserve_slot(self, slot_id: int) -> bool:
        return self.slot_repository.reserve_slot(slot_id)

    def release_slot_by_id(self, slot_id: int) -> bool:
        return self.slot_repository.release_slot(slot_id)

    def release_slot_by_distance(self, distance: float):
        print(f"Received exit distance: {distance} cm")

        slot = self.slot_repository.get_slot_from_distance(distance)

        if slot is None:
            print("Distance mapped to no known slot!")
            return {
                "status": "failed",
                "message": "Invalid distance mapping"
            }

        success = self.slot_repository.release_slot(slot.get_slot_id())

        if not success:
            return {
                "status": "failed",
                "message": "Slot could not be released"
            }

        return {
            "status": "success",
            "slot_id": slot.get_slot_id(),
            "slot_type": slot.get_slot_type().value,
            "message": "Slot released successfully"
        }

    def is_slot_released(self, slot_id: int) -> bool:
        slot = self.slot_repository.get_slot_by_id(slot_id)

        if slot is None:
            return False

        return not slot.get_slot_status()