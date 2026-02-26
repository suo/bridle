from __future__ import annotations

from test_harness.backends._base import Backend
from test_harness.backends._buildkite import BuildkiteBackend
from test_harness.backends._stub import StubBackend

_REGISTRY: dict[str, type[Backend]] = {
    "stub": StubBackend,
    "buildkite": BuildkiteBackend,
}


def get_backend(name: str) -> Backend:
    """Look up and instantiate a backend by name."""
    cls = _REGISTRY.get(name)
    if cls is None:
        available = ", ".join(sorted(_REGISTRY))
        raise ValueError(
            f"Unknown backend {name!r}. Available backends: {available}"
        )
    return cls()


__all__ = ["Backend", "BuildkiteBackend", "StubBackend", "get_backend"]
