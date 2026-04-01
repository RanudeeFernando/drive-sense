import csv


class ParkingSlot:
    def __init__(self, slot_id: int = 1, slot_type: str = "car", slot_length: float = "5", slot_width: float ="2"):
        self._slot_id = slot_id
        self._slot_type = slot_type
        self._slot_length = slot_length
        self._slot_width = slot_width
        self._is_occupied = False

    def set_slot_id(self, slot_id: int) -> None:
        self._slot_id = slot_id

    def get_slot_id(self) -> int:
        return self._slot_id

    def set_slot_type(self, slot_type: str) -> None:
        self._slot_type = slot_type

    def get_slot_type(self) -> str:
        return self._slot_type

    def set_slot_length(self, slot_length: float) -> None:
        self._slot_length = slot_length

    def get_slot_length(self) -> float:
        return self._slot_length

    def set_slot_width(self, slot_width: float) -> None:
        self._slot_width = slot_width

    def get_slot_width(self) -> float:
        return self._slot_width

    def set_slot_status(self, status: bool) -> None:
        self._is_occupied = status

    def get_slot_status(self) -> bool:
        return self._is_occupied


    def release_slot(self, slot_id: int) -> bool:
        rows = []

        with open("data/slots.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["slot_id"] == str(slot_id):
                    row["is_occupied"] = "False"
                rows.append(row)

        with open("data/slots.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        print(f"🅿️ Slot {slot_id} released")
        return True


    def findAvailableSlot(self, vehicle_type):
        with open("data/slots.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["slot_type"] == vehicle_type and row["is_occupied"] == "False":
                    return row["slot_id"]
        return None

    def reserveSlot(self, slot_id):
        rows = []

        with open("data/slots.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["slot_id"] == slot_id:
                    row["is_occupied"] = "True"
                rows.append(row)

        with open("data/slots.csv", "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        print(f"🅿️ Slot {slot_id} reserved")