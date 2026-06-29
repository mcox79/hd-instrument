# Pre-registration: substrate_lock_in_amp_phase_diagram_v3

**Date:** 2026-06-30
**Anchor:** substrate_lock_in_amp_phase_diagram_v3
**Script:** experiments/exp_substrate_lock_in_amp_phase_diagram_v3.py (core);
  dispatched as 3 seed wrappers (seeds 7, 13, 19).
**Queue:** remote_cpu_queue (NumPy; CPU-bound; ~30-45 min/seed worst-case)
**Seeds:** [7, 13, 19] dispatched as 3 separate cells via HDLAB_SEED_OVERRIDE env var
**Predecessor:** substrate_lock_in_amp_phase_diagram_v2 (3-seed MIDDLE_BAND
  landed; cause = n_ADVANTAGE hard-capped by geometry of v2's coarse SNR axis).

## Scientific question

Same as v1/v2 -- characterize SHAPE of SNR phase diagram across
(SNR_input x integration_time x N) for substrate-native lock-in amplifier.

v1 confirmed the sqrt(t/2) SNR physics on all 3 seeds (delta_LD_mean = 0.422..0.432;
lock_in_recall_mean = 0.711..0.717) but FELL SHORT on FLOOR + marginal SAT.

v2 extended the SNR axis 5 decades (1e-5 ... 1.0; 11 SNRs) + stat-valid
FLOOR_THRESH. Still landed MIDDLE_BAND. Skunkworks 2x-drill diagnosis:
**n_ADVANTAGE = 1 in v2 FULL because the ADVANTAGE band is the narrow
transition sliver between direct-fail and direct-succeed**, and v2's coarse
SNR axis had only 4 cells in that zone. Extending SNR down adds to FLOOR
count; extending SNR up adds to SAT count. **NEITHER adds ADVANTAGE cells.**

**Axis-density problem, NOT axis-extent problem.**

v3 closes the n_ADVANTAGE shortfall by REPLACING v2's coarse axis with a
DENSE geometric axis in the [1e-4, 0.1] cliff-transition zone.

## What changed from v2 (MECHANISM-CLASS DIVERSION)

### SNR axis REPLACED (not extended)

v2 axis (11 SNRs): {1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3.2e-3, 1e-2, 3.2e-2, 0.1, 0.32, 1.0}
v3 axis (8 SNRs): {1.000e-4, 2.683e-4, 7.197e-4, 1.931e-3, 5.179e-3, 1.389e-2, 3.728e-2, 1.000e-1}

Spacing: log10 increment = 3/7 = 0.4286 -> factor ~2.68 between consecutive pts.
All 8 SNRs are inside the cliff-transition zone for at least one N.

Grid: 8 SNR x 4 t x 3 N = **96 grid points per seed** (v2 was 132).
Smaller grid; HIGHER n_ADVANTAGE density.

### No mechanism change

All three arm-decode functions UNCHANGED from v1/v2:
- arm_lock_in_decode: phase-coherent integration with same (2/t)*sum_p
  norm factor; sqrt(t/2) SNR formula.
- arm_direct_decode: single-sample additive noise.
- arm_noise_floor_decode: random gaussian (chance retrieval baseline).

All 5 self-tests UNCHANGED.
Verdict-logic UNCHANGED (same stat-valid chance_thresh from v2).

## Pre-registered bands (PHASE-MAP framing; UNCHANGED from v2)

### HARD_PASS chain-grade (PARTIAL -> HIGH coverage)
ALL FOUR of:
- >= 20% of grid points show SATURATED regime (LOCK >= 0.95 AND DIR >= 0.95)
  (target: 20 cells/seed; 58 aggregated 3-seed)
- >= 20% of grid points show FLOOR regime (LOCK <= chance_thresh AND
  DIR <= chance_thresh), where chance_thresh = max(1.5/M, 1.5/N_EVAL)
  = max(0.015, 0.050) = **0.050** at M=100 N_EVAL=30 (FULL mode)
  (target: 20 cells/seed)
- >= 20% of grid points show LOCK-IN-ADVANTAGE regime (delta_LD >= 0.30)
  (target: 20 cells/seed; v3 design analytical: 30/seed -> 90/3-seed-aggregated)
- >= 50% of grid points are DISCRIMINATING
  (target: 48 cells/seed)

### Per-(SNR, t) n_ADVANTAGE projection (analytical; cliff_N=2048 ~ 0.05; cliff_N=8192 ~ 0.025)

| SNR_in  | t=10 | t=100 | t=1000 | t=10000 | total (over 3 N) |
|---------|------|-------|--------|---------|------------------|
| 1.00e-4 |   0  |   0   |   0    |   0     |   0              |
| 2.68e-4 |   0  |   0   |   0    |   0     |   0              |
| 7.20e-4 |   0  |   0   |   0    |   3     |   3              |
| 1.93e-3 |   0  |   0   |   2    |   3     |   5              |
| 5.18e-3 |   0  |   2   |   3    |   3     |   8              |
| 1.39e-2 |   1  |   3   |   3    |   3     |  10              |
| 3.73e-2 |   1  |   1   |   1    |   1     |   4              |
| 1.00e-1 |   0  |   0   |   0    |   0     |   0              |
| **TOTAL ADV cells per seed** |       |       |        |         | **30 / 96** |

Per-seed 20% target = 20. Projection 30 cells -> **PASS margin ~50%**.

### Per-(SNR, t) FLOOR / SAT projection

- FLOOR zone (SNR_in * sqrt(t/2) < 0.05/sqrt(N/2048)):
  - SNR_in=1.0e-4: all (t,N) combos floor -> 12 cells
  - SNR_in=2.7e-4: 11/12 floor (only t=10000 N=2048 borderline) -> ~11
  - SNR_in=7.2e-4: 9/12 floor (t=10000 cells transition) -> ~9
  - Subtotal: ~30-32 FLOOR cells (target 20) -> PASS

- SAT zone (both arms saturate; SNR_in > cliff AND SNR_out >> cliff):
  - SNR_in=0.1: all (t,N) combos give direct extract; SAT depending on N -> ~9-12
  - SNR_in=0.037: SAT only at high t -> ~4-6
  - Subtotal: ~13-18 SAT cells (target 20) -> BORDERLINE
  - **NOTE: SAT may MIDDLE_BAND on shortfall.** ADV is the primary lever
    in v3 (closes v2's load-bearing gap); SAT remains marginal. Acceptable
    risk per Skunkworks 2x-drill (cell-mechanism unchanged; v4 could add
    SNR=1.0 if needed; v3 prioritizes ADV closure).

### MIDDLE_BAND
- >= 50% of points discriminating AND at least 1 of (SAT OR FLOOR OR ADVANTAGE)
  populated but NOT all 3 regimes at >= 20%.

### HARD_FAIL gates (load-bearing per §15; UNCHANGED from v1/v2)
- HARD_FAIL_CARDINALITY_BREACH: any seed observed n_grid_points < EXPECTED_N_UNITS (96 full / 6 smoke).
- HARD_FAIL_BY_CONSTRUCTION_SAT: ARM_LOCK_IN.recall >= 0.99 at every grid point.
- HARD_FAIL_BY_CONSTRUCTION_FLOOR: ARM_LOCK_IN.recall <= chance_thresh at every grid point.
- HARD_FAIL_ARMS_IDENTICAL: |LOCK - DIRECT| < 0.02 at >= 90% of grid points.
- HARD_FAIL_NOISE_FLOOR_LEAK: ARM_NOISE_FLOOR.recall > 0.10 at any grid point.
- HARD_FAIL_LLM_LEAK: n_llm_calls > 0.
- HARD_FAIL stale-smoke-partials in FULL run dir.

## Smoke results (2026-06-30, 3 seeds, smoke grid: 3 SNR x 2 t x 1 N = 6 cells)

Per-seed smoke per-(SNR,t,N):

**seed=7:**
```
pt1 SNR=1e-4   t=10   L=0.000 D=0.000 L-D=+0.000 [FLOOR]
pt2 SNR=1e-4   t=1000 L=0.000 D=0.050 L-D=-0.050 [FLOOR]
pt3 SNR=1.39e-2 t=10   L=0.200 D=0.050 L-D=+0.150 [partial ADV]
pt4 SNR=1.39e-2 t=1000 L=1.000 D=0.150 L-D=+0.850 [**STRONG ADV** load-bearing]
pt5 SNR=0.1     t=10   L=1.000 D=0.950 L-D=+0.050 [SAT]
pt6 SNR=0.1     t=1000 L=1.000 D=0.800 L-D=+0.200 [partial SAT, LOCK extends]
```

**seed=13:**
```
pt1 SNR=1e-4   t=10   L=0.000 D=0.000 L-D=+0.000 [FLOOR]
pt2 SNR=1e-4   t=1000 L=0.000 D=0.000 L-D=+0.000 [FLOOR]
pt3 SNR=1.39e-2 t=10   L=0.050 D=0.100 L-D=-0.050 [transition]
pt4 SNR=1.39e-2 t=1000 L=1.000 D=0.100 L-D=+0.900 [**STRONG ADV** load-bearing]
pt5 SNR=0.1     t=10   L=1.000 D=1.000 L-D=+0.000 [SAT]
pt6 SNR=0.1     t=1000 L=1.000 D=0.950 L-D=+0.050 [SAT]
```

**seed=19:**
```
pt1 SNR=1e-4   t=10   L=0.050 D=0.000 L-D=+0.050 [near-FLOOR]
pt2 SNR=1e-4   t=1000 L=0.000 D=0.000 L-D=+0.000 [FLOOR]
pt3 SNR=1.39e-2 t=10   L=0.300 D=0.050 L-D=+0.250 [partial ADV]
pt4 SNR=1.39e-2 t=1000 L=1.000 D=0.050 L-D=+0.950 [**STRONG ADV** load-bearing]
pt5 SNR=0.1     t=10   L=1.000 D=1.000 L-D=+0.000 [SAT]
pt6 SNR=0.1     t=1000 L=1.000 D=0.950 L-D=+0.050 [SAT]
```

**Smoke summary:** discriminator pt4 (the new dense-mid cliff cell at SNR=1.39e-2 t=1000)
fires LOCK=1.000 vs DIRECT=0.05..0.15 -> delta = +0.85 to +0.95 across all 3 seeds.
This is THE load-bearing v3 cell. Tight cv across seeds (~0.05 on delta).

**Smoke verdict (6-pt artifact):** MIDDLE_BAND per cell (each seed individually);
n_ADVANTAGE=1/6 < 2-cell 20% threshold. This is a 6-pt smoke ceiling artifact
(only 1 ADV-band cell in smoke axis); at FULL grid (96 cells / seed) the dense
[1e-4, 0.1] axis populates ADV with ~30 cells per seed per the analytical
projection. Smoke smoke-discipline #2 (discriminator FIRES not just runs) CLEARS.

## Smoke-vs-full discriminator survival (USER 2026-06-26 LOCKED)

Smoke pt4 (SNR=1.39e-2 t=1000 N=2048) is IN the FULL grid. The N=4096
and N=8192 versions of this cell are NOT in smoke but the cliff shifts
LEFT at higher N (cliff=0.05/sqrt(N/2048) -> 0.035 at N=4096, 0.025 at N=8192),
so the cliff transition is SHARPER and ADV survives. The 8-pt geometric
SNR axis in [1e-4, 0.1] guarantees cells INSIDE the [cliff_N=8192, cliff_N=2048]
band at all 3 N values; ADV-band coverage is robust to N-scaling.

## Substrate-only decode gate

`n_llm_calls == 0` by structural guarantee; no LLM in the loop. Decode =
cosine argmax against bipolar codebook. `_LLM_CALL_COUNTER = [0]` asserted
in verdict.

## Per-seed runtime estimate (REQUIRED per Fix #17)

### Measured wall reference

- v1: 60 pts/seed (5 SNR x 4 t x 3 N), 1672-2027s per seed.
- v2: 132 pts/seed (11 SNR x 4 t x 3 N), expected ~60-75 min per seed.
- v3: 96 pts/seed (8 SNR x 4 t x 3 N), expected ~50-65 min per seed.

### Cost driver: t=10000 cells

t=10000 cells dominate compute. v3 has 8 SNR x 3 N = 24 cells at t=10000
(v1 had 15; v2 had 33). Per-cell wall at t=10000 N=8192: ~30s (v1 measurement).
24 t=10000 cells * 30s = 720s for t=10000 alone.
Plus proportional smaller-t cells (~600s).
Total estimated: ~1320-1500s wall per seed (22-25 min).

### timeout_s

formula: ceil(1.5 * v1_per_seed_max_s * (96/60) * (30/30))
       = ceil(1.5 * 2027 * 1.6 * 1.0)
       = ceil(4865s) ~ 5000s

**Set timeout to 5400s (90 min)** to match v2's bound and give ~3-4x buffer
over empirical-expected (1500s).

If observed wall exceeds 5400s consistently: bump to 7200s.

## CARDINALITY_OK (§15)

- EXPECTED_N_UNITS = 96 per seed (8 SNR x 4 t x 3 N) in FULL mode
- EXPECTED_N_UNITS = 6 per seed (3 SNR x 2 t x 1 N) in SMOKE mode
- HARD_FAIL_CARDINALITY_BREACH fires if observed < EXPECTED_N_UNITS per seed.

## META_RULE_AF (arms-must-differ)

Load-bearing physics is delta_LD per cell. Arms are mechanistically distinct:
- ARM_LOCK_IN: phase-coherent integration over t (gain = sqrt(t/2))
- ARM_DIRECT_COSINE: single-sample additive noise (no gain)
- ARM_NOISE_FLOOR: random gaussian guess (chance baseline)

Smoke confirms arms differ at MID-cliff cell: LOCK=1.000 vs DIRECT=0.05..0.15
across all 3 seeds at pt4 (SNR=1.39e-2 t=1000 N=2048).

## Discipline checklist

- PRESERVE_ENV_VARS: HDLAB_QUEUE -- header comment in core + 3 seed wrappers
- No gpu_mandate_check (CPU dispatch OK)
- ARM_BASELINE rail (ARM_DIRECT_COSINE): YES
- 3-arm bracket: YES (LOCK_IN + DIRECT + NOISE_FLOOR)
- Multi-seed FULL >= 3: YES (seeds [7, 13, 19] across 3 dispatches)
- ASCII-only: YES
- Substrate-only decode gate: YES (_LLM_CALL_COUNTER asserted)
- Per-arm metrics-vs-verdict-msg (Fix #28): YES (verdict reads per-grid-point
  per-arm recalls directly)
- CARDINALITY_OK: YES (EXPECTED_N_UNITS=96 full / 6 smoke; HARD_FAIL_CARDINALITY_BREACH gate)
- DISCRIMINATOR_SURVIVES_SCALE: YES (smoke pt4 fired delta=+0.85..+0.95 across
  3 seeds; FULL expands the cliff-transition regime where this is geometric)
- HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR: YES (gate explicit)
- HARD_FAIL_ARMS_IDENTICAL: YES (gate explicit)
- HARD_FAIL_NOISE_FLOOR_LEAK: YES (gate explicit; chance retrieval verified)
- §13 patterns: §13.1 (envelope-fail-bands; HP/MM/HF defined); §13.7
  (run-mode discipline; HARD_FAIL on stale smoke partials in FULL)
- META_RULE_H CARDINALITY_OK: declared above
- META_RULE_AF arms-must-differ: declared above; smoke confirmed
- Pre-flight Fix #26 predispatch_check.py: v3 is novel anchor name; v2 already
  landed (MIDDLE_BAND); v3 supersedes v2 with DENSE [1e-4, 0.1] SNR axis.
- Honest-downward classification (default MM): v3 cell will report HARD_PASS
  ONLY if all 4 conditions cleared; default tier from cell = HARD_PASS / MM
  per criterion (cert-owner Skunkworks ultimately tiers).

## Calibration (cliff + positive control)

Cliff: SNR_input * sqrt(t/2) ~ 0.05/sqrt(N/2048) for N=2048..8192
       (bipolar M=100 codebook).
  - Below cliff: ARM_LOCK_IN cannot extract; both arms floor.
  - Above cliff: ARM_LOCK_IN saturates to 1.0; DIRECT depends on SNR_input alone.
  - Lock-in advantage when SNR_in below cliff AND SNR_in*sqrt(t/2) above cliff.

Positive control at trivial-signal: SNR_in=0.1, t=10, N=2048 -> probe shows
LOCK=DIR=1.000 (signal trivially dominates; ARM_DIRECT extracts directly).

Load-bearing ADV control at MID cliff: SNR_in=1.39e-2 t=1000 N=2048 -> probe
shows LOCK=1.000 DIRECT=0.05..0.15 (3 seeds) -> delta = +0.85 to +0.95.
This cell + its t=10000 / N=4096+8192 variants drive the n_ADVANTAGE count.

## Anchor / hand-off / sign-off

Authored by: exp_dev (Opus 4.7 1M context), 2026-06-30
Routed from: Research (mechanism-class diversion of v2 MIDDLE_BAND per
  Skunkworks 2x-drill diagnosis: n_ADVANTAGE hard-capped by axis-density,
  not axis-extent)
Atomization: post-VET via Skunkworks if HARD_PASS / MIDDLE_BAND with cv <= 0.05
Wave/Stage: Stage 2 (substrate optimize) -- existing chain-grade primitive
  phase-diagram fill (NOT a new mechanism; only coverage gap closure via
  density-shift)
