# main.py

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging
import time
import os
import json

# Importujemy z nowych modułów
from state_manager import state_manager
from utils import parse_function_code
from algorithms import ALGORITHM_MAP

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Heuristic Algorithms Tester")

# --- Modele danych (pozostają w main, bo są specyficzne dla API) ---

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
    resume: bool = False  # <--- Nowe pole: czy wznawiać?

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Logika Procesowania ---

def process_simulation(data: SimulationRequest):
    # Jeśli NIE wznawiamy, resetujemy menedżera
    if not data.resume:
        state_manager.start_new_session()
        existing_data = {}
    else:
        # Jeśli WZNAWIAMY, próbujemy wczytać plik
        try:
            if os.path.exists("simulation_checkpoint.json"):
                with open("simulation_checkpoint.json", "r") as f:
                    checkpoint = json.load(f)
                    # Wyciągamy wyniki per algorytm
                    existing_data = checkpoint.get("results", {})
                    logger.info("Załadowano dane do wznowienia.")
            else:
                logger.warning("Brak pliku checkpointu, start od zera.")
                existing_data = {}
        except Exception as e:
            logger.error(f"Błąd odczytu checkpointu: {e}")
            existing_data = {}

    try:
        objective_func = parse_function_code(data.selected_function.code, data.selected_function.name)
    except Exception:
        return

    for algo_config in data.algorithms:
        if not algo_config.isUsed:
            continue
            
        if state_manager.should_stop():
            break

        runner = ALGORITHM_MAP.get(algo_config.name)
        if runner:
            try:
                algo_params = {arg.name: {"min": arg.min, "max": arg.max, "step": arg.step} for arg in algo_config.args}
                
                # Pobierz dane dla KONKRETNEGO algorytmu (jeśli istnieją)
                resume_payload = existing_data.get(algo_config.name) if data.resume else None
                
                # Przekazujemy resume_payload do funkcji algorytmu
                runner(objective_func, algo_params, state_manager, resume_data=resume_payload)
                
            except Exception as e:
                logger.error(f"Krytyczny błąd w algorytmie {algo_config.name}: {e}")
                state_manager.update_progress(algo_config.name, {"status": "error", "message": str(e)})
    
    state_manager.save_checkpoint("simulation_final.json")

# --- Endpointy ---

@app.post("/api/start")
async def start_simulation(request: SimulationRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_simulation, request)
    return {"message": "Symulacja rozpoczęta"}

@app.post("/api/stop")
async def stop_simulation():
    state_manager.request_stop()
    time.sleep(0.2) 
    state_manager.save_checkpoint("simulation_stopped.json")
    return {"message": "Zatrzymano", "data": state_manager.get_results()}

@app.get("/api/status")
async def get_status():
    """Endpoint do pobierania aktualnego postępu przez frontend."""
    return state_manager.get_results()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)