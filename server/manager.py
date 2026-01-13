import asyncio
import json
import os
import requests
import math
from algorithms.MetaheuristicTuner import MetaheuristicTuner

class SimulationManager:
    def __init__(self):
        
        self.active_connections = []
        self.isPaused = False
        self.isRunning = False
        self._current_task = None
        self.metaheuristic_tuner = None
        self.filename = "checkpoint.json"

        self._load_params()

    async def connect(self, ws):
        await ws.accept()
        self.active_connections.append(ws)
        # Send current state to the newly connected client
        await self._send_params_to(ws)

    def disconnect(self, ws):
        if ws in self.active_connections:
            self.active_connections.remove(ws)

    async def send(self, type, message):
        if not self.active_connections:
            return
            
        payload = {"type": type, "message": message}
        
        # Broadcast to all active connections
        disconnected = []
        for ws in self.active_connections:
            try:
                await ws.send_json(payload)
            except Exception as e:
                print(f"Error sending to websocket: {e}")
                disconnected.append(ws)
        
        # Clean up any connections that failed
        for ws in disconnected:
            self.disconnect(ws)

    async def _send_params_to(self, ws):
        try:
            await ws.send_json({
                "type": "get_params",
                "message": {
                    "algorithms": self.algorithmsData,
                    "shared_params": self.shared_params_data,
                    "functions_data": self.functionsData,
                    "isStarted": self.isRunning,
                    "isPaused": self.isPaused,
                }
            })
        except Exception as e:
            print(f"Error sending initial params: {e}")
            self.disconnect(ws)



    def string_to_function(self, code_string):
        """
        Zamienia string na obiekt funkcji i sprawdza błędy składni.
        """

        globals_dict = {"math": math}
        locals_dict = {}

        try:
            exec(code_string, globals_dict, locals_dict)
            func = next((v for v in locals_dict.values() if callable(v)), None)
            if func is None:
                raise ValueError("W podanym kodzie nie znaleziono definicji funkcji (brak 'def').")
                
            return func

        except SyntaxError as e:
            print(f"BŁĄD SKŁADNI (SyntaxError): {e}")
            return None
        except Exception as e:
            print(f"INNY BŁĄD: {e}")
            return None

    def _load_params(self):
        print("Getting parameters")
        with open("./data/algorithms.json") as f:
            data = json.load(f)
            algorithmsData = data["algorithms"].copy()
            for i in range(len(algorithmsData)):
                algorithmsData[i]["isUsed"] = True
                for j in range(len(algorithmsData[i]["params"])):
                    if algorithmsData[i]["params"][j]["range"] == "value":
                        algorithmsData[i]["params"][j]["value"] = 5
                    if algorithmsData[i]["params"][j]["range"] == "min-max":
                        algorithmsData[i]["params"][j]["max"] = 1
                        algorithmsData[i]["params"][j]["min"] = 0

            shared_params_data = data["shared_params"].copy()
            for i in range(len(shared_params_data)):
                if shared_params_data[i]["range"] == "value":
                    shared_params_data[i]["value"] = 5
                if shared_params_data[i]["range"] == "min-max":
                    shared_params_data[i]["max"] = 1
                    shared_params_data[i]["min"] = 0
        
        with open("./data/functions.json") as f:
            functionsData = json.load(f)

        self.algorithmsData = algorithmsData
        self.shared_params_data = shared_params_data
        self.functionsData = functionsData
        self.selected_function = functionsData[0]

    async def _send_params(self):
        await self.send(
            type="get_params",
            message={
                "algorithms": self.algorithmsData,
                "shared_params": self.shared_params_data,
                "functions_data": self.functionsData,
                "isStarted": self.isRunning,
                "isPaused": self.isPaused,
            },
        )

    def _update_params(self, data):
        self.algorithmsData = data.get("algorithmsData", self.algorithmsData)
        self.shared_params_data = data.get("shared_params", self.shared_params_data)
        self.selected_function = data.get("selected_function", self.selected_function)  


    async def handle_command(self, data):
        command = data.get("type").strip()
        print(command)
        if command == "start":
            self._update_params(data)
            self.isRunning = True
            self.isPaused = False
            self._current_task = asyncio.create_task(self.start())
        elif command == "pause":
            print("Pausing simulation")
            self.isPaused = True
        elif command == "stop":
            print("Stopping simulation")
            self.isRunning = False
            self.isPaused = False
        elif command == "get_params":
            await self._send_params()


    async def start(self):
        print("Starting simulation")
        # 1. Pobierz referencję do aktualnie wykonywanego zadania
        this_task = asyncio.current_task()

        # 2. Anuluj poprzednie zadanie tylko, jeśli jest inne niż obecne
        if self._current_task and self._current_task != this_task:
            self._current_task.cancel()
            try:
                await self._current_task # opcjonalnie czekaj na zamknięcie
            except asyncio.CancelledError:
                pass

        await self.send("start","started successfully")
        if type(self.selected_function["code"]) == str:
            func = self.string_to_function(self.selected_function["code"])
            if func is None:
                await self.send(type="error", message = "Function code has syntax errors.")
                return
            self.selected_function["code"] = func

   
        
        # Always recreate tuner with current parameters to ensure fresh configuration
        async def _progress_send_fn(progress, type):
            await self.send(type="progress", message = ({"type": type, "progress": progress}))
        

        async def _stop_check_fn():
            if not self.isRunning:
                print("Stop detected")
            return not self.isRunning
        
        async def _pause_check_fn():
            if self.isPaused:
                print("Pause detected")
            return self.isPaused
        
        self.metaheuristic_tuner = MetaheuristicTuner(self.algorithmsData, 
                                                      progress_send_fn=_progress_send_fn,
                                                      stop_check_fn=_stop_check_fn,
                                                      pause_check_fn=_pause_check_fn)

        selected = list(filter(lambda alg: alg["isUsed"], self.algorithmsData))

        # Validate: at least one algorithm must be selected
        if not selected:
            await self.send(type="error", message="No algorithms selected. Please enable at least one algorithm.")
            self.isRunning = False
            return

        # Validate and fix parameter bounds (swap if min > max)
        for alg in self.algorithmsData:
            for param in alg.get("params", []):
                if "min" in param and "max" in param:
                    if param["min"] > param["max"]:
                        param["min"], param["max"] = param["max"], param["min"]
                        print(f"Warning: Swapped min/max for {alg['name']}.{param['name']}")
                    # Ensure integer params have valid range (at least 1 for counts)
                    if param.get("type") == "int" and param["min"] < 1:
                        if param["name"] in ["n_bats", "n_bees", "pop_size", "tournament_size"]:
                            param["min"] = 1
                            print(f"Warning: Set min=1 for {alg['name']}.{param['name']} (count parameter)")

        dim = next((p["value"] for p in self.shared_params_data if p["name"] == "Dimentions"), None)
        iterations = next((p["value"] for p in self.shared_params_data if p["name"] == "Iterations"), None)

        # Validate dimensions and iterations
        if dim is None or dim < 1:
            await self.send(type="error", message="Invalid dimensions value. Must be at least 1.")
            self.isRunning = False
            return
        if iterations is None or iterations < 1:
            await self.send(type="error", message="Invalid iterations value. Must be at least 1.")
            self.isRunning = False
            return
      
        # TODO: What is the perpose of iterations here?
        results, figures = await self.metaheuristic_tuner.tune_algorithms(
            selected=[alg["name"] for alg in selected],
            selected_funcs=[self.selected_function],
            dim=dim,
            iterations=iterations, 
            R=20, 
        )

        if self.isPaused:
            await self.send(type="pause", message = "Paused successfully")
            return

        if not self.isRunning:
            await self.send(type="stop", message = "Stoped successfully")
            return

        await self.send(type="finished", message={"result": results, "figures": figures})
