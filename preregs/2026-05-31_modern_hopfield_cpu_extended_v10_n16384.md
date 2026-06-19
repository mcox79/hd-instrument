# Pre-registration: modern_hopfield_cpu_extended_v10_n16384

**Date:** 2026-05-31
**Anchor:** modern_hopfield_cpu_extended_v10_n16384
**Queue:** remote_cpu_queue
**Script:** experiments/exp_modern_hopfield_cpu_extended_v10_n16384.py
**Cap-map row:** C9 Modern Hopfield ceiling (currently 0.78-0.92 after v9 HARD_PASS)
**Trigger:** v9 HARD_PASS at M in {4N,8N,16N} at N=16384 BSC, 9/9 cells unanimous recall=1.0

## Scientific question

At N=16384, CPU, BSC bipolar, M in {20N, 32N, 64N} = {327680, 524288, 1048576},
what is the largest M at which 95% recall holds in 3/5+ seeds?

## M-grid rationale

Wide sparse cliff-locator chosen over finer {20N,24N,28N,32N} grid:
- v9 HARD_PASS'd the entire {4N,8N,16N} range unanimously (recall=1.0 all cells)
- The cliff is hiding well past 16N; a dense near-16N grid wastes compute probing
  a region that is almost certainly still above the cliff
- {20N, 32N, 64N} lets us locate the cliff to within a factor of 2, which is
  sufficient for the "LIFT to 0.85-0.95+" decision
- If 64N also passes unanimously, the next extension can use a 4x jump again

## Pre-registered threshold bands

**HARD_PASS:** max_M_per_seed includes 64N (=1048576) in 3/5+ seeds.
  Interpretation: ceiling is past 64N; row lifts to 0.85-0.95+ (>64x linear capacity).

**HARD_FAIL:** construction OOMs at 20N or 32N in 3/5+ seeds before recall
  is measured (system RAM is the effective ceiling, not the substrate's capacity).
  Note: HARD_FAIL is informative, not catastrophic -- it reports the RAM wall.

**MIDDLE_BAND:** cliff identified within {20N..64N} in 3/5+ seeds, OR OOM in
  fewer than 3/5 seeds with ceiling located at 20N-32N. Row annotated with
  "ceiling between 20N and 64N at N=16384 BSC."

## N-suffix binding (PROT-018)

`_n16384` binds N = 16384. Production config: `N = 16384`, `N_FULL = 16384`.
Pre-ship audit confirms `grep -E "(N\s*=|n\s*=)\s*16384"` matches.

## Seed policy

5 seeds [7, 17, 23, 31, 41] per PROT-021 seed-checkpoint pattern.
(v9 used 3 seeds; 5 seeds raises power for the borderline cliff-locator question.)

## Smoke result

Smoke at N=1024, M_sweep=[20480, 32768]:
- seed=17: M=20480 recall=1.0, M=32768 recall=0.92
- Wall: 1.1s. Self-test PASS.
- Smoke verdict: MIDDLE_BAND at N=1024 (cliff between 20N and 32N at small scale).
  This is expected -- small-N has proportionally lower capacity per the Modern Hopfield
  scaling law. The FULL run at N=16384 is the primary question.

## Walk-back gate assessment

Smoke effect is not borderline for the cliff-locator purpose -- both probe points
work (recall > 0.90), and the "cliff below 32N" at smoke scale is consistent with
theory (capacity scales with N, so the cliff moves right at larger N). No walk-back
doubling needed.

## Timeout estimate

Formula: ceil(1.5 * estimated_seed_wall_s * FULL_seeds / smoke_seeds)

Reference: v9 at N=16384 ran ~33min (1980s) for 3 seeds over {4N,8N,16N}.
Per-seed construction cost for C=64N=1048576 is ~4x C=16N=262144 (v9's top).
Estimated per-seed wall at v10: ~4x(660s/3seeds) = ~880s/seed.
5 seeds * 880s = 4400s. Applying 1.5x margin: ceil(6600s).

PROT-019 floor for _n16384 (>=8192): **21600s (6h)**. This is the binding floor.

**timeout_s = 21600**

## Post-ship cap_map decision plan

- HARD_PASS -> LIFT C9 row to 0.85-0.95+; annotate "ceiling past 64N at N=16384 BSC"
- MIDDLE_BAND -> LIFT C9 row to 0.80-0.92; annotate "ceiling located between 20N-64N"
- HARD_FAIL -> cap_map row annotated with RAM-wall note; LIFT unchanged; dispatch
  research probe on RAM-efficient construction
