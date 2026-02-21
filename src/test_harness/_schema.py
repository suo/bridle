from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Self

logger = logging.getLogger(__name__)


class Outcome(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    XFAILED = "xfailed"
    XPASSED = "xpassed"


@dataclass(frozen=True, slots=True)
class TestResult:
    node_id: str
    outcome: Outcome
    duration_seconds: float
    timestamp: datetime
    longrepr: str | None = None
    worker: str | None = None

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "outcome": self.outcome.value,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat(),
            "longrepr": self.longrepr,
            "worker": self.worker,
        }

    def to_json_line(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            node_id=data["node_id"],
            outcome=Outcome(data["outcome"]),
            duration_seconds=data["duration_seconds"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            longrepr=data.get("longrepr"),
            worker=data.get("worker"),
        )

    @classmethod
    def from_json_line(cls, line: str) -> Self:
        return cls.from_dict(json.loads(line))


def read_results(path: Path) -> list[TestResult]:
    """Read JSONL results file, skipping malformed/truncated lines."""
    results: list[TestResult] = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return results

    for lineno, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            results.append(TestResult.from_json_line(line))
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.warning("Skipping malformed line %d: %s", lineno, exc)

    return results
