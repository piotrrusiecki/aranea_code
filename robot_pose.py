# robot_pose.py

import math
import numpy as np
import logging

logger = logging.getLogger("robot")

def calculate_posture_balance(roll, pitch, yaw, body_height):
    """
    Calculate new foot positions based on body roll, pitch, yaw and height.
    """
    position = np.array([[0.0], [0.0], [body_height]])
    rpy = np.array([roll, pitch, yaw]) * math.pi / 180
    roll_angle, pitch_angle, yaw_angle = rpy[0], rpy[1], rpy[2]
    rotation_x = np.array([[1, 0, 0],
                          [0, math.cos(pitch_angle), -math.sin(pitch_angle)],
                          [0, math.sin(pitch_angle), math.cos(pitch_angle)]])
    rotation_y = np.array([[math.cos(roll_angle), 0, -math.sin(roll_angle)],
                          [0, 1, 0],
                          [math.sin(roll_angle), 0, math.cos(roll_angle)]])
    rotation_z = np.array([[math.cos(yaw_angle), -math.sin(yaw_angle), 0],
                          [math.sin(yaw_angle), math.cos(yaw_angle), 0],
                          [0, 0, 1]])
    rotation_matrix = rotation_x @ rotation_y @ rotation_z
    body_structure = np.array([[55, 76, 0],
                              [85, 0, 0],
                              [55, -76, 0],
                              [-55, -76, 0],
                              [-85, 0, 0],
                              [-55, 76, 0]]).T
    footpoint_structure = np.array([[137.1, 189.4, 0],
                                   [225, 0, 0],
                                   [137.1, -189.4, 0],
                                   [-137.1, -189.4, 0],
                                   [-225, 0, 0],
                                   [-137.1, 189.4, 0]]).T
    ab = np.zeros((3, 6))
    foot_positions = [[0, 0, 0] for _ in range(6)]
    for i in range(6):
        ab[:, i] = (position + rotation_matrix @ footpoint_structure[:, i:i+1]).flatten()
        foot_positions[i][0] = ab[0, i]
        foot_positions[i][1] = ab[1, i]
        foot_positions[i][2] = ab[2, i]
    return foot_positions

def transform_coordinates(points, leg_positions):
    """
    Transform 'points' and update the passed-in leg_positions.
    Operates in-place, returns the updated list for convenience.
    """
    # Leg 1
    leg_positions[0][0] = points[0][0] * math.cos(54 / 180 * math.pi) + points[0][1] * math.sin(54 / 180 * math.pi) - 94
    leg_positions[0][1] = -points[0][0] * math.sin(54 / 180 * math.pi) + points[0][1] * math.cos(54 / 180 * math.pi)
    leg_positions[0][2] = points[0][2] - 14
    # Leg 2
    leg_positions[1][0] = points[1][0] * math.cos(0 / 180 * math.pi) + points[1][1] * math.sin(0 / 180 * math.pi) - 85
    leg_positions[1][1] = -points[1][0] * math.sin(0 / 180 * math.pi) + points[1][1] * math.cos(0 / 180 * math.pi)
    leg_positions[1][2] = points[1][2] - 14
    # Leg 3
    leg_positions[2][0] = points[2][0] * math.cos(-54 / 180 * math.pi) + points[2][1] * math.sin(-54 / 180 * math.pi) - 94
    leg_positions[2][1] = -points[2][0] * math.sin(-54 / 180 * math.pi) + points[2][1] * math.cos(-54 / 180 * math.pi)
    leg_positions[2][2] = points[2][2] - 14
    # Leg 4
    leg_positions[3][0] = points[3][0] * math.cos(-126 / 180 * math.pi) + points[3][1] * math.sin(-126 / 180 * math.pi) - 94
    leg_positions[3][1] = -points[3][0] * math.sin(-126 / 180 * math.pi) + points[3][1] * math.cos(-126 / 180 * math.pi)
    leg_positions[3][2] = points[3][2] - 14
    # Leg 5
    leg_positions[4][0] = points[4][0] * math.cos(180 / 180 * math.pi) + points[4][1] * math.sin(180 / 180 * math.pi) - 85
    leg_positions[4][1] = -points[4][0] * math.sin(180 / 180 * math.pi) + points[4][1] * math.cos(180 / 180 * math.pi)
    leg_positions[4][2] = points[4][2] - 14
    # Leg 6
    leg_positions[5][0] = points[5][0] * math.cos(126 / 180 * math.pi) + points[5][1] * math.sin(126 / 180 * math.pi) - 94
    leg_positions[5][1] = -points[5][0] * math.sin(126 / 180 * math.pi) + points[5][1] * math.cos(126 / 180 * math.pi)
    leg_positions[5][2] = points[5][2] - 14
    return leg_positions

if __name__ == '__main__':
    # Example usage/tests (dummy values)
    test_body_height = -25
    result = calculate_posture_balance(0, 0, 0, test_body_height)
    logger.info("calculate_posture_balance(0,0,0,%d): %s", test_body_height, result)
    leg_pos = [[0, 0, 0] for _ in range(6)]
    body_pts = [[0, 0, 0] for _ in range(6)]
    logger.info("transform_coordinates: %s", transform_coordinates(result, leg_pos))
