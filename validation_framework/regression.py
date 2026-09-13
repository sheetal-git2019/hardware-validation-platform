from __future__ import annotations

import time
import uuid
from dataclasses import asdict
from pathlib import Path

from .environment import collect_environment
from .models import SensorReading, TestResult, utc_now
from .stress import CpuLoad
from .test_plan import TestPlan
from .validation import HardwareValidator


class RegressionSuite:
    """Traceable validation executor with selectable suites and fault coverage."""

    def __init__(self, validator: HardwareValidator, continuous_duration_seconds: float = 600.0,
                 test_plan_path: Path | None = None) -> None:
        self.validator = validator
        self.continuous_duration_seconds = continuous_duration_seconds
        self.plan = TestPlan.load(test_plan_path)

    def _result(self, key: str, started: str, status: str, details: str, metrics: dict) -> TestResult:
        definition = self.plan.get(key)
        return TestResult(
            name=definition.title, status=status, started_at=started, finished_at=utc_now(), details=details,
            metrics={"test_key": key, **metrics}, test_id=definition.id, requirement_id=definition.requirement,
            tags=list(definition.tags), priority=definition.priority, release_blocking=definition.release_blocking,
        )

    def sensor_data_integrity(self, samples: int = 5) -> TestResult:
        started = utc_now()
        readings = [self.validator.collect_reading("normal") for _ in range(samples)]
        valid = [self._is_valid(reading) for reading in readings]
        return self._result("sensor_data_integrity", started, "PASS" if all(valid) else "FAIL",
                            f"{sum(valid)}/{samples} readings passed presence and range checks.",
                            {"sample_count": samples, "valid_count": sum(valid)})

    def disconnect_reconnect_recovery(self) -> TestResult:
        started = utc_now()
        module = self.validator.module
        if hasattr(module, "set_connected"):
            getattr(module, "set_connected")(False)
            disconnected = self.validator.collect_reading("simulated_disconnect")
            getattr(module, "set_connected")(True)
            recovered = self.validator.collect_reading("reconnect")
            passed = not disconnected.connected and self._is_valid(recovered)
            details = "Disconnect was detected and a valid reading was recovered."
            metrics = {"disconnect_detected": not disconnected.connected, "recovered": self._is_valid(recovered), "method": "simulated_disconnect"}
        else:
            module.close()
            module.initialize()
            recovered = self.validator.collect_reading("driver_recovery")
            passed = self._is_valid(recovered)
            details = "Driver re-initialization recovered a valid reading; perform the documented physical unplug test separately."
            metrics = {"recovered": passed, "method": "driver_reinitialization"}
        return self._result("disconnect_reconnect_recovery", started, "PASS" if passed else "FAIL",
                            details if passed else "Disconnect/recovery behavior was incorrect.", metrics)

    def continuous_sampling_performance(self) -> TestResult:
        started = utc_now()
        start = time.monotonic()
        with CpuLoad():
            readings = self.validator.sample_for("high_load", self.continuous_duration_seconds)
        elapsed = time.monotonic() - start
        valid = sum(self._is_valid(reading) for reading in readings)
        expected_minimum = max(1, int(self.continuous_duration_seconds / self.validator.config.sample_interval_seconds))
        passed = valid == len(readings) and len(readings) >= expected_minimum
        return self._result("continuous_sampling_performance", started, "PASS" if passed else "FAIL",
                            "Continuous sampling completed." if passed else "Sampling loss or invalid data detected.",
                            {"duration_seconds": round(elapsed, 3), "samples": len(readings), "valid_samples": valid,
                             "expected_minimum_samples": expected_minimum})

    def fault_injection_detection(self) -> TestResult:
        started = utc_now()
        module = self.validator.module
        if not all(hasattr(module, name) for name in ("inject_fault", "clear_fault")):
            return self._result("fault_injection_detection", started, "SKIP",
                                "This hardware adapter has no controllable fault injector.", {"method": "not_supported"})
        getattr(module, "inject_fault")("out_of_range")
        faulted = self.validator.collect_reading("fault_injection_out_of_range")
        getattr(module, "clear_fault")()
        recovered = self.validator.collect_reading("fault_recovery")
        detected = not self._is_valid(faulted)
        recovered_ok = self._is_valid(recovered)
        passed = detected and recovered_ok
        return self._result("fault_injection_detection", started, "PASS" if passed else "FAIL",
                            "Injected invalid data was detected and valid data recovered." if passed else "Fault injection was not detected or recovery failed.",
                            {"fault_detected": detected, "recovered": recovered_ok, "fault": "out_of_range"})

    def run(self, suite: str = "regression", tags: tuple[str, ...] = ()) -> dict:
        selected = self.plan.select(suite, tags)
        if not selected:
            raise ValueError(f"No test cases selected for suite={suite!r}, tags={tags!r}")
        if not self.validator.initialize_and_verify():
            raise RuntimeError("Sensor connectivity verification failed")
        methods = {
            "sensor_data_integrity": self.sensor_data_integrity,
            "disconnect_reconnect_recovery": self.disconnect_reconnect_recovery,
            "continuous_sampling_performance": self.continuous_sampling_performance,
            "fault_injection_detection": self.fault_injection_detection,
        }
        results = [methods[test.key]() for test in selected]
        blocking_failures = [result.test_id for result in results if result.release_blocking and result.status != "PASS"]
        counts = {status: sum(result.status == status for result in results) for status in ("PASS", "FAIL", "SKIP")}
        quality = {
            "total_cases": len(results), "passed": counts["PASS"], "failed": counts["FAIL"], "skipped": counts["SKIP"],
            "pass_rate_percent": round(100 * counts["PASS"] / len(results), 1),
            "release_ready": not blocking_failures, "blocking_failures": blocking_failures,
        }
        run = {
            "run_id": str(uuid.uuid4()), "plan_id": self.plan.plan_id, "plan_title": self.plan.title,
            "suite": suite, "tags": list(tags), "started_at": results[0].started_at, "finished_at": utc_now(),
            "status": "PASS" if quality["release_ready"] else "FAIL", "release_gate": self.plan.release_gate,
            "quality_summary": quality,
            "environment": {**collect_environment(), "module": self.validator.module.name,
                            "sample_interval_seconds": self.validator.config.sample_interval_seconds},
            "results": [asdict(result) for result in results],
        }
        self.validator.store.save_regression_run(run)
        return run

    def run_all(self) -> dict:
        return self.run()

    def _is_valid(self, reading: SensorReading) -> bool:
        return (reading.connected and reading.temperature_c is not None and reading.humidity_percent is not None
                and self.validator.config.temperature_range_c[0] <= reading.temperature_c <= self.validator.config.temperature_range_c[1]
                and self.validator.config.humidity_range_percent[0] <= reading.humidity_percent <= self.validator.config.humidity_range_percent[1])
