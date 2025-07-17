import sounddevice as sd
import queue
import json
import socket
import time
import threading
import difflib
from vosk import Model, KaldiRecognizer

class RobotClient:
    def __init__(self, ip='127.0.0.1', port=5002):
        self.ip = ip
        self.port = port
        self.sock = None
        self.tcp_flag = False

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip, self.port))
            self.tcp_flag = True
            print(f"[INFO] Connected to robot server at {self.ip}:{self.port}")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
            self.tcp_flag = False

    def send_data(self, command):
        if self.tcp_flag and self.sock:
            try:
                self.sock.send((command + '\n').encode('utf-8'))
                print(f"[CMD] {command}")
            except Exception as e:
                print(f"[ERROR] Send failed: {e}")

    def stop(self):
        try:
            self.sock.send(b"CMD_MOVE#1#0#0#8#0\n")
        except:
            pass

    def close(self):
        if self.sock:
            self.sock.close()
        self.tcp_flag = False
        print("[INFO] Disconnected.")

model_path = r"Q:\Code\aranea_code\voice"
samplerate = 16000            
blocksize = 4000

print("[DEBUG] Loading Vosk model...")
model = Model(model_path)
print("[DEBUG] Vosk model loaded.")

command_map = {
    "iru": "CMD_MOVE#1#0#35#8#0",
    "iru reen": "CMD_MOVE#1#0#-35#8#0",
    "iru maldekstren": "CMD_MOVE#1#-35#0#8#0",
    "iru dekstren": "CMD_MOVE#1#35#0#8#0",

    "turnu maldekstren": ["CMD_MOVE#1#5#5#8#-10","CMD_MOVE#1#-5#0#8#-10","CMD_MOVE#1#5#-5#8#-10","CMD_MOVE#1#-5#-5#8#-10"],
    "turnu dekstren": ["CMD_MOVE#1#5#5#8#10","CMD_MOVE#1#-5#0#8#10","CMD_MOVE#1#5#-5#8#10","CMD_MOVE#1#-5#-5#8#10"],
    "turnu iomete maldekstren": "CMD_MOVE#1#5#-5#8#-10",
    "turnu iomete dekstren": "CMD_MOVE#1#5#-5#8#10",

    "klinu fronte": "CMD_ATTITUDE#0#15#-2",
    "klinu reen": "CMD_ATTITUDE#0#-15#-2",
    "klinu maldekstren": "CMD_ATTITUDE#-15#0#-2",
    "klinu dekstren": "CMD_ATTITUDE#15#0#-2",

    "rigardu fronte": ["CMD_HEAD#0#90", "CMD_HEAD#1#90"],
    "rigardu maldekstren": "CMD_HEAD#1#135",
    "rigardu dekstren": "CMD_HEAD#1#45",
    "rigardu supren": "CMD_HEAD#0#180",
    "rigardu malsupren": "CMD_HEAD#0#50",

    "ripozu": "CMD_SERVOPOWER#0",
    "veku": "CMD_SERVOPOWER#1",

    "movu maldekstren": "CMD_POSITION#-40#0#0",
    "movu dekstren": "CMD_POSITION#40#0#0",
    "movu reen": "CMD_POSITION#0#-40#0",
    "movu fronte": "CMD_POSITION#0#40#0",

    "lumigu ruĝe": "CMD_LED#255#0#0",
    "lumigu verde": "CMD_LED#0#255#0",
    "lumigu blue": "CMD_LED#0#0#255",
    "malŝaltu lumo": "CMD_LED#0#0#0",

    "evitu obstaklon": "START_SONIC_MODE",
    "haltu eviton": "STOP_SONIC_MODE", 
    
    "marŝu": "START_MARCH",
    "marŝu maldekstren": "START_MARCH_LEFT",
    "marŝu dekstren": "START_MARCH_RIGHT",
    "marŝu reen": "START_MARCH_BACK",

    "kuru": "START_RUN",
    "kuru maldekstren": "START_RUN_LEFT",
    "kuru dekstren": "START_RUN_RIGHT",
    "kuru reen": "START_RUN_BACK",    
 
    "haltu": "STOP_MOTION_LOOP"

}

q = queue.Queue()
client = RobotClient()
client.connect()


def callback(indata, frames, time, status):
    if status:
        print("[WARN] Audio:", status)
    q.put(bytes(indata))


march_mode = False
march_thread = None

motion_mode = False
motion_thread = None

def motion_loop(gait, x, y, speed, head_angle):
    global motion_mode
    # Head direction
    client.send_data(f"CMD_HEAD#1#{head_angle}")
    client.send_data("CMD_HEAD#0#90")  # Vertical center
    while motion_mode:
        try:
            client.send_data("CMD_SONIC")
            response = client.sock.recv(1024).decode("utf-8").strip()
            if response.startswith("CMD_SONIC#"):
                distance = float(response.split("#")[1])
                print(f"🔎 Sonic distance: {distance:.1f} cm")
                if distance < 30:
                    print("🛑 Obstacle too close. Stopping.")
                    client.stop()
                    for _ in range(3):
                        client.send_data("CMD_LED#255#0#0")
                        time.sleep(0.2)
                        client.send_data("CMD_LED#0#0#0")
                        time.sleep(0.2)
                    break
                client.send_data(f"CMD_MOVE#{gait}#{x}#{y}#{speed}#0")
                time.sleep(0.6)
            time.sleep(0.5)
        except Exception as e:
            print(f"❌ Motion loop error: {e}")
            break
    client.send_data("CMD_HEAD#1#90")  # Restore head
    motion_mode = False

sonic_mode = False

def motion_loop_simple(gait, x, y, speed, head_angle):
    global motion_mode
    client.send_data(f"CMD_HEAD#1#{head_angle}")
    client.send_data("CMD_HEAD#0#90")
    for _ in range(20):  # e.g., 20 steps
        if not motion_mode:
            break
        client.send_data(f"CMD_MOVE#{gait}#{x}#{y}#{speed}#0")
        time.sleep(0.6)
    client.stop()
    client.send_data("CMD_HEAD#1#90")
    motion_mode = False


# Background loop to monitor sonic distance and trigger movement
def sonic_monitor_loop():
    global sonic_mode
    while sonic_mode:
        try:
            client.send_data("CMD_SONIC")
            response = client.sock.recv(1024).decode("utf-8").strip()
            if response.startswith("CMD_SONIC#"):
                try:
                    distance = float(response.split("#")[1])
                    print(f"🔎 Sonic distance: {distance:.1f} cm")
                    if distance < 40:
                        client.send_data("CMD_MOVE#1#0#-35#8#0")
                        time.sleep(0.6)
                        client.stop()
                    elif distance > 50:
                        client.send_data("CMD_MOVE#1#0#35#8#0")
                        time.sleep(0.6)
                        client.stop()
                except ValueError:
                    print(f"[INFO] Malformed distance in: {response}")
            time.sleep(1.5)
        except Exception as e:
            print(f"[ERROR] Sonic mode error: {e}")
            break


# Marching loop based on direction and speed
def march_loop(x, y, speed):
    global march_mode
    if x < 0:
        client.send_data("CMD_HEAD#1#135")  # Look left
    elif x > 0:
        client.send_data("CMD_HEAD#1#45")   # Look right
    else:
        client.send_data("CMD_HEAD#1#90")   # Look forward
    client.send_data("CMD_HEAD#0#90")       # Look straight

    while march_mode:
        try:
            client.send_data("CMD_SONIC")
            response = client.sock.recv(1024).decode("utf-8").strip()
            if response.startswith("CMD_SONIC#"):
                distance = float(response.split("#")[1])
                print(f"🔎 Sonic distance: {distance:.1f} cm")
                if distance < 25:
                    print("[STOP] Obstacle too close. Stopping.")
                    client.stop()
                    # Flash red LED
                    for _ in range(3):
                        client.send_data("CMD_LED#255#0#0")
                        time.sleep(0.2)
                        client.send_data("CMD_LED#0#0#0")
                        time.sleep(0.2)
                    break
                client.send_data(f"CMD_MOVE#2#{x}#{y}#{speed}#0")
                time.sleep(0.6)
            time.sleep(0.5)
        except Exception as e:
            print(f"[ERROR] March loop error: {e}")
            break
    client.send_data("CMD_HEAD#1#90")   # Recenter head

# Replace command execution section with new logic supporting sonic mode
import difflib
sonic_thread = None

try:
    sd.default.device = (1, None)                                                                            
    with sd.RawInputStream(samplerate=samplerate, blocksize=None, dtype='int16', channels=1, callback=callback):
        print("[INFO] Listening (fuzzy fallback enabled + sonic mode)... Ctrl+C to stop")
        recognizer = KaldiRecognizer(model, samplerate)

        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                spoken = result.get("text", "").strip()
                if not spoken:
                    continue
                if spoken in command_map:
                    command = command_map[spoken]
                    print(f"[INFO] Exact match: '{spoken}' → {command}")
                else:
                    match = difflib.get_close_matches(spoken, command_map.keys(), n=1, cutoff=0.6)
                    if match:
                        spoken = match[0]
                        command = command_map[spoken]
                        print(f"[INFO] Fuzzy match: '{result.get('text')}' ≈ '{spoken}' → {command}")
                    else:
                        print(f"[ERROR] No match for: '{spoken}'")
                        continue

                if command == "START_SONIC_MODE":
                    if not sonic_mode:
                        print("▶️ Starting sonic mode...")
                        sonic_mode = True
                        sonic_thread = threading.Thread(target=sonic_monitor_loop, daemon=True)
                        sonic_thread.start()
                    continue
                elif command == "STOP_SONIC_MODE":
                    if sonic_mode:
                        print("[STOP] Stopping sonic mode.")
                        sonic_mode = False
                    continue

                elif command == "STOP_MARCH_MODE":
                    if march_mode:
                        print("[STOP] Stopping march mode.")
                        march_mode = False
                    continue

                if isinstance(command, str) and command in {"START_MARCH", "START_MARCH_LEFT", "START_MARCH_RIGHT"}:
                    if not motion_mode:
                        print("[INFO] Starting march")
                        motion_mode = True
                        x, y, speed = 0, 35, 10
                        angle = 90
                        if "maldekstren" in spoken:
                            x, y = -35, 0
                            angle = 180
                        elif "dekstren" in spoken:
                            x, y = 35, 0
                            angle = 0
                        motion_thread = threading.Thread(target=motion_loop, args=(2, x, y, speed, angle), daemon=True)
                        motion_thread.start()
                    continue

                elif isinstance(command, str) and command in {"START_RUN", "START_RUN_LEFT", "START_RUN_RIGHT"}:
                    if not motion_mode:
                        print("[INFO] Starting run")
                        motion_mode = True
                        x, y, speed = 0, 20, 10
                        angle = 90
                        if "maldekstren" in spoken:
                            x, y = -20, 0
                            angle = 180
                        elif "dekstren" in spoken:
                            x, y = 20, 0
                            angle = 0
                        motion_thread = threading.Thread(target=motion_loop, args=(1, x, y, speed, angle), daemon=True)
                        motion_thread.start()
                    continue

                elif command == "START_MARCH_BACK":
                    if not motion_mode:
                        print("[INFO] Starting backward march")
                        motion_mode = True
                        gait, x, y, speed, angle = 2, 0, -35, 8, 90
                        motion_thread = threading.Thread(
                            target=motion_loop_simple, args=(gait, x, y, speed, angle), daemon=True)
                        motion_thread.start()
                    continue

                elif command == "START_RUN_BACK":
                    if not motion_mode:
                        print("[INFO] Starting backward run")
                        motion_mode = True
                        gait, x, y, speed, angle = 1, 0, -35, 10, 90
                        motion_thread = threading.Thread(
                            target=motion_loop_simple, args=(gait, x, y, speed, angle), daemon=True)
                        motion_thread.start()
                    continue

                elif command == "STOP_MOTION_LOOP":
                    if motion_mode:
                        print("[INFO] Stopping motion loop.")
                        motion_mode = False
                        client.send_data("CMD_HEAD#1#90")
                        client.send_data("CMD_LED#0#0#0")
                        client.stop()
                    continue

                if isinstance(command, list):
                    for c in command:
                        client.send_data(c)
                        time.sleep(0.6)
                    client.stop()
                else:
                    client.send_data(command)
                    if command.startswith("CMD_MOVE"):
                        time.sleep(0.6)
                        client.stop()

except KeyboardInterrupt:
    print("[STOP] Ctrl+C received — shutting down robot safely...")
    client.send_data("CMD_MOVE#1#0#0#8#0")
    client.send_data("CMD_SERVOPOWER#0")
    client.send_data("CMD_LED#0#0#0")
    client.send_data("CMD_HEAD#1#90")
    client.send_data("CMD_HEAD#0#90")
    client.close()                           
