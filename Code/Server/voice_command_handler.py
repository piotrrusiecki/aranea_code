import threading
import time
from robot_routines import (
    march_forward, march_left, march_right, march_back,
    run_forward, run_left, run_right, run_back,
    sonic_monitor_loop, shutdown_sequence
)
from command import COMMAND as cmd

class VoiceCommandHandler:
    def __init__(self, command_sender, ultrasonic_sensor, robot_state):
        self.command_sender = command_sender
        self.ultrasonic_sensor = ultrasonic_sensor
        self.robot_state = robot_state
        self.sonic_thread = None
        self.motion_thread = None

    def handle_command(self, spoken, command):
        if command == "START_SONIC_MODE":
            if not self.robot_state.get_flag('sonic_state'):
                print("Starting sonic mode...")
                self.robot_state.set_flag('sonic_state', True)
                self.sonic_thread = threading.Thread(
                    target=sonic_monitor_loop,
                    args=(self.command_sender, self.ultrasonic_sensor, lambda: self.robot_state.get_flag('sonic_state')),
                    daemon=True
                )
                self.sonic_thread.start()
            return

        if command == "STOP_SONIC_MODE":
            if self.robot_state.get_flag('sonic_state'):
                print("Stopping sonic mode.")
                self.robot_state.set_flag('sonic_state', False)
            return

        if command == "STOP_MOTION_LOOP":
            if self.robot_state.get_flag('motion_state'):
                print("Stopping motion loop.")
                self.robot_state.set_flag('motion_state', False)
                self.command_sender([cmd.CMD_HEAD, "1", "90"])
                self.command_sender([cmd.CMD_LED, "0", "0", "0"])
                self.command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
            return

        # March commands
        if command in {"START_MARCH", "START_MARCH_LEFT", "START_MARCH_RIGHT", "START_MARCH_BACK"}:
            if not self.robot_state.get_flag('motion_state'):
                print("Starting march")
                self.robot_state.set_flag('motion_state', True)
                march_map = {
                    "START_MARCH": march_forward,
                    "START_MARCH_LEFT": march_left,
                    "START_MARCH_RIGHT": march_right,
                    "START_MARCH_BACK": march_back,
                }
                routine = march_map[command]
                self.motion_thread = threading.Thread(
                    target=routine,
                    args=(self.command_sender, self.ultrasonic_sensor, lambda: self.robot_state.get_flag('motion_state')),
                    daemon=True
                )
                self.motion_thread.start()
            return

        # Run commands
        if command in {"START_RUN", "START_RUN_LEFT", "START_RUN_RIGHT", "START_RUN_BACK"}:
            if not self.robot_state.get_flag('motion_state'):
                print("Starting run")
                self.robot_state.set_flag('motion_state', True)
                run_map = {
                    "START_RUN": run_forward,
                    "START_RUN_LEFT": run_left,
                    "START_RUN_RIGHT": run_right,
                    "START_RUN_BACK": run_back,
                }
                routine = run_map[command]
                self.motion_thread = threading.Thread(
                    target=routine,
                    args=(self.command_sender, self.ultrasonic_sensor, lambda: self.robot_state.get_flag('motion_state')),
                    daemon=True
                )
                self.motion_thread.start()
            return

        # Multi-command routines (sequences)
        if isinstance(command, list):
            for c in command:
                self.command_sender(c.split("#"))
                time.sleep(0.6)
            self.command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
        else:
            self.command_sender(command.split("#"))
            if command.startswith(cmd.CMD_MOVE):
                time.sleep(0.6)
                self.command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
