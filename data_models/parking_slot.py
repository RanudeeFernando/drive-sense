from dataclasses import dataclass


@dataclass
class ParkingSlot:
    slot_id: int
    slot_type: str
    slot_length: float
    slot_width: float
    slot_status: bool = False

    def get_slot_id(self):
        return self.slot_id

    def set_slot_id(self, slot_id):
        self.slot_id = slot_id

    def get_slot_type(self):
        return self.slot_type

    def set_slot_type(self, slot_type):
        self.slot_type = slot_type

    def get_slot_length(self):
        return self.slot_length

    def set_slot_length(self, slot_length):
        self.slot_length = slot_length

    def get_slot_width(self):
        return self.slot_width

    def set_slot_width(self, slot_width):
        self.slot_width = slot_width

    def get_slot_status(self):
        return self.slot_status

    def set_slot_status(self, slot_status):
        self.slot_status = slot_status

    def allocate_slot(self):
        if not self.slot_status:
            self.slot_status = True
            return True
        return False

    def release_slot(self):
        if self.slot_status:
            self.slot_status = False
            return True
        return False