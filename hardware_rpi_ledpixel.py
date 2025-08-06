import time
import logging
from rpi_ws281x import Adafruit_NeoPixel, Color
from typing import List, Tuple, Optional

# Configure LED logger
logger = logging.getLogger('led.hw.rpi')

class Freenove_RPI_WS281X:
    def __init__(self, led_count=8, bright=255, sequence="RGB"):
        # Initialize the LED strip with default parameters
        logger.info("Initializing LED strip with %d LEDs, brightness %d, sequence %s", led_count, bright, sequence)
        self.set_led_type(sequence)
        self.set_led_count(led_count)
        self.set_led_brightness(bright)
        self.led_begin()
        self.set_all_led_color(0, 0, 0)
        logger.info("LED strip initialization complete")

    def led_begin(self):
        # Initialize the NeoPixel strip
        logger.debug("Initializing NeoPixel strip with %d LEDs", self.get_led_count())
        self.strip = Adafruit_NeoPixel(self.get_led_count(), 18, 800000, 10, False, self.led_brightness, 0)
        self.led_init_state = 0 if self.strip.begin() else 1
        if self.led_init_state == 0:
            logger.info("NeoPixel strip initialized successfully")
        else:
            logger.error("Failed to initialize NeoPixel strip")

    def check_rpi_ws281x_state(self):
        # Check the initialization state of the NeoPixel strip
        logger.debug("Checking LED strip state: %d", self.led_init_state)
        return self.led_init_state

    def led_close(self):
        # Turn off all LEDs
        logger.info("Turning off all LEDs")
        self.set_all_led_rgb([0, 0, 0])

    def set_led_count(self, count):
        # Set the number of LEDs in the strip
        logger.debug("Setting LED count to %d", count)
        self.led_count = count
        self.led_color = [0, 0, 0] * self.led_count
        self.led_original_color = [0, 0, 0] * self.led_count

    def get_led_count(self):
        # Get the number of LEDs in the strip
        return self.led_count

    def set_led_type(self, rgb_type):
        # Set the RGB sequence type for the LEDs
        logger.debug("Setting LED type to %s", rgb_type)
        try:
            led_type = ['RGB', 'RBG', 'GRB', 'GBR', 'BRG', 'BGR']
            led_type_offset = [0x06, 0x09, 0x12, 0x21, 0x18, 0x24]
            index = led_type.index(rgb_type)
            self.led_red_offset = (led_type_offset[index] >> 4) & 0x03
            self.led_green_offset = (led_type_offset[index] >> 2) & 0x03
            self.led_blue_offset = (led_type_offset[index] >> 0) & 0x03
            logger.debug("LED type set successfully, offsets: R=%d, G=%d, B=%d", self.led_red_offset, self.led_green_offset, self.led_blue_offset)
            return index
        except ValueError:
            logger.warning("Invalid LED type '%s', using default RGB", rgb_type)
            self.led_red_offset = 1
            self.led_green_offset = 0
            self.led_blue_offset = 2
            return -1

    def set_led_brightness(self, brightness):
        # Set the brightness of the LEDs
        logger.debug("Setting LED brightness to %d", brightness)
        self.led_brightness = brightness
        # Use any() to make the side effects intentional
        any(self.set_led_rgb_data(position, self.led_original_color) for position in range(self.get_led_count()))

    def set_ledpixel(self, index, r, g, b):
        # Set the color of a specific LED
        p = [0, 0, 0]
        p[self.led_red_offset] = round(r * self.led_brightness / 255)
        p[self.led_green_offset] = round(g * self.led_brightness / 255)
        p[self.led_blue_offset] = round(b * self.led_brightness / 255)
        self.led_original_color[index * 3 + self.led_red_offset] = r
        self.led_original_color[index * 3 + self.led_green_offset] = g
        self.led_original_color[index * 3 + self.led_blue_offset] = b
        # Use enumerate to avoid loop variable shadowing
        for color_position, _ in enumerate(range(3)):
            self.led_color[index * 3 + color_position] = p[color_position]

    def set_led_color_data(self, index, r, g, b):
        # Set the color data of a specific LED
        self.set_ledpixel(index, r, g, b)

    def set_led_rgb_data(self, index, color):
        # Set the RGB data of a specific LED
        self.set_ledpixel(index, color[0], color[1], color[2])

    def set_led_color(self, index, r, g, b):
        # Set the color of a specific LED and update the display
        self.set_ledpixel(index, r, g, b)
        self.show()

    def set_led_rgb(self, index, color):
        # Set the RGB color of a specific LED and update the display
        self.set_led_rgb_data(index, color)
        self.show()

    def set_all_led_color_data(self, r, g, b):
        # Set the color data of all LEDs
        logger.debug("Setting all LEDs to RGB(%d, %d, %d)", r, g, b)
        # Use any() to make the side effects intentional
        any(self.set_led_color_data(position, r, g, b) for position in range(self.get_led_count()))

    def set_all_led_rgb_data(self, color):
        # Set the RGB data of all LEDs
        logger.debug("Setting all LEDs to RGB%s", color)
        # Use any() to make the side effects intentional
        any(self.set_led_rgb_data(position, color) for position in range(self.get_led_count()))

    def set_all_led_color(self, r, g, b):
        # Set the color of all LEDs and update the display
        # Use any() to make the side effects intentional
        any(self.set_led_color_data(position, r, g, b) for position in range(self.get_led_count()))
        self.show()

    def set_all_led_rgb(self, color):
        # Set the RGB color of all LEDs and update the display
        # Use any() to make the side effects intentional
        any(self.set_led_rgb_data(position, color) for position in range(self.get_led_count()))
        self.show()

    def show(self):
        # Update the LED strip with the current color data
        # Use enumerate to avoid loop variable shadowing
        for led_index, _ in enumerate(range(self.get_led_count())):
            self.strip.setPixelColor(led_index, Color(
                self.led_color[led_index * 3], 
                self.led_color[led_index * 3 + 1], 
                self.led_color[led_index * 3 + 2]
            ))
        self.strip.show()

    @staticmethod
    def wheel(pos):
        # Generate a color wheel value based on the position
        if pos < 85:
            return [(255 - pos * 3), (pos * 3), 0]
        elif pos < 170:
            pos = pos - 85
            return [0, (255 - pos * 3), (pos * 3)]
        else:
            pos = pos - 170
            return [(pos * 3), 0, (255 - pos * 3)]

    @staticmethod
    def hsv2rgb(h, s, v):
        # Convert HSV to RGB
        h = h % 360
        rgb_max = round(v * 2.55)
        rgb_min = round(rgb_max * (100 - s) / 100)
        sector = round(h / 60)
        diff = round(h % 60)
        rgb_adj = round((rgb_max - rgb_min) * diff / 60)
        if sector == 0:
            r = rgb_max
            g = rgb_min + rgb_adj
            b = rgb_min
        elif sector == 1:
            r = rgb_max - rgb_adj
            g = rgb_max
            b = rgb_min
        elif sector == 2:
            r = rgb_min
            g = rgb_max
            b = rgb_min + rgb_adj
        elif sector == 3:
            r = rgb_min
            g = rgb_max - rgb_adj
            b = rgb_max
        elif sector == 4:
            r = rgb_min + rgb_adj
            g = rgb_min
            b = rgb_max
        else:
            r = rgb_max
            g = rgb_min
            b = rgb_max - rgb_adj
        return [r, g, b]

if __name__ == '__main__':
    import os
    
    # Configure logging for the test
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting LED test")
    led = Freenove_RPI_WS281X(4, 255, "RGB")

    try:
        if led.check_rpi_ws281x_state() != 0:
            logger.info("LED strip ready, running test sequence")
            led.set_led_count(4)
            led.set_all_led_color_data(255, 0, 0)
            led.show()
            time.sleep(0.5)
            led.set_all_led_rgb_data([0, 255, 0])
            led.show()
            time.sleep(0.5)
            led.set_all_led_color(0, 0, 255)
            time.sleep(0.5)
            led.set_all_led_rgb([255, 255, 255])
            time.sleep(0.5)
            led.set_all_led_rgb([0, 0, 0])
            time.sleep(0.5)

            led.set_led_brightness(20)
            logger.info("Starting rainbow animation")
            while True:
                for j in range(255):
                    # Use enumerate to avoid loop variable shadowing
                    for position, _ in enumerate(range(led.led_count)):
                        led.set_led_rgb_data(position, Freenove_RPI_WS281X.wheel((round(position * 255 / led.led_count) + j) % 256))
                    led.show()
                    time.sleep(0.002)
        else:
            logger.error("LED strip not ready, closing")
            led.led_close()
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        led.led_close()
    except Exception as e:
        logger.error("Test failed with error: %s", e)
        led.led_close()