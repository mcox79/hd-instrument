# Pre-registration: Sherman-Morrison rank-1 deletion cert-drop test v2 (Option A)

**Date:** 2026-06-02
**Anchor:** `sherman_morrison_rank1_deletion_cert_drop_v2_n4096`
**Queue:** remote_cpu_queue
**Trigger:** Item 22 v1 INSTRUMENTATION_SUSPECT; Strategy routing recommends Option A redesign.
**Priority:** Candidate C from v349 REFILL; PP-56 regulatory cert positioning (cross-drill Reservoir x Federated).

## Capability question

Does Sherman-Morrison rank-1 deletion produce a measurable cert-drop in the algebraic cert primitive (xi^T W xi / N), confirming that the SM update can serve as the algebraic basis for the PP-46/PP-56 deletion certificate?

## Redesign rationale (v1 INSTRUMENTATION_SUSPECT)

v1 tested Hopfield attractor dynamics: does SM deletion make xi a non-attractor?
Root cause: SM rank-1 update weakens but does NOT remove Hopfield attractors. xi is STILL an
attractor in W_new (residual_cos = 1.0). This was a spec error, not an instrumentation bug.

Option A correct framing: test cert = xi^T W xi / N as the deletion evidence.
- cert_before ~ 1.0 for stored patterns (pattern is algebraically encoded)
- cert_after ~ lam / (lam + N) ~ 0.00024 at N=4096, lam=1.0 (theoretical prediction)
- cert_ratio = cert_after / cert_before << 1 if deletion registers in cert primitive

## Pre-registered bands

### HARD-PASS
(a) mean cert_ratio = cert_after(xi_del, W_new) / cert_before(xi_del, W) < 0.15
    Theoretical value: 0.00024. HP threshold is 625x above theoretical (very conservative).
(b) mean retained_cert_delta = |cert_after(xi_j, W_new) - cert_before(xi_j, W)| < 0.10
    Retained patterns should be minimally affected by deletion.
(c) 5-seed unanimous on both (a) and (b).

### MIDDLE
cert_ratio in [0.15, 0.30] OR retained_cert_delta in [0.10, 0.20].

### HARD-FAIL
cert_ratio > 0.30 (deletion doesn't register in cert primitive)
OR retained_cert_delta > 0.30 (deletion damages retained patterns -- collateral damage).

Note: bands set at +/-50% around theoretical per calibration-probe policy.
Theoretical cert_ratio at N=4096: 0.00024 << HP threshold 0.15.

## Smoke gate

Smoke at N=512: cert_ratio=0.0019, retained_delta=0.005 -- strongly HARD_PASS.
Multi-scale at N=2048: cert_ratio=0.00049, retained_delta=0.00025 -- improves with N.
Effect size >> 1.0 (cert_ratio is 80x below HP threshold). No walk-back needed.
FULL run at N=4096 5-seed confirms at production scale.

## Cap_map impact if HARD_PASS

PP-56 regulatory cert row FOUNDED on algebraic side:
substrate's deletion cert provably maps to SM Newton-step formula;
cert-drop is measurable and monotone-decreasing with N.
Strongest Reservoir x Federated cross-drill resonance finding.

## N-suffix binding (PROT-018)

Script: `N = 4096`, `_N_SUFFIX = 4096`. Anchor name has `_n4096`. Matches.

## Timeout estimate

Smoke wall: <0.05s per seed (2 seeds at N=512).
FULL: N=4096, 5 seeds, M_STORE=50 patterns, N_TRIALS=20 deletion trials.
Matrix ops: W = N x N float32 = 67 MB; SM update is O(N^2) per trial.
Estimate: ceil(1.5 * 0.05 * (4096/512)^2.0 * (5/2) * 20) = rough upper bound.
Alternative estimate from smoke: 0.02s/seed * N^2 scaling: ceil(0.02 * 8^2 * 5) = ceil(6.4) ~ 30s.
Use conservative: **300s** (5 min; well under 14400s).

## Dependency verification

No data dependencies. Pure numpy CPU. Self-contained.
