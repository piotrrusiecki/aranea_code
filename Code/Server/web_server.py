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
        })

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

    return app