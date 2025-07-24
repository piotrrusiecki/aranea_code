import threading

class RobotState:
    def __init__(self):
        self._flags = {
            "motion_state": False,
            "sonic_state": False,
            # Removed 'march_mode' as per discussion
        }
        self._lock = threading.Lock()

    def get_flag(self, name):
        with self._lock:
            return self._flags.get(name, False)

    def set_flag(self, name, value):
        with self._lock:
            if name in self._flags:
                self._flags[name] = value
            else:
                raise KeyError(f"Unknown flag '{name}'")
