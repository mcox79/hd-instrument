# Pre-registration: substrate_ultrametric_clustering_phase_diagram_v1

**Date:** 2026-06-28
**Anchor:** substrate_ultrametric_clustering_phase_diagram_v1
**Script:** experiments/exp_substrate_ultrametric_clustering_phase_diagram_v1.py
**Queue:** local_cpu_queue (NumPy; CPU-bound; ~10-30min per seed)
**Seeds:** [7, 13, 19] dispatched as 3 separate cells via HDLAB_SEED_OVERRIDE env var
**Primitive:** hdlab/ultrametric_clustering.py (existing chain-grade; this cell
  fills MID -> HIGH phase coverage per Stage 2 substrate characteristics table)

## Scientific question

The ULTRAMETRIC clustering primitive is chain-grade at one operating point
(N=1024, N_FAMILIES=8, ATOMS_PER_FAM=8; cortex_ultrametric_clustering_coarse_
grain_v1 -> HARD_PASS/MM landing). The primitive's CHARACTERISTICS table
entry reports Stage 2 phase coverage as MID at 70% completeness. What is the
shape of the phase diagram across (n_clusters x cluster_size x N x
tree_depth)? Where does single-linkage agglomerative ultrametric clustering
WIN vs flat k-means; where does it tie; and where does it suffer (e.g., the
classical chain-effect failure)?

## v1 design

### Grid axes (60 points = 5 * 4 * 3 with tree_depth fixed at 2)
- n_top_clusters in {2, 5, 10, 20, 50}
- cluster_size in {10, 50, 100, 500}      [auto-clamped if n_atoms > 5000]
- N (substrate dim) in {2048, 4096, 8192}
- tree_depth fixed at 2 (branch_factor=2; leaves = nc * 2^(td-1))
- TOTAL = 60 grid points per seed

### Hierarchical atom generation
Each top-level cluster splits into branch_factor=2 sub-clusters; each leaf
gets `cluster_size_effective` atoms = center + Gaussian noise per-dim.
Noise per-dim = `NOISE_OVERLAP_BASE * sqrt(log(n_leaf) / n_dim) * sqrt(cs)`
(NOISE_OVERLAP_BASE=0.30; scales noise into the overlap regime where flat
k-means starts mis-assigning boundary atoms).

### Arms (3-arm bracket; per task spec)
- ARM_ULTRAMETRIC: single-linkage agglomerative clustering with cut at
  target_n_clusters = n_leaf (the known ground-truth leaf count). Returns
  per-atom cluster_id.
- ARM_FLAT_KMEANS: spherical k-means at k=n_leaf with 20 iterations.
- ARM_RANDOM_GROUPING: random per-atom assignment in [0, n_leaf).

### Primary discriminator: label-recovery accuracy
For each arm, compute label_recovery_accuracy(true_ids, pred_labels) =
fraction of atoms with correct planted-label match after greedy 1-1 label
permutation on the confusion matrix. Reports per-arm acc_leaf + the deltas
ultra_acc_minus_kmeans and ultra_acc_minus_random.

### Secondary instrumentation: within-vs-between cosine gap
Sampled-pair within/between cosine distinguishes clustering coherence vs
separation; reported per arm as (mean_within, mean_between, gap=within-between).

## Pre-registered bands (PHASE-MAP framing)

### HARD_PASS (chain-grade phase-coverage MID -> HIGH)
ALL FOUR of:
- >= 20% of grid points show separable regime (ARM_ULTRAMETRIC.acc_leaf >= 0.95)
- >= 20% of grid points show chain-failure regime (d_uk_acc <= -0.20,
  ULTRA falls behind KMEANS due to single-linkage chain effect)
- >= 20% of grid points show ultrametric-advantage regime (d_uk_acc >= 0.10)
- >= 50% of grid points are discriminating (|d_uk_acc| > 0.05)
This characterizes the phase diagram in all three relevant regimes; ULTRA's
HIGH-coverage entry on the substrate characteristics table is justified by
explicit mapping of where it wins, ties, and loses.

### MIDDLE_BAND
- >= 50% of points discriminating AND at least 1 of (separable OR
  ultrametric-advantage) but NOT all 3 regimes populated. Phase diagram
  partially mapped; some regimes under-sampled.

### HARD_FAIL gates (load-bearing per §15)
- HARD_FAIL_CARDINALITY_BREACH: any seed observed n_grid_points < EXPECTED_N_UNITS (60).
- HARD_FAIL_BY_CONSTRUCTION_SAT: ULTRA acc_leaf >= 0.99 at every grid point
  (ceiling-saturated; no discrimination).
- HARD_FAIL_BY_CONSTRUCTION_FLOOR: ULTRA acc_leaf <= 0.05 at every grid point
  (mechanism floored).
- HARD_FAIL_ARMS_IDENTICAL: |ULTRA.acc - KMEANS.acc| < 0.02 at >= 90% of
  grid points.
- HARD_FAIL_LLM_LEAK: n_llm_calls > 0 (substrate-only-decode gate violated).

## Calibration rationale

Smoke (8 grid points, seed=7) showed: 6 separable + 2 chain-failure + 4
ultra-advantage + 6 discriminating across the 8-point smoke grid. All three
regimes populated at smoke scale; smoke verdict = HARD_PASS phase-map. At
FULL grid (60 points) the proportion thresholds are 20% (12 points per
regime category) and 50% (30 discriminating). These bands are calibrated on
the smoke result projected linearly to 60 points (smoke ratios:
6/8=75%, 2/8=25%, 4/8=50%, 6/8=75% -> all > 20%/50% thresholds).

## Smoke gate (smoke-discipline #2: discriminator FIRES not saturates)

```
[seed=7] 8 grid points (smoke axes: nc x cs x N = [2,10] x [10,50] x [2048,4096])
  pt1  nc=2 cs=10 N=2048 acc_u=1.000 acc_k=0.650 d_uk=+0.350
  pt2  nc=2 cs=10 N=4096 acc_u=1.000 acc_k=1.000 d_uk=+0.000
  pt3  nc=2 cs=50 N=2048 acc_u=1.000 acc_k=1.000 d_uk=+0.000
  pt4  nc=2 cs=50 N=4096 acc_u=1.000 acc_k=0.765 d_uk=+0.235
  pt5  nc=10 cs=10 N=2048 acc_u=1.000 acc_k=0.805 d_uk=+0.195
  pt6  nc=10 cs=10 N=4096 acc_u=1.000 acc_k=0.805 d_uk=+0.195
  pt7  nc=10 cs=50 N=2048 acc_u=0.050 acc_k=0.931 d_uk=-0.881  [chain-failure regime]
  pt8  nc=10 cs=50 N=4096 acc_u=0.050 acc_k=0.936 d_uk=-0.886  [chain-failure regime]
[VERDICT] HARD_PASS phase-map: all 3 regimes populated.
[elapsed] 10.1s
```

Smoke CLEARS: discriminator FIRES across all 3 regimes (separable: 6/8;
chain-failure: 2/8; ultra-advantage: 4/8; discriminating: 6/8). No
saturation, no floor, no by-construction tie. The chain-failure regime at
high nc x high cs reproduces the textbook single-linkage failure mode.

## Substrate-only decode gate

`n_llm_calls == 0` by structural guarantee; no LLM in the loop. Decode =
cosine argmax / label-permutation matching against planted truth.

## Per-seed runtime estimate (REQUIRED per Fix #17)

- Smoke wall-clock (8 grid points, N up to 4096, max n_atoms = 1000): 10.1s
- FULL grid: 60 grid points per seed; largest = (nc=50, cs=500) projecting to
  n_atoms = 50000 -> CAPPED to 5000 via N_ATOMS_CAP (memory cap). With
  effective cap, worst grid point per seed: 5000 atoms * O(n_atoms^2) cosine
  distance + O(iter * n_atoms * k) k-means. Empirical worst-case grid point
  measurement at full-N preview: see selftest log.
- Conservative per-seed wall (60 points): ~10-20 min including all axes.
- Timeout per seed: 2700s (45 min) -- gives 2-3x buffer.

## CARDINALITY_OK (§15)

- EXPECTED_N_UNITS = 60 (per seed)
- HARD_FAIL_CARDINALITY_BREACH gate fires if observed < 60 per seed.

## Discriminator-survives-scale (USER 2026-06-26 LOCKED)

Smoke at sub-grid (8 points) FIRED discriminator across all 3 regimes. Full
grid expands axes range; expectation is the same three regimes persist with
the chain-failure regime EXPANDING (more high-cs x high-nc combinations
trigger single-linkage chain). Discriminator survives scale because the
PHASE classification (separable / advantage / chain-failure) is regime-
preserving under axis expansion.

## Discipline checklist

- PRESERVE_ENV_VARS: HDLAB_QUEUE -- header comment in script
- No gpu_mandate_check (CPU dispatch OK)
- ARM_BASELINE rail (ARM_RANDOM_GROUPING): YES
- 3-arm bracket: YES
- Multi-seed FULL >= 3: YES (seeds [7, 13, 19] across 3 dispatches)
- ASCII-only: YES
- Substrate-only decode gate: YES
- Per-arm metrics-vs-verdict-msg (Fix #28): YES (verdict reads per-grid-point
  per-arm accs directly; not just delta means)
- CARDINALITY_OK: YES (EXPECTED_N_UNITS=60; HARD_FAIL_CARDINALITY_BREACH gate)
- DISCRIMINATOR_SURVIVES_SCALE: YES (smoke fired across 3 regimes; FULL
  expands same regime structure)
- HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR: YES (gate explicit; smoke = 0.05-1.000)
- HARD_FAIL_ARMS_IDENTICAL: YES (gate explicit; smoke d_uk = -0.886 to +0.350)
- §13 patterns: §13.1 (envelope-fail-bands; HP/MM/HF all defined); §13.7
  (run-mode discipline; HARD_FAIL on stale smoke partials in FULL)
- META_RULE_H CARDINALITY_OK: declared above
- Pre-flight Fix #26 predispatch_check.py: anchor name has no prior landing;
  novel cell.

-- exp_dev (Opus 4.7 1M context), 2026-06-28
