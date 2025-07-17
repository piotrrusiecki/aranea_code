import socket

def format_cmd(gait, x, y, speed, r):
    return f"CMD_MOVE#{gait}#{x}#{y}#{speed}#{r}"

print("🧪 CMD_MOVE persistent tester. Press Ctrl+C to exit.")
print("Enter values step by step:")

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('192.168.178.50', 5002))
        print("✅ Connected to robot")

        while True:
            gait = input("Gait (1 or 2): ").strip()
            x = int(input("X: "))
            y = int(input("Y: "))
            speed = int(input("Speed: "))
            r = int(input("Rotation: "))
            cmd = format_cmd(gait, x, y, speed, r)
            s.send((cmd + '\n').encode('utf-8'))
            print(f"📤 Sent: {cmd}\n")

except KeyboardInterrupt:
    print("\n🛑 Exiting.")
except Exception as e:
    print(f"❌ Error: {e}")