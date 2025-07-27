# command_dispatcher_symbolic.py

"""
Executes symbolic or routine commands from internal code (routines, voice, etc.),
without requiring direct access to dispatcher logic or risking circular imports.
"""

import logging
from command_dispatcher_core import symbolic_commands, routine_commands, server_instance
from command_dispatcher_utils import send_str

logger = logging.getLogger("dispatcher.symbolic")


def execute_symbolic(symbolic_name, source="internal"):
    """
    Executes a symbolic command (task_*, routine_*, sys_*) using dispatcher mappings.
    Used internally by routines and voice to avoid circular dispatcher calls.
    """
    if symbolic_name in symbolic_commands:
        logger.info("[symbolic][%s] Executing symbolic command: %s", source, symbolic_name)
        try:
            symbolic_commands[symbolic_name]()
        except Exception as e:
            logger.error("[symbolic][%s] Error executing symbolic '%s': %s", source, symbolic_name, e)

    elif symbolic_name in routine_commands:
        logger.info("[symbolic][%s] Executing routine command: %s", source, symbolic_name)
        try:
            routine_commands[symbolic_name](
                server_instance.process_command,
                server_instance.ultrasonic_sensor,
                server_instance.robot_state.get_flag("motion_mode"),
                robot_state=server_instance.robot_state
            )
        except Exception as e:
            logger.error("[symbolic][%s] Error executing routine '%s': %s", source, symbolic_name, e)

    else:
        logger.warning("[symbolic][%s] Symbolic command not found: %s", source, symbolic_name)
