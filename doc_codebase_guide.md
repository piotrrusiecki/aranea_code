# Aranea Codebase Guide

## Overview
This document provides a comprehensive guide to the Aranea hexapod robot codebase, including architecture, file organization, and key functionality.

## Architecture

### File Organization
The codebase follows a systematic naming convention with functional prefixes:

- **hardware_***: Hardware drivers and abstraction layers
- **sensor_***: Input devices (camera, IMU, ultrasonic, ADC)
- **actuator_***: Output devices (servos, LEDs, buzzer)
- **robot_***: Robot logic and control systems
- **config/**: Configuration files and parameters
- **voice_***: Voice control system
- **web_***: Web interface and server
- **command_dispatcher_***: Command system architecture
- **doc_***: Documentation files

### Key Components

#### Camera System
- **sensor_camera.py**: Camera driver using Picamera2
- **Web Interface**: Camera feed accessible via `/video_feed` endpoint
- **Legacy Client**: TCP-based camera streaming on port 8002
- **Shared Access**: Both web and legacy clients can access camera simultaneously
- **MJPEG Streaming**: Web interface uses HTTP MJPEG for browser compatibility

#### Web Interface
- **web_server.py**: Flask-based web server on port 80
- **Camera Tab**: New camera control interface with start/stop functionality
- **Real-time Status**: Camera streaming status indicator
- **Responsive Design**: Works on mobile and desktop browsers

## Recent Updates

### Comprehensive Logging System (December 2024)
- ✅ Implemented proper logging throughout all modules
- ✅ Added lazy formatting for performance optimization
- ✅ Configured appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- ✅ Color-coded logging output by module type
- ✅ Preserved DEBUG_LEGS flag functionality for leg movement debugging
- ✅ Added error handling with proper logging
- ✅ Standardized logger naming convention

### Camera Web Interface (December 2024)
- ✅ Added camera feed to web interface
- ✅ MJPEG streaming via `/video_feed` endpoint
- ✅ Camera controls (start/stop) in dedicated tab
- ✅ Real-time status monitoring
- ✅ Shared camera access with legacy client
- ✅ Automatic resource management

### Code Quality Improvements (December 2024)
- ✅ Resolved PYL-W0201 warnings (attribute defined outside __init__)
- ✅ Resolved PY-W2000 warnings (unused imports)
- ✅ Improved error handling and logging
- ✅ Enhanced type hints and documentation

## Logging System

### Logger Naming Convention
The codebase uses a hierarchical logger naming system for clear identification:

- **main**: Main application logger
- **robot.***: Robot control modules (control, gait, kinematics, pose, calibration, state, pid, patrol)
- **sensor.***: Sensor modules (camera, adc, imu, ultrasonic)
- **actuator.***: Actuator modules (servo, led)
- **hardware.***: Hardware drivers (pca9685)
- **dispatcher.***: Command dispatcher modules (core, logic, registry, symbolic, utils)
- **voice**: Voice control system
- **web**: Web interface
- **led.***: LED subsystem (commands, hw.rpi, hw.spi)

### Log Levels
- **DEBUG**: Detailed diagnostic information (leg movements, sensor readings, calculations)
- **INFO**: General operational information (initialization, state changes, commands)
- **WARNING**: Atypical behavior that doesn't prevent operation (obstacles, invalid inputs)
- **ERROR**: Errors that affect functionality (hardware failures, exceptions)

### Color Coding
Log messages are color-coded by module type for easy identification:
- **Blue**: Main application
- **Green**: Robot control modules
- **Yellow**: Hardware and dispatcher modules
- **Red**: Actuator modules
- **Magenta**: Sensor modules
- **Cyan**: Web interface and camera

### Configuration
Logging is configured in `config/robot_config.py`:
- `LOGGING_LEVEL`: Global log level (DEBUG, INFO, WARNING, ERROR)
- `LOGGER_COLORS`: Color mapping for different logger names
- `DEBUG_LEGS`: Special flag for detailed leg movement logging

### Best Practices
- Use lazy formatting: `logger.debug("Value: %s", value)` instead of `logger.debug(f"Value: {value}")`
- Include context in log messages for debugging
- Use appropriate log levels for different types of information
- Add error handling with logging for all critical operations
- Preserve existing DEBUG_LEGS functionality for leg movement debugging

## File Responsibilities

### Core Hardware
- **hardware_server.py**: Main server managing TCP connections and camera streaming
- **hardware_pca9685.py**: PCA9685 servo controller driver
- **hardware_rpi_ledpixel.py**: WS281x LED strip driver

### Sensors
- **sensor_camera.py**: Camera driver with streaming capabilities
- **sensor_imu.py**: IMU sensor interface
- **sensor_ultrasonic.py**: Ultrasonic distance sensor
- **sensor_adc.py**: Analog-to-digital converter for battery monitoring

### Actuators
- **actuator_servo.py**: Servo motor control
- **actuator_led.py**: LED strip control
- **actuator_buzzer.py**: Buzzer control

### Robot Control
- **robot_control.py**: Main robot control system
- **robot_gait.py**: Walking gait algorithms
- **robot_kinematics.py**: Inverse kinematics calculations
- **robot_calibration.py**: Leg calibration system

### Web Interface
- **web_server.py**: Flask web server with camera streaming
- **web_interface/**: HTML templates and static assets
- **Camera Tab**: Real-time camera feed with controls

### Voice Control
- **voice_manager.py**: Voice control system manager
- **voice_control.py**: Voice recognition and processing
- **config/voice/**: Multi-language voice command files

### Command System
- **command_dispatcher_core.py**: Core command dispatch system
- **command_dispatcher_logic.py**: Command execution logic
- **command_dispatcher_registry.py**: Command registration system

## Configuration

### Robot Configuration
- **config/robot_config.py**: Main robot configuration
- **config/parameter.py**: Robot parameters and calibration data
- **params.json**: JSON configuration file

### Voice Configuration
- **config/voice/**: Multi-language voice command files
- **Supported Languages**: English, German, French, Spanish, Polish, Portuguese, Hindi, Esperanto

## Development Guidelines

### Code Quality
- Use type hints for all function parameters and return values
- Initialize all attributes in `__init__` methods
- Use proper error handling with try/except blocks
- Add comprehensive logging for debugging

### Logging Guidelines
- Use appropriate logger names following the hierarchical convention
- Implement lazy formatting for performance
- Use correct log levels for different types of information
- Include context and error details in log messages
- Preserve DEBUG_LEGS functionality for leg movement debugging

### Camera Integration
- Camera can only be accessed by one process at a time
- Web interface shares camera instance with legacy client
- Use proper resource management to prevent conflicts
- Implement timeout handling for frame capture

### Web Interface
- Use Bootstrap for responsive design
- Implement proper error handling for HTTP endpoints
- Use MJPEG streaming for real-time video
- Provide status indicators for all operations

## Troubleshooting

### Logging Issues
- **No colored output**: Check `LOGGER_COLORS` configuration in robot_config.py
- **Too much debug output**: Set `LOGGING_LEVEL` to INFO or WARNING
- **Missing leg movement logs**: Enable `DEBUG_LEGS` flag in robot_config.py
- **Performance issues**: Ensure lazy formatting is used for all log messages

### Camera Issues
- **"Device or resource busy"**: Camera is already in use by another process
- **No frames received**: Camera not properly streaming, check `start_stream()` call
- **Web interface not showing video**: Check browser console for errors

### Web Interface Issues
- **Camera tab not loading**: Check JavaScript console for errors
- **Status not updating**: Verify `/camera_status` endpoint is working
- **Stream not starting**: Check server logs for camera initialization errors

## Future Improvements

### Planned Features
- [ ] Camera quality/format controls in web interface
- [ ] Camera recording functionality
- [ ] Multiple camera support
- [ ] Advanced camera settings
- [ ] Logging storage and web interface display

### Technical Debt
- [ ] Improve camera resource management
- [ ] Add camera health monitoring
- [ ] Implement camera error recovery
- [ ] Optimize frame rate and quality settings
- [ ] Add log rotation and archival
- [ ] Implement structured logging for better analysis