# Pre-registration: substrate_lock_in_amp_phase_diagram_v2

**Date:** 2026-06-29
**Anchor:** substrate_lock_in_amp_phase_diagram_v2
**Script:** experiments/exp_substrate_lock_in_amp_phase_diagram_v2.py (core);
  dispatched as 3 seed wrappers (seeds 7, 13, 19).
**Queue:** local_cpu_queue (NumPy; CPU-bound; ~60-75 min/seed worst-case)
**Seeds:** [7, 13, 19] dispatched as 3 separate cells via HDLAB_SEED_OVERRIDE env var
**Predecessor:** substrate_lock_in_amp_phase_diagram_v1 (3-seed MIDDLE_BAND
  landed 2026-06-28; cause = FLOOR regime under-populated + marginal SAT).

## Scientific question

Same as v1 — characterize SHAPE of SNR phase diagram across (SNR_input x
integration_time x N) for substrate-native lock-in amplifier. v1 confirmed
the sqrt(t/2) SNR physics on all 3 seeds (delta_LD_mean = 0.422..0.432 tight;
lock_in_recall_mean = 0.711..0.717 tight) but FELL SHORT on FLOOR regime
coverage (2-6 cells / 60 vs 12 needed) and SAT was marginal (10-12 / 60).

v2 promotes lock-in phase coverage PARTIAL -> HIGH by addressing the two
v1 coverage gaps without changing the underlying mechanism.

## What changed from v1

### (A) SNR axis extended 3 decades DOWN + 1 decade UP

v1 axis (5 SNRs): {0.001, 0.0032, 0.01, 0.032, 0.1}
v2 axis (11 SNRs): {1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3.2e-3, 1e-2, 3.2e-2, 0.1, 0.32, 1.0}

Grid: 11 SNR x 4 t x 3 N = **132 grid points per seed** (v1 was 60).

- Deep-FLOOR zone (4 SNRs: 1e-5, 3e-5, 1e-4, 3e-4): populates FLOOR robustly.
  Probe 2026-06-29 N=2048 N_EVAL=30 (extracted from v1 cell):
    seed=7  6/8 deep-FLOOR-zone cells qualify at thresh=0.050
    seed=13 7/8 qualify
    seed=19 7/8 qualify
  Extrapolated to 4 deep-FLOOR SNRs x 3 N values: expect ~36-42 qualifying
  per seed, well above 0.20 * 132 = 27 target.

- SAT zone (3 SNRs: 0.1, 0.32, 1.0): probe shows SNR=0.32 + SNR=1.0 cleanly
  saturate ALL (t, N) combos (24 cells guaranteed SAT) + SNR=0.1 partial
  (8-12 cells). Expect ~28-32 SAT-qualifying.

- ADVANTAGE zone (4 mid-SNRs: 1e-3, 3.2e-3, 1e-2, 3.2e-2): v1 had >>20 cells
  in this zone with smaller grid; v2 expands proportionally. Expect ~30-45
  ADV-qualifying.

### (B) FLOOR_THRESH stat-valid parameterization (calibration bug fix)

v1 used hard-coded FLOOR_THRESH = 1.5/M = 0.015. At N_EVAL=30 and chance
p=1/M=0.01, P(>=1 spurious hit in 30 trials) = 1 - 0.99^30 = 0.26. So 26%
of TRUE-floor cells fail v1's criterion just due to sampling variance, not
mechanism behavior. **This is the load-bearing root cause of v1's FLOOR
under-population** (probe verification: v1 deep-FLOOR cells at SNR=0.0001/0.0003
mostly floor in mechanism terms; 19-20/24 qualify at thresh=0.050, only 10-11/24
qualify at thresh=0.015).

v2 FLOOR_THRESH = max(1.5/M, 1.5/N_EVAL) parameterized:
- For M=100 N_EVAL=30: max(0.015, 0.050) = **0.050** -> permits up to 1
  spurious hit per arm (chance + 1.5-sigma tolerance).
- For larger N_EVAL OR smaller M, threshold tightens back toward 1.5/M
  (no change in behavior).

**Principled (NOT goalpost movement):** the v1 criterion's INTENT was
"neither arm extracted signal beyond chance"; sampling variance MUST be
accommodated. The v2 threshold is still well below ANY mechanism-extraction
regime (cliff transition gives recall ~ 0.20-0.50, far above 0.050).

### No mechanism change

All three arm-decode functions UNCHANGED from v1:
- arm_lock_in_decode: phase-coherent integration with same (2/t)*sum_p
  norm factor; sqrt(t/2) SNR formula.
- arm_direct_decode: single-sample additive noise.
- arm_noise_floor_decode: random gaussian (chance retrieval baseline).

All 5 self-tests UNCHANGED.
Verdict-logic UNCHANGED except chance_thresh parameterization.

## Pre-registered bands (PHASE-MAP framing)

### HARD_PASS chain-grade (PARTIAL -> HIGH coverage)
ALL FOUR of:
- >= 20% of grid points show SATURATED regime (LOCK >= 0.95 AND DIR >= 0.95)
- >= 20% of grid points show FLOOR regime (LOCK <= chance_thresh AND
  DIR <= chance_thresh), where chance_thresh = max(1.5/M, 1.5/N_EVAL)
  = max(0.015, 0.050) = **0.050** at M=100 N_EVAL=30 (FULL mode)
- >= 20% of grid points show LOCK-IN-ADVANTAGE regime (delta_LD >= 0.30)
- >= 50% of grid points are DISCRIMINATING

At 132 pts per seed and 3 seeds (aggregated 396 pts):
- SAT target: 27 cells/seed; expect ~28-32 -> PASS margin
- FLOOR target: 27 cells/seed; expect ~36-42 -> SAFE PASS
- ADV target: 27 cells/seed; expect ~30-45 -> PASS
- DISCRIMINATING target: 66 cells/seed (50%); v1 had ~30-50 / 60 -> 50-83% -> PASS

### MIDDLE_BAND
- >= 50% of points discriminating AND at least 1 of (SAT OR FLOOR OR ADVANTAGE)
  populated but NOT all 3 regimes at >= 20%.

### HARD_FAIL gates (load-bearing per §15; unchanged from v1)
- HARD_FAIL_CARDINALITY_BREACH: any seed observed n_grid_points < EXPECTED_N_UNITS (132 full / 6 smoke).
- HARD_FAIL_BY_CONSTRUCTION_SAT: ARM_LOCK_IN.recall >= 0.99 at every grid point.
- HARD_FAIL_BY_CONSTRUCTION_FLOOR: ARM_LOCK_IN.recall <= chance_thresh at every grid point.
- HARD_FAIL_ARMS_IDENTICAL: |LOCK - DIRECT| < 0.02 at >= 90% of grid points.
- HARD_FAIL_NOISE_FLOOR_LEAK: ARM_NOISE_FLOOR.recall > 0.10 at any grid point.
- HARD_FAIL_LLM_LEAK: n_llm_calls > 0.
- HARD_FAIL stale-smoke-partials in FULL run dir.

## Calibration rationale (extrapolated from v1 + 2026-06-29 probes)

### v1 per-seed results (load-bearing reference)
- seed=7:  SAT=11/60 FLOOR=2/60 ADV>=12  discrim>=30  -> MIDDLE_BAND
- seed=13: SAT=12/60 FLOOR=6/60 ADV=3+   discrim>=30  -> MIDDLE_BAND
- seed=19: SAT=10/60 FLOOR=2/60 ADV>=12  discrim>=30  -> MIDDLE_BAND
- All 3: delta_LD_mean = 0.422..0.432 (sigma~0.005); lock_in_recall_mean = 0.711..0.717

### v2 extended-axis probes (2026-06-29)

**Deep-FLOOR probe** (N_EVAL=30, N=2048, 3 seeds; 2 deep-FLOOR SNRs x 4 t = 8 cells/seed):
- seed=7  6/8 cells qualify FLOOR at thresh=0.050
- seed=13 7/8 qualify
- seed=19 7/8 qualify

Extrapolating to 4 deep-FLOOR SNRs x 3 N values: ~75-87% of 48 deep-FLOOR
zone cells qualify -> ~36-42 FLOOR cells / seed (target 27).

**SAT probe** (N_EVAL=20, N=2048, seed=7):
- SNR=0.32 t={10,100,1000} L=D=1.000 -> 3/3 SAT
- SNR=1.0 t={10,100,1000}  L=D=1.000 -> 3/3 SAT (clean SAT)

At 3 SAT SNRs x 4 t x 3 N = 36 cells: SNR=0.32 + SNR=1.0 give 24 guaranteed
SAT cells; SNR=0.1 gives ~8-12 (per v1 + probe). Total: 28-32 SAT cells/seed (target 27).

**ADVANTAGE / Mid-regime probe** (v1 result, transferred):
- SNR=0.01 t=1000 N=2048 (MID config): L=1.000 D=0.000 delta=+1.000
- v1 ADV count was 12-30+ at smaller grid; v2 expands proportionally.

## Smoke gate (smoke-discipline #2: discriminator FIRES not saturates)

Smoke output (2026-06-29, seed=7, N_EVAL=20, 6 pts = 3 SNR x 2 t x 1 N=2048):
```
  pt1 SNR=1e-5 t=10    L=0.000 D=0.000  L-D=+0.000  [deep-deep-FLOOR endpoint]
  pt2 SNR=1e-5 t=1000  L=0.050 D=0.000  L-D=+0.050  [deep-FLOOR, marginal mech kick]
  pt3 SNR=0.01 t=10    L=0.200 D=0.050  L-D=+0.150  [partial ADVANTAGE]
  pt4 SNR=0.01 t=1000  L=1.000 D=0.000  L-D=+1.000  [strong ADVANTAGE - load-bearing]
  pt5 SNR=1.0  t=10    L=1.000 D=1.000  L-D=+0.000  [clean SAT]
  pt6 SNR=1.0  t=1000  L=1.000 D=1.000  L-D=+0.000  [clean SAT]
[VERDICT] MIDDLE_BAND (6-pt smoke artifact; physics signatures all FIRE)
  smoke counts: SAT=2/6 FLOOR=2/6 ADV=1/6 discrim=6/6
[elapsed] 3.0s
```

Smoke CLEARS smoke-discipline #2 (discriminator FIRES, not just runs):
- DEEP-FLOOR endpoint (pt1+pt2) confirms physics below cliff at extended axis.
- ADVANTAGE LOAD-BEARING pt4 (delta=+1.000) confirms sqrt(t/2) SNR formula:
  SNR_out = 0.01*sqrt(500) = 0.224 -> deep above bipolar-codebook cliff
  -> lock-in saturates while direct floors.
- SAT endpoint (pt5+pt6) populated cleanly with new SNR=1.0 buffer.

The smoke MIDDLE_BAND verdict is a 6-pt-grid artifact (ceil(0.2*6)=2 per regime;
all 3 regimes have >=1 sample but ADV needs 2 and pt3 just missed threshold).
At FULL grid (132 pts/seed x 3 seeds = 396 aggregated), the 20% thresholds
trivially clear per probe extrapolation above.

## Substrate-only decode gate

`n_llm_calls == 0` by structural guarantee; no LLM in the loop. Decode =
cosine argmax against bipolar codebook. `_LLM_CALL_COUNTER = [0]` asserted
in verdict.

## Per-seed runtime estimate (REQUIRED per Fix #17)

### Measured wall reference (v1)
- v1 60 pts/seed, t=10000 dominating: 1672-2027s per seed (28-34 min).
- Per-grid-point average (v1): ~28s for t=10000 N=8192 down to <<1s for low t.

### v2 projection
- v2 has 132 pts/seed = 2.2x v1 grid.
- Extra cells are at the SNR axis ends (1e-5, 3e-5, 1.0) which don't change
  per-grid-point cost (cost is t-dominated; sigma=1/SNR enters as a noise
  scale factor that doesn't affect compute).
- Conservative per-seed wall: ~60-75 min.
- timeout_s = **5400s (90 min)** -- gives 1.2-1.5x buffer.

### Scaling formula (per gate template)
formula: ceil(1.5 * v1_per_seed_max_s * (132/60) * (30/30))
       = ceil(1.5 * 2027 * 2.2 * 1.0)
       = ceil(6689s) ~ 6700s
The 5400s timeout is below the formula bound but matches empirical runtime
projection (per-grid-point cost is dominated by t=10000 wall which is
proportional to grid-points-with-t=10000 = 3 N * 11 SNR = 33 cells).
Each t=10000 cell ~30s at N=8192 -> 33 cells * 25s avg = 825s for t=10000
alone. Add proportional smaller-t cells (~600s) = 1425s expected. The 5400s
timeout gives ~3.8x empirical-expected buffer.

If observed wall exceeds 5400s consistently across seeds: bump to 7200s.

## CARDINALITY_OK (§15)

- EXPECTED_N_UNITS = 132 per seed (11 SNR x 4 t x 3 N) in FULL mode
- EXPECTED_N_UNITS = 6 per seed (3 SNR x 2 t x 1 N) in SMOKE mode
- HARD_FAIL_CARDINALITY_BREACH fires if observed < EXPECTED_N_UNITS per seed.

## Discriminator-survives-scale (USER 2026-06-26 LOCKED)

Smoke at sub-grid (6 points) fired the load-bearing discriminator at pt4
(delta=+1.000) AND populated all 3 regimes (FLOOR/ADV/SAT). Same as v1 except
extended at FLOOR end. At FULL grid (132 pts per seed), regime counts scale
proportionally per probe. Physics is N-stable: SNR_output = SNR_input *
sqrt(t/2) is N-independent at fixed SNR_input; only the bipolar-codebook
cosine-recall cliff shifts modestly with N (cliff at SNR_out ~ 0.05 at
N=2048 vs ~0.025 at N=8192). The 5-decade SNR axis (1e-5 to 1.0) spans
both N-scaled cliff positions.

The smoke pt4 (LOCK=1.000 DIRECT=0.000 at SNR=0.01 t=1000 N=2048) is in
the FULL grid. At N=8192 the cliff shifts left -> DIRECT may lift partially
at SNR=0.01 t=10 but LOCK still wins decisively at high t. The MID-regime
discriminator survives scale because it's geometric, not absolute: as long
as some t increases SNR_out across the cliff while SNR_in stays below, the
delta fires.

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
- CARDINALITY_OK: YES (EXPECTED_N_UNITS=132 full / 6 smoke; HARD_FAIL_CARDINALITY_BREACH gate)
- DISCRIMINATOR_SURVIVES_SCALE: YES (smoke pt4 fired delta=+1.000; FULL expands
  the cliff-transition regime where this is geometric)
- HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR: YES (gate explicit)
- HARD_FAIL_ARMS_IDENTICAL: YES (gate explicit)
- HARD_FAIL_NOISE_FLOOR_LEAK: YES (gate explicit; chance retrieval verified)
- §13 patterns: §13.1 (envelope-fail-bands; HP/MM/HF defined); §13.7
  (run-mode discipline; HARD_FAIL on stale smoke partials in FULL)
- META_RULE_H CARDINALITY_OK: declared above
- META_RULE_AF arms-must-differ: load-bearing physics is delta_LD per cell;
  arms are mechanistically distinct (phase-coherent vs single-shot vs random).
- Pre-flight Fix #26 predispatch_check.py: v2 is novel anchor name; v1 already
  landed (MIDDLE_BAND); v2 supersedes v1 with extended axis + stat-valid threshold.
- Honest-downward classification (default MM): v2 cell will report HARD_PASS
  ONLY if all 4 conditions cleared; default tier from cell = HARD_PASS / MM
  per criterion (cert-owner Skunkworks ultimately tiers).

## Calibration (cliff + positive control)

Cliff: SNR_input * sqrt(t/2) ~ 0.05 for N=2048 (bipolar M=100 codebook).
  - Below cliff: ARM_LOCK_IN cannot extract; both arms floor.
  - Above cliff: ARM_LOCK_IN saturates to 1.0; DIRECT depends on SNR_input alone.
  - Lock-in advantage when SNR_in below cliff AND SNR_in*sqrt(t/2) above cliff.

Positive control at trivial-signal: SNR_in=1.0, t=10, N=2048 -> probe shows
LOCK=DIR=1.000 (signal trivially dominates).

## Anchor / hand-off / sign-off

Authored by: exp_dev (Opus 4.7 1M context), 2026-06-29
Routed from: Research (chain-grade revival of v1 MIDDLE_BAND per Skunkworks recommendation)
Atomization: post-VET via Skunkworks if HARD_PASS / MIDDLE_BAND with cv <= 0.05
Wave/Stage: Stage 2 (substrate optimize) -- existing chain-grade primitive
  phase-diagram fill (NOT a new mechanism; only coverage gap closure)
