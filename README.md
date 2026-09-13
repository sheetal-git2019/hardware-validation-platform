# Raspberry Pi Hardware/Software Validation Framework

[![Simulated validation](https://github.com/sheetal-git2019/hardware-validation-platform/actions/workflows/validation.yml/badge.svg)](https://github.com/sheetal-git2019/hardware-validation-platform/actions/workflows/validation.yml)

This package validates a DHT22 temperature/humidity sensor on a Raspberry Pi and provides an extensible path for other hardware modules. It is safe to develop on a laptop: the default `SimulatedDHT22` adapter produces realistic readings and exercises disconnect recovery without GPIO hardware. Pass `--hardware` only on the Pi connected to the physical device.

For a concise design overview and execution guide, see [Architecture](docs/ARCHITECTURE.md) and the [validation walkthrough](docs/VALIDATION_WALKTHROUGH.md).

## Architecture and coverage

`validation_framework/hardware/` contains hardware adapters behind a small `HardwareModule` contract: `initialize`, `verify_connectivity`, `read`, and `close`. `HardwareValidator` adds timestamps, error capture, normal/high-load/disconnect conditions, and durable logs. `RegressionSuite` applies acceptance rules, while `ResultStore` writes append-only JSONL, human-friendly CSV, and regression summaries. The Flask application consumes those same files; it has no access to GPIO and does not control equipment.

The root-level `test_plan.json` is the validation source of truth. Each case maps a stable test ID to a requirement, tags, priority, and whether it blocks release. This separates **what must be validated** from the Python implementation of **how it is validated**, which makes review and scope changes auditable.

Coverage provided by the automated suite:

| Case | Method | Expected outcome |
| --- | --- | --- |
| Connectivity | Initialize then read the sensor | Hardware answers a valid measurement |
| Data integrity | Five normal samples, values present and within -40–80 °C and 0–100 %RH | All readings pass |
| High load | CPU contention while continuous sampling runs | No invalid/missing readings; expected sample count reached |
| Disconnect/reconnect | Simulated cable/device loss then restoration; driver re-initialization on physical hardware | Error is logged, recovery measurement is valid |
| Endurance | High-load continuous sampling for 600 seconds | All samples valid and report is PASS |

The physical DHT22 path translates empty values and driver errors to a structured disconnected reading instead of allowing an unhandled exception to terminate the run. For physical cable testing, temporarily remove the sensor data connection during a running sampling command, restore it, and confirm the CSV/JSONL shows a `connected=false` record followed by a valid record. The included automated recovery test uses the simulation hook; physical reconnect remains an execution test because software cannot safely remove a wire.

## Setup

Use Python 3.10+ and a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On the Raspberry Pi, additionally install the DHT22 driver and connect data to GPIO4 (the default; change `gpio_pin` in `ValidationConfig` for another pin):

```bash
pip install adafruit-circuitpython-dht
```

Run a safe local smoke regression (the short duration is only for CI/development):

```powershell
python regression_run.py --duration 2 --interval 0.2
pytest -q
```

Run only the rapid release-blocking smoke suite, or select cases by plan tag:

```powershell
python regression_run.py --suite smoke --duration 10 --interval 1
python regression_run.py --suite regression --tag fault-injection --duration 1 --interval 0.1
```

The regression report captures the selected plan, quality summary, release-gate decision, Python/platform details, module name, sampling configuration, and Git revision when available. `SimulatedDHT22` also provides deterministic injected out-of-range and read-error faults so the framework can prove detection and recovery logic, not just happy-path sampling.

Run the release-duration, physical validation on the Pi:

```bash
python regression_run.py --hardware --duration 600 --interval 2
```

For an individual condition, use `validation_run.py`. `high_load` adds bounded CPU contention, and `simulated_disconnect` records unavailable readings when using the simulated adapter.

```powershell
python validation_run.py --condition normal --duration 60
python validation_run.py --condition high_load --duration 60
python validation_run.py --condition simulated_disconnect --duration 10
```

## Dashboard and artifacts

Start the dashboard after at least one collection or regression run:

```powershell
python dashboard.py
```

Open `http://<raspberry-pi-ip>:5000`. It refreshes every five seconds and shows the latest sensor values, a 100-sample trend, connection state, and the latest ten regression reports. Change the data location with `VALIDATION_DATA_DIR` when the dashboard needs to read a shared mounted directory.

| Artifact | Purpose |
| --- | --- |
| `data/readings.jsonl` | Append-only detailed evidence, one measurement per JSON record |
| `data/readings.csv` | Spreadsheet-compatible evidence |
| `data/regression_runs.json` | Run ID, case status, timestamps, details, and performance metrics |

## Execution procedure

1. Record Pi image version, Python version, sensor serial/lot, wiring, and ambient reference in the test record.
2. Run the automated unit tests and a simulated smoke run.
3. On target hardware, run the full `--hardware --duration 600` regression. Monitor the dashboard or JSONL file.
4. Perform the documented physical disconnect/reconnect step and attach the resulting log records to the test evidence.
5. Review range failures, errors, and sample count. Create defects for every unexpected observation; rerun all affected cases after a fix.

## Defect logging format

Use the following fields in the issue tracker so failures can be reproduced:

```json
{
  "defect_id": "HWVAL-123",
  "title": "DHT22 returns null humidity after reconnect",
  "severity": "major",
  "environment": {"pi_model": "Pi 4", "os_image": "...", "firmware": "...", "sensor_lot": "..."},
  "test_case": "disconnect_reconnect_recovery",
  "steps_to_reproduce": ["Run regression", "Disconnect data wire", "Reconnect"],
  "expected": "A valid reading is recovered and the test passes.",
  "actual": "Null humidity persisted for three samples.",
  "evidence": {"run_id": "...", "timestamps": ["..."], "log_file": "data/readings.jsonl"},
  "status": "open"
}
```

## Adding hardware

Implement the `HardwareModule` protocol in `validation_framework/hardware/`, return a dictionary of normalized metrics from `read`, and register a factory using `HardwareRegistry`. Add validation rules that understand the new metrics and corresponding simulated adapter tests. Existing logger, report, dashboard endpoints, and run lifecycle remain reusable.

## Continuous validation

The included GitHub Actions workflow runs unit tests and a simulated smoke regression for every push and pull request, then retains the generated log artifacts. It is deliberately simulation-only: physical Pi tests should run through a self-hosted lab runner after appropriate GPIO and equipment safety controls are in place.

## Portfolio demo narrative

This is intentionally a small hardware target used to demonstrate a scalable validation pattern: declarative requirements-to-test traceability, hardware abstraction, deterministic fault injection, high-load execution, structured evidence, release gates, and engineering visibility. In an interview, show `test_plan.json`, run the `smoke` suite, inject a fault, then open the dashboard and explain the release decision. Do not represent simulated readings as physical hardware evidence.

## Release readiness criteria

Release is ready only when the full 10-minute physical regression is PASS, no data-integrity/range failures occurred, physical reconnect recovery is documented as successful, all automated tests pass, and any open critical or major hardware-validation defects have an approved disposition. Archive the three generated data artifacts and environmental metadata with the release evidence.
