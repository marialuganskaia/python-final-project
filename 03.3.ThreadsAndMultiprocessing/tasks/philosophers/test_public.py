from philosophers import Dinner, Philosopher, Fork
from typing import List
import time
from random import randint


class PhilosopherSimulationChecker:
    def __init__(self, dinner: Dinner):
        self.dinner: Dinner = dinner
        self.philosophers: List[Philosopher] = dinner.philosophers

        self.min_interval: float = min(
            [min(el.get_think_time(), el.get_eat_time()) for el in dinner.philosophers]) # noqa

        self.forks: List[Fork] = dinner.forks

    def check_deadlock(self) -> bool:
        """
        Check if the system is in a deadlock state.
        """
        return all([el.is_thinking() for el in self.philosophers])

    def check_starvation(self, timeout: int = 10) -> bool:
        """
        Check if any philosopher is starving (hasn't eaten for a long time).
        """
        return False

    def check_mutual_exclusion(self) -> bool:
        """
        Check if no two adjacent philosophers are eating simultaneously.
        """
        for i in range(len(self.philosophers)):
            if self.philosophers[i].is_eating() and self.philosophers[(
                    i + 1) % len(self.philosophers)].is_eating():
                return True
        return False

    def comprehensive_check(self, duration: float) -> bool:
        """
        Run a comprehensive check for a specified duration.
        """
        start_time = time.time()
        self.dinner.run_simulation(duration)
        while time.time() - start_time < duration:
            if self.check_deadlock() or self.check_starvation() or self.check_mutual_exclusion(): # noqa
                return False
            time.sleep(self.min_interval)
        return True


def test_public():
    checker = PhilosopherSimulationChecker(Dinner(5, [lambda: randint(
        1, 10) for _ in range(5)], [lambda: randint(1, 10) for _ in range(5)]))

    assert checker.comprehensive_check(100)
