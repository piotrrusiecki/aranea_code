# actuator_led_commands.py

"""
Centralized LED command handling for the Aranea robot.
Provides flexible, parameterized methods for different LED patterns and states.
Uses direct hardware calls instead of CMD_LED for better control.
"""

import time
import threading
import logging
from typing import Optional, Callable, List

logger = logging.getLogger("led.commands")

class LEDCommands:
    """Centralized LED command handling with flexible patterns."""
    
    def __init__(self, led_controller):
        """
        Initialize LED command handler.
        
        Args:
            led_controller: LED hardware controller instance (from actuator_led.py)
        """
        self.led_controller = led_controller
        self._current_pattern = None
        self._pattern_thread = None
        self._stop_pattern = False
        
    def _set_led_color(self, led_index: int, r: int, g: int, b: int):
        """Set a specific LED to a color."""
        try:
            if hasattr(self.led_controller, 'strip'):
                self.led_controller.strip.set_led_color(led_index, r, g, b)
            else:
                logger.warning("LED controller has no strip attribute - hardware not available")
        except Exception as e:
            logger.warning("Failed to set LED %d to color [%d,%d,%d]: %s (hardware may not be available)", led_index, r, g, b, e)
    
    def _set_all_leds_color(self, r: int, g: int, b: int):
        """Set all LEDs to the same color."""
        try:
            if hasattr(self.led_controller, 'strip'):
                self.led_controller.strip.set_all_led_color(r, g, b)
            else:
                logger.warning("LED controller has no strip attribute - hardware not available")
        except Exception as e:
            logger.warning("Failed to set all LEDs to color [%d,%d,%d]: %s (hardware may not be available)", r, g, b, e)
    
    def set_led_color(self, led_indices: List[int], r: int, g: int, b: int):
        """
        Set specific LEDs to a color.
        
        Args:
            led_indices: List of LED indices (0-6 for 7 LEDs)
            r: Red value (0-255)
            g: Green value (0-255) 
            b: Blue value (0-255)
        """
        self._stop_current_pattern()
        
        if not led_indices:
            logger.warning("No LED indices provided")
            return
            
        # Convert 1-based indices to 0-based
        zero_based_indices = [idx - 1 for idx in led_indices if 1 <= idx <= 7]
        
        if not zero_based_indices:
            logger.warning("No valid LED indices in range 1-7")
            return
            
        # If all LEDs are selected, use the more efficient all-LED method
        if len(zero_based_indices) == 7:
            self._set_all_leds_color(r, g, b)
        else:
            # Set individual LEDs
            for led_idx in zero_based_indices:
                self._set_led_color(led_idx, r, g, b)
        
        logger.info("Set LEDs %s to color RGB(%d,%d,%d)", led_indices, r, g, b)
    
    def turn_off(self, led_indices: Optional[List[int]] = None):
        """
        Turn off specific LEDs or all LEDs.
        
        Args:
            led_indices: List of LED indices (1-7) or None for all LEDs
        """
        if led_indices is None:
            self._stop_current_pattern()
            self._set_all_leds_color(0, 0, 0)
            logger.info("Turned off all LEDs")
        else:
            self.set_led_color(led_indices, 0, 0, 0)
    
    def flash_color(self, led_indices: List[int], r: int, g: int, b: int, duration: float = 0.5, times: int = 1):
        """
        Flash specific LEDs with a color.
        
        Args:
            led_indices: List of LED indices (1-7)
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
            duration: Duration of each flash in seconds
            times: Number of times to flash (0 for continuous)
        """
        def flash_pattern():
            flash_count = 0
            while not self._stop_pattern and (times == 0 or flash_count < times):
                # Turn on
                self.set_led_color(led_indices, r, g, b)
                time.sleep(duration)
                
                if self._stop_pattern:
                    break
                    
                # Turn off
                self.set_led_color(led_indices, 0, 0, 0)
                if times == 0 or flash_count < times - 1:  # Don't sleep after last flash
                    time.sleep(duration)
                
                flash_count += 1
        
        self._run_pattern(flash_pattern, f"flash_color({led_indices},{r},{g},{b})")
    
    def glow_color(self, led_indices: List[int], r: int, g: int, b: int, fade_duration: float = 1.0):
        """
        Start a glowing pattern for specific LEDs.
        
        Args:
            led_indices: List of LED indices (1-7)
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
            fade_duration: Duration of fade cycle in seconds
        """
        def glow_pattern():
            while not self._stop_pattern:
                # Fade in
                for intensity in range(0, 256, 5):
                    if self._stop_pattern:
                        break
                    self.set_led_color(
                        led_indices,
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255)
                    )
                    time.sleep(fade_duration / 50)  # 50 steps per cycle
                
                if self._stop_pattern:
                    break
                    
                # Fade out
                for intensity in range(255, -1, -5):
                    if self._stop_pattern:
                        break
                    self.set_led_color(
                        led_indices,
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255)
                    )
                    time.sleep(fade_duration / 50)  # 50 steps per cycle
        
        self._run_pattern(glow_pattern, f"glow_color({led_indices},{r},{g},{b})")
    
    def stop_pattern(self):
        """Stop any currently running LED pattern."""
        self._stop_current_pattern()
    
    def _run_pattern(self, pattern_func: Callable, pattern_name: str):
        """Run a LED pattern in a separate thread."""
        self._stop_current_pattern()
        self._current_pattern = pattern_name
        self._stop_pattern = False
        self._pattern_thread = threading.Thread(target=pattern_func, daemon=True)
        self._pattern_thread.start()
    
    def _stop_current_pattern(self):
        """Stop the currently running LED pattern."""
        if self._pattern_thread and self._pattern_thread.is_alive():
            self._stop_pattern = True
            # Don't try to join the current thread
            if self._pattern_thread != threading.current_thread():
                self._pattern_thread.join(timeout=1.0)
            pattern_name = self._current_pattern
            self._current_pattern = None
            logger.debug("Stopped LED pattern: %s", pattern_name)





class LEDCommandsManager:
    """Singleton class to manage LED commands instance."""
    _instance: Optional['LEDCommandsManager'] = None
    _led_commands: Optional[LEDCommands] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_led_commands(cls) -> Optional[LEDCommands]:
        """Get the LED commands instance."""
        return cls._led_commands
    
    @classmethod
    def set_led_commands(cls, led_commands: Optional[LEDCommands]) -> None:
        """Set the LED commands instance."""
        cls._led_commands = led_commands


def init_led_commands(led_controller):
    """Initialize the LED commands instance."""
    try:
        led_commands = LEDCommands(led_controller)
        LEDCommandsManager.set_led_commands(led_commands)
        logger.info("LED commands initialized with direct hardware control")
    except Exception as e:
        logger.warning("Failed to initialize LED commands: %s (hardware may not be available)", e)
        LEDCommandsManager.set_led_commands(None)


def get_led_commands() -> Optional[LEDCommands]:
    """Get the LED commands instance."""
    return LEDCommandsManager.get_led_commands() 


# Web Interface LED Control Functions
def set_led_static(led_indices: list, r: int, g: int, b: int) -> bool:
    """
    Set specific LEDs to a static color.
    
    Args:
        led_indices: List of LED indices (1-7)
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        led_commands = get_led_commands()
        if led_commands is None:
            logger.error("LED commands not initialized")
            return False
        
        led_commands.set_led_color(led_indices, r, g, b)
        logger.info(f"Set LEDs {led_indices} to static color RGB({r},{g},{b})")
        return True
    except Exception as e:
        logger.error(f"Failed to set LED static: {e}")
        return False


def set_led_glow(led_indices: list, r: int, g: int, b: int) -> bool:
    """
    Start a glowing pattern for specific LEDs.
    
    Args:
        led_indices: List of LED indices (1-7)
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        led_commands = get_led_commands()
        if led_commands is None:
            logger.error("LED commands not initialized")
            return False
        
        # Start glow pattern
        led_commands.glow_color(led_indices, r, g, b, fade_duration=1.0)
        logger.info(f"Started glow pattern for LEDs {led_indices} with color RGB({r},{g},{b})")
        return True
    except Exception as e:
        logger.error(f"Failed to set LED glow: {e}")
        return False


def set_led_flash(led_indices: list, r: int, g: int, b: int) -> bool:
    """
    Start a flashing pattern for specific LEDs.
    
    Args:
        led_indices: List of LED indices (1-7)
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        led_commands = get_led_commands()
        if led_commands is None:
            logger.error("LED commands not initialized")
            return False
        
        # Start flash pattern (1 second intervals as specified)
        led_commands.flash_color(led_indices, r, g, b, duration=1.0, times=0)  # 0 means continuous
        logger.info(f"Started flash pattern for LEDs {led_indices} with color RGB({r},{g},{b})")
        return True
    except Exception as e:
        logger.error(f"Failed to set LED flash: {e}")
        return False


def turn_off_all_leds() -> bool:
    """
    Turn off all LEDs.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        led_commands = get_led_commands()
        if led_commands is None:
            logger.error("LED commands not initialized")
            return False
        
        led_commands.turn_off()
        logger.info("All LEDs turned off")
        return True
    except Exception as e:
        logger.error("Failed to turn off all LEDs: %s", e)
        return False


def language_switch_feedback() -> bool:
    """
    Provide LED feedback for language switching: red glow then blue blink.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        led_commands = get_led_commands()
        if led_commands is None:
            logger.error("LED commands not initialized")
            return False
        
        # Start red glow to indicate language switching
        led_commands.glow_color([1, 2, 3, 4, 5, 6, 7], 255, 0, 0, fade_duration=0.8)
        logger.debug("Started red glow for language switching")
        return True
    except Exception as e:
        logger.error("Failed to start language switch feedback: %s", e)
        return False


def language_switch_complete() -> bool:
    """
    Complete language switching feedback: stop red glow and do blue blink.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        led_commands = get_led_commands()
        if led_commands is None:
            logger.error("LED commands not initialized")
            return False
        
        # Stop red glow and do blue blink
        led_commands.stop_pattern()  # Stop the red glow
        led_commands.flash_color([1, 2, 3, 4, 5, 6, 7], 0, 0, 255, duration=0.4, times=1)
        logger.debug("Completed language switch feedback with blue blink")
        return True
    except Exception as e:
        logger.error("Failed to complete language switch feedback: %s", e)
        return False


def server_ready_feedback() -> bool:
    """
    Provide LED feedback for server ready: green blink.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        led_commands = get_led_commands()
        if led_commands is None:
            logger.error("LED commands not initialized")
            return False
        
        # Green blink to indicate server is ready
        led_commands.flash_color([1, 2, 3, 4, 5, 6, 7], 0, 255, 0, duration=0.3, times=2)
        logger.debug("Server ready feedback: green blink")
        return True
    except Exception as e:
        logger.error("Failed to provide server ready feedback: %s", e)
        return False