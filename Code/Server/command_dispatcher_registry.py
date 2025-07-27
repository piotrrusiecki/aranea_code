# command_dispatcher_registry.py

"""
Registers all symbolic and routine commands into the dispatcher registry.

This is the only file that should import routines or patrol modules directly.
It updates the registries defined in command_dispatcher_core.py.
"""

import logging
from command_dispatcher_core import symbolic_commands, routine_commands, server_instance
from command_dispatcher_utils import send_str
from command import COMMAND as cmd

from robot_routines import (
    routine_march_forward,
    routine_march_left,
    routine_march_right,
    routine_march_back,
    routine_run_forward,
    routine_run_left,
    routine_run_right,
    routine_run_back,
    routine_turn_left,
    routine_turn_right,
    sys_prep_calibration,
    sys_exit_calibration
)
from robot_patrol import routine_patrol
from tests.test_servo import start_servo_test, stop_servo_test

logger = logging.getLogger("dispatcher.registry")

# === Symbolic Command Definitions ===

_symbolic_to_register = {
    "task_step_forward": lambda: send_str(f"{cmd.CMD_MOVE}#1#0#35#8#0", server_instance.process_command),
    "task_step_back":    lambda: send_str(f"{cmd.CMD_MOVE}#1#0#-35#8#0", server_instance.process_command),

    "task_look_left":  lambda: send_str(f"{cmd.CMD_HEAD}#1#180", server_instance.process_command),
    "task_look_right": lambda: send_str(f"{cmd.CMD_HEAD}#1#0",   server_instance.process_command),
    "task_look_up":    lambda: send_str(f"{cmd.CMD_HEAD}#0#180", server_instance.process_command),
    "task_look_down":  lambda: send_str(f"{cmd.CMD_HEAD}#0#50",  server_instance.process_command),

    "sys_shutdown": lambda: send_str(f"{cmd.CMD_POWER}#0", server_instance.process_command),
    "sys_led_off":  lambda: send_str(f"{cmd.CMD_LED}#0#0#0", server_instance.process_command),
}

for name, func in _symbolic_to_register.items():
    if name in symbolic_commands:
        logger.warning("Symbolic command already registered, overwriting: %s", name)
    else:
        logger.info("Registering symbolic command: %s", name)
    symbolic_commands[name] = func


# === Routine Definitions ===

_routines_to_register = {
    "routine_march_forward": routine_march_forward,
    "routine_march_left":    routine_march_left,
    "routine_march_right":   routine_march_right,
    "routine_march_back":    routine_march_back,
    "routine_run_forward":   routine_run_forward,
    "routine_run_left":      routine_run_left,
    "routine_run_right":     routine_run_right,
    "routine_run_back":      routine_run_back,
    "routine_turn_left":     routine_turn_left,
    "routine_turn_right":    routine_turn_right,
    "routine_patrol":        routine_patrol,
    "sys_prep_calibration": sys_prep_calibration,
    "sys_exit_calibration": sys_exit_calibration,
    "sys_start_servo_test": lambda *_: start_servo_test(),
    "sys_stop_servo_test":  lambda *_: stop_servo_test(),
}

for name, func in _routines_to_register.items():
    if name in routine_commands:
        logger.warning("Routine already registered, overwriting: %s", name)
    else:
        logger.info("Registering routine: %s", name)
    routine_commands[name] = func
