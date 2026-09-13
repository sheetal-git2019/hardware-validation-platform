"""Flask dashboard for latest sensor data, trends, and regression status."""
from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, render_template

from validation_framework.storage import ResultStore


def create_app(data_dir: Path | None = None) -> Flask:
    app = Flask(__name__)
    store = ResultStore(data_dir or Path(os.environ.get("VALIDATION_DATA_DIR", "data")))

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/readings")
    def readings():
        return jsonify(store.load_readings())

    @app.get("/api/regressions")
    def regressions():
        return jsonify(store.load_regression_runs())

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)
