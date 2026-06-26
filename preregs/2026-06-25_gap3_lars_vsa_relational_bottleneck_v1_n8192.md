# Pre-registration: gap3_lars_vsa_relational_bottleneck_v1_n8192

**Date:** 2026-06-25
**Anchor:** gap3_lars_vsa_relational_bottleneck_v1_n8192
**Queue:** local_cpu_queue
**N:** 8192, **Seeds:** [11, 13, 19], **K_symbols:** 64

## Scientific question

Gap 3 (compositional generalization) capability suite scored 0.00 heldout. This cell
tests whether either of two structurally distinct mechanisms - (a) LARS-VSA learned-
symbol relational bottleneck (Webb-Goyal-Smolensky 2024; arxiv 2405.14436), (b)
resonator-network iterative factor decomposition (Frady-Sommer arxiv 1906.11684) -
lifts substrate above the 0.10 floor at N=8192 on a clean 5-cat compositional task.
3-arm decisive discriminator with ARM_BASELINE = nearest-neighbor episodic.

## Pre-registered bands

**HARD-PASS:**
- Any of {ARM_RELBOTTLENECK, ARM_RESONATOR} mean_heldout_top1 >= 0.50
- AND >= 4.0x ARM_BASELINE
- AND cv across 3 seeds <= 0.10

**HARD-PASS-PARTIAL:** Any schema arm >= 0.30 AND >= 2.5x ARM_BASELINE.

**MIDDLE:** Any schema arm in [0.10, 0.30] OR 3-arm spread < 0.05 (non-discriminating; redesign before USER arbitration per [[feedback-encoder-picks-emerge-from-data]]).

**HARD-FAIL:**
- All 3 arms <= 0.10 (entire mechanism family ruled out at this scale)
- OR ARM_BASELINE >= 0.30 (HARD_FAIL_CONFOUND: training-set leak; re-audit harness)

**BIAS-Q saturation guard:** any arm >= 0.995 with cv < 0.01 -> flag as suspect-leak (do NOT tier-claim).

## Calibration rationale

- Chance = 1/5 = 0.20; HARD_PASS floor 0.50 is 2.5x chance, matches research note prereg ("heldout >= 0.50 = 10x chance 0.05") adjusted for 5-cat task (chance 0.20 not 0.05).
- 4x baseline multiplier reflects research note's "lift over baseline >= 4x" requirement; baseline expected ~0.20 (chance) with embedded cat-signal frac=0.005 (NOT 0.30+ which would indicate leak).
- PARTIAL threshold 0.30 + 2.5x multiplier captures real but not chain-grade lift; queues capacity-sweep follow-up per research note.
- HARD_FAIL floor 0.10 matches research note ("all three arms <= 0.10 = rules out mechanism family"); CONFOUND floor 0.30 from baseline-leak guard.
- cv ceiling 0.10 looser than cortex-schema cell's 0.07 because LARS-VSA + resonator have more stochasticity (learned-symbol Hebbian + iterative-resonator convergence).
- CAT_SIGNAL_FRAC=0.005 matches cortex_schema_v1 discriminating-regime choice (proven on precedent cell to keep baseline weak ~0.30 ceiling).
- META_M7 (capacity-sensitive dims identical smoke/full): N=8192 in BOTH smoke and full per HRR-crosstalk lesson; reduces task to single seed in smoke (SEEDS=[11]) instead of changing N.

## N-suffix section

Anchor _n8192; production N = 8192; script enforces N = 8192 in BOTH smoke and full mode per META_M7. PROT-018 satisfied (literal `N = 8192` assigned).

## Timeout estimate

Smoke wall (single seed N=8192): expected ~30-60s (HRR FFT bind/unbind at N=8192 is fast; 3 arms x 25 heldout queries each + 50 training-set Hebbian routes; resonator inner loop 25 iters x 25 queries).

FULL: N=8192, seeds=3, identical mechanism, ~3x smoke wall.

formula: ceil(1.5 * 60 * (8192/8192)^1.0 * (3/1)) = ceil(1.5 * 60 * 1 * 3) = 270s

PROT-019 requires _n>=4096 cells use timeout_s >= 3600 minimum.

timeout_s = 3600 (PROT-019 floor)
