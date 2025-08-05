import threading
import time
import logging
from typing import TYPE_CHECKING, Optional
from constants_commands import COMMAND as cmd
from config.robot_config import DRY_RUN
from command_dispatcher_core import routine_commands, symbolic_commands
from command_dispatcher_utils import send_str
from robot_routines import sonic_monitor_loop

if TYPE_CHECKING:
    from hardware_server import Server

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


class CommandDispatcher:
    """Singleton class to manage command dispatcher state."""
    _instance: Optional['CommandDispatcher'] = None
    _server_instance: Optional['Server'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_server(cls) -> 'Server':
        """Get the server instance with proper None checking."""
        if cls._server_instance is None:
            logger.error("Server instance not initialized! Call init_command_dispatcher() first.")
            raise RuntimeError("Command dispatcher not initialized")
        return cls._server_instance
    
    @classmethod
    def set_server(cls, server: 'Server') -> None:
        """Set the server instance."""
        cls._server_instance = server


def init_command_dispatcher(server):
    """Initialize the command dispatcher with server instance."""
    CommandDispatcher.set_server(server)
    logger.info("Dispatcher initialized with server instance: %s", bool(server))


def _create_send_function(source, server):
    """Create a send function with proper logging for a given source."""
    def send(parts):
        if DRY_RUN:
            logger.debug("[%s] DRY_RUN active: would send %s", source, parts)
        else:
            logger.info("[%s] Dispatching: %s", source, parts)
            server.process_command(parts)
    return send


def _get_server():
    """Get the server instance with proper None checking."""
    return CommandDispatcher.get_server()


def _handle_command_list(source, command):
    """Handle dispatch of command lists (arrays of commands)."""
    logger.debug("[%s] Processing list of commands (%d items)", source, len(command))
    
    # Handle single CMD_ list - send directly to hardware
    if command and isinstance(command[0], str) and command[0].startswith("CMD_"):
        logger.debug("[%s] Single CMD_ list detected. Sending directly.", source)
        send = _create_send_function(source, _get_server())
        send(command)
        return True
    
    # Handle sequential command execution
    for cmd_item in command:
        logger.debug("[%s] Sequential dispatch of subcommand: %s", source, cmd_item)
        dispatch_command(source, cmd_item)
        time.sleep(0.6)
    return True


def _handle_symbolic_commands(source, command):
    """Handle symbolic commands - simple lookup and execution."""
    if command not in symbolic_commands:
        return False
        
    logger.info("[%s] Executing symbolic command: %s", source, command)
    send = _create_send_function(source, _get_server())
    symbolic_commands[command](send)
    return True


def _handle_gait_routines(source, command, send):
    """Handle gait movement routines (march/run commands)."""
    gait_commands = {
        "routine_march_forward", "routine_march_left", "routine_march_right", "routine_march_back",
        "routine_run_forward", "routine_run_left", "routine_run_right", "routine_run_back"
    }
    
    if command not in gait_commands:
        return False
        
    # Reset motion state if already active
    if _get_server().robot_state.get_flag("motion_state"):
        logger.warning("[%s] motion_state already True. Forcibly resetting before new motion.", source)
        _get_server().robot_state.set_flag("motion_state", False)
        time.sleep(0.1)

    # Determine sensor usage (disabled for backward movements)
    use_sensor = (
        False if command in {"routine_march_back", "routine_run_back"}
        else _get_server().robot_state.get_flag("sonic_state")
    )

    logger.info("[%s] Starting gait routine: %s | safety=%s", source, command, "ON" if use_sensor else "OFF")
    _get_server().robot_state.set_flag("motion_state", True)

    # Start routine in separate thread
    threading.Thread(
        target=routine_commands[command],
        args=(
            send,
            _get_server().ultrasonic_sensor,
            lambda: _get_server().robot_state.get_flag("motion_state"),
            _get_server().robot_state,
            use_sensor,
        ),
        daemon=True
    ).start()
    return True


def _handle_turn_routines(source, command, send):
    """Handle turning routines (left/right turns)."""
    if command not in {"routine_turn_left", "routine_turn_right"}:
        return False
        
    try:
        speed = _get_server().robot_state.get_flag("move_speed") or 5
    except Exception as e:
        logger.warning("[%s] move_speed read failed: %s", source, e)
        speed = 5

    logger.info("[%s] Executing turn routine: %s | speed=%d", source, command, speed)
    routine_commands[command](send, steps=1, speed=speed)
    return True


def _handle_system_control_routines(source, command, send):
    """Handle system control routines (motion, sonic, shutdown, etc.)."""
    
    if command == "sys_stop_motion":
        if _get_server().robot_state.get_flag("motion_state"):
            logger.info("[%s] Stopping motion loop.", source)
            _get_server().robot_state.set_flag("motion_state", False)
            send([cmd.CMD_MOVE, "1", "0", "0", "8", "0"])
            send([cmd.CMD_LED, "0", "0", "0"])
            send([cmd.CMD_HEAD, "1", "90"])
        else:
            logger.info("[%s] Motion already inactive.", source)
        return True

    elif command == "sys_start_sonic":
        if not _get_server().robot_state.get_flag("sonic_state"):
            logger.info("[%s] Enabling sonic mode...", source)
            _get_server().robot_state.set_flag("sonic_state", True)
            threading.Thread(
                target=sonic_monitor_loop,
                args=(send, _get_server().ultrasonic_sensor, lambda: _get_server().robot_state.get_flag("sonic_state")),
                daemon=True
            ).start()
        else:
            logger.info("[%s] Sonic mode already active.", source)
        return True

    elif command == "sys_stop_sonic":
        if _get_server().robot_state.get_flag("sonic_state"):
            logger.info("[%s] Disabling sonic mode.", source)
            _get_server().robot_state.set_flag("sonic_state", False)
        else:
            logger.info("[%s] Sonic mode already inactive.", source)
        return True

    elif command == "sys_shutdown":
        logger.info("[%s] Executing shutdown sequence.", source)
        routine_commands[command](send)
        return True

    elif command == "sys_start_servo_test":
        logger.info("[%s] Starting servo test loop", source)
        routine_commands[command]()  # No send function needed
        return True

    elif command == "sys_stop_servo_test":
        logger.info("[%s] Stopping servo test loop", source)
        routine_commands[command]()  # No send function needed
        return True
        
    return False


def _handle_calibration_routines(source, command, send):
    """Handle calibration setup and teardown routines."""
    if command not in {"sys_prep_calibration", "sys_exit_calibration"}:
        return False
        
    logger.info("[%s] Executing calibration control: %s", source, command)
    routine_commands[command](send, _get_server().control_system, _get_server().robot_state)
    return True


def _handle_routine_commands(source, command):
    """Handle all routine commands by delegating to specific handlers."""
    if command not in routine_commands:
        return False
        
    logger.info("[%s] Routine command matched: %s", source, command)
    send = _create_send_function(source, _get_server())
    
    # Try each routine handler in logical order
    handlers = [
        _handle_gait_routines,
        _handle_turn_routines,
        _handle_calibration_routines,
        _handle_system_control_routines,
    ]
    
    for handler in handlers:
        if handler(source, command, send):
            return True
    
    # If we get here, the command is in routine_commands but no handler processed it
    logger.warning("[%s] Routine command '%s' found but no handler processed it", source, command)
    return False


def _handle_diag_set_servo(args, source="unknown"):
    """Handle diag_set_servo command - set servo to specific angle."""
    if len(args) != 2:
        logger.error("[%s] diag_set_servo requires 2 arguments: channel and angle", source)
        return False

    try:
        channel = int(args[0])
        angle = int(args[1])
        
        from actuator_servo import Servo
        servo = Servo()
        servo.set_servo_angle(channel, angle)
        
        logger.info("[%s] Diagnostic servo set: channel %d → angle %d", source, channel, angle)
        return True
    except Exception as e:
        logger.error("[%s] Error in diag_set_servo: %s", source, e)
        return False


def _handle_diagnostic_commands(source, command):
    """Handle diagnostic commands (diag_ prefixed)."""
    if not command.startswith("diag_"):
        return False
        
    parts = command.split("#")
    try:
        if parts[0] == "diag_set_servo":
            return _handle_diag_set_servo(parts[1:], source)
        else:
            logger.warning("[%s] Unknown diag_ command: %s", source, command)
            return True  # Still handled, just unknown
    except Exception as e:
        logger.error("[%s] Error handling diag command: %s", source, e)
        return True  # Still handled, just errored


def _handle_cmd_style_commands(source, command):
    """Handle traditional CMD-style commands (CMD_MOVE, CMD_POSITION, etc.)."""
    # Check if command starts with any known simple command prefix
    for prefix in known_simple_commands:
        if command.startswith(prefix):
            parts = command.split("#")
            cmd_name = parts[0]
            params = parts[1:]

            if cmd_name == cmd.CMD_MOVE:
                return _handle_cmd_move(source, command, cmd_name, params)
            
            elif cmd_name in {cmd.CMD_POSITION, cmd.CMD_ATTITUDE, cmd.CMD_BALANCE, cmd.CMD_CALIBRATION}:
                return _handle_cmd_queue_commands(source, command, cmd_name, params)
            
            elif cmd_name == cmd.CMD_SERVOPOWER:
                return _handle_cmd_servopower(source, command, cmd_name, params)
            
            else:
                # Generic fallback for other CMD commands
                logger.info("[%s] Sending generic CMD command: %s", source, command)
                try:
                    server = _get_server()
                    logger.info("[%s] Server instance type: %s", source, type(server))
                    logger.info("[%s] Server process_command: %s", source, server.process_command)
                    logger.info("[%s] Process_command callable: %s", source, callable(server.process_command))
                    send_str(command, server.process_command)
                    logger.info("[%s] send_str call completed successfully", source)
                except Exception as e:
                    logger.error("[%s] CRITICAL ERROR in generic CMD handling: %s", source, e)
                    import traceback
                    logger.error("[%s] Full traceback: %s", source, traceback.format_exc())
                return True
    
    return False


def _handle_cmd_move(source, command, cmd_name, params):
    """Handle CMD_MOVE commands specifically."""
    if _get_server().robot_state.get_flag("motion_state"):
        logger.debug("[%s] Detected CMD_MOVE during routine. Resetting motion_state.", source)
        _get_server().robot_state.set_flag("motion_state", False)
    
    if len(params) == 5:
        _get_server().control_system.command_queue = [cmd_name] + params
        _get_server().control_system.timeout = time.time()
        logger.info("[%s] Queued CMD_MOVE into control_system.command_queue: %s", source, [cmd_name] + params)
        return True
    else:
        logger.warning("[%s] Invalid CMD_MOVE format: %s", source, command)
        return True  # Still handled, just invalid


def _handle_cmd_queue_commands(source, command, cmd_name, params):
    """Handle commands that get queued in the control system."""
    _get_server().control_system.command_queue = [cmd_name] + params
    _get_server().control_system.timeout = time.time()
    logger.info("[%s] Queued %s into control_system.command_queue", source, command)
    return True


def _handle_cmd_servopower(source, command, _cmd_name, params):
    """Handle CMD_SERVOPOWER commands specifically."""
    if params and params[0] in {"0", "1"}:
        _get_server().robot_state.set_flag("servo_off", params[0] == "0")
        logger.info("[%s] CMD_SERVOPOWER received. servo_off set to %s", source, params[0] == "0")
    else:
        logger.warning("[%s] Invalid CMD_SERVOPOWER params: %s", source, params)
    
    # Always send the command through as well
    send_str(command, _get_server().process_command)
    return True


def _handle_special_commands(source, command):
    """Handle special case commands (CMD_RELAX, CMD_BATTERY, etc.)."""
    
    # CMD_RELAX - immediate servo relaxation
    if command == cmd.CMD_RELAX:
        logger.info("[%s] Relax command issued", source)
        send = _create_send_function(source, _get_server())
        send([cmd.CMD_RELAX])
        return True

    # CMD_BATTERY - battery voltage query
    elif command.startswith(cmd.CMD_BATTERY):
        try:
            battery = _get_server().read_battery_voltage()
            if battery:
                logger.info("[%s] Battery values read: %s", source, battery)
                return ["CMD_BATTERY", *battery]
            else:
                logger.error("[%s] Battery read returned empty or None", source)
                return ["CMD_BATTERY", "ERROR"]
        except Exception as e:
            logger.error("[%s] Battery read failed: %s", source, e)
            return ["CMD_BATTERY", "ERROR"]
    
    # Command not handled by this function
    return None


def dispatch_command(source, command):
    logger.info("[%s] dispatch_command received: %s", source, command)

    # Handle command lists
    if isinstance(command, list):
        return _handle_command_list(source, command)

    # Validate command type
    if not isinstance(command, str):
        logger.warning("[%s] Invalid command type: %s", source, command)
        return

    # Handle symbolic commands
    if _handle_symbolic_commands(source, command):
        return

    # Handle routine commands
    if _handle_routine_commands(source, command):
        return

    # Handle diagnostic commands
    if _handle_diagnostic_commands(source, command):
        return

    # Handle CMD-style commands
    if _handle_cmd_style_commands(source, command):
        return




    # Handle special case commands
    result = _handle_special_commands(source, command)
    if result is not None:
        return result


    # Unknown command fallback
    logger.warning("[%s] Unknown or unhandled command: %s", source, command)
    return False


def get_supported_commands():
    logger.debug("get_supported_commands() called")
    return list(symbolic_commands.keys()) + list(routine_commands.keys())
