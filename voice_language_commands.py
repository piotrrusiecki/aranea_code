# voice_language_commands.py

import importlib
import logging

logger = logging.getLogger("voice")

def get_language_command_map(lang_code):
    """Get command map for a specific language code."""
    try:
        module = importlib.import_module(f"config.voice.{lang_code}")
        return module.command_map
    except ImportError as e:
        logger.error("Failed to import command map for language '%s': %s", lang_code, e)
        return {}

# Available language codes
SUPPORTED_LANGUAGES = ["en", "eo", "de", "fr", "es", "hi", "pl", "pt"]

def get_language_command_maps():
    """Get all language command maps."""
    maps = {}
    for lang in SUPPORTED_LANGUAGES:
        maps[lang] = get_language_command_map(lang)
    return maps

# Initialize the maps
language_command_maps = get_language_command_maps()
