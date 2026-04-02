# cloud_server/cloud_controller/light_controller.py

class LightController:
    def __init__(self, threshold=15):
        self.threshold = threshold
        self.light_on = False

    def process_light(self, resistance: float):
        print(f"💡 Resistance: {resistance}")
        
        if resistance > self.threshold:
            if not self.light_on:
                self.light_on = True
                print("🔆 Turned ON")
            return {"status": "success", "light_on": True}
        else:
            if self.light_on:
                self.light_on = False
                print("🌑 Turned OFF")
            return {"status": "success", "light_on": False}