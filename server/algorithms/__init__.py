# algorithms/__init__.py

from .bat_algorithm import run_bat_algorithm
from .genetic_algorithm import run_genetic_algorithm
from .abc_algorithm import run_abc_algorithm

ALGORITHM_MAP = {
    "Bat alhorithm": run_bat_algorithm,
    "Genetic algorytm": run_genetic_algorithm,
    "ABC alhorithm": run_abc_algorithm,
}