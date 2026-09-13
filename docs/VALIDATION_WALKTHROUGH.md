# Validation Walkthrough

This walkthrough demonstrates the intended validation workflow: traceability, focused execution, negative testing, evidence review, and release assessment.

## Review validation intent

Open `test_plan.json` and review the planned coverage:

- `VAL-001` / `REQ-SENS-001`: data integrity, P0, release blocking.
- `VAL-002` / `REQ-REC-001`: recovery behavior, P0, release blocking.
- `VAL-003` / `REQ-PERF-001`: continuous sampling under load.
- `VAL-004` / `REQ-QUAL-001`: negative fault-injection coverage.

The test plan makes the release decision reviewable: requirements, priorities, tags, and blocking rules are explicit rather than buried in test implementation.

## Execute a rapid smoke suite

```powershell
python regression_run.py --suite smoke --duration 10 --interval 1
```

Expected outcome: `VAL-001` and `VAL-002` pass, with a release-ready quality summary.

## Verify negative-test behavior

```powershell
python regression_run.py --suite regression --tag fault-injection --duration 1 --interval 0.1
```

The simulator deliberately returns out-of-range data. The run passes only when the framework identifies the bad measurement and verifies recovery. A passing result proves the detection logic, not acceptance of the injected data.

## Execute and review regression evidence

```powershell
python regression_run.py --suite regression --duration 60 --interval 2
python dashboard.py
```

Open `http://localhost:5000` and review:

- **Release gate**: `READY` only if blocking cases pass.
- **Pass rate** and failed/skipped case counts.
- Test IDs in the regression table.
- Timestamped JSONL/CSV measurement evidence and JSON report.
- Environment and sampling configuration captured in the report.

## Extension model

The same test engine can run against a physical DHT22 on a Raspberry Pi or a simulated device in CI. A new device needs an adapter that implements initialize, connectivity verification, read, and close; the logging, reporting, test-plan model, and release gate remain reusable.

## Common review questions

| Question | Response |
| --- | --- |
| Is this actual silicon validation? | No. It is a small, honest demonstration of validation infrastructure patterns. The physical adapter is ready for a Pi/DHT22; the current evidence is simulated. |
| How would it scale? | Separate test plans by platform, add resource locks and lab runners, persist results centrally, and use CI to select smoke versus overnight suites. |
| Why simulation? | It makes fault paths deterministic and makes every code change testable without equipment availability. Hardware runs then validate the adapter, board, and system behavior. |
| What is the release criterion? | No failing release-blocking case; each report records the exact plan, execution environment, configuration, metrics, and evidence. |
