# -*- coding: utf-8 -*-
import threading
import time
import os
from server import Server
from voice_control import VoiceControl
shutdown_event = threading.Event()
       
if __name__ == '__main__':
    try:
        server = Server()
        server.start_server()
        server.is_tcp_active = True

        video_thread = threading.Thread(target=server.transmit_video, args=(shutdown_event,), daemon=True)
        command_thread = threading.Thread(target=server.receive_commands, args=(shutdown_event,), daemon=True)

        video_thread.start()
        command_thread.start()

        voice = VoiceControl(server.process_command, server.ultrasonic_sensor)
        voice_thread = threading.Thread(target=voice.start, daemon=True)
        voice_thread.start()

        print("Server started. Press Ctrl+C to stop.")
        shutdown_event.wait()

    except KeyboardInterrupt:
        print("\nStopping server...")

        shutdown_event.set()

        if voice:
            voice.stop()  # <-- New graceful shutdown

        if server:
            server.is_tcp_active = False
            server.stop_server()

        print("Server stopped.")
        os._exit(0)