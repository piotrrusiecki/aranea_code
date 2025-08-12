import threading
import logging

logger = logging.getLogger("robot.state")

class RobotState:
    def __init__(self):
        self._flags = {
            "motion_state": False,
            "sonic_state": False,
            "calibration_mode": False,
            "servo_off": False,  # <-- NEW FLAG
            "voice_active": False,  # Voice control active state
            "move_speed": 5,
            "body_height_z": 0,  # Z position for body height (-20 to 20)
        }
        self._lock = threading.Lock()
        logger.info("Robot state initialized with %d flags", len(self._flags))
        logger.debug("Initial flags: %s", self._flags)

    def get_flag(self, name):
        with self._lock:
            value = self._flags.get(name, False)
            # Enhanced logging for Z position access
            if name == "body_height_z":
                logger.debug("Z position accessed: %d", value)
            elif logger.isEnabledFor(logging.DEBUG):
                logger.debug("Flag '%s' accessed: %s", name, value)
            return value

    def set_flag(self, name, value):
        with self._lock:
            # Calibration exclusivity logic remains unchanged
            if name == "calibration_mode" and value is True:
                self._flags["motion_state"] = False
                self._flags["sonic_state"] = False
                logger.info("Enabling calibration_mode; motion_state and sonic_state set to False")
            
            # Enhanced logging for Z position changes
            if name == "body_height_z":
                old_value = self._flags.get(name, 0)
                if old_value != value:
                    logger.info("Z position change: %d → %d", old_value, value)
                else:
                    logger.debug("Z position unchanged: %d", value)
            
            if name in self._flags:
                old_value = self._flags[name]
                if old_value != value:
                    logger.info("Flag '%s' changed: %s → %s", name, old_value, value)
                else:
                    logger.debug("Flag '%s' unchanged: %s", name, value)
                self._flags[name] = value
            else:
                logger.error("Attempted to set unknown flag '%s'", name)
                raise KeyError(f"Unknown flag '{name}'")

    def get_all_flags(self):
        with self._lock:
            flags_copy = dict(self._flags)
            logger.debug("All flags retrieved: %s", flags_copy)
            return flags_copy

    def reset_flags(self):
        with self._lock:
            logger.info("Resetting all flags to False")
            for key in self._flags:
                if key in ["move_speed", "body_height_z"]:
                    # Don't reset numeric values
                    continue
                self._flags[key] = False
            logger.debug("Flags after reset: %s", self._flags)
