# Aranea Robot Development Roadmap

*Last updated: December 2024 - Global variable refactoring completed*

## Phase 1: Field Autonomy & Performance (Priority: HIGH)
### Network & Connectivity
- [ ] Standalone AP fallback mode (AraneaRobot hotspot)
- [ ] WiFi network manager with auto-failover
- [ ] Connection status indicators in web UI

### Performance Optimization
- [ ] Investigate movement slowdown (check SendMove(0,0) in move.js) 
- [ ] Servo communication optimization (batch operations)
- [ ] Memory pool for gait calculations
- [ ] Performance monitoring dashboard

## Phase 2: Multi-Language Voice System (Priority: HIGH)
### Language Support
- [ ] German voice model and commands ("spinne deutsch")
- [ ] Spanish voice model and commands ("araneo español") 
- [ ] French voice model and commands ("araignée français")
- [ ] Polish voice model and commands ("pająk polski")
- [ ] English voice model and commands ("araneo english")

### Voice Architecture
- [ ] Runtime language switching with source language commands
- [ ] Dynamic model loading and unloading
- [ ] Voice command fuzzy matching per language
- [ ] All voice commands integrated to dispatcher

## Phase 3: Core System Refinement (Priority: MEDIUM)
### Architecture Improvements
- [ ] Centralize status_flag management in robot_state.py
- [ ] Centralize all configuration in config/ (parameter.py moved, robot_config.py exists, but config still scattered throughout codebase)
- [ ] Enhanced error handling and recovery strategies
- [ ] Thread safety audit and optimization

### Web Interface Enhancement
- [ ] Mobile-responsive UI improvements
- [ ] Complete diagnostics tab (IMU, servo state, ultrasonic, battery)
- [ ] Real-time performance metrics display
- [ ] Configuration management via web UI
- [ ] Real-time video streaming integration - Embedded camera feed in web interface

## Phase 4: Advanced Robot Behaviors (Priority: MEDIUM)
### Movement & Navigation
- [ ] Enhanced patrol mode with obstacle avoidance
- [ ] Posture recovery using IMU feedback
- [ ] Dancing composite moves and sequences
- [ ] Beat detection and rhythm-based movement

### Feedback Systems
- [ ] LED status indicators and feedback patterns
- [ ] Local speech feedback (espeak integration)
- [ ] Buzzer alert patterns for different states

## Phase 5: External Integration (Priority: LOW)
### APIs & Control
- [ ] REST API for external control
- [ ] WebSocket interface for real-time communication
- [ ] Git auto-updater in web interface
- [ ] Remote debugging capabilities

### Data & Logging
- [ ] Persistent logging (SQLite/file-based)
- [ ] Battery usage graphs and trend analysis
- [ ] Movement pattern recording and playback
- [ ] Routine recorder and editor via web UI

## Phase 6: Advanced Features (Priority: FUTURE)
### Sensors & Hardware
- [ ] LiDAR integration for advanced navigation
- [ ] Camera-based object recognition
- [ ] Additional sensor integration framework

### AI & Learning
- [ ] Voice command learning and adaptation
- [ ] Movement optimization based on terrain
- [ ] Behavioral pattern recognition

## Maintenance & Quality Assurance (Ongoing)
### Testing & Deployment
- [ ] Comprehensive test suite development
- [ ] Regression testing framework
- [ ] Fresh install deployment scripts
- [ ] Documentation and user guides

### Code Quality
- [x] **Global variable elimination** - Removed all problematic global statements (PYL-W0603 warnings)
- [x] **Logging format optimization** - Converted eager string formatting to lazy % formatting in sensor modules
- [x] **Type annotation improvements** - Added Optional types and fixed method signature compatibility issues
- [ ] DeepSource issue resolution (ongoing)
- [ ] Type hints addition to critical modules (in progress - sensor_camera.py completed)
- [ ] Performance profiling and optimization
- [ ] Security audit and hardening

## Completed ✅

### **Architecture Transformation**
- [x] **Eliminated PyQt5 desktop dependency** - Replaced PyQt5 GUI with web-based interface
- [x] **Command dispatcher architecture** - Built unified command routing system vs original direct command handling
- [x] **Multi-interface command routing** - Unified web, voice, and TCP interfaces through single dispatcher
- [x] **Thread-safe robot state management** - Added centralized RobotState class vs scattered state variables
- [x] **Modular hardware abstraction** - Separated hardware interfaces from business logic

### **Interface & Control Improvements**
- [x] **Web interface development** - Complete Flask-based control interface (original had none)
- [x] **Voice control foundation** - Added Vosk-based voice recognition with Esperanto support (original had none)
- [x] **Mobile-responsive web UI** - Touch-friendly interface for field operation
- [x] **Calibration web interface** - Visual servo calibration vs command-line only

### **System Architecture Enhancements**
- [x] **Comprehensive logging system** - Color-coded, multi-level logging vs print statements only
- [x] **Configuration management** - Centralized config system vs hardcoded values
- [x] **Error handling framework** - Structured exception handling vs basic try-catch
- [x] **Service architecture** - Separated concerns vs monolithic server class
- [x] **Command registry pattern** - Extensible command system vs hardcoded command parsing
- [x] **File naming convention standardization** - Systematic renaming of 15 legacy files with functional prefixes (hardware_*, sensor_*, actuator_*, robot_*, config/) for clear architectural separation

### **Operational Improvements**
- [x] **Headless operation capability** - No GUI dependency for server operation
- [x] **Graceful shutdown handling** - Proper resource cleanup vs abrupt termination
- [x] **Auto servo relax logic removal** - Simplified servo management
- [x] **Turning functionality enhancement** - Improved movement control
- [x] **Cross-platform compatibility** - Removed Windows/PyQt dependencies

### **Developer Experience**
- [x] **Code modularity** - Separated 8.8KB monolithic server.py into focused modules
- [x] **Import organization** - Clean dependency management vs mixed imports
- [x] **Documentation structure** - Added docstrings and code comments
- [x] **Version control integration** - Git-ready structure vs standalone files
- [x] **Codebase organization** - Implemented consistent naming convention with git history preservation: legacy files renamed to reflect function (server.py→hardware_server.py, control.py→robot_control.py, etc.)
- [x] **Documentation maintenance** - Updated codebase guide and roadmap to reflect architectural changes and naming conventions
- [x] **Critical performance bug fix** - Resolved infinite recursion in robot_control.py run_gait method that was causing robot slowdown

### **Code Quality & Architecture Refinements (Dec 2024)**
- [x] **Global variable elimination** - Refactored voice_manager.py and command_dispatcher_logic.py to eliminate all global statements
  - Converted voice_manager.py to class-based VoiceManager with instance state management
  - Added safe server instance access in command_dispatcher_logic.py with _get_server() helper
  - Enhanced type safety with proper None checking and runtime validation
  - Maintained backward compatibility while improving thread safety and testability
  - Result: Zero PYL-W0603 linting errors, enhanced IDE support, cleaner architecture
- [x] **Sensor module code quality improvements** - Enhanced sensor_camera.py logging and type safety
  - Converted f-string logging to lazy % formatting for performance optimization
  - Added proper Optional type annotations for nullable return values and parameters
  - Fixed method signature compatibility with parent classes
  - Improved type checker compliance and IDE support