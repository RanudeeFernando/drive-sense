from cloud_server.repositories.light_repository import LightRepository

class LightManagerService:
    def __init__(self, threshold=15):
        self.threshold = threshold
        self.light_on = False
        self.light_repository = LightRepository()

    def process_light(self, light_on: bool):
        print(f"Light status received from PI: {light_on}")

        # Update internal state (optional but useful)
        if light_on != self.light_on:
            self.light_on = light_on
            self.light_repository.log_event(self.light_on) # Log change

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
        if not self.light_on:
            self.light_on = True
            self.light_repository.log_event(True)
            print("Light manually turned ON")

    def turn_off(self):
        """Manually turn off the lighting system."""
        if self.light_on:
            self.light_on = False
            self.light_repository.log_event(False)
            print("Light manually turned OFF")
