# Pre-registration: vsa_binding_over_static_skahm_class_v1_n4096

**Date:** 2026-06-02
**Anchor:** `vsa_binding_over_static_skahm_class_v1_n4096`
**Queue:** remote_cpu_queue
**Script:** `experiments/exp_vsa_binding_over_static_skahm_class_v1_n4096.py`
**Source:** v343 routing, Item 19 (cross-drill resonance Reservoir x Memristor); P_deflated=0.55

## Hypothesis

Standard VSA bind/unbind operations (HRR-style Hadamard binding) preserve fidelity
when operating over patterns stored in the substrate's SKAH-M-class static attractor
network (vs the standard temporal-reservoir treatment).

Cross-drill resonance: Reservoir drill confirmed VSA community treats reservoirs only
as nonlinear expansion kernels, never as mutable algebraic stores. Memristor drill
confirmed SKAH-M class hardware-family match with Kuramoto-honeycomb. This test
verifies the algebraic side.

## Pre-registered bands

**HARD-PASS**: cos(retrieved, xi_A) >= 0.85 in >= 4/5 seeds at alpha=0.05 N=4096

**MIDDLE**: cos in [0.60, 0.85)

**HARD-FAIL**: cos < 0.50 -- VSA bind-unbind algebra doesn't survive static SKAH-M storage

Calibration probe: no prior empirical anchor. Bands at theoretical prediction (cos~0.90
expected at alpha=0.05) +-20%. Wider per calibration-probe policy.

## Formula self-tests (PROT-022)

1. Hadamard bind is self-inverse over +-1 vectors: (a*b)*b = a exactly.
2. Random bipolar vectors near-orthogonal at N=4096: mean |cos| < 0.10.
3. Hopfield retrieval at alpha~0.05: mean fidelity > 0.50 at N=256 (smoke-scale).
   [All verified at module scope in _instrumentation_selftest()]

## N-suffix

PROT-018 binding: anchor `_n4096`; script MUST have N=4096 in full config.
Smoke runs at N_ACT=512; full runs at N_ACT=N=4096. Verified: `N = 4096`.

## Timeout estimate

Smoke: N=512, M=26, 2 seeds, 10 probes.
Full: N=4096, M=204, 5 seeds, 30 probes.
Per seed at N=4096: W build (~3s) + retrieval (30 queries * 20 steps * N^2 matmul ~ 15s) = ~18s.
Smoke wall: ~5s (N=512). Full: ~18s * 5 seeds = 90s.
timeout_s = ceil(1.5 * 5 * (4096/512)^1.0 * (5/2)) = ceil(1.5 * 5 * 8 * 2.5) = ceil(150) -> **600s**

(Conservative due to N^2 per-query retrieval; 600s gives ample headroom.)

## PROT-018 pre-ship audit

```
grep -E "(N\s*=|n\s*=)\s*4096" experiments/exp_vsa_binding_over_static_skahm_class_v1_n4096.py
```
Expected match: `N = 4096`
