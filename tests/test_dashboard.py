from __future__ import annotations

from dashboard import create_app
from validation_framework.storage import ResultStore


def test_dashboard_api_returns_logged_data(tmp_path):
    store = ResultStore(tmp_path)
    store.log_reading({"timestamp": "2026-01-01T00:00:00+00:00", "sensor": "dht22", "condition": "normal", "temperature_c": 25.0, "humidity_percent": 50.0, "connected": True, "error": None})
    store.save_regression_run({"run_id": "test", "status": "PASS", "started_at": "x", "finished_at": "2026-01-01T00:00:01+00:00", "results": []})
    client = create_app(tmp_path).test_client()
    assert client.get("/").status_code == 200
    assert client.get("/api/readings").get_json()[0]["temperature_c"] == 25.0
    assert client.get("/api/regressions").get_json()[0]["status"] == "PASS"
