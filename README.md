# test-harness

A harness for running pytest. It handles the collection and upload of test result information in a way that is resilient to crashes/OOMs in the code under test.

## Features

- **Crash resilience** — pytest runs in a subprocess; results are flushed to disk after every test. Even if the subprocess segfaults or OOMs, the harness reads whatever was written.
- **Pluggable backends** — can register one or more backends to upload test results to.
- **Rich console output** — summary table with outcome counts and duration, plus detailed failure panels, all printed to stderr.
- **Exit code passthrough** — the harness returns the subprocess exit code so CI can gate on it.

## JSONL Schema

Each test produces one line. The schema mirrors `pytest.TestReport` fields:

```json
{"nodeid":"tests/test_a.py::test_ok","outcome":"passed","when":"call","duration":0.005,"start":1735689600.0,"stop":1735689600.005,"location":["tests/test_a.py",0,"test_ok"],"longrepr":null,"sections":null,"wasxfail":null}
```

| Field      | Type                          | Description                                                      |
|------------|-------------------------------|------------------------------------------------------------------|
| `nodeid`   | `string`                      | Pytest node ID                                                   |
| `outcome`  | `string`                      | `passed`, `failed`, `skipped`, `error`, `xfailed`, `xpassed`    |
| `when`     | `string`                      | Phase: `setup`, `call`, or `teardown`                            |
| `duration` | `float`                       | Test duration in seconds                                         |
| `start`    | `float`                       | Epoch timestamp when the phase started                           |
| `stop`     | `float`                       | Epoch timestamp when the phase ended                             |
| `location` | `[string, int\|null, string]` | `[filepath, lineno, domain]`, or null                            |
| `longrepr` | `string \| null`              | Failure representation, null on pass                             |
| `sections` | `[[string, string]] \| null`  | Captured output sections, e.g. `[["Captured stdout call", "..."]]` |
| `wasxfail` | `string \| null`              | xfail reason if the test was marked xfail                        |

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
