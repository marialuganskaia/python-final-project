import threading
from enum import StrEnum
from typing import Callable

class Fork:
    def __init__(self, index: int):
        self.lock: threading.Lock = threading.Lock()
        self.index: int = index
        # Добавьте любые другие необходимые атрибуты

    def is_locked(self) -> bool:
        """Check if the fork is locked"""
        pass

class PhilosopherState(StrEnum):
    THINKING = "thinking"
    HUNGRY = "hungry"
    EATING = "eating"

class Philosopher(threading.Thread):
    def __init__(
        self,
        index: int,
        left_fork: Fork,
        right_fork: Fork,
        get_think_time: Callable[[], float],
        get_eat_time: Callable[[], float]
    ):
        super().__init__()
        self.index : int = index
        self.left_fork : Fork = left_fork
        self.right_fork : Fork = right_fork
        # Добавьте любые другие необходимые атрибуты

    def run(self):
        # Реализуйте основную логику жизненного цикла философа
        pass

    def is_eating(self) -> bool:
        pass
    
    def is_hungry(self) -> bool:
        pass
    
    def is_thinking(self) -> bool:
        pass
    
    def count_meals(self) -> int:
        pass
    

class Dinner:
    def __init__(
        self,
        num_philosophers,
        get_think_time: list[Callable[[], float]],
        get_eat_time: list[Callable[[], float]]
    ):
        self.num_philosophers = num_philosophers
        self.philosophers = []
        self.forks = []
        # Инициализируйте вилки и философов
        # get_think_time и get_eat_time - список функций, которые возвращают время для размышления и еды для каждого философа

    def run_simulation(self, duration):
        # Запустите симуляцию и выполните ее в течение указанного времени
        pass

    def stop_simulation(self):
        # Реализуйте метод для корректной остановки симуляции
        pass
