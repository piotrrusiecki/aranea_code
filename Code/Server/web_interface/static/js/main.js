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

// State holders
let attitudeX = 0, attitudeY = 0, attitudeZ = 0;
let positionX = 0, positionY = 0, positionZ = 0;

// IMU
let imuPolling = false;
let imuPollInterval = null;

function sendCommand(cmd) {
  fetch('/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cmd })
  })
  .then(r => r.json())
  .then(data => console.log("Command sent:", data))
  .catch(err => console.error("Command failed:", err));
}

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
              document.getElementById('imuYaw').textContent = data.yaw.toFixed(2);
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
  runRoutine('stop_motion');
}

function toggleSonic(isOn) {
  if (isOn) {
    runRoutine('start_sonic');
  } else {
    runRoutine('stop_sonic');
  }
}

updateHeadDisplay();

// --- Routine Trigger ---
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
