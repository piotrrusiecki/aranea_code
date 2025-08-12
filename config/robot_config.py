# config/robot_config.py
VOICE_LANG = "en"  # default language code, e.g. "eo", "en", etc.
VOICE_AUTOSTART = False  # Whether to start voice control automatically on startup
VOICE_MODELS = {
    "eo": "voice_models/vosk-model-small-eo-0.22",
    "en": "voice_models/vosk-model-small-en-us-0.15",
    "de": "voice_models/vosk-model-small-de-0.15",
    "fr": "voice_models/vosk-model-small-fr-0.22",
    "es": "voice_models/vosk-model-small-es-0.42",
    "hi": "voice_models/vosk-model-small-hi-0.22",
    "pl": "voice_models/vosk-model-small-pl-0.22",
    "pt": "voice_models/vosk-model-small-pt-0.3"
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
    'robot.kinematics': '\033[92m',  # Bright green
    'robot.pose':     '\033[92m',    # Bright green
    'robot.calibration': '\033[92m', # Bright green
    'robot.state':    '\033[92m',    # Bright green
    'robot.pid':      '\033[92m',    # Bright green
    'robot.patrol':   '\033[92m',    # Bright green
    'robot.gait':     '\033[92m',    # Bright green
    # Hardware and actuator loggers
    'hardware':       '\033[93m',    # Bright yellow
    'hardware.pca9685': '\033[93m',  # Bright yellow
    'actuator':       '\033[91m',    # Bright red
    'actuator.servo': '\033[91m',    # Bright red
    'actuator.led':   '\033[91m',    # Bright red
    'led':            '\033[91m',    # Bright red for LED subsystem (legacy)
    'led.commands':   '\033[91m',    # Bright red
    'led.hw.rpi':     '\033[91m',    # Bright red
    'led.hw.spi':     '\033[91m',    # Bright red
    # Sensor loggers
    'sensor':         '\033[95m',    # Bright magenta for sensor subsystem
    'sensor.camera':  '\033[96m',    # Bright cyan (aqua) for camera sensor
    'sensor.adc':     '\033[95m',    # Bright magenta
    'sensor.imu':     '\033[95m',    # Bright magenta
    'sensor.ultrasonic': '\033[95m', # Bright magenta
    # Camera subsystem
    'picamera2.picamera2':         '\033[96m',    # Bright cyan (aqua) for camera subsystem
    'RESET':          '\033[0m'
}
VOICE_SAMPLERATE = 44100
VOICE_BLOCKSIZE = 8000  # Increased from 4000 to reduce audio buffer overflows
VOICE_INPUT_DEVICE = 1
DRY_RUN = False
DEBUG_LEGS = False
AUTO_RELAX = False
CLEAR_MOVE_QUEUE_AFTER_EXEC = False