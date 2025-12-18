import asyncio
import json
import os
import logging
from bat_algorithm import run_bat_simple
from genetic_algorithm import run_genetic_simple

logger = logging.getLogger(__name__)

# Mapa dostępnych algorytmów
ALGO_MAP = {
    "Bat alhorithm": run_bat_simple,
    "Genetic algorytm": run_genetic_simple
}

class SimulationManager:
    def __init__(self):
        self.websocket = None
        self.isPaused = False
        self.isRunning = False
        self._current_task = None
        self.filename = "checkpoint.json"

    async def connect(self, ws):
        self.websocket = ws
        await ws.accept()

    def disconnect(self):
        self.websocket = None
        self.isRunning = False

    async def handle_command(self, data):
        command = data.get("type")
        
        if command == "start":
            if self._current_task:
                self._current_task.cancel()
            self._current_task = asyncio.create_task(self.start(data))
            
        elif command == "pause":
            await self.pause()
            
        elif command == "stop":
            self.isRunning = False
            self.isPaused = False
            if self.websocket:
                await self.websocket.send_text("done")

    def save_checkpoint(self, state_data):
        try:
            with open(self.filename, "w") as f:
                json.dump(state_data, f, indent=4)
        except Exception as e:
            print(f"Błąd zapisu: {e}")

    def load_checkpoint(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Błąd odczytu: {e}")
        return None

    async def start(self, data):
        self.isRunning = True
        self.isPaused = False
        
        input_data = data.get("data", {})
        # Pobieramy listę algorytmów zaznaczonych na froncie
        selected_algos = input_data.get("algorithms", [])
        should_resume = str(input_data.get("resume", False)).lower() == "true"

        try:
            for algo_config in selected_algos:
                if not self.isRunning: break
                
                algo_name = algo_config.get("name")
                algo_func = ALGO_MAP.get(algo_name)
                
                if algo_func:
                    print(f"Uruchamiam: {algo_name}")
                    
                    resume_data = None
                    if should_resume:
                        resume_data = self.load_checkpoint()
                        # Sprawdzamy czy checkpoint dotyczy tego samego algorytmu
                        if resume_data and resume_data.get("algo_name") != algo_name:
                            resume_data = None

                    # Uruchomienie algorytmu
                    await algo_func(self, algo_config, resume_data)
                
            if self.websocket and self.isRunning:
                await self.websocket.send_text("done")
                
        except asyncio.CancelledError:
            print("Zadania przerwane.")
        except Exception as e:
            if self.websocket:
                await self.websocket.send_json({"type": "error", "message": str(e)})

    async def pause(self):
        self.isPaused = not self.isPaused
        status = "paused" if self.isPaused else "resumed"
        if self.websocket:
            await self.websocket.send_json({"type": "status", "response": status})