from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol


class SensorDisconnectedError(ConnectionError):
    """The module is unavailable but the host process remains healthy."""


class HardwareModule(Protocol):
    """Contract new modules (RFID, accelerometer, etc.) must implement."""

    name: str

    def initialize(self) -> None: ...

    def verify_connectivity(self) -> bool: ...

    def read(self) -> dict[str, float]: ...

    def close(self) -> None: ...


class BaseHardwareModule(ABC):
    name: str

    @abstractmethod
    def initialize(self) -> None: ...

    @abstractmethod
    def verify_connectivity(self) -> bool: ...

    @abstractmethod
    def read(self) -> dict[str, float]: ...

    def close(self) -> None:
        pass
