"""Execute the DHT22 regression suite and save a structured result report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validation_framework.config import ValidationConfig
from validation_framework.hardware import DHT22Sensor, SimulatedDHT22
from validation_framework.regression import RegressionSuite
from validation_framework.validation import HardwareValidator


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hardware", action="store_true", help="Use a physical DHT22")
    parser.add_argument("--duration", type=float, default=600.0, help="Continuous sampling duration; default is ten minutes")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--suite", choices=["smoke", "regression"], default="regression", help="Test-plan suite to execute")
    parser.add_argument("--tag", action="append", default=[], help="Require a test-plan tag; repeat for multiple tags")
    parser.add_argument("--test-plan", type=Path, help="Path to a custom JSON test plan")
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    config = ValidationConfig(data_dir=args.data_dir, sample_interval_seconds=args.interval)
    module = DHT22Sensor() if args.hardware else SimulatedDHT22()
    validator = HardwareValidator(module, config)
    try:
        run = RegressionSuite(validator, args.duration, args.test_plan).run(args.suite, tuple(args.tag))
        print(json.dumps(run, indent=2))
        return 0 if run["status"] == "PASS" else 1
    finally:
        validator.close()


if __name__ == "__main__":
    raise SystemExit(main())
