# main.py

import asyncio
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging
import json
import os

# Importy z Twoich modułów
from state_manager import state_manager
from utils import parse_function_code
from algorithms import ALGORITHM_MAP

# Import nowego runnera
from experiment_runner import run_experiment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Heuristic Algorithms Tester")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket Manager ---
# Klasa zarządzająca aktywnymi połączeniami z frontendem
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Wysyłamy wiadomość do wszystkich podłączonych klientów (np. przeglądarek)
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Jeśli połączenie zerwane, można je usunąć, tu dla uproszczenia pass
                pass

manager = ConnectionManager()

# --- Modele ---
class FunctionPayload(BaseModel):
    name: str
    code: str
    isCustom: bool

class AlgoArg(BaseModel):
    name: str
    min: float
    max: float
    step: float

class AlgorithmConfig(BaseModel):
    name: str
    args: List[AlgoArg]
    isUsed: bool

class SimulationRequest(BaseModel):
    selected_function: FunctionPayload
    algorithms: List[AlgorithmConfig]
    resume: bool = False
    mode: str = "single"  # 'single' lub 'experiment'

# --- Logika Wyboru ---

def process_request(data: SimulationRequest):
    """Router logiczny: wybiera zwykłą symulację lub eksperyment."""
    
    # 1. Parsowanie funkcji
    try:
        objective_func = parse_function_code(data.selected_function.code, data.selected_function.name)
    except Exception as e:
        logger.error(f"Function parse error: {e}")
        return

    # 2. Wybór trybu
    if data.mode == "experiment":
        logger.info("Uruchamianie trybu eksperymentalnego (Grid Search)...")
        # Uruchamiamy nowy runner eksperymentów
        run_experiment(objective_func, data.algorithms, repeats=10)
        
    else:
        # Klasyczna symulacja (pojedynczy przebieg)
        # (Tu wklej starą logikę pętli z poprzednich odpowiedzi)
        process_single_simulation(data, objective_func)

def process_single_simulation(data, objective_func):
    # Logika z poprzednich wersji (Resume, Single Run)
    if not data.resume:
        state_manager.start_new_session()
        existing_data = {}
    else:
        # ... (kod ładowania JSON)
        existing_data = {} # skrót

    for algo_config in data.algorithms:
        if not algo_config.isUsed: continue
        if state_manager.should_stop(): break

        runner = ALGORITHM_MAP.get(algo_config.name)
        if runner:
            try:
                algo_params = {arg.name: {"min": arg.min, "max": arg.max, "step": arg.step} for arg in algo_config.args}
                resume_payload = existing_data.get(algo_config.name) if data.resume else None
                runner(objective_func, algo_params, state_manager, resume_data=resume_payload)
            except Exception as e:
                logger.error(f"Error: {e}")

    state_manager.save_checkpoint("simulation_final.json")


# --- Endpointy ---

@app.post("/api/start")
async def start_simulation(request: SimulationRequest, background_tasks: BackgroundTasks):
    # Uruchom odpowiednią logikę w tle
    background_tasks.add_task(process_request, request)
    return {"message": f"Rozpoczęto w trybie: {request.mode}"}

@app.post("/api/stop")
async def stop_simulation():
    state_manager.request_stop()
    # Małe opóźnienie dla wątków
    await asyncio.sleep(0.5)
    state_manager.save_checkpoint("simulation_stopped.json")
    return {"message": "Zatrzymano", "data": state_manager.get_results()}

@app.get("/api/status")
async def get_status():
    return state_manager.get_results()

# --- Nowy Endpoint WebSocket ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Oczekujemy na wiadomości od klienta (opcjonalne, np. ping)
            # Tutaj po prostu utrzymujemy połączenie
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)