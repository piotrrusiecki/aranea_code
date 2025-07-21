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
  const cmd = `CMD_MOVE#${gaitMode}#${x}#${y}#${moveSpeed}#${actionMode}`;
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

updateHeadDisplay();
