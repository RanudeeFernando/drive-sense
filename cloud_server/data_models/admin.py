# cloud_server/data_models/admin.py


class Admin:
    def __init__(self, username: str, password: str):
        self._username = username
        self._password = password

    def get_username(self) -> str:
        return self._username

    def get_password(self) -> str:
        return self._password

    def to_dict(self) -> dict:
        return {
            "username": self._username,
            "password": self._password,
        }
