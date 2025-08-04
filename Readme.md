# Aranea - Advanced Hexapod Robot Control System

<img src='Picture/icon.png' width='50%'/>

## 🤖 What is Aranea?

**Aranea** is a sophisticated hexapod robot control system built on the Freenove Raspberry Pi kit. It has evolved from a basic desktop application into a modern, multi-interface robot control platform with advanced features like voice control, web interface, and LED feedback systems.

## ✨ Key Features

### 🌐 **Multi-Interface Control**
- **Web Interface**: Responsive web-based control accessible from any device
- **Voice Control**: 8-language voice recognition system (EN, EO, DE, FR, ES, HI, PL, PT)
- **TCP Interface**: Legacy protocol support for compatibility
- **Mobile-Ready**: Touch-friendly interface optimized for field operation

### 🎯 **Advanced Robot Capabilities**
- **18-Servo Hexapod**: Precise 6-legged movement with inverse kinematics
- **Multiple Gaits**: Tripod and wave gait patterns for different terrains
- **Real-Time Control**: Sub-millisecond servo response times
- **Sensor Integration**: IMU, ultrasonic, camera, and battery monitoring
- **LED Feedback**: Visual status indicators and user feedback

### 🏗️ **Modern Architecture**
- **Command Dispatcher**: Unified routing system for all interfaces
- **Hardware Abstraction**: Clean separation between logic and hardware
- **Thread-Safe Design**: Robust multi-threaded architecture
- **Modular Codebase**: Well-organized, maintainable code structure

## 🚀 Quick Start

### Prerequisites
- Raspberry Pi (3B+ or 4 recommended)
- Freenove Hexapod Robot Kit
- Python 3.7+
- Network connection for web interface

### Installation
```bash
# Clone the repository
git clone https://github.com/piotrrusiecki/aranea_code.git
cd aranea_code

# Install dependencies
pip install -r requirements.txt

# Run the robot
python main.py
```

### Access the Web Interface
1. Connect to the robot's WiFi network
2. Open your browser to `http://[robot-ip]:5000`
3. Use the web interface to control the robot

## 🎮 Control Methods

### Web Interface
- **Movement**: Drag controls for walking, turning, and positioning
- **Routines**: Pre-programmed movements like marching and patrolling
- **Calibration**: Visual servo calibration interface
- **Sensors**: Real-time sensor data display
- **Voice**: Language switching and voice command interface

### Voice Commands
- **Movement**: "Forward", "Backward", "Turn left", "Turn right"
- **Routines**: "March", "Run", "Patrol"
- **Language Switching**: "Spider german", "Araignée français"
- **Status**: "Stop", "Relax", "Calibrate"

### Supported Languages
- 🇺🇸 English
- 🌍 Esperanto  
- 🇩🇪 German
- 🇫🇷 French
- 🇪🇸 Spanish
- 🇮🇳 Hindi
- 🇵🇱 Polish
- 🇵🇹 Portuguese

## 🔧 Technical Architecture

### System Flow
```
[Web Interface] ──┐
[Voice Control] ──┼─→ [Command Dispatcher] ──→ [Hardware Layer] ──→ [Physical Robot]
[TCP Interface] ──┘                            ↕
                                        [Robot State Manager]
```

### Key Components
- **Command Dispatcher**: Routes commands from multiple interfaces
- **Hardware Abstraction**: PCA9685 servo controllers, LED strips, sensors
- **Robot Control**: Kinematics, gait patterns, movement routines
- **Voice System**: Vosk speech recognition with multi-language support
- **Web Server**: Flask-based responsive interface

## 📁 Project Structure

```
aranea_code/
├── main.py                 # Application entry point
├── hardware_*.py          # Hardware interface layer
├── sensor_*.py            # Sensor modules (camera, IMU, ultrasonic)
├── actuator_*.py          # Actuator control (servos, LEDs, buzzer)
├── robot_*.py             # Robot logic (control, gait, routines)
├── voice_*.py             # Voice recognition system
├── command_dispatcher_*.py # Command routing system
├── web_interface/         # Web UI templates and static files
├── config/               # Configuration and voice language files
└── tests/                # Test modules
```

## 🎯 Enhancements Over Original

### **Architecture Evolution**
- **Original**: PyQt5 desktop GUI → **Enhanced**: Web interface
- **Original**: No voice control → **Enhanced**: 8-language voice recognition
- **Original**: Direct command parsing → **Enhanced**: Command dispatcher pattern
- **Original**: Print statements → **Enhanced**: Comprehensive logging
- **Original**: Scattered state → **Enhanced**: Centralized RobotState
- **Original**: Monolithic server.py → **Enhanced**: Modular architecture

### **Enhanced Features**
- **Multi-Language Voice**: Runtime language switching with native translations
- **LED Feedback System**: Visual status indicators and user feedback
- **Mobile Interface**: Touch-friendly web interface for field operation
- **Real-Time Control**: Sub-millisecond servo response times
- **Sensor Integration**: Comprehensive sensor fusion and monitoring

## 🔍 Documentation

- **[Codebase Guide](doc_codebase_guide.md)**: Comprehensive technical documentation
- **[Development Roadmap](doc_roadmap.md)**: Project progress and future plans
- **[Installation Guide](doc_install.md)**: Detailed setup instructions
- **[WiFi Configuration](doc_wifi.md)**: Network setup for remote access

## 🤝 Acknowledgments

This project builds upon the excellent **Freenove Hexapod Robot Kit**. We're grateful to Freenove for:

- **Open Source Code**: Providing their complete robot control system as open source
- **Fantastic Support**: Sending replacement STL files and parts when needed
- **Quality Hardware**: Well-designed hexapod platform with reliable components
- **Educational Focus**: Making robotics accessible to enthusiasts and learners

### Key Enhancements Made
While maintaining compatibility with the original Freenove system, we've added:

- **Better Threading**: Improved thread safety and resource management
- **Simplified Structure**: Streamlined codebase while preserving core functionality
- **Modern Architecture**: Command dispatcher pattern and hardware abstraction
- **Enhanced Features**: Voice control, web interface, LED feedback

## 📊 Project Status

- ✅ **Core System**: Fully functional robot control
- ✅ **Web Interface**: Responsive multi-tab interface
- ✅ **Voice Control**: 8-language support with runtime switching
- ✅ **LED Feedback**: Visual status and user feedback system
- ✅ **Hardware Integration**: Complete sensor and actuator support
- 🔄 **Performance Optimization**: Ongoing movement and response improvements
- 🔄 **Field Autonomy**: AP fallback and standalone operation

## 📞 Support

For issues, questions, or contributions:
- Check the [documentation](doc_codebase_guide.md) first
- Review the [roadmap](doc_roadmap.md) for current priorities
- Open an issue for bugs or feature requests

---

**Built with ❤️ on Raspberry Pi** | **Based on the excellent Freenove Hexapod Kit** | **Enhanced with modern web and voice technologies**