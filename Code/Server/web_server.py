import os
import logging
from flask import Flask, request, jsonify, render_template
import threading
from voice_manager import start_voice, stop_voice
from command_dispatcher import dispatch_command, init_command_dispatcher
from robot_routines import shutdown_sequence  # other routines are handled by dispatcher

logger = logging.getLogger("web")

def create_app(server_instance, robot_state):
    app = Flask(
        __name__,
        static_folder="web_interface/static",
        template_folder="web_interface/templates"
    )

    # Initialize dispatcher with the shared Server instance
    init_command_dispatcher(server_instance)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/command", methods=["POST"])
    def send_command():
        cmd = request.json.get("cmd")
        if cmd:
            logger.info("Command received: %s", cmd)
            dispatch_command("web", cmd)
            return jsonify({"status": "ok", "executed": cmd})
        logger.warning("No command provided in /command POST")
        return jsonify({"status": "error", "reason": "No command provided"}), 400

    @app.route("/voice", methods=["POST"])
    def toggle_voice():
        action = request.json.get("action")
        if action == "start":
            logger.info("Voice start requested via web")
            try:
                start_voice(
                    server_instance.process_command,
                    server_instance.ultrasonic_sensor,
                    robot_state
                )
                return jsonify({"status": "started"})
            except Exception as e:
                logger.error("Failed to start voice control: %s", e)
                return jsonify({"status": "error", "reason": "Failed to start voice control"}), 500
        elif action == "stop":
            logger.info("Voice stop requested via web")
            try:
                stop_voice()
                return jsonify({"status": "stopped"})
            except Exception as e:
                logger.error("Failed to stop voice control: %s", e)
                return jsonify({"status": "error", "reason": "Failed to stop voice control"}), 500
        logger.warning("Invalid action for /voice: %s", action)
        return jsonify({"error": "Invalid action"}), 400

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
            logger.error("Failed to get status: %s", e)
            return jsonify({"status": "error", "reason": "Failed to get status"}), 500

    @app.route("/calibration_mode", methods=["GET", "POST"])
    def calibration_mode():
        if request.method == "GET":
            try:
                cm = robot_state.get_flag("calibration_mode")
                return jsonify({"calibration_mode": cm})
            except Exception as e:
                logger.error("Failed to get calibration mode: %s", e)
                return jsonify({"status": "error", "reason": "Failed to get calibration mode"}), 500
        # POST: set calibration mode
        data = request.get_json()
        mode = data.get("calibration_mode")
        if isinstance(mode, bool):
            try:
                robot_state.set_flag("calibration_mode", mode)
                logger.info("Calibration mode set to %s", mode)
                return jsonify({"status": "ok", "calibration_mode": robot_state.get_flag("calibration_mode")})
            except Exception as e:
                logger.error("Failed to set calibration mode: %s", e)
                return jsonify({"status": "error", "reason": "Failed to set calibration mode"}), 500
        logger.warning("Invalid calibration_mode value: %s", mode)
        return jsonify({"status": "error", "reason": "Invalid calibration_mode value"}), 400

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
            logger.error("Failed to get IMU status: %s", e)
            return jsonify({"status": "error", "reason": "Failed to get IMU status"}), 500

    @app.route("/routine", methods=["POST"])
    def trigger_routine():
        data = request.get_json()
        routine_name = data.get("routine")
        if routine_name:
            logger.info("Routine trigger requested: %s", routine_name)
            try:
                dispatch_command("web", routine_name)
                return jsonify({"status": "ok", "started": routine_name})
            except Exception as e:
                logger.error("Failed to trigger routine %s: %s", routine_name, e)
                return jsonify({"status": "error", "reason": f"Failed to trigger routine: {routine_name}"}), 500
        else:
            logger.warning("No routine specified in routine trigger request")
            return jsonify({"status": "error", "reason": "No routine specified"}), 400

    @app.route("/calibration", methods=["GET"])
    def get_calibration():
        # Try to read from current in-memory state (preferred), fallback to file if needed
        try:
            # Use the control system's in-memory data if available
            data = server_instance.control_system.calibration_leg_positions
            logger.info("Calibration data returned from in-memory state")
        except Exception as e:
            logger.warning("Falling back to point.txt for calibration data: %s", e)
            if os.path.exists("point.txt"):
                try:
                    with open("point.txt") as f:
                        lines = f.readlines()
                    data = [list(map(int, line.strip().split("\t"))) for line in lines]
                    logger.info("Calibration data returned from point.txt")
                except Exception as file_e:
                    logger.error("Failed to read calibration from point.txt: %s", file_e)
                    data = [[0, 72, 0] for _ in range(6)]
            else:
                logger.warning("point.txt not found, using default calibration data")
                data = [[0, 72, 0] for _ in range(6)]  # reasonable default

        return jsonify(data)

    return app