import RPi.GPIO as GPIO
import time
import csv
import random
from sensors.sensor import Sensor


class UltrasonicSensor(Sensor):

    def __init__(self, sensor_id: int = 2):
        super().__init__(sensor_id)

        GPIO.setmode(GPIO.BOARD)
        self.TRIG = 16
        self.ECHO = 18

        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)

    def detect_slot_occupancy(self) -> bool:
        print("📡 Checking for vehicle...")
        time.sleep(1)
        return True

    def detect_exit_vehicle(self):
        return True  # simulate always detecting for now

    def get_distance(self):
        # simulate distance in cm
        return random.randint(1, 20)

    def get_slot_from_distance(self, distance):
        with open("data/slots.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                start = float(row["distance_start"])
                end = float(row["distance_end"])
                if start <= distance <= end:
                    return int(row["slot_id"])
        return None
    
    def read_distance_gpio(self):
        # Ensure trigger is low
        GPIO.output(self.TRIG, False)
        time.sleep(0.2)

        # Send trigger pulse
        GPIO.output(self.TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, False)

        # Wait for echo start
        while GPIO.input(self.ECHO) == 0:
            pulse_start = time.time()

        # Wait for echo end
        while GPIO.input(self.ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start

        # Speed of sound = 34300 cm/s
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        return distance
