"""Superposition (bundling) of hypervectors, recency-weighted via modulator state."""

from __future__ import annotations

import time

import torch

from . import modulators, tracing

# Semi-saturation constant for norm="divnorm" (pooled Carandini-Heeger). 0.0 -> pure pooled scalar (RMS-like);
# the serial-readout recovery is parameter-FLAT across sigma (SWEPT, not adopted -- it is the OPERATION that matters).
DIVNORM_SIGMA = 0.0


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
        elif norm == "divnorm":                               # POOLED divisive normalization (Carandini-Heeger 2012)
            # ONE scalar over the pool: S / (sigma + mean|S|) -- a global rescale that PRESERVES the linear/relative
            # structure (unlike the per-component branch), so a superposition stays serially decodable. Landed
            # 2026-08-28 from the integrated `the_register_bundle_renorm_breaks_the_serial_readout` (SOLVED/EXCELLENT,
            # owner-DONE): per-component 0.367 -> divisive 0.988 @M=64 on the register's serial readout. DEFAULT-OFF;
            # a read-terminal bundle (not re-bound) should use this, NOT per-component. DIVNORM_SIGMA=0.0 -> RMS-like
            # pooled scalar (the recovery is parameter-flat: an OPERATION, not a tuned number).
            pooled = s.abs().mean()
            denom = (DIVNORM_SIGMA + pooled).clamp_min(1e-12)
            out = s / denom.to(s.dtype)
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
