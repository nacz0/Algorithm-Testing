from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from manager import SimulationManager

app = FastAPI()
manager = SimulationManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.handle_command(data)
    except WebSocketDisconnect:
        manager.disconnect()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)