# cloud_server/services/light_manager_service.py

class LightManagerService:
    def __init__(self, threshold=15):
        self.threshold = threshold
        self.light_on = False

    def process_light(self, light_on: bool):
        print(f"Light status received from PI: {light_on}")

        # Update internal state (optional but useful)
        if light_on != self.light_on:
            self.light_on = light_on

            if self.light_on:
                print("Light turned ON (edge-triggered)")
            else:
                print("Light turned OFF (edge-triggered)")

        return {
            "status": "success",
            "light_on": self.light_on
        }

    def turn_on(self):
        """Manually turn on the lighting system."""
        self.light_on = True
        print("Light manually turned ON")

    def turn_off(self):
        """Manually turn off the lighting system."""
        self.light_on = False
        print("Light manually turned OFF")
