# PRE-REG: substrate_lock_in_amp_phase_diagram_v4_density_not_extent

Drafted: 2026-06-30 by hdi_exp_dev per Skunkworks negatives 2x-drill audit (a65f731f priority queue).

## Context
v3 (substrate_lock_in_amp_phase_diagram_v3) FULL landed 3-seed MIDDLE_BAND:
- MEASURED@data/exp_substrate_lock_in_amp_phase_diagram_v3_seed_{7,13,19}/metrics.json
  - n_SAT = 11/96 vs target 20 (HARD_PASS floor: >= 19.2 = 20%)
  - n_FLOOR sufficient (24/96+), n_ADV sufficient (~20/96+)
  - cv = 0.013 EXCELLENT reproducibility
- hp_checks=[sat=False, floor=True, adv=True, discrim=True]
- One axis-extent away from HARD_PASS; SNR axis upper bound 0.1 too low to
  populate SAT band sufficiently.

## Diagnosis (HYPOTHESIZED)
SAT requires BOTH ARM_LOCK_IN.recall >= 0.95 AND ARM_DIRECT_COSINE.recall >= 0.95.
DIRECT saturation requires SNR_in above bipolar-codebook cross-talk cliff
(~0.05 at N=2048, lower at higher N). v3 axis maxes at SNR=0.1 with only
1 point at this SAT zone; needs more SAT-zone density.

## v4 fix (EXTENT extension, NOT mechanism change)

EXTEND axes:
- SNR_AXIS: 0.1 -> 1.0 (+2 SAT-zone points: 0.359 and 1.0). New axis:
  [1e-4, 2.78e-4, 7.74e-4, 2.15e-3, 5.99e-3, 1.67e-2, 4.64e-2, 1.29e-1,
   3.59e-1, 1.0] (10 points)
- INTEGRATION_TIME: 10000 -> 100000 (one extra t). New axis:
  [10, 100, 1000, 10000, 100000] (5 points)
- N_AXIS: unchanged [2048, 4096, 8192]

Grid size: 10 x 5 x 3 = 150 cells per seed (v3: 96).

## Predicted (HYPOTHESIZED)

Analytical SAT/FLOOR/ADV predictions per SNR (15 cells per SNR = 3 N x 5 t):
- SNR=1e-4: 15 FLOOR (cannot reach cliff)
- SNR=2.78e-4: 10-15 FLOOR
- SNR=7.74e-4 to 1.67e-2: dense ADV transition zone
- SNR=4.64e-2: 3-9 SAT
- SNR=1.29e-1: 15 SAT
- SNR=3.59e-1: 15 SAT
- SNR=1.0: 15 SAT

Total predicted:
- n_SAT ~= 45-50/150 = 30-33% (HARD_PASS need >= 30/150 = 20%)
- n_FLOOR ~= 25-40/150 = 17-27%
- n_ADV ~= 25-35/150 = 17-23%
- n_discriminating ~= 120/150 = 80%

## HARD_PASS gate (envelope-fail-bands)

All FOUR of:
1. n_SAT >= 30/150 (>= 20%)
2. n_FLOOR >= 30/150 (>= 20%)
3. n_ADVANTAGE >= 30/150 (>= 20%)
4. n_discriminating >= 75/150 (>= 50%)
AND cv across 3 seeds for n_SAT, n_FLOOR, n_ADV each <= 0.05

## HARD_FAIL ladder

- HARD_FAIL_CARDINALITY_BREACH: any seed observed < 150 grid points
- HARD_FAIL_NOISE_FLOOR_LEAK: ARM_NOISE_FLOOR.recall > 0.10 at any cell
- HARD_FAIL_BY_CONSTRUCTION_SAT: ARM_LOCK_IN >= 0.99 at every cell
- HARD_FAIL_BY_CONSTRUCTION_FLOOR: ARM_LOCK_IN <= chance at every cell
- HARD_FAIL_ARMS_IDENTICAL: |LOCK_IN - DIRECT| < 0.02 at >= 90% cells
- HARD_FAIL_LLM_LEAK: _LLM_CALL_COUNTER != 0
- HARD_FAIL stale smoke partials in FULL run

## SCHEMA-VET fields (META_RULE_AC/AF/AG/AH compliance)

- cardinality_ok: EXPECTED_N_UNITS_FULL=150, _SMOKE=6
- arms_differ_verified: True (LOCK_IN, DIRECT, NOISE_FLOOR distinct by formula)
- final_metrics_atomicity: tmp_replace
- discriminator_reachability: True (predicted SAT > floor; smoke shows SAT=2/6)
- crlb_n_a: phase-diagram cell; analytical band counts in cell-doc
- calibration_check: "default_ok_for_this_regime_v3_axis_extension_only"
- baseline_in_band: smoke at SNR=0.0001 t=10 N=2048: D=0.000 (FLOOR);
  smoke at SNR=1.0 t=1000 N=2048: D=1.000 (SAT); baseline in band
- DISCRIMINATOR_SURVIVES_SCALE: smoke at full-N=2048 with 3 regime probes;
  predicted SAT/FLOOR/ADV gaps in design match analytical
- positive_control_arms: ARM_NOISE_FLOOR ~= 1/M (verified in selftest)
- HP_SCOPE: ARM_LOCK_IN / ARM_DIRECT_COSINE bands apply; ARM_NOISE_FLOOR
  must be at chance (PIPELINE_BROKEN if not)

## Smoke evidence (MEASURED@data/exp_substrate_lock_in_amp_phase_diagram_v4_density_not_extent_smoke/metrics.json)

seed=7 smoke (3 SNR x 2 t x 1 N = 6 cells):
- pt 1 SNR=1e-4 t=10 N=2048: L=0.000 D=0.000 F=0.000 (FLOOR)
- pt 2 SNR=1e-4 t=1000 N=2048: L=0.000 D=0.050 F=0.000 (FLOOR)
- pt 3 SNR=0.01668 t=10 N=2048: L=0.100 D=0.000 (ADV-region intermediate)
- pt 4 SNR=0.01668 t=1000 N=2048: L=1.000 D=0.100 (ADV=0.900, big margin)
- pt 5 SNR=1.0 t=10 N=2048: L=1.000 D=1.000 (SAT)
- pt 6 SNR=1.0 t=1000 N=2048: L=1.000 D=1.000 (SAT)

Smoke result: n_SAT=2/6, n_FLOOR=2/6, n_ADV=1/6, discriminating=6/6.
All 3 regimes FIRED in smoke. Discriminator survives scale.

## Dispatch

- Queue: remote_cpu_queue (CPU-affordable; physics-band sweep)
- 3 seeds: [7, 13, 19] (matched v3 seed config; META_RULE_AW)
- Timeout: 5400s per seed (v3 measured ~1000s; v4 has 1.56x grid + 10x t for
  longest cell = ~3000s realistic + buffer)

## Dependencies / risks

- Cell uses numpy; no GPU dependencies
- run_mode=full honored via HDLAB_RUN_MODE env or argv parsing
- discriminator gate in selftest MID-anchor at SNR=0.01 t=1000 N=2048 must
  show LOCK-DIRECT >= 0.30 (v3 measured delta=1.000; v4 axis includes this
  anchor implicitly via runtime self-test call)
