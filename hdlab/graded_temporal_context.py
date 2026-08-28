"""Graded temporal context (a bindable multi-timescale clock) -- the "when" half of the factorized entity store.

Landed 2026-08-28 as landing-step 1 of the FACTORIZED two-system entity store (the proven-ready follow-on of the
integrated `the_entity_store_is_a_dense_bundle_that_fans`, SOLVED/EXCELLENT, owner-DONE). The maximally-faithful episodic
store factorises a trace into CONTENT (the "what", a near-orthogonal / sparse code) x this graded TEMPORAL CONTEXT (the
"when"), bound only at storage and read separately -- matching human single-unit data (Bausch et al. 2026: content and
context are SEPARATE populations bound by timing) + TEM (Whittington & Behrens 2020). This module is the "when" primitive.

WHAT IS PINNED (copy the operation): temporal context DRIFTS continuously and its similarity DECAYS smoothly with the time
lag -- the source of the TEMPORAL CONTIGUITY effect (adjacent moments are retrieved together; Howard & Kahana 2002 TCM;
Shankar & Howard 2012 leaky-integrator / Laplace bank; MacDonald 2011 time cells). A MULTI-TIMESCALE (log-spaced) bank
gives contiguity across many lags at once. The code is a UNIT-magnitude phasor so it is FHRR-BINDABLE (`bind`/`unbind`
compose it with content + order) while still carrying the graded contiguity kernel.

  ctx(t)[k] = exp(i (omega_k * t + phi_k)),  omega_k = 2*pi / period_k,  period_k log-spaced over [min_period, max].
  kernel(t, t') = Re<conj(ctx(t)), ctx(t')> / d  ->  1.0 at t=t', decaying smoothly with |t - t'|.

OUR-INVENTION-UNDER-TEST: the period range / spacing (a parameter to sweep, not adopt). PINNED: the log-multi-timescale
drift + the graded (not orthogonal) contiguity kernel -- an orthogonal sub-slot key would DESTROY contiguity (the cheap
finer-key fix's deficit; STEP 18/entity-store integration).

DEFAULT-SAFE island: new module, nothing imports it (the factorized store that composes content x this x order is the
following landing steps). torch complex64, FHRR-native.
"""
from __future__ import annotations

import math

import torch

DEFAULT_D = 1024


class GradedTemporalContext:
    """Bindable graded multi-timescale temporal context. `ctx(t)` -> a unit-magnitude complex64 FHRR vector whose
    inner product with `ctx(t')` decays smoothly with |t - t'| (temporal contiguity)."""

    def __init__(self, d: int = DEFAULT_D, seed: int = 20260828,
                 min_period: float = 2.0, max_period_mult: float = 4.0, horizon: float = 1000.0) -> None:
        self.d = int(d)
        g = torch.Generator().manual_seed(int(seed))
        # log-spaced periods over [min_period, max_period_mult * horizon] -> a multi-timescale bank
        lo, hi = math.log(min_period), math.log(max_period_mult * horizon)
        periods = torch.exp(torch.linspace(lo, hi, d, dtype=torch.float64))
        self.omega = (2.0 * math.pi) / periods                                   # (d,) float64
        self.phase = torch.rand(d, generator=g, dtype=torch.float64) * (2.0 * math.pi)

    def ctx(self, t: float) -> torch.Tensor:
        """The temporal-context code at continuous time `t`: exp(i(omega*t + phase)), complex64 (FHRR-bindable)."""
        ang = self.omega * float(t) + self.phase
        return torch.polar(torch.ones(self.d, dtype=torch.float64), ang).to(torch.complex64)


class EventSegmentedContext:
    """Graded temporal context whose drift JUMPS at EVENT BOUNDARIES -- so contiguity is HIGH within an event and CUT
    across a boundary at the same real-time lag (Baldassano 2017; DuBrow & Davachi 2013; Zwaan event-indexing: subjective
    temporal distance is LARGER across boundaries, and within-event order memory is better than across).

    Implemented as WARPED TIME: within an event `tau` advances by 1 per step; at a boundary it jumps by `boundary_jump`.
    `ctx(t)[k] = exp(i(omega_k * tau(t) + phi_k))`, unit-magnitude (FHRR-bindable). The BOUNDARIES are an INPUT (a
    prediction-error boundary detector -- e.g. the N400 coherence monitor -- supplies them; that wiring is a follow-on).
    This is the "when-to-segment" structure of the factorized episodic store (landing-step 3)."""

    def __init__(self, boundaries, d: int = DEFAULT_D, seed: int = 20260828, boundary_jump: float = 8.0,
                 min_period: float = 2.0, horizon: int = 1000) -> None:
        self.d = int(d)
        self.boundaries = set(int(b) for b in boundaries)
        tau = [0.0] * (horizon + 2)
        for t in range(1, horizon + 2):
            tau[t] = tau[t - 1] + 1.0 + (boundary_jump if t in self.boundaries else 0.0)
        self._tau = tau
        g = torch.Generator().manual_seed(int(seed))
        lo, hi = math.log(min_period), math.log(4.0 * max(tau[horizon], 1.0))
        periods = torch.exp(torch.linspace(lo, hi, d, dtype=torch.float64))
        self.omega = (2.0 * math.pi) / periods
        self.phase = torch.rand(d, generator=g, dtype=torch.float64) * (2.0 * math.pi)

    def _warp(self, t: float) -> float:
        i = int(math.floor(t))
        if i < 0:
            return self._tau[0]
        if i + 1 >= len(self._tau):
            return self._tau[-1]
        frac = t - i
        return self._tau[i] * (1.0 - frac) + self._tau[i + 1] * frac

    def ctx(self, t: float) -> torch.Tensor:
        """Temporal-context code at continuous time `t`, warped so drift jumps at event boundaries. complex64."""
        ang = self.omega * self._warp(t) + self.phase
        return torch.polar(torch.ones(self.d, dtype=torch.float64), ang).to(torch.complex64)
