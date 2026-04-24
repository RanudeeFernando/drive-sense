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
            "is_occupied",
            "is_synced"
        ]

        self._ensure_file_exists()

    @staticmethod
    def _to_bool(value) -> bool:
        return str(value).strip().lower() in ("true", "1", "yes")

    def _ensure_file_exists(self) -> None:
        """
        Creates the CSV file if it does not exist.
        Also upgrades older files by adding missing fields.
        """
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()
            print(f"DEBUG[SlotMemoryStore]: created {self.csv_path}")
            return

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

            print("DEBUG[SlotMemoryStore]: upgraded CSV with is_synced column")

    def _row_to_slot(self, row: dict) -> ParkingSlot:
        """
        Converts a CSV row dictionary into a ParkingSlot object.
        """
        return ParkingSlot(
            slot_id=int(row["slot_id"]),
            slot_type=VehicleType(row["slot_type"]),
            is_occupied=self._to_bool(row["is_occupied"])
        )

    def _slot_to_row(self, slot: ParkingSlot, is_synced: bool = False) -> dict:
        """
        Converts a ParkingSlot object into a CSV row dictionary.
        """
        return {
            "slot_id": str(slot.get_slot_id()),
            "slot_type": slot.get_slot_type().value,
            "is_occupied": str(slot.get_slot_status()),
            "is_synced": str(is_synced)
        }

    def get_all_rows(self) -> List[dict]:
        """
        Retrieves all rows from the CSV file.
        Ensures missing fields are populated with default values.
        """
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
        """
        Replaces all existing CSV data with provided rows.
        """
        self._ensure_file_exists()

        normalized_rows = []
        for row in rows:
            normalized_rows.append({
                "slot_id": str(row["slot_id"]),
                "slot_type": str(row["slot_type"]),
                "is_occupied": str(row["is_occupied"]),
                "is_synced": str(row.get("is_synced", False))
            })

        with open(self.csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            for row in normalized_rows:
                writer.writerow(row)

        print(f"DEBUG[SlotMemoryStore]: wrote {len(normalized_rows)} slot rows")

    def get_all_slots(self) -> List[ParkingSlot]:
        return [self._row_to_slot(row) for row in self.get_all_rows()]

    def overwrite_all_slots(self, slots: List[ParkingSlot], is_synced: bool = False) -> None:
        """
        Replaces all slot data using ParkingSlot objects.
        Converts objects into rows before saving.
        """
        rows = [self._slot_to_row(slot, is_synced=is_synced) for slot in slots]
        self.overwrite_all_rows(rows)

    def get_slot_by_id(self, slot_id: int) -> Optional[ParkingSlot]:
        """
        Retrieves a single slot by its ID.
        Returns None if no matching slot is found.
        """
        for row in self.get_all_rows():
            if int(row["slot_id"]) == slot_id:
                return self._row_to_slot(row)
        return None

    def find_available_slot(self, vehicle_type: VehicleType) -> Optional[ParkingSlot]:
        """
        Finds the first available slot for a given vehicle type.
        Returns None if no suitable slot is available.
        """
        for row in self.get_all_rows():
            slot = self._row_to_slot(row)
            if slot.get_slot_type() == vehicle_type and not slot.get_slot_status():
                return slot
        return None

    def upsert_slot(self, slot: ParkingSlot, is_synced: bool = False) -> None:
        """
        Updates an existing slot or inserts a new one.
        Maintains sync status during the operation.
        """
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
        print(f"DEBUG[SlotMemoryStore]: upserted slot {slot.get_slot_id()} synced={is_synced}")

    def reserve_slot(self, slot_id: int, is_synced: bool = False) -> bool:
        """
        Marks a slot as occupied if available.
        Returns False if the slot is already occupied or not found.
        """
        rows = self.get_all_rows()

        for row in rows:
            if int(row["slot_id"]) == slot_id:
                if self._to_bool(row["is_occupied"]):
                    return False

                row["is_occupied"] = "True"
                row["is_synced"] = str(is_synced)
                self.overwrite_all_rows(rows)
                print(f"DEBUG[SlotMemoryStore]: reserved slot {slot_id} synced={is_synced}")
                return True

        return False

    def release_slot(self, slot_id: int, is_synced: bool = False) -> bool:
        """
        Marks a slot as free if currently occupied.
        Returns False if the slot is already free or not found.
        """
        rows = self.get_all_rows()

        for row in rows:
            if int(row["slot_id"]) == slot_id:
                if not self._to_bool(row["is_occupied"]):
                    return False

                row["is_occupied"] = "False"
                row["is_synced"] = str(is_synced)
                self.overwrite_all_rows(rows)
                print(f"DEBUG[SlotMemoryStore]: released slot {slot_id} synced={is_synced}")
                return True

        return False

    def seed_from_slots(self, slots: List[ParkingSlot]) -> None:
        """
        Initializes the CSV with a list of slots.
        Used to sync initial data from external sources.
        """
        if not slots:
            print("DEBUG[SlotMemoryStore]: seed skipped because slot list is empty")
            return

        self.overwrite_all_slots(slots, is_synced=True)
        print(f"DEBUG[SlotMemoryStore]: seeded {len(slots)} slots from Firestore")

    def get_unsynced_slots(self) -> List[ParkingSlot]:
        """
        Retrieves all slots that are not yet synced.
        Used for pushing updates to external systems.
        """
        unsynced = []
        for row in self.get_all_rows():
            if not self._to_bool(row.get("is_synced", False)):
                unsynced.append(self._row_to_slot(row))
        return unsynced

    def mark_slot_synced(self, slot_id: int) -> None:
        """
        Marks a specific slot as synced in the CSV.
        Updates only the sync status field.
        """
        rows = self.get_all_rows()

        for row in rows:
            if int(row["slot_id"]) == slot_id:
                row["is_synced"] = "True"
                break

        self.overwrite_all_rows(rows)
        print(f"DEBUG[SlotMemoryStore]: marked slot {slot_id} as synced")

