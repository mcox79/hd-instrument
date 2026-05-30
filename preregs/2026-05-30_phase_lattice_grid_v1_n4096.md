# Pre-registration: phase_lattice_grid_v1_n4096

**Date:** 2026-05-30
**Anchor:** phase_lattice_grid_v1_n4096
**Script:** experiments/exp_phase_lattice_grid_v1_n4096.py
**Queue:** overnight_queue
**Timeout:** 86400s (24h; battery-class scope; flagged for user visibility
under PROT-019 long-run flag)

## Hypothesis

The substrate has a measurable operational envelope across the (beta,
M_frac) plane at N=4096. This anchor delivers populated 6-metric data
for the full 9 x 7 = 63-cell grid x 5 seeds = 315 cell-seeds. Region
labels (A/B/C/D) are derived at analysis-time from the M_c probe result;
interpretation lives in cap_map post-analysis.

THIS IS A CHARACTERIZATION not a verdict-test. "Pass" = sufficient
coverage for envelope map.

## Configuration

- N: 4096 (PROT-018 binding)
- Grid: 9 betas x 7 M_fracs = 63 cells
  - betas: [2, 4, 8, 10, 12, 16, 32, 64, 128]
  - M_fracs (fraction-of-N): [0.25, 0.5, 1, 2, 4, 8, 16]
  - Absolute M = M_frac * 4096 -> M in [1024..65536]
- Seeds: [7, 17, 23, 31, 41] (5)
- Total: 315 cell-seeds. Per-cell-seed checkpoint
  (key = `b<beta>_m<mfrac>_seed<seed>`)
- Smoke: 3 betas x 3 mfracs x 1 seed = 9 cell-seeds

## 6-metric battery (shared with Anchor 2 via experiments/_metric_battery.py)

Same 6 metrics as Anchor 2, computed on a SINGLE substrate setup per
cell (no recompute-per-metric). See Anchor 2 prereg for the metric list
and direction conventions.

## Pre-registered bands (COVERAGE, not verdict-test)

**HARD_PASS:** >= 290/315 cell-seeds populated with all 6 metrics
(>= 92% completion). Equivalent fractional gate: frac_complete >=
290/315 = 0.9206.

**HARD_FAIL:** < 200/315 cell-seeds populated (< 63.5%). Equivalent
fractional gate: frac_complete < 200/315 = 0.6349. Indicates something
systematic broke (most likely OOM on the heaviest cells, or import
failure on the runner).

**MIDDLE_BAND:** 200-289 cell-seeds (frac in [0.635, 0.921)). Partial
map; analysis identifies what failed.

NOTE: this is COVERAGE characterization. The metric values themselves
are the deliverable for cap_map post-analysis -- not bands here.

## Smoke result

Wall: 9.78s. N=1024, 3x3x1 = 9 cells, all populated, all 6 metrics
non-null/non-sentinel. Verdict at smoke = HARD_PASS (9/9 cells; frac=
1.0 >= 0.9206). All cells at smoke scale show ret=1.0, hallu=0.0,
max_iso=0.0 (M << C at small N) -- the phase separation lives at FULL
N=4096. Smoke confirms the codepath is intact and the metric battery
returns valid numbers across the smoke grid.

Effect size at smoke is not informative for the FULL question (smoke is
COVERAGE-only; the FULL grid IS the deliverable). Walk-back gate not
triggered.

## Timeout estimate

- smoke_wall_s = 9.78 (9 cell-seeds at N=1024, CPU)
- FULL_N / smoke_N = 4
- FULL count = 315 cell-seeds vs smoke 9 = 35x
- scaling_exp = 1.5 per cell + linear in cell-count
- formula: ceil(1.5 * 9.78 * 4^1.5 * 35) = ceil(4108) = 4108s nominal
- Heavy cells (M_frac=16 -> M=65536) cost 2-5x mean; conservative
  re-estimate ~ 1.5 * 4108 * 3 = 18486s ~ 5.1h.
- User spec adopts 86400s (24h) per PROT-019 keyword guidance for the
  battery-class scope. Justification: 9-beta x 7-M_frac x 5-seed sweep
  at N=4096 with 6-metric battery per cell; conservative ceiling
  against OOM-recovery overhead.
- Per role-contract "Per-experiment timeout estimation": values > 7200s
  flagged for user visibility (this is one such flag); values > 14400s
  blocked unless user-authorized. **User authorized 86400s explicitly
  in 2026-05-30 dispatch.**

## Formula self-tests (verified at module import)

1. N == 4096 (PROT-018 binding) -- PASS
2. 9 betas x 7 M_fracs == 63 cells -- PASS
3. 63 x 5 seeds == 315 cell-seeds -- PASS
4. M @ M_frac=0.25 N=4096: 1024 -- PASS
5. M @ M_frac=16   N=4096: 65536 -- PASS
6. OOM at FULL max-M (M=65536, N=4096): ~1.4 GB -- under 6 GB -- PASS
7. Cell-key formula: `cell_key(32.0, 1.0, 17) == 'b32_m1_seed17'` -- PASS
8. Cell-key formula: `cell_key(0.25, 0.5, 7) == 'b0p25_m0p5_seed7'` -- PASS
9. Verdict gates: HARD_PASS (290/315), HARD_FAIL (100/315), MIDDLE_BAND
   (250/315) all reachable -- PASS

## Anchor-name binding

`_n4096` suffix -> N_FULL = 4096 enforced via module-level assertion.
queue_add.py exit-6 validator will re-verify.

## Cell-failure handling

The script catches RuntimeError and MemoryError per cell, prints
`CELL_FAILED`, frees the CUDA cache, and continues. Failed cells appear
as absent partials and reduce n_complete (and frac_complete). This is
intentional: HARD_FAIL is reserved for systematic breakage (< 63.5%
completion); partial OOM losses on heavy cells fall through to
MIDDLE_BAND.

## Notes

Anchor 3 of the 3-anchor phase-region characterization batch
(2026-05-30). The 24h timeout is the longest of the batch; ETA depends
on heavy-cell OOM resilience. User explicitly authorized this anchor.
