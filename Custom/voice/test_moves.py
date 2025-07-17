import socket

def format_cmd(gait, x, y, speed, r):
    return f"CMD_MOVE#{gait}#{x}#{y}#{speed}#{r}"

def cap(val, min_val, max_val):
    return max(min_val, min(max_val, int(val)))

print("🧪 CMD_MOVE persistent tester. Press Ctrl+C to exit.")
print("Enter values step by step:")

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('192.168.178.50', 5002))
        print("✅ Connected to robot")

        while True:
            gait = input("Gait (1 or 2): ").strip()
            x = cap(input("X [-35 to 35]: "), -35, 35)
            y = cap(input("Y [-35 to 35]: "), -35, 35)
            speed = cap(input("Speed [2 to 10]: "), 2, 10)
            r = cap(input("Rotation [-10 to 10]: "), -10, 10)
            cmd = format_cmd(gait, x, y, speed, r)
            s.send((cmd + '\n').encode('utf-8'))
            print(f"📤 Sent: {cmd}\n")

except KeyboardInterrupt:
    print("\n🛑 Exiting.")
except Exception as e:
    print(f"❌ Error: {e}")