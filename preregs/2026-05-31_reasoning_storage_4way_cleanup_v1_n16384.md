# Pre-registration: reasoning_storage_4way_cleanup_v1_n16384

**Date**: 2026-05-31
**Anchor**: reasoning_storage_4way_cleanup_v1_n16384
**Queue**: remote_cpu_queue
**Script**: experiments/exp_reasoning_storage_4way_cleanup_v1_n16384.py
**PROT-018**: _n16384 binds N = 16384.
**PROT-019**: timeout_s = 14400 (floor).
**PROT-021**: per-seed checkpointing.

## Context

PP-11 (reasoning_storage_scheme_b_smoke_v1_n16384) landed RSB_MIDDLE_BAND:
structured-key accuracy ratio ~0.93 (5% gap vs random-key baseline). Research 2x
drill (2026-05-31) identified 4-way binding + per-hop cleanup (Steinberg-Sompolinsky
2022) as the primary closure mechanism. Routing note:
notes/strategy_request_to_strategy_reasoning_storage_alternative_encoding_2026-05-31.md

## Configuration

- N = 16384, BSC bipolar codebook
- 500 reasoning chains, depth Uniform{3,4,5}
- Codebooks: 5 rule, 200 entity, 20 relation, 10 hop-id (independently drawn)
- Seeds: [7, 17, 23] (3 seeds minimum per routing HP bands)
- Cleanup: nearest-neighbor snap to entity codebook (cosine argmax)

## 3-Arm design

- Arm A: 4-way binding ALONE (k_step = r*k1*k2*h; no cleanup)
- Arm B: 3-way binding + per-hop cleanup ALONE (no hop-id)
- Arm C: combined 4-way binding + cleanup (primary deliverable)
- Baseline: 3-way structured (PP-11 equivalent)
- Random: matched random-key corpus

## Pre-registered thresholds

### Arm C (combined 4-way + cleanup) -- PRIMARY

| Band | Condition |
|---|---|
| HARD-PASS | mean structured/random ratio >= 0.98 (gap < 2%); ALL 3 seeds pass; cleanup verify_rate >= 0.95 |
| HARD-FAIL | mean ratio < 0.96 (< 1% absolute improvement vs PP-11 ~0.93 baseline) |
| MIDDLE-BAND | mean ratio 0.96-0.98; 2-3% residual gap |

### Arm A (4-way alone) -- Informative

| Outcome | Interpretation |
|---|---|
| ratio >= 0.97 | hop-id independently addresses a different interference class than permutation mitigation |
| ratio < 0.96 | hop-id addresses same class as failed permutation; cleanup is the load-bearing component |

### Arm B (cleanup alone) -- Informative

| Outcome | Interpretation |
|---|---|
| ratio >= 0.97 | cleanup alone sufficient; 4-way adds marginal value |
| ratio < 0.96 | cleanup snaps to wrong attractor under structured noise (drill B Axis 2); 4-way is load-bearing |

### Audit moat

| Band | Condition |
|---|---|
| PRESERVED | cleanup_verify_rate >= 0.95 AND algebraic decomp completeness 1.0 |
| THREATENED | cleanup_verify_rate < 0.80 (multiple near-argmax entries) |

## Outcome plans

**IF HARD-PASS (Arm C)**: PP-11 row cap_map move from INCONCLUSIVE (0.40-0.55) to
CANDIDATE (0.65-0.80). PP-9 amortization economics update: 5% quality-degradation
budget tightens to <2%. Dispatch: Arm A/B ablation informs whether GHRR or FHRR
is the better fallback if needed in future. No immediate follow-on needed.

**IF MIDDLE-BAND (Arm C)**: PP-11 stays INCONCLUSIVE. File GHRR
(non-commutative HRR, Yeung-Zou-Imani 2024) comparison experiment as next escalation.
FHRR DEPRECATED (audit-moat-weakening unacceptable per routing note).

**IF HARD-FAIL (Arm C)**: PP-11 permanently INCONCLUSIVE at 0.40-0.55. PP-9 locks
in 5% quality-degradation budget as a documented product property. Substrate framing
narrows to "audit-grade fast retrieval at known quality cost" for structured-key
corpora. No further algebra change experiments without new prior.

## Timeout estimate

Smoke at N=512, 20 chains, 1 seed: ~2s. Comparable PP-11 full: ~25s/seed.
This adds 4-way binding (same compute) + cleanup (200-vec argmax per step: trivial).
Estimate: ~35s/seed x 3 seeds = 105s. Safety ceil(1.5 * 105) = 158s.
PROT-019 floor dominates. **timeout_s = 14400**.

## Calibration note

P_deflated 0.30-0.45 (combined Arm C) per [[feedback-lit-scan-calibration-penalty]].
Prior empirical anchor available from PP-11: baseline ratio ~0.93. Bands set from
that anchor (HP at 0.98 = closure to <2%; HF at 0.96 = <1% improvement).
Not a calibration probe (prior anchor available). Standard bands apply.

## N-suffix

PROT-018 binding: N_FULL = 16384 in script. Production config matches _n16384 suffix.
