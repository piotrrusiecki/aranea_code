# Robot Server Code Structure

Project layout (flattened view with folder grouping):

/aranea_code
|---- main.py                   # System entry point
|---- command.py               # Command constants
|---- command_dispatcher.py    # Core command router
|---- control.py               # Legacy orchestrator
|---- robot_state.py           # Global robot flags and status
|---- robot_gait.py            # Walking gait logic
|---- robot_routines.py        # Predefined movements (turn, patrol, etc.)
|---- robot_calibration.py     # Leg calibration functions
|---- robot_kinematics.py      # Inverse/forward kinematics
|---- robot_pose.py            # Converts leg angles to posture
|---- servo.py                 # Servo motor control logic
|---- adc.py                   # Analog sensor reader
|---- imu.py                   # IMU sensor logic (MPU6050)
|---- ultrasonic.py            # Ultrasonic sensor handler
|---- camera.py                # PiCamera2 handler
|---- buzzer.py                # Sound feedback
|---- led.py                   # LED abstraction
|---- rpi_ledpixel.py          # LED control via GPIO
|---- spi_ledpixel.py          # LED control via SPI
|---- pid.py                   # PID control logic
|---- parameter.py             # Config abstraction
|---- install_aranea.py        # Setup script
|---- aranea-server.service    # Systemd unit file
|---- point.txt                # Saved servo positions
|---- test.py                  # Experimental/test logic
|---- web_server.py            # Flask server

/config
|---- robot_config.py          # Central config (paths, audio, model)
/config/voice
|---- __init__.py
|---- eo.py                    # Esperanto voice config

/web_interface
|---- templates/
      |---- base.html
      |---- index.html
      `---- tabs/
          |---- move.html
          |---- routines.html
          |---- calibration.html
          |---- sensors.html
          |---- hardware.html
          |---- voice.html
          `---- position.html
|---- static/
      |---- js/
            `---- main.js
      |---- css/
            |---- bootstrap.min.css
            |---- bootstrap-icons.min.css
            `---- fonts/
                |---- bootstrap-icons.woff
                `---- bootstrap-icons.woff2

