class SlotAllocator:
    def __init__(self, slots):
        self.slots = slots

    def allocate_slot(self, vehicle_type):
        for slot in self.slots:
            if not slot.slot_status and slot.slot_type == vehicle_type:
                return slot
        return None