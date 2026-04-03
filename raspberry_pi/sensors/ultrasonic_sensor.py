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

    def detect_vehicle_by_range(self, min_distance, max_distance):
        distance = self.get_distance()
        print(f"{self.get_sensor_name()} Distance: {distance} cm")

        if min_distance <= distance <= max_distance:
            print(f"Vehicle detected in range {min_distance}-{max_distance}")
            return True
        return False