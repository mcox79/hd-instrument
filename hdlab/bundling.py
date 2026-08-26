"""Superposition (bundling) of hypervectors, recency-weighted via modulator state."""

from __future__ import annotations

import time

import torch

from . import modulators, tracing


def bundle(vectors: torch.Tensor, norm: str | None = None) -> torch.Tensor:
    """Superpose (k, n) -> (n,). With recency=0: uniform sum. With recency>0: geometric decay toward older items.

    FHRR: per-component magnitude renormalization. HRR: whole-vector L2 normalization.

    norm=None (DEFAULT, byte-identical): the above -- FHRR per-component renorm.
    norm="l2": whole-vector L2 for the FHRR (complex) branch too. The per-component normaliser is the
      inverse of the faithful op and only ever HURTS role-filler recovery (evidence: problem
      the_core_binding_operator_may_not_be_brain_faithful -- L2/raw-sum beat per-component 32/32, it wins
      zero). REQUIRES the coupled readout atoms.similarity(..., cosine=True); a /n readout on an L2 bundle
      is miscalibrated. DEFAULT-OFF -- measure on the LIVE task before flipping (an isolation win is not a
      capability).
    """
    t0 = time.perf_counter_ns()
    state = modulators.current()
    is_complex = vectors.is_complex()

    if state.recency > 0:
        k = vectors.shape[0]
        decay = max(1.0 - state.recency, 1e-6)
        weights = torch.tensor(
            [decay ** (k - 1 - i) for i in range(k)],
            dtype=torch.float32,
        )
        if is_complex:
            w = torch.complex(weights, torch.zeros_like(weights)).to(vectors.dtype)
        else:
            w = weights.to(vectors.dtype)
        s = (vectors * w.unsqueeze(-1)).sum(dim=0)
    else:
        s = vectors.sum(dim=0)

    if is_complex:
        if norm == "l2":                                      # whole-vector L2 (brain-motivated); DEFAULT-OFF
            nrm = s.norm()
            out = s / nrm if float(nrm) > 0 else s
        else:                                                 # DEFAULT: per-component unit-torus (unchanged)
            mag = s.abs()
            mag = torch.where(mag > 0, mag, torch.ones_like(mag))
            out = s / mag.to(s.dtype)
    else:
        nrm = s.norm()
        out = s / nrm if float(nrm) > 0 else s

    tracing.emit(
        "bundling.bundle",
        {"shape": list(vectors.shape)},
        out,
        elapsed_ns=time.perf_counter_ns() - t0,
    )
    return out
