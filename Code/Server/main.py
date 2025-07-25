# -*- coding: utf-8 -*-
import threading
import time
import sys
import os
import logging
from datetime import datetime
from flask import Flask
from server import Server
from voice_manager import start_voice, stop_voice
from command_dispatcher import init_command_dispatcher, dispatch_command
from web_server import create_app
from werkzeug.serving import make_server
from robot_state import RobotState
from config import robot_config

# --- Vosk/C-level stderr redirect (rotate per server start) ---
VOSK_LOG_DIR = "/path/to/log/dir"  # <-- CHANGE THIS to your preferred directory (e.g. "/home/piotr/logs")
if not os.path.exists(VOSK_LOG_DIR):
    os.makedirs(VOSK_LOG_DIR)
vosk_log_basename = "vosk_native-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".log"
vosk_log_path = os.path.join(VOSK_LOG_DIR, vosk_log_basename)
vosk_log_file = open(vosk_log_path, "w")
sys.stderr.flush()
os.dup2(vosk_log_file.fileno(), sys.stderr.fileno())
sys.stderr = vosk_log_file

# --- Logging setup with color by logger name ---
class LoggerColorFormatter(logging.Formatter):
    def format(self, record):
        colors = robot_config.LOGGER_COLORS
        # Try exact match
        color = colors.get(record.name)
        if not color:
            # Try to match by prefix
            for prefix, c in colors.items():
                if prefix != 'RESET' and record.name.startswith(prefix + '.'):
                    color = c
                    break
        if not color:
            color = colors.get('RESET')
        message = super().format(record)
        return f"{color}{message}{colors['RESET']}"

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(LoggerColorFormatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))

log_level = getattr(logging, robot_config.LOGGING_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    handlers=[handler]
)
logger = logging.getLogger("main")

# Suppress Flask/Werkzeug info logs
logging.getLogger('werkzeug').setLevel(logging.WARNING)

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
