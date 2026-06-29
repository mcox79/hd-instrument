# Pre-registration: substrate_anchor3_coarse_grain_phase_diagram_v1

**Date:** 2026-06-28
**Anchor:** substrate_anchor3_coarse_grain_phase_diagram_v1
**Queue:** local_cpu_queue (numpy-only; ~7-10 min wall at full grid; CPU-cheap)
**N:** 1024 (no _n suffix per PROT-018; phase-diagram axes are the production variables)
**Seeds:** 3 (7, 17, 23)

## Scientific question
What is the operating regime for the substrate's ultrametric coarse-graining
mechanism (ANCHOR 3) as a function of granularity (COSINE_THRESH) and density
(alpha = N_TOTAL / N)? Is there an observable phase boundary between
"over-compression" (recall destroyed) and "healthy compression" (capacity gain
with discrimination intact)?

This v1 takes ANCHOR 3 coverage from MID (a single point in granularity space
proven chain-grade by `cortex_ultrametric_clustering_coarse_grain_v1`) to HIGH
(2D map across granularity x density with phase boundary visible). Companion
to the parallel ANCHOR 4 time-decay phase-fill.

## Phase-diagram grid

**Axis 1 -- GRANULARITY (COSINE_THRESH):**
- COSINE_THRESH_GRID = [0.70, 0.80, 0.85, 0.90, 0.95]
- 0.70 = aggressive merging (multi-family atoms collapse together; expected
  over-compression at low density too)
- 0.85 = base-cell canonical (chain-grade reference)
- 0.95 = conservative (only the tightest mini-clusters merge; expected small
  capacity gain; discrimination preserved)

**Axis 2 -- DENSITY (n_families with ATOMS_PER_FAMILY=8 fixed):**
- N_FAMILIES_GRID = [4, 8, 16, 24]
- n_atoms_total = N_FAMILIES * 8 + 200 = {232, 264, 328, 392}
- alpha (=n_atoms/N) at N=1024 = {0.226, 0.258, 0.320, 0.383}
- Higher density -> more capacity pressure -> more benefit from coarse-grain;
  discriminator expected to LIVE on this axis (selectivity vs random).

**Arms (META_RULE_AF arms-must-differ):**
- ARM_NO_COLLAPSE (baseline; capacity_drop=0 by construction)
- ARM_ULTRAMETRIC (mechanism under test)
- ARM_RANDOM (selectivity control: same n_atoms collapsed, but grouped
  randomly not by cosine similarity)

**CARDINALITY_OK (META_RULE_H discipline):**
- EXPECTED_N_UNITS = 5 thresholds x 4 densities x 3 arms x 3 seeds = 180
- HARD_FAIL_CARDINALITY_BREACH if observed_units < 180.

## Pre-registered bands

**PHASE_HARD_PASS:**
- >=1 (threshold, density) cell where ALL of:
  - ULTRA.cap_drop_frac >= 0.20
  - ULTRA.recall_clustered >= 0.80
  - ULTRA.recall_unclustered >= 0.85
  - cv(ULTRA.recall_clustered across seeds) <= 0.05
  - d_ULTRA_vs_RND = ULTRA.recall_all - RANDOM.recall_all >= 0.05
- AND phase boundary observable: at the PASS density, exists another
  threshold cell where ULTRA over-compresses
  (ULTRA.recall_clustered < 0.80 AND ULTRA.cap_drop >= 0.20).
- AND CARDINALITY_OK: observed_units == 180.

**PHASE_MIDDLE_BAND:**
- PASS cells exist but phase boundary not visible at this grid resolution
  (over-compression cell at PASS density missing). Mechanism observable;
  phase structure under-resolved.

**PHASE_HARD_FAIL:**
- No cell clears HARD_PASS bands, OR
- max(d_ULTRA_vs_RND) across all cells < 0.02 (mechanism has no selectivity
  above random anywhere on the diagram), OR
- CARDINALITY_BREACH (observed_units < 180).

## Calibration rationale
- 0.20 cap_drop floor: matches base-cell HARD_PASS (cortex_ultrametric_v1 at
  0.85 thresh, nf=8 achieves cap_drop=0.212).
- 0.80 recall_clustered floor: matches base-cell HARD_PASS band.
- 0.85 recall_unclustered floor: matches base-cell band.
- 0.05 cv: standard seed-stability discipline (Skunkworks cv<=0.05).
- 0.05 d_ULTRA_vs_RND: matches base-cell observed delta=+0.104; conservative
  half of that. Below 0.02 = no selectivity (HARD_FAIL gate per
  base-cell verdict logic, scaled to phase diagram).

## Discriminator-survives-scale (USER 2026-06-26 discipline)

Smoke uses **full N=1024** (NOT scaled-down N) so the discriminator is tested
at its production-scale operating point. Smoke grid reduces axes only:
- COSINE_THRESH_GRID_SMOKE = [0.70, 0.90] (low + high end)
- N_FAMILIES_GRID_SMOKE = [8, 24] (low + high density)
- SEEDS_SMOKE = [7] (single seed)
- 2 x 2 x 3 arms x 1 seed = 12 smoke cells

**Smoke gate (discriminator FIRES):** at least one of the 4 (threshold,
density) cells in smoke must show d_ULTRA_vs_RND >= 0.05. Otherwise
discriminator does not survive scale -> NO full dispatch.

This satisfies the discriminator-must-survive-scale rule via Method A
(smoke at full-N): if the mechanism's selectivity floor (0.05) is not
detectable at smoke=full-N on the suspected phase-boundary cells, the
mechanism is mis-calibrated for full-grid dispatch.

## Three smoke disciplines (USER 2026-06-26)
1. **No silent except blocks** -- record + halt. The cell uses explicit
   `raise ValueError` for unknown arms; no bare `except:`.
2. **Smoke must FIRE the discriminator** -- the smoke gate above enforces this
   (d_ULTRA_vs_RND >= 0.05 in at least one cell, not just "cell runs").
3. **Band-floor PASS reads MIDDLE_BAND not HARD_PASS** -- the HARD_PASS gate
   requires the phase boundary to be VISIBLE (over-compression cell present);
   PASS-only without boundary -> MIDDLE_BAND.

## N-suffix section
NO _n<N> suffix per PROT-018: anchor is a PHASE-DIAGRAM SWEEP across
COSINE_THRESH and N_FAMILIES axes at FIXED N=1024. Production scope is the
2D grid, not a single N. Following the precedent of
`substrate_stage1_integration_NDIM_phase_diagram_v1`.

## Timeout estimate

Smoke wall (laptop CPU, 2x2x3x1=12 cells, N=1024): expected ~10-20s based on
base-cell wall_s of ~0.6s for 3 arms at N=1024 (single (thresh, density) point).
Generation cost is O(N * n_atoms) per density (~hundreds of microseconds);
clustering cost is O(n_atoms^2) per (thresh, density). At nf=24,
n_atoms=392, D matrix is 392^2 = ~150k entries; per-arm wall ~ 0.2-0.4s.
12 smoke cells * 0.3s ~ 4s arm-side; per-density W setup ~1ms. Total
smoke expected ~5-10s.

Full grid (5x4x3x3 = 180 cells, N=1024): scaling factor from smoke = 180/12 = 15x.
Estimated wall ~75-150s. Add safety: 1.5x = ~225s.

ceil(1.5 * smoke_wall_s * 15) = ceil(1.5 * 30 * 15) = 675s upper estimate.

CONSERVATIVE timeout: 1800s (30 min) -- gives generous headroom for CPU
contention, queue waits, and per-seed checkpoint I/O. Well below PROT-021
4h checkpoint floor (cell uses _seed_checkpoint regardless for resume on kill).

timeout_s = 1800

## Disciplines applied
- ASCII-only per feedback_ascii_only_in_scripts
- META_RULE_H CARDINALITY_OK per pre-reg + verdict gate (HARD_FAIL on breach)
- META_RULE_AF arms-must-differ via ULTRA vs RANDOM vs NO_COLLAPSE
- Discriminator-must-survive-scale via smoke at full-N (Method A)
- No silent except blocks (verified in source)
- Smoke fires discriminator (gate above)
- Band-floor = MIDDLE_BAND not HARD_PASS (phase boundary visibility gate)
- PROT-018: no _n<N> suffix (2D phase-diagram sweep)
- PROT-019: N=1024 < 4096 -> no large-N timeout floor
- PROT-020: numpy-only on local_cpu_queue (NOT overnight_queue) -> OK
- PROT-021: cell uses _seed_checkpoint.write_partial for per-seed resume
- A5: cert-owner final tier (this cell pre-reg sets bands; landed-VET decides)
- Honest-downward classification: verdict logic defaults to MIDDLE_BAND when
  PASS cell exists but boundary not visible; defaults to HARD_FAIL on no PASS.

## Cites
- experiments/exp_substrate_anchor3_coarse_grain_phase_diagram_v1.py (this cell)
- experiments/exp_cortex_ultrametric_clustering_coarse_grain_v1.py (base
  primitive; ANCHOR 3 chain-grade reference at single point ct=0.85, nf=8)
- hdlab/ultrametric_clustering.py (substrate primitive)
- preregs/2026-06-24_substrate_stage1_integration_NDIM_phase_diagram_v1.md
  (template precedent for phase-diagram pre-reg)
- USER 2026-06-26 discriminator-must-survive-scale + 3 smoke disciplines
- USER 2026-06-26 cap_map ANCHOR 3 phase-fill MID -> HIGH directive
- META_RULE_H CARDINALITY_OK mandatory for sweep-axis cells
- META_RULE_AF arms-must-differ
