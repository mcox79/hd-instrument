# Pre-registration: additive_hebbian_sequence_binding_capacity_cliff_sweep_v1

**Date:** 2026-06-27
**Anchor:** additive_hebbian_sequence_binding_capacity_cliff_sweep_v1
**Queue:** overnight_queue
**N:** 16384, **Seeds:** [11, 17, 23], **Sweep:** N_PAIRS in [50, 100, 200, 500, 1000, 2000, 5000]

## Scientific question

At what N_PAIRS load does the substrate's additive Hebbian sequence-binding mechanism (which today recall=1.000 at N=2048 V=200 N_PAIRS=50 per BTSP v2 smoke 2026-06-27) drop below order_discrimination=0.50 and below 0.20, when storing 2*N_PAIRS sequence bindings into one shared W? This DEFINES the regime envelope for all future order-sensitive sequence-binding mechanism cells.

## Pre-registered bands

**HARD-PASS:**
- Both CLIFF_50 (first N_PAIRS where additive_hebbian order_disc < 0.50) AND CLIFF_20 (first N_PAIRS where < 0.20) identified within the sweep.
- cv across seeds < 0.10 at every N_PAIRS where order_disc is in the discriminating band (0.05, 0.95).
- No measurement instability (NaN/inf/negative).
- GPU util p50 >= 30% in smoke (Fix #24).

**MIDDLE:** Only one of CLIFF_50 / CLIFF_20 identified (e.g., the harder threshold lies above N_PAIRS=5000) OR cv in [0.10, 0.20].

**HARD-FAIL:** additive_hebbian order_disc >= 0.95 at ALL N_PAIRS up to 5000 (regime never broken; this would be a big substrate-capacity finding meriting higher-load follow-up, but per directive it is HF for THIS cell) OR GPU util p50 < 30% in smoke.

## Calibration rationale

BTSP v2 smoke 2026-06-27 confirmed additive_hebbian = 1.000 at N=2048 V=200 N_PAIRS=50. Substrate Hebbian capacity scales roughly as N (Hopfield-1982: ~0.14*N items at zero error). With N=16384 we expect capacity around ~2000 items before crosstalk dominates. Cross-order discrimination is harder than mere recall (must reject the swapped-order context for the same atom-pair), so the cliff for order_disc<0.50 likely sits between N_PAIRS=200 and 2000. The thresholds 0.50 and 0.20 bracket the discriminating regime; the sweep step (geometric ~2x) lets us pinpoint within a factor-2 window.

## N-suffix section

Anchor scales by N_DIM, not _n<N> suffix. Production N_DIM = 16384; smoke N_DIM = 2048. Script enforces N_DIM at module init based on RUN_MODE.

## Timeout estimate

Smoke: N=2048, V=200, sweep=[50,200,1000], 1 seed -> ~3-6 min estimated (dominated by N_PAIRS=1000 outer-product builds + 2N_DIM x 2N_DIM W storage + per-binding random_tag loop).
Full: N=16384, V=200, sweep=[50..5000], 3 seeds. Per-seed dominant term is the largest sweep point (N_PAIRS=5000) on a 16384x16384 W. Random-tag arm runs a per-binding loop (10000 iterations at largest sweep) which dominates. Additive uses batched matmul (cheap). Context-bank-lookup is O(N_PAIRS) cosine. Estimated 5000-iter random_tag at N=16384 ~= 20-40 min; full sweep ~= 60-90 min per seed; 3 seeds = 3-4.5 hours plus overhead.
formula: ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^1.7 * (FULL_seeds/smoke_seeds)) approximation. With smoke_wall ~360s and scaling factor ~30, expected ~30-60 min per seed; 3 seeds plus margin.
timeout_s = 14400 (4h hard cap; if it exceeds we expect partial-seed checkpoint recovery)

# -----------------------------------------------------------------------------
# Token glossary (for reference; unfilled placeholders are intentional in this file)
# -----------------------------------------------------------------------------
