import threading
import time
import logging
from robot_routines import (
    sonic_monitor_loop, shutdown_sequence
)
from command_dispatcher_symbolic import execute_symbolic
from command_dispatcher_logic import dispatch_command
from constants_commands import COMMAND as cmd

logger = logging.getLogger("voice")

class VoiceCommandHandler:
    def __init__(self, command_sender, ultrasonic_sensor, robot_state):
        self.command_sender = command_sender
        self.ultrasonic_sensor = ultrasonic_sensor
        self.robot_state = robot_state
        self.sonic_thread = None
        self.motion_thread = None

    def handle_command(self, spoken, command):

        # Multi-command routines (e.g., compound raw CMD_ strings)
        if isinstance(command, list):
            logger.info("Executing multi-command sequence: %s", command)
            for c in command:
                self.command_sender(c.split("#"))
                time.sleep(0.6)
            self.command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
            return

        # Route all other commands through the command dispatcher
        logger.info("Routing command through dispatcher: %s", command)
        dispatch_command("voice", command)