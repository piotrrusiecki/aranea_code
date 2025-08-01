import time
from rpi_ws281x import Adafruit_NeoPixel, Color

class Freenove_RPI_WS281X:
    def __init__(self, led_count=8, bright=255, sequence="RGB"):
        # Initialize the LED strip with default parameters
        self.set_led_type(sequence)
        self.set_led_count(led_count)
        self.set_led_brightness(bright)
        self.led_begin()
        self.set_all_led_color(0, 0, 0)

    def led_begin(self):
        # Initialize the NeoPixel strip
        self.strip = Adafruit_NeoPixel(self.get_led_count(), 18, 800000, 10, False, self.led_brightness, 0)
        self.led_init_state = 0 if self.strip.begin() else 1

    def check_rpi_ws281x_state(self):
        # Check the initialization state of the NeoPixel strip
        return self.led_init_state

    def led_close(self):
        # Turn off all LEDs
        self.set_all_led_rgb([0, 0, 0])

    def set_led_count(self, count):
        # Set the number of LEDs in the strip
        self.led_count = count
        self.led_color = [0, 0, 0] * self.led_count
        self.led_original_color = [0, 0, 0] * self.led_count

    def get_led_count(self):
        # Get the number of LEDs in the strip
        return self.led_count

    def set_led_type(self, rgb_type):
        # Set the RGB sequence type for the LEDs
        try:
            led_type = ['RGB', 'RBG', 'GRB', 'GBR', 'BRG', 'BGR']
            led_type_offset = [0x06, 0x09, 0x12, 0x21, 0x18, 0x24]
            index = led_type.index(rgb_type)
            self.led_red_offset = (led_type_offset[index] >> 4) & 0x03
            self.led_green_offset = (led_type_offset[index] >> 2) & 0x03
            self.led_blue_offset = (led_type_offset[index] >> 0) & 0x03
            return index
        except ValueError:
            self.led_red_offset = 1
            self.led_green_offset = 0
            self.led_blue_offset = 2
            return -1

    def set_led_brightness(self, brightness):
        # Set the brightness of the LEDs
        self.led_brightness = brightness
        for led_idx in range(self.get_led_count()):
            self.set_led_rgb_data(led_idx, self.led_original_color)

    def set_ledpixel(self, index, r, g, b):
        # Set the color of a specific LED
        p = [0, 0, 0]
        p[self.led_red_offset] = round(r * self.led_brightness / 255)
        p[self.led_green_offset] = round(g * self.led_brightness / 255)
        p[self.led_blue_offset] = round(b * self.led_brightness / 255)
        self.led_original_color[index * 3 + self.led_red_offset] = r
        self.led_original_color[index * 3 + self.led_green_offset] = g
        self.led_original_color[index * 3 + self.led_blue_offset] = b
        for color_idx in range(3):
            self.led_color[index * 3 + color_idx] = p[color_idx]

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
        for led_idx in range(self.get_led_count()):
            self.set_led_color_data(led_idx, r, g, b)

    def set_all_led_rgb_data(self, color):
        # Set the RGB data of all LEDs
        for led_idx in range(self.get_led_count()):
            self.set_led_rgb_data(led_idx, color)

    def set_all_led_color(self, r, g, b):
        # Set the color of all LEDs and update the display
        for led_idx in range(self.get_led_count()):
            self.set_led_color_data(led_idx, r, g, b)
        self.show()

    def set_all_led_rgb(self, color):
        # Set the RGB color of all LEDs and update the display
        for led_idx in range(self.get_led_count()):
            self.set_led_rgb_data(led_idx, color)
        self.show()

    def show(self):
        # Update the LED strip with the current color data
        for led_idx in range(self.get_led_count()):
            self.strip.setPixelColor(led_idx, Color(self.led_color[led_idx * 3], self.led_color[led_idx * 3 + 1], self.led_color[led_idx * 3 + 2]))
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
    led = Freenove_RPI_WS281X(4, 255, "RGB")

    try:
        if led.check_rpi_ws281x_state() != 0:
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
            while True:
                for j in range(255):
                    for led_idx in range(led.led_count):
                        led.set_led_rgb_data(led_idx, Freenove_RPI_WS281X.wheel((round(led_idx * 255 / led.led_count) + j) % 256))
                    led.show()
                    time.sleep(0.002)
        else:
            led.led_close()
    except KeyboardInterrupt:
        led.led_close()