import os
from flask import Flask, request, jsonify, render_template
import threading
from voice_manager import start_voice, stop_voice
from command_dispatcher import dispatch_command, init_command_dispatcher
from robot_routines import shutdown_sequence  # other routines are handled by dispatcher

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
            dispatch_command("web", cmd)
            return jsonify({"status": "ok", "executed": cmd})
        return jsonify({"status": "error", "reason": "No command provided"}), 400

    @app.route("/voice", methods=["POST"])
    def toggle_voice():
        action = request.json.get("action")
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
        return jsonify({"error": "Invalid action"}), 400

    @app.route("/status")
    def status():
        return jsonify({
            "tcp_active": server_instance.is_tcp_active,
            "servo_relaxed": server_instance.is_servo_relaxed,
            "calibration_mode": robot_state.get_flag("calibration_mode"),
            "motion_state": robot_state.get_flag("motion_state"),
            "sonic_state": robot_state.get_flag("sonic_state"),
        })

    @app.route("/calibration_mode", methods=["GET", "POST"])
    def calibration_mode():
        if request.method == "GET":
            return jsonify({"calibration_mode": robot_state.get_flag("calibration_mode")})
        # POST: set calibration mode
        data = request.get_json()
        mode = data.get("calibration_mode")
        if isinstance(mode, bool):
            robot_state.set_flag("calibration_mode", mode)
            return jsonify({"status": "ok", "calibration_mode": robot_state.get_flag("calibration_mode")})
        return jsonify({"status": "error", "reason": "Invalid calibration_mode value"}), 400

    @app.route("/imu")
    def imu_status():
        pitch, roll, yaw = server_instance.control_system.imu.update_imu_state()
        return jsonify({
            "pitch": round(pitch, 2),
            "roll": round(roll, 2),
            "yaw": round(yaw, 2)
        })

    @app.route("/routine", methods=["POST"])
    def trigger_routine():
        data = request.get_json()
        routine_name = data.get("routine")
        if routine_name:
            dispatch_command("web", routine_name)
            return jsonify({"status": "ok", "started": routine_name})
        else:
            return jsonify({"status": "error", "reason": "No routine specified"}), 400

    @app.route("/calibration", methods=["GET"])
    def get_calibration():
        # Try to read from current in-memory state (preferred), fallback to file if needed
        try:
            # Use the control system's in-memory data if available
            data = server_instance.control_system.calibration_leg_positions
        except Exception:
            # Fallback to reading the file directly
            if os.path.exists("point.txt"):
                with open("point.txt") as f:
                    lines = f.readlines()
                data = [list(map(int, line.strip().split("\t"))) for line in lines]
            else:
                data = [[0, 72, 0] for _ in range(6)]  # reasonable default

        return jsonify(data)

    return app
