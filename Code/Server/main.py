# -*- coding: utf-8 -*-
import threading
import Thread
import time
from server import Server
shutdown_event = threading.Event()
       
if __name__ == '__main__':
    try:
        server = Server()
        server.start_server()
        server.is_tcp_active = True

        video_thread = threading.Thread(target=server.transmit_video, args=(shutdown_event,))
        command_thread = threading.Thread(target=server.receive_commands, args=(shutdown_event,))

        video_thread.start()
        command_thread.start()

        print("Server started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping server...")

        shutdown_event.set()  # signal threads to exit

        if video_thread:
            video_thread.join()
        if command_thread:
            command_thread.join()

        if server:
            server.is_tcp_active = False
            server.stop_server()

        print("Server stopped.")