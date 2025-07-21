import threading
from voice_control import VoiceControl

voice = None
voice_thread = None
voice_active = False

def start_voice(process_command, ultrasonic_sensor):
    global voice, voice_thread, voice_active
    if not voice_active:
        voice = VoiceControl(process_command, ultrasonic_sensor)
        voice_thread = threading.Thread(target=voice.start, daemon=True)
        voice_thread.start()
        voice_active = True
        print("Voice control started.")

def stop_voice():
    global voice, voice_active
    if voice_active and voice:
        voice.stop()
        voice_active = False
        print("Voice control stopped.")
