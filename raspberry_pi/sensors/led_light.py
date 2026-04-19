from gpiozero import LED

class LEDLight:
    def __init__(self, pin):
        self.led = LED(pin)

    def turn_on(self):
        self.led.on()

    def turn_off(self):
        self.led.off()