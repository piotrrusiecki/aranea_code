# robot_calibration.py

import logging
import os
from robot_kinematics import coordinate_to_angle

logger = logging.getLogger("robot.calibration")

def _validate_filename(filename):
    """Validate filename to prevent path traversal attacks."""
    try:
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
        
        logger.debug("Filename validation passed: %s", filename)
        return basename
    except Exception as e:
        logger.error("Filename validation failed for '%s': %s", filename, e)
        raise

def read_from_txt(filename):
    try:
        validated_filename = _validate_filename(filename)
        filepath = validated_filename + ".txt"
        
        logger.debug("Reading calibration data from %s", filepath)
        with open(filepath, "r") as file:
            lines = file.readlines()
            data = [list(map(int, line.strip().split("\t"))) for line in lines]
        
        logger.info("Calibration data read from %s (%d entries)", filepath, len(data))
        logger.debug("Calibration data: %s", data)
        return data
    except FileNotFoundError:
        logger.warning("Calibration file %s.txt not found, using default values", filename)
        # Return default calibration data
        return [[0, 0, 0] for _ in range(6)]
    except Exception as e:
        logger.error("Failed to read calibration data from %s.txt: %s", filename, e)
        raise

def save_to_txt(data, filename):
    try:
        validated_filename = _validate_filename(filename)
        filepath = validated_filename + '.txt'
        
        logger.debug("Saving calibration data to %s", filepath)
        with open(filepath, 'w') as file:
            for row in data:
                file.write('\t'.join(map(str, row)) + '\n')
        
        logger.info("Calibration data saved to %s (%d entries)", filepath, len(data))
        logger.debug("Saved calibration data: %s", data)
    except Exception as e:
        logger.error("Failed to save calibration data to %s.txt: %s", filename, e)
        raise

def calibrate(leg_positions, calibration_leg_positions, calibration_angles, current_angles):
    """
    Calibrates the robot's legs and updates calibration_angles in place.
    All lists should be 6x3 and mutable.
    """
    try:
        logger.info("Starting robot leg calibration process")
        logger.debug("Input leg positions: %s", leg_positions)
        logger.debug("Calibration leg positions: %s", calibration_leg_positions)
        
        # Set default leg positions
        for i in range(6):
            leg_positions[i][0] = 140
            leg_positions[i][1] = 0
            leg_positions[i][2] = 0
        logger.debug("Set default leg positions: %s", leg_positions)
        
        # Calculate calibration angles
        for i in range(6):
            calibration_angles[i][0], calibration_angles[i][1], calibration_angles[i][2] = coordinate_to_angle(
                -calibration_leg_positions[i][2], calibration_leg_positions[i][0], calibration_leg_positions[i][1])
        logger.debug("Calculated calibration angles: %s", calibration_angles)
        
        # Calculate current angles
        for i in range(6):
            current_angles[i][0], current_angles[i][1], current_angles[i][2] = coordinate_to_angle(
                -leg_positions[i][2], leg_positions[i][0], leg_positions[i][1])
        logger.debug("Calculated current angles: %s", current_angles)
        
        # Calculate angle offsets
        for i in range(6):
            calibration_angles[i][0] = calibration_angles[i][0] - current_angles[i][0]
            calibration_angles[i][1] = calibration_angles[i][1] - current_angles[i][1]
            calibration_angles[i][2] = calibration_angles[i][2] - current_angles[i][2]
        
        logger.info("Robot leg calibration completed successfully")
        logger.debug("Final calibration angles: %s", calibration_angles)
        # No return; in-place modification
    except Exception as e:
        logger.error("Error during robot leg calibration: %s", e)
        raise
