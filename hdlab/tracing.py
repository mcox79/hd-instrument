"""Structured trace event bus for every public operation in the framework.

Two layers:
- Operator-level events (binding.bind, learning.update, etc.) emitted by hdlab modules.
- Semantic events (hdlab.semantic) emitted by higher-level multi-hop logic.

A `query_span(query_id, ...)` context manager stamps every event inside its scope
with the same query_id, so a multi-hop query forms one inspectable group across both layers.
"""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
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
    query_id: str | None = None
    tags: dict[str, Any] = field(default_factory=dict)

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
_current_query_id: str | None = None
_current_query_tags: dict[str, Any] = {}


def get_current_bus() -> TraceBus | None:
    return _current_bus


def current_query_id() -> str | None:
    """Return the active query span id, or None if no span is open."""
    return _current_query_id


def current_query_tags() -> dict[str, Any]:
    """Return the active query span tags (copy)."""
    return dict(_current_query_tags)


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


@contextmanager
def query_span(query_id: str, **tags: Any) -> Iterator[str]:
    """Open a logical-query span; every event emitted inside inherits this query_id.

    Use tags to record query kind, source, target relation, hop budget, etc.
    Emits semantic.query_start at entry and semantic.query_end at exit.
    """
    global _current_query_id, _current_query_tags
    old_id, old_tags = _current_query_id, _current_query_tags
    _current_query_id = query_id
    _current_query_tags = dict(tags)
    emit("semantic.query_start", {"query_id": query_id, **tags}, None)
    try:
        yield query_id
    finally:
        emit("semantic.query_end", {"query_id": query_id}, None)
        _current_query_id, _current_query_tags = old_id, old_tags


def set_state_provider(fn: "Callable[[], dict[str, Any]]") -> None:
    """Register a callable that returns the current modulator state for each trace event."""
    global _state_provider
    _state_provider = fn


def emit(
    op: str,
    inputs: dict[str, Any],
    output: Any,
    elapsed_ns: int = 0,
    tags: dict[str, Any] | None = None,
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
    merged_tags: dict[str, Any] = dict(_current_query_tags)
    if tags:
        merged_tags.update(tags)
    event = TraceEvent(
        step=bus.next_step(),
        op=op,
        inputs=inputs,
        output=out_desc,
        modulator_state=_state_provider(),
        timestamp_ns=time.perf_counter_ns(),
        elapsed_ns=elapsed_ns,
        query_id=_current_query_id,
        tags=merged_tags,
    )
    bus.emit(event)
