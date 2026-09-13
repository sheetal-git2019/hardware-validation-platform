from __future__ import annotations

from collections.abc import Callable

from .base import HardwareModule


class HardwareRegistry:
    """Factory registry for plug-in modules without changes to the test engine."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable[[], HardwareModule]] = {}

    def register(self, name: str, factory: Callable[[], HardwareModule]) -> None:
        if name in self._factories:
            raise ValueError(f"Module already registered: {name}")
        self._factories[name] = factory

    def create(self, name: str) -> HardwareModule:
        try:
            return self._factories[name]()
        except KeyError as exc:
            raise KeyError(f"No hardware module registered as {name}") from exc
