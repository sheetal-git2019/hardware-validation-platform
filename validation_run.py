"""Collect timestamped DHT22 readings under a selected stress condition."""
from __future__ import annotations

import argparse
from pathlib import Path

from validation_framework.config import ValidationConfig
from validation_framework.hardware import DHT22Sensor, SimulatedDHT22
from validation_framework.stress import CpuLoad
from validation_framework.validation import HardwareValidator


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hardware", action="store_true", help="Use the physical DHT22 rather than simulation")
    parser.add_argument("--condition", choices=["normal", "high_load", "simulated_disconnect"], default="normal")
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    module = DHT22Sensor() if args.hardware else SimulatedDHT22()
    validator = HardwareValidator(module, ValidationConfig(data_dir=args.data_dir))
    try:
        if not validator.initialize_and_verify():
            print("Connectivity check failed")
            return 2
        if args.condition == "simulated_disconnect" and hasattr(module, "set_connected"):
            getattr(module, "set_connected")(False)
        if args.condition == "high_load":
            with CpuLoad():
                readings = validator.sample_for(args.condition, args.duration)
        else:
            readings = validator.sample_for(args.condition, args.duration)
        print(f"Collected {len(readings)} readings in {args.condition} condition.")
        return 0
    finally:
        validator.close()


if __name__ == "__main__":
    raise SystemExit(main())
