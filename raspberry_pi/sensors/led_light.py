from gpiozero import LED

class LEDLight:
    """
    Controls a GPIO LED using gpiozero library.
    Provides simple on/off functionality for hardware indication.
    """
    def __init__(self, pin):
        self.led = LED(pin)

    def turn_on(self):
        self.led.on()

    def turn_off(self):
        self.led.off()