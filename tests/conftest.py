from __future__ import annotations

from datetime import datetime, timezone

import pytest

from test_harness._schema import Outcome, TestResult

pytest_plugins = ["pytester"]

# Deterministic timestamp for snapshot tests.
FIXED_TS = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


@pytest.fixture()
def sample_results() -> list[TestResult]:
    return [
        TestResult(
            node_id="tests/test_a.py::test_ok",
            outcome=Outcome.PASSED,
            duration_seconds=0.005,
            timestamp=FIXED_TS,
        ),
        TestResult(
            node_id="tests/test_a.py::test_fail",
            outcome=Outcome.FAILED,
            duration_seconds=0.123,
            timestamp=FIXED_TS,
            longrepr="assert 1 == 2",
        ),
        TestResult(
            node_id="tests/test_a.py::test_skip",
            outcome=Outcome.SKIPPED,
            duration_seconds=0.0,
            timestamp=FIXED_TS,
        ),
    ]
