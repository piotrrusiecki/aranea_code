# command_dispatcher_symbolic.py

"""
Executes symbolic or routine commands from internal code (routines, voice, etc.),
without requiring direct access to dispatcher logic or risking circular imports.
"""

import logging
from command_dispatcher_core import symbolic_commands, routine_commands
from command_dispatcher_logic import CommandDispatcher
from command_dispatcher_utils import send_str
from actuator_servo import Servo

logger = logging.getLogger("dispatcher.symbolic")


def execute_symbolic(symbolic_name, source="internal"):
    """
    Executes a symbolic command (task_*, routine_*, sys_*) using dispatcher mappings.
    Used internally by routines and voice to avoid circular dispatcher calls.
    """
    try:
        server = CommandDispatcher.get_server()
    except RuntimeError:
        logger.error("[symbolic][%s] Server instance not initialized, cannot execute '%s'", source, symbolic_name)
        return
    
    if symbolic_name in symbolic_commands:
        logger.info("[symbolic][%s] Executing symbolic command: %s", source, symbolic_name)
        try:
            # Create send function for symbolic commands
            def send(parts):
                send_str("#".join(parts), server.process_command)
            
            symbolic_commands[symbolic_name](send)
        except Exception as e:
            logger.error("[symbolic][%s] Error executing symbolic '%s': %s", source, symbolic_name, e)

    elif symbolic_name in routine_commands:
        logger.info("[symbolic][%s] Executing routine command: %s", source, symbolic_name)
        try:
            routine_commands[symbolic_name](
                server.process_command,
                server.ultrasonic_sensor,
                server.robot_state.get_flag("motion_mode"),
                robot_state=server.robot_state
            )
        except Exception as e:
            logger.error("[symbolic][%s] Error executing routine '%s': %s", source, symbolic_name, e)

    else:
        logger.warning("[symbolic][%s] Symbolic command not found: %s", source, symbolic_name)


def handle_diag_set_servo(args, source="unknown"):
    if len(args) != 2:
        raise ValueError("diag_set_servo requires 2 arguments: channel and angle")

    channel = int(args[0])
    angle = int(args[1])

    servo = Servo()
    servo.set_servo_angle(channel, angle)

    logger.info("[%s] Diagnostic servo set: channel %d → angle %d", source, channel, angle)
