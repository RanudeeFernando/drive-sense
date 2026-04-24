


class Admin:
    """
    Simple admin user model with username and password,
    with a method to convert it to a dictionary.
    """
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
