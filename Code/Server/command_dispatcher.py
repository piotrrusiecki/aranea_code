import threading
import time
from command import COMMAND as cmd
from robot_routines import (
    march_forward, march_left, march_right, march_back,
    run_forward, run_left, run_right, run_back,
    sonic_monitor_loop, shutdown_sequence, prepare_for_calibration, exit_calibration
)

server_instance = None

def init_command_dispatcher(server):
    global server_instance
    server_instance = server

def dispatch_command(source, command):
    print(f"[{source}] dispatch_command received: {command}")

    def send(parts):
        server_instance.process_command(parts)

    def send_str(cmd_string):
        send(cmd_string.strip().split("#"))

    # Routine function map
    routine_commands = {
        "march_forward": march_forward,
        "march_left": march_left,
        "march_right": march_right,
        "march_back": march_back,
        "run_forward": run_forward,
        "run_left": run_left,
        "run_right": run_right,
        "run_back": run_back,
        "start_sonic": sonic_monitor_loop,
        "stop_sonic": None,   # handled inline
        "shutdown": shutdown_sequence,
        "stop_motion": None,  # handled inline
        "prep_calibration": prepare_for_calibration,
        "exit_calibration": exit_calibration
    }

    # Support for both single and batch commands (as string or list)
    if isinstance(command, list):
        if command and isinstance(command[0], str) and command[0].startswith("CMD_"):
            send(command)
            return
        for cmd_item in command:
            dispatch_command(source, cmd_item)
            time.sleep(0.6)
        return

    if not isinstance(command, str):
        print(f"[{source}] Invalid command type: {command}")
        return

    # --- Routine triggers ---
    if command in routine_commands:

        # --- Start Sonic Mode ---
        if command == "start_sonic":
            if not server_instance.robot_state.get_flag("sonic_state"):
                print("Starting sonic mode...")
                server_instance.robot_state.set_flag("sonic_state", True)
                threading.Thread(
                    target=sonic_monitor_loop,
                    args=(send, server_instance.ultrasonic_sensor, lambda: server_instance.robot_state.get_flag("sonic_state")),
                    daemon=True
                ).start()
            else:
                print("Sonic mode already active.")
            return

        # --- Stop Sonic Mode ---
        if command == "stop_sonic":
            if server_instance.robot_state.get_flag("sonic_state"):
                print("Stopping sonic mode...")
                server_instance.robot_state.set_flag("sonic_state", False)
            else:
                print("Sonic mode was not active.")
            return

        # --- Stop Motion Loops ---
        if command == "stop_motion":
            if server_instance.robot_state.get_flag("motion_state"):
                print("Stopping motion loop...")
                server_instance.robot_state.set_flag("motion_state", False)
                send_str(f"{cmd.CMD_MOVE}#1#0#0#8#0")
                send_str(f"{cmd.CMD_LED}#0#0#0")
                send_str(f"{cmd.CMD_HEAD}#1#90")
            else:
                print("Motion was not active.")
            return

        # --- Shutdown Routine ---
        if command == "shutdown":
            print("Running shutdown sequence...")
            shutdown_sequence(send)
            return

        if command in {"prep_calibration", "exit_calibration"}:
            routine_commands[command](
                send, server_instance.control_system, server_instance.robot_state
            )
            return

        # --- Start Motion Routines (march/run) ---
        if command in {
            "march_forward", "march_left", "march_right", "march_back",
            "run_forward", "run_left", "run_right", "run_back"
        }:
            # Always forcibly clear stale motion state before new routine
            if server_instance.robot_state.get_flag("motion_state"):
                print("Motion already active or stuck, forcibly resetting state before starting new motion.")
                server_instance.robot_state.set_flag("motion_state", False)
                time.sleep(0.1)
            # --- KEY FIX HERE ---
            if command in {"march_back", "run_back"}:
                use_sensor = False
            else:
                use_sensor = server_instance.robot_state.get_flag("sonic_state")
            print(f"Starting routine: {command} (safety {'ON' if use_sensor else 'OFF'})")
            server_instance.robot_state.set_flag("motion_state", True)
            routine_fn = routine_commands[command]
            threading.Thread(
                target=routine_fn,
                args=(send, server_instance.ultrasonic_sensor, lambda: server_instance.robot_state.get_flag("motion_state"),
                      server_instance.robot_state, use_sensor),
                daemon=True
            ).start()
            return

    # --- Low-level commands ---
    if command.startswith(cmd.CMD_MOVE):
        send_str(command)
        time.sleep(0.6)
        send_str(f"{cmd.CMD_MOVE}#1#0#0#8#0")
        return

    elif command.startswith(cmd.CMD_HEAD):
        send_str(command)
        return

    elif command.startswith(cmd.CMD_SERVOPOWER):
        send_str(command)
        return

    elif command == cmd.CMD_RELAX:
        send([cmd.CMD_RELAX])
        return

    elif command.startswith(cmd.CMD_ATTITUDE):
        send_str(command)
        return

    elif command.startswith(cmd.CMD_POSITION):
        send_str(command)
        return

    elif command.startswith(cmd.CMD_IMU_STATUS):
        send_str(command)
        return
    
    elif command.startswith(cmd.CMD_CALIBRATION):
        send_str(command)
        return

    print(f"[{source}] Unknown or unhandled command: {command}")