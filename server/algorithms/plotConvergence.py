import matplotlib.pyplot as plt
import io
import base64

def plot_convergence(convergence_curve, algorithm, func):
    plt.figure(figsize=(10, 6))
    plt.plot(convergence_curve, 'b-', linewidth=2)
    plt.xlabel('Iteracja')
    plt.ylabel('Najlepsza wartość funkcji celu')
    plt.title(f'Krzywa zbieżności algorytmu {algorithm} dla funkcji {func}')
    plt.grid(True, alpha=0.3)
    plt.yscale('log')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()

    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    buf.close()

    return img_base64