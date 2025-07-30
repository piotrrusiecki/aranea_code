import threading
import time
import logging
from robot_routines import (
    sonic_monitor_loop, shutdown_sequence
)
from command_dispatcher_symbolic import execute_symbolic
from command import COMMAND as cmd

logger = logging.getLogger("voice")


class VoiceCommandHandler:
    def __init__(self, command_sender, ultrasonic_sensor, robot_state):
        self.command_sender = command_sender
        self.ultrasonic_sensor = ultrasonic_sensor
        self.robot_state = robot_state
        self.sonic_thread = None
        self.motion_thread = None

    def handle_command(self, spoken, command):
        if command == "START_SONIC_MODE":
            if not self.robot_state.get_flag("sonic_state"):
                logger.info("Starting sonic mode.")
                self.robot_state.set_flag("sonic_state", True)
                self.sonic_thread = threading.Thread(
                    target=sonic_monitor_loop,
                    args=(self.command_sender, self.ultrasonic_sensor, lambda: self.robot_state.get_flag("sonic_state")),
                    daemon=True
                )
                self.sonic_thread.start()
            return

        if command == "STOP_SONIC_MODE":
            if self.robot_state.get_flag("sonic_state"):
                logger.info("Stopping sonic mode.")
                self.robot_state.set_flag("sonic_state", False)
            return

        if command == "STOP_MOTION_LOOP":
            if self.robot_state.get_flag("motion_state"):
                logger.info("Stopping motion loop.")
                self.robot_state.set_flag("motion_state", False)
                self.command_sender([cmd.CMD_HEAD, "1", "90"])
                self.command_sender([cmd.CMD_LED, "0", "0", "0"])
                self.command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
            return

        # START_MARCH and START_RUN commands using symbolic dispatcher
        symbolic_map = {
            "START_MARCH": "routine_march_forward",
            "START_MARCH_LEFT": "routine_march_left",
            "START_MARCH_RIGHT": "routine_march_right",
            "START_MARCH_BACK": "routine_march_back",
            "START_RUN": "routine_run_forward",
            "START_RUN_LEFT": "routine_run_left",
            "START_RUN_RIGHT": "routine_run_right",
            "START_RUN_BACK": "routine_run_back",
        }

        if command in symbolic_map:
            if not self.robot_state.get_flag("motion_state"):
                logger.info("Starting movement: %s", command)
                self.robot_state.set_flag("motion_state", True)

                symbolic_name = symbolic_map[command]

                def run_if_active():
                    if self.robot_state.get_flag("motion_state"):
                        execute_symbolic(symbolic_name)
                    else:
                        logger.info("Motion blocked: motion_state is False")

                self.motion_thread = threading.Thread(
                    target=run_if_active,
                    daemon=True
                )
                self.motion_thread.start()
            return

        # Multi-command routines (e.g., compound raw CMD_ strings)
        if isinstance(command, list):
            logger.info("Executing multi-command sequence: %s", command)
            for c in command:
                self.command_sender(c.split("#"))
                time.sleep(0.6)
            self.command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
            return

        # Default: single raw CMD string
        logger.info("Handling command: %s", command)
        self.command_sender(command.split("#"))
        if command.startswith(cmd.CMD_MOVE):
            time.sleep(0.6)
            self.command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])