# command_dispatcher_core.py

"""
Core dispatcher registry module.

Contains symbolic and routine command mappings, and the shared server_instance
used across dispatcher, symbolic execution, and routines.
"""

import logging

logger = logging.getLogger("dispatcher.core")

symbolic_commands = {}
routine_commands = {}

server_instance = None  # This should be assigned externally, typically in main.py


def register_symbolic(name, func):
    if name in symbolic_commands:
        logger.warning("Overwriting existing symbolic command: %s", name)
    else:
        logger.info("Registering symbolic command: %s", name)
    symbolic_commands[name] = func


def register_routine(name, func):
    if name in routine_commands:
        logger.warning("Overwriting existing routine command: %s", name)
    else:
        logger.info("Registering routine command: %s", name)
    routine_commands[name] = func


def dump_registry():
    logger.debug("Registered symbolic commands: %s", list(symbolic_commands.keys()))
    logger.debug("Registered routine commands: %s", list(routine_commands.keys()))
    logger.debug("Server instance set: %s", server_instance is not None)
