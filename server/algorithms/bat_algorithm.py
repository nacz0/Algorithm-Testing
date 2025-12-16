# algorithms/bat_algorithm.py

import numpy as np
import logging
from typing import Dict, Any, Callable, Optional
from state_manager import SimulationStateManager

logger = logging.getLogger(__name__)

# --- Funkcje pomocnicze ---
def initialization_bats(bounds, n_bats, dims):
    x = np.zeros((n_bats, dims))
    for i in range(n_bats):
        for j in range(dims):
            x[i, j] = bounds[0] + np.random.rand() * (bounds[1] - bounds[0])
    return x

def update_position_frequency_velocity(xi, vi, best, f_bounds, A_avg, ri):
    f_min, f_max = f_bounds
    beta = np.random.rand()
    f = f_min + (f_max - f_min) * beta
    vi = vi + (best - xi) * f
    xi = xi + vi
    if np.random.rand() < ri:
        epsilon = np.random.uniform(-1, 1)
        xi = best + epsilon * A_avg
    return xi, vi, f

def adjust_loudness(A, alpha):
    return A * alpha

def adjust_pulse_rate(r0, gamma, t):
    return r0 * (1 - np.exp(-gamma * t))

# --- Helper do zapisywania stanu (POPRAWIONY) ---
def save_current_state(manager, t, max_iter, best_f, best, history, x, v, f, A, r, r0, status):
    """
    Zapisuje stan. Dodano parametr 'max_iter', aby frontend wiedział ile było planowanych iteracji.
    """
    manager.update_progress("Bat alhorithm", {
        "status": status,
        "current_iteration": t,
        "total_iterations": max_iter,  # <--- TU BYŁ BŁĄD (BRAK TEGO POLA)
        "best_score": float(best_f),
        "best_position": best.tolist(),
        "history": [float(h) for h in history],
        "internal_state": {
            "x": x.tolist(),
            "v": v.tolist(),
            "f": f.tolist(),
            "A": A.tolist(),
            "r": r.tolist(),
            "r0": r0.tolist()
        }
    })

# --- Główna funkcja ---

def run_bat_algorithm(
    objective_function: Callable, 
    params: Dict[str, Any], 
    manager: SimulationStateManager,
    resume_data: Optional[Dict[str, Any]] = None
):
    logger.info("Uruchamianie Bat Algorithm...")

    try:
        n_bats = int(params.get("Agents", {}).get("min", 20))
        max_iter = int(params.get("Iterations", {}).get("min", 50)) # To jest total_iterations
        alpha = float(params.get("Alpha", {}).get("min", 0.9))
        gamma = float(params.get("Gamma", {}).get("min", 0.9))
        f_max_param = float(params.get("Frequancy", {}).get("min", 2.0))
        f_bounds = (0, f_max_param)
        bounds = (-5, 5)
        dims = 2
    except Exception as e:
        manager.update_progress("Bat alhorithm", {"status": "error", "message": str(e)})
        return

    # Inicjalizacja lub Wznowienie
    start_iter = 0
    history = []
    
    if resume_data and resume_data.get("internal_state"):
        logger.info(">>> WZNAWIAMY OBLICZENIA <<<")
        state = resume_data["internal_state"]
        x = np.array(state["x"])
        v = np.array(state["v"])
        f = np.array(state["f"])
        A = np.array(state["A"])
        r = np.array(state["r"])
        r0 = np.array(state["r0"])
        history = resume_data.get("history", [])
        start_iter = resume_data.get("current_iteration", 0)
        
        fitness = np.array([objective_function(xi) for xi in x])
        best_idx = np.argmin(fitness)
        best = x[best_idx].copy()
        best_f = fitness[best_idx]
    else:
        np.random.seed(None)
        v = np.zeros((n_bats, dims))
        x = initialization_bats(bounds, n_bats, dims)
        f = np.zeros(n_bats)
        A = np.full(n_bats, 1.5)
        r0 = np.full(n_bats, 0.5)
        r = r0.copy()
        fitness = np.array([objective_function(xi) for xi in x])
        best_idx = np.argmin(fitness)
        best = x[best_idx].copy()
        best_f = fitness[best_idx]

    # Główna pętla
    for t in range(start_iter, max_iter):
        
        # STOP
        if manager.should_stop():
            # Przekazujemy max_iter do funkcji save
            save_current_state(manager, t, max_iter, best_f, best, history, x, v, f, A, r, r0, status="stopped")
            return {"status": "stopped"}
        
        # Algorytm
        A_avg = np.average(A)
        for i in range(n_bats):
            x[i], v[i], f[i] = update_position_frequency_velocity(x[i], v[i], best, f_bounds, A_avg, r[i])
            x[i] = np.clip(x[i], bounds[0], bounds[1])
            f_new = objective_function(x[i])

            if np.random.rand() < A[i] and f_new < fitness[i]:
                fitness[i] = f_new
                A[i] = adjust_loudness(A[i], alpha)
                r[i] = adjust_pulse_rate(r0[i], gamma, t + 1)

            if f_new < best_f:
                best_f = f_new
                best = x[i].copy()

        history.append(best_f)

        # Auto-zapis co 10 iteracji
        if t % 10 == 0:
            save_current_state(manager, t, max_iter, best_f, best, history, x, v, f, A, r, r0, status="running")
            manager.save_checkpoint("simulation_checkpoint.json")

    # Koniec
    save_current_state(manager, max_iter, max_iter, best_f, best, history, x, v, f, A, r, r0, status="finished")
    return {"status": "finished", "best_score": float(best_f)}