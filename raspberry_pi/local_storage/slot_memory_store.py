import csv
import os
from typing import Optional, List

from raspberry_pi.data_models.parking_slot import ParkingSlot
from raspberry_pi.data_models.vehicle_type import VehicleType


class SlotMemoryStore:
    def __init__(self, csv_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_storage_dir = os.path.join(base_dir, "local_storage")

        os.makedirs(local_storage_dir, exist_ok=True)

        self.csv_path = csv_path or os.path.join(local_storage_dir, "slots_memory.csv")
        self.fieldnames = [
            "slot_id",
            "slot_type",
            "slot_length",
            "slot_width",
            "is_occupied"
        ]

        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()

    def _row_to_slot(self, row: dict) -> ParkingSlot:
        is_occupied_raw = str(row["is_occupied"]).strip().lower()
        is_occupied = is_occupied_raw in ("true", "1", "yes")

        return ParkingSlot(
            slot_id=int(row["slot_id"]),
            slot_type=VehicleType(row["slot_type"]),
            slot_length=float(row["slot_length"]),
            slot_width=float(row["slot_width"]),
            is_occupied=is_occupied
        )

    def _slot_to_row(self, slot: ParkingSlot) -> dict:
        return {
            "slot_id": str(slot.get_slot_id()),
            "slot_type": slot.get_slot_type().value,
            "slot_length": str(slot.get_slot_length()),
            "slot_width": str(slot.get_slot_width()),
            "is_occupied": str(slot.get_slot_status())
        }

    def get_all_slots(self) -> List[ParkingSlot]:
        self._ensure_file_exists()

        slots = []
        with open(self.csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                slots.append(self._row_to_slot(row))

        return slots

    def overwrite_all_slots(self, slots: List[ParkingSlot]) -> None:
        self._ensure_file_exists()

        with open(self.csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            for slot in slots:
                writer.writerow(self._slot_to_row(slot))

    def get_slot_by_id(self, slot_id: int) -> Optional[ParkingSlot]:
        slots = self.get_all_slots()
        for slot in slots:
            if slot.get_slot_id() == slot_id:
                return slot
        return None

    def find_available_slot(self, vehicle_type: VehicleType) -> Optional[ParkingSlot]:
        slots = self.get_all_slots()

        for slot in slots:
            if (
                slot.get_slot_type() == vehicle_type
                and not slot.get_slot_status()
            ):
                return slot

        return None

    def upsert_slot(self, slot: ParkingSlot) -> None:
        slots = self.get_all_slots()
        updated = False

        for index, existing_slot in enumerate(slots):
            if existing_slot.get_slot_id() == slot.get_slot_id():
                slots[index] = slot
                updated = True
                break

        if not updated:
            slots.append(slot)

        self.overwrite_all_slots(slots)

    def reserve_slot(self, slot_id: int) -> bool:
        slots = self.get_all_slots()

        for slot in slots:
            if slot.get_slot_id() == slot_id:
                if slot.get_slot_status():
                    return False

                slot.set_slot_status(True)
                self.overwrite_all_slots(slots)
                return True

        return False

    def release_slot(self, slot_id: int) -> bool:
        slots = self.get_all_slots()

        for slot in slots:
            if slot.get_slot_id() == slot_id:
                if not slot.get_slot_status():
                    return False

                slot.set_slot_status(False)
                self.overwrite_all_slots(slots)
                return True

        return False

    def seed_from_slots(self, slots: List[ParkingSlot]) -> None:
        self.overwrite_all_slots(slots)