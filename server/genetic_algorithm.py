import asyncio
import numpy as np

async def run_genetic_simple(manager, config, resume_data=None):
    params = {arg['name']: arg['min'] for arg in config.get('args', [])}
    agents_count = int(params.get("Agents", 20))
    iterations = int(params.get("Iterations", 100))
    
    if resume_data:
        start_t = resume_data["current_iter"]
        best_val = resume_data["best_val"]
    else:
        start_t = 0
        best_val = 1000.0 # Przykładowy startowy fitness

    for t in range(start_t, iterations):
        if not manager.isRunning: break
        while manager.isPaused:
            await asyncio.sleep(0.1)
            if not manager.isRunning: return

        # Logika genetyczna (Mutacja, Krzyżowanie - symulacja)
        await asyncio.sleep(0.05)
        best_val -= np.random.random() # Zmniejszamy fitness
        
        if t % 10 == 0:
            manager.save_checkpoint({
                "algo_name": "Genetic algorytm",
                "current_iter": t,
                "best_val": float(best_val),
                "population": [] # Tu byłaby populacja
            })

        if manager.websocket:
            await manager.websocket.send_json({
                "type": "progress",
                "algo": "Genetic algorytm",
                "iteration": t + 1,
                "total": iterations,
                "best_score": best_val
            })