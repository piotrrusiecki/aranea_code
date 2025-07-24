# -*- coding: utf-8 -*-
import time
import math
import copy
import threading
import numpy as np
from gpiozero import OutputDevice
from pid import Incremental_PID
from command import COMMAND as cmd
from imu import IMU
from servo import Servo
from robot_kinematics import coordinate_to_angle, angle_to_coordinate, restrict_value, map_value
from robot_pose import calculate_posture_balance, transform_coordinates
from robot_gait import run_gait
from robot_calibration import read_from_txt, save_to_txt, calibrate

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
        self.condition_thread = threading.Thread(target=self.condition_monitor)
        self.Thread_conditiona = threading.Condition()
        self.stop_event = threading.Event()
        self.condition_thread.start()

    def stop(self):
        self.stop_event.set()
        if self.condition_thread.is_alive():
            self.condition_thread.join()

    def set_leg_angles(self):
        print("DEBUG: set_leg_angles called.")
        print("DEBUG: leg_positions before calculation:", self.leg_positions)
        print("DEBUG: calibration_angles:", self.calibration_angles)

        if self.check_point_validity():
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

            print("DEBUG: current_angles after applying calibration:", self.current_angles)

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
        else:
            print("This coordinate point is out of the active range")


    def check_point_validity(self):
        is_valid = True
        leg_lengths = [0] * 6
        for i in range(6):
            leg_lengths[i] = math.sqrt(self.leg_positions[i][0] ** 2 + self.leg_positions[i][1] ** 2 + self.leg_positions[i][2] ** 2)
        for length in leg_lengths:
            if length > 248 or length < 90:
                is_valid = False
        return is_valid

    def condition_monitor(self):
        while not self.stop_event.is_set():
            # Block all actions if servos are powered off
            if self.robot_state.get_flag("servo_off"):
                time.sleep(0.1)
                continue

            if cmd.CMD_POSITION in self.command_queue and len(self.command_queue) == 4:
                x = restrict_value(int(self.command_queue[1]), -40, 40)
                y = restrict_value(int(self.command_queue[2]), -40, 40)
                z = restrict_value(int(self.command_queue[3]), -20, 20)
                self.move_position(x, y, z)
                self.status_flag = 0x01
                self.command_queue = ['', '', '', '', '', '']

            elif cmd.CMD_ATTITUDE in self.command_queue and len(self.command_queue) == 4:
                roll = restrict_value(int(self.command_queue[1]), -15, 15)
                pitch = restrict_value(int(self.command_queue[2]), -15, 15)
                yaw = restrict_value(int(self.command_queue[3]), -15, 15)
                points = calculate_posture_balance(roll, pitch, yaw, self.body_height)
                transform_coordinates(points, self.leg_positions, self.body_points)
                self.set_leg_angles()
                self.status_flag = 0x02
                self.command_queue = ['', '', '', '', '', '']

            elif cmd.CMD_MOVE in self.command_queue and len(self.command_queue) == 6:
                if self.command_queue[2] == "0" and self.command_queue[3] == "0":
                    self.run_gait(self.command_queue)
                    self.command_queue = ['', '', '', '', '', '']
                else:
                    self.run_gait(self.command_queue)
                    self.status_flag = 0x03

            elif cmd.CMD_BALANCE in self.command_queue and len(self.command_queue) == 2:
                if self.command_queue[1] == "1":
                    self.command_queue = ['', '', '', '', '', '']
                    self.status_flag = 0x04
                    self.imu6050()

            elif cmd.CMD_CALIBRATION in self.command_queue:
                # --- Calibration mode safety check ---
                if not self.robot_state.get_flag("calibration_mode"):
                    print("Ignoring calibration command: not in calibration mode.")
                    self.command_queue = ['', '', '', '', '', '']
                    continue

                print("DEBUG: Calibration block hit. Queue:", self.command_queue)
                self.timeout = 0
                calibrate(self.leg_positions, self.calibration_leg_positions, self.calibration_angles, self.current_angles)
                print("DEBUG: After calibrate, angles:", self.calibration_angles)
                self.set_leg_angles()
                if len(self.command_queue) >= 2:
                    print("DEBUG: Command details:", self.command_queue[1:])
                    if self.command_queue[1] == "one":
                        idx = 0
                        self.calibration_leg_positions[idx][0] = int(self.command_queue[2])
                        self.calibration_leg_positions[idx][1] = int(self.command_queue[3])
                        self.calibration_leg_positions[idx][2] = int(self.command_queue[4])
                        self.leg_positions[idx] = self.calibration_leg_positions[idx][:]
                        calibrate(self.leg_positions, self.calibration_leg_positions, self.calibration_angles, self.current_angles)
                        self.set_leg_angles()
                    elif self.command_queue[1] == "two":
                        idx = 1
                        self.calibration_leg_positions[idx][0] = int(self.command_queue[2])
                        self.calibration_leg_positions[idx][1] = int(self.command_queue[3])
                        self.calibration_leg_positions[idx][2] = int(self.command_queue[4])
                        self.leg_positions[idx] = self.calibration_leg_positions[idx][:]
                        calibrate(self.leg_positions, self.calibration_leg_positions, self.calibration_angles, self.current_angles)
                        self.set_leg_angles()
                    elif self.command_queue[1] == "three":
                        idx = 2
                        self.calibration_leg_positions[idx][0] = int(self.command_queue[2])
                        self.calibration_leg_positions[idx][1] = int(self.command_queue[3])
                        self.calibration_leg_positions[idx][2] = int(self.command_queue[4])
                        self.leg_positions[idx] = self.calibration_leg_positions[idx][:]
                        calibrate(self.leg_positions, self.calibration_leg_positions, self.calibration_angles, self.current_angles)
                        self.set_leg_angles()
                    elif self.command_queue[1] == "four":
                        idx = 3
                        self.calibration_leg_positions[idx][0] = int(self.command_queue[2])
                        self.calibration_leg_positions[idx][1] = int(self.command_queue[3])
                        self.calibration_leg_positions[idx][2] = int(self.command_queue[4])
                        self.leg_positions[idx] = self.calibration_leg_positions[idx][:]
                        calibrate(self.leg_positions, self.calibration_leg_positions, self.calibration_angles, self.current_angles)
                        self.set_leg_angles()
                    elif self.command_queue[1] == "five":
                        idx = 4
                        self.calibration_leg_positions[idx][0] = int(self.command_queue[2])
                        self.calibration_leg_positions[idx][1] = int(self.command_queue[3])
                        self.calibration_leg_positions[idx][2] = int(self.command_queue[4])
                        self.leg_positions[idx] = self.calibration_leg_positions[idx][:]
                        calibrate(self.leg_positions, self.calibration_leg_positions, self.calibration_angles, self.current_angles)
                        self.set_leg_angles()
                    elif self.command_queue[1] == "six":
                        idx = 5
                        self.calibration_leg_positions[idx][0] = int(self.command_queue[2])
                        self.calibration_leg_positions[idx][1] = int(self.command_queue[3])
                        self.calibration_leg_positions[idx][2] = int(self.command_queue[4])
                        self.leg_positions[idx] = self.calibration_leg_positions[idx][:]
                        calibrate(self.leg_positions, self.calibration_leg_positions, self.calibration_angles, self.current_angles)
                        self.set_leg_angles()
                    elif self.command_queue[1] == "save":
                        save_to_txt(self.calibration_leg_positions, 'point')
                self.command_queue = ['', '', '', '', '', '']



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
        transform_coordinates(points, self.leg_positions, self.body_points)
        self.set_leg_angles()

    def imu6050(self):
        old_roll = 0
        old_pitch = 0
        points = calculate_posture_balance(0, 0, 0, self.body_height)
        transform_coordinates(points, self.leg_positions, self.body_points)
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
            transform_coordinates(points, self.leg_positions, self.body_points)
            self.set_leg_angles()

    def run_gait(self, data, Z=40, F=64):
        run_gait(self, data, Z, F)

if __name__ == '__main__':
    pass