# command_dispatcher.py

import threading
import time
from voice_runtime import (
    set_runtime_interfaces, motion_mode, march_mode, sonic_mode
)

server_instance = None

def init_command_dispatcher(server):
    global server_instance
    server_instance = server
    set_runtime_interfaces(server.process_command, server.ultrasonic_sensor)

def dispatch_command(source, command):
    print(f"[{source}] dispatch_command received: {command}")
    def send(parts):
        server_instance.process_command(parts)

    def send_str(cmd_string):
        send(cmd_string.strip().split("#"))

    if isinstance(command, list):
        for cmd in command:
            dispatch_command(source, cmd)
            time.sleep(0.6)
        send_str("CMD_MOVE#1#0#0#8#0")
        return

    if not isinstance(command, str):
        print(f"[{source}] Invalid command type: {command}")
        return

    if command.startswith("CMD_MOVE"):
        send_str(command)
        time.sleep(0.6)
        send_str("CMD_MOVE#1#0#0#8#0")
        return

    elif command.startswith("CMD_HEAD"):
        send_str(command)
        return

    elif command.startswith("CMD_SERVOPOWER"):
        send_str(command)
        return

    elif command == "CMD_RELAX":
        send(["CMD_RELAX"])
        return
    
    elif command.startswith("CMD_ATTITUDE"):
        send_str(command)
        return

    elif command.startswith("CMD_POSITION"):
        send_str(command)
        return
    
    elif command.startswith("CMD_IMU_STATUS"):
        send_str(command)
        return
    
    print(f"[{source}] Unknown or unhandled command: {command}")
