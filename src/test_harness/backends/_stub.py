from __future__ import annotations

import sys

from rich.console import Console

from test_harness._schema import TestResult
from test_harness.backends._base import Backend


class StubBackend(Backend):
    """Stub backend that logs results to stderr instead of uploading."""

    def name(self) -> str:
        return "stub"

    def upload(self, results: list[TestResult]) -> None:
        console = Console(stderr=True)
        console.print(
            f"[dim]StubBackend: would upload {len(results)} result(s)[/dim]"
        )
