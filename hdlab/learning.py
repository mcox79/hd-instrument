"""Reward-modulated Hebbian learning over a sparse atom-association matrix.

Update rule:  W[t+1] = (1 - decay) * W[t] + arousal * reward    (for co-active pairs)
              W[t+1] = (1 - decay) * W[t]                       (otherwise)

Stored sparsely; decay is applied lazily on read so cost per step is O(active_pairs).
"""

from __future__ import annotations

import time

from . import modulators, tracing
from .modulators import ModulatorState


class HebbianAssociations:
    """Sparse co-activation weights between atoms, modulated by reward and arousal."""

    def __init__(self, decay: float = 1e-3) -> None:
        if not 0.0 <= decay < 1.0:
            raise ValueError(f"decay must be in [0, 1), got {decay}")
        self.decay = float(decay)
        self._weights: dict[tuple[str, str], float] = {}
        self._last_step: dict[tuple[str, str], int] = {}
        self._step = 0

    def __len__(self) -> int:
        return len(self._weights)

    @property
    def step(self) -> int:
        return self._step

    @staticmethod
    def _key(a: str, b: str) -> tuple[str, str]:
        return (a, b) if a <= b else (b, a)

    def _read(self, key: tuple[str, str]) -> float:
        if key not in self._weights:
            return 0.0
        elapsed = self._step - self._last_step[key]
        return self._weights[key] * ((1.0 - self.decay) ** elapsed)

    def weight(self, a: str, b: str) -> float:
        """Current association strength between atoms a and b (decay applied lazily)."""
        return self._read(self._key(a, b))

    def set_weight(self, a: str, b: str, value: float, at_step: int) -> None:
        """Direct weight assignment, used by replay-from-trace reconstruction."""
        key = self._key(a, b)
        self._weights[key] = float(value)
        self._last_step[key] = int(at_step)
        if at_step > self._step:
            self._step = int(at_step)

    def update(
        self,
        active_atoms: list[str],
        state: ModulatorState | None = None,
    ) -> None:
        """Advance one Hebbian step; reinforce all co-active pairs by arousal * reward."""
        if state is None:
            state = modulators.current()
        self._step += 1
        if state.reward == 0.0 or state.arousal == 0.0 or len(active_atoms) < 2:
            return
        delta = state.arousal * state.reward
        n = len(active_atoms)
        for i in range(n):
            for j in range(i + 1, n):
                t0 = time.perf_counter_ns()
                key = self._key(active_atoms[i], active_atoms[j])
                current = self._read(key)
                new_value = current + delta
                self._weights[key] = new_value
                self._last_step[key] = self._step
                tracing.emit(
                    "learning.update",
                    {
                        "a": key[0],
                        "b": key[1],
                        "delta": delta,
                        "hebbian_step": self._step,
                    },
                    {"weight": new_value},
                    elapsed_ns=time.perf_counter_ns() - t0,
                )
