# Pre-registration: composition_ceiling_k_c_alpha_constant_m_per_stage_v1_n4096

**Date:** 2026-06-02
**Anchor:** `composition_ceiling_k_c_alpha_constant_m_per_stage_v1_n4096`
**Queue:** overnight_queue (GPU)
**Script:** `experiments/exp_composition_ceiling_k_c_alpha_constant_m_per_stage_v1_n4096.py`
**Source:** v343 routing, Item 32 (Arrhenius-drill Test P5); P_deflated=0.50

## Hypothesis

Substrate composition fails at depth k_c(alpha) ~ 0.138/alpha when M per stage is held
CONSTANT (not halving per stage as Q-A3 architecture does).

Arrhenius-drill prediction: sum of per-stage loadings must stay below alpha_c = 0.138.
At alpha=0.05: k_c ~ 2.76 (ceiling at k~3).
At alpha=0.10: k_c ~ 1.38 (ceiling at k~2).

Q-A3 L=10 EXACT-1.0 works because it halves M per stage: each stage decreases effective
alpha, implementing implicit isochoric composition. This test removes that protection.

## Pre-registered bands

**HARD-PASS**: L_fid >= 0.95 for k < k_c(alpha) AND L_fid < 0.50 for k > k_c(alpha)+1;
ceiling location within +-1 stage of prediction

**MIDDLE**: clear ceiling exists but location +-2 stages of prediction

**HARD-FAIL**: L_fid flat across all tested k (no ceiling, refutes prediction) OR
ceiling at k > 2 * predicted

No prior empirical anchor for constant-M composition. Calibration-probe policy:
bands at +-50% of theoretical prediction.

## Formula self-tests (PROT-022)

1. k_c formula: k_c(0.05) = 0.138/0.05 = 2.76; k_c(0.10) = 0.138/0.10 = 1.38.
   [Verified at module scope: assert abs(_kc_005 - 2.76) < 0.01]
2. Single-level Hadamard-over-Hopfield at alpha~0.05 N=256: L_fid > 0.30 (broad calibration).
   [Verified in _selftest_single_level()]
3. GPU matmul sanity: a @ b correct. [Verified in _selftest_gpu_ok()]

## N-suffix

PROT-018 binding: anchor `_n4096`; script MUST have N=4096 in full config.
Smoke runs at N_ACT=1024; full runs at N_ACT=N=4096. Verified: `N = 4096`.

## Timeout estimate

Smoke: N=1024, 2 seeds, 2 alpha, k=1..5. Estimated smoke_wall ~20s (GPU).
Full: N=4096, 5 seeds, 2 alpha, k=1..8.
Per (seed, alpha, k) at N=4096: W build (~2s) + 20 queries @ 20 steps (~1s) = ~3s.
Full: 5 * 2 * 8 * 3s = 240s.
timeout_s = ceil(1.5 * 20 * (4096/1024)^1.5 * (5/2)) = ceil(1.5 * 20 * 8 * 2.5) = ceil(600) -> **900s**

## PROT-018 pre-ship audit

```
grep -E "(N\s*=|n\s*=)\s*4096" experiments/exp_composition_ceiling_k_c_alpha_constant_m_per_stage_v1_n4096.py
```
Expected match: `N = 4096`
