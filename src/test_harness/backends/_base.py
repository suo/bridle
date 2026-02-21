from __future__ import annotations

from abc import ABC, abstractmethod

from test_harness._schema import TestResult


class Backend(ABC):
    """Abstract base class for test result upload backends."""

    @abstractmethod
    def upload(self, results: list[TestResult]) -> None:
        """Upload test results to the backend."""

    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this backend."""
