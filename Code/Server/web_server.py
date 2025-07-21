from flask import Flask, request, jsonify, render_template
from voice_manager import start_voice, stop_voice
from command_dispatcher import dispatch_command, init_command_dispatcher

def create_app(server_instance):
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
            start_voice(server_instance.process_command, server_instance.ultrasonic_sensor)
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
        # Direct internal call; no sockets, no network
        pitch, roll, yaw = server_instance.control_system.imu.update_imu_state()
        return jsonify({
            "pitch": round(pitch, 2),
            "roll": round(roll, 2),
            "yaw": round(yaw, 2)
        })

    return app
