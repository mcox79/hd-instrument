# Pre-registration: REACHABILITY-AUDIT PREDICTIVE-DIAGNOSTIC TEST v2 (scramble-control fix)

- **Cell:** `experiments/exp_reachability_predicts_relational_failure_cskg_v2.py`
- **Tool:** `hdlab/reachability_audit.py` (UNCHANGED from v1; the traversal + partial-correlation machinery is correct)
- **Anchor:** `reachability_predicts_relational_failure_cskg_v2`
- **Supersedes:** v1 (`..._cskg_v1`), which landed `INCONCLUSIVE_SCRAMBLE_NOT_CONTROLLED`
  (MEASURED@data/exp_reachability_predicts_relational_failure_cskg_v1/metrics.json).
- **Queue / device:** SMOKE -> `remote_cpu_queue` (discriminator-preview: full induced graph, 1 seed, reduced epochs)
  | FULL -> `remote_cpu_queue` (2 seeds [7,13]) | device=cpu (task-specified; CPU-appropriate scale).
  NO LOCAL COMPUTE: authored + syntax/import-checked locally only; self-test + smoke + full all run REMOTE
  (the remote runner's `--self-test` is the gate).

## Why v2 (root-cause of the v1 INCONCLUSIVE)
The v1 FULL run was scientifically SOUND on its primary question but tripped a mis-calibrated arena-validity gate:
- **The diagnostic FIRED cleanly:** partial_spearman(k-hop reachability, per-entity RR | degree) =
  MEASURED[0.142, 0.159] across seeds [7,13]; within-degree-stratum permutation p = MEASURED[0.002, 0.002]
  (real rho >> null_mean 0.003 +/- null_std 0.024); bottom-vs-top RR-decile mean reachability = [110->185, 112->188]
  (low-accuracy entities ARE the low-reachability entities -- the track-record tie-in). n_entities=1835 both seeds.
- **The scramble gate mis-fired.** v1's must-fail RELATION_SCRAMBLE was the WEAKEST possible scramble: a score-time
  permutation of the FITTED D relation rows, leaving the fitted entity geometry (homophily) intact. On the
  homophily-heavy real reduced-CSKG (MEASURED MAIN=0.0242 ~ POP=0.0244; readout at frequency-parity) it removed only
  ~58% of the beyond-random margin (RANDOM=0.0011, SCRAMBLE=0.0107 -> rel_specific_frac=0.58). v1 gated this with
  `SCRAMBLE_CEIL_FRAC=0.25` == demand the relation carry >=75% of the beyond-random signal -- a purity bar inherited
  from the synthetic-clean `bucket_diversity` cell and MIS-SPECIFIED for a real KG where homophily/degree structure
  legitimately coexists with relation structure (`readable signal largely additive`, `single-relation
  homophily-solvable`). So the control FIRED (moved the metric 56%) but the GATE was wrong -> INCONCLUSIVE.

## The two-part v2 fix (verify perturb-moves-the-metric BEFORE tiering)
1. **STRENGTHEN the control -> `RELATION_SCRAMBLE_REFIT`.** Shuffle the relation label on each TRAIN edge, then REFIT
   the SAME additive recipe (`fit_kge_anchor1`, CE self-adversarial + N3 + reciprocal) on the scrambled edges
   (train-time scramble, not score-time). No relation-specific regularity can be LEARNED; head/tail adjacency is
   preserved so whatever the refit recovers is the relation-invariant / homophily floor. This is the STANDARD KGE
   relation ablation (same as the `_course_c_rotate_core` SCRAMBLE_ROTATE arm). One extra fit per seed.
2. **RE-CALIBRATE the gate -> `scramble_fires` (telemetry-sensitivity / saturation-vacuous guard).** The control
   FIRES iff the refit-scramble MOVES MAIN down by a substantial pre-registered fraction of the beyond-random margin:
   `rel_specific_frac = (MAIN - SCRAMBLE_REFIT)/(MAIN - RANDOM) >= REL_FRAC_MIN(0.30)` AND
   `(MAIN - SCRAMBLE_REFIT) >= SCRAMBLE_MOVE_ABS(0.004)` AND `SCRAMBLE_REFIT < MAIN` AND
   `SCRAMBLE_REFIT >= RANDOM - SCR_FLOOR_EPS(0.005)` (not broken-below-random). `rel_specific_frac` +
   `homophily_frac` are REPORTED in every verdict so the relation-vs-homophily character is explicit and NOT
   over-claimed. `REL_FRAC_MIN=0.30` is a principled "substantial genuine relational contribution" bar picked BELOW
   the v1-observed 0.58 (NOT tuned-to-pass-at-the-margin); it supersedes v1's >=0.75 purity bar which is wrong for
   real KGs.

## Anti-goalpost-moving statement (honesty)
The recalibration is NOT relabelling a failing result as passing. (a) The v1 diagnostic's OWN decisive control (the
within-degree stratified permutation null on partial_rho) already fired at p=0.002 independent of the scramble gate.
(b) v2 makes the scramble control STRONGER, not weaker (train-time refit collapses at least as much as v1's score-time
permutation -> rel_specific_frac in the FULL run is expected >= the v1-observed 0.58). (c) The gate still FAILS CLOSED:
if the refit-scramble does NOT remove a substantial relation-specific fraction, verdict = INCONCLUSIVE_SCRAMBLE_DID_NOT
_FIRE (the contract's "control won't fire" HARD-FAIL branch) and the "relational" framing is reported as unsupported.
The remote FULL run decides HARD_PASS vs INCONCLUSIVE on measured numbers, not on this pre-reg's expectation.

## Per-entity quantities + the diagnostic test (UNCHANGED from v1)
For each QUERY-HEAD entity (all from TRAIN-remaining edges, no query leakage): `y` = mean filtered RR, `z` =
undirected TRAIN degree (confound), `R` = k-hop reachable mass (k=2). PRIMARY (gated) = partial Spearman(R, y | z)
with the within-degree-stratum permutation null (N_PERM=500, DEG_STRATA_BINS=10). SECONDARY (reported): partial
Spearman(distance_to_hub, y|z) [expected NEGATIVE]; partial Spearman(mean_neighbor_degree, y|z) [expected POSITIVE];
raw Spearman(R,y) and Spearman(deg,y); bottom-vs-top RR-decile mean reachability (the 6-instance failure-track-record
tie-in). Mode (a) `measured_reachability` remains STUB-READY/inert on the metadata-empty substrate (reported
`measured_reachability_active=False`).

## PRE-REGISTERED BANDS (picked BEFORE the v2 run; effect-size thresholds, NOT tuned on outcome)
- `HARD_PASS_REACHABILITY_PREDICTS_RELATIONAL_FAILURE`: arena_fires AND **scramble_fires** AND both seeds
  n_entities >= MIN_ENTITIES(200) AND BOTH seeds: partial_rho > 0 (correct sign) AND partial_rho >= RHO_HARD(0.10)
  AND perm_p <= P_SIG(0.05). => the audit's diagnostic claim HOLDS beyond degree on an arena with a genuine (firing)
  relation-scramble control.
- `MIDDLE_REACHABILITY_WEAK_OR_LARGELY_DEGREE`: arena+scramble+entities OK AND both correct sign AND both
  perm_p <= P_MID(0.15) AND both |partial_rho| >= RHO_MID(0.04), not meeting HARD.
- `REFUTE_REACHABILITY_DOES_NOT_PREDICT_BEYOND_DEGREE`: arena+scramble+entities OK AND NOT correct-sign-significant
  (any seed wrong sign OR both |partial_rho| < RHO_MID OR any perm_p > P_MID OR seed sign-disagreement). HONEST
  NEGATIVE.
- `INCONCLUSIVE_ARENA_DID_NOT_FIRE` / `INCONCLUSIVE_SCRAMBLE_DID_NOT_FIRE` / `INCONCLUSIVE_INSUFFICIENT_ENTITIES`:
  fail-closed. `INCONCLUSIVE_SCRAMBLE_DID_NOT_FIRE` = the "control won't fire" branch (refit-scramble removed <30% of
  the margin => MAIN homophily/degree-dominated; "relational" framing unsupported at this arena). Report
  rel_specific_frac + homophily_frac.

## Compute architecture
class (a) batched: TWO transductive additive-KGE fits per seed (MAIN + RELATION_SCRAMBLE_REFIT), vectorized torch
minibatch SGD, CPU, k=16/epochs=150/n_neg=64/batch=8192/neg_chunk=16 (same recipe as v1 FULL, which ran 474s for
2 seeds x 1 fit). Doubling to 2 fits/seed -> ~2x wall. Both fits checkpoint (ckpt_every=20; distinct tags
kge_seed{N} + kge_scramble_seed{N}). Reachability traversal (k-hop BFS, multi-source BFS, partial Spearman,
stratified permutation) is CHEAP (seconds), dwarfed by the fits. Storage SHARDED. Readout query-chunked batched
matmul. device=cpu. Seeds sequential in one process. Compute-proportionality: the fit is unavoidable (the CLAIM is
the substrate's own per-entity accuracy); the extra refit buys an unimpeachable must-fail control.

## SCHEMA-VET fields
- `arms_differ_verified: true` (MAIN / RANDOM / SCRAMBLE_REFIT score-signature hashes >= 3 distinct, self-test +
  per-seed; enforced by a hard ARMS_MUST_DIFFER raise in core_main).
- `final_metrics_atomicity: tmp_replace` (write_metrics + os.replace).
- `except SystemExit before except Exception`; no BaseException / no bare except.
- `crlb_n/a`: no closed-form noise floor for a partial-rank-correlation test; feasibility via arena_fires +
  MIN_ENTITIES population floor (both amply cleared by v1: MAIN/RANDOM ratio 22x; n_entities 1835 >= 200).
- `baseline_in_band`: arena_fires IS the baseline-in-band check (RANDOM near floor; MAIN clears it 22x).
- `discriminator survives scale`: option (C) discriminator-preview -- SMOKE runs the FULL induced graph (full
  N/edges, 1 seed, reduced epochs) to preview arena_fires + **scramble_fires (the v2 refit-scramble at full scale)**
  + entity population + a non-degenerate partial-rho pipeline BEFORE the 2-seed FULL commits full compute. (v1
  already established arena_fires + partial-rho at full scale; the ONLY new unknown v2 introduces is the
  refit-scramble collapse, which the SMOKE previews at 1 seed.)
- `HP_SCOPE`: arena_fires + scramble_fires apply to ALL seeds; HARD/MIDDLE/REFUTE bands apply to the cross-seed
  aggregate of the partial-rho.
- `cardinality`: EXPECTED_N_UNITS = n_seeds (2 FULL / 1 SMOKE); per-seed failure halts with failure_class +
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
- `calibration_check: adaptive_with_discriminator_gate` -- v2 recalibrates the v1 gate (documented above); the
  discriminator (scramble_fires) still-fires requirement is a fail-closed gate logged in metrics.
- `real_code_path`: self-test constructs the REAL reachability tool + REAL fit/score/RR/partial-rho pipeline AND the
  REAL train-time refit-scramble at N~150, plus mode-(a) measured_reachability traversal-correctness + inert-when-empty.
- `substrate_signature`: fit_kge_anchor1 bound against live signature (base/portable kwargs).
- `deterministic_seeding: true` (fixed int seeds; sorted iteration; np.random.default_rng only; no hash()/list(set());
  PROT-023 source-scan clean).
- `progress_logging: print_flush_true` (line-buffered stdout + per-seed flush).

## ETA / timeouts
- **SMOKE** (`remote_cpu_queue`, 1 seed, epochs=40, 2 fits): estimated ~150-300s remote CPU. `--timeout 1200`.
- **FULL** (`remote_cpu_queue`, 2 seeds, epochs=150, 2 fits/seed): v1 FULL = 474s (2 seeds x 1 fit); v2 ~= 950-1100s
  (2 fits/seed) + BFS/perm. `--timeout 3600` (comfortable safety margin; ckpt_every=20 resumes on kill/sleep).
