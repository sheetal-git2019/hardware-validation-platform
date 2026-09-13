from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SensorReading:
    timestamp: str
    sensor: str
    condition: str
    temperature_c: float | None
    humidity_percent: float | None
    connected: bool
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TestResult:
    name: str
    status: str
    started_at: str
    finished_at: str
    details: str
    metrics: dict[str, Any]
    test_id: str | None = None
    requirement_id: str | None = None
    tags: list[str] | None = None
    priority: str | None = None
    release_blocking: bool = True

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
