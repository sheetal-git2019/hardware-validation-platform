from __future__ import annotations

from .base import BaseHardwareModule, SensorDisconnectedError


class DHT22Sensor(BaseHardwareModule):
    """Raspberry Pi DHT22 adapter; imports hardware packages only when used."""

    name = "dht22"

    def __init__(self, gpio_pin: str = "D4") -> None:
        self.gpio_pin = gpio_pin
        self._device = None

    def initialize(self) -> None:
        try:
            import adafruit_dht  # type: ignore[import-not-found]
            import board  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "DHT22 support is not installed. Install adafruit-circuitpython-dht on the Pi."
            ) from exc
        try:
            pin = getattr(board, self.gpio_pin)
        except AttributeError as exc:
            raise ValueError(f"Unknown board pin: {self.gpio_pin}") from exc
        self._device = adafruit_dht.DHT22(pin)

    def verify_connectivity(self) -> bool:
        try:
            self.read()
            return True
        except SensorDisconnectedError:
            return False

    def read(self) -> dict[str, float]:
        if self._device is None:
            raise RuntimeError("Sensor must be initialized before reading")
        try:
            temperature, humidity = self._device.temperature, self._device.humidity
        except Exception as exc:  # library exposes platform-specific runtime errors
            raise SensorDisconnectedError(str(exc)) from exc
        if temperature is None or humidity is None:
            raise SensorDisconnectedError("DHT22 returned an empty reading")
        return {"temperature_c": float(temperature), "humidity_percent": float(humidity)}

    def close(self) -> None:
        if self._device is not None:
            self._device.exit()
            self._device = None
