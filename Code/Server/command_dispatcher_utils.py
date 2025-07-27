# command_dispatcher_utils.py

import logging

logger = logging.getLogger("dispatcher.utils")


def send_str(command_str, process_func):
    """
    Splits a raw command string and sends it using the provided process function.
    """
    parts = command_str.split("#")
    logger.info("send_str called with command: %s", command_str)
    logger.debug("Split parts: %s", parts)

    try:
        process_func(parts)
    except Exception as e:
        logger.error("Failed to process command '%s': %s", command_str, e)
