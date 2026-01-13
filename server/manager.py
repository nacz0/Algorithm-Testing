import asyncio
import json
import os
import requests
import math
from algorithms.MetaheuristicTuner import MetaheuristicTuner

class SimulationManager:
    def __init__(self):
        
        self.clients: list = []  # Lista aktywnych połączeń WebSocket
        self.isPaused = False
        self.isRunning = False
        self._current_task = None
        self.metaheuristic_tuner = None
        self.filename = "checkpoint.json"

        self._load_params()

        async def _progress_send_fn(progress, type):
                await self.broadcast(type="progress", message = ({"type": type, "progress": progress}))
            

        async def _stop_check_fn():
                if not self.isRunning:
                    print("Stop detected")
                return not self.isRunning
            
        async def _pause_check_fn():
                if self.isPaused:
                    print("Pause detected")
                return self.isPaused
            
        self.metaheuristic_tuner = MetaheuristicTuner( 
                                                          progress_send_fn=_progress_send_fn,
                                                          stop_check_fn=_stop_check_fn,
                                                          pause_check_fn=_pause_check_fn)


    async def connect(self, ws):
        """Dodaje nowego klienta do listy i akceptuje połączenie."""
        await ws.accept()
        self.clients.append(ws)
        print(f"Klient podłączony. Aktywnych klientów: {len(self.clients)}")

    def disconnect(self, ws):
        """Usuwa klienta z listy."""
        if ws in self.clients:
            self.clients.remove(ws)
        print(f"Klient odłączony. Aktywnych klientów: {len(self.clients)}")
        # Zatrzymaj symulację tylko jeśli nie ma żadnych klientów
        if len(self.clients) == 0:
            self.isRunning = False

    async def send(self, ws, type, message):
        """Wysyła wiadomość do konkretnego klienta."""
        try:
            await ws.send_json({"type": type, "message": message})
        except Exception as e:
            print(f"Błąd wysyłania do klienta: {e}")
            self.disconnect(ws)

    async def broadcast(self, type, message):
        """Wysyła wiadomość do wszystkich podłączonych klientów."""
        disconnected = []
        for client in self.clients:
            try:
                await client.send_json({"type": type, "message": message})
            except Exception as e:
                print(f"Błąd wysyłania do klienta: {e}")
                disconnected.append(client)
        
        # Usuń odłączonych klientów
        for client in disconnected:
            self.disconnect(client)



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

    async def _send_params(self, ws):
        """Wysyła parametry do konkretnego klienta."""
        await self.send(
            ws,
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


    async def handle_command(self, ws, data):
        """Obsługuje polecenie od konkretnego klienta."""
        command = data.get("type").strip()
        print(f"Komenda od klienta: {command}")
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
            if self.isPaused:
                self.metaheuristic_tuner.delete_checkpoints()
                await self.broadcast(type="stop", message="Stoped successfully")
            self.isRunning = False
            self.isPaused = False
            
        elif command == "get_params":
            await self._send_params(ws)


    async def start(self):
        print("Starting simulation")
        this_task = asyncio.current_task()

        if self._current_task and self._current_task != this_task:
            self._current_task.cancel()
            try:
                await self._current_task
            except asyncio.CancelledError:
                pass

        await self.broadcast(type="start", message="started successfully")
        if type(self.selected_function["code"]) == str:
            func = self.string_to_function(self.selected_function["code"])
            if func is None:
                await self.broadcast(type="error", message="Function code has syntax errors.")
                return
            self.selected_function["code"] = func

   
        selected = list(filter(lambda alg: alg["isUsed"], self.algorithmsData))

        dim = next((p["value"] for p in self.shared_params_data if p["name"] == "Dimentions"), None)
        iterations = next((p["value"] for p in self.shared_params_data if p["name"] == "Iterations"), None)
      
        results, figures = await self.metaheuristic_tuner.tune_algorithms(
            algorithmsData = self.algorithmsData,
            selected=[alg["name"] for alg in selected],
            selected_funcs=[self.selected_function],
            dim=dim,
            iterations=iterations, 
            R=20, 
        )

        if self.isPaused:
            await self.broadcast(type="pause", message="Paused successfully")
            return

        if not self.isRunning:
            await self.broadcast(type="stop", message="Stoped successfully")
            return

        await self.broadcast(type="finished", message={"result": results, "figures": figures})
