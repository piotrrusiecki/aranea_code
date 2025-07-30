import threading
import logging
from voice_control import VoiceControl

logger = logging.getLogger("voice")

voice = None
voice_thread = None
voice_active = False

def start_voice(process_command, ultrasonic_sensor, robot_state):
    global voice, voice_thread, voice_active
    if not voice_active:
        try:
            voice = VoiceControl(process_command, ultrasonic_sensor, robot_state)
            voice_thread = threading.Thread(target=voice.start, daemon=True)
            voice_thread.start()
            voice_active = True
            logger.info("Voice control started.")
        except Exception as e:
            logger.error("Failed to start voice control: %s", e)

def stop_voice():
    global voice_active
    if voice_active and voice:
        try:
            voice.stop()
            voice_active = False
            logger.info("Voice control stopped.")
        except Exception as e:
            logger.error("Failed to stop voice control: %s", e)
