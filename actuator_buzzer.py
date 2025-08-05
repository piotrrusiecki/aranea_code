import time
from gpiozero import OutputDevice

class Buzzer:
    def __init__(self):
        """Initialize the Buzzer class."""
        self.PIN = 17                            # Set the GPIO pin for the buzzer
        self.buzzer_pin = OutputDevice(self.PIN) # Initialize the buzzer pin

    def set_state(self, state: bool) -> None:
        """Set the state of the buzzer."""
        if state:
            self.buzzer_pin.on()
        else:
            self.buzzer_pin.off()

    def close(self) -> None:
        """Close the buzzer pin."""
        self.buzzer_pin.close()           # type: ignore  # Close the buzzer pin to release the GPIO resource

if __name__ == '__main__':
    buzzer = None
    try:
        buzzer = Buzzer()                 # Create an instance of the Buzzer class
        buzzer.set_state(True)            # Turn on the buzzer
        time.sleep(3)                     # Wait for 3 second
        buzzer.set_state(False)           # Turn off the buzzer
    finally:
        if buzzer is not None:
            buzzer.close()                # Ensure the buzzer pin is closed when the program is interrupted



