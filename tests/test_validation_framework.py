from __future__ import annotations

import json

from validation_framework.config import ValidationConfig
from validation_framework.hardware.simulated import SimulatedDHT22
from validation_framework.regression import RegressionSuite
from validation_framework.validation import HardwareValidator


def make_validator(tmp_path, interval: float = 0.01) -> HardwareValidator:
    validator = HardwareValidator(SimulatedDHT22(), ValidationConfig(data_dir=tmp_path, sample_interval_seconds=interval))
    assert validator.initialize_and_verify()
    return validator


def test_reading_is_written_to_jsonl_and_csv(tmp_path):
    validator = make_validator(tmp_path)
    reading = validator.collect_reading("normal")
    assert reading.connected
    assert json.loads((tmp_path / "readings.jsonl").read_text())["temperature_c"] is not None
    assert "humidity_percent" in (tmp_path / "readings.csv").read_text()


def test_integrity_regression_passes_for_simulated_sensor(tmp_path):
    suite = RegressionSuite(make_validator(tmp_path))
    result = suite.sensor_data_integrity(samples=3)
    assert result.status == "PASS"
    assert result.metrics["valid_count"] == 3


def test_disconnect_reconnect_is_detected_and_recovers(tmp_path):
    suite = RegressionSuite(make_validator(tmp_path))
    result = suite.disconnect_reconnect_recovery()
    assert result.status == "PASS"
    assert result.metrics["disconnect_detected"] is True
    assert result.metrics["recovered"] is True


def test_fault_injection_is_detected_and_recovers(tmp_path):
    suite = RegressionSuite(make_validator(tmp_path))
    result = suite.fault_injection_detection()
    assert result.status == "PASS"
    assert result.metrics["fault_detected"] is True
    assert result.metrics["recovered"] is True


def test_short_continuous_sampling_records_valid_samples(tmp_path):
    suite = RegressionSuite(make_validator(tmp_path), continuous_duration_seconds=0.03)
    result = suite.continuous_sampling_performance()
    assert result.status == "PASS"
    assert result.metrics["samples"] >= 1


def test_full_run_persists_dashboard_report(tmp_path):
    suite = RegressionSuite(make_validator(tmp_path), continuous_duration_seconds=0.01)
    run = suite.run_all()
    assert run["status"] == "PASS"
    saved = json.loads((tmp_path / "regression_runs.json").read_text())
    assert saved[0]["run_id"] == run["run_id"]
    assert saved[0]["quality_summary"]["release_ready"] is True


def test_smoke_suite_uses_traceable_test_plan(tmp_path):
    suite = RegressionSuite(make_validator(tmp_path), continuous_duration_seconds=0.01)
    run = suite.run("smoke")
    assert run["plan_id"] == "HWSW-VAL-001"
    assert [result["test_id"] for result in run["results"]] == ["VAL-001", "VAL-002"]
