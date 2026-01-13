import numpy as np
import random
import json
import pickle
import os
import cma
import asyncio

from algorithms.BatAlgorithm import bat_algorithm
from algorithms.ArtificialBeeColony import artificial_bee_colony
from algorithms.GeneticAlgorithm import (
    genetic_algorithm,
    arithmetic_crossover,
    single_point_crossover,
    gaussian_mutation,
    uniform_mutation
)

from algorithms.plotConvergence import plot_convergence
from algorithms.animateAlgorithms import animate_algorithm

from algorithms.objective_functions import sphere_function, rastrigin_function, rosenbrock_function

class MetaheuristicTuner:

    def param_spaces_fn(self, algorithm):
        new_param_space = {}

        for alg in  algorithm:
            name = alg["name"]
            params = {}
            for param in alg["params"]:
                p_name = param["name"]
                p_type = param["type"]
                if param["range"] == "min-max":
                    if p_type == "int":
                        p_min = int(param["min"])
                        p_max = int(param["max"])
                    else:
                        p_min = float(param["min"])
                        p_max = float(param["max"])
                    params[p_name] = (p_min, p_max, p_type)
               
            new_param_space[name] = params
        return new_param_space


    def __init__(self, progress_send_fn, pause_check_fn, stop_check_fn):
        self.progress_send_fn = progress_send_fn
        self.pause_check_fn = pause_check_fn
        self.stop_check_fn = stop_check_fn

        # Folder na wszystkie pliki
        self.folder = "checkpoints"
        os.makedirs(self.folder, exist_ok=True)

        # Plik globalnego stanu tunera
        self.tuner_state_file = os.path.join(self.folder, "tuner_state.json")

        # ============================
        # WRAPPERY ALGORYTMÓW
        # ============================
        self.runners = {
            "Bat": self.run_BAT,
            "Genetic": self.run_GA,
            "ABC": self.run_ABC
        }

    # ============================================================
    # WRAPPERY ALGORYTMÓW
    # ============================================================

    def run_BAT(self, params, func, bounds, dim):
        _, best_value, _, _ = bat_algorithm(
            fn=func,
            n_bats=params["n_bats"],
            bounds=bounds,
            max_iter=params["max_iter"],
            dims=dim,
            alpha=params["alpha"],
            gamma=params["gamma"],
            f_bounds=(params["f_bounds_min"], params["f_bounds_max"])
        )
        return best_value

    def run_ABC(self, params, func, bounds, dim):
        _, best_value, _, _ = artificial_bee_colony(
            n_bees=params["n_bees"],
            dim=dim,
            bounds=bounds,
            max_iter=params["max_iter"],
            objective_func=func
        )
        return best_value

    def run_GA(self, params, func, bounds, dim):
        # Parametry kategoryczne są już zmapowane w vector_to_params()
        crossover_type = params["crossover_type"]
        mutation_type  = params["mutation_type"]

        crossover = (
            arithmetic_crossover if crossover_type == "arithmetic"
            else single_point_crossover
        )

        mutation = (
            uniform_mutation if mutation_type == "uniform"
            else gaussian_mutation
        )

        _, best_value, _, _ = genetic_algorithm(
            dim=dim,
            pop_size=params["pop_size"],
            objective_func=func,
            bounds=bounds,
            max_generations=params["max_generations"],
            crossover_rate=params["crossover_rate"],
            mutation_rate=params["mutation_rate"],
            mutation_scale=params["mutation_scale"],
            elitism_rate=params["elitism_rate"],
            tournament_size=params["tournament_size"],
            crossover_type=crossover,
            mutation_type=mutation
        )

        return best_value

    # ============================================================
    # FUNKCJA CELU
    # ============================================================

    def evaluate_params(self, params, runner, selected_funcs, dim, R=20):
        sigmas = []

        for fmeta in selected_funcs:
            func = fmeta["code"]
            bounds = fmeta["bounds"]

            results = []
            for r in range(R):
                np.random.seed(r)
                random.seed(r)
                results.append(runner(params, func, bounds, dim))

            sigmas.append(np.std(results))

        return np.mean(sigmas)

    # ============================================================
    # KONWERSJA WEKTORA CMA → PARAMETRY
    # (tu dokładamy kategorie dla GA)
    # ============================================================

    def vector_to_params(self, x, param_space, algorithm):
        params = {}
        i = 0

        # parametry liczbowe
        for name, (pmin, pmax, ptype) in param_space.items():
            val = x[i]
            val = max(pmin, min(pmax, val))
            if ptype == "int":
                val = int(round(val))
            params[name] = val
            i += 1

        # parametry kategoryczne GA
        if algorithm == "GA":
            crossover_raw = int(round(x[i]))
            mutation_raw  = int(round(x[i+1]))

            crossover_raw = max(0, min(1, crossover_raw))
            mutation_raw  = max(0, min(1, mutation_raw))

            params["crossover_type"] = "arithmetic" if crossover_raw == 0 else "single_point"
            params["mutation_type"]  = "uniform"    if mutation_raw  == 0 else "gaussian"

        return params

    # ============================================================
    # TUNER JEDNEGO ALGORYTMU
    # ============================================================

    async def tune_single_algorithm(self, algorithm, selected_funcs, dim,
                              iterations=30, R=20):

        param_space = self.param_spaces[algorithm]
        runner = self.runners[algorithm]

        checkpoint_json = os.path.join(self.folder, f"checkpoint_{algorithm}.json")
        checkpoint_pkl  = os.path.join(self.folder, f"checkpoint_{algorithm}.pkl")

        es = None
        start_iter = 0

        # ====== WZNOWIENIE ======
        if os.path.exists(checkpoint_json) and os.path.exists(checkpoint_pkl):
            print(f"Wznawiam tuner {algorithm} z checkpointu...")

            with open(checkpoint_json, "r") as f:
                start_iter = json.load(f)["current_iteration"]

            with open(checkpoint_pkl, "rb") as f:
                es = pickle.load(f)

        else:
            print(f"Startuję tuner {algorithm} od początku...")

            base_dim = len(param_space)
            extra_dims = 2 if algorithm == "GA" else 0

            x0 = [(pmin + pmax) / 2 for (pmin, pmax, _) in param_space.values()]
            for _ in range(extra_dims):
                x0.append(0.5)

            es = cma.CMAEvolutionStrategy(x0, 0.3)

        # ====== GŁÓWNA PĘTLA ======
        for it in range(start_iter, iterations):
            await asyncio.sleep(0)
            if await self.pause_check_fn():
                print(f"Zatrzymano tuner {algorithm} na iteracji {it}.")
                return "pause"
            
            if await self.stop_check_fn():
                
                print(f"Zatrzymano tuner {algorithm} na iteracji {it}")
                return "stop"
          
            await self.progress_send_fn(int((it + 1) / iterations * 100), type="param_progress")
            solutions = es.ask()
            fitness = []

            for x in solutions:
                params = self.vector_to_params(x, param_space, algorithm)
                fitness.append(self.evaluate_params(params, runner, selected_funcs, dim, R))

            es.tell(solutions, fitness)
            es.disp()

            # zapis checkpointu
            with open(checkpoint_pkl, "wb") as f:
                pickle.dump(es, f)

            with open(checkpoint_json, "w") as f:
                json.dump({
                    "current_iteration": it + 1
                }, f)

        best_vector = es.result.xbest
        return self.vector_to_params(best_vector, param_space, algorithm)


    # ============================================================
    # GENEROWANIE WYKRESU I ANIMACJI
    # ============================================================
    def generate_figures(self, best, alg, dim, selected_funcs):
        print(dim)
        figure = {}
        for fn in selected_funcs:
            fn_name = fn["name"]
            figure = {}
            func = fn["code"]
            bounds = fn["bounds"]
            print("Generating figures for", alg, "on", fn_name)
            if alg == "ABC":
                _, _, convergence_curve, positions_log = artificial_bee_colony(best['n_bees'], dim, bounds, best['max_iter'], func, limit=None)
            if alg == "Bat":
                _, _, convergence_curve, positions_log = bat_algorithm(
                    fn=func,
                    n_bats=best['n_bats'],
                    bounds=bounds,
                    alpha=best['alpha'],
                    gamma=best['gamma'],
                    f_bounds=(best['f_bounds_min'], best['f_bounds_max']),
                    max_iter=best['max_iter'],
                    dims=dim)
            if alg == "Genetic":
                crossover = (arithmetic_crossover if best['crossover_type'] == 0 else single_point_crossover)
                mutation = (gaussian_mutation if best['mutation_type'] == 0 else uniform_mutation)
                _, _, convergence_curve, positions_log = genetic_algorithm(best['pop_size'], dim, bounds, best['max_generations'], func, best['crossover_rate'], best['mutation_rate'], best['mutation_scale'], best['elitism_rate'], best['tournament_size'], crossover, mutation)
 
            convergence_plot_base64 = plot_convergence(convergence_curve, alg, fn_name)
            figure['convergence_plot'] = convergence_plot_base64
            if dim == 2:
                animation_base64 = animate_algorithm(positions_log, [bounds, bounds], func)
                figure['animation'] = animation_base64
        return figure

    # ============================================================
    # TUNER WIELU ALGORYTMÓW
    # ============================================================
    def delete_checkpoints(self):
        # usuwamy checkpointy algorytmów
        for file in os.listdir(self.folder):
            os.remove(os.path.join(self.folder, file))
            
            
    async def tune_algorithms(self, algorithmsData, selected, selected_funcs, dim,
                        iterations=30, R=20):
        self.param_spaces = self.param_spaces_fn(algorithmsData)
        results = {}

        # ====== WZNOWIENIE GLOBALNE ======
        if os.path.exists(self.tuner_state_file):
            with open(self.tuner_state_file, "r") as f:
                start_index = json.load(f)["current_algorithm_index"]
            print(f"Wznawiam tuning od algorytmu index {start_index}.")
        else:
            start_index = 0

        # ====== Wczytanie wyników poprzednich algorytmów ======
        for j in range(start_index):
            alg = selected[j]
            res_file = os.path.join(self.folder, f"results_{alg}.json")
            if os.path.exists(res_file):
                with open(res_file, "r") as f:
                    results[alg] = json.load(f)

        # ====== PĘTLA ALGORYTMÓW ======
        for i in range(start_index, len(selected)):
            await self.progress_send_fn(int(i/len(selected)*100), type="alg_progress")

            alg = selected[i]
            print(alg)
            print(f"\n=== Zaczynam algorytm: {alg} ===")

            best = await self.tune_single_algorithm(
                algorithm=alg,
                selected_funcs=selected_funcs,
                dim=dim,
                iterations=iterations,
                R=R
            )
    
            if best == "pause":
                print(f"Tuner przerwany podczas strojenia algorytmu {alg}.")
                # Zapisujemy stan globalny, żeby wznowić od TEGO algorytmu
                with open(self.tuner_state_file, "w") as f:
                    json.dump({
                        "current_algorithm_index": i,
                        "selected_algorithms": selected
                    }, f)
                return None, None
            
            if best == "stop":
                self.delete_checkpoints()
                return None, None
            
            results[alg] = best

            # zapis wyniku
            with open(os.path.join(self.folder, f"results_{alg}.json"), "w") as f:
                json.dump(best, f)

            # zapis globalnego stanu
            with open(self.tuner_state_file, "w") as f:
                json.dump({"current_algorithm_index": i + 1}, f)

            # usuwamy checkpointy algorytmu
            for ext in ["json", "pkl"]:
                path = os.path.join(self.folder, f"checkpoint_{alg}.{ext}")
                if os.path.exists(path):
                    os.remove(path)

        figures = {}
        for alg in selected:
            if alg in results:  # Tylko dla ukończonych algorytmów
                figure = self.generate_figures(results[alg], alg, dim, selected_funcs)
                figures[alg] = figure

        # ====== SPRZĄTANIE ======
        if os.path.exists(self.tuner_state_file):
            os.remove(self.tuner_state_file)

        # usuwamy results_*.json
        for alg in selected:
            path = os.path.join(self.folder, f"results_{alg}.json")
            if os.path.exists(path):
                os.remove(path)

        return results, figures