from config.robot_config import VOICE_LANG

if VOICE_LANG == "eo":
    from .eo import *
elif VOICE_LANG == "en":
    from .en import *
else:
    raise ImportError(f"Unsupported voice language: {VOICE_LANG}")