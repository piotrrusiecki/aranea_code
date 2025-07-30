## Robot Roadmap

### Completed
[x] Turning!
[x] Remove auto servo relax logic
[x] Logging and diagnostic tools - switchable to levels

### Voice Control
[ ] All voice commands as simple commands in dispatcher
[ ] Revise voice commands to include all simple moves and routines
[ ] Refactor voice integration to command dispatcher
[ ] Multilingual voice control (runtime switch)

### Core Architecture
[ ] Centralize status_flag management in robot_state.py
[ ] Centralise all config into robot_config.py
[ ] Standalone AP fallback mode

### Web Interface
[ ] Improve web UI responsiveness (mobile scaling, overlap fix)
[ ] Complete diagnostics tab (IMU, servo state, ultrasonic, battery), incl graphs

### Robot Behavior
[ ] Implement patrol mode (ultrasonic + head logic)
[ ] LED control and feedback
[ ] Dancing composite moves
[ ] Dancing mode (beat detection + movement)
[ ] LiDAR integration (future)

### External Control & APIs
[ ] REST API or WebSocket interface
[ ] Git pull auto-updater in WebUI

### Advanced Capabilities
[ ] Routine recorder and editor via WebUI
[ ] Local speech feedback (e.g., espeak)
[ ] Posture recovery using IMU
[ ] Persistent logging via file or SQLite
[ ] Battery graph and trend history

### Maintenance
[ ] Test scripts and testing; regression testing 
[ ] Fresh install deployment