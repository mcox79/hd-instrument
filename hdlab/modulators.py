"""Named scalar control variables wired to specific substrate operations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ModulatorState:
    """Five named scalars, each gating a specific op. Snapshotted on every trace event."""

    attention: float = 0.5  # cleanup threshold (ACh-like)
    reward: float = 0.0  # Hebbian update sign/gain (DA-like)
    arousal: float = 1.0  # global plasticity rate (NE-like)
    recency: float = 0.5  # bundling weight on new items (5-HT-like)
    gating: dict[str, float] = field(default_factory=dict)  # per-module mask (GABA-like)
