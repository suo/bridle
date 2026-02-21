# test-harness

A crash-resilient pytest subprocess harness that collects structured test results as JSONL and uploads them to pluggable backends. Designed for CI, with rich formatted output and exit code passthrough.

## Features

- **Crash resilience** — pytest runs in a subprocess; results are flushed to disk after every test. Even if the subprocess segfaults or OOMs, the harness reads whatever was written.
- **Structured JSONL output** — one JSON object per test with node ID, outcome, duration, timestamp, and failure details.
- **Pluggable backends** — results are dispatched to a backend for upload. Ships with a `stub` backend; add your own by subclassing `Backend`.
- **Rich console output** — summary table with outcome counts and duration, plus detailed failure panels, all printed to stderr.
- **Exit code passthrough** — the harness returns the subprocess exit code so CI can gate on it.

## Installation

Requires Python 3.13+.

```
uv sync
```

## Usage

```
test-harness <pytest args> [--backend <name>]
```

All arguments except `--backend` are forwarded to pytest:

```
# Run tests in a directory
test-harness tests/

# Run with a specific backend
test-harness tests/ --backend stub

# Pass pytest flags through
test-harness tests/ -k "test_login" -x --tb=short

# Via python -m
python -m test_harness tests/ --backend stub
```

## JSONL Schema

Each test produces one line:

```json
{"node_id":"tests/test_a.py::test_ok","outcome":"passed","duration_seconds":0.005,"timestamp":"2026-01-01T00:00:00+00:00","longrepr":null,"worker":null}
```

| Field              | Type             | Description                                      |
|--------------------|------------------|--------------------------------------------------|
| `node_id`          | `string`         | Pytest node ID                                   |
| `outcome`          | `string`         | `passed`, `failed`, `skipped`, `error`, `xfailed`, `xpassed` |
| `duration_seconds` | `float`          | Test duration in seconds                         |
| `timestamp`        | `string`         | ISO 8601 timestamp (UTC)                         |
| `longrepr`         | `string \| null` | Failure representation, null on pass             |
| `worker`           | `string \| null` | Reserved for future xdist support                |

## Adding a Backend

Subclass `Backend` and register it in `backends/__init__.py`:

```python
from test_harness.backends._base import Backend
from test_harness._schema import TestResult

class MyBackend(Backend):
    def name(self) -> str:
        return "my-backend"

    def upload(self, results: list[TestResult]) -> None:
        # upload logic here
        ...
```

Then add it to the registry in `backends/__init__.py`:

```python
_REGISTRY: dict[str, type[Backend]] = {
    "stub": StubBackend,
    "my-backend": MyBackend,
}
```

## Development

```
# Install dev dependencies
uv sync

# Run tests
uv run pytest tests/

# Update syrupy snapshots
uv run pytest tests/ --snapshot-update
```

## Project Structure

```
src/test_harness/
├── __init__.py          # main() entrypoint
├── __main__.py          # python -m support
├── _schema.py           # TestResult dataclass + Outcome enum + JSONL ser/de
├── _plugin.py           # TestResultPlugin (pytest plugin, flush-per-line)
├── _runner.py           # Subprocess entry point
├── _harness.py          # Orchestrator: argparse, subprocess, read results, dispatch
├── _console.py          # Rich-formatted output helpers
└── backends/
    ├── __init__.py      # Registry + get_backend()
    ├── _base.py         # Abstract Backend base class
    └── _stub.py         # StubBackend (logs to console)
```
