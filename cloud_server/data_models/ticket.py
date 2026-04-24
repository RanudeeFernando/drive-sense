# # cloud_server/data_models/ticket.py
#
# from cloud_server.data_models.parking_slot import ParkingSlot
# from cloud_server.data_models.vehicle_type import VehicleType
#
# class Ticket:
#     def __init__(
#         self,
#         ticket_id: str,
#         parking_slot: ParkingSlot,
#         vehicle_type: VehicleType,
#         entry_time: str,
#         exit_time: str = "",
#         duration_minutes: float = 0,
#         price: float = 0,
#         status: str = "active",
#         pin_code: str = "",
#         pin_status: str = "active"
#     ):
#         self._ticket_id = ticket_id
#         self._parking_slot = parking_slot
#         self._vehicle_type = vehicle_type
#         self._entry_time = entry_time
#         self._exit_time = exit_time
#         self._duration_minutes = duration_minutes
#         self._price = price
#         self._status = status
#         self._pin_code = pin_code
#         self._pin_status = pin_status
#
#     def get_ticket_id(self) -> str:
#         return self._ticket_id
#
#     def set_ticket_id(self, ticket_id: str) -> None:
#         self._ticket_id = ticket_id
#
#     def get_parking_slot(self) -> ParkingSlot:
#         return self._parking_slot
#
#     def set_parking_slot(self, parking_slot: ParkingSlot) -> None:
#         self._parking_slot = parking_slot
#
#     def get_slot_id(self) -> int:
#         return self._parking_slot.get_slot_id()
#
#     def get_vehicle_type(self) -> VehicleType:
#         return self._vehicle_type
#
#     def set_vehicle_type(self, vehicle_type: VehicleType) -> None:
#         self._vehicle_type = vehicle_type
#
#     def get_entry_time(self) -> str:
#         return self._entry_time
#
#     def set_entry_time(self, entry_time: str) -> None:
#         self._entry_time = entry_time
#
#     def get_exit_time(self) -> str:
#         return self._exit_time
#
#     def set_exit_time(self, exit_time: str) -> None:
#         self._exit_time = exit_time
#
#     def get_duration_minutes(self) -> float:
#         return self._duration_minutes
#
#     def set_duration_minutes(self, duration_minutes: float) -> None:
#         self._duration_minutes = duration_minutes
#
#     def get_price(self) -> float:
#         return self._price
#
#     def set_price(self, price: float) -> None:
#         self._price = price
#
#     def get_status(self) -> str:
#         return self._status
#
#     def set_status(self, status: str) -> None:
#         self._status = status
#
#     def get_pin_code(self) -> str:
#         return self._pin_code
#
#     def set_pin_code(self, pin_code: str) -> None:
#         self._pin_code = pin_code
#
#     def get_pin_status(self) -> str:
#         return self._pin_status
#
#     def set_pin_status(self, pin_status: str) -> None:
#         self._pin_status = pin_status
#
#
#
#     def to_dict(self) -> dict:
#         return {
#             "ticket_id": self._ticket_id,
#             "slot_id": self._parking_slot.get_slot_id(),  # store only ID
#             "vehicle_type": self._vehicle_type.value,
#             "entry_time": self._entry_time,
#             "exit_time": self._exit_time,
#             "duration_minutes": self._duration_minutes,
#             "price": self._price,
#             "status": self._status,
#             "pin_code": self._pin_code,
#             "pin_status": self._pin_status
#         }