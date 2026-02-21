from __future__ import annotations

from test_harness.backends._base import Backend
from test_harness.backends._stub import StubBackend

_REGISTRY: dict[str, type[Backend]] = {
    "stub": StubBackend,
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


__all__ = ["Backend", "StubBackend", "get_backend"]
