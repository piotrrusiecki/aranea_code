import threading
import time
import logging
from command import COMMAND as cmd
from config.robot_config import DRY_RUN
from command_dispatcher_core import routine_commands, symbolic_commands, server_instance
from command_dispatcher_utils import send_str
from robot_routines import sonic_monitor_loop

logger = logging.getLogger("dispatcher.logic")

known_simple_commands = [
    cmd.CMD_MOVE,
    cmd.CMD_HEAD,
    cmd.CMD_SERVOPOWER,
    cmd.CMD_ATTITUDE,
    cmd.CMD_POSITION,
    cmd.CMD_IMU_STATUS,
    cmd.CMD_CALIBRATION,
]


def init_command_dispatcher(server):
    global server_instance
    server_instance = server
    logger.info("Dispatcher initialized with server instance: %s", bool(server))


def dispatch_command(source, command):
    logger.info("[%s] dispatch_command received: %s", source, command)

    def send(parts):
        if DRY_RUN:
            logger.debug("[%s] DRY_RUN active: would send %s", source, parts)
        else:
            logger.info("[%s] Dispatching: %s", source, parts)
            server_instance.process_command(parts)

    if isinstance(command, list):
        logger.debug("[%s] Processing list of commands (%d items)", source, len(command))
        if command and isinstance(command[0], str) and command[0].startswith("CMD_"):
            logger.debug("[%s] Single CMD_ list detected. Sending directly.", source)
            send(command)
            return
        for cmd_item in command:
            logger.debug("[%s] Sequential dispatch of subcommand: %s", source, cmd_item)
            dispatch_command(source, cmd_item)
            time.sleep(0.6)
        return

    if not isinstance(command, str):
        logger.warning("[%s] Invalid command type: %s", source, command)
        return

    if command in symbolic_commands:
        logger.info("[%s] Executing symbolic command: %s", source, command)
        symbolic_commands[command](send)
        return

    if command in routine_commands:
        logger.info("[%s] Routine command matched: %s", source, command)

        # Group 1: Gait routines
        if command in {
            "routine_march_forward", "routine_march_left", "routine_march_right", "routine_march_back",
            "routine_run_forward", "routine_run_left", "routine_run_right", "routine_run_back"
        }:
            if server_instance.robot_state.get_flag("motion_state"):
                logger.warning("[%s] motion_state already True. Forcibly resetting before new motion.", source)
                server_instance.robot_state.set_flag("motion_state", False)
                time.sleep(0.1)

            use_sensor = (
                False if command in {"routine_march_back", "routine_run_back"}
                else server_instance.robot_state.get_flag("sonic_state")
            )

            logger.info("[%s] Starting gait routine: %s | safety=%s", source, command, "ON" if use_sensor else "OFF")
            server_instance.robot_state.set_flag("motion_state", True)

            threading.Thread(
                target=routine_commands[command],
                args=(
                    send,
                    server_instance.ultrasonic_sensor,
                    lambda: server_instance.robot_state.get_flag("motion_state"),
                    server_instance.robot_state,
                    use_sensor,
                ),
                daemon=True
            ).start()
            return

        # Group 2: Turn routines (use speed)
        elif command in {"routine_turn_left", "routine_turn_right"}:
            try:
                speed = server_instance.robot_state.get_flag("move_speed") or 5
            except Exception as e:
                logger.warning("[%s] move_speed read failed: %s", source, e)
                speed = 5

            logger.info("[%s] Executing turn routine: %s | speed=%d", source, command, speed)
            routine_commands[command](send, steps=1, speed=speed)
            return

        # Group 3: Calibration
        elif command in {"sys_prep_calibration", "sys_exit_calibration"}:
            logger.info("[%s] Executing calibration control: %s", source, command)
            routine_commands[command](send, server_instance.control_system, server_instance.robot_state)
            return

        # Group 4: System control
        elif command == "sys_stop_motion":
            if server_instance.robot_state.get_flag("motion_state"):
                logger.info("[%s] Stopping motion loop.", source)
                server_instance.robot_state.set_flag("motion_state", False)
                send([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
                send([cmd.CMD_LED, "0", "0", "0"])
                send([cmd.CMD_HEAD, "1", "90"])
            else:
                logger.info("[%s] Motion already inactive.", source)
            return

        elif command == "sys_start_sonic":
            if not server_instance.robot_state.get_flag("sonic_state"):
                logger.info("[%s] Enabling sonic mode...", source)
                server_instance.robot_state.set_flag("sonic_state", True)
                threading.Thread(
                    target=sonic_monitor_loop,
                    args=(send, server_instance.ultrasonic_sensor, lambda: server_instance.robot_state.get_flag("sonic_state")),
                    daemon=True
                ).start()
            else:
                logger.info("[%s] Sonic mode already active.", source)
            return

        elif command == "sys_stop_sonic":
            if server_instance.robot_state.get_flag("sonic_state"):
                logger.info("[%s] Disabling sonic mode.", source)
                server_instance.robot_state.set_flag("sonic_state", False)
            else:
                logger.info("[%s] Sonic mode already inactive.", source)
            return

        elif command == "sys_shutdown":
            logger.info("[%s] Executing shutdown sequence.", source)
            routine_commands[command](send)
            return

        elif command == "sys_start_servo_test":
            logger.info("[%s] Starting servo test loop", source)
            routine_commands[command]()  # or directly: start_servo_test()
            return

        elif command == "sys_stop_servo_test":
            logger.info("[%s] Stopping servo test loop", source)
            routine_commands[command]()  # or directly: stop_servo_test()
            return

    if command.startswith("diag_"):
        parts = command.split("#")
        try:
            from command_dispatcher_registry import DIAG_COMMANDS
            from command_dispatcher_symbolic import handle_diag_set_servo

            if parts[0] == "diag_set_servo":
                handle_diag_set_servo(parts[1:], source)
                return
            else:
                logger.warning("[%s] Unknown diag_ command: %s", source, command)
        except Exception as e:
            logger.error("[%s] Error handling diag command: %s", source, e)
        return

    # CMD-style command fallback
    for prefix in known_simple_commands:
        if command.startswith(prefix):
            if prefix == cmd.CMD_MOVE:
                logger.debug("[%s] Detected direct CMD_MOVE. Forcing motion_state=False", source)
                server_instance.robot_state.set_flag("motion_state", False)
            logger.info("[%s] Direct command fallback matched: %s", source, command)
            send_str(command, server_instance.process_command)
            return


    # Special case: CMD_RELAX
    if command == cmd.CMD_RELAX:
        logger.info("[%s] Relax command issued", source)
        send([cmd.CMD_RELAX])
        return

    # Battery query
    elif command.startswith(cmd.CMD_BATTERY):
        try:
            battery = server_instance.read_battery_voltage()
            if battery:
                logger.info("[%s] Battery values read: %s", source, battery)
                return ["CMD_BATTERY", *battery]
            else:
                logger.error("[%s] Battery read returned empty or None", source)
                return ["CMD_BATTERY", "ERROR"]
        except Exception as e:
            logger.error("[%s] Battery read failed: %s", source, e)
            return ["CMD_BATTERY", "ERROR"]
        # Symbolic diagnostic commands


    # Unknown command fallback
    logger.warning("[%s] Unknown or unhandled command: %s", source, command)


def get_supported_commands():
    logger.debug("get_supported_commands() called")
    return list(symbolic_commands.keys()) + list(routine_commands.keys())
