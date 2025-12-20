import asyncio
import json
import os


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

    async def send(self, type, message):
        if self.websocket:
            await self.websocket.send_json({"type":type, "message": message})


    async def handle_command(self, data):
        command = data.get("type").strip()
        print(command)
        if command == "start":
            self._current_task = asyncio.create_task(self.start(data))
        elif command == "pause":
            self.isPaused = "paused"
        elif command == "stop":
            self.isRunning = False
            self.isPaused = False


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

        self.isRunning = True
        self.isPaused = False
        
        algorithms = data.get("algorithms", [])
        functionData = data["selected_function"]
        i = 0
        for algo_config in algorithms:
            # TODO: pause
            # TODO: Stop
            # TODO: Sending report
            # TODO: tesing algorithms for every parameter
            await self.send(type="progress", message = round(i/len(algorithms)*100))
            await asyncio.sleep(10)
            
            if self.isPaused:
              
                await self.send(type="pause", message = "Paused successfully")
                return

            if not self.isRunning:
                await self.send(type="stop", message = "Stoped successfully")
                return
            i+= 1

        await self.websocket.send_json({"type":"finished", "message":"Finished"})
