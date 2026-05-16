"""Reward-modulated Hebbian learning over a sparse atom-association matrix."""

from __future__ import annotations

from .modulators import ModulatorState


class HebbianAssociations:
    """Sparse co-activation weights between atoms, modulated by reward and arousal."""

    def __init__(self, decay: float = 1e-3) -> None:
        raise NotImplementedError("Week 3")

    def update(
        self,
        active_atoms: list[str],
        modulators: ModulatorState,
    ) -> None:
        """Apply reward-modulated Hebbian update across pairwise co-active atoms."""
        raise NotImplementedError("Week 3")

    def weight(self, a: str, b: str) -> float:
        """Current association strength between atoms a and b."""
        raise NotImplementedError("Week 3")
