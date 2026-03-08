import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="MONO Phase 29 Playground")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:5174", 
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_socket = None
from phase29_instance_manager import InstanceManager
from phase29_predator_engine import RedQueenPredator

class ChatMessage(BaseModel):
    message: str

@app.on_event("startup")
async def startup_event():
    global instance_manager
    # Initialize the engine and give it the broadcast callback
    instance_manager = InstanceManager(broadcast_telemetry)
    # Start the continuous ecological loop in the background
    asyncio.create_task(instance_manager.run_ecosystem())
    
    # Initialize and release the Predator
    predator = RedQueenPredator(instance_manager)
    asyncio.create_task(predator.run_hunt_loop())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global active_socket
    await websocket.accept()
    active_socket = websocket
    print("UI Connected to Telemetry Stream")
    
    try:
        while True:
            # Keep socket alive, wait for incoming control messages if needed
            data = await websocket.receive_text()
            print(f"WS Received: {data}")
    except WebSocketDisconnect:
        print("UI Disconnected")
        if active_socket == websocket:
            active_socket = None

@app.post("/api/chat")
async def handle_chat(chat: ChatMessage = Body(...)):
    if instance_manager:
        # Pass the message to the active MonoAgent
        response = await instance_manager.process_query(chat.message)
        return {"status": "ok", "response": response}
    else:
        return {"status": "error", "message": "Ecosystem not initialized"}

# Background telemetry loop broadcaster
async def broadcast_telemetry(data: dict):
    if active_socket:
        try:
            await active_socket.send_text(json.dumps({
                "type": "telemetry",
                "data": data
            }))
        except Exception as e:
            print(f"Telemetry broadcast err: {e}")

if __name__ == "__main__":
    import uvicorn
    # Make sure we run `python phase29_server.py`
    uvicorn.run("phase29_server:app", host="127.0.0.1", port=8000, reload=True)
