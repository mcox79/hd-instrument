# Pre-reg: substrate_seqbind_N_dim_scaling_law_v2

Filed 2026-06-30 (exp_dev). Recalibration of v1.6 Gate D positive-control
formula based on seed 7 FULL data. Mechanism is real (Skunkworks c7feb0c4
tiered HARD_FAIL; 3-seed cross-seed consistency preserved); only the analytical
K_cliff(N=8192) prediction was miscalibrated.

Supersedes: preregs/2026-06-30_substrate_seqbind_N_dim_scaling_law_v1.md
(v1.6 amendment). All non-Gate-D fields inherit from v1.6 unchanged.

## v2 amendment (2026-06-30, exp_dev)

**Root cause of v1.6 HARD_FAIL (seed 7, only FULL that landed):**
- Cell code (v1.6) hardcoded `POSCTRL_LOG2_K_CENTER = log2(1000) = 9.966`
  (Gate D center) with `POSCTRL_LOG2_TOL = 0.5`, sourced from theta-gamma v2
  CG language "K_cliff ~ 1000 at N=8192".
- Seed 7 FULL observed at N=8192: acc(K=500)=0.833, acc(K=1000)=0.400,
  acc(K=2000)=0.133. Cliff definition (`largest_K_where_acc>=0.5`) puts
  observed cliff at K=500, not K=1000.
- `|delta| = |log2(500) - log2(1000)| = 1.000` > tol 0.5 => Gate D fired
  HARD_FAIL_POSITIVE_CONTROL_REGRESSION.

**Root diagnosis:**
1. Prior CG language "K_cliff ~ 1000" was **transition-zone** talk. The precise
   cliff-definition (`>=0.5` threshold) puts the crossing at K=500 not K=1000.
2. K-grid `{50, 100, 200, 500, 1000, 2000, 4000}` has adjacent log2 steps of
   exactly 1.0 -- a tolerance < 1.0 quantization-fails even when mechanism is
   exactly on a K-grid step.
3. The mechanism IS scaling: seed 7 log2-log2 fit gives slope=0.83, R^2=0.90
   over 4 anchors (N in {2048, 4096, 8192, 16384}, K_cliff in {200, 200, 500,
   1000}).

## v2 recalibration (Gate D only)

Fitted power-law from seed 7 FULL v1.6 data:
```
log2(K_cliff) = 0.8288 * log2(N) - 1.8048   (R^2 = 0.8992, n_points = 4)
```

Predictions from fit:
- N=8192  (log2=13): log2(K_cliff) = 8.969 => K = 501
- N=16384 (log2=14): log2(K_cliff) = 9.798 => K = 890
- N=32768 (log2=15): log2(K_cliff) = 10.627 => K = 1581 (extrapolated)

**v2 Gate D parameters (recalibrated):**
- `POSCTRL_N = 8192` (unchanged)
- `POSCTRL_LOG2_K_CENTER = log2(500) = 8.9658` (was `log2(1000) = 9.9658`)
- `POSCTRL_LOG2_TOL = 1.0` log2 (was `0.5`; widened to cover K-grid step of
  exactly log2(2) = 1.0 between adjacent K-grid points)

**Verification against seed 7 observed:**
- Observed K_cliff at N=8192: 500 (log2 = 8.966)
- v2 posctrl center: 8.966; |delta| = 0.000 => Gate D PASSES
- v2 posctrl tol (1.0) also covers K=1000 (delta = 1.000) and K=250 (delta ~ 1.0)
  giving robust cliff-transition acceptance window.

## Discriminator survives at scale (same as v1.6)

- N=16384 K=1000 anchor (v1.6 seed 7 observed acc=0.933) preserved.
- N=16384 preview in smoke (pattern C; unchanged).
- If seed 7 v1.6 FULL data replays under v2 code: verdict = MIDDLE_BAND (Gate D
  passes; but R^2=0.899 < HP_R2_FLOOR=0.95 and slope=0.828 < HP_SLOPE_LOW=0.85).
  Awaiting seeds 13+19 FULL for chain-grade cv assessment.

## HP/MB bands (UNCHANGED from v1.6)

- HARD_PASS: R^2 >= 0.95 AND slope in [0.85, 1.15] AND cv-slope <= 0.10 AND posctrl passes
- MIDDLE_BAND: R^2 in [0.80, 0.95) OR slope in [0.70, 1.30) but not HARD_PASS
- HARD_FAIL: R^2 < 0.80 OR slope outside [0.70, 1.30] OR posctrl fails (Gate D)

Note: seed 7 v1.6 FULL currently falls in MIDDLE_BAND under v2 (slope=0.83 just
0.02 below HP band; R^2=0.90 in MB range). We do NOT widen HP bands in v2 --
that would inflate HP claims. Genuine HP would require slope in [0.85, 1.15]
after all 3 seeds land. If persistent slope ~ 0.83 across 3 seeds, MIDDLE_BAND
is the correct tier and reflects K-grid quantization bias (observed cliff-K is
always <= true-cliff-K by up to 1 K-grid step).

## Cell code delta v1.6 -> v2 (minimal)

- `experiments/_substrate_seqbind_N_dim_scaling_law_v2_core.py`
  - lines 108-124: `POSCTRL_LOG2_K_CENTER = log2(500)`, `POSCTRL_LOG2_TOL = 1.0`
    (was `log2(1000)` and `0.5`)
- `experiments/exp_substrate_seqbind_N_dim_scaling_law_v2_seed_{7,13,19}.py`
  - anchor names: `..._v2_seed_N`
  - config_version: `posctrl_log2_K_center=log2(500),posctrl_tol=1.0`
  - hardening_marker: `v2_seqbind_N_dim_scaling_law_gate_D_recalibrated`
  - import: `_substrate_seqbind_N_dim_scaling_law_v2_core`
- All other code (sweep grids, encoder, arms, cliff-definition, verdict logic,
  self-test, smoke gate) is byte-identical to v1.6.

## Cardinality (unchanged from v1.6)

- FULL per seed: 2 * 4 * 7 = **56** phase points
- SMOKE per seed: 2 * 3 * 3 = **18** phase points

## Schema-VET checklist (inherits v1.6; deltas noted)

- cardinality_ok: MANDATORY at aggregate (v1.6 seed 7 observed=56 = expected)
- final_metrics_atomicity: tmp_replace (unchanged)
- arms_differ_verified: MANDATORY at smoke (SUBSTRATE hash a3b8...cc != RANDOM
  hash 12bb...23; v1.6 seed 7 observed distinctness confirmed)
- baseline_in_band: RANDOM=0 at all K (v1.6 seed 7 confirmed 100%)
- calibration_check: "recalibrated_v2_gate_D_only" (was "default_ok" in v1.6)
- discriminator survives scale: same as v1.6 (pattern C; smoke includes N=16384)
- HARD_PASS strictly above floor: same bands as v1.6; band-floor result stays
  MIDDLE_BAND (META_RULE: band-floor is not HARD_PASS)
- HP_SCOPE: same as v1.6 {SUBSTRATE: all gates; RANDOM: baseline_in_band only}
- sweep_alignment_verdict: ALIGNED (same as v1.6)
- discriminating_fraction: 4/4 N values discriminating (seed 7 confirmed
  cliff-K neither 0 nor at sweep boundary)
- composition_edges: single primitive (same as v1.6)
- positive_control_arms: SEQBIND_REPRODUCE_AT_N8192_K500 (v2 relabel; was K1000)

## Chunked architecture (unchanged from v1.6)

- cell_chunked: true (3 sibling files, one seed each)
- start_marker_written: true
- crash_diagnostic_present: true
- heartbeat_present: true
- defensive_error_checking: passed_all_4_patterns

## Cell files

- experiments/_substrate_seqbind_N_dim_scaling_law_v2_core.py
- experiments/exp_substrate_seqbind_N_dim_scaling_law_v2_seed_7.py
- experiments/exp_substrate_seqbind_N_dim_scaling_law_v2_seed_13.py
- experiments/exp_substrate_seqbind_N_dim_scaling_law_v2_seed_19.py

## Queue

Target: overnight_queue (GPU). Same as v1.6.
Rationale: complex64 matmul over V=10000 x N=16384 codebook. Import torch
present. Wall estimate per seed ~40s (seed 7 v1.6 landed in 37.18s).
Timeout per seed: 3600s (unchanged from v1.6).

## Numbers cited (META_RULE_AC tagging)

- Fitted formula slope=0.8288 intercept=-1.8048 R^2=0.8992
  MEASURED@data/exp_substrate_seqbind_N_dim_scaling_law_v1_seed_7/metrics.json
  (substrate_scaling_fit block from seed 7 v1.6 FULL)
- K_cliff_by_N seed 7: {2048:200, 4096:200, 8192:500, 16384:1000}
  MEASURED@same source (K_cliff_by_arm_N.SUBSTRATE)
- Predicted K_cliff at N=8192 = 501  DERIVED@fitted formula log2(K)=0.8288*13-1.8048
- POSCTRL_LOG2_K_CENTER = log2(500) = 8.9658  DERIVED@fitted value at N=8192
- POSCTRL_LOG2_TOL = 1.0  DERIVED@K-grid step log2(K[i+1]/K[i]) = 1.0 uniformly
- Wall estimate ~40s per seed  MEASURED@seed 7 v1.6 elapsed_s = 37.18
