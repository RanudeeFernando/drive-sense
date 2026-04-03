class Admin:
    def __init__(self, admin_id: int, username: str, password: str):
        self._admin_id = admin_id
        self._username = username
        self._password = password

    def get_admin_id(self) -> int:
        return self._admin_id

    def set_admin_id(self, admin_id: int) -> None:
        self._admin_id = admin_id

    def get_username(self) -> str:
        return self._username

    def set_username(self, username: str) -> None:
        self._username = username

    def get_password(self) -> str:
        return self._password

    def set_password(self, password: str) -> None:
        self._password = password

    def login(self) -> bool:
        pass

    def view_parking_logs(self) -> None:
        pass

    def control_availability(self) -> bool:
        pass

    def view_slot_availability(self) -> None:
        pass
