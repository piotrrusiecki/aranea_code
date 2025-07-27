# servo.py
from pca9685 import PCA9685
import threading
import time

def map_value(value, from_low, from_high, to_low, to_high):
    return (to_high - to_low) * (value - from_low) / (from_high - from_low) + to_low

class Servo:
    def __init__(self):
        self.pwm_40 = PCA9685(0x40, debug=True)
        self.pwm_41 = PCA9685(0x41, debug=True)
        self.pwm_40.set_pwm_freq(50)
        self.pwm_41.set_pwm_freq(50)

    def set_servo_angle(self, channel, angle):
        if channel < 16:
            duty_cycle = map_value(angle, 0, 180, 500, 2500)
            duty_cycle = map_value(duty_cycle, 0, 20000, 0, 4095)
            self.pwm_41.set_pwm(channel, 0, int(duty_cycle))
        elif channel < 32:
            duty_cycle = map_value(angle, 0, 180, 500, 2500)
            duty_cycle = map_value(duty_cycle, 0, 20000, 0, 4095)
            self.pwm_40.set_pwm(channel - 16, 0, int(duty_cycle))

    def relax(self):
        for i in range(8):
            self.pwm_41.set_pwm(i + 8, 4096, 4096)
            self.pwm_40.set_pwm(i, 4096, 4096)
            self.pwm_40.set_pwm(i + 8, 4096, 4096)

# --- Test Mode Thread Control ---
_running = False
_thread = None
_servo = Servo()

def _run_test_loop():
    global _running
    while _running:
        for i in range(32):
            if i in [10, 13, 31]:
                _servo.set_servo_angle(i, 10)
            elif i in [18, 21, 27]:
                _servo.set_servo_angle(i, 170)
            else:
                _servo.set_servo_angle(i, 90)
        time.sleep(3)

def start_servo_test():
    global _running, _thread
    if not _running:
        _running = True
        _thread = threading.Thread(target=_run_test_loop, daemon=True)
        _thread.start()

def stop_servo_test():
    global _running
    _running = False
    _servo.relax()

# Optional for standalone running
if __name__ == '__main__':
    start_servo_test()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_servo_test()