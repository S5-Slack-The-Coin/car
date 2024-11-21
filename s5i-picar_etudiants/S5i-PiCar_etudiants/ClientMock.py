import asyncio
import websockets

async def websocket_client(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            await websocket.send(b'\x01\x02')
            # Receive data and print it
            try:
                data = await websocket.recv()
                print("Client received this data")
                print(["0x%02x" % b for b in data])
            except websockets.ConnectionClosed:
                print("Connection closed")
                break
            # Wait 1 second before the next send
            await asyncio.sleep(1)

# Define the WebSocket server URI
uri = "ws://localhost:8765"  # Replace with your server's URI

# Run the client
asyncio.run(websocket_client(uri))