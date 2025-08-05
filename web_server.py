import os
import logging
from flask import Flask, request, jsonify, render_template
from voice_manager import start_voice, stop_voice
from command_dispatcher_logic import dispatch_command, init_command_dispatcher

logger = logging.getLogger("web")

LEG_TO_SERVO = {
    (0, 0): 15, (0, 1): 14, (0, 2): 13,  # L1
    (1, 0): 12, (1, 1): 11, (1, 2): 10,  # L2
    (2, 0): 9,  (2, 1): 8,  (2, 2): 31,  # L3
    (3, 0): 22, (3, 1): 23, (3, 2): 27,  # L4
    (4, 0): 19, (4, 1): 20, (4, 2): 21,  # L5
    (5, 0): 16, (5, 1): 17, (5, 2): 18,  # L6
}

# Route handler functions
def create_index_handler(default_angles, used_channels):
    """Create the index route handler with closure over default_angles and used_channels."""
    def index():
        try:
            return render_template("index.html", default_angles=default_angles, used_channels=used_channels)
        except Exception as e:
            logger.error("Failed to render index.html: %s", e)
            return render_template("error.html"), 500
    return index


def send_command():
    """Handle command dispatch from web interface."""
    cmd = request.json.get("cmd")
    if cmd:
        logger.info("Command received: %s", cmd)
        try:
            result = dispatch_command("web", cmd)
            return jsonify({"status": "ok", "executed": cmd, "result": result})
        except Exception as e:
            logger.error("Failed to dispatch command '%s': %s", cmd, e)
            return jsonify({"status": "error", "reason": "Command dispatch failed"}), 500
    logger.warning("No command provided in /command POST")
    return jsonify({"status": "error", "reason": "No command provided"}), 400


def create_voice_handler(server_instance, robot_state):
    """Create voice control handler with closure over server instance and robot state."""
    def toggle_voice():
        action = request.json.get("action")
        logger.info("Voice action requested via web: %s", action)
        try:
            if action == "start":
                start_voice(
                    server_instance.process_command,
                    server_instance.ultrasonic_sensor,
                    robot_state
                )
                return jsonify({"status": "started"})
            elif action == "stop":
                stop_voice()
                return jsonify({"status": "stopped"})
            else:
                logger.warning("Invalid voice action: %s", action)
                return jsonify({"status": "error", "reason": "Invalid voice action"}), 400
        except Exception as e:
            logger.error("Voice control error [%s]: %s", action, e)
            return jsonify({"status": "error", "reason": "Voice control failed"}), 500
    return toggle_voice


def create_language_handler(language_switcher):
    """Create language switching handler with callback pattern."""
    def switch_language_web():
        lang_code = request.json.get("language")
        logger.info("Language switch requested via web: %s", lang_code)
        try:
            if lang_code and language_switcher:
                language_switcher(lang_code)
                return jsonify({"status": "switched", "language": lang_code})
            else:
                logger.warning("No language code provided or language switcher not available")
                return jsonify({"status": "error", "reason": "No language code provided"}), 400
        except Exception as e:
            logger.error("Language switch error [%s]: %s", lang_code, e)
            return jsonify({"status": "error", "reason": "Language switch failed"}), 500
    return switch_language_web


def create_status_handler(server_instance, robot_state):
    """Create status handler with closure over server instance and robot state."""
    def status():
        try:
            status_data = {
                "tcp_active": server_instance.is_tcp_active,
                "servo_relaxed": server_instance.is_servo_relaxed,
                "calibration_mode": robot_state.get_flag("calibration_mode"),
                "motion_state": robot_state.get_flag("motion_state"),
                "sonic_state": robot_state.get_flag("sonic_state"),
            }
            return jsonify(status_data)
        except Exception as e:
            logger.error("Failed to retrieve robot status: %s", e)
            return jsonify({"status": "error", "reason": "Failed to get status"}), 500
    return status


def create_imu_handler(server_instance):
    """Create IMU status handler with closure over server instance."""
    def imu_status():
        try:
            pitch, roll, yaw = server_instance.control_system.imu.update_imu_state()
            return jsonify({
                "pitch": round(pitch, 2),
                "roll": round(roll, 2),
                "yaw": round(yaw, 2)
            })
        except Exception as e:
            logger.error("Failed to read IMU: %s", e)
            return jsonify({"status": "error", "reason": "Failed to get IMU status"}), 500
    return imu_status


def trigger_routine():
    """Handle routine trigger requests."""
    routine_name = request.json.get("routine")
    if not routine_name:
        logger.warning("No routine specified in POST")
        return jsonify({"status": "error", "reason": "No routine specified"}), 400

    logger.info("Routine trigger requested: %s", routine_name)
    try:
        dispatch_command("web", routine_name)
        return jsonify({"status": "ok", "started": routine_name})
    except Exception as e:
        logger.error("Routine trigger failed (%s): %s", routine_name, e)
        return jsonify({"status": "error", "reason": f"Failed to trigger routine: {routine_name}"}), 500


def create_calibration_handler(server_instance):
    """Create calibration data handler with closure over server instance."""
    def get_calibration():
        try:
            data = server_instance.control_system.calibration_leg_positions
            logger.info("Returned calibration from memory")
        except Exception as e:
            logger.warning("Memory read failed. Fallback to point.txt: %s", e)
            if os.path.exists("point.txt"):
                try:
                    with open("point.txt") as f:
                        lines = f.readlines()
                    data = [list(map(int, line.strip().split("\t"))) for line in lines]
                    logger.info("Returned calibration from point.txt")
                except Exception as file_e:
                    logger.error("Failed to read point.txt: %s", file_e)
                    data = [[0, 72, 0] for _ in range(6)]
            else:
                logger.warning("point.txt missing — using default calibration")
                data = [[0, 72, 0] for _ in range(6)]
        return jsonify(data)
    return get_calibration


def create_calibration_mode_handler(robot_state):
    """Create calibration mode handler with closure over robot state."""
    def calibration_mode():
        if request.method == "GET":
            try:
                return jsonify({"calibration_mode": robot_state.get_flag("calibration_mode")})
            except Exception as e:
                logger.error("GET calibration_mode failed: %s", e)
                return jsonify({"status": "error", "reason": "Failed to read flag"}), 500

        mode = request.get_json().get("calibration_mode")
        if isinstance(mode, bool):
            try:
                robot_state.set_flag("calibration_mode", mode)
                logger.info("Calibration mode set to: %s", mode)
                return jsonify({"status": "ok", "calibration_mode": mode})
            except Exception as e:
                logger.error("Setting calibration_mode failed: %s", e)
                return jsonify({"status": "error", "reason": "Failed to set flag"}), 500
        logger.warning("Invalid calibration_mode value received: %s", mode)
        return jsonify({"status": "error", "reason": "Invalid value"}), 400
    return calibration_mode


def create_set_speed_handler(robot_state):
    """Create speed setting handler with closure over robot state."""
    def set_speed():
        """Handle speed setting requests."""
        try:
            speed = int(request.json.get("speed", 0))
            robot_state.set_flag("move_speed", speed)
            logger.debug("Updated move_speed: %s", speed)
            return jsonify({"status": "ok"})
        except Exception as e:
            logger.error("Speed update failed: %s", e)
            return jsonify({"status": "error", "reason": "Invalid speed value"}), 400
    return set_speed


def load_point_txt():
    """Load calibration data from point.txt file."""
    servo_map = {}
    try:
        with open("point.txt", "r") as f:
            for leg_idx, line in enumerate(f.readlines()):
                values = line.strip().split()
                if len(values) != 3:
                    continue
                angles = list(map(int, values))
                for joint_idx, angle in enumerate(angles):
                    servo = LEG_TO_SERVO.get((leg_idx, joint_idx))
                    if servo is not None:
                        servo_map[str(servo)] = angle
        return jsonify(servo_map)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def internal_error(e):
    """Handle internal server errors."""
    logger.error("Unhandled 500 error: %s", e)
    return render_template("error.html"), 500


def create_app(server_instance, robot_state):
    """Create and configure the Flask web application."""
    app = Flask(
        __name__,
        static_folder="web_interface/static",
        template_folder="web_interface/templates"
    )

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.robot_state = robot_state

    init_command_dispatcher(server_instance)

    # Setup default servo angles and used channels
    used_channels = [0, 1, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 27, 31]
    default_angles = _calculate_default_angles(used_channels)

    # Get language switcher from voice manager to avoid cyclic imports
    from voice_manager import _voice_manager
    language_switcher = _voice_manager.switch_language

    # Register route handlers
    app.add_url_rule("/", "index", create_index_handler(default_angles, used_channels))
    app.add_url_rule("/command", "send_command", send_command, methods=["POST"])
    app.add_url_rule("/voice", "toggle_voice", create_voice_handler(server_instance, robot_state), methods=["POST"])
    app.add_url_rule("/language", "switch_language", create_language_handler(language_switcher), methods=["POST"])
    app.add_url_rule("/status", "status", create_status_handler(server_instance, robot_state))
    app.add_url_rule("/imu", "imu_status", create_imu_handler(server_instance))
    app.add_url_rule("/routine", "trigger_routine", trigger_routine, methods=["POST"])
    app.add_url_rule("/calibration", "get_calibration", create_calibration_handler(server_instance), methods=["GET"])
    app.add_url_rule("/calibration_mode", "calibration_mode", create_calibration_mode_handler(robot_state), methods=["GET", "POST"])
    app.add_url_rule("/set_speed", "set_speed", create_set_speed_handler(robot_state), methods=["POST"])
    app.add_url_rule("/load_point_txt", "load_point_txt", load_point_txt)
    
    app.errorhandler(500)(internal_error)

    return app


def _calculate_default_angles(used_channels):
    """Calculate default servo angles for the given channels."""
    default_angles = {}
    for ch in used_channels:
        if ch in [10, 13, 31]:
            default_angles[ch] = 10
        elif ch in [18, 21, 27]:
            default_angles[ch] = 170
        else:
            default_angles[ch] = 90
    return default_angles
