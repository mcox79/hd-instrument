"""Transitive-comparison ordering -- the FIRST glass-box REASONING primitive.

Landed 2026-08-28 from the integrated `transitive_comparison_reasoning_over_the_magnitude_ordering`
(SOLVED/EXCELLENT, owner-DONE; witness verification/test_transitive_ordering_reasoning.py). Reads pairwise
comparisons (A > B, B > C), INTEGRATES them into ONE magnitude ordering, and answers the UN-STATED pair (A vs C)
by a native read-out -- NOT a symbolic sort.

Brain mechanism (PINNED, copied): relational integration by a DELTA-RULE / value-transfer settling (Frank, Rudy &
O'Reilly 2003; Dusek & Eichenbaum hippocampal relational memory) -- the Bradley-Terry ML gradient. Overlapping
premises couple through their shared middle term, so the stated adjacent comparisons settle into one integrated scalar
ordering. Items are then placed on a BOUNDED parietal MAGNITUDE LINE (Zorzi/Dehaene; working-memory span is bounded)
and each item is bound to its magnitude PLACE CODE via fractional-power encoding (the p1 ruler's FPE), superposed into
one FHRR register `S = sum_i bind(item_key_i, FPE(scale * x_i))`. An un-stated pair is answered by unbinding each
item's key, decoding its coordinate off the FPE grid (the native resonator read-out), and comparing -- so the answer
to A vs C is READ off the integrated line, never chained.

OUR-INVENTION-UNDER-TEST (swept, not adopted): eta / epochs / temp (settling), FPE sigma, pos_scale (the line's
half-range -- bounded to keep coordinates in the FPE faithful regime; an unbounded Bradley-Terry chain phase-aliases
the code). The distance effect + end-anchor effect emerge from read-out noise on the bounded line (a MEASURED human
signature; the distance-effect DIRECTION -- far pairs EASIER -- rules out serial chaining, which would make far pairs
harder). Copy the COMPUTATION (settle -> magnitude line -> native read), sweep the parameters.

This is glass-box: the settling is an explicit delta rule, the ordering is an FHRR superposition, the read-out is an
FPE grid argmax -- no external model at inference (the invariant).
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

import numpy as np
import torch

from . import binding
from . import fractional_power_encoding as fpe
from .situation_model_accumulate import unit_phase_vec

FPE_SIGMA = 1.0       # Gaussian phase-rate sigma (p1 default; the log-Gaussian tuning width)
POS_SCALE = 2.0       # half-range of the bounded mental line (settled scores in [-1,1] -> coords in [-pos_scale, +pos_scale])
GRID_MAX = 3.0        # decode grid half-width (> POS_SCALE so bounded coords never sit at the grid edge)
GRID_STEP = 0.05


def _settle(premises: Sequence[Tuple[int, int]], n: int, eta: float = 0.3, epochs: int = 200,
            temp: float = 1.0, seed: int = 0) -> np.ndarray:
    """Delta-rule / value-transfer relaxation of stated premises into scalar magnitude positions (Bradley-Terry ML
    gradient). For each premise (w, l): p = sigmoid(temp*(x_w - x_l)); x_w += eta*(1-p), x_l -= eta*(1-p). Overlapping
    premises couple through the shared middle term -> ONE integrated ordering. Zero-mean each epoch."""
    x = np.zeros(n, dtype=np.float64)
    rng = np.random.default_rng(seed + 7)
    order = list(range(len(premises)))
    for _ in range(epochs):
        rng.shuffle(order)
        for k in order:
            w, l = premises[k]
            p = 1.0 / (1.0 + np.exp(-temp * (x[w] - x[l])))
            g = eta * (1.0 - p)
            x[w] += g
            x[l] -= g
        x -= x.mean()
    return x


def _normalize_line(x: np.ndarray) -> np.ndarray:
    """Map settled scores onto a BOUNDED mental line [-1, 1] (the parietal magnitude line is bounded). Preserves the
    settled (convex) spacing shape -- so the distance effect and the BT end-anchor effect survive -- while keeping every
    coordinate inside the FPE faithful regime (no phase aliasing)."""
    m = float(np.abs(x).max()) + 1e-9
    return x / m


def _encode_register(x: np.ndarray, keys: List[torch.Tensor], rates: torch.Tensor, scale: float) -> torch.Tensor:
    """S = sum_i bind(item_key_i, FPE(scale * x_i)). The register holds the whole ordering as a superposition."""
    d = keys[0].shape[0]
    S = torch.zeros(d, dtype=torch.complex64)
    for i in range(len(keys)):
        place = fpe.enc(rates, scale * float(x[i]))
        S = S + binding.bind(keys[i], place)
    return S


def _grid_codes(rates: torch.Tensor, grid: np.ndarray) -> torch.Tensor:
    return torch.stack([fpe.enc(rates, float(g)) for g in grid], dim=0)    # (G, d) complex


def _decode_coord(S: torch.Tensor, key_i: torch.Tensor, grid_codes: torch.Tensor, grid: np.ndarray) -> float:
    """Recover item i's place code (unbind its key) and decode its coordinate: argmax similarity to the FPE grid (the
    native resonator read-out). Returns the estimated mental-line coordinate."""
    place = binding.unbind(S, key_i)                        # ~ FPE(scale*x_i) + crosstalk from the other items
    p = place / place.abs().clamp_min(1e-12)
    sims = torch.real(grid_codes.conj() @ p) / place.shape[0]
    j = int(torch.argmax(sims))
    return float(grid[j])


def _sign(v: float) -> int:
    return 1 if v > 1e-9 else (-1 if v < -1e-9 else 0)


class TransitiveOrderingLine:
    """Delta-rule MAGNITUDE-LINE integrator over an FHRR register -- read pairwise comparisons, integrate into one
    ordering, answer UN-STATED pairs by native FPE read-out. The first glass-box REASONING primitive (see module doc).

    Usage:
        line = TransitiveOrderingLine(n_items, d, torch.Generator().manual_seed(s), seed=s)
        line.integrate([(0, 1), (1, 2), (2, 3)])     # premises: (winner_idx, loser_idx), items 0..n-1
        line.compare(0, 3)                            # +1 if item0 > item3 on the integrated line (un-stated)
        line.coord(2)                                 # decoded magnitude-line coordinate of item 2
    """

    def __init__(self, n_items: int, d: int, generator: torch.Generator, fpe_sigma: float = FPE_SIGMA,
                 pos_scale: float = POS_SCALE, grid_max: float = GRID_MAX, grid_step: float = GRID_STEP,
                 seed: int = 0) -> None:
        self.n = int(n_items)
        self.d = int(d)
        self.pos_scale = float(pos_scale)
        self.keys: List[torch.Tensor] = [unit_phase_vec(self.d, generator) for _ in range(self.n)]
        self.rates = fpe.phase_rates("gauss", self.d, seed + 13, sigma=fpe_sigma)
        self.grid = np.arange(-grid_max, grid_max + 1e-9, grid_step)
        self.grid_codes = _grid_codes(self.rates, self.grid)
        self._S: torch.Tensor = None
        self._x: np.ndarray = None

    def integrate(self, premises: Sequence[Tuple[int, int]], eta: float = 0.3, epochs: int = 200,
                  temp: float = 1.0, seed: int = 0) -> np.ndarray:
        """Settle the pairwise premises [(winner_idx, loser_idx), ...] into a bounded magnitude line and encode the
        FHRR register. Premises may be a partial/overlapping set of comparisons; relational integration fills the rest.
        Returns the (bounded) settled positions."""
        self._x = _normalize_line(_settle(premises, self.n, eta=eta, epochs=epochs, temp=temp, seed=seed))
        self._S = _encode_register(self._x, self.keys, self.rates, self.pos_scale)
        return self._x

    def coord(self, i: int) -> float:
        """Decoded magnitude-line coordinate of item i, read off the register (native FPE resonator read-out)."""
        if self._S is None:
            raise RuntimeError("call integrate(premises) before reading coordinates")
        return _decode_coord(self._S, self.keys[i], self.grid_codes, self.grid)

    def compare(self, a: int, b: int) -> int:
        """Answer the (possibly UN-STATED) pair on the integrated line: +1 if a > b, -1 if b > a, 0 tie -- by comparing
        the two items' decoded coordinates. Higher coordinate = 'bigger' (winner side of the premises)."""
        return _sign(self.coord(a) - self.coord(b))
