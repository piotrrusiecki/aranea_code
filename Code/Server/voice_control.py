import queue
import json
import threading
import time
import difflib
import sounddevice as sd
from vosk import Model, KaldiRecognizer

from voice_config import command_map, model_path, samplerate, blocksize
from voice_runtime import (
    motion_mode, march_mode, sonic_mode,
    motion_loop, motion_loop_simple, march_loop, sonic_monitor_loop,
    set_runtime_interfaces
)

class VoiceControl:
    def __init__(self, command_sender, ultrasonic_sensor):
        self.command_sender = command_sender
        self.ultrasonic_sensor = ultrasonic_sensor
        self.queue = queue.Queue()
        self.recognizer = KaldiRecognizer(Model(model_path), samplerate)
        self.sonic_thread = None
        self.motion_thread = None
        self.running = False

        # Inject interfaces into runtime module
        set_runtime_interfaces(command_sender, ultrasonic_sensor)

    def _callback(self, indata, frames, time_info, status):
        if status:
            print("Audio status:", status)
        self.queue.put(bytes(indata))

    def stop(self):
        self.running = False

    def _handle_command(self, spoken, command):
        global motion_mode, march_mode, sonic_mode

        if command == "START_SONIC_MODE":
            if not sonic_mode:
                print("Starting sonic mode...")
                sonic_mode = True
                self.sonic_thread = threading.Thread(target=sonic_monitor_loop, daemon=True)
                self.sonic_thread.start()
            return

        elif command == "STOP_SONIC_MODE":
            if sonic_mode:
                print("Stopping sonic mode.")
                sonic_mode = False
            return

        elif command == "STOP_MARCH_MODE":
            if march_mode:
                print("Stopping march mode.")
                march_mode = False
            return

        if isinstance(command, str) and command in {
            "START_MARCH", "START_MARCH_LEFT", "START_MARCH_RIGHT"
        }:
            if not motion_mode:
                print("Starting march")
                motion_mode = True
                x, y, speed = 0, 35, 10
                angle = 90
                if "maldekstren" in spoken:
                    x, y, angle = -35, 0, 180
                elif "dekstren" in spoken:
                    x, y, angle = 35, 0, 0
                self.motion_thread = threading.Thread(
                    target=motion_loop, args=(2, x, y, speed, angle), daemon=True
                )
                self.motion_thread.start()
            return

        elif isinstance(command, str) and command in {
            "START_RUN", "START_RUN_LEFT", "START_RUN_RIGHT"
        }:
            if not motion_mode:
                print("Starting run")
                motion_mode = True
                x, y, speed = 0, 20, 10
                angle = 90
                if "maldekstren" in spoken:
                    x, y, angle = -20, 0, 180
                elif "dekstren" in spoken:
                    x, y, angle = 20, 0, 0
                self.motion_thread = threading.Thread(
                    target=motion_loop, args=(1, x, y, speed, angle), daemon=True
                )
                self.motion_thread.start()
            return

        elif command == "START_MARCH_BACK":
            if not motion_mode:
                print("Starting backward march")
                motion_mode = True
                self.motion_thread = threading.Thread(
                    target=motion_loop_simple, args=(2, 0, -35, 8, 90), daemon=True
                )
                self.motion_thread.start()
            return

        elif command == "START_RUN_BACK":
            if not motion_mode:
                print("Starting backward run")
                motion_mode = True
                self.motion_thread = threading.Thread(
                    target=motion_loop_simple, args=(1, 0, -35, 10, 90), daemon=True
                )
                self.motion_thread.start()
            return

        elif command == "STOP_MOTION_LOOP":
            if motion_mode:
                print("Stopping motion loop.")
                motion_mode = False
                self.command_sender(["CMD_HEAD", "1", "90"])
                self.command_sender(["CMD_LED", "0", "0", "0"])
                self.command_sender(["CMD_MOVE", "1", "0", "0", "8", "0"])
            return

        if isinstance(command, list):
            for c in command:
                self.command_sender(c.split("#"))
                time.sleep(0.6)
            self.command_sender(["CMD_MOVE", "1", "0", "0", "8", "0"])
        else:
            self.command_sender(command.split("#"))
            if command.startswith("CMD_MOVE"):
                time.sleep(0.6)
                self.command_sender(["CMD_MOVE", "1", "0", "0", "8", "0"])

    def start(self):
        self.running = True
        try:
            with sd.RawInputStream(
                samplerate=samplerate,
                blocksize=800,
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
                            print("Exact match: '{}' -> {}".format(spoken, command))
                        else:
                            match = difflib.get_close_matches(spoken, command_map.keys(), n=1, cutoff=0.6)
                            if match:
                                spoken = match[0]
                                command = command_map[spoken]
                                print("Fuzzy match: '{}' -> {}".format(spoken, command))
                            else:
                                print("No match for: '{}'".format(spoken))
                                continue

                        self._handle_command(spoken, command)

        except KeyboardInterrupt:
            print("Ctrl+C received. Shutting down voice control.")
            self.command_sender(["CMD_MOVE", "1", "0", "0", "8", "0"])
            self.command_sender(["CMD_SERVOPOWER", "0"])
            self.command_sender(["CMD_LED", "0", "0", "0"])
            self.command_sender(["CMD_HEAD", "1", "90"])
            self.command_sender(["CMD_HEAD", "0", "90"])