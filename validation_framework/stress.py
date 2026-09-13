from __future__ import annotations

import multiprocessing
import time


def _burn(stop: multiprocessing.synchronize.Event, duty_cycle: float) -> None:
    """Process target kept at module scope so Windows and Raspberry Pi can spawn it."""
    while not stop.is_set():
        active_until = time.monotonic() + (0.1 * duty_cycle)
        accumulator = 0
        while time.monotonic() < active_until:
            accumulator = (accumulator * 13 + 7) % 100_003
        stop.wait(0.1 * (1 - duty_cycle))


class CpuLoad:
    """Bounded CPU contention used to exercise sampling while the host is busy."""

    def __init__(self, workers: int = 1, duty_cycle: float = 0.85) -> None:
        self.workers = max(1, workers)
        self.duty_cycle = min(1.0, max(0.05, duty_cycle))
        self._stop = multiprocessing.Event()
        self._processes: list[multiprocessing.Process] = []

    def __enter__(self) -> "CpuLoad":
        for _ in range(self.workers):
            process = multiprocessing.Process(target=_burn, args=(self._stop, self.duty_cycle), daemon=True)
            process.start()
            self._processes.append(process)
        return self

    def __exit__(self, *_: object) -> None:
        self._stop.set()
        for process in self._processes:
            process.join(timeout=1)
            if process.is_alive():
                process.terminate()
