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
- `command_dispatcher_core.py` - Registry for symbolic and routine commands  
- `command_dispatcher_registry.py` - Command registration (imports all routines)
- `command_dispatcher_symbolic.py` - Simple symbolic command execution
- `command_dispatcher_utils.py` - Utility functions for command processing

#### **Hardware Interface Layer**
- `hardware_server.py` - Hardware abstraction server (evolved from manufacturer code)
  - Command handlers for all hardware components
  - TCP socket management for legacy compatibility
  - Video streaming coordination
- `hardware_pca9685.py` - PCA9685 I2C controller driver for servo management
- `hardware_spi_ledpixel.py` - SPI-based LED strip driver (Freenove SPI LED pixels)
- `hardware_rpi_ledpixel.py` - Raspberry Pi WS281X LED strip driver

#### **Sensors**
- `sensor_camera.py` - Pi camera streaming interface
- `sensor_ultrasonic.py` - Distance sensor interface
- `sensor_adc.py` - Battery voltage monitoring
- `sensor_imu.py` - Inertial measurement unit with Kalman filtering

#### **Actuators**
- `actuator_servo.py` - 18-servo hexapod control via PCA9685 I2C controllers
- `actuator_led.py` - RGB LED strip control with effects
- `actuator_buzzer.py` - Simple buzzer control

#### **Robot Control & Movement**
- `robot_control.py` - Main robot control system with condition monitoring thread
  - Servo angle calculations and safety checks
  - Command queue processing
  - Auto-relax functionality
- `robot_pid.py` - PID controller for robot balance and stability
- `robot_kinematics.py` - Forward/inverse kinematics calculations
- `robot_gait.py` - Gait pattern generation (walking algorithms)
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
- `web_interface/templates/` - Jinja2 HTML templates
- `web_interface/static/` - CSS, JS, Bootstrap assets
- Routes: `/` (main), `/command` (API), `/voice` (control), `/status`

#### **Voice Control System**
- `voice_manager.py` - Voice system lifecycle management
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

### **Performance Issues Identified**
- **Movement slowdown**: Related to command queue retention and SendMove(0,0) in move.js
- **Servo bottleneck**: 18 sequential I2C calls per movement frame
- **Thread contention**: Condition monitor loop overhead

### **Configuration Flags (Important)**
- `CLEAR_MOVE_QUEUE_AFTER_EXEC = False` - **CRITICAL**: Legacy compatibility with factory firmware
  - `False` → Commands loop indefinitely (requires explicit reset commands)
  - `True` → Commands execute once and auto-clear (future enhancement)
  - **Why False**: Maintains compatibility with original manufacturer client patterns
  - **Impact**: Single commands need reset pattern (`CMD_MOVE` + `CMD_MOVE#0#0#0`)
- `DEBUG_LEGS = True` - Enables detailed leg position logging
- `DRY_RUN = False` - Set to True for testing without hardware
- `VOICE_BLOCKSIZE = 8000` - Audio buffer size (increased from 4000 to reduce overflow)

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

---

*This guide represents the codebase state after comprehensive refactoring from manufacturer PyQt5 desktop application to modern web-based robot control system. Reference roadmap.md for development priorities and completed features.*