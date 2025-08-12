# -*-coding: utf-8 -*-
import time
import threading
import logging
from config.parameter import ParameterManager
from hardware_rpi_ledpixel import Freenove_RPI_WS281X
from hardware_spi_ledpixel import Freenove_SPI_LedPixel

logger = logging.getLogger("actuator.led")

class Led:
    def __init__(self):
        self.thread = None
        self.stop_event = threading.Event()
        """Initialize the Led class and set up LED strip based on PCB and Raspberry Pi versions."""
        try:
            # Initialize the ParameterManager instance
            self.param = ParameterManager()
            # Get the PCB version from the parameter file
            self.pcb_version = self.param.get_pcb_version()
            # Get the Raspberry Pi version from the parameter file
            self.pi_version = ParameterManager.get_raspberry_pi_version()

            logger.info("Initializing LED controller - PCB v%d, Pi v%d", self.pcb_version, self.pi_version)

            # Set up the LED strip based on PCB and Raspberry Pi versions
            if self.pcb_version == 1 and self.pi_version == 1:
                self.strip = Freenove_RPI_WS281X(7, 255, 'RGB')
                self.is_support_led_function = True
                logger.info("Using RPI WS281X LED strip (RGB)")

            elif self.pcb_version == 2 and self.pi_version in (1, 2):
                self.strip = Freenove_SPI_LedPixel(7, 255, 'GRB')
                self.is_support_led_function = True
                logger.info("Using SPI LED strip (GRB)")

            elif self.pcb_version == 1 and self.pi_version == 2:
                # Log an error message and disable LED function if unsupported combination
                logger.error("PCB Version 1.0 is not supported on Raspberry PI 5")
                self.is_support_led_function = False

            self.led_mode = '1'
            self.received_color = [20, 0, 0]
            logger.info("LED controller initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize LED controller: %s", e)
            self.is_support_led_function = False
            raise

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.thread = None
        self.stop_event.clear()
        logger.debug("LED animation thread stopped")

    def color_wipe(self, color, wait_ms=50):
        if not self.is_support_led_function:
            logger.debug("LED function not supported, skipping color_wipe")
            return
        try:
            logger.debug("Starting color_wipe animation - color: %s, wait: %dms", color, wait_ms)
            for led_idx in range(self.strip.get_led_count()):
                self.strip.set_led_rgb_data(led_idx, color)
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
            logger.debug("Color wipe animation completed")
        except Exception as e:
            logger.error("Error in color_wipe animation: %s", e)

    @staticmethod
    def wheel(pos):
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
            logger.debug("LED function not supported, skipping rainbow")
            return
        try:
            logger.debug("Starting rainbow animation - wait: %dms, iterations: %d", wait_ms, iterations)
            for j in range(256 * iterations):
                for led_idx in range(self.strip.get_led_count()):
                    self.strip.set_led_rgb_data(led_idx, self.wheel((led_idx + j) & 255))
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
            logger.debug("Rainbow animation completed")
        except Exception as e:
            logger.error("Error in rainbow animation: %s", e)

    def rainbow_cycle(self, wait_ms=20, iterations=1):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        if not self.is_support_led_function:
            logger.debug("LED function not supported, skipping rainbow_cycle")
            return
        try:
            logger.debug("Starting rainbow_cycle animation - wait: %dms, iterations: %d", wait_ms, iterations)
            for j in range(256 * iterations):
                if self.stop_event.is_set():
                    logger.debug("Rainbow cycle animation stopped by stop event")
                    return
                for led_idx in range(self.strip.get_led_count()):
                    if self.stop_event.is_set():
                        break
                    self.strip.set_led_rgb_data(led_idx, self.wheel((int(led_idx * 256 / self.strip.get_led_count()) + j) & 255))
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
            logger.debug("Rainbow cycle animation completed")
        except Exception as e:
            logger.error("Error in rainbow_cycle animation: %s", e)

    def theater_chase(self, color, wait_ms=50):
        """Movie theater light style chaser animation."""
        if not self.is_support_led_function:
            logger.debug("LED function not supported, skipping theater_chase")
            return 
        try:
            logger.debug("Starting theater_chase animation - color: %s, wait: %dms", color, wait_ms)
            led_count = self.strip.get_led_count()
            for led_index in range(led_count):
                for q in range(3):
                    self.strip.set_led_rgb_data((led_index + q * 4) % led_count, color)
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for q in range(3):
                    self.strip.set_led_rgb_data((led_index + q * 4) % led_count, [0, 0, 0])
            logger.debug("Theater chase animation completed")
        except Exception as e:
            logger.error("Error in theater_chase animation: %s", e)

    def led_index(self, index, r, g, b):
        if not self.is_support_led_function:
            logger.debug("LED function not supported, skipping led_index")
            return
        try:
            change_color = [r, g, b]
            logger.debug("Setting LED index %d to color %s", index, change_color)
            for bit_index in range(8):
                if index & 0x01 == 1:
                    self.strip.set_led_rgb_data(bit_index, change_color)
                index = index >> 1
            self.strip.show()
        except Exception as e:
            logger.error("Error setting LED index %d: %s", index, e)

    def process_light_command(self, data):
        """Process light commands to control LED behavior."""
        try:
            if len(data) < 4:
                self.led_mode = data[1]
            else:
                for color_channel in range(3):
                    self.received_color[color_channel] = int(data[color_channel + 1])
            
            logger.debug("Processing light command - mode: %s, color: %s", self.led_mode, self.received_color)
            
            if self.led_mode == '0':
                logger.info("Turning off all LEDs")
                self.stop()
                self.color_wipe([0, 0, 0])
                return
            elif self.led_mode == '1':
                logger.debug("Setting static LED color")
                self.led_index(0x7f, self.received_color[0], self.received_color[1], self.received_color[2])
            elif self.led_mode == '2':
                logger.info("Starting RGB wipe animation")
                self.stop()
                def loop():
                    while not self.stop_event.is_set():
                        self.color_wipe([255, 0, 0])   # Red wipe
                        self.color_wipe([0, 255, 0])   # Green wipe
                        self.color_wipe([0, 0, 255])   # Blue wipe
                self.thread = threading.Thread(target=loop)
                self.thread.start()
            elif self.led_mode == '3':
                logger.info("Starting theater chase animation")
                self.stop()
                def loop():
                    while not self.stop_event.is_set():
                        self.theater_chase(self.received_color)
                self.thread = threading.Thread(target=loop)
                self.thread.start()
            elif self.led_mode == '4':
                logger.info("Starting rainbow animation")
                self.stop()
                def loop():
                    while not self.stop_event.is_set():
                        self.rainbow()
                self.thread = threading.Thread(target=loop)
                self.thread.start()
            elif self.led_mode == '5':
                logger.info("Starting rainbow cycle animation")
                self.stop()
                def loop():
                    while not self.stop_event.is_set():
                        self.rainbow_cycle()
                self.thread = threading.Thread(target=loop)
                self.thread.start()
            else:
                logger.warning("Unknown LED mode: %s", self.led_mode)
        except Exception as e:
            logger.error("Error processing light command: %s", e)

# Main program logic follows:
if __name__ == '__main__':
    logger.info('LED test program starting')
    try:
        led = Led()
        logger.info("Testing color_wipe animation")
        led.color_wipe([255, 0, 0])  # Red wipe
        led.color_wipe([0, 255, 0])  # Green wipe
        led.color_wipe([0, 0, 255])  # Blue wipe
        logger.info("Testing rainbow animation")
        led.rainbow(wait_ms=5)
        logger.info("Testing rainbow_cycle animation")
        led.rainbow_cycle(wait_ms=5)
        led.color_wipe([0, 0, 0], 10)
        logger.info("LED test program completed successfully")
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
        logger.info("LED test program interrupted by user")
        led.color_wipe([0, 0, 0], 10)
    except Exception as e:
        logger.error("Error in LED test program: %s", e)
    finally:
        logger.info("LED test program ended")