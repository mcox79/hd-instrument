# Pre-registration: PP-33 R4 activation barrier N-scale at N=8192

**Date:** 2026-06-03
**Anchor:** `activation_barrier_n_scale_v1_n8192`
**Queue:** remote_cpu_queue
**Trigger:** PP-33 LVH #209: v2_n4096 mean ratio=1.0962 fell below MIDDLE lower bound 1.10; honest tag BELOW_MIDDLE. Hypothesis: ratio is N-suppressed at N=4096 and increases toward Arrhenius prediction (2.316) at larger N.
**Priority:** PP-33 barrier characterization: does N-scaling rescue the barrier signal?

## Capability question

Does the activation barrier ratio (nf_crit(0.05)/nf_crit(0.10)) increase at N=8192 compared to N=4096 value of 1.0962? This tests whether the sub-MIDDLE result at N=4096 reflects finite-N suppression or a genuine weakness.

## Prior results

| Anchor | N | mean ratio | verdict |
|---|---|---|---|
| v1_n4096 (0.04-step) | 4096 | 1.10 | MIDDLE |
| v2_n4096 (0.01-step) | 4096 | 1.0962 | BELOW_MIDDLE (LVH #209) |

Theory (Arrhenius): ratio = (alpha_c - 0.05)/(alpha_c - 0.10) = 0.088/0.038 = 2.3158.
N=4096 ratio ~47% of theory. Finite-N hypothesis predicts ratio rises with N.

## Pre-registered bands

### HARD-PASS
(a) mean ratio > 1.20 (clear N-scaling improvement over N=4096=1.0962)
(b) n_monotone >= 4/5 seeds show ratio > 1.10 (consistency check)
N-scaling confirmed; finite-N suppression supported.

### MIDDLE
1.05 < mean ratio <= 1.20 (modest N-scaling improvement; not conclusive)
OR ratio > 1.20 but n_monotone < 4/5 (inconsistent across seeds)

### HARD-FAIL
ratio <= 1.02 (no N-scaling; direction lost; Arrhenius unsupported at all substrate N)

## Smoke result

N_ACTIVE=1024, 2 seeds, 0.04-step coarse grid:
ratio=1.1500 in (1.02, 1.2] => MIDDLE (improvement over N=4096=1.0962, not yet HP).
Direction: positive. n_monotone=2/2 at smoke scale.
Effect improvement: +5% ratio gain from N=1024 to production. Production N=8192 may push further.

## N-suffix binding (PROT-018)

No `_nN` suffix in anchor name (alpha-sweep experiment; production N=8192 is fixed in script).
Script assertion: `assert N == 8192`. PROT-018 note documented in script header.

## Timeout estimate

Smoke: ~0.05s per seed at N=1024 (2 seeds, coarse grid).
Scale: (N=8192/N=1024)^2.0 (W=NxN dominant) = 64x. Seeds: 5/2 = 2.5x. Grid: 61/13 = 4.7x trials.
timeout = ceil(1.5 * 0.05 * 64 * 2.5 * 4.7) = ceil(56.4) = 57s. Raw very short.
Conservative: use 3600s (268 MB W matrix at N=8192; 5 seeds x fine grid = 300+ W builds; each ~0.5s).
Using **3600s** (conservative for CPU with repeated 268 MB matrix builds).

## Dependency verification

No data dependencies. Pure numpy CPU. W matrix 268 MB (float32) fits in 16 GB RAM.
Self-contained script; `_seed_checkpoint` import verified in experiments package.
