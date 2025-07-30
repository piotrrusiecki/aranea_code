# robot_kinematics.py

import math
import logging

logger = logging.getLogger("robot")

def coordinate_to_angle(x, y, z, l1=33, l2=90, l3=110):
    """
    Convert Cartesian coordinates to servo angles for a single robot leg.
    """
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
    return round(math.degrees(a)), round(math.degrees(b)), round(math.degrees(c))

def angle_to_coordinate(a, b, c, l1=33, l2=90, l3=110):
    """
    Convert servo angles to Cartesian coordinates for a single robot leg.
    """
    a = math.pi / 180 * a
    b = math.pi / 180 * b
    c = math.pi / 180 * c
    x = round(l3 * math.sin(b + c) + l2 * math.sin(b))
    y = round(l3 * math.sin(a) * math.cos(b + c) + l2 * math.sin(a) * math.cos(b) + l1 * math.sin(a))
    z = round(l3 * math.cos(a) * math.cos(b + c) + l2 * math.cos(a) * math.cos(b) + l1 * math.cos(a))
    return x, y, z

def restrict_value(value, min_value, max_value):
    """
    Restrict a value to be within min_value and max_value.
    """
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value

def map_value(value, from_low, from_high, to_low, to_high):
    """
    Map a value from one range to another.
    """
    return (to_high - to_low) * (value - from_low) / (from_high - from_low) + to_low

if __name__ == '__main__':
    # Example usage/tests:
    logger.info("coordinate_to_angle(140, 0, 0): %s", coordinate_to_angle(140, 0, 0))
    logger.info("angle_to_coordinate(90, 0, 0): %s", angle_to_coordinate(90, 0, 0))
