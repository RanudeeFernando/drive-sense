from dataclasses import dataclass


@dataclass
class Receipt:
    exit_time: str
    price: float = 0.0

    def get_exit_time(self):
        return self.exit_time

    def set_exit_time(self, exit_time):
        self.exit_time = exit_time

    def get_price(self):
        return self.price

    def set_price(self, price):
        self.price = price

    def calculate_price(self, duration_minutes, vehicle_type):
        rates = {
            "bike": 50,
            "car": 100,
            "lorry": 150,
        }

        hours = max(1, duration_minutes / 60)
        self.price = round(rates.get(vehicle_type, 100) * hours, 2)
        return self.price

    def generate_receipt(self):
        return {
            "exit_time": self.exit_time,
            "price": self.price
        }