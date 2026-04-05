# cloud_server/cloud_controller/light_controller.py

class LightController:
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