from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TestDefinition:
    key: str
    id: str
    requirement: str
    title: str
    tags: tuple[str, ...]
    priority: str
    release_blocking: bool


class TestPlan:
    """Declarative, traceable definition of what the regression executes."""

    def __init__(self, plan_id: str, title: str, release_gate: str, tests: list[TestDefinition]) -> None:
        self.plan_id = plan_id
        self.title = title
        self.release_gate = release_gate
        self.tests = tests
        self._by_key = {test.key: test for test in tests}

    @classmethod
    def load(cls, path: Path | None = None) -> "TestPlan":
        plan_path = path or Path(__file__).resolve().parents[1] / "test_plan.json"
        raw = json.loads(plan_path.read_text(encoding="utf-8"))
        tests = [TestDefinition(
            key=item["key"], id=item["id"], requirement=item["requirement"], title=item["title"],
            tags=tuple(item["tags"]), priority=item["priority"], release_blocking=item["release_blocking"],
        ) for item in raw["tests"]]
        return cls(raw["plan_id"], raw["title"], raw["release_gate"], tests)

    def get(self, key: str) -> TestDefinition:
        return self._by_key[key]

    def select(self, suite: str = "regression", tags: tuple[str, ...] = ()) -> list[TestDefinition]:
        selected = [test for test in self.tests if suite in test.tags]
        if tags:
            selected = [test for test in selected if set(tags).issubset(test.tags)]
        return selected
