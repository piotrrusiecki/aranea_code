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

### Technical Debt
- [ ] Improve camera resource management
- [ ] Add camera health monitoring
- [ ] Implement camera error recovery
- [ ] Optimize frame rate and quality settings