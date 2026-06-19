"""Timestamped connection-state snapshots: Hebbian weights, modulator state, ablations.

Snapshots are emitted as semantic.snapshot trace events so they live in the same store
as the rest of the trace and can be replayed alongside it. Use at hop boundaries or at
the start/end of a query span to produce diffable state.
"""

from __future__ import annotations

from typing import Any

from . import ablation, modulators, tracing


def _hebbian_dump(h: Any) -> dict[str, float]:
    """Extract the current weight dict from a HebbianAssociations instance."""
    if not hasattr(h, "_weights"):
        return {}
    out: dict[str, float] = {}
    for (a, b), w in h._weights.items():
        out[f"{a}|{b}"] = float(h.weight(a, b))  # apply lazy decay
    return out


def capture(label: str, hebbian: Any = None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Capture a snapshot of connection state and emit semantic.snapshot.

    Returns the captured payload so callers can also use it directly.
    """
    payload: dict[str, Any] = {
        "label": label,
        "modulator_state": _modulator_state(),
        "ablations": ablation.active(),
    }
    if hebbian is not None:
        payload["hebbian_weights"] = _hebbian_dump(hebbian)
        payload["hebbian_step"] = int(getattr(hebbian, "step", 0))
    if extra:
        payload["extra"] = extra
    tracing.emit("semantic.snapshot", {"label": label}, payload)
    return payload


def _modulator_state() -> dict[str, Any]:
    s = modulators.current()
    return {
        "attention": s.attention,
        "reward": s.reward,
        "arousal": s.arousal,
        "recency": s.recency,
        "gating": dict(s.gating),
    }
