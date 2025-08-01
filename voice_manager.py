import threading
import logging
from voice_control import VoiceControl

logger = logging.getLogger("voice")


class VoiceManager:
    """Manages voice control lifecycle without global state."""
    
    def __init__(self):
        self.voice = None
        self.voice_thread = None
        self.voice_active = False
    
    def start_voice(self, process_command, ultrasonic_sensor, robot_state):
        """Start voice control if not already active."""
        if not self.voice_active:
            try:
                self.voice = VoiceControl(process_command, ultrasonic_sensor, robot_state)
                self.voice_thread = threading.Thread(target=self.voice.start, daemon=True)
                self.voice_thread.start()
                self.voice_active = True
                logger.info("Voice control started.")
            except Exception as e:
                logger.error("Failed to start voice control: %s", e)
    
    def stop_voice(self):
        """Stop voice control if active."""
        if self.voice_active and self.voice:
            try:
                self.voice.stop()
                self.voice_active = False
                logger.info("Voice control stopped.")
            except Exception as e:
                logger.error("Failed to stop voice control: %s", e)


# Global instance for backward compatibility
_voice_manager = VoiceManager()

def start_voice(process_command, ultrasonic_sensor, robot_state):
    """Legacy function wrapper for backward compatibility."""
    _voice_manager.start_voice(process_command, ultrasonic_sensor, robot_state)

def stop_voice():
    """Legacy function wrapper for backward compatibility."""
    _voice_manager.stop_voice()
