import os
import logging
from flask import Flask, request, jsonify, render_template
from voice_manager import start_voice, stop_voice
from command_dispatcher_logic import dispatch_command, init_command_dispatcher
from robot_routines import shutdown_sequence

logger = logging.getLogger("web")


def create_app(server_instance, robot_state):
    app = Flask(
        __name__,
        static_folder="web_interface/static",
        template_folder="web_interface/templates"
    )

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.robot_state = robot_state

    init_command_dispatcher(server_instance)

    used_channels = [
        0, 1,
        8, 9, 10, 11, 12, 13, 14, 15,
        16, 17, 18, 19, 20, 21,
        22, 23, 27, 31
    ]
    default_angles = {}
    for ch in used_channels:
        if ch in [10, 13, 31]:
            default_angles[ch] = 10
        elif ch in [18, 21, 27]:
            default_angles[ch] = 170
        else:
            default_angles[ch] = 90

    @app.route("/")
    def index():
        try:
            return render_template("index.html", default_angles=default_angles, used_channels=used_channels)
        except Exception as e:
            logger.error("Failed to render index.html: %s", e)
            return render_template("error.html"), 500

    @app.route("/command", methods=["POST"])
    def send_command():
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

    @app.route("/voice", methods=["POST"])
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

    @app.route("/status")
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

    @app.route("/imu")
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

    @app.route("/routine", methods=["POST"])
    def trigger_routine():
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

    @app.route("/calibration", methods=["GET"])
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

    @app.route("/calibration_mode", methods=["GET", "POST"])
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

    @app.route("/set_speed", methods=["POST"])
    def set_speed():
        try:
            speed = int(request.json.get("speed", 0))
            app.robot_state.set_flag("move_speed", speed)
            logger.debug("Updated move_speed: %s", speed)
            return jsonify({"status": "ok"})
        except Exception as e:
            logger.error("Speed update failed: %s", e)
            return jsonify({"status": "error", "reason": "Invalid speed value"}), 400

    @app.errorhandler(500)
    def internal_error(e):
        logger.error("Unhandled 500 error: %s", e)
        return render_template("error.html"), 500

    return app
