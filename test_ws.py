import asyncio
import websockets


async def send_receive():
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        # Envía un mensaje al WebSocket
        await websocket.send("Hola, soy un mensaje de prueba desde Python")

        # Recibe la respuesta del WebSocket
        response = await websocket.recv()
        print(f"Respuesta del WebSocket: {response}")


if __name__ == "__main__":
    asyncio.run(send_receive())
