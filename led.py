# -*-coding: utf-8 -*-
import time
import threading
import logging
from parameter import ParameterManager
from rpi_ledpixel import Freenove_RPI_WS281X
from spi_ledpixel import Freenove_SPI_LedPixel

logger = logging.getLogger("led")

class Led:
    def __init__(self):
        self.thread = None
        self.stop_event = threading.Event()
        """Initialize the Led class and set up LED strip based on PCB and Raspberry Pi versions."""
        # Initialize the ParameterManager instance
        self.param = ParameterManager()
        # Get the PCB version from the parameter file
        self.pcb_version = self.param.get_pcb_version()
        # Get the Raspberry Pi version from the parameter file
        self.pi_version = self.param.get_raspberry_pi_version()

        # Set up the LED strip based on PCB and Raspberry Pi versions
        if self.pcb_version == 1 and self.pi_version == 1:
            self.strip = Freenove_RPI_WS281X(7, 255, 'RGB')
            self.is_support_led_function = True

        elif self.pcb_version == 2 and self.pi_version in (1, 2):
            self.strip = Freenove_SPI_LedPixel(7, 255, 'GRB')
            self.is_support_led_function = True

        elif self.pcb_version == 1 and self.pi_version == 2:
            # Log an error message and disable LED function if unsupported combination
            logger.error("PCB Version 1.0 is not supported on Raspberry PI 5.")
            self.is_support_led_function = False

        self.led_mode = '1'
        self.received_color = [20, 0, 0]

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.thread = None
        self.stop_event.clear()

    def color_wipe(self, color, wait_ms=50):
        if not self.is_support_led_function:
            return
        for i in range(self.strip.get_led_count()):
            self.strip.set_led_rgb_data(i, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = pos * 3
            g = 255 - pos * 3
            b = 0
        elif pos < 170:
            pos -= 85
            r = 255 - pos * 3
            g = 0
            b = pos * 3
        else:
            pos -= 170
            r = 0
            g = pos * 3
            b = 255 - pos * 3
        return [r, g, b]

    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        if not self.is_support_led_function:
            return
        for j in range(256 * iterations):
            for i in range(self.strip.get_led_count()):
                self.strip.set_led_rgb_data(i, self.wheel((i + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def rainbow_cycle(self, wait_ms=20, iterations=1):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        if not self.is_support_led_function:
            return
        for j in range(256 * iterations):
            if self.stop_event.is_set():
                return
            for i in range(self.strip.get_led_count()):
                if self.stop_event.is_set():
                    break
                self.strip.set_led_rgb_data(i, self.wheel((int(i * 256 / self.strip.get_led_count()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def theater_chase(self, color, wait_ms=50):
        """Movie theater light style chaser animation."""
        if not self.is_support_led_function:
            return 
        led_count = self.strip.get_led_count()
        for i in range(led_count):
            for q in range(3):
                self.strip.set_led_rgb_data((i + q * 4) % led_count, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
            for q in range(3):
                self.strip.set_led_rgb_data((i + q * 4) % led_count, [0, 0, 0])

    def led_index(self, index, r, g, b):
        if not self.is_support_led_function:
            return
        change_color = [r, g, b]
        for i in range(8):
            if index & 0x01 == 1:
                self.strip.set_led_rgb_data(i, change_color)
            index = index >> 1
        self.strip.show()

    def process_light_command(self, data):
        """Process light commands to control LED behavior."""
        old_mode = self.led_mode
        if len(data) < 4:
            self.led_mode = data[1]
        else:
            for i in range(3):
                self.received_color[i] = int(data[i + 1])
        if self.led_mode == '0':
            self.stop()
            self.color_wipe([0, 0, 0])
            return
        elif self.led_mode == '1':
            self.led_index(0x7f, self.received_color[0], self.received_color[1], self.received_color[2])
        elif self.led_mode == '2':
            self.stop()
            def loop():
                while not self.stop_event.is_set():
                    self.color_wipe([255, 0, 0])   # Red wipe
                    self.color_wipe([0, 255, 0])   # Green wipe
                    self.color_wipe([0, 0, 255])   # Blue wipe
            self.thread = threading.Thread(target=loop)
            self.thread.start()
        elif self.led_mode == '3':
            self.stop()
            def loop():
                while not self.stop_event.is_set():
                    self.theater_chase(self.received_color)
            self.thread = threading.Thread(target=loop)
            self.thread.start()
        elif self.led_mode == '4':
            self.stop()
            def loop():
                while not self.stop_event.is_set():
                    self.rainbow()
            self.thread = threading.Thread(target=loop)
            self.thread.start()
        elif self.led_mode == '5':
            self.stop()
            def loop():
                while not self.stop_event.is_set():
                    self.rainbow_cycle()
            self.thread = threading.Thread(target=loop)
            self.thread.start()

# Main program logic follows:
if __name__ == '__main__':
    logger.info('Program is starting ... ')
    led = Led()
    try:
        logger.info("color_wipe animation")
        led.color_wipe([255, 0, 0])  # Red wipe
        led.color_wipe([0, 255, 0])  # Green wipe
        led.color_wipe([0, 0, 255])  # Blue wipe
        logger.info("rainbow animation")
        led.rainbow(wait_ms=5)
        logger.info("rainbow_cycle animation")
        led.rainbow_cycle(wait_ms=5)
        led.color_wipe([0, 0, 0], 10)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
        led.color_wipe([0, 0, 0], 10)
    finally:
        logger.info("End of program")