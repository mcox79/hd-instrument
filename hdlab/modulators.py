"""Named scalar control variables wired to specific substrate operations."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator

from . import tracing


@dataclass
class ModulatorState:
    """Five named scalars, each gating a specific op. Snapshotted on every trace event."""

    attention: float = 0.0  # cleanup threshold (ACh-like). 0 = accept anything; higher = stricter.
    reward: float = 0.0  # Hebbian update sign/gain (DA-like). Used in Week 3.
    arousal: float = 1.0  # global plasticity rate (NE-like). Used in Week 3.
    recency: float = 0.0  # bundling weight on new items (5-HT-like). 0 = uniform; 1 = newest only.
    gating: dict[str, float] = field(default_factory=dict)  # per-module mask (GABA-like).


_current_state = ModulatorState()


def current() -> ModulatorState:
    """Return the live ModulatorState (mutating it mutates the global)."""
    return _current_state


def reset() -> None:
    """Reset all modulators to their default values."""
    global _current_state
    _current_state = ModulatorState()


def set_attention(value: float) -> None:
    _current_state.attention = float(value)
    tracing.emit("modulators.set_attention", {"value": float(value)}, None)


def set_reward(value: float) -> None:
    _current_state.reward = float(value)
    tracing.emit("modulators.set_reward", {"value": float(value)}, None)


def set_arousal(value: float) -> None:
    _current_state.arousal = float(value)
    tracing.emit("modulators.set_arousal", {"value": float(value)}, None)


def set_recency(value: float) -> None:
    _current_state.recency = float(value)
    tracing.emit("modulators.set_recency", {"value": float(value)}, None)


def set_gating(module: str, value: float) -> None:
    _current_state.gating[module] = float(value)
    tracing.emit("modulators.set_gating", {"module": module, "value": float(value)}, None)


@contextmanager
def using(**overrides: Any) -> Iterator[ModulatorState]:
    """Temporarily override modulator values for the duration of the block."""
    global _current_state
    old = _current_state
    new = ModulatorState(
        attention=float(overrides.get("attention", old.attention)),
        reward=float(overrides.get("reward", old.reward)),
        arousal=float(overrides.get("arousal", old.arousal)),
        recency=float(overrides.get("recency", old.recency)),
        gating=dict(overrides["gating"]) if "gating" in overrides else dict(old.gating),
    )
    _current_state = new
    try:
        yield new
    finally:
        _current_state = old


def _provide_state() -> dict[str, Any]:
    """State snapshot for trace events. Registered with tracing on import."""
    s = _current_state
    return {
        "attention": s.attention,
        "reward": s.reward,
        "arousal": s.arousal,
        "recency": s.recency,
        "gating": dict(s.gating),
    }


tracing.set_state_provider(_provide_state)
