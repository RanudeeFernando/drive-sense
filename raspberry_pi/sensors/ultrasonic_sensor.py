import RPi.GPIO as GPIO
import time
from sensors.sensor import Sensor


class UltrasonicSensor(Sensor):
    def __init__(self, sensor_id, name, trig_pin, echo_pin):
        super().__init__(sensor_id, name)

        self.trig_pin = trig_pin
        self.echo_pin = echo_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def get_distance(self):
        """
        Measures distance using ultrasonic pulse timing.
        Returns calculated distance in centimeters.
        """
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)

        start_time = time.time()
        stop_time = time.time()

        
        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()

        
        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()

        
        time_elapsed = stop_time - start_time

        
        distance = (time_elapsed * 34300) / 2

        return round(distance, 2)
    
    def detect_object_in_range(self, min_distance=0, max_distance=10):
        """
        Detects whether an object is within a specified distance range.
        Used for triggering events like camera activation.
        """
        distance = self.get_distance()
        print(f"Measured distance: {distance} cm")

        if min_distance <= distance <= max_distance:
            print("Object detected in range!")
            return True
        else:
            return False

    def is_within_threshold(self, max_threshold):
        """
        Checks if an object is within a maximum distance threshold.
        Returns distance if within range, otherwise None.
        """
        distance = self.get_distance()

        if distance is None:
            return None

        if distance <= max_threshold:
            return distance

        return None

    def get_slot_id_by_distance(self, distance=None):
        """
        Maps measured distance to a predefined parking slot ID.
        Returns slot ID based on configured distance ranges.
        """
        if distance is None:
            distance = self.get_distance()

        if distance is None:
            return None

        slot_ranges = {
            1: (61.5, 71.5),
            2: (51.5, 61.5),
            3: (36.5, 51.5),
            4: (21.5, 36.5),
            5: (1.5, 21.5)
        }

        for slot_id, (min_d, max_d) in slot_ranges.items():
            if min_d <= distance < max_d:
                return slot_id

        return None