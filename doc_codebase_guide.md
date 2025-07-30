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
- `server.py` - Hardware abstraction server (evolved from manufacturer code)
  - Command handlers for all hardware components
  - TCP socket management for legacy compatibility
  - Video streaming coordination
- `servo.py` - 18-servo hexapod control via PCA9685 I2C controllers
- `led.py` - RGB LED strip control with effects
- `buzzer.py` - Simple buzzer control
- `camera.py` - Pi camera streaming interface
- `ultrasonic.py` - Distance sensor interface
- `adc.py` - Battery voltage monitoring
- `imu.py` - Inertial measurement unit with Kalman filtering

#### **Robot Control & Movement**
- `control.py` - Main robot control system with condition monitoring thread
  - Servo angle calculations and safety checks
  - Command queue processing
  - Auto-relax functionality
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

#### **Configuration**
- `config/robot_config.py` - Centralized configuration
  - Voice settings, logging colors, debug flags
  - Hardware-specific settings
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
3. **Execution** → Hardware commands via server.py
4. **State Update** → RobotState flags updated
5. **Feedback** → LEDs, buzzer, or response data

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
- `CLEAR_MOVE_QUEUE_AFTER_EXEC = False` - Intentionally keeps legacy behavior
- `DEBUG_LEGS = True` - Enables detailed leg position logging
- `DRY_RUN = False` - Set to True for testing without hardware

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
- Start with: `robot_gait.py`, `control.py`, `robot_routines.py`
- Check: `config/robot_config.py` for timing flags
- Monitor: Servo communication in `servo.py`

### **For Voice Features**
- Core: `voice_control.py`, `voice_manager.py`
- Commands: `config/voice/eo.py` (template for other languages)
- Integration: `command_dispatcher_logic.py`

### **For Web Interface**
- Backend: `web_server.py`
- Frontend: `web_interface/templates/index.html`
- API: `/command` endpoint for all robot control

### **For Hardware Issues**
- Hardware layer: `server.py` (evolved manufacturer code)
- Individual components: `servo.py`, `led.py`, `camera.py`, etc.
- Calibration: `robot_calibration.py`

### **For State Management**
- Central state: `robot_state.py`
- State monitoring: `control.py` condition_monitor()
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
symbolic_commands["command_name"] = lambda: send_str("CMD_...", server.process_command)
routine_commands["routine_name"] = routine_function
```

### **State Checking**
```python
if robot_state.get_flag("motion_state"):
    # Safe to execute movement
```

### **Hardware Commands**
```python
# Via server instance
server.servo_controller.set_servo_angle(channel, angle)
server.led_controller.process_light_command(parts)
```

## 🐛 Known Issues & Workarounds

1. **Movement Slowdown**: Check `SendMove(0,0)` calls in web interface
2. **Voice Model Loading**: Ensure sufficient RAM for multiple language models  
3. **Servo Timing**: Consider batching servo updates for better performance
4. **Legacy Compatibility**: Some manufacturer patterns retained intentionally

---

*This guide represents the codebase state after comprehensive refactoring from manufacturer PyQt5 desktop application to modern web-based robot control system. Reference roadmap.md for development priorities and completed features.*