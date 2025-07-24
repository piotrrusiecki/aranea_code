import time
import logging
from command import COMMAND as cmd

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
                for _ in range(3):
                    command_sender([cmd.CMD_LED, "255", "0", "0"])
                    time.sleep(0.2)
                    command_sender([cmd.CMD_LED, "0", "0", "0"])
                    time.sleep(0.2)
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
                        for _ in range(3):
                            command_sender([cmd.CMD_LED, "255", "0", "0"])
                            time.sleep(0.2)
                            command_sender([cmd.CMD_LED, "0", "0", "0"])
                            time.sleep(0.2)
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
        # Always reset state and pose
        if robot_state is not None:
            robot_state.set_flag("motion_state", False)
        time.sleep(0.2)  # Allow any outside resets or command race conditions to settle
        command_sender([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
        command_sender([cmd.CMD_HEAD, "0", "90"])


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

def prepare_for_calibration(send, control_system, robot_state):
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


def exit_calibration(send, control_system, robot_state):
    logger.info("Exiting calibration mode...")
    robot_state.set_flag("calibration_mode", False)
    # Optionally: relax servos or move to safe pose
    logger.info("Calibration mode OFF.")

# === High-level wrappers for routines ===

def march_forward(command_sender, ultrasonic_sensor, motion_mode_flag, robot_state=None, use_sensor=True):
    motion_loop(
        command_sender,
        ultrasonic_sensor,
        gait=2,
        x=0,
        y=35,
        speed=8,
        head_angle=90,
        motion_mode_flag=motion_mode_flag,
        robot_state=robot_state,
        use_sensor=use_sensor
    )

def march_left(command_sender, ultrasonic_sensor, motion_mode_flag, robot_state=None, use_sensor=True):
    motion_loop(
        command_sender,
        ultrasonic_sensor,
        gait=2,
        x=-35,
        y=0,
        speed=8,
        head_angle=180,
        motion_mode_flag=motion_mode_flag,
        robot_state=robot_state,
        use_sensor=use_sensor
    )

def march_right(command_sender, ultrasonic_sensor, motion_mode_flag, robot_state=None, use_sensor=True):
    motion_loop(
        command_sender,
        ultrasonic_sensor,
        gait=2,
        x=35,
        y=0,
        speed=8,
        head_angle=0,
        motion_mode_flag=motion_mode_flag,
        robot_state=robot_state,
        use_sensor=use_sensor
    )

def march_back(command_sender, ultrasonic_sensor, motion_mode_flag, robot_state=None, use_sensor=False):
    motion_loop(
        command_sender,
        ultrasonic_sensor,
        gait=2,
        x=0,
        y=-35,
        speed=8,
        head_angle=90,
        motion_mode_flag=motion_mode_flag,
        robot_state=robot_state,
        use_sensor=use_sensor
    )

def run_forward(command_sender, ultrasonic_sensor, motion_mode_flag, robot_state=None, use_sensor=True):
    motion_loop(
        command_sender,
        ultrasonic_sensor,
        gait=1,
        x=0,
        y=20,
        speed=10,
        head_angle=90,
        motion_mode_flag=motion_mode_flag,
        robot_state=robot_state,
        use_sensor=use_sensor
    )

def run_left(command_sender, ultrasonic_sensor, motion_mode_flag, robot_state=None, use_sensor=True):
    motion_loop(
        command_sender,
        ultrasonic_sensor,
        gait=1,
        x=-20,
        y=0,
        speed=10,
        head_angle=180,
        motion_mode_flag=motion_mode_flag,
        robot_state=robot_state,
        use_sensor=use_sensor
    )

def run_right(command_sender, ultrasonic_sensor, motion_mode_flag, robot_state=None, use_sensor=True):
    motion_loop(
        command_sender,
        ultrasonic_sensor,
        gait=1,
        x=20,
        y=0,
        speed=10,
        head_angle=0,
        motion_mode_flag=motion_mode_flag,
        robot_state=robot_state,
        use_sensor=use_sensor
    )

def run_back(command_sender, ultrasonic_sensor, motion_mode_flag, robot_state=None, use_sensor=False):
    motion_loop(
        command_sender,
        ultrasonic_sensor,
        gait=1,
        x=0,
        y=-20,
        speed=10,
        head_angle=90,
        motion_mode_flag=motion_mode_flag,
        robot_state=robot_state,
        use_sensor=use_sensor
    )
