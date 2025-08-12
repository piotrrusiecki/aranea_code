# robot_kinematics.py

import math
import logging

logger = logging.getLogger("robot.kinematics")

def coordinate_to_angle(x, y, z, l1=33, l2=90, l3=110):
    """
    Convert Cartesian coordinates to servo angles for a single robot leg.
    """
    try:
        a = math.pi / 2 - math.atan2(z, y)
        x_3 = 0
        x_4 = l1 * math.sin(a)
        x_5 = l1 * math.cos(a)
        l23 = math.sqrt((z - x_5) ** 2 + (y - x_4) ** 2 + (x - x_3) ** 2)
        w = restrict_value((x - x_3) / l23, -1, 1)
        v = restrict_value((l2 * l2 + l23 * l23 - l3 * l3) / (2 * l2 * l23), -1, 1)
        u = restrict_value((l2 ** 2 + l3 ** 2 - l23 ** 2) / (2 * l3 * l2), -1, 1)
        b = math.asin(round(w, 2)) - math.acos(round(v, 2))
        c = math.pi - math.acos(round(u, 2))
        result = (round(math.degrees(a)), round(math.degrees(b)), round(math.degrees(c)))
        logger.debug("coordinate_to_angle: input=(%.1f, %.1f, %.1f) -> angles=(%d°, %d°, %d°)", 
                    x, y, z, result[0], result[1], result[2])
        return result
    except Exception as e:
        logger.error("Error in coordinate_to_angle(%.1f, %.1f, %.1f): %s", x, y, z, e)
        return 90, 0, 0  # Return safe default angles

def angle_to_coordinate(a, b, c, l1=33, l2=90, l3=110):
    """
    Convert servo angles to Cartesian coordinates for a single robot leg.
    """
    try:
        a_rad = math.pi / 180 * a
        b_rad = math.pi / 180 * b
        c_rad = math.pi / 180 * c
        x = round(l3 * math.sin(b_rad + c_rad) + l2 * math.sin(b_rad))
        y = round(l3 * math.sin(a_rad) * math.cos(b_rad + c_rad) + l2 * math.sin(a_rad) * math.cos(b_rad) + l1 * math.sin(a_rad))
        z = round(l3 * math.cos(a_rad) * math.cos(b_rad + c_rad) + l2 * math.cos(a_rad) * math.cos(b_rad) + l1 * math.cos(a_rad))
        result = (x, y, z)
        logger.debug("angle_to_coordinate: angles=(%d°, %d°, %d°) -> coords=(%d, %d, %d)", 
                    a, b, c, result[0], result[1], result[2])
        return result
    except Exception as e:
        logger.error("Error in angle_to_coordinate(%d°, %d°, %d°): %s", a, b, c, e)
        return 140, 0, 0  # Return safe default coordinates

def restrict_value(value, min_value, max_value):
    """
    Restrict a value to be within min_value and max_value.
    """
    if value < min_value:
        logger.debug("Value %.3f restricted to minimum %.3f", value, min_value)
        return min_value
    elif value > max_value:
        logger.debug("Value %.3f restricted to maximum %.3f", value, max_value)
        return max_value
    else:
        return value

def map_value(value, from_low, from_high, to_low, to_high):
    """
    Map a value from one range to another.
    """
    try:
        result = (to_high - to_low) * (value - from_low) / (from_high - from_low) + to_low
        logger.debug("map_value: %.3f [%.3f,%.3f] -> %.3f [%.3f,%.3f]", 
                    value, from_low, from_high, result, to_low, to_high)
        return result
    except ZeroDivisionError:
        logger.warning("map_value: division by zero, returning to_low value %.3f", to_low)
        return to_low
    except Exception as e:
        logger.error("Error in map_value: %s", e)
        return to_low

if __name__ == '__main__':
    # Example usage/tests:
    logger.info("Testing coordinate_to_angle(140, 0, 0): %s", coordinate_to_angle(140, 0, 0))
    logger.info("Testing angle_to_coordinate(90, 0, 0): %s", angle_to_coordinate(90, 0, 0))
