# command_dispatcher_registry.py

"""
Registers all symbolic and routine commands into the dispatcher registry.

This is the only file that should import routines or patrol modules directly.
It updates the registries defined in command_dispatcher_core.py.
"""

import logging
from command_dispatcher_core import symbolic_commands, routine_commands, server_instance
from command_dispatcher_utils import send_str
from constants_commands import COMMAND as cmd

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

DIAG_SET_SERVO = "diag_set_servo"

DIAG_COMMANDS = {
    DIAG_SET_SERVO: "Set a single servo to a target angle (for diagnostics)",
}

# === Symbolic Command Definitions ===

def _send_move_with_reset(send, move_cmd):
    """Send a movement command followed by a reset command (matching web interface pattern)"""
    send(move_cmd)
    # Add small delay to ensure movement completes before reset
    import time
    time.sleep(0.1)  
    # Send stop command (x=0, y=0, angle=0)
    send([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])

_symbolic_to_register = {
    # Movement commands - send movement + reset (matching web interface pattern)
    "task_step_forward": lambda send: _send_move_with_reset(send, [cmd.CMD_MOVE, "1", "0", "35", "8", "0"]),
    "task_step_back":    lambda send: _send_move_with_reset(send, [cmd.CMD_MOVE, "1", "0", "-35", "8", "0"]),
    "task_step_left":    lambda send: _send_move_with_reset(send, [cmd.CMD_MOVE, "1", "-35", "0", "8", "0"]),
    "task_step_right":   lambda send: _send_move_with_reset(send, [cmd.CMD_MOVE, "1", "35", "0", "8", "0"]),
    
    # Small turn commands - also need reset  
    "task_turn_small_left":  lambda send: _send_move_with_reset(send, [cmd.CMD_MOVE, "1", "0", "0", "8", "-5"]),
    "task_turn_small_right": lambda send: _send_move_with_reset(send, [cmd.CMD_MOVE, "1", "0", "0", "8", "5"]),
    
    # Attitude commands
    "task_attitude_forward": lambda send: send([cmd.CMD_ATTITUDE, "0", "15", "0"]),
    "task_attitude_back":    lambda send: send([cmd.CMD_ATTITUDE, "0", "-15", "0"]),
    "task_attitude_left":    lambda send: send([cmd.CMD_ATTITUDE, "-10", "0", "0"]),
    "task_attitude_right":   lambda send: send([cmd.CMD_ATTITUDE, "10", "0", "0"]),
    
    # Shift commands (body position)
    "task_shift_forward": lambda send: send([cmd.CMD_POSITION, "0", "10", "0"]),
    "task_shift_back":    lambda send: send([cmd.CMD_POSITION, "0", "-10", "0"]),
    "task_shift_left":    lambda send: send([cmd.CMD_POSITION, "-10", "0", "0"]),
    "task_shift_right":   lambda send: send([cmd.CMD_POSITION, "10", "0", "0"]),

    # Head/look commands
    "task_look_left":  lambda send: send([cmd.CMD_HEAD, "1", "180"]),
    "task_look_right": lambda send: send([cmd.CMD_HEAD, "1", "0"]),
    "task_look_up":    lambda send: send([cmd.CMD_HEAD, "0", "180"]),
    "task_look_down":  lambda send: send([cmd.CMD_HEAD, "0", "50"]),
    "sys_reset_head":  lambda send: send([cmd.CMD_HEAD, "1", "90"]),
    
    # Servo power commands
    "task_servo_off": lambda send: send([cmd.CMD_SERVOPOWER, "0"]),
    "task_servo_on":  lambda send: send([cmd.CMD_SERVOPOWER, "1"]),
    
    # Light commands
    "task_light_red":   lambda send: send([cmd.CMD_LED, "255", "0", "0"]),
    "task_light_green": lambda send: send([cmd.CMD_LED, "0", "255", "0"]),
    "task_light_blue":  lambda send: send([cmd.CMD_LED, "0", "0", "255"]),
    "task_light_off":   lambda send: send([cmd.CMD_LED, "0", "0", "0"]),

    # System commands
    "sys_shutdown": lambda send: send([cmd.CMD_POWER, "0"]),
    "sys_led_off":  lambda send: send([cmd.CMD_LED, "0", "0", "0"]),
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
    "sys_prep_calibration":  sys_prep_calibration,
    "sys_exit_calibration":  sys_exit_calibration,
    "sys_start_servo_test":  lambda *_: start_servo_test(),
    "sys_stop_servo_test":   lambda *_: stop_servo_test(),
    "sys_stop_motion":       lambda *_: None,
    "sys_start_sonic":       lambda *_: None,
    "sys_stop_sonic":        lambda *_: None,
}

for name, func in _routines_to_register.items():
    if name in routine_commands:
        logger.warning("Routine already registered, overwriting: %s", name)
    else:
        logger.info("Registering routine: %s", name)
    routine_commands[name] = func
