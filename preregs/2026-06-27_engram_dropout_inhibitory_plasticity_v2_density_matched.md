# PRE-REG: engram_dropout_inhibitory_plasticity_v2_density_matched

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7-1M agent spawn, Research team-lead dispatch)
**Barrier:** B3 (consolidation under saturation) - Wave 2 redesign
**Skunkworks audit:** notes/skunkworks_mechanism_null_audit_wave2_2026-06-27.md (commit edee21b3)
**Predecessor:** experiments/exp_engram_dropout_inhibitory_plasticity_v1.py

## TRIGGERS v2 OVER v1

v1 hardcoded `RANDOM_MASK_DENSITY=0.50` (lines 121, 447) while engram_dropout's mask naturally shrinks via cycle-by-cycle pruning to mean density ~0.37. Density confound: RANDOM_MASK had 0.50/0.37 = 1.35x more active dims than ENGRAM. Skunkworks audit: apples-to-oranges; v1's "ENGRAM beats RANDOM" claim is unverifiable because RANDOM had a capacity headroom advantage by construction.

## HYPOTHESIS

With per-pattern density-matched random control, the engram_dropout selectivity advantage IS or IS NOT present:
- HARD_PASS: ENGRAM_DROPOUT_DROPIN.cor - RANDOM_MATCHED.cor >= 0.05 (genuine selectivity benefit)
- HARD_FAIL: ENGRAM <= RANDOM_MATCHED (density was the lever; Pignatelli mechanism null in our task class)

## ROOT-CAUSE FIX

Procedure:
1. Run engram_dropout_dropin -> capture per-pattern final density D[p] (length=N_CAT)
2. Build RANDOM_MATCHED mask with per-pattern density = D[p] (random selection)
3. Both arms evaluated with identical readout surface (masked-readout cor_score)

Discriminator: random vs engram at matched density.

## ARMS (4)

1. ARM_BASELINE_NO_MASK -- control: mask=1.0 (fair-regime check)
2. ARM_RANDOM_MATCHED -- random per-pattern mask with density = D[p] from engram_dropout_dropin
3. ARM_ENGRAM_DROPOUT -- selectivity-driven mask (dropout only; no recruitment)
4. ARM_ENGRAM_DROPOUT_DROPIN -- PRIMARY: dropout + recruitment (Pignatelli mechanism)

## PRE-REG BANDS

**HARD_PASS:**
- ENGRAM_DROPOUT_DROPIN.cor >= 0.40
- AND cor_lift over RANDOM_MATCHED >= 0.05
- AND BASELINE_NO_MASK NOT in [0.95, 1.00] (fair regime)
- AND density alignment (engram_mean - random_mean)/engram_mean < 10%
- AND cv across seeds < 0.10 (full only)

**MIDDLE_BAND:**
- cor_lift in [0.02, 0.05) OR partial alignment

**HARD_FAIL:**
- BASELINE >= 0.95 (regime broken)
- OR ENGRAM <= RANDOM_MATCHED (mechanism null at matched density)
- OR density alignment > 10% (procedure broken)
- OR cardinality breach

## REGIME

N_DIM=512, N_CAT=25, N_TRAIN=5, proto_noise=0.6 (BTSP-probed Skunkworks audit regime).
N_RETRIEVAL_CYCLES=200 full / 50 smoke.
DELTA_DROPOUT=0.10, DELTA_DROPIN=0.02, RECRUITMENT_PROB=0.05.
Seeds: full=[7,17,23,31,41]; smoke=[7,17].

## CARDINALITY_OK

EXPECTED_N_UNITS = n_seeds * 4 arms. Full=20; smoke=8.

## FAIRNESS (META_RULE_AA)

- All arms read SAME SURFACE: masked-readout argmax cor_score to true prototype
- BASELINE_NO_MASK = control (mask=1.0); ENGRAM=mechanism; RANDOM_MATCHED=confound control
- Density-matched random isolates the SELECTION variable from the SPARSIFICATION variable
- Smoke discriminator FIRES: density alignment must work in selftest (assert rel_diff < 0.15)

## DISPATCH

Queue: remote_cpu_queue (~2 CPU-hr full).
Timeout: 7200s.

## EXPECTED OUTCOMES

- HARD_PASS: Pignatelli engram-driven selectivity load-bearing
- HARD_FAIL via ENGRAM<=RANDOM: v1 result was density-confounded; mechanism null
- HARD_FAIL via density alignment: procedure broken (re-author)
