import time
import logging
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

        # Handle language switching
        if isinstance(command, str) and command.startswith("language_"):
            lang_code = command.split("_")[1].lower()  # Convert to lowercase
            from voice_manager import _voice_manager
            _voice_manager.switch_language(lang_code)
            return

        # Multi-command routines
        if isinstance(command, list):
            logger.info("Executing multi-command sequence: %s", command)
            for c in command:
                self.command_sender(c.split("#"))
                time.sleep(0.6)
            self.command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
            return

        # Route other commands
        logger.info("Routing command through dispatcher: %s", command)
        dispatch_command("voice", command)
