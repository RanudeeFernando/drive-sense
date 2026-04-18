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
            "is_occupied",
            "is_synced",
        ]

        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()
            return

        # Upgrade old CSV files that do not yet have is_synced
        with open(self.csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            existing_fields = reader.fieldnames or []

        if "is_synced" not in existing_fields:
            rows = []
            with open(self.csv_path, "r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row["is_synced"] = "True"
                    rows.append(row)

            with open(self.csv_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)

    @staticmethod
    def _to_bool(value) -> bool:
        return str(value).strip().lower() in ("true", "1", "yes")

    def _row_to_slot(self, row: dict) -> ParkingSlot:
        return ParkingSlot(
            slot_id=int(row["slot_id"]),
            slot_type=VehicleType(row["slot_type"]),
            slot_length=float(row["slot_length"]),
            slot_width=float(row["slot_width"]),
            is_occupied=self._to_bool(row["is_occupied"]),
        )

    def _slot_to_row(self, slot: ParkingSlot, is_synced: bool = True) -> dict:
        return {
            "slot_id": str(slot.get_slot_id()),
            "slot_type": slot.get_slot_type().value,
            "slot_length": str(slot.get_slot_length()),
            "slot_width": str(slot.get_slot_width()),
            "is_occupied": str(slot.get_slot_status()),
            "is_synced": str(is_synced),
        }

    def get_all_slots(self) -> List[ParkingSlot]:
        self._ensure_file_exists()

        slots = []
        with open(self.csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                slots.append(self._row_to_slot(row))

        return slots

    def get_all_rows(self) -> List[dict]:
        self._ensure_file_exists()

        rows = []
        with open(self.csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if "is_synced" not in row:
                    row["is_synced"] = "True"
                rows.append(row)

        return rows

    def overwrite_all_rows(self, rows: List[dict]) -> None:
        self._ensure_file_exists()

        normalized_rows = []
        for row in rows:
            normalized = {
                "slot_id": str(row["slot_id"]),
                "slot_type": str(row["slot_type"]),
                "slot_length": str(row["slot_length"]),
                "slot_width": str(row["slot_width"]),
                "is_occupied": str(row["is_occupied"]),
                "is_synced": str(row.get("is_synced", True)),
            }
            normalized_rows.append(normalized)

        with open(self.csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            for row in normalized_rows:
                writer.writerow(row)

    def overwrite_all_slots(self, slots: List[ParkingSlot], is_synced: bool = True) -> None:
        rows = [self._slot_to_row(slot, is_synced=is_synced) for slot in slots]
        self.overwrite_all_rows(rows)

    def get_slot_by_id(self, slot_id: int) -> Optional[ParkingSlot]:
        rows = self.get_all_rows()
        for row in rows:
            if int(row["slot_id"]) == slot_id:
                return self._row_to_slot(row)
        return None

    def find_available_slot(self, vehicle_type: VehicleType) -> Optional[ParkingSlot]:
        rows = self.get_all_rows()

        for row in rows:
            slot = self._row_to_slot(row)
            if slot.get_slot_type() == vehicle_type and not slot.get_slot_status():
                return slot

        return None

    def upsert_slot(self, slot: ParkingSlot, is_synced: bool = True) -> None:
        rows = self.get_all_rows()
        updated = False

        for index, row in enumerate(rows):
            if int(row["slot_id"]) == slot.get_slot_id():
                rows[index] = self._slot_to_row(slot, is_synced=is_synced)
                updated = True
                break

        if not updated:
            rows.append(self._slot_to_row(slot, is_synced=is_synced))

        self.overwrite_all_rows(rows)

    def reserve_slot(self, slot_id: int, is_synced: bool = False) -> bool:
        rows = self.get_all_rows()

        for row in rows:
            if int(row["slot_id"]) == slot_id:
                if self._to_bool(row["is_occupied"]):
                    return False

                row["is_occupied"] = "True"
                row["is_synced"] = str(is_synced)
                self.overwrite_all_rows(rows)
                return True

        return False

    def release_slot(self, slot_id: int, is_synced: bool = False) -> bool:
        rows = self.get_all_rows()

        for row in rows:
            if int(row["slot_id"]) == slot_id:
                if not self._to_bool(row["is_occupied"]):
                    return False

                row["is_occupied"] = "False"
                row["is_synced"] = str(is_synced)
                self.overwrite_all_rows(rows)
                return True

        return False

    def seed_from_slots(self, slots: List[ParkingSlot]) -> None:
        self.overwrite_all_slots(slots, is_synced=True)

    def get_unsynced_slots(self) -> List[ParkingSlot]:
        rows = self.get_all_rows()
        unsynced = []

        for row in rows:
            if not self._to_bool(row.get("is_synced", True)):
                unsynced.append(self._row_to_slot(row))

        return unsynced

    def mark_slot_synced(self, slot_id: int) -> None:
        rows = self.get_all_rows()

        for row in rows:
            if int(row["slot_id"]) == slot_id:
                row["is_synced"] = "True"
                break

        self.overwrite_all_rows(rows)