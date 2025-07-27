let gaitMode = 1;
let actionMode = 0;
let moveSpeed = 8;
let tilt = 90;
let pan = 90;

// Step constants
const stepAttX = 3;
const stepAttY = 3;
const stepAttZ = 3;

const stepPosX = 5;
const stepPosY = 5;
const stepPosZ = 4;

const speed = document.getElementById("speedSlider").value;

// State holders
let attitudeX = 0, attitudeY = 0, attitudeZ = 0;
let positionX = 0, positionY = 0, positionZ = 0;

// IMU
let imuPolling = false;
let imuPollInterval = null;

// Calibration state
const calibLegNames = ["one", "two", "three", "four", "five", "six"];
let calibLegs = [
  { x: 0, y: 72, z: 0 }, // Default values, adjust if needed or load from backend
  { x: 0, y: 72, z: 0 },
  { x: 0, y: 72, z: 0 },
  { x: 0, y: 72, z: 0 },
  { x: 0, y: 72, z: 0 },
  { x: 0, y: 72, z: 0 }
];
let calibSelectedLeg = 0; // 0 = one, 1 = two, ...

function sendCommand(cmd, callback = null) {
  fetch('/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cmd })
  })
  .then(r => r.json())
  .then(data => {
    console.log("Command sent:", data);
    if (callback) callback(data.result); // pass only the result payload
  })
  .catch(err => console.error("Command failed:", err));
}

function runRoutine(routine) {
  fetch('/routine', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ routine })
  })
  .then(r => r.json())
  .then(data => console.log("Routine triggered:", data))
  .catch(err => console.error("Routine failed:", err));
}

// -- Calibration Mode Integration --

// Check if robot is in calibration mode (returns a Promise)
function checkCalibrationMode() {
  return fetch("/calibration_mode")
    .then(r => r.json())
    .then(data => data.calibration_mode === true)
    .catch(() => false);
}

// Request robot to enter calibration mode (neutral pose)
function prepareForCalibration() {
  runRoutine('sys_prep_calibration');
  // Poll every 200ms until calibration_mode is ON (max 2s)
  let tries = 0;
  function poll() {
    fetch('/calibration_mode')
      .then(r => r.json())
      .then(data => {
        if (data.calibration_mode) {
          updateCalibrationModeStatus();
        } else if (tries++ < 10) {
          setTimeout(poll, 200);
        } else {
          updateCalibrationModeStatus(); // Give up after 2s, update UI anyway
        }
      });
  }
  setTimeout(poll, 200);
}


// Request robot to exit calibration mode (optional)
function exitCalibration() {
  runRoutine('sys_exit_calibration');
  let tries = 0;
  function poll() {
    fetch('/calibration_mode')
      .then(r => r.json())
      .then(data => {
        if (!data.calibration_mode) {
          updateCalibrationModeStatus();
        } else if (tries++ < 10) {
          setTimeout(poll, 200);
        } else {
          updateCalibrationModeStatus();
        }
      });
  }
  setTimeout(poll, 200);
}


// Select a leg to calibrate
function selectCalibrationLeg(idx) {
  calibSelectedLeg = idx;
  // Update button styles
  for (let i = 0; i < 6; i++) {
    document.getElementById('legBtn' + (i + 1)).classList.toggle('active', i === idx);
  }
  updateCalibrationFields();
}

// Update XYZ value fields for the selected leg
function updateCalibrationFields() {
  const leg = calibLegs[calibSelectedLeg];
  document.getElementById('calibX').value = leg.x;
  document.getElementById('calibY').value = leg.y;
  document.getElementById('calibZ').value = leg.z;
}

// Nudge the current axis and send command (only if in calibration mode)
function nudgeCalibration(axis, delta) {
  checkCalibrationMode().then(isCalib => {
    if (!isCalib) {
      alert("Robot is not in calibration mode. Click 'Prepare for Calibration' first.");
      return;
    }
    const leg = calibLegs[calibSelectedLeg];
    leg[axis] += delta;
    updateCalibrationFields();
    sendCommand(`CMD_CALIBRATION#${calibLegNames[calibSelectedLeg]}#${leg.x}#${leg.y}#${leg.z}`);
  });
}

// Save all current calibration values to robot (only if in calibration mode)
function saveCalibration() {
  checkCalibrationMode().then(isCalib => {
    if (!isCalib) {
      alert("Robot is not in calibration mode. Click 'Prepare for Calibration' first.");
      return;
    }
    sendCommand("CMD_CALIBRATION#save");
    const status = document.getElementById('calibStatus');
    status.textContent = "Saved!";
    setTimeout(() => { status.textContent = ""; }, 2000);
  });
}

// Fetch calibration points and update UI
function loadCalibrationFromRobot() {
  fetch("/calibration")
    .then(r => r.json())
    .then(data => {
      for (let i = 0; i < 6; i++) {
        calibLegs[i].x = data[i][0];
        calibLegs[i].y = data[i][1];
        calibLegs[i].z = data[i][2];
      }
      updateCalibrationFields();
    })
    .catch(() => {
      // Could show error or ignore
    });
}

// Detect Calibration tab selection using Bootstrap event
document.addEventListener("DOMContentLoaded", () => {
  // Setup tab show event (Bootstrap 5+)
  const tabEl = document.querySelector('a[href="#calibration"]');
  if (tabEl) {
    tabEl.addEventListener('shown.bs.tab', function (event) {
      loadCalibrationFromRobot();
    });
  }
  // Default select first leg
  selectCalibrationLeg(0);
});

// ---- Movement, Voice, IMU, and Other Robot Controls ----

function sendHead(newTilt, newPan) {
  newTilt = Math.max(50, Math.min(180, newTilt));
  newPan = Math.max(0, Math.min(180, newPan));
  if (Math.abs(newTilt - tilt) >= 1) {
    tilt = newTilt;
    sendCommand(`CMD_HEAD#0#${tilt}`);
  }
  if (Math.abs(newPan - pan) >= 1) {
    pan = newPan;
    sendCommand(`CMD_HEAD#1#${pan}`);
  }
  updateHeadDisplay();
}

function setGaitMode(mode) {
  gaitMode = mode;
  document.getElementById("gaitModeDisplay").innerText = gaitMode;
}

function setActionMode(mode) {
  actionMode = mode;
  document.getElementById("actionModeDisplay").innerText = actionMode;
}

function updateHeadDisplay() {
  document.getElementById("tiltDisplay").innerText = tilt;
  document.getElementById("panDisplay").innerText = pan;
}

function updateSpeed(val) {
  moveSpeed = parseInt(val);
  document.getElementById("speedDisplay").innerText = val;
}

function sendMove(x, y) {
  const angle = computeAngle(x, y);
  const cmd = `CMD_MOVE#${gaitMode}#${x}#${y}#${moveSpeed}#${angle}`;
  sendCommand(cmd);
}

function toggleVoice(action) {
  fetch('/voice', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action })
  })
  .then(r => r.json())
  .then(data => {
    if (data.status) {
      document.getElementById("voiceStatus").innerText = data.status.toUpperCase();
    }
  })
  .catch(err => console.error("Voice control toggle failed:", err));
}

function computeAngle(x, y) {
  if (actionMode === 0 || (x === 0 && y === 0)) return 0;
  const radians = Math.atan2(x, y);  // x then y: forward is y+
  let angleDeg = radians * (180 / Math.PI);
  if (angleDeg >= -90 && angleDeg <= 90) {
    return Math.round(((angleDeg + 90) / 180) * 20 - 10);  // [-90, 90] → [-10, 10]
  } else {
    if (angleDeg < 0) angleDeg += 360;
    return Math.round(((angleDeg - 270) / 180) * -20 + 10); // [270–360]+[0–90] → [10, -10]
  }
}

function adjustAttitude(deltaX, deltaY, reset = false) {
  if (reset) {
    attitudeX = 0;
    attitudeY = 0;
    attitudeZ = 0;
  } else {
    attitudeX = clamp(attitudeX + deltaX, -15, 15);
    attitudeY = clamp(attitudeY + deltaY, -15, 15);
  }
  sendCommand(`CMD_ATTITUDE#${attitudeX}#${attitudeY}#${attitudeZ}`);
}

function adjustAttitudeZ(deltaZ) {
  attitudeZ = clamp(attitudeZ + deltaZ, -15, 15);
  sendCommand(`CMD_ATTITUDE#${attitudeX}#${attitudeY}#${attitudeZ}`);
}

function adjustPosition(deltaX, deltaY, reset = false) {
  if (reset) {
    positionX = 0;
    positionY = 0;
    positionZ = 0;
  } else {
    positionX = clamp(positionX + deltaX, -40, 40);
    positionY = clamp(positionY + deltaY, -40, 40);
  }
  sendCommand(`CMD_POSITION#${positionX}#${positionY}#${positionZ}`);
}

function adjustPositionZ(deltaZ) {
  positionZ = clamp(positionZ + deltaZ, -20, 20);
  sendCommand(`CMD_POSITION#${positionX}#${positionY}#${positionZ}`);
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function fetchIMU() {
    fetch("/imu")
        .then(response => response.json())
        .then(data => {
            document.getElementById('imuPitch').textContent = data.pitch.toFixed(2);
            document.getElementById('imuRoll').textContent = data.roll.toFixed(2);
            if (document.getElementById('imuYaw')) {
              document.getElementById('imuYaw').textContent = data.yaw.toFixed(2);
            }
        })
        .catch(() => {
            document.getElementById('imuPitch').textContent = '--';
            document.getElementById('imuRoll').textContent = '--';
            if (document.getElementById('imuYaw')) {
              document.getElementById('imuYaw').textContent = '--';
            }
        });
}
function toggleIMUPolling() {
    imuPolling = !imuPolling;
    document.getElementById('imuPollingStatus').textContent = imuPolling ? "ON" : "OFF";
    if (imuPolling) {
        fetchIMU();
        imuPollInterval = setInterval(fetchIMU, 1000);
    } else {
        clearInterval(imuPollInterval);
    }
}

function stopMotion() {
  runRoutine('sys_stop_motion');
}

function toggleSonic(isOn) {
  if (isOn) {
    runRoutine('sys_start_sonic');
  } else {
    runRoutine('sys_stop_sonic');
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const tabEl = document.querySelector('a[href="#calibration"]');
  if (tabEl) {
    tabEl.addEventListener('shown.bs.tab', function () {
      loadCalibrationFromRobot();
      updateCalibrationModeStatus();
    });
  }
  // Default select first leg
  selectCalibrationLeg(0);
});
function setCalibrationControlsEnabled(enabled) {
  document.querySelectorAll('#calibration .btn-secondary, #calibration .btn-success').forEach(btn => {
    btn.disabled = !enabled;
  });
}

function updateCalibrationModeStatus() {
  fetch('/calibration_mode')
    .then(r => r.json())
    .then(data => {
      const statusSpan = document.getElementById('calibModeStatus');
      if (data.calibration_mode) {
        statusSpan.textContent = "CALIBRATION MODE ACTIVE";
        statusSpan.classList.remove('text-secondary');
        statusSpan.classList.add('text-success');
        setCalibrationControlsEnabled(true);
      } else {
        statusSpan.textContent = "Calibration mode OFF";
        statusSpan.classList.remove('text-success');
        statusSpan.classList.add('text-secondary');
        setCalibrationControlsEnabled(false);
      }
    });
}

function sendTurn(direction) {
  if (direction === "left") {
    runRoutine("routine_turn_left");
  } else if (direction === "right") {
    runRoutine("routine_turn_right");
  } else {
    console.warn("Invalid turn direction:", direction);
  }
}

function updateSpeedState(value) {
  fetch('/set_speed', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ speed: value })
  });
}

function queryBattery() {
    sendCommand('CMD_BATTERY', function(response) {
        if (response && response.length === 3 && response[0] === "CMD_BATTERY") {
            const loadVoltage = parseFloat(response[1]);
            const raspiVoltage = parseFloat(response[2]);

            updateVoltageBars(loadVoltage, raspiVoltage);
        } else {
            alert("Battery read failed or unexpected response.");
        }
    });
}

function getColor(voltage) {
  if (voltage < 6.0) return 'bg-danger';  // red
  else if (voltage < 7.0) return 'bg-warning';  // yellow
  else return 'bg-success';  // green
}

function updateVoltageBars(loadVoltage, raspiVoltage) {
  const minVoltage = 5.0;
  const maxVoltage = 8.4;

  function getPercent(voltage) {
    return Math.min(100, Math.max(0, ((voltage - minVoltage) / (maxVoltage - minVoltage)) * 100));
  }

  // Calculate fill % for both consistently
  const loadPercent = getPercent(loadVoltage);
  const raspiPercent = getPercent(raspiVoltage);

  const loadBar = document.getElementById('loadBar');
  const raspiBar = document.getElementById('raspiBar');

  loadBar.classList.remove('bg-success', 'bg-warning', 'bg-danger');
  raspiBar.classList.remove('bg-success', 'bg-warning', 'bg-danger');

  loadBar.style.width = loadPercent + '%';
  loadBar.classList.add(getColor(loadVoltage));
  loadBar.textContent = loadVoltage.toFixed(2) + ' V';

  raspiBar.style.width = raspiPercent + '%';
  raspiBar.classList.add(getColor(raspiVoltage));
  raspiBar.textContent = raspiVoltage.toFixed(2) + ' V';
}

function toggleServoTest(isOn) {
  runRoutine(isOn ? "sys_start_servo_test" : "sys_stop_servo_test");
}

updateHeadDisplay();
