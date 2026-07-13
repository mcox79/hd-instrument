# Pre-registration: DIMENSION SCALING and the native representational CEILING (CLIMB vs FLATLINE discriminator)

- **Cell:** `experiments/exp_kg_store_dim_scaling_ceiling_v1.py`
- **Anchor name:** `kg_store_dim_scaling_ceiling_v1`
- **Metrics path:** `data/exp_kg_store_dim_scaling_ceiling_v1/metrics.json`
- **Filed:** 2026-07-13 (exp_dev). **Target queue:** `remote_cpu_queue` (one-shot Hebbian, no SGD -> CPU-cheap).
- **Source of design:** `notes/research_native_representational_ceiling_levers_2026-07-13.md` (Anchor candidate B `kg_store_dim_scaling_ceiling_v1`, levers 2 + 5).

## Prior-work check (mandatory)
`bash tools/substrate_query.sh "dimension scaling n_dim capacity ceiling native Hebbian associative memory SNR sqrt"`
-> confidence 0.3203; top hits are GENERIC: `associative` (wordnet, cosine 0.3203, spurious), `an associative relation`
(wordnet 0.3125), `Modern Hopfield / dense associative memory capacity` lit-scan note chunk (0.3047,
`research_drill_substrate_frontier_scale_interaction_2x_2026-06-11.md`), `Capacity scaling` (generic). **Prior-work
check: at cosine>0.30 only GENERIC associative-memory-capacity lit notes + spurious wordnet; NO prior arc CELL sweeps
n_dim inside the LIVE KGStore native-bind compose harness.** This is the dimension companion to the settled write-rule
negative (`kg_store_write_rule_decorrelated_ceiling_v1` HARD_FAIL_WRITE_RULE_NOT_THE_LEVER): with the write-rule lever
CLOSED, the ~6x native-vs-additive oracle-ceiling gap is DIMENSION-bound and/or CODE-STRUCTURE-bound, and this cell is
the clean discriminator between those two. Not a rediscovery: prior scale/capacity work is generic lit; this measures
whether n_dim is the right axis on THIS store's own inductive-compose oracle ceiling.

## Question
Does purely INCREASING `n_dim` (one-shot Hebbian write rule UNCHANGED -- the write rule is SETTLED, NOT varied) RAISE
the substrate's native ORACLE_FOLDIN ceiling toward the additive level, or does it FLATLINE?
- **CLIMB (HARD-PASS)** => DIMENSION/CAPACITY WALL is RELIEVABLE; nativize feasible by scaling n_dim (the store just
  needs more dimensions for the 25.7k-entity / 360k-triple load).
- **FLATLINE (HARD-FAIL)** => CODE-STRUCTURE WALL; random-bipolar codes cannot encode the relational geometry at this
  load; next lever is STRUCTURED/SPARSE codes (glass-box DG front-end), NOT more dimension or any write rule.
- **MIDDLE** => dimension helps but does not alone close the 6x gap (the sqrt(N/M) ~2.8x-at-8x expected region).
All three outcomes are decisive/publishable-internally.

## Mechanism / construction (only n_dim changes; HEBBIAN write rule at every dim)
Re-run the EXACT `exp_native_bind_compose_inductive_entity_cskg_v1` 7-arm harness (split / planted arena / compose /
readout / localization / verdict REUSED VERBATIM via import), HEBBIAN write rule ONLY, sweeping `n_dim` across
`{1024, 2048, 4096, 8192}` on a BIT-IDENTICAL held-out-entity split per seed (the split is seed-only and
n_dim-INDEPENDENT -> the ONLY variable across the sweep is the store's E/R/W dimensionality). Measure the native
`ORACLE_FOLDIN` mrr (the metric the ceiling claim is about) + `NATIVE_ANCHOR_COMPOSE` inductive mrr + the must-fails
(`NATIVE_SCRAMBLE` / `IDENTITY_SHUFFLE`) at each dim.
- **Sweep-axis choice (autonomy):** `{1024, 2048, 4096, 8192}` -- extends the note's Anchor-B `{1024, 2048, 4096}` with
  8192 (8x the base dim) per the task, to reach the sqrt(N/M) law's ~2.8x-at-8x prediction and give a decisive top-ratio
  point. 1024 = the store default + CERT-584/585 regime (Gate D reproduction anchor).
- **Memory (autonomy):** KGStore E/W are float32 already (E ~843MB, W ~256MB per store at n_dim=8192). Per-arm score
  tensors are FREED immediately after their metric is computed (no whole (nq,N) map held across arms); store_oracle +
  recall_oracle freed after ORACLE; weak-point localization (arm_scores retained ~1.85GB, dim-INDEPENDENT) is enabled
  only for `n_dim <= 4096` -- the 8192 dim (memory-risk point) runs lean since the top-ratio point needs only
  oracle/native mrr, not localization. PER-(seed,dim) CHECKPOINT (`write_partial_key` + resume) so a dropped dim resumes
  from disk instead of re-running the whole sweep.
- **NO regression risk to CERT-584/585.** KGStore is NOT modified; cell-owned store INSTANCES only; the Hebbian
  `ingest_triples` path is bit-identical / untouched -> the n_dim=1024 arm must reproduce the landed oracle (Gate D).

## Arms
Each n_dim runs the full base 7-arm harness (NATIVE_ANCHOR_COMPOSE / MEMORIZE_FIXEDCODE / RANDOM_CODES / NATIVE_SCRAMBLE
/ IDENTITY_SHUFFLE / ORACLE_FOLDIN / BASELINE_POP), scored PAIRED on the SAME held-out QUERY edges. The top-level verdict
reads the ORACLE_FOLDIN-mrr-vs-n_dim trend.

## Pre-registered bands (primary = ORACLE_FOLDIN mrr; d_lo=1024, d_hi=8192; picked BEFORE the run)
- `CLIMB_RATIO = oracle_mrr[d_hi] / oracle_mrr[d_lo]`;
  `GAP_CLOSED = (oracle_mrr[d_hi] - oracle_mrr[d_lo]) / (0.137 - oracle_mrr[d_lo])`;
  `RATIO_4096 = oracle_mrr[4096] / oracle_mrr[1024]` (the note's Anchor-B pre-reg point; reported).
  ADDITIVE_ORACLE_CEIL = 0.137 CITED@notes/research_native_representational_ceiling_levers_2026-07-13.md.
- **HARD-PASS / CLIMB** (`HARD_PASS_DIMENSION_RELIEVES_CEILING`): `(CLIMB_RATIO >= 3.0 OR GAP_CLOSED >= 0.50)` AND
  trending up (`oracle_mrr[d_hi] - oracle_mrr[d_lo] >= 0.003`) AND ORACLE fires at EVERY dim AND scramble/identity
  must-fails controlled at EVERY dim AND the n_dim=1024 baseline reproduces the landed oracle (Gate D). (Above the sqrt
  prediction => dimension is a stronger-than-theory lever => nativize feasible by scaling n_dim.)
- **HARD-FAIL / FLATLINE** (`HARD_FAIL_CODE_STRUCTURE_WALL_NOT_DIMENSION`): `CLIMB_RATIO < 1.3` (8x dim buys < 1.3x
  oracle; native oracle stuck ~0.02-0.03) AND ORACLE fires at every dim (a genuine flatline, not a broken harness) AND
  Gate D holds => the wall is code-structure, not dimension; next lever = structured/sparse codes.
- **MIDDLE** (`MIDDLE_BAND_PARTIAL_DIMENSION_GAIN`): `1.3 <= CLIMB_RATIO < 3.0` AND `GAP_CLOSED < 0.50` => dimension
  helps but does not alone close the 6x gap (the sqrt(N/M) ~2.8x-at-8x expected region; dimension is a contributing axis
  that STACKS with other levers, not the sole fix). The pre-registered EXPECTED outcome per the note.
- **INCONCLUSIVE** if the n_dim=1024 baseline does not reproduce the landed oracle (Gate D drift), if ORACLE does not fire
  at some dim (arena unanswerable there), or if a must-fail control leaks at some dim.

MEASURED / CITED anchors:
- native ORACLE_FOLDIN mrr @ n_dim=1024 = 0.023083  MEASURED@data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_FOLDIN (Gate D target, tol +-0.006)
- native NATIVE_ANCHOR mrr @ n_dim=1024 = 0.013967  MEASURED@ same path :NATIVE_ANCHOR_COMPOSE
- additive oracle ceiling = 0.137                    CITED@notes/research_native_representational_ceiling_levers_2026-07-13.md
- sqrt(N/M) SNR law: 4x dim ~2x, 8x dim ~2.8x        CITED@ same note, lever 5 (Frady/Kleyko/Sommer)

## Compute architecture
class (c) MIXED: split/support-query/POP = sequential-CPU graph ops. Store = untouched one-shot KGStore Hebbian ingest
(chunked matmul; NO SGD, NO epochs, NO solve). Per (seed, n_dim): 2 store builds (train-W + oracle fold-in) + a single
batched native compose + query-chunked bilinear readouts. Ingest ~O(triples*n_dim^2); readout ~O(nq*N*n_dim); both
CPU-cheap; GPU unnecessary (one-shot dense matmuls) -> `remote_cpu_queue` (device=cpu). FULL = 3 seeds x 4 dims = 12
units; wall estimate ~40min (8192 ingest dominates). storage_strategy: no_composition (native Hebbian W is a matrix
store; no bundled-vs-sharded axis; E/R untouched). Peak RAM at n_dim=8192 ~3-4GB (float32, per-arm score frees +
lean-8192); per-(seed,dim) checkpoint resumes a dropped dim.

## SCHEMA-VET fields
- `arms_differ_verified: true` (7 arms per (seed,dim) + W-hash differs across dims asserted at self-test; META_RULE_AF)
- `final_metrics_atomicity: "tmp_replace"` (write_metrics + write_partial_key os.replace)
- `cardinality_ok: true`; `EXPECTED_N_UNITS = n_seeds * n_dims = 3 * 4 = 12`; verdict counts units, HARD_FAIL_CARDINALITY_BREACH if short
- `crlb_n/a: "primary is a RISE RATIO of ORACLE mrr (ceiling-relative) + a GAP_CLOSED fraction of the additive headroom; bands are ratios, not absolute thresholds"`
- `discriminator_reachability: true` (ratio bands scale to whatever ceiling the FULL measures; additive 0.137 is the scale target)
- `baseline_in_band: true` (n_dim=1024 ORACLE must fire + reproduce landed 0.023083 within +-0.006; RANDOM/POP near 1/N floor at every dim)
- `calibration_check: "default_ok_for_this_regime"` (ORACLE_FIRE ratio/abs + heldout/support fracs + n_heldout_eval are the base arena's pre-registered knobs, NOT tuned on real data; only new knobs are the pre-registered dimension bands)
- `discriminator_survives_scale: analytical + self-test` (SNR ~ sqrt(N/M) is a scale-INVARIANT law and the sweep IS the scale axis; the self-test DIMENSION micro-discriminator fires hebb-recall-rises-with-n by margin 0.2175 at fixed plant M=110 straddling the ~0.14N cliff, and the planted-arena ORACLE fires at every self-test dim with oracle rising 0.763 -> 0.887)
- `positive_control_arms:` n_dim=1024 hebbian arm reproduces landed oracle 0.023083 within +-0.006 (Gate D); ORACLE fires at EVERY dim
- `effective_vs_nominal_parameter_audit: ALIGNED` (n_dim is the store E/R/W dimensionality directly; every primitive -- bind key `E[s]*R[p]*sqrt(n_dim)`, Hebbian W [n_dim x n_dim], bilinear readout `E@(W@key)` -- experiences the swept n_dim with NO partition/routing that could hold effective-n_dim constant)
- `per_unit_failure_class: true` (no bare except; per (seed,dim) failure_class recorded)
- `start_marker_written / crash_diagnostic_present / heartbeat_present: true`; `cell_chunked: false` (12 units in one cell, all persisted per-(seed,dim) via write_partial_key + resume; single-shot CPU cell ~40min)
- `progress_logging: "print_flush_true"` (line-buffered stdout + per-(seed,dim) flush prints; timeout >= 1800)
- `functional_requirements:` (1) measure whether n_dim raises the native oracle ceiling -> sweep n_dim, read ORACLE_FOLDIN mrr trend; (2) keep the relation-operator / entity-identity signal at every dim -> scramble/idshuf must-fails still fire per dim; (3) not regress CERT-584/585 -> KGStore untouched, n_dim=1024 arm reproduces landed (Gate D)

## Four validity-preflight checks (declared in the self-test)
1. positive_control_passes: ORACLE_FOLDIN fires at EVERY self-test dim on the planted arena.
2. metric_moves: the DIMENSION micro-discriminator moves synthetic Hebbian heteroassociative recall cosine as n_dim rises at fixed plant M (SNR ~ sqrt(N/M), straddling the ~0.14N cliff).
3. negative_control_margin: at the larger self-test dim RANDOM + relation-scramble + identity-shuffle sit below NATIVE_ANCHOR by the MRR margin (>=3 controls).
4. full_gates_exercised: dimension_sweep_verdict fires every fail-closed gate at self-test scale.

## Self-test result (MEASURED, local .venv, run_mode=self_test, dims=[256,512])
- dimension discriminator: cos_lo=0.7334 (n=128, M=110) cos_hi=0.9509 (n=1024, M=110) margin=0.2175 (>= 0.15 gate); Hebbian recall cosine RISES with n_dim at fixed plant.
- compose harness (planted arena): ORACLE mrr 0.763 (dim256) -> 0.887 (dim512) rises with dim; oracle_fires_all=True; scramble_all=True; idshuf_all=True; oracle_not_collapse=True; W-hash differs across dims; arms_differ (>=5 sigs).
- `SELFTEST_PASS`, validity_preflight_ok=True, exit=0.

## Dispatch
`bash tools/orchestrator/queue_add.sh remote_cpu_queue kg_store_dim_scaling_ceiling_v1 experiments/exp_kg_store_dim_scaling_ceiling_v1.py preregs/2026-07-13_kg_store_dim_scaling_ceiling_v1.md 9000`
- Timeout 9000s (2.5h): FULL wall estimate ~40min (8192 ingest ~O(triples*n_dim^2) dominates); 3.7x margin for CPU/thread variance. Per-(seed,dim) checkpoint means a timeout-kill resumes landed dims on re-dispatch.
