import socketio
import asyncio

sio_client = socketio.AsyncClient()


@sio_client.event
async def connect():
    print("Hello Camilo")


@sio_client.event
async def disconnect():
    print("Bye Camilo")


async def main():
    await sio_client.connect(url="http://localhost:8000", socketio_path="sockets")
    await sio_client.disconnect()


asyncio.run(main())
