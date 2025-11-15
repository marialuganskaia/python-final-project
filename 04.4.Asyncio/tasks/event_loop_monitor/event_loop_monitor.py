import asyncio
import statistics
import time
from typing import List, Dict, Optional


class EventLoopMonitor:
    """Класс-монитор событийного цикла."""
    def __init__(self) -> None:
        self.block_times: List[float] = []
        self.last_time: Optional[float] = None
        self.block_time: float = 0.001

    async def monitor_callback(self) -> None:
        """
        Callback to measure time between event loop iterations.
        Runs asynchronously as a daemon in the event loop.
        """
        while True:
            cur_time = time.time()
            if self.last_time is not None:
                t = cur_time - self.last_time
                if t > self.block_time:
                    self.block_times.append(t)
            self.last_time = cur_time
            await asyncio.sleep(0)

    def get_statistics(self) -> Dict[str, float]:
        """
        Calculate statistics about blocking times.
        TODO: Replace with actual implementation
        """
        if not self.block_times:
            return {
                "count": 0,
                "average": 0,
                "max": 0,
                "min": 0,
                "median": 0
            }
        count = len(self.block_times)
        average = statistics.mean(self.block_times)
        max_block = max(self.block_times)
        min_block = min(self.block_times)
        med_block = statistics.median(self.block_times)

        return {
            "count": count,
            "average": average,
            "max": max_block,
            "min": min_block,
            "median": med_block
        }
