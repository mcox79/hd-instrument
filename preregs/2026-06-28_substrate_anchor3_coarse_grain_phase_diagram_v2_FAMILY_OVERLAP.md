# Pre-reg: substrate_anchor3_coarse_grain_phase_diagram_v2_FAMILY_OVERLAP

Date: 2026-06-28
Cell author: hdi_exp_dev (Agent Teams)
Anchor: ANCHOR 3 coarse-grain (mechanism-class diversion of v1)
Cell file: `experiments/exp_substrate_anchor3_coarse_grain_phase_diagram_v2_FAMILY_OVERLAP.py`

## Background and motivation

v1 (`exp_substrate_anchor3_coarse_grain_phase_diagram_v1`) landed
**MIDDLE_BAND** on 2026-06-28:
- n_pass_cells=12, n_over_compress=0, boundary_visible=False
- ARM_ULTRAMETRIC recall_all = 1.000 at every (cosine_thresh, n_families)
  tested -- including nf=24 (densest cell at alpha=0.38)
- Capacity_drop_frac rose with density (+0.343 at nf=24) but recall NEVER
  degraded -- substrate is robust at the clean-noise regime v1 swept

**Skunkworks 2x-drill (this turn)**: v1 swept GRANULARITY (cosine_thresh) x
DENSITY (n_families). Both axes test WITHIN-family scatter / cohesion. NEITHER
axis tests inter-cluster DISCRIMINATION. Over-compression is a DISCRIMINATION
failure (substrate merges UNRELATED families into one cluster), not a
cohesion failure. v1 measured the wrong axis.

**v2 mechanism diversion**: introduce a 3rd axis `FAMILY_OVERLAP` = mean
inter-family cosine of family centroids. At FAMILY_OVERLAP=0.9, family
centroids are near-collinear; cosine_thresh-based single-linkage clustering
SHOULD pull these unrelated families into one mega-cluster -> ULTRAMETRIC
recall against TRUTH families DROPS.

**Critical discovery during smoke (this turn)**: v1's `recall_via_lookup`
metric uses the COLLAPSED cluster_lookup -- it counts an argmax that lands in
the SAME COLLAPSED CLUSTER as a hit, even if that argmax is in a different
TRUTH family. This metric tolerates the over-compression failure mode by
construction. v2's PRIMARY metric is `recall_truth_family` which requires the
argmax to be in the SAME PLANTED FAMILY. v1's metric is kept as
`recall_*_v1_metric` for parity audit. The metric pivot is what actually
unblocked the discriminator.

## Mechanism class and discriminator

3-axis phase diagram:
- **Axis 1 GRANULARITY** (`COSINE_THRESH`): [0.70, 0.85, 0.95]
- **Axis 2 DENSITY** (`N_FAMILIES`): [8, 16, 24]
- **Axis 3 FAMILY_OVERLAP** (`rho`): [0.0, 0.3, 0.6, 0.9]

Family centroids constructed as:
```
family_centroid_i = sqrt(1 - rho) * orthogonal_i + sqrt(rho) * shared_basis
```
where orthogonal_i are unit Gaussian random vectors (near-orthogonal at D=1024)
and shared_basis is a single unit vector. Mean inter-family cosine target =
rho. Constructor verified to within +/- 0.10 tolerance per --self-test
(observed cosine 0.003 at rho=0.0 and 0.901 at rho=0.9).

Discriminator (PRIMARY):
```
d_v2_FAMILY_OVERLAP = ULTRA.recall_all(rho=0.0) - ULTRA.recall_all(rho=0.9)
```
- HARD_PASS threshold: d_v2 >= 0.15 in at least one (ct, nf) cell
- HARD_FAIL threshold: max d_v2 < 0.05 in all cells (substrate robust;
  ANCHOR 3 jointly closed as MEASURED_MECHANISM with v1)
- MIDDLE_BAND: 0.05 <= max d_v2 < 0.15 in all cells

## Arms (META_RULE_AF arms-must-differ)

1. `ARM_NO_COLLAPSE` -- baseline, capacity_drop=0 by construction.
2. `ARM_ULTRAMETRIC` -- mechanism under test.
3. `ARM_RANDOM_FLOOR` -- selectivity control (random clusters matching ULTRA
   cluster-sizes; cohesion floor).
4. `ARM_FLAT_NO_OVERLAP` -- POSITIVE CONTROL. Runs ULTRAMETRIC at
   FAMILY_OVERLAP=0.0 ONLY. Reproduces v1's clean regime; recall should
   approach 1.000. Cross-checks the mechanism class is intact (not just the
   discriminator).

## Pre-reg bands

### PHASE_HARD_PASS

`>= 1 (granularity, density)` cell where ALL hold:
- `ULTRA.recall_all(rho=0.0) >= 0.95` (clean regime works)
- `ULTRA.recall_all(rho=0.9) <= 0.80` (over-compression visible)
- `d_v2_FAMILY_OVERLAP >= 0.15` (discriminator clears threshold)
- `cv(ULTRA.recall_all per seed at rho=0.0) <= 0.10` (low seed variance)
- `ULTRA.recall_all(rho=0.0) - ARM_RANDOM_FLOOR.recall_all(rho=0.0) >= 0.10`
  (selectivity floor: ULTRA beats RANDOM_FLOOR at clean regime)

AND `CARDINALITY_OK`: `EXPECTED_N_UNITS = 351` (= 3 ct x 3 nf x 4 rho x 3 arms
x 3 seeds + 3 ct x 3 nf x 1 (POS_CTRL rho=0.0) x 3 seeds = 324 + 27 = 351).
HARD_FAIL if observed < 351.

AND positive-control health: `ARM_FLAT_NO_OVERLAP.recall_all(rho=0.0) >= 0.90`
at SOME cell (mechanism class intact).

AND constructor health: `|observed_inter_family_cosine - rho| <= 0.10` at
every cell (SCRIPT_PRECONDITION).

### PHASE_MIDDLE_BAND

Mechanism observable (`0.05 <= max d_v2 < 0.15`) but no cell clears HARD_PASS
bands.

### PHASE_HARD_FAIL

- Substrate robust (`max d_v2 < 0.05` across all cells) -- jointly closes
  ANCHOR 3 with v1 as MEASURED_MECHANISM; OR
- CARDINALITY_BREACH (`observed_n_units < 351`); OR
- LLM-gate violated (`n_llm_calls > 0`); OR
- SCRIPT_PRECONDITION violation (constructor delivered wrong rho at any cell); OR
- Positive control failed (`ARM_FLAT_NO_OVERLAP.recall_all(rho=0.0) < 0.90` at
  every cell -- mechanism class broken).

## Smoke gate verdict

Smoke ran at full N=1024 (discriminator-must-survive-scale per USER 2026-06-26)
with reduced grid: 2 ct x 1 nf x 2 rho {0.0, 0.9} x 3 arms x 1 seed = 12 cells
+ 2 pos_ctrl = 14 cells.

**Smoke VERDICT: HARD_PASS** at the smoke grid:
- (ct=0.70, nf=16, rho=0.0): ULTRA recall = 1.000 (clean regime)
- (ct=0.70, nf=16, rho=0.9): ULTRA recall = **0.530** (over-compression
  visible; n_qualifying_clusters=1 -- 16 truth-families merged into ONE
  mega-cluster)
- d_v2_FAMILY_OVERLAP = **0.470** (well above 0.15)
- Positive control at rho=0.0: 1.000 (mechanism class intact)
- Selectivity at rho=0.0: ULTRA (1.000) - RANDOM_FLOOR (0.790) = 0.21
  (above 0.10)
- At ct=0.95 (conservative merging): no over-compression even at rho=0.9
  (n_clusters=0, recall=1.0) -- phase structure observable on the ct axis

The smoke result shows the discriminator FIRES at full N (no scale-survival
risk). Full dispatch authorized.

## Substrate-only-decode gate

`n_llm_calls = 0` by construction. Cell does NumPy linear algebra only; no
torch / no LLM call sites.

## Disciplines compliance checklist

- ASCII-only: yes (no unicode, no em-dashes, no emojis).
- META_RULE_AF (arms-must-differ): yes (4 distinct mechanisms).
- META_RULE_H (CARDINALITY_OK): yes (EXPECTED_N_UNITS=351 declared + verified
  in verdict).
- META_RULE_S (discriminator-must-survive-scale): yes (smoke at full N=1024).
- META_RULE_AF/three-smoke-disciplines: yes (no silent `except:` blocks; smoke
  FIRES the discriminator at rho=0.9; band-floor handling defaults to MIDDLE_BAND
  not HARD_PASS).
- PROT-018: no `_n<N>` suffix in anchor (no constraint).
- PROT-019: no `_n>=4096` (no timeout floor).
- PROT-020: NumPy-only -> remote_cpu_queue (NOT overnight_queue).
- PROT-021: timeout 3600s < 14400s threshold -- no checkpoint requirement (but
  cell uses `_seed_checkpoint` defensively anyway).
- PROT-022: no `# KB_REFERENT:` declarations (no referent dependency).
- Substrate-only-decode gate: yes.
- Self-test: PASS (constructor + monotonicity + discriminator-fires-at-test-point).
- Smoke: PASS at full N=1024 with d_v2=0.470 at one cell.

## Dispatch

- Queue: `remote_cpu_queue` (NumPy; light cell)
- Timeout: 3600s (1hr; smoke wall-s = 16.2s; estimate
  `1.5 * 16.2 * (351/14) * 3 = 1828s` rounded up to 3600s for ~2x safety)
- Seeds: [7, 17, 23] (3-seed)
- N=1024 (PROT-018 OK)

## Expected outcome priors

P(HARD_PASS) ~ 0.85 -- smoke already cleared discriminator; failure mode
would be cell-by-cell cv exceeding 0.10 across seeds 17/23, or some other
seeds not reproducing the rho=0.9 over-compression. Conservative downward
prior adjustment because the smoke result was the FIRST seed to clear; 2x
seeds remaining to confirm.

P(MIDDLE_BAND) ~ 0.10 -- if seed 17 or 23 produces unusually high
ult_9_recall (e.g. 0.85+) the cv constraint or band threshold could push to
MIDDLE_BAND.

P(HARD_FAIL) ~ 0.05 -- seed effects swamping discriminator is the main risk.
Cardinality and substrate-only-decode gates are by-construction satisfied.

## Notes / known limitations

1. The constructor delivers rho within 0.10 tolerance, not exact. This is
   because Gaussian-random orthogonals at finite D=1024 have non-zero inner
   product among themselves; the mixing formula targets MEAN inter-family
   cosine but individual pairs scatter. Tolerance check in verdict.
2. The v1-parity metric `recall_*_v1_metric` is kept in the per-cell record
   for downstream comparison; it should be FLAT in rho (v1's bias). Not
   used in verdict computation.
3. At cosine_thresh=0.95 (very conservative), no over-compression is
   expected even at rho=0.9 because the threshold is tighter than
   inter-family cosines achievable by the linkage. This is correct behavior
   and surfaces in the phase diagram.
