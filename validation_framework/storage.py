from __future__ import annotations

import csv
import json
from pathlib import Path
from threading import Lock
from typing import Any


class ResultStore:
    """Appends readings to JSONL/CSV and keeps regression summaries in JSON."""

    reading_columns = ["timestamp", "sensor", "condition", "temperature_c", "humidity_percent", "connected", "error"]

    def __init__(self, data_dir: Path) -> None:
        data_dir.mkdir(parents=True, exist_ok=True)
        self.readings_jsonl = data_dir / "readings.jsonl"
        self.readings_csv = data_dir / "readings.csv"
        self.regressions_json = data_dir / "regression_runs.json"
        self._lock = Lock()

    def log_reading(self, reading: dict[str, Any]) -> None:
        with self._lock:
            with self.readings_jsonl.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(reading, separators=(",", ":")) + "\n")
            new_file = not self.readings_csv.exists()
            with self.readings_csv.open("a", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=self.reading_columns)
                if new_file:
                    writer.writeheader()
                writer.writerow({key: reading.get(key) for key in self.reading_columns})

    def save_regression_run(self, run: dict[str, Any]) -> None:
        with self._lock:
            runs = self.load_regression_runs()
            runs.append(run)
            self.regressions_json.write_text(json.dumps(runs, indent=2), encoding="utf-8")

    def load_readings(self, limit: int = 300) -> list[dict[str, Any]]:
        if not self.readings_jsonl.exists():
            return []
        lines = self.readings_jsonl.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(line) for line in lines]

    def load_regression_runs(self) -> list[dict[str, Any]]:
        if not self.regressions_json.exists():
            return []
        return json.loads(self.regressions_json.read_text(encoding="utf-8"))
