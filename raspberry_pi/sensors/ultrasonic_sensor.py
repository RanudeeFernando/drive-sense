import RPi.GPIO as GPIO
import time
from sensors.sensor import Sensor

class UltrasonicSensor(Sensor):
    def __init__(self, sensor_id, name, trig_pin, echo_pin):
        super().__init__(sensor_id, name)

        self.trig_pin = trig_pin
        self.echo_pin = echo_pin

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def get_distance(self):
        # Send trigger pulse
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)

        start_time = time.time()
        stop_time = time.time()

        # Save start time
        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()

        # Save arrival time
        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()

        # Time difference
        time_elapsed = stop_time - start_time

        # Distance calculation
        distance = (time_elapsed * 34300) / 2

        return round(distance, 2)

    # This method is used to detect the slot availabiltity.
    def detect_free_slot_by_distance(self):
        distance = self.get_distance()
        print(f"{self.get_sensor_name()} Distance: {distance} cm")

        slot_ranges = {
            1: (0, 5),
            2: (5, 10),
            3: (10, 15),
            4: (15, 20),
            5: (20, 25)
        }

        for slot_id, (min_d, max_d) in slot_ranges.items():
            if min_d <= distance < max_d:
                print(f" Slot {slot_id} vehicle exited")
                return slot_id

        return None
    
    # This method is used to detect the presence of a vechicle at the entry point and trigger the camera.
    def detect_object_in_range(self, min_distance=5, max_distance=10):
        distance = self.get_distance()
        print(f"Measured distance: {distance} cm")

        if min_distance <= distance <= max_distance:
            print(" Object detected in range!")
            return True
        else:
            return False