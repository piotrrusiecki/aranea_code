from config.robot_config import VOICE_LANG

if VOICE_LANG == "eo":
    from .eo import *
elif VOICE_LANG == "en":
    # If en.py doesn't exist yet, fallback or raise
    try:
        from .en import *
    except ImportError:
        raise ImportError("English voice config not found.")
else:
    raise ImportError(f"Unsupported voice language: {VOICE_LANG}")
