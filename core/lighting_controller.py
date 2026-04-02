class LightingController:
    def __init__(self):
        self.light_status = False

    def turn_on(self):
        self.light_status = True
        return "ON"

    def turn_off(self):
        self.light_status = False
        return "OFF"

    def get_status(self):
        return self.light_status