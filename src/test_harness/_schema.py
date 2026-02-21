from __future__ import annotations

import json
import logging
from dataclasses import dataclass
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
    nodeid: str
    outcome: Outcome
    when: str
    duration: float
    start: float
    stop: float
    location: tuple[str, int | None, str] | None = None
    longrepr: str | None = None
    sections: list[tuple[str, str]] | None = None
    wasxfail: str | None = None

    def to_dict(self) -> dict:
        return {
            "nodeid": self.nodeid,
            "outcome": self.outcome.value,
            "when": self.when,
            "duration": self.duration,
            "start": self.start,
            "stop": self.stop,
            "location": list(self.location) if self.location is not None else None,
            "longrepr": self.longrepr,
            "sections": [list(s) for s in self.sections]
            if self.sections is not None
            else None,
            "wasxfail": self.wasxfail,
        }

    def to_json_line(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        location = data.get("location")
        if location is not None:
            location = (location[0], location[1], location[2])
        sections = data.get("sections")
        if sections is not None:
            sections = [(s[0], s[1]) for s in sections]
        return cls(
            nodeid=data["nodeid"],
            outcome=Outcome(data["outcome"]),
            when=data["when"],
            duration=data["duration"],
            start=data["start"],
            stop=data["stop"],
            location=location,
            longrepr=data.get("longrepr"),
            sections=sections,
            wasxfail=data.get("wasxfail"),
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
