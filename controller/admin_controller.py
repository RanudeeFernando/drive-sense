# controller/admin_controller.py

from core.admin import Admin

class AdminController:

    def __init__(self, light_controller):
        self.admin = Admin()
        self.light_controller = light_controller

    def disable_lighting(self):
        print("\n🔐 Admin authentication required to disable lighting")

        if self.admin.login():
            self.light_controller.disable_system()
        else:
            print("❌ Access denied")

    def enable_lighting(self):
        print("\n🔐 Admin authentication required to enable lighting")

        if self.admin.login():
            self.light_controller.enable_system()
        else:
            print("❌ Access denied")