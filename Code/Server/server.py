# -*- coding: utf-8 -*-
import io
import time
import fcntl
import socket
import struct
from threading import Condition
import threading
from led import Led
from servo import Servo
from buzzer import Buzzer
from control import Control
from adc import ADC
from ultrasonic import Ultrasonic
from command import COMMAND as cmd
from camera import Camera  

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
class Server:
    def __init__(self):
        # Initialize server state and components
        self.is_tcp_active = False
        self.is_servo_relaxed = False
        self.led_controller = Led()
        self.adc_sensor = ADC()
        self.servo_controller = Servo()
        self.buzzer_controller = Buzzer()
        self.control_system = Control()
        self.ultrasonic_sensor = Ultrasonic()
        self.camera_device = Camera()  
        self.control_system.condition_thread.start()

        self.command_handlers = {
            cmd.CMD_BUZZER: self.handle_buzzer,
            cmd.CMD_POWER: self.handle_power,
            cmd.CMD_LED: self.handle_led,
            cmd.CMD_LED_MOD: self.handle_led,
            cmd.CMD_SONIC: self.handle_sonic,
            cmd.CMD_HEAD: self.handle_head,
            cmd.CMD_CAMERA: self.handle_camera,
            cmd.CMD_RELAX: self.handle_relax,
            cmd.CMD_SERVOPOWER: self.handle_servo_power,
            cmd.CMD_MOVE: self.handle_move
        }

    def handle_buzzer(self, parts):
        if len(parts) >= 2:
            self.buzzer_controller.set_state(parts[1] == "1")

    def handle_power(self, parts):
        try:
            battery_voltage = self.adc_sensor.read_battery_voltage()
            response = f"{cmd.CMD_POWER}#{battery_voltage[0]}#{battery_voltage[1]}\n"
            self.send_data(self.command_connection, response)
            if battery_voltage[0] < 5.5 or battery_voltage[1] < 6:
                for _ in range(3):
                    self.buzzer_controller.set_state(True)
                    time.sleep(0.15)
                    self.buzzer_controller.set_state(False)
                    time.sleep(0.1)
        except:
            pass

    def handle_led(self, parts):
        self.led_controller.process_light_command(parts)

    def handle_sonic(self, parts):
        distance = self.ultrasonic_sensor.get_distance()
        response = f"{cmd.CMD_SONIC}#{distance}\n"
        self.send_data(self.command_connection, response)

    def handle_head(self, parts):
        if len(parts) == 3:
            self.servo_controller.set_servo_angle(int(parts[1]), int(parts[2]))

    def handle_camera(self, parts):
        if len(parts) == 3:
            x = self.control_system.restrict_value(int(parts[1]), 50, 180)
            y = self.control_system.restrict_value(int(parts[2]), 0, 180)
            self.servo_controller.set_servo_angle(0, x)
            self.servo_controller.set_servo_angle(1, y)

    def handle_relax(self, parts):
        self.is_servo_relaxed = not self.is_servo_relaxed
        self.control_system.relax(self.is_servo_relaxed)
        print("relax" if self.is_servo_relaxed else "unrelax")

    def handle_servo_power(self, parts):
        if len(parts) >= 2:
            if parts[1] == "0":
                self.control_system.servo_power_disable.on()
            else:
                self.control_system.servo_power_disable.off()

    def handle_move(self, parts):
        self.control_system.command_queue = parts
        self.control_system.timeout = time.time()

    def get_interface_ip(self):
        # Get the IP address of the wlan0 interface
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(sock.fileno(),
                                            0x8915,
                                            struct.pack('256s', b'wlan0'[:15])
                                            )[20:24])

    def start_server(self):
        # Start the video and command servers
        host_ip = self.get_interface_ip()
        self.video_socket = socket.socket()
        self.video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.video_socket.bind((host_ip, 8002))
        self.video_socket.listen(1)
        self.command_socket = socket.socket()
        self.command_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.command_socket.bind((host_ip, 5002))
        self.command_socket.listen(1)
        print('Server address: ' + host_ip)

    def stop_server(self):
        try:
            if hasattr(self, 'video_connection'):
                self.video_connection.close()
                self.video_connection = None
            if hasattr(self, 'command_connection'):
                self.command_connection.close()
                self.command_connection = None
            if hasattr(self, 'video_raw_socket'):
                self.video_raw_socket.close()
                self.video_raw_socket = None
            if hasattr(self, 'command_raw_socket'):
                self.command_raw_socket.close()
                self.command_raw_socket = None
        except Exception as e:
            print("Error during stop_server:", e)

    def process_command(self, parts):
        if not parts or parts[0].strip() == "":
            return

        command = parts[0].strip()
        handler = self.command_handlers.get(command)

        if handler:
            handler(parts)
        else:
            print(f"Unknown command received: {command} | full: {parts}")
            self.control_system.command_queue = parts
            self.control_system.timeout = time.time()


    def send_data(self, connection, data):
        try:
            if data.strip():  # skip empty or whitespace-only strings
                connection.send(data.encode('utf-8'))
        except Exception as e:
            print(e)


    def transmit_video(self, shutdown_event):
        while not shutdown_event.is_set():
            try:
                print("Waiting for video connection...")
                self.video_raw_socket, addr = self.video_socket.accept()
                self.video_raw_socket.settimeout(1.0)
                self.video_connection = self.video_raw_socket.makefile('wb')
                print("Video socket connected ...")

                self.camera_device.start_stream()
                while not shutdown_event.is_set():
                    try:
                        frame = self.camera_device.get_frame()
                        frame_length = len(frame)
                        length_binary = struct.pack('<I', frame_length)
                        self.video_connection.write(length_binary)
                        self.video_connection.write(frame)
                    except Exception as e:
                        print("Video transmission error:", e)
                        break
                self.camera_device.stop_stream()

            except Exception as e:
                print("Video accept failed:", e)
                time.sleep(1)


    def receive_commands(self, shutdown_event):
        while not shutdown_event.is_set():
            try:
                print("Waiting for command connection...")
                self.command_raw_socket, self.command_client_address = self.command_socket.accept()
                self.command_raw_socket.settimeout(1.0)
                self.command_connection = self.command_raw_socket  
                print("Client connection successful!")
            except Exception as e:
                print("Client connect failed:", e)
                time.sleep(1)
                continue  # Retry accept()

            while not shutdown_event.is_set():
                try:
                    received_data = self.command_connection.recv(1024).decode('utf-8')
                except socket.timeout:
                    continue
                except Exception as e:
                    print("Receive error:", e)
                    break

                if received_data == "" and self.is_tcp_active:
                    print("Client disconnected.")
                    break

                command_array = [cmd for cmd in received_data.split('\n') if cmd.strip()]
                print("Received command array:", command_array)

                for single_command in command_array:
                    parts = single_command.split("#")
                    self.process_command(parts)

            print("Command session ended. Awaiting new connection...")

        print("close_recv")