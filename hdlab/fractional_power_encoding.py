"""Fractional Power Encoding (FPE) -- the FHRR magnitude CODE (log-Weber), the substrate foundation for scalar magnitude.

Landed 2026-08-28 as landing-step 1 of the p1 scalar-magnitude channel (integrated
`build_the_composed_scalar_magnitude_meaning_channel`, SOLVED/EXCELLENT, owner-DONE). The composed magnitude "ruler"
(`scalar_adjective_operation`, following) and the `quality_relation` Channel-B upgrade both build on this primitive; it is
ported here first because an hdlab organ cannot import from `experiments/`.

WHAT IS PINNED (copy the operation): a scalar coordinate `u` is encoded as a unit-phasor vector `polar(1, rates*u)` on a
SHARED random phase axis (Plate's fractional power encoding; Frady, Kleyko & Sommer). Encoding the LOG of a magnitude
gives the brain's number code:
  * with GAUSSIAN phase rates the similarity kernel is Gaussian in log-space = a LOG-GAUSSIAN tuning curve in x -- the
    measured number-neuron shape (asymmetric on a linear axis, symmetric on a log axis; Nieder);
  * it obeys WEBER'S LAW -- fixed-RATIO pairs (x, k*x) have a SCALE-INVARIANT kernel (constant along the magnitude axis),
    where a fixed-DIFFERENCE (linear) code does not;
  * the comparator is NATIVE substrate arithmetic: `unbind(enc(log x), enc(log ref)) == enc(log(x/ref))`, whose decoded
    coordinate is `log(x/ref)` -- the directional Weber comparison signal, with NO extra machinery.
The rate distribution (Gaussian sigma) is OUR-INVENTION-UNDER-TEST (a parameter to sweep, not adopt); the log-encoding and
the phasor form are pinned.

DEFAULT-SAFE: a new module, nothing imports it yet (ISLAND). Depends only on torch + `hdlab.lexical_similarity._cos_complex`.
"""
from __future__ import annotations

import math

import torch

from .lexical_similarity import _cos_complex as _cos_complex


def phase_rates(kind: str, d: int, seed: int, sigma: float = 1.0, half_width: float = math.pi) -> torch.Tensor:
    """The SHARED random phase-rate axis (float64). `gauss` (log-Gaussian tuning) is the brain-faithful default;
    `uniform` is a flat alternative; `random_twin` is an info-free control drawn from a disjoint seed."""
    g = torch.Generator().manual_seed(int(seed))
    if kind == "gauss":
        return torch.randn(d, generator=g, dtype=torch.float64) * sigma
    if kind == "uniform":
        return (torch.rand(d, generator=g, dtype=torch.float64) - 0.5) * 2.0 * half_width
    if kind == "random_twin":
        return torch.randn(d, generator=torch.Generator().manual_seed(int(seed) + 777), dtype=torch.float64) * sigma
    raise ValueError(f"unknown rate kind {kind!r}; expected gauss/uniform/random_twin")


def enc(rates: torch.Tensor, u: float) -> torch.Tensor:
    """FPE code of scalar coordinate `u` on the shared phase axis: polar(1, rates*u), complex64 (substrate dtype)."""
    ang = rates * float(u)
    return torch.polar(torch.ones(rates.shape[0], dtype=torch.float64), ang).to(torch.complex64)


def log_encode(rates: torch.Tensor, x: float) -> torch.Tensor:
    """The magnitude CODE: encode log(x) so the kernel is log-Gaussian and Weber (fixed-ratio scale-invariant).
    `x` must be positive (a magnitude / degree)."""
    return enc(rates, math.log(float(x)))


def kern(rates: torch.Tensor, ua: float, ub: float) -> float:
    """Similarity kernel between two coordinates = cos of their FPE codes (real part)."""
    return float(_cos_complex(enc(rates, ua), enc(rates, ub)))
