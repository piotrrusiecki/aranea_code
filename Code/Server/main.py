# -*- coding: utf-8 -*-
import threading
import time
import sys
import os
import logging
from flask import Flask
from server import Server
from voice_manager import start_voice, stop_voice
from command_dispatcher import init_command_dispatcher, dispatch_command
from web_server import create_app
from werkzeug.serving import make_server
from robot_state import RobotState
from config import robot_config

# --- Logging setup ---
log_level = getattr(logging, robot_config.LOGGING_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger("main")

# Suppress Flask/Werkzeug info logs
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# --- Vosk logger setup (attempt to capture/suppress) ---
vosk_logger = logging.getLogger("vosk")
vosk_logger.setLevel(log_level)
vosk_logger.handlers = []  # Remove any existing handlers Vosk might set up
vosk_stream_handler = logging.StreamHandler(sys.stdout)
vosk_stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [vosk] %(message)s"))
vosk_logger.addHandler(vosk_stream_handler)

# Optional: Redirect sys.stderr to capture additional raw Vosk (or other C/C++) logs
class VoskLogRedirector:
    def write(self, message):
        message = message.strip()
        if message:
            vosk_logger.info(message)
    def flush(self):
        pass

sys.stderr = VoskLogRedirector()

# --- Flask threaded server ---
class FlaskServerThread(threading.Thread):
    def __init__(self, app):
        super().__init__(daemon=True)
        self.server = make_server('0.0.0.0', 80, app)
        self.ctx = app.app_context()
        self.ctx.push()
    def run(self):
        logger.info("Web server started on port 80 (HTTP)")
        self.server.serve_forever()
    def shutdown(self):
        self.server.shutdown()
        logger.info("Web server stopped")

# --- Main entrypoint ---
shutdown_event = threading.Event()
server = None
web_thread = None

if __name__ == '__main__':
    try:
        # Initialize server and robot state (ONE instance only!)
        robot_state = RobotState()
        robot_state.set_flag("servo_off", False)
        server = Server(robot_state=robot_state)
        server.robot_state = robot_state

        # Pass robot_state to Control when initializing if needed

        server.start_server()
        server.is_tcp_active = True

        # Start server threads
        video_thread = threading.Thread(target=server.transmit_video, args=(shutdown_event,), daemon=True)
        command_thread = threading.Thread(target=server.receive_commands, args=(shutdown_event,), daemon=True)
        video_thread.start()
        command_thread.start()

        # Start voice control (pass robot_state)
        init_command_dispatcher(server)
        start_voice(
            lambda cmd: dispatch_command("voice", cmd),
            server.ultrasonic_sensor,
            robot_state
        )

        # Start web interface
        flask_app = create_app(server, robot_state)
        web_thread = FlaskServerThread(flask_app)
        web_thread.start()

        logger.info("Server started. Press Ctrl+C to stop.")
        shutdown_event.wait()

    except KeyboardInterrupt:
        logger.warning("Stopping server...")

    except Exception as e:
        logger.exception("Unexpected error occurred")

    finally:
        shutdown_event.set()
        stop_voice()

        if server:
            server.is_tcp_active = False
            server.stop_server()

        if web_thread:
            web_thread.shutdown()

        logger.info("Server stopped.")
        os._exit(0)
