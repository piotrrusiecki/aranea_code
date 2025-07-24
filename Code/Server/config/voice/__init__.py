import logging
from config.robot_config import VOICE_LANG

logger = logging.getLogger("voice")

if VOICE_LANG == "eo":
    logger.info("Loading Esperanto voice config.")
    from .eo import *
elif VOICE_LANG == "en":
    try:
        logger.info("Loading English voice config.")
        from .en import *
    except ImportError:
        logger.error("English voice config not found.")
        raise ImportError("English voice config not found.")
else:
    logger.error("Unsupported voice language: %s", VOICE_LANG)
    raise ImportError(f"Unsupported voice language: {VOICE_LANG}")
