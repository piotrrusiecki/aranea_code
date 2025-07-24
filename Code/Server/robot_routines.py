import time
from command import COMMAND as cmd

def motion_loop(command_sender, ultrasonic_sensor, gait, x, y, speed, head_angle, motion_mode_flag):
    command_sender([cmd.CMD_HEAD, "1", str(head_angle)])
    command_sender([cmd.CMD_HEAD, "0", "90"])
    while motion_mode_flag():
        try:
            distance = ultrasonic_sensor.get_distance()
            print(f"SONIC distance: {distance:.1f} cm")
            if distance < 30:
                print("Obstacle too close. Stopping.")
                for _ in range(3):
                    command_sender([cmd.CMD_LED, "255", "0", "0"])
                    time.sleep(0.2)
                    command_sender([cmd.CMD_LED, "0", "0", "0"])
                    time.sleep(0.2)
                break
            command_sender([cmd.CMD_MOVE, str(gait), str(x), str(y), str(speed), "0"])

            # Sleep in smaller intervals to check flag more often
            for _ in range(6):  # total ~0.6s
                if not motion_mode_flag():
                    break
                time.sleep(0.1)

        except Exception as e:
            print(f"Motion loop error: {e}")
            break
        # Similarly reduce or split this sleep if still used
        # time.sleep(0.5)
    command_sender([cmd.CMD_HEAD, "0", "90"])

def sonic_monitor_loop(command_sender, ultrasonic_sensor, sonic_mode_flag):
    """Monitor ultrasonic sensor and avoid obstacles (auto-move left/right)."""
    while sonic_mode_flag():
        try:
            distance = ultrasonic_sensor.get_distance()
            print(f"SONIC distance: {distance:.1f} cm")
            if distance < 40:
                command_sender([cmd.CMD_MOVE, "1", "0", "-35", "8", "0"])
                time.sleep(0.6)
                command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
            elif distance > 50:
                command_sender([cmd.CMD_MOVE, "1", "0", "35", "8", "0"])
                time.sleep(0.6)
                command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
            time.sleep(1.5)
        except Exception as e:
            print(f"Sonic mode error: {e}")
            break

def shutdown_sequence(command_sender):
    """Standard shutdown/reset pose for robot."""
    command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
    command_sender([cmd.CMD_SERVOPOWER, "0"])
    command_sender([cmd.CMD_LED, "0", "0", "0"])
    command_sender([cmd.CMD_HEAD, "1", "90"])
    command_sender([cmd.CMD_HEAD, "0", "90"])

# === High-level wrappers for voice/web commands ===

def march_forward(command_sender, ultrasonic_sensor, motion_mode_flag):
    motion_loop(command_sender, ultrasonic_sensor, gait=2, x=0, y=35, speed=10, head_angle=90, motion_mode_flag=motion_mode_flag)

def march_left(command_sender, ultrasonic_sensor, motion_mode_flag):
    motion_loop(command_sender, ultrasonic_sensor, gait=2, x=-35, y=0, speed=10, head_angle=135, motion_mode_flag=motion_mode_flag)

def march_right(command_sender, ultrasonic_sensor, motion_mode_flag):
    motion_loop(command_sender, ultrasonic_sensor, gait=2, x=35, y=0, speed=10, head_angle=45, motion_mode_flag=motion_mode_flag)

def march_back(command_sender, ultrasonic_sensor, motion_mode_flag):
    motion_loop(command_sender, ultrasonic_sensor, gait=2, x=0, y=-35, speed=10, head_angle=90, motion_mode_flag=motion_mode_flag)

def run_forward(command_sender, ultrasonic_sensor, motion_mode_flag):
    motion_loop(command_sender, ultrasonic_sensor, gait=1, x=0, y=20, speed=10, head_angle=90, motion_mode_flag=motion_mode_flag)

def run_left(command_sender, ultrasonic_sensor, motion_mode_flag):
    motion_loop(command_sender, ultrasonic_sensor, gait=1, x=-20, y=0, speed=10, head_angle=135, motion_mode_flag=motion_mode_flag)

def run_right(command_sender, ultrasonic_sensor, motion_mode_flag):
    motion_loop(command_sender, ultrasonic_sensor, gait=1, x=20, y=0, speed=10, head_angle=45, motion_mode_flag=motion_mode_flag)

def run_back(command_sender, ultrasonic_sensor, motion_mode_flag):
    motion_loop(command_sender, ultrasonic_sensor, gait=1, x=0, y=-20, speed=10, head_angle=90, motion_mode_flag=motion_mode_flag)
