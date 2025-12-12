from state_manager import SimulationStateManager
from typing import Dict, Any, Callable

def run_genetic_algorithm(objective_function: Callable, params: Dict[str, Any], manager: SimulationStateManager, resume_data=None):
    # Placeholder: tutaj wstawisz logikę GA
    manager.update_progress("Genetic algorytm", {"status": "running", "message": "Started..."})
    if manager.should_stop():
        manager.update_progress("Genetic algorytm", {"status": "stopped"})
        return {"status": "stopped"}
        
    # Symulacja pracy
    # ...
    
    manager.update_progress("Genetic algorytm", {"status": "finished", "best_score": 0.0})
    return {"status": "finished", "best_score": 0.0}