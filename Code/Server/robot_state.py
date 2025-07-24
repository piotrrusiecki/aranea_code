import threading

class RobotState:
    def __init__(self):
        self._flags = {
            "motion_state": False,
            "sonic_state": False,
            "calibration_mode": False,
            "servo_off": False,  # <-- NEW FLAG
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
            if name in self._flags:
                self._flags[name] = value
            else:
                raise KeyError(f"Unknown flag '{name}'")

    def get_all_flags(self):
        with self._lock:
            return dict(self._flags)

    def reset_flags(self):
        with self._lock:
            for key in self._flags:
                self._flags[key] = False
