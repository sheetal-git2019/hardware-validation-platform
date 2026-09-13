from __future__ import annotations

import random

from .base import BaseHardwareModule, SensorDisconnectedError


class SimulatedDHT22(BaseHardwareModule):
    """Repeatable-enough DHT22 emulator used for local development and CI."""

    name = "dht22-simulated"

    def __init__(self, seed: int = 42) -> None:
        self._random = random.Random(seed)
        self._initialized = False
        self._connected = True
        self._fault: str | None = None

    def initialize(self) -> None:
        self._initialized = True

    def verify_connectivity(self) -> bool:
        return self._initialized and self._connected

    def set_connected(self, connected: bool) -> None:
        self._connected = connected

    def inject_fault(self, fault: str) -> None:
        """Enable deterministic negative-test behavior without real equipment."""
        if fault not in {"out_of_range", "read_error"}:
            raise ValueError(f"Unsupported simulated fault: {fault}")
        self._fault = fault

    def clear_fault(self) -> None:
        self._fault = None

    def read(self) -> dict[str, float]:
        if not self._initialized:
            raise RuntimeError("Sensor must be initialized before reading")
        if not self._connected:
            raise SensorDisconnectedError("Simulated DHT22 is disconnected")
        if self._fault == "read_error":
            raise SensorDisconnectedError("Injected simulated read error")
        if self._fault == "out_of_range":
            return {"temperature_c": 120.0, "humidity_percent": 140.0}
        return {
            "temperature_c": round(24.0 + self._random.uniform(-1.5, 1.5), 2),
            "humidity_percent": round(48.0 + self._random.uniform(-4.0, 4.0), 2),
        }

    def close(self) -> None:
        self._initialized = False
