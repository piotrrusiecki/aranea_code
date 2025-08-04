# actuator_led_commands.py

"""
Centralized LED command handling for the Aranea robot.
Provides flexible, parameterized methods for different LED patterns and states.
"""

import time
import threading
import logging
from typing import Optional, Callable

logger = logging.getLogger("led.commands")

class LEDCommands:
    """Centralized LED command handling with flexible patterns."""
    
    def __init__(self, command_sender: Callable):
        """
        Initialize LED command handler.
        
        Args:
            command_sender: Function to send commands to hardware
        """
        self.command_sender = command_sender
        self._current_pattern = None
        self._pattern_thread = None
        self._stop_pattern = False
        
    def _send_led_command(self, r: int, g: int, b: int):
        """Send LED command to hardware."""
        try:
            self.command_sender(["CMD_LED", str(r), str(g), str(b)])
        except Exception as e:
            logger.error("Failed to send LED command [%d,%d,%d]: %s", r, g, b, e)
    
    def set_color(self, r: int, g: int, b: int):
        """
        Set LED to a specific color.
        
        Args:
            r: Red value (0-255)
            g: Green value (0-255) 
            b: Blue value (0-255)
        """
        self._stop_current_pattern()
        self._send_led_command(r, g, b)
    
    def turn_off(self):
        """Turn off LED."""
        self.set_color(0, 0, 0)
    
    def flash_color(self, r: int, g: int, b: int, duration: float = 0.5, times: int = 1):
        """
        Flash LED with a specific color.
        
        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
            duration: Duration of each flash in seconds
            times: Number of times to flash
        """
        def flash_pattern():
            for _ in range(times):
                if self._stop_pattern:
                    break
                self._send_led_command(r, g, b)
                time.sleep(duration)
                if self._stop_pattern:
                    break
                self._send_led_command(0, 0, 0)
                if _ < times - 1:  # Don't sleep after last flash
                    time.sleep(duration)
        
        self._run_pattern(flash_pattern, "flash_color(%d,%d,%d)" % (r, g, b))
    
    def glow_color(self, r: int, g: int, b: int, fade_duration: float = 1.0):
        """
        Start a glowing pattern with a specific color.
        
        Args:
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
                    self._send_led_command(
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
                    self._send_led_command(
                        int(r * intensity / 255),
                        int(g * intensity / 255),
                        int(b * intensity / 255)
                    )
                    time.sleep(fade_duration / 50)  # 50 steps per cycle
        
        self._run_pattern(glow_pattern, "glow_color(%d,%d,%d)" % (r, g, b))
    
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
            self._pattern_thread.join(timeout=1.0)
            pattern_name = self._current_pattern
            self._current_pattern = None
            logger.debug("Stopped LED pattern: %s", pattern_name)


# Convenience functions for common LED patterns
def server_ready_flash(led_commands: LEDCommands):
    """Quick green flash to indicate server is ready."""
    led_commands.flash_color(0, 255, 0, duration=0.3, times=2)
    logger.info("Server ready flash - green LED flashed")


def language_switching_glow(led_commands: LEDCommands):
    """Start red glow to indicate language switching in progress."""
    led_commands.glow_color(255, 0, 0, fade_duration=0.8)
    logger.info("Language switching started - red LED glow")


def language_ready_flash(led_commands: LEDCommands):
    """Blue flash to indicate language switching is complete."""
    led_commands.stop_pattern()  # Stop the red glow
    led_commands.flash_color(0, 0, 255, duration=0.4, times=1)
    logger.info("Language switching complete - blue LED flash")


# Global LED commands instance (will be initialized by main.py)
_led_commands: Optional[LEDCommands] = None

def init_led_commands(command_sender: Callable):
    """Initialize the global LED commands instance."""
    global _led_commands
    _led_commands = LEDCommands(command_sender)
    logger.info("LED commands initialized")


def get_led_commands() -> Optional[LEDCommands]:
    """Get the global LED commands instance."""
    return _led_commands 