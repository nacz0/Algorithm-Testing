# state_manager.py

import threading
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SimulationStateManager:
    def __init__(self):
        self._stop_event = threading.Event()
        self._current_results = {}
        self._lock = threading.Lock()
        self._start_time = None

    def start_new_session(self):
        self._stop_event.clear()
        with self._lock:
            self._current_results = {}
            self._start_time = datetime.now().isoformat()

    def request_stop(self):
        logger.info("Zażądano zatrzymania symulacji.")
        self._stop_event.set()

    def should_stop(self) -> bool:
        return self._stop_event.is_set()

    def update_progress(self, algo_name: str, data: dict):
        with self._lock:
            self._current_results[algo_name] = data

    def save_checkpoint(self, filename="simulation_checkpoint.json"):
        with self._lock:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "start_time": self._start_time,
                "status": "stopped" if self._stop_event.is_set() else "running",
                "results": self._current_results
            }
            
        try:
            with open(filename, "w", encoding='utf-8') as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)
            logger.info(f"Stan zapisano do pliku: {filename}")
            return True
        except Exception as e:
            logger.error(f"Błąd zapisu pliku: {e}")
            return False

    def get_results(self):
        with self._lock:
            return self._current_results

# Globalna instancja, którą będziemy importować w main.py
state_manager = SimulationStateManager()