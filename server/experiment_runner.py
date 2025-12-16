# experiment_runner.py

import itertools
import numpy as np
import logging
import time
from typing import List, Dict, Any, Callable
from state_manager import state_manager
from algorithms.bat_algorithm import bat_worker

logger = logging.getLogger(__name__)

def generate_param_grid(algo_config: Any) -> List[Dict[str, float]]:
    """Generuje listę wszystkich kombinacji parametrów (Grid Search)."""
    ranges = {}
    constant_params = {}

    for arg in algo_config.args:
        # Jeśli min != max i step > 0, to jest zakres do iteracji
        if arg.min != arg.max and arg.step > 0:
            # np. arange(0.1, 0.4, 0.1) -> [0.1, 0.2, 0.3]
            # Dodajemy mały epsilon do max, żeby włączyć ostatnią wartość
            values = np.arange(arg.min, arg.max + 0.00001, arg.step)
            ranges[arg.name] = [round(v, 4) for v in values]
        else:
            # Wartość stała
            constant_params[arg.name] = arg.min

    if not ranges:
        return [constant_params]

    # Iloczyn kartezjański (wszystkie kombinacje)
    keys = ranges.keys()
    combinations = []
    for values in itertools.product(*ranges.values()):
        params = constant_params.copy()
        params.update(zip(keys, values))
        combinations.append(params)
    
    return combinations

def run_experiment(
    objective_func: Callable,
    algo_configs: List[Any],
    repeats: int = 10  # Domyślnie 10 powtórzeń dla badania powtarzalności
):
    """
    Główna pętla eksperymentu:
    1. Grid Search parametrów
    2. Wielokrotne uruchomienie (repeats)
    3. Analiza statystyczna (Mean, StdDev, CV)
    """
    state_manager.start_new_session()
    
    total_results = {}

    for algo in algo_configs:
        if not algo.isUsed:
            continue
            
        param_grid = generate_param_grid(algo)
        logger.info(f"Algorytm: {algo.name}, Liczba kombinacji: {len(param_grid)}")
        
        experiment_data = []

        for idx, params in enumerate(param_grid):
            if state_manager.should_stop():
                break

            scores = []
            
            # Pętla powtórzeń (dla badania stabilności/powtarzalności)
            for r in range(repeats):
                if state_manager.should_stop(): break

                # Wywołanie workera (tutaj hardcodujemy mapowanie nazw params na argumenty funkcji)
                # W pełnej wersji trzeba by zrobić dynamiczne mapowanie.
                if algo.name == "Bat alhorithm":
                    res = bat_worker(
                        objective_func,
                        n_bats=int(params.get("Agents", 20)),
                        max_iter=int(params.get("Iterations", 50)),
                        alpha=float(params.get("Alpha", 0.9)),
                        gamma=float(params.get("Gamma", 0.9)),
                        f_bounds=(0, float(params.get("Frequancy", 2.0))),
                        bounds=(-5, 5),
                        dims=2
                    )
                    scores.append(res["best_score"])
                
                # Raportowanie cząstkowe (żeby pasek postępu żył)
                state_manager.update_progress(algo.name, {
                    "status": "running_experiment",
                    "current_config": idx + 1,
                    "total_configs": len(param_grid),
                    "current_repeat": r + 1,
                    "total_repeats": repeats,
                    "current_params": params
                })
            
            # Analiza statystyczna dla tej konfiguracji
            if scores:
                mean_score = np.mean(scores)
                std_dev = np.std(scores)
                cv = (std_dev / mean_score) * 100 if mean_score != 0 else 0.0 # Coefficient of Variation w %
                
                # Zapisujemy wynik tej konfiguracji
                result_entry = {
                    "params": params,
                    "mean_score": float(mean_score),
                    "std_dev": float(std_dev),
                    "cv_percent": float(cv),
                    "is_stable": float(cv) < 2.0, # Warunek 2% ze schematu
                    "raw_scores": scores
                }
                experiment_data.append(result_entry)
        
        total_results[algo.name] = experiment_data
        
        # Zapisz częściowy wynik eksperymentu
        state_manager.update_progress(algo.name, {
            "status": "finished_experiment",
            "results_summary": experiment_data
        })

    # Finalny zapis
    state_manager.save_checkpoint("experiment_results.json")