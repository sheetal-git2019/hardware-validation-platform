from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ValidationConfig:
    """Runtime settings kept independent of any specific hardware backend."""

    data_dir: Path = Path("data")
    sensor_name: str = "dht22"
    gpio_pin: str = "D4"
    sample_interval_seconds: float = 2.0
    temperature_range_c: tuple[float, float] = (-40.0, 80.0)
    humidity_range_percent: tuple[float, float] = (0.0, 100.0)

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
