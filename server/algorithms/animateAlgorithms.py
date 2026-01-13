import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import base64
import os

def animate_algorithm(positions_log, bounds, objective_func, interval=500):

    # Przygotowanie siatki pod contour plot
    x = np.linspace(bounds[0][0], bounds[0][1], 200)
    y = np.linspace(bounds[1][0], bounds[1][1], 200)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)

    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i, j] = objective_func(np.array([X[i, j], Y[i, j]]))

    fig, ax = plt.subplots(figsize=(7, 7))

    # Tło: poziomice funkcji celu
    ax.contourf(X, Y, Z, levels=50, cmap='viridis')
    ax.set_xlim(bounds[0])
    ax.set_ylim(bounds[1])
    ax.set_title("Ruch agentów algorytmu")

    # Punkty agentów
    scatter = ax.scatter([], [], c='red', s=40)

    # Funkcja aktualizująca klatkę
    def update(frame):
        positions = positions_log[frame]
        scatter.set_offsets(positions)
        ax.set_title(f"Ruch agentów — iteracja {frame}")
        return scatter,

    anim = FuncAnimation(fig, update, frames=len(positions_log), interval=interval, blit=True)

    # Zapis do bufora
    anim.save("animation.gif", writer='pillow', fps=1000/interval)
    with open("animation.gif", 'rb') as f:
        gif_bytes = f.read()

    gif_base64 = base64.b64encode(gif_bytes).decode('utf-8')

    plt.close(fig)
    os.remove("animation.gif")

    return gif_base64