# robot_gait.py

import math
import copy
import time
import logging
from robot_kinematics import restrict_value, map_value
from robot_pose import transform_coordinates

logger = logging.getLogger("robot.gait")

def _parse_gait_parameters(data):
    """Parse and validate gait parameters from command data."""
    gait = data[1]
    x = restrict_value(int(data[2]), -35, 35)
    y = restrict_value(int(data[3]), -35, 35)
    angle = int(data[5])
    return gait, x, y, angle


def _calculate_frame_count(gait, speed_data):
    """Calculate frame count based on gait type and speed."""
    if gait == "1":
        return round(map_value(int(speed_data), 2, 10, 126, 22))
    else:
        return round(map_value(int(speed_data), 2, 10, 171, 45))


def _calculate_movement_deltas(points, x, y, angle, F):
    """Calculate movement deltas for each leg based on rotation and translation."""
    xy = [[0, 0] for _ in range(6)]
    angle_rad = angle / 180 * math.pi
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)
    
    for i in range(6):
        # Rotation transformation
        rotated_x = points[i][0] * cos_angle + points[i][1] * sin_angle
        rotated_y = -points[i][0] * sin_angle + points[i][1] * cos_angle
        
        # Movement delta per frame
        xy[i][0] = ((rotated_x - points[i][0]) + x) / F
        xy[i][1] = ((rotated_y - points[i][1]) + y) / F
    
    return xy


def _execute_neutral_position(control, points):
    """Execute neutral position (no movement)."""
    transform_coordinates(points, control.leg_positions)
    control.set_leg_angles()


def _execute_tripod_gait(control, points, xy, Z, F, z, delay):
    """Execute tripod gait pattern (gait type 1)."""
    for j in range(F):
        for i in range(3):
            # Phase 1: First eighth of cycle
            if j < (F / 8):
                _apply_tripod_phase_1(points, xy, i, Z, control.body_height)
            # Phase 2: Second eighth of cycle  
            elif j < (F / 4):
                _apply_tripod_phase_2(points, xy, i, z)
            # Phase 3: Third eighth of cycle
            elif j < (3 * F / 8):
                _apply_tripod_phase_3(points, xy, i, z)
            # Phase 4: Fourth eighth of cycle
            elif j < (5 * F / 8):
                _apply_tripod_phase_4(points, xy, i)
            # Phase 5: Fifth eighth of cycle
            elif j < (3 * F / 4):
                _apply_tripod_phase_5(points, xy, i, z)
            # Phase 6: Sixth eighth of cycle
            elif j < (7 * F / 8):
                _apply_tripod_phase_6(points, xy, i, z)
            # Phase 7: Final eighth of cycle
            elif j < F:
                _apply_tripod_phase_7(points, xy, i)
        
        transform_coordinates(points, control.leg_positions)
        control.set_leg_angles()
        time.sleep(delay)


def _apply_tripod_phase_1(points, xy, i, Z, body_height):
    """Apply tripod gait phase 1 movements."""
    points[2 * i][0] -= 4 * xy[2 * i][0]
    points[2 * i][1] -= 4 * xy[2 * i][1]
    points[2 * i + 1][0] += 8 * xy[2 * i + 1][0]
    points[2 * i + 1][1] += 8 * xy[2 * i + 1][1]
    points[2 * i + 1][2] = Z + body_height


def _apply_tripod_phase_2(points, xy, i, z):
    """Apply tripod gait phase 2 movements."""
    points[2 * i][0] -= 4 * xy[2 * i][0]
    points[2 * i][1] -= 4 * xy[2 * i][1]
    points[2 * i + 1][2] -= z * 8


def _apply_tripod_phase_3(points, xy, i, z):
    """Apply tripod gait phase 3 movements."""
    points[2 * i][2] += z * 8
    points[2 * i + 1][0] -= 4 * xy[2 * i + 1][0]
    points[2 * i + 1][1] -= 4 * xy[2 * i + 1][1]


def _apply_tripod_phase_4(points, xy, i):
    """Apply tripod gait phase 4 movements."""
    points[2 * i][0] += 8 * xy[2 * i][0]
    points[2 * i][1] += 8 * xy[2 * i][1]
    points[2 * i + 1][0] -= 4 * xy[2 * i + 1][0]
    points[2 * i + 1][1] -= 4 * xy[2 * i + 1][1]


def _apply_tripod_phase_5(points, xy, i, z):
    """Apply tripod gait phase 5 movements."""
    points[2 * i][2] -= z * 8
    points[2 * i + 1][0] -= 4 * xy[2 * i + 1][0]
    points[2 * i + 1][1] -= 4 * xy[2 * i + 1][1]


def _apply_tripod_phase_6(points, xy, i, z):
    """Apply tripod gait phase 6 movements."""
    points[2 * i][0] -= 4 * xy[2 * i][0]
    points[2 * i][1] -= 4 * xy[2 * i][1]
    points[2 * i + 1][2] += z * 8


def _apply_tripod_phase_7(points, xy, i):
    """Apply tripod gait phase 7 movements."""
    points[2 * i][0] -= 4 * xy[2 * i][0]
    points[2 * i][1] -= 4 * xy[2 * i][1]
    points[2 * i + 1][0] += 8 * xy[2 * i + 1][0]
    points[2 * i + 1][1] += 8 * xy[2 * i + 1][1]


def _execute_wave_gait(control, points, xy, z, F, delay):
    """Execute wave gait pattern (gait type 2)."""
    leg_sequence = [5, 2, 1, 0, 3, 4]  # Order in which legs move
    
    for i in range(6):
        for j in range(int(F / 6)):
            for k in range(6):
                if leg_sequence[i] == k:
                    _apply_wave_leg_movement(points, xy, k, j, z, F)
                else:
                    _apply_wave_body_movement(points, xy, k)
            
            transform_coordinates(points, control.leg_positions)
            control.set_leg_angles()
            time.sleep(delay)


def _apply_wave_leg_movement(points, xy, k, j, z, F):
    """Apply movement for the active leg in wave gait."""
    if j < int(F / 18):
        # Lift leg
        points[k][2] += 18 * z
    elif j < int(F / 9):
        # Move leg forward
        points[k][0] += 30 * xy[k][0]
        points[k][1] += 30 * xy[k][1]
    elif j < int(F / 6):
        # Lower leg
        points[k][2] -= 18 * z


def _apply_wave_body_movement(points, xy, k):
    """Apply movement for non-active legs in wave gait (body movement)."""
    points[k][0] -= 2 * xy[k][0]
    points[k][1] -= 2 * xy[k][1]


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
        # Parse and validate parameters
        gait, x, y, angle = _parse_gait_parameters(data)
        F = _calculate_frame_count(gait, data[4])
        
        logger.info("run_gait called with gait=%s, x=%d, y=%d, Z=%d, F=%d, angle=%s", 
                   gait, x, y, Z, F, data[5])
        
        # Setup movement calculations
        z = Z / F
        delay = 0.01
        points = copy.deepcopy(control.body_points)
        xy = _calculate_movement_deltas(points, x, y, angle, F)
        
        # Execute appropriate gait pattern
        if x == 0 and y == 0 and angle == 0:
            _execute_neutral_position(control, points)
        elif gait == "1":
            _execute_tripod_gait(control, points, xy, Z, F, z, delay)
        elif gait == "2":
            _execute_wave_gait(control, points, xy, z, F, delay)
        
        logger.info("run_gait completed successfully.")
    except Exception as e:
        logger.error("Exception in run_gait: %s", e)
        raise
