# controller/admin_controller.py

from core.admin import Admin

class AdminController:

    def __init__(self, light_controller):
        self.admin = Admin()
        self.light_controller = light_controller
    def toggle_light(self, turn_on: bool):
        if turn_on:
            self.light_controller.turn_on()
        else:
            self.light_controller.turn_off()