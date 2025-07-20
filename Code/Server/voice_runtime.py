import time

# Runtime flags
motion_mode = False
march_mode = False
sonic_mode = False

# Interfaces (injected)
command_sender = None
ultrasonic_sensor = None

def set_runtime_interfaces(sender_func, sensor):
    global command_sender, ultrasonic_sensor
    command_sender = sender_func
    ultrasonic_sensor = sensor


def motion_loop(gait, x, y, speed, head_angle):
    global motion_mode
    command_sender(["CMD_HEAD", "1", str(head_angle)])
    command_sender(["CMD_HEAD", "0", "90"])
    while motion_mode:
        try:
            distance = ultrasonic_sensor.get_distance()
            print("SONIC distance: {:.1f} cm".format(distance))
            if distance < 30:
                print("Obstacle too close. Stopping.")
                for _ in range(3):
                    command_sender(["CMD_LED", "255", "0", "0"])
                    time.sleep(0.2)
                    command_sender(["CMD_LED", "0", "0", "0"])
                    time.sleep(0.2)
                break
            command_sender(["CMD_MOVE", str(gait), str(x), str(y), str(speed), "0"])
            time.sleep(0.6)
        except Exception as e:
            print("Motion loop error: {}".format(e))
            break
        time.sleep(0.5)
    command_sender(["CMD_HEAD", "0", "90"])
    motion_mode = False


def motion_loop_simple(gait, x, y, speed, head_angle):
    global motion_mode
    command_sender(["CMD_HEAD", "1", str(head_angle)])
    command_sender(["CMD_HEAD", "0", "90"])
    for _ in range(20):
        if not motion_mode:
            break
        command_sender(["CMD_MOVE", str(gait), str(x), str(y), str(speed), "0"])
        time.sleep(0.6)
    command_sender(["CMD_MOVE", "1", "0", "0", "8", "0"])
    command_sender(["CMD_HEAD", "1", "90"])
    command_sender(["CMD_HEAD", "0", "90"])


def sonic_monitor_loop():
    global sonic_mode
    while sonic_mode:
        try:
            distance = ultrasonic_sensor.get_distance()
            print("SONIC distance: {:.1f} cm".format(distance))

            if distance < 40:
                command_sender(["CMD_MOVE", "1", "0", "-35", "8", "0"])
                time.sleep(0.6)
                command_sender(["CMD_MOVE", "1", "0", "0", "8", "0"])
            elif distance > 50:
                command_sender(["CMD_MOVE", "1", "0", "35", "8", "0"])
                time.sleep(0.6)
                command_sender(["CMD_MOVE", "1", "0", "0", "8", "0"])

            time.sleep(1.5)

        except Exception as e:
            print("Sonic mode error: {}".format(e))
            break


def march_loop(x, y, speed):
    global march_mode
    if x < 0:
        command_sender(["CMD_HEAD", "1", "135"])
    elif x > 0:
        command_sender(["CMD_HEAD", "1", "45"])
    else:
        command_sender(["CMD_HEAD", "1", "90"])
    command_sender(["CMD_HEAD", "0", "90"])

    while march_mode:
        try:
            distance = ultrasonic_sensor.get_distance()
            print("SONIC distance: {:.1f} cm".format(distance))

            if distance < 25:
                print("Obstacle too close. Stopping.")
                command_sender(["CMD_MOVE", "1", "0", "0", "8", "0"])
                for _ in range(3):
                    command_sender(["CMD_LED", "255", "0", "0"])
                    time.sleep(0.2)
                    command_sender(["CMD_LED", "0", "0", "0"])
                    time.sleep(0.2)
                break

            command_sender(["CMD_MOVE", "2", str(x), str(y), str(speed), "0"])
            time.sleep(0.6)

        except Exception as e:
            print("March loop error: {}".format(e))
            break

        time.sleep(0.5)

    command_sender(["CMD_HEAD", "1", "90"])
