# Five-Minute Interview Demo

## Opening: 30 seconds

> I used a small sensor target to rebuild an embedded validation workflow as a modern, repeatable platform. The point is not the DHT22 itself; it is the system of traceable requirements, fault injection, automated regression, evidence capture, and release decisions.

Show [the architecture](ARCHITECTURE.md). Explain that `test_plan.json` separates validation intent from implementation.

## Demonstrate traceability: 45 seconds

Open `test_plan.json` and point to:

- `VAL-001` / `REQ-SENS-001`: data integrity, P0, release blocking.
- `VAL-002` / `REQ-REC-001`: recovery behavior, P0, release blocking.
- `VAL-003` / `REQ-PERF-001`: continuous sampling under load.
- `VAL-004` / `REQ-QUAL-001`: negative fault-injection coverage.

Say: “A release decision uses explicit blocking rules, not an informal reading of a console log.”

## Run a rapid smoke suite: 45 seconds

```powershell
python regression_run.py --suite smoke --duration 10 --interval 1
```

Expected outcome: `VAL-001` and `VAL-002` pass, with a release-ready quality summary.

## Prove negative testing: 45 seconds

```powershell
python regression_run.py --suite regression --tag fault-injection --duration 1 --interval 0.1
```

Explain: “The simulator deliberately returns out-of-range data. The run passes only because the framework identifies the bad measurement and verifies recovery. A passing test here proves detection behavior, not that the injected data was acceptable.”

## Show release evidence: 60 seconds

```powershell
python regression_run.py --suite regression --duration 60 --interval 2
python dashboard.py
```

Open `http://localhost:5000` and show the latest run. Call out:

- **Release gate**: `READY` only if blocking cases pass.
- **Pass rate** and failed/skipped case counts.
- Test IDs in the regression table.
- Timestamped JSONL/CSV measurement evidence and JSON report.
- Environment and sampling configuration captured in the report.

## Close: 30 seconds

> The same test engine can run against a physical DHT22 on a Raspberry Pi or a simulated device in CI. A new device needs an adapter that implements initialize, connectivity verification, read, and close; the logging, reporting, test-plan model, and release gate remain reusable.

## Questions to anticipate

| Question | Concise response |
| --- | --- |
| Is this actual silicon validation? | No. It is a small, honest demonstration of validation infrastructure patterns. The physical adapter is ready for a Pi/DHT22; the current evidence is simulated. |
| How would it scale? | Separate test plans by platform, add resource locks and lab runners, persist results centrally, and use CI to select smoke versus overnight suites. |
| Why simulation? | It makes fault paths deterministic and makes every code change testable without equipment availability. Hardware runs then validate the adapter, board, and system behavior. |
| What is the release criterion? | No failing release-blocking case; each report records the exact plan, execution environment, configuration, metrics, and evidence. |
