# -*- coding: utf-8 -*-
import io
import time
import fcntl
import socket
import struct
from threading import Condition
import logging
from actuator_led import Led
from actuator_servo import Servo
from actuator_buzzer import Buzzer
from robot_control import Control
from sensor_adc import ADC
from sensor_ultrasonic import Ultrasonic
from constants_commands import COMMAND as cmd
from sensor_camera import Camera  


logger = logging.getLogger("robot.server")

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class Server:
    def __init__(self, robot_state):
        self.robot_state = robot_state
        self.control_system = Control(robot_state=robot_state)
        self.is_tcp_active = False
        self.is_servo_relaxed = False
        self.led_controller = Led()
        self.adc_sensor = ADC()
        self.servo_controller = Servo()
        self.buzzer_controller = Buzzer()
        self.servo_controller.set_servo_angle(0, 90)  # Pan
        self.servo_controller.set_servo_angle(1, 90)  # Til
        self.ultrasonic_sensor = Ultrasonic()
        self.camera_device = Camera()  

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
            cmd.CMD_MOVE: self.handle_move,
            cmd.CMD_IMU_STATUS: self.handle_imu_status,
            cmd.CMD_CALIBRATION: self.handle_calibration,
            cmd.CMD_ATTITUDE: self.handle_attitude,
            cmd.CMD_POSITION: self.handle_position,
        }

    def handle_calibration(self, parts):
        self.control_system.command_queue = parts
        self.control_system.timeout = time.time()

    def handle_buzzer(self, parts):
        if len(parts) >= 2:
            self.buzzer_controller.set_state(parts[1] == "1")
    def read_battery_voltage(self):
        try:
            return self.adc_sensor.read_battery_voltage()
        except Exception as e:
            logger.error("Battery read failed: %s", e)
            return None
    def handle_imu_status(self, parts):
        pitch, roll, yaw = self.control_system.imu.update_imu_state()
        response = f"{cmd.CMD_IMU_STATUS}#{pitch:.2f}#{roll:.2f}#{yaw:.2f}\n"
        self.send_data(self.command_connection, response)

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
        except Exception as e:
            logger.error("Power handling error: %s", e)

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
        new_state = not self.robot_state.get_flag("servo_relaxed")
        self.robot_state.set_flag("servo_relaxed", new_state)
        self.control_system.relax(new_state)
        logger.info("Relax" if new_state else "Unrelax")

    def handle_servo_power(self, parts):
        if len(parts) >= 2:
            if parts[1] == "0":
                self.control_system.servo_power_disable.on()
            else:
                self.control_system.servo_power_disable.off()

    def handle_move(self, parts):
        self.control_system.command_queue = parts
        self.control_system.timeout = time.time()
        logger.debug("[server] handle_move: command_queue set to %s", parts)

    def handle_attitude(self, parts):
        logger.info("Handling attitude command")
        self.control_system.command_queue = parts.copy()
        self.control_system.timeout = time.time()

    def handle_position(self, parts):
        logger.info("Handling position command")
        self.control_system.command_queue = parts.copy()
        self.control_system.timeout = time.time()


    @staticmethod
    def get_interface_ip():
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
        logger.info('Server address: %s', host_ip)

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
            self.control_system.stop()
            if hasattr(self.camera_device, "stop_stream"):
                self.camera_device.stop_stream()
        except Exception as e:
            logger.error("Error during stop_server: %s", e)

    def process_command(self, parts):
        if not parts or parts[0].strip() == "":
            return

        command = parts[0].strip()
        handler = self.command_handlers.get(command)

        if handler:
            handler(parts)
        else:
            logger.warning("Unknown command received: %s | full: %s", command, parts)
            self.control_system.command_queue = parts
            self.control_system.timeout = time.time()


    @staticmethod
    def send_data(connection, data):
        try:
            if data.strip():  # skip empty or whitespace-only strings
                connection.send(data.encode('utf-8'))
        except Exception as e:
            logger.error("Send data error: %s", e)


    def transmit_video(self, shutdown_event):
        while not shutdown_event.is_set():
            try:
                logger.info("Waiting for video connection...")
                self.video_raw_socket, addr = self.video_socket.accept()
                self.video_raw_socket.settimeout(1.0)
                self.video_connection = self.video_raw_socket.makefile('wb')
                logger.info("Video socket connected ...")

                self.camera_device.start_stream()
                while not shutdown_event.is_set():
                    try:
                        frame = self.camera_device.get_frame()
                        frame_length = len(frame)
                        length_binary = struct.pack('<I', frame_length)
                        self.video_connection.write(length_binary)
                        self.video_connection.write(frame)
                    except Exception as e:
                        logger.error("Video transmission error: %s", e)
                        break
                self.camera_device.stop_stream()

            except Exception as e:
                logger.error("Video accept failed: %s", e)
                time.sleep(1)


    def receive_commands(self, shutdown_event):
        while not shutdown_event.is_set():
            try:
                logger.info("Waiting for command connection...")
                self.command_raw_socket, self.command_client_address = self.command_socket.accept()
                self.command_raw_socket.settimeout(1.0)
                self.command_connection = self.command_raw_socket  
                logger.info("Client connection successful!")
            except Exception as e:
                logger.error("Client connect failed: %s", e)
                time.sleep(1)
                continue  # Retry accept()

            while not shutdown_event.is_set():
                try:
                    received_data = self.command_connection.recv(1024).decode('utf-8')
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error("Receive error: %s", e)
                    break

                if received_data == "" and self.is_tcp_active:
                    logger.warning("Client disconnected.")
                    break

                command_array = [cmd for cmd in received_data.split('\n') if cmd.strip()]
                logger.info("Received command array: %s", command_array)

                for single_command in command_array:
                    parts = single_command.split("#")
                    self.process_command(parts)

            logger.info("Command session ended. Awaiting new connection...")

        logger.info("close_recv")
