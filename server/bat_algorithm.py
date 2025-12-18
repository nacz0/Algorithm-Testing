import asyncio
import numpy as np

def objective_function(x):
    return sum(100.0 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)

async def run_bat_simple(manager, config, resume_data=None):
    params = {arg['name']: arg['min'] for arg in config.get('args', [])}
    agents_count = int(params.get("Agents", 20))
    iterations = int(params.get("Iterations", 100))
    
    if resume_data:
        start_t = resume_data["current_iter"]
        population = np.array(resume_data["population"])
        best_val = resume_data["best_val"]
    else:
        population = np.random.uniform(-2, 2, (agents_count, 2))
        start_t = 0
        best_val = float('inf')

    for t in range(start_t, iterations):
        if not manager.isRunning: break
        while manager.isPaused:
            await asyncio.sleep(0.1)
            if not manager.isRunning: return

        # Symulacja obliczeń
        await asyncio.sleep(0.05)
        best_val *= 0.98 # Demo postępu
        
        if t % 10 == 0:
            manager.save_checkpoint({
                "algo_name": "Bat alhorithm",
                "current_iter": t,
                "best_val": float(best_val),
                "population": population.tolist()
            })

        if manager.websocket:
            await manager.websocket.send_json({
                "type": "progress",
                "algo": "Bat alhorithm",
                "iteration": t + 1,
                "total": iterations,
                "best_score": best_val
            })