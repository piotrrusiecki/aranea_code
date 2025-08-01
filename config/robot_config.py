# config/robot_config.py
VOICE_LANG = "eo"  # default language code, e.g. "eo", "en", etc.
VOICE_MODELS = {
    "eo": "voice_models/vosk-model-small-eo-0.22",
    "en": "voice_models/vosk-model-small-en-us-0.15",
}

LOGGING_LEVEL = "DEBUG"
LOGGER_COLORS = {
    'main':           '\033[94m',    # Bright blue
    'voice':          '\033[35m',    # Magenta
    'web':            '\033[36m',    # Cyan
    'dispatcher':     '\033[33m',    # Yellow
    'dispatcher.core':     '\033[33m',    # Yellow
    'dispatcher.logic':     '\033[33m',    # Yellow
    'dispatcher.registry':     '\033[33m',    # Yellow
    'dispatcher.symbolic':     '\033[33m',    # Yellow
    'dispatcher.utils':     '\033[33m',    # Yellow
    # Robot and sub-loggers shades of green
    'robot':          '\033[32m',    # Green
    'robot.control':  '\033[92m',    # Bright green
    'robot.server':   '\033[32m',    # Regular green
    'robot.routines': '\033[32;1m',  # Bold green
    'picamera2.picamera2':         '\033[96m',    # Bright cyan (aqua) for camera subsystem
    'sensor':         '\033[95m',    # Bright magenta for sensor subsystem
    'sensor.camera':  '\033[96m',    # Bright cyan (aqua) for camera sensor
    'led':            '\033[91m',    # Bright red for LED subsystem
    'RESET':          '\033[0m'
}
VOICE_SAMPLERATE = 44100
VOICE_BLOCKSIZE = 8000  # Increased from 4000 to reduce audio buffer overflows
VOICE_INPUT_DEVICE = 1
DRY_RUN = False
DEBUG_LEGS = True
AUTO_RELAX = False
CLEAR_MOVE_QUEUE_AFTER_EXEC = False