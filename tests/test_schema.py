from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from syrupy.assertion import SnapshotAssertion

from test_harness._schema import Outcome, TestResult, read_results

FIXED_TS = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


class TestTestResult:
    def test_to_json_line_snapshot(
        self, sample_results: list[TestResult], snapshot: SnapshotAssertion
    ) -> None:
        for result in sample_results:
            assert result.to_json_line() == snapshot

    def test_roundtrip(self, sample_results: list[TestResult]) -> None:
        for result in sample_results:
            line = result.to_json_line()
            restored = TestResult.from_json_line(line)
            assert restored == result

    def test_to_dict_keys(self) -> None:
        result = TestResult(
            node_id="t::x",
            outcome=Outcome.PASSED,
            duration_seconds=0.0,
            timestamp=FIXED_TS,
        )
        d = result.to_dict()
        assert set(d.keys()) == {
            "node_id",
            "outcome",
            "duration_seconds",
            "timestamp",
            "longrepr",
            "worker",
        }
        assert d["longrepr"] is None
        assert d["worker"] is None

    def test_outcome_values(self) -> None:
        assert Outcome.PASSED.value == "passed"
        assert Outcome.XPASSED.value == "xpassed"


class TestReadResults:
    def test_reads_valid_jsonl(self, tmp_path) -> None:
        f = tmp_path / "results.jsonl"
        r = TestResult(
            node_id="t::a",
            outcome=Outcome.PASSED,
            duration_seconds=0.001,
            timestamp=FIXED_TS,
        )
        f.write_text(r.to_json_line() + "\n")
        results = read_results(f)
        assert len(results) == 1
        assert results[0] == r

    def test_skips_malformed_lines(self, tmp_path) -> None:
        f = tmp_path / "results.jsonl"
        r = TestResult(
            node_id="t::a",
            outcome=Outcome.PASSED,
            duration_seconds=0.001,
            timestamp=FIXED_TS,
        )
        content = r.to_json_line() + "\n" + "NOT JSON\n" + '{"truncated": true}\n'
        f.write_text(content)
        results = read_results(f)
        assert len(results) == 1

    def test_missing_file(self, tmp_path) -> None:
        results = read_results(tmp_path / "nonexistent.jsonl")
        assert results == []

    def test_empty_file(self, tmp_path) -> None:
        f = tmp_path / "results.jsonl"
        f.write_text("")
        results = read_results(f)
        assert results == []
