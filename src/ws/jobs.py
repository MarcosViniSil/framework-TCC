from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect

app = FastAPI()

clients: list[WebSocket] = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    try:
        while True:
            await websocket.receive()
    except WebSocketDisconnect:
        clients.remove(websocket)


async def send_message(message: dict):
    for client in clients:
        await client.send_json(message)
