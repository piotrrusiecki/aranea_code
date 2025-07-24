# robot_gait.py

import math
import copy
import time
import logging
from robot_kinematics import restrict_value, map_value
from robot_pose import transform_coordinates

logger = logging.getLogger("robot")

def run_gait(control, data, Z=40, F=64):
    """
    Execute a gait movement for the robot.

    Args:
        control: The parent Control object (to access state/methods).
        data: Movement command data array.
        Z: Step height.
        F: Step frames.
    """
    try:
        gait = data[1]
        x = restrict_value(int(data[2]), -35, 35)
        y = restrict_value(int(data[3]), -35, 35)
        logger.info("run_gait called with gait=%s, x=%d, y=%d, Z=%d, F=%d, angle=%s", gait, x, y, Z, F, data[5])
        if gait == "1":
            F = round(map_value(int(data[4]), 2, 10, 126, 22))
        else:
            F = round(map_value(int(data[4]), 2, 10, 171, 45))
        angle = int(data[5])
        z = Z / F
        delay = 0.01
        points = copy.deepcopy(control.body_points)
        xy = [[0, 0] for _ in range(6)]
        for i in range(6):
            xy[i][0] = ((points[i][0] * math.cos(angle / 180 * math.pi) + points[i][1] * math.sin(angle / 180 * math.pi) - points[i][0]) + x) / F
            xy[i][1] = ((-points[i][0] * math.sin(angle / 180 * math.pi) + points[i][1] * math.cos(angle / 180 * math.pi) - points[i][1]) + y) / F
        if x == 0 and y == 0 and angle == 0:
            transform_coordinates(points, control.leg_positions, control.body_points)
            control.set_leg_angles()
        elif gait == "1":
            for j in range(F):
                for i in range(3):
                    if j < (F / 8):
                        points[2 * i][0] -= 4 * xy[2 * i][0]
                        points[2 * i][1] -= 4 * xy[2 * i][1]
                        points[2 * i + 1][0] += 8 * xy[2 * i + 1][0]
                        points[2 * i + 1][1] += 8 * xy[2 * i + 1][1]
                        points[2 * i + 1][2] = Z + control.body_height
                    elif j < (F / 4):
                        points[2 * i][0] -= 4 * xy[2 * i][0]
                        points[2 * i][1] -= 4 * xy[2 * i][1]
                        points[2 * i + 1][2] -= z * 8
                    elif j < (3 * F / 8):
                        points[2 * i][2] += z * 8
                        points[2 * i + 1][0] -= 4 * xy[2 * i + 1][0]
                        points[2 * i + 1][1] -= 4 * xy[2 * i + 1][1]
                    elif j < (5 * F / 8):
                        points[2 * i][0] += 8 * xy[2 * i][0]
                        points[2 * i][1] += 8 * xy[2 * i][1]
                        points[2 * i + 1][0] -= 4 * xy[2 * i + 1][0]
                        points[2 * i + 1][1] -= 4 * xy[2 * i + 1][1]
                    elif j < (3 * F / 4):
                        points[2 * i][2] -= z * 8
                        points[2 * i + 1][0] -= 4 * xy[2 * i + 1][0]
                        points[2 * i + 1][1] -= 4 * xy[2 * i + 1][1]
                    elif j < (7 * F / 8):
                        points[2 * i][0] -= 4 * xy[2 * i][0]
                        points[2 * i][1] -= 4 * xy[2 * i][1]
                        points[2 * i + 1][2] += z * 8
                    elif j < F:
                        points[2 * i][0] -= 4 * xy[2 * i][0]
                        points[2 * i][1] -= 4 * xy[2 * i][1]
                        points[2 * i + 1][0] += 8 * xy[2 * i + 1][0]
                        points[2 * i + 1][1] += 8 * xy[2 * i + 1][1]
                transform_coordinates(points, control.leg_positions, control.body_points)
                control.set_leg_angles()
                time.sleep(delay)
        elif gait == "2":
            number = [5, 2, 1, 0, 3, 4]
            for i in range(6):
                for j in range(int(F / 6)):
                    for k in range(6):
                        if number[i] == k:
                            if j < int(F / 18):
                                points[k][2] += 18 * z
                            elif j < int(F / 9):
                                points[k][0] += 30 * xy[k][0]
                                points[k][1] += 30 * xy[k][1]
                            elif j < int(F / 6):
                                points[k][2] -= 18 * z
                        else:
                            points[k][0] -= 2 * xy[k][0]
                            points[k][1] -= 2 * xy[k][1]
                    transform_coordinates(points, control.leg_positions, control.body_points)
                    control.set_leg_angles()
                    time.sleep(delay)
        logger.info("run_gait completed successfully.")
    except Exception as e:
        logger.error("Exception in run_gait: %s", e)
        raise
