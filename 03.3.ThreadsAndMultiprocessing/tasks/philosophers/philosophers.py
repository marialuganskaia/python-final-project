import threading
from enum import StrEnum
from typing import Callable
import time


class Fork:
    def __init__(self, index: int):
        self.lock: threading.Lock = threading.Lock()
        self.index: int = index
        # Добавьте любые другие необходимые атрибуты

    def is_locked(self) -> bool:
        """Check if the fork is locked"""
        return self.lock.locked()


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
        self.index: int = index
        self.left_fork: Fork = left_fork
        self.right_fork: Fork = right_fork
        self.get_think_time: Callable[[], float] = get_think_time
        self.get_eat_time: Callable[[], float] = get_eat_time
        self.state: PhilosopherState = PhilosopherState.THINKING
        self.meals_cnt: int = 0
        self.stop = threading.Event()

        if left_fork.index < right_fork.index:
            self.first_fork: Fork = left_fork
            self.second_fork: Fork = right_fork
        else:
            self.first_fork = right_fork
            self.second_fork = left_fork

    def run(self) -> None:
        # Реализуйте основную логику жизненного цикла философа
        while not self.stop.is_set():
            self.state = PhilosopherState.THINKING
            if self.stop.wait(self.get_think_time()):
                break

            self.state = PhilosopherState.HUNGRY

            with self.first_fork.lock:
                with self.second_fork.lock:
                    self.state = PhilosopherState.EATING
                    self.meals_cnt += 1
                    if self.stop.wait(self.get_eat_time()):
                        break

    def is_eating(self) -> bool:
        return self.state == PhilosopherState.EATING

    def is_hungry(self) -> bool:
        return self.state == PhilosopherState.HUNGRY

    def is_thinking(self) -> bool:
        return self.state == PhilosopherState.THINKING

    def count_meals(self) -> int:
        return self.meals_cnt


class Dinner:
    def __init__(
        self,
        num_philosophers: int,
        get_think_time: list[Callable[[], float]],
        get_eat_time: list[Callable[[], float]]
    ):
        self.num_philosophers: int = num_philosophers
        self.philosophers: list[Philosopher] = []
        self.forks: list[Fork] = []
        # Инициализируйте вилки и философов
        for i in range(num_philosophers):
            self.forks.append(Fork(i))
        for i in range(num_philosophers):
            left_fork = self.forks[i]
            right_fork = self.forks[(i + 1) % num_philosophers]
            phil = Philosopher(
                index=i,
                left_fork=left_fork,
                right_fork=right_fork,
                get_think_time=get_think_time[i],
                get_eat_time=get_eat_time[i]
            )
            self.philosophers.append(phil)

    def run_simulation(self, duration: int) -> None:
        # Запустите симуляцию и выполните ее в течение указанного времени
        for phil in self.philosophers:
            phil.start()
        time.sleep(duration)
        self.stop_simulation()

    def run_meals(self, max_m: int) -> None:
        for phil in self.philosophers:
            phil.start()
        while not all(phil.meals_cnt >= max_m for phil in self.philosophers):
            time.sleep(0.1)
        self.stop_simulation()

    def stop_simulation(self) -> None:
        # Реализуйте метод для корректной остановки симуляции
        for phil in self.philosophers:
            phil.stop.set()
        while any(phil.is_alive() for phil in self.philosophers):
            time.sleep(0.1)
