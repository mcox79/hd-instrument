# Pre-registration: reasoning_depth_mechanistic_survival_law_extrapolation_v1

Cell: `experiments/exp_reasoning_depth_mechanistic_survival_law_extrapolation_v1.py`
Author: hdi_exp_dev. Date: 2026-07-08. Queue target: `remote_cpu_queue` (numpy-CPU generation; not GPU).

## Question

Does a MECHANISTIC (physics-derived) survival law let the substrate EXTRAPOLATE its own reasoning-depth
capacity OUT-OF-RANGE, where the VET'd empirical 2-param affine law cannot? Extends the CHAIN_GRADE
reasoning-depth self-prediction north-star from proven INTERPOLATION to unproven EXTRAPOLATION.

Background (VET'd, commit 775b5cd92 / VET afd8dd68): empirical law `depth = a + b*phi(fill)` beats constant
(LOO MAE 1.20 vs 4.70) and nearest-lookup (1.65) on interpolation, but on the ONE true out-of-range fold
(fill=0.3516) does NOT beat lookup (1.86 vs 1.60). An empirical curve interpolates; it cannot extrapolate.

## Mechanistic law (closed form; THEORETICAL@this-file)

Accumulating-interference transmission / percolation-compounding:
- `coll_d = min(coll0 * (1 + kappa*(d-1)), 0.999)`  (per-hop collision, accumulating with depth)
- `p_d    = max(1 - s*coll_d, 1e-3)`                 (per-hop transmission coefficient)
- `S(D) = prod_{d=1..D} p_d ; D* = max{D : S(D) >= FLOOR}`   (chain-survival compounding)
- Physics input `coll0 = collision_frac_theo` = closed-form birthday-paradox `1-((K-1)/K)^(M-1)`,
  computable A PRIORI for unmeasured provisioning levels (REQUIRED for a genuine forward model; empirical
  collision would require running the substrate at the unmeasured level).
- Free params fit on TRAIN levels: `{s (interference amplification), kappa (depth-accumulation)}` (2 params,
  same count as the empirical affine's `{a,b}` -- fair comparison).
- THEORETICAL@ closed-form nesting: at `{s=1, kappa=0, coll0=fill}` reduces EXACTLY to the naive
  occupancy-binary bound `phi(fill)=ln(FLOOR)/ln(1-fill)`. Self-test asserts `|mech-phi| < 1e-6`.
  MEASURED@self_test: verified at fill in {0.07,0.20,0.35}.

## Extrapolation protocol (genuine out-of-range; NO leakage)

FIT candidate laws on LOW provisioning levels (fill <= OOR_SPLIT=0.3516, the landed envelope max);
TEST on HIGH levels (fill > 0.3516). nearest-lookup on an out-of-range point == boundary (max-train)
depth (honest flat extrapolation). The FULL GENERATES genuinely-new folds at fill ~0.42/0.50/0.60 (via
the VET'd keyslots generator baseline arm) that lie BEYOND the entire measured landscape -- the real
out-of-range test (current design had exactly one fold, also the top training point = weak test).
Robustness: repeat at every forward-split horizon; report fraction where mech beats lookup.

## Bands (task-primary)

- HARD-PASS = mechanistic law MAE on the GENUINE out-of-range folds (fill>0.3516) < nearest-lookup
  AND < empirical-affine AND < 1.60 (the VET'd single-fold lookup err) AND both firing controls fire.
- HARD-FAIL = mechanistic law does NOT beat nearest-lookup out-of-range = genuine REGIME SHIFT at high
  fill; extrapolation needs a different mechanism -> escalate to percolation-critical-fill drill.
  (This is itself a valuable, publishable substrate-physics finding: motivates hunting the critical fill.)
- MIDDLE = mech beats affine + improves over the empirical law but ties/loses to lookup near the
  flattening knee (lookup remains the practical extrapolation floor); scope caveat UPGRADED not resolved.

Firing controls (both required for HARD-PASS):
- C1 (mechanism-is-real): full-landscape collision-physics scramble -- true `collT<->depth` pairing must
  beat random pairings (real MAE below scrambled p10 + margin). NOTE: does NOT require chance-collapse --
  a survival law is monotone-in-collision by construction, so structure floors label-scramble damage; the
  honest null is real-beats-scrambled over the FULL landscape (steep low-fill region is discriminable).
- C2 (monotone-real): `spearman(fill, depth)` over the landscape outside a permuted null.

## Pre-flight calibration (MEASURED@ this cell's prototype; landed + regenerated telemetry)

- Closed-form nesting: PASS (mech == phi at s=1,kappa=0). MEASURED@self_test.
- FULL 5-seed (N=8192), genuine-new folds {0.4219,0.5010,0.5977}, actual depth 2.8/2.4/2.2:
  mech MAE=0.770 BEATS lookup 0.933 and affine 1.179 (< 1.60). Margin vs lookup ~17% (below the research's
  strict 20% suggestion -> a MODEST, deflated win). MEASURED@prototype.
- Robustness across forward-split horizons: mech beats lookup at 0.884@train5, 1.261@train7, 0.770@train8.
- Empirical quad `a+b*phi+c*phi^2` MAE=0.566 EDGES mech on the large-train split BUT is horizon-fragile
  (2.013@train5). Reported as a curvature-attribution CONTROL, NOT a gate: the physical form earns its
  keep via ROBUST extrapolation across all horizons, not lowest single-split MAE.
- SMOKE (2-seed preview, same 3-fold set): HARD_PASS, mech 0.570 < lookup 0.733 (margin 22.2%) < affine
  0.979; mech also beats quad 0.766; C1+C2 fire. MEASURED@data/exp_..._smoke/metrics.json. The 5-seed
  FULL is CANONICAL (canon != 2-seed preview).

HONEST framing (deflated per USER ground rule): this is a MODEST-but-real extrapolation win. The ROBUST,
non-borderline finding is that the mechanistic form beats the VET'd empirical AFFINE law out-of-range in
EVERY configuration; the mech-vs-lookup margin (~17-22%) is genuine but modest, driven by the FAR folds
(lookup's flat boundary-value is a good SHORT-range guess but degrades with extrapolation distance).

## Compute architecture

- Storage strategy: `no_composition` (analysis/monitor cell). Telemetry-generation reuses the VET'd
  keyslots FactoredStore (baseline arm); that generator's storage is FACTORED_HEBBIAN (already VET'd).
- Class: `(b) sequential-CPU with justification`. Generation is numpy-CPU (matmul cleanup at N=8192, V=512
  is small; per-rung ~8s). 15 rungs (3 folds x 5 seeds) ~120s + fast eval/controls. GPU batching would
  give negligible speedup at this scale (small matrices, dominated by codebook build + walk); routing to
  `remote_cpu_queue` (NOT overnight_queue GPU per cloud-GPU-once-per-stage + no-artificial-GPU discipline).
- Wall time est ~150-250s; timeout 1200s (6x+ headroom, under 1800 heartbeat-mandate threshold).

## SCHEMA-VET fields

- cardinality_ok: TRUE. EXPECTED out-of-range folds = len(NEW_NTEST_FULL) = 3; verdict counts oor folds,
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer.
- arms_differ_verified: TRUE (5 prediction arms mech/affine/quad/lookup/const hash-distinct; MEASURED@smoke).
- final_metrics_atomicity: `tmp_replace`.
- except SystemExit: raise BEFORE except Exception (no BaseException/bare except). Grep-gate: CLEAN.
- crlb_n/a: analysis cell; telemetry-gen reuses VET'd generator (own noise floor characterized).
  discriminator_reachability: TRUE (HARD-PASS threshold 1.60 is achievable; mech measured 0.770 < 1.60).
- baseline_in_band: N/A (no accuracy-saturation baseline; discriminator is a MAE comparison, const arm
  err ~7.6 confirms the landscape is non-trivial/non-saturated).
- calibration_check: `default_ok_for_this_regime` (FLOOR=0.5, D_MAX=18 inherited from the VET'd source
  cell; telemetry regenerated with the identical generator -> distributions match by construction).
- progress_logging: `print_flush_true` (per-fold `[gen]` lines flush=True; verdict lines flush=True).
- start_marker_written / crash_diagnostic_present: TRUE. heartbeat_present: FALSE (gen prints per-fold
  every ~8s = de-facto heartbeat; eval is fast; total < 5min so no hung-cell ambiguity).
- cell_chunked: FALSE (single analysis cell; per-fold generation is internally seed-looped and fast; no
  multi-seed-per-cell zombie risk at this runtime).
- run_mode channel: explicit `--run-mode` (local) OR `HDLAB_RUN_MODE` env (runner injects `full`); no
  silent default (bare + no env -> SystemExit). VERIFIED bare+env=full path.

### Section 15 gates

- effective_vs_nominal_parameter_audit / sweep_alignment_verdict: ALIGNED. The swept axis is provisioning
  fill = eff_fill(n_test) = n_test*18/2048 for the baseline arm; the mechanistic law's input collT =
  theoretical_collision_frac(n_test*18, 2048) is the SAME per-fold physics the substrate experiences (no
  nominal-vs-effective divergence; both derive from the same n_test).
- bracket_includes_discriminating_band / discriminating_fraction: 1.00. All out-of-range folds land in the
  discriminating regime (actual depth 2.2-2.8, well inside [0,18], not saturated/floored). const-arm err
  ~7.6 confirms non-triviality.
- signal_shape_compatibility_audit / composition_edges: none (no primitive->primitive composition; single
  generator arm feeding an analysis).
- positive_control_arms (Gate D): n_test=40 baseline-arm generation reproduces the LANDED fill=0.3516
  depth (~3.0-3.4 vs landed 3.40) via the IMPORTED VET'd generator functions -- SHAPE_MATCH, same regime.
  MEASURED@prototype (n_test=40 -> ud 3-4, collT 0.296). tolerance << 0.5 depth.
- functional_requirements: (1) derive a physics-grounded per-hop survival law computable a priori ->
  transmission-coefficient survival on theoretical collision; (2) fit on low fills, test on high out-of-
  range folds -> forward-split protocol, no leakage; (3) compare vs empirical affine + nearest-lookup +
  constant -> 5 declared prediction arms. Each maps to implemented code.

## Dispatch

- Queue: `remote_cpu_queue`. Timeout: 1200s.
- FULL generates 3 new folds x 5 seeds (N=8192) + merges with landed + runs the identical eval as smoke.
- Canonical metrics: `data/exp_reasoning_depth_mechanistic_survival_law_extrapolation_v1/metrics.json`.
- Post-ship: verify `run_mode==full`, size > 5KB, out_of_range_fills == [0.4219,0.501,0.5977], and the
  5-seed mech-vs-lookup verdict (canonical; may deflate the 2-seed-smoke margin).
