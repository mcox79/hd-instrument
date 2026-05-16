"""Per-op latency, FLOPs, and memory-access profiling for hardware-substrate analysis."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def profile(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that records wall time, FLOPs, and access pattern on every call."""
    raise NotImplementedError("Week 4")
