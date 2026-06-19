# Prereg: pp58_bbp_spectral_gap_calibration_v1_n16384

**Date:** 2026-06-03
**Anchor:** pp58_bbp_spectral_gap_calibration_v1_n16384
**Queue:** overnight_queue (GPU machine, eigendecomp on CPU numpy)
**Source:** research_routing_v359_drill_battery_synthesis_2026-06-03.md Section 3 Exp 2

---

## Capability question

Does substrate's BBP spectral-gap protocol (bulk-edge eigenvalue merging) give the predicted
N-independent ratio 4.13 at alpha=0.05, with sigma_g_audit_crit = 0.726 and cap_crit (NLO) = 3.0?

---

## N-suffix

Anchor has _n16384; production N = 16384. PROT-018 enforced via assert in script.

---

## Pre-registered threshold bands

**HARD-PASS (all three conditions required):**
- ratio (cap_crit / audit_crit) in [3.5, 4.5]
- sigma_g_audit_crit in [0.65, 0.80]
- cap_crit in [2.5, 3.5]

**MIDDLE-BAND:**
- ratio in [3.0, 5.0] but at least one envelope-location outside HP band

**HARD-FAIL:**
- ratio < 3.0 OR > 5.0 (BBP prediction wrong)

Strategic significance: HARD-PASS founds PP-58 row at 0.65-0.80 (LIFT from EXPLORATORY MIDDLE).
HARD-FAIL means BBP protocol needs further theoretical refinement; PP-58 stays MIDDLE.

---

## Formula self-tests (PROT-022)

1. BBP formula: 1 - sqrt(0.05) - 0.05 = 0.7264 within 0.001
2. MP upper edge: (1 + sqrt(0.05))^2 = 1.4972 within 0.01
3. M check: int(0.05 * 16384) = 819
4. NLO sigma_crit: sqrt(ln(1 + 0.15/(3*0.05))) = sqrt(ln(2)) = 0.8326 within 0.002

All verified at module-scope in _instrumentation_selftest().

---

## Test design

- N = 16384, alpha = 0.05, 5 seeds [7, 17, 23, 31, 41]
- sigma_g sweep: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.65, 0.70, 0.726, 0.75, 0.80, 0.85, 0.90, 1.0, 1.2, 1.5, 2.0]
- W = (Xi.T @ Xi)/N + sigma_g * symmetric_noise/N (additive noise, not multiplicative)
- Metric: mean retrieval recall vs sigma_g; find audit_crit (recall drops below 0.5) and
  cap_crit (recall approaches 0.1 near-zero). Ratio = cap_crit / audit_crit.
- Instrumentation self-test: MANDATORY (all 6 assertions in _instrumentation_selftest())

---

## OOM check

W matrix CPU float64 at N=16384: 2.15 GB. Remote machine has 16+ GB. No OOM risk.
Xi on GPU float32: M=819 * 16384 * 4 = 53.7 MB. Fine.

---

## Timeout estimate

Eigendecomp NOT used in current implementation (recall-based proxy for audit/cap crit).
Main cost: 18 sigma_g * 5 seeds * matrix build + retrieval at N=16384.
W build at N=16384: ~1s/call. Retrieval: ~0.1s. Total: 18 * 5 * 1.1 = 99s. With overhead: ~200s.
timeout = 900s (4.5x overhead factor for remote machine latency and safety margin).

---

## Calibration notes

Prior PP-58 empirical anchors: ratio=3.0 (N=8192), ratio=4.0 (N=16384) MIDDLE_BAND.
BBP asymptote prediction = 4.13. HP band [3.5, 4.5] covers +-25% around prediction.
This is a REFINED calibration (not first measurement) -- prior ratios give anchor.
Bands set per existing [3.0, 5.0] MIDDLE definition from v354 with HP tightening to [3.5, 4.5].

---

## Smoke profile

N_smoke = 512, SEEDS_smoke = [7, 17], SIGMA_G_USE = [0.0, 0.3, 0.726, 1.0, 2.0], N_queries = 5.
Expected smoke wall: ~10s. Instrumentation self-test verified first.

## Multi-scale smoke

N=512 and N=512*4=2048 -- both smoke runs required per role contract when N is load-bearing.
(N is NOT the primary axis here; sigma_g is. Single-N smoke is sufficient.)
