# main.py
from websockets.asyncio.server import serve
import SingleClientSocketServer
import asyncio
import threading
import time
import packet
import control

def main_thread(server):
    ctrl = control.Control()
    while True:
        time.sleep(1)
        distance = ctrl.get_distance()
        suiveur = ctrl.get_line_position()
        # Read data from captors here
        sender = packet.data_to_packet(distance, suiveur)
        # Send data to godot
        server.send_packet(sender)
        # Get data from godot
        receiver = server.get_last_received_packet()
        if receiver != None:
            # W should parse the data using the packaet methods and update the captors
            angle, vitesse = packet.packet_to_data(receiver)
            ctrl.set_angle(angle)
            ctrl.set_speed(vitesse)
            print(f"Angle : {angle}, vitesse : {vitesse}")

def main():
    # Create and start the WebSocket server
    server = SingleClientSocketServer.SingleClientWebSocketServer()
    # Start background tasks for sending packets
    server.start_background_tasks()
    # Start the WebSocket server in the main thread
    thread = threading.Thread(target=main_thread, args=(server,))
    thread.start()

    asyncio.run(server.start_server())
    pass

if __name__ == "__main__":
    main()