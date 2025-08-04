# robot_calibration.py

import logging
import os
from robot_kinematics import coordinate_to_angle

logger = logging.getLogger("robot")

def _validate_filename(filename):
    """Validate filename to prevent path traversal attacks."""
    if not filename or not isinstance(filename, str):
        raise ValueError("Filename must be a non-empty string")
    
    # Remove any path separators and normalize
    basename = os.path.basename(filename)
    if basename != filename:
        raise ValueError("Filename cannot contain path separators")
    
    # Check for dangerous characters
    dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        if char in filename:
            raise ValueError(f"Filename contains invalid character: {char}")
    
    return basename

def read_from_txt(filename):
    try:
        validated_filename = _validate_filename(filename)
        filepath = validated_filename + ".txt"
        
        with open(filepath, "r") as file:
            lines = file.readlines()
            data = [list(map(int, line.strip().split("\t"))) for line in lines]
        logger.info("Calibration data read from %s", filepath)
        return data
    except Exception as e:
        logger.error("Failed to read calibration data from %s.txt: %s", filename, e)
        raise

def save_to_txt(data, filename):
    try:
        validated_filename = _validate_filename(filename)
        filepath = validated_filename + '.txt'
        
        with open(filepath, 'w') as file:
            for row in data:
                file.write('\t'.join(map(str, row)) + '\n')
        logger.info("Calibration data saved to %s", filepath)
    except Exception as e:
        logger.error("Failed to save calibration data to %s.txt: %s", filename, e)
        raise

def calibrate(leg_positions, calibration_leg_positions, calibration_angles, current_angles):
    """
    Calibrates the robot's legs and updates calibration_angles in place.
    All lists should be 6x3 and mutable.
    """
    # Optionally, log that calibration started
    logger.info("Calibration process started.")
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
    logger.info("Calibration process completed.")
    # No return; in-place modification
