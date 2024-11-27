import asyncio
import websockets
import threading

class SingleClientWebSocketServer:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.connected_client = None
        self.client_lock = asyncio.Lock()
        self.last_received_packet = None
        self.sender_event_loop = None

    async def handler(self, websocket, path):
        async with self.client_lock:
            if self.connected_client is not None:
                # Close the previous client connection
                await self.connected_client.close()
            self.connected_client = websocket
            print("Client connected.")

        # Main communication loop with the client
        try:
            async for message in websocket:
                #print(f"Received message of size: {len(message)}")
                self.last_received_packet = message
        except websockets.exceptions.ConnectionClosedError:
            print("Client disconnected.")
        finally:
            async with self.client_lock:
                if self.connected_client == websocket:
                    self.connected_client = None

    async def start_server(self):
        server = await websockets.serve(self.handler, self.host, self.port)
        print(f"Server started at ws://{self.host}:{self.port}")
        await server.wait_closed()

    def start_background_tasks(self):
        # Start background thread to handle sending packets
        def run_send_loop():
            loop = asyncio.new_event_loop()
            self.sender_event_loop = loop
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._send_loop())

        thread = threading.Thread(target=run_send_loop)
        thread.start()

    async def _send_loop(self):
        self.send_packet_queue = asyncio.Queue()
        while True:
            packet = await self.send_packet_queue.get()
            #print(f"Sending packet {packet}")
            async with self.client_lock:
                if self.connected_client is not None:
                    try:
                        await self.connected_client.send(packet)
                        #print(f"Sent packet: {packet}")
                    except websockets.exceptions.ConnectionClosedError:
                        #print("Error: Client disconnected during send.")
                        self.connected_client = None
            self.send_packet_queue.task_done()
        print("Exited send_packet_queue")

    def send_packet(self, packet: str):
        """
        Adds a packet to the send queue, to be sent to the connected client.
        Can be called from another thread.
        """
        asyncio.run_coroutine_threadsafe(self.send_packet_queue.put(packet), self.sender_event_loop)
        #print(f"Queue size: {self.send_packet_queue.qsize()}")  # Log queue size
        #print(f"Queued packet for sending: {packet}")

    def get_last_received_packet(self):
        """
        Returns the last received packet. Can be called from another thread.
        """
        return self.last_received_packet