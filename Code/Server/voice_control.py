import queue
import json
import threading
import time
import difflib
import sounddevice as sd
from vosk import Model, KaldiRecognizer

from config.voice import command_map, model_path, samplerate, blocksize
from voice_command_handler import VoiceCommandHandler

class VoiceControl:
    def __init__(self, command_sender, ultrasonic_sensor, robot_state):
        self.command_sender = command_sender
        self.ultrasonic_sensor = ultrasonic_sensor
        self.robot_state = robot_state
        self.queue = queue.Queue()
        self.recognizer = KaldiRecognizer(Model(model_path), samplerate)
        self.running = False
        self.command_handler = VoiceCommandHandler(command_sender, ultrasonic_sensor, robot_state)

    def _callback(self, indata, frames, time_info, status):
        if status:
            print("Audio status:", status)
        self.queue.put(bytes(indata))

    def stop(self):
        self.running = False

    def start(self):
        self.running = True
        try:
            with sd.RawInputStream(
                samplerate=samplerate,
                blocksize=blocksize,
                dtype="int16",
                channels=1,
                device=1,
                callback=self._callback
            ):
                print("Voice control listening... Press Ctrl+C to stop.")
                while self.running:
                    data = self.queue.get()
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        spoken = result.get("text", "").strip()
                        if not spoken:
                            continue

                        if spoken in command_map:
                            command = command_map[spoken]
                            print(f"Exact match: '{spoken}' -> {command}")
                        else:
                            match = difflib.get_close_matches(spoken, command_map.keys(), n=1, cutoff=0.6)
                            if match:
                                spoken = match[0]
                                command = command_map[spoken]
                                print(f"Fuzzy match: '{spoken}' -> {command}")
                            else:
                                print(f"No match for: '{spoken}'")
                                continue

                        self.command_handler.handle_command(spoken, command)
        except KeyboardInterrupt:
            print("Ctrl+C received. Shutting down voice control.")
            from robot_routines import shutdown_sequence
            shutdown_sequence(self.command_sender)