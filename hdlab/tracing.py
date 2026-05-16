"""Structured trace event bus for every public operation in the framework."""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from typing import Any, Callable, Iterator

import torch


def _describe(x: Any) -> Any:
    """Convert an object to a JSON-serializable descriptor."""
    if isinstance(x, torch.Tensor):
        return {"shape": list(x.shape), "dtype": str(x.dtype)}
    if isinstance(x, (list, tuple)):
        return [_describe(v) for v in x]
    if isinstance(x, dict):
        return {k: _describe(v) for k, v in x.items()}
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    return repr(x)


@dataclass
class TraceEvent:
    """A single op invocation recorded for replay and analysis."""

    step: int
    op: str
    inputs: dict[str, Any]
    output: Any
    modulator_state: dict[str, Any]
    timestamp_ns: int
    elapsed_ns: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class TraceBus:
    """Ring-buffer trace recorder, toggleable for overhead-free verification runs."""

    def __init__(self, enabled: bool = True, capacity: int = 100_000) -> None:
        self.enabled = enabled
        self.capacity = capacity
        self._buffer: list[TraceEvent] = []
        self._step = 0

    def emit(self, event: TraceEvent) -> None:
        if not self.enabled:
            return
        if len(self._buffer) >= self.capacity:
            self._buffer.pop(0)
        self._buffer.append(event)

    def flush(self) -> list[TraceEvent]:
        out = self._buffer
        self._buffer = []
        return out

    def next_step(self) -> int:
        self._step += 1
        return self._step


_current_bus: TraceBus | None = None
_state_provider: "Callable[[], dict[str, Any]]" = lambda: {}


def get_current_bus() -> TraceBus | None:
    return _current_bus


@contextmanager
def using(bus: TraceBus | None) -> Iterator[TraceBus | None]:
    """Set the active bus for the duration of the block."""
    global _current_bus
    old = _current_bus
    _current_bus = bus
    try:
        yield bus
    finally:
        _current_bus = old


def set_state_provider(fn: "Callable[[], dict[str, Any]]") -> None:
    """Register a callable that returns the current modulator state for each trace event."""
    global _state_provider
    _state_provider = fn


def emit(
    op: str,
    inputs: dict[str, Any],
    output: Any,
    elapsed_ns: int = 0,
) -> None:
    """Emit a TraceEvent to the current bus if one is active and enabled."""
    bus = _current_bus
    if bus is None or not bus.enabled:
        return
    if isinstance(output, torch.Tensor):
        out_desc: Any = {"shape": list(output.shape), "dtype": str(output.dtype)}
    elif output is None or isinstance(output, (str, int, float, bool)):
        out_desc = output
    else:
        out_desc = _describe(output)
    event = TraceEvent(
        step=bus.next_step(),
        op=op,
        inputs=inputs,
        output=out_desc,
        modulator_state=_state_provider(),
        timestamp_ns=time.perf_counter_ns(),
        elapsed_ns=elapsed_ns,
    )
    bus.emit(event)
