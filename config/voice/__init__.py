import logging
from config.robot_config import VOICE_LANG

logger = logging.getLogger("voice")

# Map of supported languages to their module names
SUPPORTED_LANGUAGES = {
    "en": "en",
    "eo": "eo", 
    "de": "de",
    "fr": "fr",
    "es": "es",
    "hi": "hi",
    "pl": "pl",
    "pt": "pt"
}

# Initialize command_map for the default language
if VOICE_LANG in SUPPORTED_LANGUAGES:
    try:
        logger.info("Loading %s voice config.", VOICE_LANG.upper())
        # Import the command map for the default language
        if VOICE_LANG == "en":
            from .en import command_map
        elif VOICE_LANG == "eo":
            from .eo import command_map
        elif VOICE_LANG == "de":
            from .de import command_map
        elif VOICE_LANG == "fr":
            from .fr import command_map
        elif VOICE_LANG == "es":
            from .es import command_map
        elif VOICE_LANG == "hi":
            from .hi import command_map
        elif VOICE_LANG == "pl":
            from .pl import command_map
        elif VOICE_LANG == "pt":
            from .pt import command_map
    except ImportError as e:
        logger.error("Voice config for language '%s' not found: %s", VOICE_LANG, e)
        raise ImportError(f"Voice config for language '{VOICE_LANG}' not found: {e}")
else:
    logger.error("Unsupported voice language: %s", VOICE_LANG)
    raise ImportError(f"Unsupported voice language: {VOICE_LANG}")
