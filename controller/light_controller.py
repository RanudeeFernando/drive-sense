# controller/light_controller.py

import time

class LightController:
    def __init__(self, light_sensor, threshold=15):
        self.light_sensor = light_sensor
        self.threshold = threshold
        self.light_on = False

    
    

    def control_light(self):
        resistance = self.light_sensor.detect_light_level()

        print(f"💡 [LIGHT] Resistance: {resistance}")

        
        if resistance > self.threshold:
            if not self.light_on:
                self.light_on = True
                print("🔆 [LIGHT] Turned ON")

        
        else:
            if self.light_on:
                self.light_on = False
                print("🌑 [LIGHT] Turned OFF")

    def run(self):
        while True:
            self.control_light()
            time.sleep(10)