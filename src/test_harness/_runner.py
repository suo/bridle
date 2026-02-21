"""Subprocess entry point: python -m test_harness._runner <pytest args...>

This module is invoked by the harness in a subprocess. The TEST_HARNESS_RESULTS_FILE
env var must already be set so that the plugin auto-registers via pytest_configure.
"""
from __future__ import annotations

import sys

import pytest


def main() -> int:
    # Forward all argv (minus the module name) to pytest.
    return pytest.main(sys.argv[1:], plugins=[])


if __name__ == "__main__":
    sys.exit(main())
