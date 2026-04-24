import csv
import os
from typing import Optional, List

from raspberry_pi.data_models.ticket import Ticket
from raspberry_pi.data_models.parking_slot import ParkingSlot
from raspberry_pi.data_models.vehicle_type import VehicleType


class TicketMemoryStore:
    def __init__(self, csv_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_storage_dir = os.path.join(base_dir, "local_storage")
        os.makedirs(local_storage_dir, exist_ok=True)

        self.csv_path = csv_path or os.path.join(local_storage_dir, "tickets_memory.csv")
        self.fieldnames = [
            "ticket_id",
            "slot_id",
            "vehicle_type",
            "entry_time",
            "exit_time",
            "duration_minutes",
            "price",
            "status",
            "pin_code",
            "pin_status",
            "is_synced"
        ]

        self._ensure_file_exists()

    @staticmethod
    def _to_bool(value) -> bool:
        return str(value).strip().lower() in ("true", "1", "yes")

    def _ensure_file_exists(self) -> None:
        """
        Creates the CSV file if it does not exist.
        Upgrades older files by adding missing fields.
        """
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()
            print(f"DEBUG[TicketMemoryStore]: created {self.csv_path}")
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

            print("DEBUG[TicketMemoryStore]: upgraded CSV with is_synced column")

    def _build_slot(self, slot_id: int, vehicle_type: VehicleType) -> ParkingSlot:
        """
        Creates a basic ParkingSlot object using given slot ID and type.
        Used when reconstructing ticket data.
        """
        return ParkingSlot(
            slot_id=slot_id,
            slot_type=vehicle_type,
            is_occupied=False
        )

    def _row_to_ticket(self, row: dict) -> Ticket:
        """
        Converts a CSV row dictionary into a Ticket object.
        Handles type conversions and default values.
        """
        vehicle_type = VehicleType(row["vehicle_type"])
        slot = self._build_slot(int(row["slot_id"]), vehicle_type)

        return Ticket(
            ticket_id=row["ticket_id"],
            parking_slot=slot,
            vehicle_type=vehicle_type,
            entry_time=row["entry_time"],
            exit_time=row.get("exit_time", ""),
            duration_minutes=float(row.get("duration_minutes", 0) or 0),
            price=float(row.get("price", 0) or 0),
            status=row.get("status", "active"),
            pin_code=row.get("pin_code", ""),
            pin_status=row.get("pin_status", "active")
        )

    def _ticket_to_row(self, ticket: Ticket, is_synced: bool = False) -> dict:
        """
        Converts a Ticket object into a CSV row dictionary.
        Includes sync status for external synchronization.
        """
        return {
            "ticket_id": ticket.get_ticket_id(),
            "slot_id": str(ticket.get_slot_id()),
            "vehicle_type": ticket.get_vehicle_type().value,
            "entry_time": ticket.get_entry_time(),
            "exit_time": ticket.get_exit_time(),
            "duration_minutes": str(ticket.get_duration_minutes()),
            "price": str(ticket.get_price()),
            "status": ticket.get_status(),
            "pin_code": ticket.get_pin_code(),
            "pin_status": ticket.get_pin_status(),
            "is_synced": str(is_synced)
        }

    def get_all_rows(self) -> List[dict]:
        """
        Retrieves all ticket rows from the CSV file.
        Ensures required fields are present.
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
        Replaces all existing ticket data with new rows.
        Normalizes values before writing to CSV.
        """
        self._ensure_file_exists()

        normalized_rows = []
        for row in rows:
            normalized_rows.append({
                "ticket_id": str(row["ticket_id"]),
                "slot_id": str(row["slot_id"]),
                "vehicle_type": str(row["vehicle_type"]),
                "entry_time": str(row["entry_time"]),
                "exit_time": str(row.get("exit_time", "")),
                "duration_minutes": str(row.get("duration_minutes", 0)),
                "price": str(row.get("price", 0)),
                "status": str(row.get("status", "active")),
                "pin_code": str(row.get("pin_code", "")),
                "pin_status": str(row.get("pin_status", "active")),
                "is_synced": str(row.get("is_synced", False))
            })

        with open(self.csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            for row in normalized_rows:
                writer.writerow(row)

        print(f"DEBUG[TicketMemoryStore]: wrote {len(normalized_rows)} ticket rows")

    def get_all_tickets(self) -> List[Ticket]:
        return [self._row_to_ticket(row) for row in self.get_all_rows()]

    def overwrite_all_tickets(self, tickets: List[Ticket], is_synced: bool = False) -> None:
        """
        Replaces all ticket data using Ticket objects.
        Converts them into rows before saving.
        """
        rows = [self._ticket_to_row(ticket, is_synced=is_synced) for ticket in tickets]
        self.overwrite_all_rows(rows)

    def upsert_ticket(self, ticket: Ticket, is_synced: bool = False) -> None:
        """
        Updates an existing ticket or inserts a new one.
        Maintains sync status during the operation.
        """
        rows = self.get_all_rows()
        updated = False

        for index, row in enumerate(rows):
            if row["ticket_id"] == ticket.get_ticket_id():
                rows[index] = self._ticket_to_row(ticket, is_synced=is_synced)
                updated = True
                break

        if not updated:
            rows.append(self._ticket_to_row(ticket, is_synced=is_synced))

        self.overwrite_all_rows(rows)
        print(f"DEBUG[TicketMemoryStore]: upserted ticket {ticket.get_ticket_id()} synced={is_synced}")

    def get_ticket_by_id(self, ticket_id: str):
        """
        Retrieves a ticket by its ID.
        Returns None if no matching ticket is found.
        """
        for ticket in self.get_all_tickets():
            if ticket.get_ticket_id() == ticket_id:
                return ticket
        return None

    def get_active_ticket_by_slot_id(self, slot_id: int):
        """
        Finds an active ticket for a given slot ID.
        Returns None if no active ticket exists.
        """
        for ticket in self.get_all_tickets():
            if ticket.get_slot_id() == slot_id and ticket.get_status() == "active":
                return ticket
        return None

    def count_active_tickets_for_slot_id(self, slot_id: int) -> int:
        """
        Counts active tickets associated with a slot.
        Used to track multiple allocations if any.
        """
        count = 0
        for ticket in self.get_all_tickets():
            if ticket.get_slot_id() == slot_id and ticket.get_status() == "active":
                count += 1
        return count

    def get_active_ticket_by_pin(self, pin_code: str):
        """
        Retrieves an active ticket using a PIN code.
        Returns None if no match is found.
        """
        for ticket in self.get_all_tickets():
            if ticket.get_pin_code() == pin_code and ticket.get_status() == "active":
                return ticket
        return None

    def generate_ticket(
        self,
        parking_slot: ParkingSlot,
        vehicle_type: VehicleType,
        ticket_id: str,
        pin_code: str,
        entry_time: str,
        is_synced: bool = False
    ) -> dict:

        """
        Creates a new ticket and stores it.
        Returns essential ticket details for immediate use.
        """

        ticket = Ticket(
            ticket_id=ticket_id,
            parking_slot=parking_slot,
            vehicle_type=vehicle_type,
            entry_time=entry_time,
            exit_time="",
            duration_minutes=0,
            price=0,
            status="active",
            pin_code=pin_code,
            pin_status="active"
        )

        self.upsert_ticket(ticket, is_synced=is_synced)

        return {
            "ticket_id": ticket_id,
            "pin_code": pin_code,
            "entry_time": entry_time,
            "slot_id": parking_slot.get_slot_id(),
            "vehicle_type": vehicle_type.value
        }

    def update_ticket_on_exit(
        self,
        ticket_id: str,
        exit_time: str,
        duration_minutes: float,
        price: float,
        is_synced: bool = False
    ) -> bool:

        """
        Updates ticket details when a vehicle exits.
        Marks ticket as closed and updates pricing info.
        """
        rows = self.get_all_rows()

        for row in rows:
            if row["ticket_id"] == ticket_id:
                row["exit_time"] = exit_time
                row["duration_minutes"] = str(round(duration_minutes, 2))
                row["price"] = str(price)
                row["status"] = "closed"
                row["pin_status"] = "expired"
                row["is_synced"] = str(is_synced)
                self.overwrite_all_rows(rows)
                print(f"DEBUG[TicketMemoryStore]: updated ticket exit {ticket_id} synced={is_synced}")
                return True

        return False

    def seed_from_tickets(self, tickets: List[Ticket]) -> None:
        """
        Initializes storage with a list of tickets.
        Used to sync data from external sources.
        """
        if not tickets:
            print("DEBUG[TicketMemoryStore]: seed skipped because ticket list is empty")
            return

        self.overwrite_all_tickets(tickets, is_synced=True)
        print(f"DEBUG[TicketMemoryStore]: seeded {len(tickets)} tickets from Firestore")

    def get_unsynced_tickets(self) -> List[Ticket]:
        """
        Retrieves tickets that are not yet synced.
        Used for pushing updates externally.
        """

        unsynced = []
        for row in self.get_all_rows():
            if not self._to_bool(row.get("is_synced", False)):
                unsynced.append(self._row_to_ticket(row))
        return unsynced

    def mark_ticket_synced(self, ticket_id: str) -> None:
        """
        Marks a specific ticket as synced.
        Updates only the sync status field.
        """
        rows = self.get_all_rows()

        for row in rows:
            if row["ticket_id"] == ticket_id:
                row["is_synced"] = "True"
                break

        self.overwrite_all_rows(rows)
        print(f"DEBUG[TicketMemoryStore]: marked ticket {ticket_id} as synced")

