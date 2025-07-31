# -*- coding: utf-8 -*-
import time
import math
import copy
import threading
import logging
from gpiozero import OutputDevice
from robot_pid import Incremental_PID
from constants_commands import COMMAND as cmd
from sensor_imu import IMU
from actuator_servo import Servo
from robot_kinematics import coordinate_to_angle, restrict_value
from robot_pose import calculate_posture_balance, transform_coordinates
from robot_gait import run_gait as gait_function
from robot_calibration import read_from_txt, save_to_txt, calibrate
from config import robot_config


logger = logging.getLogger("robot.control")

class Control:
    def __init__(self, robot_state):  # Add any other params you need
        self.robot_state = robot_state
        self.imu = IMU()
        self.servo = Servo()
        self.movement_flag = 0x01
        self.pid_controller = Incremental_PID(0.500, 0.00, 0.0025)
        self.servo_power_disable = OutputDevice(4)
        self.servo_power_disable.off()
        self.status_flag = 0x00
        self.timeout = 0
        self.body_height = -25
        self.body_points = [
            [137.1, 189.4, self.body_height], [225, 0, self.body_height], [137.1, -189.4, self.body_height],
            [-137.1, -189.4, self.body_height], [-225, 0, self.body_height], [-137.1, 189.4, self.body_height]
        ]
        self.calibration_leg_positions = read_from_txt('point')
        self.leg_positions = [[140, 0, 0] for _ in range(6)]
        self.calibration_angles = [[0, 0, 0] for _ in range(6)]
        self.current_angles = [[90, 0, 0] for _ in range(6)]
        self.command_queue = ['', '', '', '', '', '']
        calibrate(self.leg_positions, self.calibration_leg_positions, self.calibration_angles, self.current_angles)
        self.set_leg_angles()
        self.debug_leg_pose_report()
        self.condition_thread = threading.Thread(target=self.condition_monitor)
        self.Thread_conditiona = threading.Condition()
        self.stop_event = threading.Event()
        self.condition_thread.start()
        logger.warning("Control system initialized. Thread alive = %s", self.condition_thread.is_alive())

    def debug_leg_pose_report(self):
        if not robot_config.DEBUG_LEGS or not logger.isEnabledFor(logging.DEBUG):
            return  # Skip if debugging disabled or log level too low

        logger.debug("Leg diagnostics (initial):")
        for i in range(6):
            raw = self.leg_positions[i]
            try:
                pre = coordinate_to_angle(-raw[2], raw[0], raw[1])
            except Exception as e:
                logger.warning("Leg %d | ERROR in coordinate_to_angle: %s", i+1, e)
                pre = [0, 0, 0]
            cal = self.calibration_angles[i]
            post = self.current_angles[i]
            logger.debug("Leg %d | pos: [%6.1f, %6.1f, %6.1f] | pre-angle: [%3d, %3d, %3d] | calib: [%3d, %3d, %3d] | final: [%3d, %3d, %3d]",
                        i+1, raw[0], raw[1], raw[2],
                        pre[0], pre[1], pre[2],
                        cal[0], cal[1], cal[2],
                        post[0], post[1], post[2])
    
    def stop(self):
        self.stop_event.set()
        if self.condition_thread.is_alive():
            self.condition_thread.join()

    def set_leg_angles(self):
        # Skip if servo power is off
        if self.robot_state.get_flag("servo_off"):
            logger.debug("Skipped set_leg_angles: servo_off is True.")
            return

        if not self.check_point_validity():
            logger.debug("This coordinate point is out of the active range.")
            return

        # Show GPIO state at the start of execution

        # Calculate angles based on leg_positions
        for i in range(6):
            self.current_angles[i][0], self.current_angles[i][1], self.current_angles[i][2] = coordinate_to_angle(
                -self.leg_positions[i][2], self.leg_positions[i][0], self.leg_positions[i][1])

        # Apply calibration offsets and clamp for legs 0 to 2
        for i in range(3):
            self.current_angles[i][0] = restrict_value(self.current_angles[i][0] + self.calibration_angles[i][0], 0, 180)
            self.current_angles[i][1] = restrict_value(90 - (self.current_angles[i][1] + self.calibration_angles[i][1]), 0, 180)
            self.current_angles[i][2] = restrict_value(self.current_angles[i][2] + self.calibration_angles[i][2], 0, 180)
            # Legs 3 to 5 with adjustments
            self.current_angles[i + 3][0] = restrict_value(self.current_angles[i + 3][0] + self.calibration_angles[i + 3][0], 0, 180)
            self.current_angles[i + 3][1] = restrict_value(90 + self.current_angles[i + 3][1] + self.calibration_angles[i + 3][1], 0, 180)
            self.current_angles[i + 3][2] = restrict_value(180 - (self.current_angles[i + 3][2] + self.calibration_angles[i + 3][2]), 0, 180)

        # Send angles to servos in the correct order
        # Leg 1
        self.servo.set_servo_angle(15, self.current_angles[0][0])
        self.servo.set_servo_angle(14, self.current_angles[0][1])
        self.servo.set_servo_angle(13, self.current_angles[0][2])
        # Leg 2
        self.servo.set_servo_angle(12, self.current_angles[1][0])
        self.servo.set_servo_angle(11, self.current_angles[1][1])
        self.servo.set_servo_angle(10, self.current_angles[1][2])
        # Leg 3
        self.servo.set_servo_angle(9, self.current_angles[2][0])
        self.servo.set_servo_angle(8, self.current_angles[2][1])
        self.servo.set_servo_angle(31, self.current_angles[2][2])
        # Leg 6
        self.servo.set_servo_angle(16, self.current_angles[5][0])
        self.servo.set_servo_angle(17, self.current_angles[5][1])
        self.servo.set_servo_angle(18, self.current_angles[5][2])
        # Leg 5
        self.servo.set_servo_angle(19, self.current_angles[4][0])
        self.servo.set_servo_angle(20, self.current_angles[4][1])
        self.servo.set_servo_angle(21, self.current_angles[4][2])
        # Leg 4
        self.servo.set_servo_angle(22, self.current_angles[3][0])
        self.servo.set_servo_angle(23, self.current_angles[3][1])
        self.servo.set_servo_angle(27, self.current_angles[3][2])


    def check_point_validity(self):
        is_valid = True
        leg_lengths = [0] * 6
        for i in range(6):
            leg_lengths[i] = math.sqrt(self.leg_positions[i][0] ** 2 + self.leg_positions[i][1] ** 2 + self.leg_positions[i][2] ** 2)
        for length in leg_lengths:
            if length > 248 or length < 90:
                is_valid = False
        return is_valid

    def _check_servo_off_condition(self):
        """Check if servos are powered off and handle accordingly."""
        if self.robot_state.get_flag("servo_off"):
            time.sleep(0.1)
            return True
        return False

    def _handle_auto_relax(self):
        """Handle automatic relaxation after timeout if enabled."""
        if (
            robot_config.AUTO_RELAX
            and (time.time() - self.timeout) > 10
            and self.timeout != 0
            and self.command_queue[0] == ''
        ):
            self.timeout = time.time()
            self.relax(True)
            self.status_flag = 0x00
            logger.info("[control] Auto-relaxed due to inactivity.")

    def _handle_position_command(self):
        """Handle position movement commands."""
        if cmd.CMD_POSITION in self.command_queue and len(self.command_queue) == 4:
            x = restrict_value(int(self.command_queue[1]), -40, 40)
            y = restrict_value(int(self.command_queue[2]), -40, 40)
            z = restrict_value(int(self.command_queue[3]), -20, 20)
            self.move_position(x, y, z)
            self.status_flag = 0x01
            logger.info("[control] CMD_POSITION executed: x=%d, y=%d, z=%d", x, y, z)
            self.command_queue = ['', '', '', '', '', '']
            return True
        return False

    def _handle_attitude_command(self):
        """Handle attitude adjustment commands."""
        if cmd.CMD_ATTITUDE in self.command_queue and len(self.command_queue) == 4:
            roll = restrict_value(int(self.command_queue[1]), -15, 15)
            pitch = restrict_value(int(self.command_queue[2]), -15, 15)
            yaw = restrict_value(int(self.command_queue[3]), -15, 15)
            points = calculate_posture_balance(roll, pitch, yaw, self.body_height)
            transform_coordinates(points, self.leg_positions)
            self.set_leg_angles()
            self.status_flag = 0x02
            logger.info("[control] CMD_ATTITUDE executed: roll=%d, pitch=%d, yaw=%d", roll, pitch, yaw)
            self.command_queue = ['', '', '', '', '', '']
            return True
        return False

    def _handle_move_command(self):
        """Handle movement/gait commands."""
        if cmd.CMD_MOVE in self.command_queue and len(self.command_queue) == 6:
            logger.debug("[control] CMD_MOVE triggered. queue = %s | motion_state = %s",
                        self.command_queue, self.robot_state.get_flag("motion_state"))
            
            if self.command_queue[2] == "0" and self.command_queue[3] == "0":
                self.run_gait(self.command_queue)
                logger.info("[control] CMD_MOVE (neutral) executed: robot stopped.")
                self.command_queue = ['', '', '', '', '', '']
            else:
                self.run_gait(self.command_queue)
                self.status_flag = 0x03
                logger.info("[control] CMD_MOVE executed: gait=%s, x=%s, y=%s, speed=%s, angle=%s",
                            self.command_queue[1],
                            self.command_queue[2],
                            self.command_queue[3],
                            self.command_queue[4],
                            self.command_queue[5])
                if not robot_config.CLEAR_MOVE_QUEUE_AFTER_EXEC:
                    logger.debug("[control] Retaining CMD_MOVE in queue for repeated gait.")
                else:
                    self.command_queue = ['', '', '', '', '', '']
            return True
        return False

    def _handle_balance_command(self):
        """Handle IMU balance commands."""
        if cmd.CMD_BALANCE in self.command_queue and len(self.command_queue) == 2:
            if self.command_queue[1] == "1":
                self.command_queue = ['', '', '', '', '', '']
                self.status_flag = 0x04
                logger.info("[control] CMD_BALANCE initiated.")
                self.imu6050()
            return True
        return False

    def _handle_calibration_command(self):
        """Handle calibration commands."""
        if cmd.CMD_CALIBRATION not in self.command_queue:
            return False

        if not self.robot_state.get_flag("calibration_mode"):
            logger.warning("[control] Ignoring calibration command: not in calibration mode.")
            self.command_queue = ['', '', '', '', '', '']
            return True

        logger.debug("[control] Calibration block hit. Queue: %s", self.command_queue)
        self.timeout = 0
        calibrate(self.leg_positions, self.calibration_leg_positions, self.calibration_angles, self.current_angles)
        logger.debug("[control] Calibration complete. Angles: %s", self.calibration_angles)
        self.set_leg_angles()

        if len(self.command_queue) >= 2:
            self._process_calibration_subcommand()

        self.command_queue = ['', '', '', '', '', '']
        return True

    def _process_calibration_subcommand(self):
        """Process specific calibration subcommands (leg adjustments, save)."""
        cmd_name = self.command_queue[1]
        logger.debug("[control] Calibration command details: %s", self.command_queue[1:])
        
        leg_map = {"one": 0, "two": 1, "three": 2, "four": 3, "five": 4, "six": 5}
        if cmd_name in leg_map:
            self._calibrate_specific_leg(cmd_name, leg_map[cmd_name])
        elif cmd_name == "save":
            save_to_txt(self.calibration_leg_positions, 'point')
            logger.info("[control] Calibration saved to disk.")

    def _calibrate_specific_leg(self, leg_name, leg_idx):
        """Calibrate a specific leg with new position values."""
        try:
            self.calibration_leg_positions[leg_idx] = [
                int(self.command_queue[2]),
                int(self.command_queue[3]),
                int(self.command_queue[4])
            ]
            self.leg_positions[leg_idx] = self.calibration_leg_positions[leg_idx][:]
            calibrate(self.leg_positions, self.calibration_leg_positions,
                     self.calibration_angles, self.current_angles)
            self.set_leg_angles()
            logger.info("[control] Leg %s calibration updated: %s",
                       leg_name, self.calibration_leg_positions[leg_idx])
        except Exception as e:
            logger.error("[control] Calibration failed for leg %s: %s", leg_name, e)

    def condition_monitor(self):
        """Main control loop that monitors and processes command queue."""
        while not self.stop_event.is_set():
            # Check for servo power off condition
            if self._check_servo_off_condition():
                continue

            # Handle auto-relax functionality
            self._handle_auto_relax()

            # Process commands in priority order
            if self._handle_position_command():
                continue
            elif self._handle_attitude_command():
                continue
            elif self._handle_move_command():
                continue
            elif self._handle_balance_command():
                continue
            elif self._handle_calibration_command():
                continue

    def relax(self, flag):
        if flag:
            self.servo.relax()
        else:
            self.set_leg_angles()

    def move_position(self, x, y, z):
        points = copy.deepcopy(self.body_points)
        for i in range(6):
            points[i][0] = self.body_points[i][0] - x
            points[i][1] = self.body_points[i][1] - y
            points[i][2] = -30 - z
            self.body_height = points[i][2]
            self.body_points[i][2] = points[i][2]
        transform_coordinates(points, self.leg_positions)
        self.set_leg_angles()

    def imu6050(self):
        old_roll = 0
        old_pitch = 0
        points = calculate_posture_balance(0, 0, 0, self.body_height)
        transform_coordinates(points, self.leg_positions)
        self.set_leg_angles()
        time.sleep(2)
        self.imu.Error_value_accel_data, self.imu.Error_value_gyro_data = self.imu.calculate_average_sensor_data()
        time.sleep(1)
        while True:
            if self.command_queue[0] != "":
                break
            time.sleep(0.02)
            roll, pitch, yaw = self.imu.update_imu_state()
            roll = self.pid_controller.pid_calculate(roll)
            pitch = self.pid_controller.pid_calculate(pitch)
            points = calculate_posture_balance(roll, pitch, 0, self.body_height)
            transform_coordinates(points, self.leg_positions)
            self.set_leg_angles()

    def run_gait(self, data, Z=40, F=64):
        gait_function(self, data, Z, F)


