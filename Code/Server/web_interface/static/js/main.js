let gaitMode = 1;
let actionMode = 0;
let moveSpeed = 8;
let tilt = 90;
let pan = 90;

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

updateHeadDisplay();
