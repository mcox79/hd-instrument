"""Structured trace event bus for every public operation in the framework."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TraceEvent:
    """A single op invocation recorded for replay and analysis."""

    step: int
    op: str
    inputs: dict[str, Any]
    output: Any
    modulator_state: dict[str, float]
    timestamp_ns: int


class TraceBus:
    """Ring-buffer trace recorder, toggleable for overhead-free verification runs."""

    def __init__(self, enabled: bool = True, capacity: int = 100_000) -> None:
        raise NotImplementedError("Week 1")

    def emit(self, event: TraceEvent) -> None:
        """Record one op invocation."""
        raise NotImplementedError("Week 1")

    def flush(self) -> list[TraceEvent]:
        """Drain the buffer."""
        raise NotImplementedError("Week 1")
