# Aranea Robot Codebase Guide

*Your comprehensive guide to understanding and navigating the Aranea hexapod robot codebase*

## 🎯 Quick Start

**What is this?** A hexapod robot control system that evolved from a PyQt5 desktop app into a modern web-based multi-interface system.

**Key Innovation:** Command dispatcher pattern that unifies web, voice, and TCP interfaces through a centralized routing system.

**Current State:** Fully functional robot with 8-language voice control, LED feedback system, and web interface. **Code quality improvements**: Resolved all unused variable warnings (PYL-W0612) across codebase.

---

## 🏗️ Architecture Overview

### System Flow
```
[Web Interface] ──┐
[Voice Control] ──┼─→ [Command Dispatcher] ──→ [Hardware Layer] ──→ [Physical Robot]
[TCP Interface] ──┘                            ↕
                                        [Robot State Manager]
```

### Key Design Patterns
- **Command Dispatcher**: Routes commands from multiple interfaces to hardware
- **Hardware Abstraction**: Clean separation between business logic and hardware
- **State Management**: Centralized, thread-safe robot state
- **Multi-Interface**: Web, voice, and TCP all use the same command system

---

## 📁 File Structure & Purpose

### **Entry Point**
- `main.py` - Application startup, threading setup, Flask integration
  - Initializes all subsystems (server, voice, web, LED feedback)
  - Handles graceful shutdown and resource cleanup
  - Uses colored logging system

### **Core Systems**

#### **Command Dispatching** (The Heart of the System)
- `command_dispatcher_logic.py` - Main dispatcher and command routing
  - Routes commands to symbolic or routine handlers
  - Safe server instance access with `_get_server()` helper
  - Type-safe with proper None checking
  - **FIXED**: Resolved cyclic import by moving `_handle_diag_set_servo` function
- `command_dispatcher_core.py` - Registry for symbolic commands
- `command_dispatcher_registry.py` - Command registration and routine imports
- `command_dispatcher_symbolic.py` - Simple command execution (no longer imports from logic)
- `command_dispatcher_utils.py` - Utility functions

#### **Hardware Interface Layer**
- `hardware_server.py` - Hardware abstraction server
  - Command handlers for all hardware components
  - TCP socket management for legacy compatibility
  - Video streaming coordination
- `hardware_pca9685.py` - **PCA9685 I2C controller for servo management** ⚠️
  - Controls 18 servos across two PCA9685 boards (0x40, 0x41)
  - **CRITICAL**: Must maintain complete register map and PWM write sequences
  - Any modifications require comparison with original working code
- `hardware_spi_ledpixel.py` - SPI-based LED strip driver
- `hardware_rpi_ledpixel.py` - Raspberry Pi WS281X LED strip driver

#### **Sensors** (Input Devices)
- `sensor_camera.py` - Pi camera streaming with video recording
  - Optimized logging with lazy % formatting
  - Proper Optional type annotations
- `sensor_ultrasonic.py` - Distance sensor interface
- `sensor_adc.py` - Battery voltage monitoring
- `sensor_imu.py` - Inertial measurement unit with Kalman filtering

#### **Actuators** (Output Devices)
- `actuator_servo.py` - 18-servo hexapod control via PCA9685
- `actuator_led.py` - RGB LED strip control with effects
- `actuator_buzzer.py` - Simple buzzer control
- `actuator_led_commands.py` - **Centralized LED feedback system**
  - Thread-safe LED patterns with proper cleanup
  - Server ready flash (green), language switching glow (red), language ready flash (blue)
  - Performance optimized with lazy logging

#### **Robot Control & Movement**
- `robot_control.py` - Main robot control with condition monitoring
  - Modular command handlers (`_handle_position_command`, `_handle_move_command`)
  - Servo angle calculations and safety checks
  - Command queue processing
  - **NEW**: `set_body_height_z()` method for web interface Z position control
  - **BACKWARDS COMPATIBLE**: Legacy CMD_POSITION commands still work unchanged
- `robot_pid.py` - PID controller for balance and stability
- `robot_kinematics.py` - Forward/inverse kinematics calculations
- `robot_gait.py` - Gait pattern generation (walking algorithms)
  - Tripod/wave gait implementations with phase-specific functions
  - Modular gait execution with `_execute_tripod_gait()` and `_execute_wave_gait()`
- `robot_pose.py` - Body posture and balance calculations
- `robot_routines.py` - High-level movement routines (march, run, patrol)
- `robot_calibration.py` - Servo calibration utilities
  - Security: Added filename validation to prevent path traversal attacks

#### **State Management**
- `robot_state.py` - Thread-safe centralized state management
  - Flags: motion_state, sonic_state, calibration_mode, servo_off, move_speed, body_height_z
  - **NEW**: body_height_z (-20 to 20) for web interface Z position control
  - Thread-safe with proper locking for all operations

#### **Web Interface**
- `web_server.py` - Flask application factory and routes
  - Modular route handlers with dependency injection
  - `/language` POST endpoint for web-based language switching
- `web_interface/templates/` - Jinja2 HTML templates
- `web_interface/static/` - CSS, JS, Bootstrap assets
- Routes: `/` (main), `/command` (API), `/voice` (control), `/status`, `/language`

#### **Multi-Language Voice Control System** 🌍
- `voice_manager.py` - Voice system lifecycle management
  - Class-based `VoiceManager` with instance state management
  - Language switching capability with `switch_language()` method
  - LED feedback integration for language switching
- `voice_control.py` - Core voice recognition and command processing
  - Multi-language support with runtime language switching
  - Uses Vosk speech recognition with language-specific models
  - Language-specific command maps loaded dynamically
  - Fuzzy matching for voice command recognition
- `voice_command_handler.py` - Command routing and language switching logic
  - Handles `language_XX` commands for runtime language switching
  - Routes commands to appropriate dispatcher or language manager
- `voice_language_commands.py` - Multi-language command map registry
  - Dynamic loading of language-specific command maps
  - Supports 8 languages: EN, EO, DE, FR, ES, HI, PL, PT
- `config/voice/` - Language-specific command definitions
  - Individual language files (en.py, de.py, fr.py, etc.)
  - Each language has complete command set with native translations
  - Language switching commands use "spider" + language name pattern

**Voice Language Switching Pattern:**
- Use the word for "spider" in the current language + target language name
- Examples: "spider german", "araignée français", "pająk po angielsku"
- All languages support switching to all other languages
- Web interface buttons for one-click language switching

#### **Configuration & Constants**
- `config/robot_config.py` - Centralized configuration
  - Voice settings, logging colors, debug flags
  - Hardware-specific settings
- `config/parameter.py` - Parameter management utility
  - Hardware detection and validation
  - Configuration file management
  - Security: Added file path validation
- `constants_commands.py` - Command constants and definitions
- `params.json` - Runtime parameters (PCB version, Pi version)

---

## 🔧 Technical Details

### **Threading Model**
- **Main Thread**: Flask web server
- **Video Thread**: Camera streaming (daemon)
- **Command Thread**: TCP command processing (daemon)  
- **Voice Thread**: Speech recognition (daemon)
- **Control Thread**: Robot condition monitoring
- **Routine Threads**: Movement execution (created on-demand)
- **LED Pattern Threads**: LED feedback patterns (daemon, created on-demand)

### **Command Flow**
1. **Input** → Web UI, Voice, or TCP
2. **Dispatcher** → Routes to symbolic or routine commands
3. **Execution** → Hardware commands via hardware_server.py
4. **State Update** → RobotState flags updated
5. **Feedback** → LEDs, buzzer, or response data

### **LED Feedback System**
- **Server Ready**: Green flash (2x 0.3s) when server starts
- **Language Switching**: Red glow (pulsing fade) during language switching
- **Language Ready**: Blue flash (0.4s) when switching completes
- **Thread-safe**: All patterns run in separate daemon threads
- **Error Handling**: Patterns stop automatically on errors

### **Z Position Control System**
- **Range**: -20 to 20 (matching legacy CMD_POSITION)
- **Default**: 0 (neutral body height)
- **Storage**: Thread-safe in `robot_state.body_height_z`
- **Persistence**: Z position retained across movement commands
- **Backwards Compatible**: Legacy `CMD_POSITION#0#0#10` still works
- **Web Interface**: Slider control under Speed in move tab
- **Implementation**: `set_body_height_z()` method in `robot_control.py`

### **Command Execution Patterns**

#### **Single Action Commands** (`task_*` symbols)
- **Purpose**: Execute once and stop (step forward, turn, look, lights)
- **Pattern**: Movement command + Reset command (matches web interface)
- **Example**: `task_step_forward` → `CMD_MOVE#1#0#35#8#0` + `CMD_MOVE#1#0#0#8#0`
- **Web Interface**: Uses `onmousedown`/`onmouseup` with `sendMove(x,y)` + `sendMove(0,0)`
- **Voice Commands**: Implemented with `_send_move_with_reset()` helper function

#### **Continuous Routines** (`routine_*` commands) 
- **Purpose**: Run until stopped (march, run, patrol)
- **Pattern**: Background threading with `motion_loop()` + `motion_state` flag
- **Example**: `routine_march_forward` → Thread continuously sends individual `CMD_MOVE` commands
- **State Management**: `motion_state = True` during execution, `False` to stop

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

---

## 🎯 Current State vs Original

### **Major Transformations Completed**
- ❌ PyQt5 desktop GUI → ✅ Web interface
- ❌ No voice control → ✅ Vosk-based voice recognition (8 languages)
- ❌ Direct command parsing → ✅ Command dispatcher pattern
- ❌ Print statements → ✅ Comprehensive logging
- ❌ Scattered state → ✅ Centralized RobotState
- ❌ Monolithic server.py → ✅ Modular architecture
- ❌ Global variables & state → ✅ Class-based architecture
- ❌ No LED feedback → ✅ Centralized LED feedback system
- ❌ Single language → ✅ Multi-language voice system
- ❌ Cyclic imports → ✅ Clean dependency management

### **Configuration Flags (Important)**
- `CLEAR_MOVE_QUEUE_AFTER_EXEC = False` - **CRITICAL**: Legacy compatibility
  - `False` → Commands loop indefinitely (requires explicit reset commands)
  - `True` → Commands execute once and auto-clear (future enhancement)
- `DEBUG_LEGS = True` - Enables detailed leg position logging
- `DRY_RUN = False` - Set to True for testing without hardware
- `VOICE_BLOCKSIZE = 8000` - Audio buffer size (increased from 4000)

---

## 🔍 Quick Navigation

### **For Movement Issues**
- Start with: `robot_gait.py`, `robot_control.py`, `robot_routines.py`
- Check: `config/robot_config.py` for timing flags
- Monitor: Servo communication in `actuator_servo.py`

### **For Voice Features**
- Core: `voice_control.py`, `voice_manager.py`
- Commands: `config/voice/eo.py` (template for other languages)  
- Integration: `command_dispatcher_logic.py`
- Registration: `command_dispatcher_registry.py`

### **For Web Interface**
- Backend: `web_server.py`
- Frontend: `web_interface/templates/index.html`
- API: `/command` endpoint for all robot control

### **For Hardware Issues**
- Hardware layer: `hardware_server.py`
- Individual components: `actuator_servo.py`, `actuator_led.py`, `sensor_camera.py`
- Calibration: `robot_calibration.py`

### **For State Management**
- Central state: `robot_state.py`
- State monitoring: `robot_control.py` condition_monitor()
- Flag interactions: Check exclusivity logic

---

## 📝 Code Patterns & Conventions

### **Logging**
```python
logger = logging.getLogger("module.submodule")
logger.info("Action completed: %s", result)  # Lazy formatting
```

### **Command Registration**
```python
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

---

## 🐛 Known Issues & Workarounds

### **1. Command Looping**
- **Issue**: Single movement commands loop infinitely without reset commands
- **Root Cause**: `CLEAR_MOVE_QUEUE_AFTER_EXEC = False` (legacy compatibility)
- **Solution**: Always send reset command (`CMD_MOVE#1#0#0#8#0`) after movement commands
- **Implementation**: Voice uses `_send_move_with_reset()`, Web uses `onmouseup="sendMove(0,0)"`

### **2. Voice Command Attribution Error**
- **Issue**: `'NoneType' object has no attribute 'process_command'`
- **Root Cause**: Symbolic commands trying to access `server_instance` directly
- **Solution**: Use `lambda send: send([...])` pattern in command registration
- **Status**: ✅ **FIXED** - Replaced global `server_instance` with `CommandDispatcher` singleton pattern

### **3. Audio Input Overflow**
- **Issue**: Voice control logs frequent "input overflow" messages
- **Mitigation**: Increased `VOICE_BLOCKSIZE` from 4000 to 8000, added log throttling

### **4. Hardware Driver Best Practices** ⚠️
- **NEVER remove hardware register constants** based on automated tools
- **Complete register maps required**: Even "unused" constants are needed for hardware compatibility
- **When modifying hardware files**: Always compare with original working code before deployment
- **PWM register writes must be complete**: All 4 registers (ON_L, ON_H, OFF_L, OFF_H) required per channel

### **5. Code Quality Improvements** ✅
- **Unused Variable Warnings (PYL-W0612)**: Resolved all instances across codebase
- **Pattern**: Use `_` prefix for intentionally unused variables or remove if truly unnecessary
- **Fixed Files**: `hardware_server.py`, `robot_routines.py`, `robot_pose.py`, `robot_control.py`, `hardware_spi_ledpixel.py`, `actuator_led.py`
- **Bug Fix**: Corrected undefined variable `i` in `hardware_spi_ledpixel.py` set_led_brightness method

---

## 💻 Development Environment

### **Windows Development Configuration**
For developing on Windows while deploying to Raspberry Pi:

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

### **Attribute Initialization Patterns**
After comprehensive attribute initialization fixes, established patterns for socket-related attributes:

```python
class NetworkServer:
    def __init__(self):
        # Initialize all socket attributes as None with type hints
        self.video_socket: Optional[socket.socket] = None
        self.command_socket: Optional[socket.socket] = None
        
    def start_server(self):
        # Set actual socket instances during runtime
        self.video_socket = socket.socket()
        
    def stop_server(self):
        # Defensive cleanup with None checks
        if hasattr(self, 'video_connection') and self.video_connection is not None:
            self.video_connection.close()
```

---

## 🌐 Network & Remote Access

### **WiFi Configuration**  
- **Priority System**: NetworkManager-based with phone hotspot (100) > home network (50) > wired (-999)
- **Remote Access**: Mobile hotspot enables field operations via web interface
- **Documentation**: Complete setup guide in `doc_wifi.md`
- **Auto-Failover**: Seamless switching between networks based on availability

### **Service Management**
- **Systemd Service**: `.services/aranea-server.service` for auto-start configuration
- **Installation**: Copy to `/etc/systemd/system/` and enable for boot startup
- **Monitoring**: Logs available via `journalctl -u aranea-server.service`
- **Remote Control**: Full web interface accessible from any device on network

---

## 🚀 Development Priorities

### **Phase 1: Field Autonomy** (HIGH)
- AP fallback mode for standalone operation
- Performance optimization (movement slowdown fix)

### **Phase 2: Multi-Language Voice** (HIGH) ✅ COMPLETED
- German, Spanish, French, Polish voice models
- Runtime language switching with source language commands
- Pattern: "[spider in source] [target language in source]"

### **Phase 3: System Refinement** (MEDIUM)
- Enhanced error handling
- Mobile UI improvements  
- Performance monitoring dashboard

---

*This guide represents the codebase state after comprehensive refactoring from manufacturer PyQt5 desktop application to modern web-based robot control system. Reference roadmap.md for development priorities and completed features.*

*Last updated: December 2024 with multi-language voice system, LED feedback system, and code quality improvements*