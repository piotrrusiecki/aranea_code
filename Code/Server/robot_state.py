import threading
import logging

logger = logging.getLogger("robot")

class RobotState:
    def __init__(self):
        self._flags = {
            "motion_state": False,
            "sonic_state": False,
            "calibration_mode": False,
            "servo_off": False,  # <-- NEW FLAG
            "move_speed": 5,
        }
        self._lock = threading.Lock()

    def get_flag(self, name):
        with self._lock:
            return self._flags.get(name, False)

    def set_flag(self, name, value):
        with self._lock:
            # Calibration exclusivity logic remains unchanged
            if name == "calibration_mode" and value is True:
                self._flags["motion_state"] = False
                self._flags["sonic_state"] = False
                logger.info("Enabling calibration_mode; motion_state and sonic_state set to False.")
            if name in self._flags:
                logger.info("Flag '%s' set to %s.", name, value)
                self._flags[name] = value
            else:
                logger.error("Attempted to set unknown flag '%s'.", name)
                raise KeyError(f"Unknown flag '{name}'")

    def get_all_flags(self):
        with self._lock:
            flags_copy = dict(self._flags)
            logger.info("All flags retrieved: %s", flags_copy)
            return flags_copy

    def reset_flags(self):
        with self._lock:
            for key in self._flags:
                self._flags[key] = False
            logger.info("All flags reset to False.")
