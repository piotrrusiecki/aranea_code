# Aranea Robot Codebase Navigation Guide

*Generated from comprehensive analysis - Use this to quickly understand the codebase structure and key components*

## 🏗️ Architecture Overview

**Type**: Hexapod Robot Control System  
**Transformation**: PyQt5 Desktop App → Web-based Multi-interface System  
**Key Pattern**: Command Dispatcher with Multi-interface Support  

### Core Architecture Flow
```
[Web Interface] ──┐
[Voice Control] ──┼─→ [Command Dispatcher] ──→ [Server/Hardware Layer] ──→ [Physical Hardware]
[TCP Interface] ──┘                            ↕
                                        [Robot State Manager]
```

## 📁 File Structure & Responsibilities

### **Entry Points**
- `main.py` - Main application entry, threading setup, Flask integration
  - Initializes all subsystems (server, voice, web, command dispatcher)
  - Handles graceful shutdown and resource cleanup
  - Uses colored logging system

### **Core Systems**

#### **Command Dispatching** (Key Innovation)
- `command_dispatcher_logic.py` - Main dispatcher logic and command routing
  - **Refactored Architecture**: Eliminated global server instance usage with safe `_get_server()` helper
  - Type-safe server access with proper None checking and runtime validation
  - Clean separation of concerns with dependency injection patterns
- `command_dispatcher_core.py` - Registry for symbolic and routine commands  
- `command_dispatcher_registry.py` - Command registration (imports all routines)
- `command_dispatcher_symbolic.py` - Simple symbolic command execution
- `command_dispatcher_utils.py` - Utility functions for command processing

#### **Hardware Interface Layer**
- `hardware_server.py` - Hardware abstraction server (evolved from manufacturer code)
  - Command handlers for all hardware components
  - TCP socket management for legacy compatibility
  - Video streaming coordination
- `hardware_pca9685.py` - **PCA9685 I2C controller driver for servo management** ⚠️
  - **CRITICAL**: Must maintain complete register map and PWM write sequences
  - Controls 18 servos across two PCA9685 boards (0x40, 0x41)
  - Any modifications require comparison with original working code
- `hardware_spi_ledpixel.py` - SPI-based LED strip driver (Freenove SPI LED pixels)
- `hardware_rpi_ledpixel.py` - Raspberry Pi WS281X LED strip driver

#### **Sensors**
- `sensor_camera.py` - Pi camera streaming interface with video recording and frame capture
  - **Code Quality**: Optimized logging with lazy % formatting and proper Optional type annotations
- `sensor_ultrasonic.py` - Distance sensor interface
- `sensor_adc.py` - Battery voltage monitoring
- `sensor_imu.py` - Inertial measurement unit with Kalman filtering

#### **Actuators**
- `actuator_servo.py` - 18-servo hexapod control via PCA9685 I2C controllers
- `actuator_led.py` - RGB LED strip control with effects
- `actuator_buzzer.py` - Simple buzzer control

#### **Robot Control & Movement**
- `robot_control.py` - Main robot control system with condition monitoring thread
  - **Refactored Architecture**: Modular command handlers (`_handle_position_command`, `_handle_move_command`, etc.)
  - Servo angle calculations and safety checks
  - Command queue processing with dedicated handler methods
  - Auto-relax functionality
- `robot_pid.py` - PID controller for robot balance and stability
- `robot_kinematics.py` - Forward/inverse kinematics calculations
- `robot_gait.py` - Gait pattern generation (walking algorithms)
  - **Refactored Architecture**: Separated tripod/wave gait implementations with phase-specific functions
  - Clean parameter parsing and movement delta calculations
  - Modular gait execution with `_execute_tripod_gait()` and `_execute_wave_gait()`
- `robot_pose.py` - Body posture and balance calculations
- `robot_routines.py` - High-level movement routines (march, run, patrol)
- `robot_calibration.py` - Servo calibration utilities

#### **State Management**
- `robot_state.py` - Thread-safe centralized state management
  - Flags: motion_state, sonic_state, calibration_mode, servo_off
  - Thread-safe access with locks
  - State exclusivity logic (e.g., calibration disables motion)

#### **Web Interface**
- `web_server.py` - Flask application factory and routes
  - **Refactored Architecture**: Modular route handlers extracted from monolithic `create_app()` function
  - Handler factories with closures for dependency injection (`create_voice_handler`, `create_status_handler`, etc.)
  - Clean separation of concerns for easier testing and maintenance
- `web_interface/templates/` - Jinja2 HTML templates
- `web_interface/static/` - CSS, JS, Bootstrap assets
- Routes: `/` (main), `/command` (API), `/voice` (control), `/status`

#### **Voice Control System**
- `voice_manager.py` - Voice system lifecycle management
  - **Refactored Architecture**: Class-based `VoiceManager` with instance state management  
  - Eliminated global variables for thread-safe voice control lifecycle
  - Backward-compatible wrapper functions maintain existing API
- `voice_control.py` - Vosk speech recognition integration
- `voice_command_handler.py` - Voice command processing and routing
- `config/voice/eo.py` - Esperanto command mappings
- `config/voice/__init__.py` - Multi-language support framework

#### **Configuration & Constants**
- `config/robot_config.py` - Centralized configuration
  - Voice settings, logging colors, debug flags
  - Hardware-specific settings
- `config/parameter.py` - Parameter management utility
  - Hardware detection and validation
  - Configuration file management
- `constants_commands.py` - Command constants and definitions
- `params.json` - Runtime parameters (PCB version, Pi version)

## 🔧 Key Technical Details

### **Threading Model**
- **Main Thread**: Flask web server
- **Video Thread**: Camera streaming (daemon)
- **Command Thread**: TCP command processing (daemon)  
- **Voice Thread**: Speech recognition (daemon)
- **Control Thread**: Robot condition monitoring
- **Routine Threads**: Movement execution (created on-demand)

### **Command Flow**
1. **Input** → Web UI, Voice, or TCP
2. **Dispatcher** → Routes to symbolic or routine commands
3. **Execution** → Hardware commands via hardware_server.py
4. **State Update** → RobotState flags updated
5. **Feedback** → LEDs, buzzer, or response data

### **Command Execution Patterns** (Critical Architecture)

#### **Single Action Commands** (`task_*` symbols)
- **Purpose**: Execute once and stop (step forward, turn, look, lights)
- **Pattern**: Movement command + Reset command (matches web interface)
- **Example**: `task_step_forward` → `CMD_MOVE#1#0#35#8#0` + `CMD_MOVE#1#0#0#8#0`
- **Web Interface**: Uses `onmousedown`/`onmouseup` with `sendMove(x,y)` + `sendMove(0,0)`
- **Voice Commands**: Implemented with `_send_move_with_reset()` helper function
- **Why**: `CLEAR_MOVE_QUEUE_AFTER_EXEC = False` means commands loop without explicit reset

#### **Continuous Routines** (`routine_*` commands) 
- **Purpose**: Run until stopped (march, run, patrol)
- **Pattern**: Background threading with `motion_loop()` + `motion_state` flag
- **Example**: `routine_march_forward` → Thread continuously sends individual `CMD_MOVE` commands
- **State Management**: `motion_state = True` during execution, `False` to stop
- **Voice Integration**: All voice commands route through `dispatch_command()` (no hardcoded bypasses)

### **Hardware Communication**
- **Servos**: I2C via PCA9685 controllers (0x40, 0x41)
- **LEDs**: SPI/GPIO depending on PCB version
- **Sensors**: GPIO for ultrasonic, I2C for IMU
- **Camera**: CSI interface with Pi camera module

### **Safety Systems**
- Obstacle detection with ultrasonic sensor
- Servo angle validation and clamping
- Motion state exclusivity (can't calibrate while moving)
- Auto-stop on sensor detection during forward motion
- Battery voltage monitoring with alerts

## 🎯 Current State (vs Original Manufacturer Code)

### **Major Transformations Completed**
- ❌ PyQt5 desktop GUI → ✅ Web interface
- ❌ No voice control → ✅ Vosk-based voice recognition  
- ❌ Direct command parsing → ✅ Command dispatcher pattern
- ❌ Print statements → ✅ Comprehensive logging
- ❌ Scattered state → ✅ Centralized RobotState
- ❌ Monolithic server.py → ✅ Modular architecture
- ❌ Global variables & state → ✅ Class-based architecture with proper encapsulation

### **Performance Issues Identified**
- **Movement slowdown**: Related to command queue retention and SendMove(0,0) in move.js
- **Servo bottleneck**: 18 sequential I2C calls per movement frame
- **Thread contention**: Condition monitor loop overhead

### **Critical Hardware Driver Issues (RESOLVED)**
- **Missing PWM register write**: `hardware_pca9685.py` was missing `self.write(self.__LED0_OFF_H + 4 * channel, off >> 8)` in `set_pwm()` method
  - **Symptoms**: Erratic servo behavior, twitching, power interference affecting multiple servos
  - **Root cause**: Incomplete PWM timing data sent to PCA9685 chips
  - **Fix**: Restored missing register write line (Dec 2024)
- **Missing register constants**: DeepSource cleanup removed essential PCA9685 constants
  - **Removed**: `__SUBADR1/2/3`, `__ALLLED_ON_L/H`, `__ALLLED_OFF_L/H` register definitions
  - **Impact**: Incomplete hardware register map, potential future compatibility issues
  - **Fix**: Restored all register constants by comparing with original working code
- **Hardware failure**: Servo on channel 8 (Leg 3, middle joint) failed due to long-term degradation
  - **Accelerated by**: Software PWM bug creating additional stress on already-weak servo
  - **Solution**: Servo replacement + software fix resolved all stability issues

### **Code Quality Improvements (COMPLETED - Dec 2024)**
- **Global variable elimination**: Removed all problematic global statements (PYL-W0603 warnings)
  - **`voice_manager.py`**: Converted to class-based `VoiceManager` with instance state
  - **`command_dispatcher_logic.py`**: Added safe server instance access with `_get_server()` helper
  - **Impact**: Improved thread safety, better testability, cleaner architecture
  - **Result**: Zero linting errors, enhanced IDE type checking, maintained backward compatibility

### **Configuration Flags (Important)**
- `CLEAR_MOVE_QUEUE_AFTER_EXEC = False` - **CRITICAL**: Legacy compatibility with factory firmware
  - `False` → Commands loop indefinitely (requires explicit reset commands)
  - `True` → Commands execute once and auto-clear (future enhancement)
  - **Why False**: Maintains compatibility with original manufacturer client patterns
  - **Impact**: Single commands need reset pattern (`CMD_MOVE` + `CMD_MOVE#0#0#0`)
- `DEBUG_LEGS = True` - Enables detailed leg position logging
- `DRY_RUN = False` - Set to True for testing without hardware
- `VOICE_BLOCKSIZE = 8000` - Audio buffer size (increased from 4000 to reduce overflow)

### **Hardware Driver Best Practices (CRITICAL)**
- **⚠️ NEVER remove hardware register constants** based on automated tools (DeepSource, pylint, etc.)
- **Complete register maps required**: Even "unused" constants are needed for hardware compatibility
- **Hardware drivers need all registers**: Missing constants can cause subtle hardware failures
- **When modifying hardware files**: Always compare with original working code before deployment
- **PWM register writes must be complete**: All 4 registers (ON_L, ON_H, OFF_L, OFF_H) required per channel
- **Test hardware changes immediately**: Hardware bugs can cause cumulative damage over time

## 🚀 Development Priorities (Reference roadmap.md)

### **Phase 1: Field Autonomy** (HIGH)
- AP fallback mode for standalone operation
- Performance optimization (movement slowdown fix)

### **Phase 2: Multi-Language Voice** (HIGH)  
- German, Spanish, French, Polish voice models
- Runtime language switching with source language commands
- Pattern: "[spider in source] [target language in source]"

### **Phase 3: System Refinement** (MEDIUM)
- Enhanced error handling
- Mobile UI improvements  
- Performance monitoring dashboard

## 🔍 Quick Navigation Tips

### **For Movement Issues**
- Start with: `robot_gait.py`, `robot_control.py`, `robot_routines.py`
- Check: `config/robot_config.py` for timing flags
- Monitor: Servo communication in `actuator_servo.py`

### **For Voice Features**
- Core: `voice_control.py`, `voice_manager.py`
- Commands: `config/voice/eo.py` (template for other languages)  
- Integration: `command_dispatcher_logic.py`
- **Command Registration**: `command_dispatcher_registry.py` (all voice commands route through dispatcher)

### **For Web Interface**
- Backend: `web_server.py`
- Frontend: `web_interface/templates/index.html`
- API: `/command` endpoint for all robot control

### **For Hardware Issues**
- Hardware layer: `hardware_server.py` (evolved manufacturer code)
- Individual components: `actuator_servo.py`, `actuator_led.py`, `sensor_camera.py`, etc.
- Calibration: `robot_calibration.py`

### **For State Management**
- Central state: `robot_state.py`
- State monitoring: `robot_control.py` condition_monitor()
- Flag interactions: Check exclusivity logic

## 📝 Code Patterns & Conventions

### **Logging**
```python
logger = logging.getLogger("module.submodule")
logger.info("Action completed: %s", result)
```

### **Command Registration**
```python
# In command_dispatcher_registry.py

# Single action commands (with reset pattern)
"task_step_forward": lambda send: _send_move_with_reset(send, [cmd.CMD_MOVE, "1", "0", "35", "8", "0"]),

# Non-movement commands (no reset needed)
"task_light_red": lambda send: send([cmd.CMD_LED, "255", "0", "0"]),

# Routine commands (registered in routine_commands dict)
routine_commands["routine_march_forward"] = make_motion_routine(2, 0, 35, 8, 90)
```

### **State Checking**
```python
if robot_state.get_flag("motion_state"):
    # Safe to execute movement
```

### **Hardware Commands**
```python
# Via hardware server instance
hardware_server.servo_controller.set_servo_angle(channel, angle)
hardware_server.led_controller.process_light_command(parts)
```

## 🐛 Known Issues & Workarounds

1. **Command Looping**: Single movement commands loop infinitely without reset commands
   - **Root Cause**: `CLEAR_MOVE_QUEUE_AFTER_EXEC = False` (maintained for legacy compatibility)
   - **Solution**: Always send reset command (`CMD_MOVE#1#0#0#8#0`) after movement commands
   - **Implementation**: Voice uses `_send_move_with_reset()`, Web uses `onmouseup="sendMove(0,0)"`

2. **Voice Command Attribution Error**: `'NoneType' object has no attribute 'process_command'`
   - **Root Cause**: Symbolic commands trying to access `server_instance` directly instead of using `send` parameter
   - **Solution**: Use `lambda send: send([...])` pattern in command registration

3. **Audio Input Overflow**: Voice control logs frequent "input overflow" messages
   - **Mitigation**: Increased `VOICE_BLOCKSIZE` from 4000 to 8000, added log throttling at DEBUG level

4. **Legacy Compatibility**: Some manufacturer patterns retained intentionally for fallback compatibility

5. **Logging Format Performance**: Some modules use inefficient logging formats
   - **Issue**: Using f-strings/concatenation in logging calls (e.g., `sensor_camera.py`)
   - **Bad**: `logger.info(f"Started recording video to {filename}")` 
   - **Good**: `logger.info("Started recording video to %s", filename)`
   - **Why**: Lazy % formatting avoids string construction when logging is disabled
   - **Action**: Review and fix logging calls throughout codebase

6. **Code Complexity (RESOLVED)**: Previously had high cyclomatic complexity functions
   - **Fixed**: `create_app()` in web_server.py (complexity 30 → modular route handlers)
   - **Fixed**: `run_gait()` in robot_gait.py (complexity 28 → structured gait patterns)
   - **Fixed**: `condition_monitor()` in robot_control.py (complexity 25 → command handler methods)
   - **Benefit**: Significantly improved maintainability and testability

7. **IMU Attribute Access Error (FIXED)**: Critical runtime bug in robot_control.py
   - **Issue**: Incorrect attribute names `Error_value_accel_data`/`Error_value_gyro_data` (Dec 2024)
   - **Actual**: Should be `error_accel_data`/`error_gyro_data` per sensor_imu.py
   - **Fix**: Corrected attribute names in line 322
   - **Impact**: Robot would crash during IMU calibration without this fix

8. **Type Safety Improvements (FIXED)**: Multiple type checker warnings resolved
   - **Issue**: Float/int assignment warning in leg length calculations
   - **Fix**: Initialize `leg_lengths = [0.0] * 6` instead of `[0] * 6`
   - **Issue**: None-type access warnings in command_dispatcher_symbolic.py  
   - **Fix**: Added proper None checks with early return and local variable assignment

9. **Camera Sensor Code Quality (FIXED)**: Logging and type annotation improvements
   - **Issue**: Eager string formatting in logging calls (performance impact)
   - **Fix**: Converted f-string logging to lazy % formatting for better performance
   - **Issue**: Incorrect type annotations causing compatibility and None-type warnings
   - **Fix**: Added `Optional` types and improved method signatures for proper type safety
   - **Files**: sensor_camera.py improvements following Python logging best practices

## 💻 Development Environment Setup

### **Windows Development Configuration**
For developing on Windows while deploying to Raspberry Pi hardware:

#### **IDE Configuration (.vscode/settings.json)**
```json
{
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingImports": "none"
    },
    "python.analysis.ignore": [
        "**/smbus", "**/gpiozero", "**/flask"
    ],
    "python.linting.pylintArgs": ["--disable=import-error"]
}
```

#### **Type Stub Files (.stubs/)**
Created stub files for hardware-specific libraries:
- `.stubs/smbus.pyi` - I2C communication types
- `.stubs/gpiozero.pyi` - GPIO control types  
- `.stubs/flask.pyi` - Web framework types

**⚠️ IMPORTANT**: Do not deploy stub files to robot! These are development-only tools.

#### **Deployment Guidelines**
```
✅ Deploy to Robot:     ❌ Don't Deploy:
- All .py files         - .stubs/ directory
- config/ directory     - .vscode/ directory  
- web_interface/        - pyrightconfig.json
- params.json           - __pycache__/
```

### **Attribute Initialization Patterns**

#### **Socket Management Best Practices**
After comprehensive attribute initialization fixes (December 2024), established patterns for socket-related attributes:

**Problem**: PYL-W0201 warnings for attributes defined outside `__init__` caused by socket assignments in runtime methods.

**Solution Pattern**:
```python
class NetworkServer:
    def __init__(self):
        # Initialize all socket attributes as None with type hints
        self.video_socket: Optional[socket.socket] = None
        self.command_socket: Optional[socket.socket] = None
        self.video_connection: Optional[io.BufferedWriter] = None
        self.command_connection: Optional[socket.socket] = None
        
    def start_server(self):
        # Set actual socket instances during runtime
        self.video_socket = socket.socket()
        
    def stop_server(self):
        # Defensive cleanup with None checks
        if hasattr(self, 'video_connection') and self.video_connection is not None:
            self.video_connection.close()
```

**Key Lessons**:
- Always initialize socket attributes to None in `__init__` with proper type hints
- Use `Optional[Type]` annotations for runtime-assigned attributes
- Add defensive None checks before socket operations
- Maintain existing `hasattr()` checks for backward compatibility
- Risk assessment: Attribute initialization fixes are low-risk in controlled startup sequences

#### **Type Safety Enhancements**
- `StreamingOutput.write()` - Fixed return type to match `BufferedIOBase` interface
- `ADC.read_battery_voltage()` - Corrected return type annotation to `tuple[float, float]`
- Import pattern for utility functions: `from robot_kinematics import restrict_value`

## 🌐 Network & Remote Access

### WiFi Configuration  
- **Priority System**: NetworkManager-based with phone hotspot (100) > home network (50) > wired (-999)
- **Remote Access**: Mobile hotspot enables field operations via web interface
- **Documentation**: Complete setup guide in `doc_wifi.md`
- **Auto-Failover**: Seamless switching between networks based on availability

### Service Management
- **Systemd Service**: `.services/aranea-server.service` for auto-start configuration
- **Installation**: Copy to `/etc/systemd/system/` and enable for boot startup
- **Monitoring**: Logs available via `journalctl -u aranea-server.service`
- **Remote Control**: Full web interface accessible from any device on network

---

*This guide represents the codebase state after comprehensive refactoring from manufacturer PyQt5 desktop application to modern web-based robot control system. Reference roadmap.md for development priorities and completed features.*

*Last updated: August 2025 with mobile hotspot configuration and service management*