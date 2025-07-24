# robot_calibration.py

from robot_kinematics import coordinate_to_angle

def read_from_txt(filename):
    with open(filename + ".txt", "r") as file:
        lines = file.readlines()
        data = [list(map(int, line.strip().split("\t"))) for line in lines]
    return data

def save_to_txt(data, filename):
    with open(filename + '.txt', 'w') as file:
        for row in data:
            file.write('\t'.join(map(str, row)) + '\n')

def calibrate(leg_positions, calibration_leg_positions, calibration_angles, current_angles):
    """
    Calibrates the robot's legs and updates calibration_angles in place.
    All lists should be 6x3 and mutable.
    """
    for i in range(6):
        leg_positions[i][0] = 140
        leg_positions[i][1] = 0
        leg_positions[i][2] = 0
    for i in range(6):
        calibration_angles[i][0], calibration_angles[i][1], calibration_angles[i][2] = coordinate_to_angle(
            -calibration_leg_positions[i][2], calibration_leg_positions[i][0], calibration_leg_positions[i][1])
    for i in range(6):
        current_angles[i][0], current_angles[i][1], current_angles[i][2] = coordinate_to_angle(
            -leg_positions[i][2], leg_positions[i][0], leg_positions[i][1])
    for i in range(6):
        calibration_angles[i][0] = calibration_angles[i][0] - current_angles[i][0]
        calibration_angles[i][1] = calibration_angles[i][1] - current_angles[i][1]
        calibration_angles[i][2] = calibration_angles[i][2] - current_angles[i][2]
    # No return; in-place modification

