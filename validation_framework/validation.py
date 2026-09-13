from __future__ import annotations

import time
from typing import Callable

from .config import ValidationConfig
from .hardware.base import HardwareModule, SensorDisconnectedError
from .models import SensorReading, utc_now
from .storage import ResultStore


class HardwareValidator:
    """Coordinates a hardware module and durable, structured measurement logging."""

    def __init__(self, module: HardwareModule, config: ValidationConfig, store: ResultStore | None = None) -> None:
        config.ensure_directories()
        self.module = module
        self.config = config
        self.store = store or ResultStore(config.data_dir)

    def initialize_and_verify(self) -> bool:
        self.module.initialize()
        return self.module.verify_connectivity()

    def collect_reading(self, condition: str) -> SensorReading:
        try:
            values = self.module.read()
            reading = SensorReading(utc_now(), self.module.name, condition, values.get("temperature_c"), values.get("humidity_percent"), True)
        except (SensorDisconnectedError, ConnectionError) as exc:
            reading = SensorReading(utc_now(), self.module.name, condition, None, None, False, str(exc))
        self.store.log_reading(reading.as_dict())
        return reading

    def sample_for(self, condition: str, duration_seconds: float, interval_seconds: float | None = None,
                   before_each_sample: Callable[[], None] | None = None) -> list[SensorReading]:
        interval = interval_seconds if interval_seconds is not None else self.config.sample_interval_seconds
        if interval <= 0:
            raise ValueError("Sample interval must be positive")
        deadline = time.monotonic() + duration_seconds
        readings: list[SensorReading] = []
        while True:
            if before_each_sample:
                before_each_sample()
            readings.append(self.collect_reading(condition))
            if time.monotonic() >= deadline:
                break
            time.sleep(min(interval, max(0, deadline - time.monotonic())))
        return readings

    def close(self) -> None:
        self.module.close()
