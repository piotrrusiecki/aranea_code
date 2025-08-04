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
        self.command_sender = None
        self.ultrasonic_sensor = None
        self.robot_state = None
    
    def start_voice(self, process_command, ultrasonic_sensor, robot_state):
        """Start voice control if not already active."""
        if not self.voice_active:
            try:
                self.command_sender = process_command
                self.ultrasonic_sensor = ultrasonic_sensor
                self.robot_state = robot_state
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

    def switch_language(self, lang_code):
        """Switch to a different language and restart voice control."""
        if self.voice_active and self.voice and self.command_sender:
            try:
                logger.info("Switching voice language to: %s", lang_code)
                # Stop current voice control
                self.voice.stop()
                self.voice_active = False
                
                # Create new voice control with new language
                self.voice = VoiceControl(self.command_sender, self.ultrasonic_sensor, self.robot_state)
                self.voice.set_language(lang_code)
                
                # Start new voice control
                self.voice_thread = threading.Thread(target=self.voice.start, daemon=True)
                self.voice_thread.start()
                self.voice_active = True
                logger.info("Voice control restarted with language: %s", lang_code)
            except Exception as e:
                logger.error("Failed to switch language to '%s': %s", lang_code, e)


# Global instance for backward compatibility
_voice_manager = VoiceManager()

def start_voice(process_command, ultrasonic_sensor, robot_state):
    _voice_manager.start_voice(process_command, ultrasonic_sensor, robot_state)

def stop_voice():
    _voice_manager.stop_voice()

def switch_language(lang_code):
    _voice_manager.switch_language(lang_code)
