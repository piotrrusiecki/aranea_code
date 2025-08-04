# -*- coding: utf-8 -*-
import threading
import sys
import os
import logging
from hardware_server import Server
from voice_manager import start_voice, stop_voice
from command_dispatcher_logic import init_command_dispatcher, dispatch_command
import command_dispatcher_registry  # noqa: F401 - Trigger registration of symbolic/routine commands
from web_server import create_app
from werkzeug.serving import make_server
from robot_state import RobotState
from config import robot_config

# --- Logging setup with color by logger name ---
class LoggerColorFormatter(logging.Formatter):
    def format(self, record):
        colors = robot_config.LOGGER_COLORS
        color = colors.get(record.name)
        if not color:
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
logging.basicConfig(level=log_level, handlers=[handler])
logger = logging.getLogger("main")

# Suppress Flask/Werkzeug info logs
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# --- Flask threaded server ---
class FlaskServerThread(threading.Thread):
    def __init__(self, app):
        super().__init__(daemon=True)
        self.server = make_server('0.0.0.0', 80, app)  # skipcq: BAN-B104
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
        robot_state = RobotState()
        robot_state.set_flag("servo_off", False)
        server = Server(robot_state=robot_state)
        server.robot_state = robot_state

        server.start_server()
        server.is_tcp_active = True

        threading.Thread(target=server.transmit_video, args=(shutdown_event,), daemon=True).start()
        threading.Thread(target=server.receive_commands, args=(shutdown_event,), daemon=True).start()

        init_command_dispatcher(server)
        start_voice(lambda cmd: dispatch_command("voice", cmd), server.ultrasonic_sensor, robot_state)

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
