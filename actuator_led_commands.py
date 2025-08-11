# actuator_led_commands.py
# type: ignore
"""
Simple LED control functions for the Aranea robot.
All functions are straightforward with no complex patterns or states.
"""

import time
import threading
import logging
from typing import List, Optional

logger = logging.getLogger("led.commands")

class LEDStateManager:
    """Manages LED controller and pattern state without global variables."""
    
    def __init__(self):
        self._led_controller = None
        self._current_pattern_thread = None
        self._stop_pattern = False
    
    def init_controller(self, led_controller):
        """Initialize the LED controller."""
        self._led_controller = led_controller
        logger.info("LED commands initialized with direct hardware control")
    
    def get_controller(self):
        """Get the LED controller instance."""
        return self._led_controller
    
    def stop_current_pattern(self):
        """Stop any currently running LED pattern."""
        if self._current_pattern_thread and self._current_pattern_thread.is_alive():
            self._stop_pattern = True
            # Don't try to join the current thread
            if self._current_pattern_thread != threading.current_thread():
                self._current_pattern_thread.join(timeout=1.0)
            self._current_pattern_thread = None
            logger.debug("Stopped current LED pattern")
    
    def start_pattern(self, pattern_func):
        """Start a new pattern, stopping any existing one first."""
        self.stop_current_pattern()
        self._stop_pattern = False
        self._current_pattern_thread = threading.Thread(target=pattern_func, daemon=True)
        self._current_pattern_thread.start()
        return self._current_pattern_thread
    
    def should_stop(self):
        """Check if the current pattern should stop."""
        return self._stop_pattern

# Global instance (but no global variables for state)
_led_manager = LEDStateManager()

def init_led_commands(led_controller):
    """Initialize the LED commands with a controller."""
    _led_manager.init_controller(led_controller)

def get_led_commands():
    """Get the LED controller instance."""
    return _led_manager.get_controller()

# === SET LED FUNCTIONS ===

def _clamp_color(value: int) -> int:
    """Clamp color value to 0-255 range."""
    return max(0, min(255, value))

def set_single_led(led_index: int, r: int, g: int, b: int) -> bool:
    """Set a specific LED to a specific color, stays on until turned off."""
    try:
        if _led_manager.get_controller() is None:
            logger.error("LED controller not initialized")
            return False
        
        # Clamp color values to 0-255 range
        r = _clamp_color(r)
        g = _clamp_color(g)
        b = _clamp_color(b)
        
        controller = _led_manager.get_controller()
        assert controller is not None  # Type checker hint
        controller.led_index(1 << (led_index - 1), r, g, b)  # type: ignore
        logger.info("Set LED %d to RGB(%d,%d,%d)", led_index, r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to set single LED: %s", e)
        return False

def set_multiple_leds(led_indices: List[int], r: int, g: int, b: int) -> bool:
    """Set multiple specific LEDs to a specific color, stays on until turned off."""
    try:
        if _led_manager.get_controller() is None:
            logger.error("LED controller not initialized")
            return False
        
        controller = _led_manager.get_controller()
        assert controller is not None  # Type checker hint
        # Calculate bit mask for selected LEDs
        led_mask = 0
        for led_index in led_indices:
            if 1 <= led_index <= 7:
                led_mask |= (1 << (led_index - 1))
        
        controller.led_index(led_mask, r, g, b)  # type: ignore
        logger.info("Set LEDs %s to RGB(%d,%d,%d)", led_indices, r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to set multiple LEDs: %s", e)
        return False

def set_single_led_time(led_index: int, r: int, g: int, b: int, time_seconds: int = 3) -> bool:
    """Set a specific LED to a specific color for specified seconds, then turn off."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        controller.led_index(1 << (led_index - 1), r, g, b)
        logger.info("Set LED %d to RGB(%d,%d,%d) for %d seconds", led_index, r, g, b, time_seconds)
        
        # Turn off after specified time
        def turn_off_after_time():
            time.sleep(time_seconds)
            controller.led_index(1 << (led_index - 1), 0, 0, 0)
            logger.info("Turned off LED %d after %d seconds", led_index, time_seconds)
        
        threading.Thread(target=turn_off_after_time, daemon=True).start()
        return True
    except Exception as e:
        logger.error("Failed to set single LED with time: %s", e)
        return False

def set_all_led(r: int, g: int, b: int) -> bool:
    """Set all LEDs to a specific color, stays on until turned off."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        controller.led_index(0x7F, r, g, b)  # 0x7F = 0b1111111 = all 7 LEDs
        logger.info("Set all LEDs to RGB(%d,%d,%d)", r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to set all LEDs: %s", e)
        return False

def set_all_led_time(r: int, g: int, b: int, time_seconds: int = 3) -> bool:
    """Set all LEDs to a specific color for specified seconds, then turn off."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        controller.led_index(0x7F, r, g, b)  # 0x7F = 0b1111111 = all 7 LEDs
        logger.info("Set all LEDs to RGB(%d,%d,%d) for %d seconds", r, g, b, time_seconds)
        
        # Turn off after specified time
        def turn_off_after_time():
            time.sleep(time_seconds)
            controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
            logger.info("Turned off all LEDs after %d seconds", time_seconds)
        
        threading.Thread(target=turn_off_after_time, daemon=True).start()
        return True
    except Exception as e:
        logger.error("Failed to set all LEDs with time: %s", e)
        return False

# === FLASH LED FUNCTIONS ===

def flash_led_single(led_index: int, r: int, g: int, b: int) -> bool:
    """Flash a specific LED: 1 second on, 1 second off, continues until stopped."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        def flash_pattern():
            while True:
                controller.led_index(1 << (led_index - 1), r, g, b)
                time.sleep(1)
                controller.led_index(1 << (led_index - 1), 0, 0, 0)
                time.sleep(1)
        
        threading.Thread(target=flash_pattern, daemon=True).start()
        logger.info("Started flashing LED %d with RGB(%d,%d,%d)", led_index, r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to flash single LED: %s", e)
        return False

def flash_led_single_time(led_index: int, r: int, g: int, b: int, time_seconds: int = 3) -> bool:
    """Flash a specific LED for specified seconds, then turn off."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        def flash_pattern():
            end_time = time.time() + time_seconds
            while time.time() < end_time:
                controller.led_index(1 << (led_index - 1), r, g, b)
                time.sleep(1)
                controller.led_index(1 << (led_index - 1), 0, 0, 0)
                time.sleep(1)
            controller.led_index(1 << (led_index - 1), 0, 0, 0)
        
        threading.Thread(target=flash_pattern, daemon=True).start()
        logger.info("Started flashing LED %d with RGB(%d,%d,%d) for %d seconds", led_index, r, g, b, time_seconds)
        return True
    except Exception as e:
        logger.error("Failed to flash single LED with time: %s", e)
        return False

def flash_led_all(r: int, g: int, b: int) -> bool:
    """Flash all LEDs: 1 second on, 1 second off, continues until stopped."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        def flash_pattern():
            while True:
                controller.led_index(0x7F, r, g, b)  # 0x7F = 0b1111111 = all 7 LEDs
                time.sleep(1)
                controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
                time.sleep(1)
        
        threading.Thread(target=flash_pattern, daemon=True).start()
        logger.info("Started flashing all LEDs with RGB(%d,%d,%d)", r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to flash all LEDs: %s", e)
        return False

def flash_led_all_time(r: int, g: int, b: int, time_seconds: int = 3) -> bool:
    """Flash all LEDs for specified seconds, then turn off."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        def flash_pattern():
            end_time = time.time() + time_seconds
            while time.time() < end_time:
                controller.led_index(0x7F, r, g, b)  # 0x7F = 0b1111111 = all 7 LEDs
                time.sleep(1)
                controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
                time.sleep(1)
            controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
        
        threading.Thread(target=flash_pattern, daemon=True).start()
        logger.info("Started flashing all LEDs with RGB(%d,%d,%d) for %d seconds", r, g, b, time_seconds)
        return True
    except Exception as e:
        logger.error("Failed to flash all LEDs with time: %s", e)
        return False

# === GLOW LED FUNCTIONS ===

def glow_single_led(led_index: int, r: int, g: int, b: int) -> bool:
    """Glow a specific LED: fades in and out continuously until stopped."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        # Stop any existing pattern
        _led_manager.stop_current_pattern()
        
        def glow_pattern():
            while not _led_manager.should_stop():
                # Fade in
                for intensity in range(0, 256, 5):
                    if _led_manager.should_stop():
                        break
                    controller.led_index(1 << (led_index - 1), 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)  # 50 steps per second
                
                if _led_manager.should_stop():
                    break
                    
                # Fade out
                for intensity in range(255, -1, -5):
                    if _led_manager.should_stop():
                        break
                    controller.led_index(1 << (led_index - 1), 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)  # 50 steps per second
        
        _led_manager.start_pattern(glow_pattern)
        logger.info("Started glowing LED %d with RGB(%d,%d,%d)", led_index, r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to glow single LED: %s", e)
        return False

def glow_single_led_time(led_index: int, r: int, g: int, b: int, time_seconds: int = 3) -> bool:
    """Glow a specific LED for specified seconds, then turn off."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        def glow_pattern():
            end_time = time.time() + time_seconds
            while time.time() < end_time:
                # Fade in
                for intensity in range(0, 256, 5):
                    if time.time() >= end_time:
                        break
                    controller.led_index(1 << (led_index - 1), 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)
                
                # Fade out
                for intensity in range(255, -1, -5):
                    if time.time() >= end_time:
                        break
                    controller.led_index(1 << (led_index - 1), 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)
            
            controller.led_index(1 << (led_index - 1), 0, 0, 0)
        
        threading.Thread(target=glow_pattern, daemon=True).start()
        logger.info("Started glowing LED %d with RGB(%d,%d,%d) for %d seconds", led_index, r, g, b, time_seconds)
        return True
    except Exception as e:
        logger.error("Failed to glow single LED with time: %s", e)
        return False

def glow_all_leds(r: int, g: int, b: int) -> bool:
    """Glow all LEDs: fades in and out continuously until stopped."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        # Stop any existing pattern
        _led_manager.stop_current_pattern()
        
        def glow_pattern():
            while not _led_manager.should_stop():
                # Fade in
                for intensity in range(0, 256, 5):
                    if _led_manager.should_stop():
                        break
                    controller.led_index(0x7F, 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)  # 50 steps per second
                
                if _led_manager.should_stop():
                    break
                    
                # Fade out
                for intensity in range(255, -1, -5):
                    if _led_manager.should_stop():
                        break
                    controller.led_index(0x7F, 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)  # 50 steps per second
        
        _led_manager.start_pattern(glow_pattern)
        logger.info("Started glowing all LEDs with RGB(%d,%d,%d)", r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to glow all LEDs: %s", e)
        return False

def glow_all_leds_time(r: int, g: int, b: int, time_seconds: int = 3) -> bool:
    """Glow all LEDs for specified seconds, then turn off."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        def glow_pattern():
            end_time = time.time() + time_seconds
            while time.time() < end_time:
                # Fade in
                for intensity in range(0, 256, 5):
                    if time.time() >= end_time:
                        break
                    controller.led_index(0x7F, 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)
                
                # Fade out
                for intensity in range(255, -1, -5):
                    if time.time() >= end_time:
                        break
                    controller.led_index(0x7F, 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)
            
            controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
        
        threading.Thread(target=glow_pattern, daemon=True).start()
        logger.info("Started glowing all LEDs with RGB(%d,%d,%d) for %d seconds", r, g, b, time_seconds)
        return True
    except Exception as e:
        logger.error("Failed to glow all LEDs with time: %s", e)
        return False

# === BLINK LED FUNCTIONS ===

def blink_single_led(led_index: int, r: int, g: int, b: int) -> bool:
    """Blink a specific LED: 1 second on, then off."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        def blink_pattern():
            controller.led_index(1 << (led_index - 1), r, g, b)
            time.sleep(1)
            controller.led_index(1 << (led_index - 1), 0, 0, 0)
        
        threading.Thread(target=blink_pattern, daemon=True).start()
        logger.info("Started blinking LED %d with RGB(%d,%d,%d)", led_index, r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to blink single LED: %s", e)
        return False

def blink_all_led(r: int, g: int, b: int) -> bool:
    """Blink all LEDs: 1 second on, then off."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        def blink_pattern():
            controller.led_index(0x7F, r, g, b)  # 0x7F = 0b1111111 = all 7 LEDs
            time.sleep(1)
            controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
        
        threading.Thread(target=blink_pattern, daemon=True).start()
        logger.info("Started blinking all LEDs with RGB(%d,%d,%d)", r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to blink all LEDs: %s", e)
        return False

# === UTILITY FUNCTIONS ===

def turn_off_all_leds() -> bool:
    """Turn off all LEDs."""
    try:
        controller = _led_manager.get_controller()
        if not controller:
            logger.error("LED controller not initialized")
            return False
        
        # Stop any running patterns first
        _led_manager.stop_current_pattern()
        
        controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
        logger.info("Turned off all LEDs")
        return True
    except Exception as e:
        logger.error("Failed to turn off all LEDs: %s", e)
        return False

def language_switch_feedback() -> bool:
    """Provide LED feedback for language switching: red glow."""
    return glow_all_leds_time(255, 0, 0, 2)  # Red glow for 2 seconds

def language_switch_complete() -> bool:
    """Complete language switching feedback: blue blink."""
    return blink_all_led(0, 0, 255)  # Blue blink

def server_ready_feedback() -> bool:
    """Provide LED feedback for server ready: green blink."""
    return blink_all_led(0, 255, 0)  # Green blink