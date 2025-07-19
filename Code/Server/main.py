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

        video_thread = threading.Thread(target=server.transmit_video, args=(shutdown_event,), daemon=True)
        command_thread = threading.Thread(target=server.receive_commands, args=(shutdown_event,), daemon=True)

        video_thread.start()
        command_thread.start()

        print("Server started. Press Ctrl+C to stop.")
        shutdown_event.wait()

    except KeyboardInterrupt:
        print("\nStopping server...")

        shutdown_event.set()  # signal threads to exit

        if server:
            server.is_tcp_active = False
            server.stop_server()

        print("Server stopped.")
        os._exit(0)