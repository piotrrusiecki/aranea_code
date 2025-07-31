import time
import logging
from constants_commands import COMMAND as cmd
from robot_kinematics import map_value

logger = logging.getLogger("robot.routines")

def motion_loop(
    command_sender,
    ultrasonic_sensor,
    gait,
    x,
    y,
    speed,
    head_angle,
    motion_mode_flag,
    robot_state=None,
    use_sensor=True
):
    """
    Main motion loop for routines (march/run, all directions).
    Will stop and clear motion_state if obstacle too close (if use_sensor is True),
    or if motion is otherwise ended.
    """
    try:
        if use_sensor:
            # Move head to intended direction and center tilt
            command_sender([cmd.CMD_HEAD, "1", str(head_angle)])
            command_sender([cmd.CMD_HEAD, "0", "90"])
            # Allow servo to physically turn
            time.sleep(1)
            # Pre-move sonic check
            distance = ultrasonic_sensor.get_distance()
            logger.info("PRE-MOVE SONIC distance: %.1f cm", distance)
            if distance < 40:
                logger.warning("Obstacle detected before starting motion. Aborting.")
                if robot_state is not None:
                    robot_state.set_flag("motion_state", False)
                flash_led_red(command_sender)
                # Issue stop command for safety
                command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
                return  # Abort starting the loop

        else:
            # Even if not using sensor, still set head position for visual clarity
            command_sender([cmd.CMD_HEAD, "1", str(head_angle)])
            command_sender([cmd.CMD_HEAD, "0", "90"])

        while motion_mode_flag():
            try:
                if use_sensor:
                    distance = ultrasonic_sensor.get_distance()
                    logger.info("SONIC distance: %.1f cm", distance)
                    if distance < 40:
                        logger.warning("Obstacle too close. Stopping.")
                        flash_led_red(command_sender)
                        command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
                        break
                # If not using sensor, just walk, no printout
                command_sender([
                    cmd.CMD_MOVE,
                    str(gait),
                    str(x),
                    str(y),
                    str(speed),
                    "0"
                ])

                # Check flag more frequently for responsiveness
                for _ in range(6):  # ~0.6 seconds total
                    if not motion_mode_flag():
                        break
                    time.sleep(0.1)

            except Exception as e:
                logger.error("Motion loop error: %s", e)
                break
    finally:
        if robot_state is not None:
            robot_state.set_flag("motion_state", False)
        time.sleep(0.2)
        command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
        command_sender([cmd.CMD_HEAD, "0", "90"])
        command_sender([cmd.CMD_LED, "0", "0", "0"])
        
def sonic_monitor_loop(command_sender, ultrasonic_sensor, sonic_mode_flag):
    """
    Obstacle detection/monitoring only.
    Does NOT send any move commands; only logs or flashes LEDs if obstacle detected.
    All stopping and avoidance is handled by motion routines, not here.
    """
    while sonic_mode_flag():
        try:
            distance = ultrasonic_sensor.get_distance()
            logger.info("SONIC distance: %.1f cm", distance)
            if distance < 40:
                # Optional: flash LED or log, but do NOT move!
                command_sender([cmd.CMD_LED, "255", "128", "0"])
                time.sleep(0.2)
                command_sender([cmd.CMD_LED, "0", "0", "0"])
            time.sleep(1.0)
        except Exception as e:
            logger.error("Sonic mode error: %s", e)
            break

def shutdown_sequence(command_sender):
    """
    Sends the robot to a reset pose, powers down servos and LEDs, centers head.
    """
    logger.info("Shutdown sequence triggered.")
    command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
    command_sender([cmd.CMD_SERVOPOWER, "0"])
    command_sender([cmd.CMD_LED, "0", "0", "0"])
    command_sender([cmd.CMD_HEAD, "1", "90"])
    command_sender([cmd.CMD_HEAD, "0", "90"])

def sys_prep_calibration(send, control_system, robot_state):
    logger.info("Preparing robot for calibration...")

    saved_positions = []
    try:
        with open('point.txt', 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 3:
                    saved_positions.append([int(parts[0]), int(parts[1]), int(parts[2])])
        if len(saved_positions) != 6:
            logger.warning("point.txt has %d lines, expected 6. Using default positions.", len(saved_positions))
            saved_positions = [[140, 0, 0] for _ in range(6)]
    except FileNotFoundError:
        logger.warning("point.txt not found; using default calibration positions.")
        saved_positions = [[140, 0, 0] for _ in range(6)]

    robot_state.set_flag("calibration_mode", True)

    for i in range(6):
        control_system.leg_positions[i] = saved_positions[i][:]
        control_system.calibration_leg_positions[i] = saved_positions[i][:]

    control_system.set_leg_angles()

    logger.info("Robot set to saved calibration pose. Calibration mode ON.")


def sys_exit_calibration(send, control_system, robot_state):
    logger.info("Exiting calibration mode...")
    robot_state.set_flag("calibration_mode", False)
    # Optionally: relax servos or move to safe pose
    logger.info("Calibration mode OFF.")

# === High-level wrappers for routines ===

def make_motion_routine(gait, x, y, speed, head_angle, use_sensor_default=True):
    def routine(command_sender, ultrasonic_sensor, motion_mode_flag, robot_state=None, use_sensor=None):
        motion_loop(
            command_sender,
            ultrasonic_sensor,
            gait=gait,
            x=x,
            y=y,
            speed=speed,
            head_angle=head_angle,
            motion_mode_flag=motion_mode_flag,
            robot_state=robot_state,
            use_sensor=use_sensor_default if use_sensor is None else use_sensor
        )
    return routine

routine_march_forward = make_motion_routine(2, 0, 35, 8, 90)
routine_march_back    = make_motion_routine(2, 0, -35, 8, 90, use_sensor_default=False)
routine_march_left    = make_motion_routine(2, -35, 0, 8, 180)
routine_march_right   = make_motion_routine(2, 35, 0, 8, 0)

routine_run_forward = make_motion_routine(1, 0, 20, 10, 90)
routine_run_back    = make_motion_routine(1, 0, -20, 10, 90, use_sensor_default=False)
routine_run_left    = make_motion_routine(1, -20, 0, 10, 180)
routine_run_right   = make_motion_routine(1, 20, 0, 10, 0)


def compute_angle_for_speed(speed):
    # F = map_value(speed, 2, 10, 126, 22), 6 @ 80 → 22.5 deg
    F = round(map_value(speed, 2, 10, 126, 22))
    return 6

def routine_turn_left(command_sender, steps=1, speed=5, pause=1):
    angle_per_step = compute_angle_for_speed(speed)
    logger.info("Executing turn_left routine... speed=%d, angle=%d", speed, angle_per_step)
    for _ in range(steps):
        try:
            logger.debug("Sending left turn 1: CMD_MOVE#1#5#5#%d#%d", speed, -angle_per_step)
            command_sender([cmd.CMD_MOVE, "1", "5", "5", str(5), str(-angle_per_step)])
        except Exception as e:
            logger.error("Failed to send first turn_left step: %s", e)
        time.sleep(pause)

        try:
            logger.debug("Sending left turn 2: CMD_MOVE#1#-5#0#%d#%d", speed, -angle_per_step)
            command_sender([cmd.CMD_MOVE, "1", "-5", "0", str(5), str(-angle_per_step)])
        except Exception as e:
            logger.error("Failed to send second turn_left step: %s", e)
        time.sleep(pause)

        try:
            logger.debug("Sending  left turn 3: CMD_MOVE#1#0#0#%d#0", speed)
            command_sender([cmd.CMD_MOVE, "1", "0", "0", str(5), "0"])
        except Exception as e:
            logger.error("Failed to send reset step in turn_left: %s", e)

def routine_turn_right(command_sender, steps=1, speed=5, pause=1):
    angle_per_step = compute_angle_for_speed(speed)
    logger.info("Executing turn_right routine... speed=%d, angle=%d", speed, angle_per_step)
    for _ in range(steps):
        try:
            logger.debug("Sending right turn 1: CMD_MOVE#1#5#5#%d#%d", speed, angle_per_step)
            command_sender([cmd.CMD_MOVE, "1", "5", "5", str(5), str(angle_per_step)])
        except Exception as e:
            logger.error("Failed to send first turn_right step: %s", e)
        time.sleep(pause)

        try:
            logger.debug("Sending right turn 2: CMD_MOVE#1#-5#0#%d#%d", speed, angle_per_step)
            command_sender([cmd.CMD_MOVE, "1", "-5", "0", str(5), str(angle_per_step)])
        except Exception as e:
            logger.error("Failed to send second turn_right step: %s", e)
        time.sleep(pause)

        try:
            logger.debug("Sending right turn 3: CMD_MOVE#1#0#0#%d#0", speed)
            command_sender([cmd.CMD_MOVE, "1", "0", "0", str(5), "0"])
        except Exception as e:
            logger.error("Failed to send reset step in turn_right: %s", e)

def flash_led_red(sender, times=3, interval=0.2):
    for _ in range(times):
        sender([cmd.CMD_LED, "255", "0", "0"])
        time.sleep(interval)
        sender([cmd.CMD_LED, "0", "0", "0"])
        time.sleep(interval)
    