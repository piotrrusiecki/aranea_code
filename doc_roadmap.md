# Aranea Robot Development Roadmap

*Last updated: December 2024 - LED feedback system and web interface language switching completed*

## Phase 1: Field Autonomy & Performance (Priority: HIGH)
### Network & Connectivity
- [x] Mobile hotspot remote access (NetworkManager priority configuration)
- [ ] Connection status indicators in web UI
- [x] LED functionality 
- [x] Indicate WiFi connection with LED / startup sequence / readiness
- [ ] Camera feed
- [ ] Optimise web-UI (toggles for gait and action mode instead of buttons, improve responsiveness, speed slider size swapped)
- [ ] Add position height in move, likely slider

### Performance Optimization
- [ ] Investigate movement slowdown (check SendMove(0,0) in move.js) 
- [ ] Servo communication optimization (batch operations)
- [ ] Memory pool for gait calculations
- [ ] Performance monitoring dashboard

## Phase 2: Multi-Language Voice System (Priority: HIGH) ✅ COMPLETED
### Language Support
- [x] German voice model and commands ("spinne polnisch")
- [x] Spanish voice model and commands ("araneo alleman") 
- [x] French voice model and commands ("araignée anglais")
- [x] Polish voice model and commands ("pająk esperanto, etc")
- [x] English voice model and commands ("araneo german")
- [x] Portuguese voice model and commands ("aranha alemão")
- [x] Hindi voice model and commands ("makhi hindi")
- [x] Esperanto voice model and commands ("araneo germane")

### Voice Architecture
- [x] Runtime language switching with source language commands
- [x] Dynamic model loading and unloading
- [x] Voice command fuzzy matching per language
- [x] All voice commands integrated to dispatcher
- [x] Language-specific command maps with native translations
- [x] "Spider" + language name pattern for language switching
- [x] Support for 8 languages: EN, EO, DE, FR, ES, HI, PL, PT
- [x] Web interface language switching buttons
- [x] Cyclic import resolution with callback pattern

**Multi-Language Voice System Features**:
- Runtime language switching via voice commands
- Language-specific Vosk models for accurate recognition
- Native command translations for all supported languages
- Fuzzy matching for voice command recognition
- Thread-safe language switching with proper model reloading
- Complete command coverage across all languages
- Language switching pattern: "spider" + target language name in source language
- Web interface buttons for one-click language switching
- LED feedback during language switching (red glow → blue flash)

## Phase 3: Core System Refinement (Priority: MEDIUM)
### Architecture Improvements
- [x] Centralize LED handling in actuator_led_commands.py
- [ ] Centralize status_flag management in robot_state.py
- [ ] Centralize all configuration in config/ (parameter.py moved, robot_config.py exists, but config still scattered throughout codebase)
- [ ] Enhanced error handling and recovery strategies
- [ ] Thread safety audit and optimization

### Web Interface Enhancement
- [x] Language switching interface with flag icons
- [x] LED feedback system integration
- [ ] Mobile-responsive UI improvements
- [ ] Complete diagnostics tab (IMU, servo state, ultrasonic, battery)
- [ ] Real-time performance metrics display
- [ ] Configuration management via web UI
- [ ] WiFi network configuration and management via web UI
- [ ] Real-time video streaming integration - Embedded camera feed in web interface

## Phase 4: Advanced Robot Behaviors (Priority: MEDIUM)
### Movement & Navigation
- [ ] Enhanced patrol mode with obstacle avoidance
- [ ] Posture recovery using IMU feedback
- [ ] Dancing composite moves and sequences
- [ ] Beat detection and rhythm-based movement

### Feedback Systems
- [x] LED status indicators and feedback patterns
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
- [x] DeepSource issue resolution (ongoing)
- [x] Type hints addition to critical modules (in progress - sensor_camera.py completed)
- [x] Performance profiling and optimization
- [x] Security audit and hardening - Fixed path traversal vulnerabilities in robot_calibration.py and config/parameter.py
- [x] Cyclic import resolution - Fixed voice system circular dependencies

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
- [x] **Static method optimization** - Converted utility methods to @staticmethod in hardware_server.py
  - Added @staticmethod decorators to get_interface_ip() and send_data() methods
  - Eliminated unnecessary self parameter where not used, improving code clarity
  - Resolved PYL-R0201 pylint warnings for better code structure
  - Maintained backward compatibility while optimizing memory usage
- [x] **Attribute initialization compliance** - Fixed PYL-W0201 warnings across codebase
  - Resolved all "attribute defined outside __init__" warnings in hardware_server.py and voice_control.py
  - Added proper type hints with Optional[Type] for socket-related attributes  
  - Enhanced type safety with defensive None checks in socket operations
  - Fixed return type annotations (StreamingOutput.write, ADC.read_battery_voltage)
- [x] **Static method optimization** - Fixed PYL-R0201 warning in config/parameter.py
  - Added @staticmethod decorator to _validate_file_path method for performance optimization
  - Eliminated unnecessary self parameter where not used, improving code clarity
  - Resolved linter warning while maintaining all existing functionality
- [x] **Anti-pattern resolution** - Fixed PTC-W0052 naming conflict in sensor_camera.py
  - Renamed `self.camera` attribute to `self._picamera` to avoid class name duplication
  - Improved code readability by making the underlying Picamera2 device relationship explicit
  - Zero risk change - attribute only used internally within Camera class
  - Enhanced code clarity and eliminated DeepSource anti-pattern warning
  - Maintained existing hasattr() defensive patterns while adding proper initialization
  - Result: Zero PYL-W0201 warnings, improved IDE support, enhanced type checker compliance
- [x] **Logging format optimization** - Converted eager string formatting to lazy % formatting in sensor modules
- [x] **Type annotation improvements** - Added Optional types and fixed method signature compatibility issues
- [x] **Static method optimization** - Converted handle_exception method to @staticmethod in sensor_imu.py
  - Added @staticmethod decorator to handle_exception method that doesn't use instance state
  - Updated call site from instance method to class method call (IMU.handle_exception)
  - Eliminated unnecessary self parameter, improving memory efficiency and code clarity
  - Resolved PYL-R0201 pylint warning for better code structure
  - Zero risk change - method only performs generic exception handling operations

### **Multi-Language Voice System (Dec 2024)** ✅ COMPLETED
- [x] **Complete multi-language voice system implementation**
  - Added support for 8 languages: EN, EO, DE, FR, ES, HI, PL, PT
  - Implemented runtime language switching via voice commands
  - Created language-specific command maps with native translations
  - Fixed circular import issues with lazy loading approach
  - Enhanced voice_manager.py with proper language switching
  - Updated voice_control.py to use language-specific command maps
  - Added language switching pattern: "spider" + target language name
  - Updated documentation in doc_codebase_guide.md and doc_roadmap.md
  - All languages support switching to all other languages
  - Complete command coverage (45 commands per language)
  - Thread-safe language switching with proper model reloading

### **Web Interface Language Switching (Dec 2024)** ✅ COMPLETED
- [x] **Web interface for multi-language voice switching**
  - Added /language POST endpoint for language switching
  - Enhanced voice.html with language selection buttons
  - Added switchLanguage() JavaScript function with visual feedback
  - Support for all 8 languages with flag icons
  - Success/error notifications for language switching
  - Maintains existing voice control functionality
  - Language buttons trigger server-side language switching

### **LED Feedback System (Dec 2024)** ✅ COMPLETED
- [x] **Centralized LED feedback system for user readiness**
  - Created actuator_led_commands.py with flexible LED pattern handling
  - Added server ready flash (green) when server starts
  - Added language switching glow (red) during language switching
  - Added language ready flash (blue) when language switching completes
  - Integrated LED feedback into voice_manager.py for language switching
  - Initialized LED commands in main.py with server.process_command
  - Thread-safe LED patterns with proper cleanup and error handling
  - Parameterized methods for future LED usage expansion
  - All LED patterns run in separate daemon threads
  - Performance optimized with lazy logging formatting

### **Cyclic Import Resolution (Dec 2024)** ✅ COMPLETED
- [x] **Resolve cyclic import in voice system**
  - Broke cyclic import: voice_command_handler → voice_manager → voice_control
  - Replaced direct import with callback pattern for language switching
  - Added language_switcher parameter to VoiceCommandHandler constructor
  - Updated VoiceControl to pass language switcher callback
  - Updated VoiceManager to pass self.switch_language as callback
  - Maintains all functionality while eliminating circular dependency
  - All voice modules now import successfully without cyclic imports