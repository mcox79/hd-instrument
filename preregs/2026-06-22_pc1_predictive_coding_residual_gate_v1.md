# Pre-registration: pc1_predictive_coding_residual_gate_v1

**Date:** 2026-06-22
**Anchor:** pc1_predictive_coding_residual_gate_v1
**Queue:** remote_cpu_queue
**N:** 4096, **Seeds:** [7, 17, 23], **M:** 2000 (alpha = 0.488), **threshold_pc:** 0.3

## Scientific question
Does substrate-native predictive coding (residual-gated Hebbian write, per Friston / Rao-Ballard 1999) maintain associative-memory recall while substantially reducing W matrix saturation, when the substrate already implicitly computes residual via `predict(key) = sign(W @ key)`?

## Arms
1. **VANILLA_HEBBIAN** -- baseline: every write at full strength
2. **PC_RESIDUAL_GATE_THRESH_0p3** -- write only when residual_mag >= 0.3
3. **PC_RESIDUAL_PROPORTIONAL** -- write strength = residual_mag (clipped [0, 1])
4. **RANDOM_GATE_CONTROL** -- write with p=0.5; CAN-FAIL discriminator (if this matches PC arms, gate is not load-bearing)

## Pre-registered bands

**HARD-PASS:** some PC arm achieves ALL of:
- recall_at_1 >= VANILLA recall_at_1 - 0.05 absolute
- final W_norm <= 0.5 * VANILLA W_norm (>= 50% growth reduction)
- write_skip_frac >= 0.30 (genuine saturation reduction)
- recall - RANDOM_GATE_CONTROL recall >= 0.05 (gate load-bearing, not random-skip artifact)
- CV across seeds < 0.07 mandatory for the passing arm
- substrate-only-decode (n_llm_calls = 0; structural guarantee verified in metrics)

**MIDDLE:** some PC arm preserves recall (>= VANILLA - 0.05) but W_norm reduction < 50%, OR W_norm reduction >= 50% but recall drop in (0.05, 0.10].

**HARD-FAIL:**
- all PC arms recall drop > 0.10 vs VANILLA OR
- no PC arm reduces W_norm OR
- RANDOM_GATE_CONTROL recall matches PC arms within 0.03 (gate not load-bearing) OR
- n_llm_calls > 0 (substrate-only-decode gate violation)

## Calibration rationale
M=2000 at N=4096 puts alpha = 0.488, well above the classical Hopfield capacity bound alpha_c = 0.138. In this regime, vanilla Hebbian writes saturate W (interference dominates); recall drops monotonically with each additional write. If predictive coding works, the substrate's own predictions get progressively better as W fills out, so residual magnitudes drop, and the threshold gate naturally skips writes for predicted patterns. The 50% W_norm reduction band tests that PC selectively writes only ~half the patterns. The 0.05 recall-preservation band is tight enough that random skip-50% cannot pass (random_control should hurt recall by 0.10+ in this regime because it discards genuinely-novel patterns too).

The RANDOM_GATE_CONTROL discriminator is the load-bearing test: if it matches PC arms within 0.03, the gate is not load-bearing -- any 50% write-skip preserves recall at this regime and the PC arms aren't using the residual signal. Symmetric verify both ways.

## N-suffix section
Anchor has NO _n suffix (PROT-018 N/A: this is a fixed-N capability test, not a sweep). Production N = 4096 (constant); script enforces N_FULL = 4096.

## Timeout estimate
Smoke (N=256, M=80, 1 seed, 50 queries) measured locally: < 5s wall.
FULL: N=4096, M=2000, 3 seeds, 500 queries.

formula: ceil(1.5 * 5 * (4096/256)^1.2 * (3/1)) = ceil(1.5 * 5 * 28.5 * 3) = 642s per arm. 4 arms x 3 seeds = 12 arm-runs. Per arm ~10-15min at FULL (M=2000 outer-products at N=4096 = 2000 * 4096^2 / 1e9 = ~34 GFLOPs; numpy CPU ~ 5-10 GFLOPS effective single-core -> 3-7s per arm-seed, plus recall pass = 500 * 4096^2 = 8 GFLOPs / arm). Total estimated 30-60min CPU wall.

timeout_s = 5400 (90 min ceiling; well below PROT-019 floors which don't apply since no _n suffix; provides 2-3x headroom over best estimate).

# -----------------------------------------------------------------------------
# Token glossary (per template):
# ANCHOR_NAME   pc1_predictive_coding_residual_gate_v1
# DATE          2026-06-22
# QUEUE_NAME    remote_cpu_queue
# N             4096
# SEEDS         3
# PARAM_LABEL   arm (4 levels)
# SCALING_EXP   1.2 (M outer-products dominate; sub-quadratic in N due to vectorization)
# SMOKE_WALL_S  ~5
# SMOKE_N       256
# SMOKE_SEEDS   1
# TIMEOUT_S     5400
# -----------------------------------------------------------------------------
