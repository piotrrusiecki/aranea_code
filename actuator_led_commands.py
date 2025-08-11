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

# Global LED controller instance
_led_controller = None

def init_led_commands(led_controller):
    """Initialize the LED commands with a controller."""
    global _led_controller
    _led_controller = led_controller
    logger.info("LED commands initialized with direct hardware control")

def get_led_commands():
    """Get the LED controller instance."""
    return _led_controller

# === SET LED FUNCTIONS ===

def set_single_led(led_index: int, r: int, g: int, b: int) -> bool:
    """Set a specific LED to a specific color, stays on until turned off."""
    try:
        if _led_controller is None:
            logger.error("LED controller not initialized")
            return False
        
        assert _led_controller is not None  # Type checker hint
        _led_controller.led_index(1 << (led_index - 1), r, g, b)  # type: ignore
        logger.info("Set LED %d to RGB(%d,%d,%d)", led_index, r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to set single LED: %s", e)
        return False

def set_single_led_time(led_index: int, r: int, g: int, b: int, time_seconds: int = 3) -> bool:
    """Set a specific LED to a specific color for specified seconds, then turn off."""
    try:
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        _led_controller.led_index(1 << (led_index - 1), r, g, b)
        logger.info("Set LED %d to RGB(%d,%d,%d) for %d seconds", led_index, r, g, b, time_seconds)
        
        # Turn off after specified time
        def turn_off_after_time():
            time.sleep(time_seconds)
            _led_controller.led_index(1 << (led_index - 1), 0, 0, 0)
            logger.info("Turned off LED %d after %d seconds", led_index, time_seconds)
        
        threading.Thread(target=turn_off_after_time, daemon=True).start()
        return True
    except Exception as e:
        logger.error("Failed to set single LED with time: %s", e)
        return False

def set_all_led(r: int, g: int, b: int) -> bool:
    """Set all LEDs to a specific color, stays on until turned off."""
    try:
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        _led_controller.led_index(0x7F, r, g, b)  # 0x7F = 0b1111111 = all 7 LEDs
        logger.info("Set all LEDs to RGB(%d,%d,%d)", r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to set all LEDs: %s", e)
        return False

def set_all_led_time(r: int, g: int, b: int, time_seconds: int = 3) -> bool:
    """Set all LEDs to a specific color for specified seconds, then turn off."""
    try:
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        _led_controller.led_index(0x7F, r, g, b)  # 0x7F = 0b1111111 = all 7 LEDs
        logger.info("Set all LEDs to RGB(%d,%d,%d) for %d seconds", r, g, b, time_seconds)
        
        # Turn off after specified time
        def turn_off_after_time():
            time.sleep(time_seconds)
            _led_controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
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
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        def flash_pattern():
            while True:
                _led_controller.led_index(1 << (led_index - 1), r, g, b)
                time.sleep(1)
                _led_controller.led_index(1 << (led_index - 1), 0, 0, 0)
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
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        def flash_pattern():
            end_time = time.time() + time_seconds
            while time.time() < end_time:
                _led_controller.led_index(1 << (led_index - 1), r, g, b)
                time.sleep(1)
                _led_controller.led_index(1 << (led_index - 1), 0, 0, 0)
                time.sleep(1)
            _led_controller.led_index(1 << (led_index - 1), 0, 0, 0)
        
        threading.Thread(target=flash_pattern, daemon=True).start()
        logger.info("Started flashing LED %d with RGB(%d,%d,%d) for %d seconds", led_index, r, g, b, time_seconds)
        return True
    except Exception as e:
        logger.error("Failed to flash single LED with time: %s", e)
        return False

def flash_led_all(r: int, g: int, b: int) -> bool:
    """Flash all LEDs: 1 second on, 1 second off, continues until stopped."""
    try:
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        def flash_pattern():
            while True:
                _led_controller.led_index(0x7F, r, g, b)  # 0x7F = 0b1111111 = all 7 LEDs
                time.sleep(1)
                _led_controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
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
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        def flash_pattern():
            end_time = time.time() + time_seconds
            while time.time() < end_time:
                _led_controller.led_index(0x7F, r, g, b)  # 0x7F = 0b1111111 = all 7 LEDs
                time.sleep(1)
                _led_controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
                time.sleep(1)
            _led_controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
        
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
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        def glow_pattern():
            while True:
                # Fade in
                for intensity in range(0, 256, 5):
                    _led_controller.led_index(1 << (led_index - 1), 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)  # 50 steps per second
                
                # Fade out
                for intensity in range(255, -1, -5):
                    _led_controller.led_index(1 << (led_index - 1), 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)  # 50 steps per second
        
        threading.Thread(target=glow_pattern, daemon=True).start()
        logger.info("Started glowing LED %d with RGB(%d,%d,%d)", led_index, r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to glow single LED: %s", e)
        return False

def glow_single_led_time(led_index: int, r: int, g: int, b: int, time_seconds: int = 3) -> bool:
    """Glow a specific LED for specified seconds, then turn off."""
    try:
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        def glow_pattern():
            end_time = time.time() + time_seconds
            while time.time() < end_time:
                # Fade in
                for intensity in range(0, 256, 5):
                    if time.time() >= end_time:
                        break
                    _led_controller.led_index(1 << (led_index - 1), 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)
                
                # Fade out
                for intensity in range(255, -1, -5):
                    if time.time() >= end_time:
                        break
                    _led_controller.led_index(1 << (led_index - 1), 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)
            
            _led_controller.led_index(1 << (led_index - 1), 0, 0, 0)
        
        threading.Thread(target=glow_pattern, daemon=True).start()
        logger.info("Started glowing LED %d with RGB(%d,%d,%d) for %d seconds", led_index, r, g, b, time_seconds)
        return True
    except Exception as e:
        logger.error("Failed to glow single LED with time: %s", e)
        return False

def glow_all_leds(r: int, g: int, b: int) -> bool:
    """Glow all LEDs: fades in and out continuously until stopped."""
    try:
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        def glow_pattern():
            while True:
                # Fade in
                for intensity in range(0, 256, 5):
                    _led_controller.led_index(0x7F, 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)  # 50 steps per second
                
                # Fade out
                for intensity in range(255, -1, -5):
                    _led_controller.led_index(0x7F, 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)  # 50 steps per second
        
        threading.Thread(target=glow_pattern, daemon=True).start()
        logger.info("Started glowing all LEDs with RGB(%d,%d,%d)", r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to glow all LEDs: %s", e)
        return False

def glow_all_leds_time(r: int, g: int, b: int, time_seconds: int = 3) -> bool:
    """Glow all LEDs for specified seconds, then turn off."""
    try:
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        def glow_pattern():
            end_time = time.time() + time_seconds
            while time.time() < end_time:
                # Fade in
                for intensity in range(0, 256, 5):
                    if time.time() >= end_time:
                        break
                    _led_controller.led_index(0x7F, 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)
                
                # Fade out
                for intensity in range(255, -1, -5):
                    if time.time() >= end_time:
                        break
                    _led_controller.led_index(0x7F, 
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255))
                    time.sleep(0.02)
            
            _led_controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
        
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
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        def blink_pattern():
            _led_controller.led_index(1 << (led_index - 1), r, g, b)
            time.sleep(1)
            _led_controller.led_index(1 << (led_index - 1), 0, 0, 0)
        
        threading.Thread(target=blink_pattern, daemon=True).start()
        logger.info("Started blinking LED %d with RGB(%d,%d,%d)", led_index, r, g, b)
        return True
    except Exception as e:
        logger.error("Failed to blink single LED: %s", e)
        return False

def blink_all_led(r: int, g: int, b: int) -> bool:
    """Blink all LEDs: 1 second on, then off."""
    try:
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        def blink_pattern():
            _led_controller.led_index(0x7F, r, g, b)  # 0x7F = 0b1111111 = all 7 LEDs
            time.sleep(1)
            _led_controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
        
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
        if not _led_controller:
            logger.error("LED controller not initialized")
            return False
        
        _led_controller.led_index(0x7F, 0, 0, 0)  # 0x7F = 0b1111111 = all 7 LEDs
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