import RPi.GPIO as GPIO
import time
from gpiozero import LED


class LDRSensor:
    def __init__(self, pin=4, led_pin=18, threshold=500):
        self.pin = pin
        self.threshold = threshold
        self.led = LED(led_pin)

        # ❌ DO NOT set mode here

    def read_resistance(self) -> float:
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(0.1)

        GPIO.setup(self.pin, GPIO.IN)
        start_time = time.time()

        while GPIO.input(self.pin) == GPIO.LOW:
            pass

        diff = time.time() - start_time
        resistance = diff * 1000
        return resistance

    def is_light(self, resistance):
        return resistance < self.threshold

    def control_led(self, light_on):
        if light_on:
            self.led.on()
        else:
            self.led.off()

    def cleanup(self):
        GPIO.cleanup()