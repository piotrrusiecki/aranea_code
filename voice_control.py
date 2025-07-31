import queue
import json
import threading
import time
import difflib
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import logging

from config.voice import command_map
from config.robot_config import VOICE_LANG, VOICE_MODELS, VOICE_SAMPLERATE, VOICE_BLOCKSIZE, VOICE_INPUT_DEVICE
from voice_command_handler import VoiceCommandHandler

logger = logging.getLogger("voice")

class VoiceControl:
    def __init__(self, command_sender, ultrasonic_sensor, robot_state):
        self.command_sender = command_sender
        self.ultrasonic_sensor = ultrasonic_sensor
        self.robot_state = robot_state
        self.queue = queue.Queue()
        self.running = False
        self.command_handler = VoiceCommandHandler(command_sender, ultrasonic_sensor, robot_state)

        # Load model from VOICE_MODELS based on VOICE_LANG
        self.current_lang = VOICE_LANG
        model_path = VOICE_MODELS.get(self.current_lang)

        if not model_path:
            raise ValueError(f"No model path defined for language: {self.current_lang}")

        logger.info("Loading Vosk model for '%s' from: %s", self.current_lang, model_path)
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, VOICE_SAMPLERATE)

    def _callback(self, indata, frames, time_info, status):
        if status:
            # Filter out routine "input overflow" messages to reduce log spam
            if "input overflow" not in str(status).lower():
                logger.warning("Audio status: %s", status)
            # Note: input overflow is common and usually not critical
        self.queue.put(bytes(indata))

    def stop(self):
        self.running = False

    def start(self):
        self.running = True
        try:
            with sd.RawInputStream(
                samplerate=VOICE_SAMPLERATE,
                blocksize=VOICE_BLOCKSIZE,
                dtype="int16",
                channels=1,
                device=VOICE_INPUT_DEVICE,
                callback=self._callback
            ):
                logger.info("Voice control listening... Press Ctrl+C to stop.")
                while self.running:
                    data = self.queue.get()
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        spoken = result.get("text", "").strip()
                        if not spoken:
                            continue

                        if spoken in command_map:
                            command = command_map[spoken]
                            logger.info("Exact match: '%s' -> %s", spoken, command)
                        else:
                            match = difflib.get_close_matches(spoken, command_map.keys(), n=1, cutoff=0.6)
                            if match:
                                spoken = match[0]
                                command = command_map[spoken]
                                logger.info("Fuzzy match: '%s' -> %s", spoken, command)
                            else:
                                logger.info("No match for: '%s'", spoken)
                                continue

                        self.command_handler.handle_command(spoken, command)
        except KeyboardInterrupt:
            logger.info("Ctrl+C received. Shutting down voice control.")
            from robot_routines import shutdown_sequence
            shutdown_sequence(self.command_sender)
