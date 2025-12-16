# algorithms/bat_algorithm.py

import numpy as np
import logging
from typing import Dict, Any, Callable, Optional, Tuple
from state_manager import SimulationStateManager

logger = logging.getLogger(__name__)

# --- Czysta logika matematyczna (Worker) ---
# Ta funkcja nie wie nic o JSON-ach, przyjmuje czyste liczby.
def bat_worker(
    objective_function: Callable,
    n_bats: int,
    max_iter: int,
    alpha: float,
    gamma: float,
    f_bounds: Tuple[float, float],
    bounds: Tuple[float, float],
    dims: int,
    manager: Optional[SimulationStateManager] = None,
    algo_name: str = "Bat"
) -> Dict[str, Any]:
    
    # Inicjalizacja
    x = np.zeros((n_bats, dims))
    for i in range(n_bats):
        for j in range(dims):
            x[i, j] = bounds[0] + np.random.rand() * (bounds[1] - bounds[0])
            
    v = np.zeros((n_bats, dims))
    f = np.zeros(n_bats)
    A = np.full(n_bats, 1.5)
    r0 = np.full(n_bats, 0.5)
    r = r0.copy()

    fitness = np.array([objective_function(xi) for xi in x])
    best_idx = np.argmin(fitness)
    best = x[best_idx].copy()
    best_f = fitness[best_idx]
    
    history = []

    # Pętla algorytmu
    for t in range(max_iter):
        # Sprawdzenie STOPu tylko jeśli podano managera (w eksperymentach sprawdzamy poziom wyżej)
        if manager and manager.should_stop():
            return {"status": "stopped", "best_score": float(best_f)}

        A_avg = np.average(A)
        f_min, f_max = f_bounds

        for i in range(n_bats):
            beta = np.random.rand()
            f[i] = f_min + (f_max - f_min) * beta
            v[i] = v[i] + (best - x[i]) * f[i]
            x[i] = x[i] + v[i]
            
            if np.random.rand() < r[i]:
                epsilon = np.random.uniform(-1, 1)
                x[i] = best + epsilon * A_avg

            x[i] = np.clip(x[i], bounds[0], bounds[1])
            f_new = objective_function(x[i])

            if np.random.rand() < A[i] and f_new < fitness[i]:
                fitness[i] = f_new
                A[i] = A[i] * alpha
                r[i] = r0[i] * (1 - np.exp(-gamma * (t + 1)))

            if f_new < best_f:
                best_f = f_new
                best = x[i].copy()
        
        history.append(best_f)

    return {
        "status": "finished",
        "best_score": float(best_f),
        "history": history
    }

# --- Wrapper dla pojedynczego uruchomienia (zgodność ze starym API) ---
def run_bat_algorithm(
    objective_function: Callable, 
    params: Dict[str, Any], 
    manager: SimulationStateManager,
    resume_data: Optional[Dict[str, Any]] = None
):
    # Parsowanie parametrów z JSON (bierzemy 'min' jako wartość)
    try:
        n_bats = int(params.get("Agents", {}).get("min", 20))
        max_iter = int(params.get("Iterations", {}).get("min", 50))
        alpha = float(params.get("Alpha", {}).get("min", 0.9))
        gamma = float(params.get("Gamma", {}).get("min", 0.9))
        f_max = float(params.get("Frequancy", {}).get("min", 2.0))
    except Exception as e:
        manager.update_progress("Bat alhorithm", {"status": "error", "message": str(e)})
        return

    # Uruchomienie workera
    # UWAGA: W trybie pojedynczym nie implementujemy tu pełnego resume dla czytelności przykładu,
    # ale w produkcji bat_worker też powinien przyjmować stan początkowy.
    result = bat_worker(
        objective_function, n_bats, max_iter, alpha, gamma, 
        (0, f_max), (-5, 5), 2, manager, "Bat alhorithm"
    )

    # Zapis wyniku
    if result["status"] == "finished":
        manager.update_progress("Bat alhorithm", {
            "status": "finished",
            "current_iteration": max_iter,
            "total_iterations": max_iter,
            "best_score": result["best_score"],
            "history": result["history"]
        })