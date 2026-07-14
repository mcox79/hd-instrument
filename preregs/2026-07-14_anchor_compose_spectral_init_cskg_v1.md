# Pre-reg: SPECTRAL-INIT WARM-START of the additive inductive map (held-out-entity MRR)

- anchor_name: `anchor_compose_spectral_init_cskg_v1`
- script: `experiments/exp_anchor_compose_spectral_init_cskg_v1.py`
- shared-dep change: `experiments/_kge_anchor1_fit.py` gains an additive `X_init=None, init_tag=None` kwarg
  (DEFAULT None == BIT-IDENTICAL to every existing caller; ships WITH the cell via Pattern-6 auto-SCP).
- queue: `overnight_queue` (GPU; 8 SGD refits at k=24/epochs=500/N~25.7k -- the refit is the reason to route GPU).
- date: 2026-07-14
- thrust: A (shore up what's working) -- recipe-drill rank-1 lever, single-swap, glass-box, architecture-fixed.

## Question (PRIMARY)
Does a Laplacian graph-eigenmap warm-start of the additive entity coordinate table raise the held-out-ENTITY MRR
of the zero-training ANCHOR_COMPOSE bundle over the confirmed gaussian(random)-init baseline, holding the scoring
function + loss + all hyperparameters + the held-out split BIT-IDENTICAL and changing ONLY the init of X?

## Mechanism (glass-box, closed-form, inspectable)
Spectral embedding of the TRAIN-edge graph: `A_norm = D^-1/2 A D^-1/2` (symmetric normalized adjacency over the N
entities; edge (h,t) structural, relation-agnostic, undirected). Its top-(k+1) eigenvectors (`scipy.sparse.linalg.
eigsh`, Lanczos, no dense N-by-N, no LU) are the smoothest graph-Laplacian eigenmaps; drop the trivial constant top
eigenvector, take the next k, RESCALE each column to the gaussian init per-dim std (0.1) so the comparison isolates
STRUCTURE not scale. Warm-starts only the SEEN anchor rows (held-out entities are isolated in the train graph ->
their rows stay gaussian and are overwritten by ANCHOR_COMPOSE anyway). `fit_kge_anchor1(X_init=...)` injects the
warm-start AFTER the gaussian X/D draw, so D's init + RNG order are unchanged and only X's start point differs (the
TRAINED X,D legitimately diverge under coupled SGD -- that IS the warm-start effect).

## Arms (all PAIRED on the SAME held-out QUERY edges)
- `ANCHOR_GAUSS`         : ANCHOR_COMPOSE over the gaussian-init fit. CONTROL -- reproduces 0.12821 (X_init=None,
                          same seeds/config/split as the VET-confirmed run -> bit-identical).
- `ANCHOR_SPEC`         : ANCHOR_COMPOSE over the SPECTRAL-warm-started fit. THE test arm.
- `ANCHOR_SPEC_SCRAMBLE`: ANCHOR_COMPOSE over a scrambled-spectral-init fit (same column norms, row assignment
                          permuted across seen entities -> structure destroyed, scale preserved). MUST-FAIL scale
                          isolation. (seed-7 only.)
- `ORACLE_GAUSS`        : gaussian fit, held-out folded in (codes learned) -> positive control / arena-answerable
                          ceiling. (seed-7 only.)
- `RANDOM_CODES`        : random X + random D + additive readout -> null / arena floor (no fit).

HP_SCOPE: the WARMSTART_LIFTS gates apply to `ANCHOR_SPEC` (vs `ANCHOR_GAUSS`) only. `ORACLE_GAUSS` = positive
control (must fire); `ANCHOR_SPEC_SCRAMBLE` = must-fail scale-isolation control; `ANCHOR_GAUSS` = the fixed
reproduce-0.12821 baseline; `RANDOM_CODES` = the null floor.

## Info-ceiling (compute-the-ceiling-before-iterating discipline)
MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr --
  ANCHOR_COMPOSE (gaussian) = 0.12821, ORACLE (transductive ceiling) = 0.137293, RANDOM = 0.000483.
ANCHOR is already at **93.7% of the ORACLE ceiling**; the residual headroom to the arena-answerable ceiling is only
~0.009 MRR. A raw +15% relative literature lift (-> 0.147) would EXCEED the transductive oracle and is IMPLAUSIBLE
for a zero-training composed code. The HARD-PASS bar is therefore set ceiling-aware BELOW the ceiling.

## Bands (pre-registered; primary metric = filtered MRR, degree-unbiased, rank-vs-ALL)
Let `LIFT = ANCHOR_SPEC_mrr - ANCHOR_GAUSS_mrr`, `SCRAMBLE_LIFT = ANCHOR_SPEC_SCRAMBLE_mrr - ANCHOR_GAUSS_mrr`.
- **HARD-PASS `HARD_PASS_SPECTRAL_WARMSTART_LIFTS`**: `LIFT >= LIFT_MIN (0.005)` AND
  `(LIFT - SCRAMBLE_LIFT) >= STRUCT_MARGIN (0.003)` AND ORACLE fires AND gaussian control reproduces 0.12821
  within REPRO_TOL (0.02).  [0.005 recovers >55% of the ~0.009 residual oracle headroom -> ceiling-aware AND
  strictly ACHIEVABLE (< residual headroom).]
- **MIDDLE `MIDDLE_BAND_SCALE_ARTIFACT_NOT_STRUCTURAL`**: `LIFT >= LIFT_MIN` but `(LIFT - SCRAMBLE_LIFT) <
  STRUCT_MARGIN` -> the scrambled-spectral matched the lift; it is a scale/norm artifact, not structural transfer.
- **HARD-FAIL `HARD_FAIL_NO_LIFT_COMPOSE_WASHOUT`**: `LIFT <= LIFT_NOISE (0.002)` with ORACLE firing -> genuine,
  informative negative: the degree-invariant MEAN compose op downstream of X,D washes out the structural init
  signal -> localizes the wall to the COMPOSE stage (not the FIT stage).
- **MIDDLE `MIDDLE_BAND_PARTIAL_LIFT`**: `LIFT_NOISE < LIFT < LIFT_MIN`.
- **Gated INCONCLUSIVE**: `INCONCLUSIVE_ORACLE_UNDERFIT` (ORACLE does not fire) OR
  `INCONCLUSIVE_BASELINE_REPRO_DRIFT` (gaussian control not within REPRO_TOL of 0.12821 -> fit/env drift, paired
  comparison invalid) OR `INCONCLUSIVE_TOO_FEW_HELDOUT` OR `BROKEN_TEST_RANDOM_BEATS_GAUSS`.

Number tags:
- ANCHOR_GAUSS reproduces 0.12821: CITED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json (bit-identity
  proven locally on the planted grid: my ANCHOR_GAUSS == arena ANCHOR_COMPOSE == 0.40467 at 5dp).
- LIFT_MIN=0.005 / LIFT_NOISE=0.002 / STRUCT_MARGIN=0.003 / REPRO_TOL=0.02: HYPOTHESIZED@this prereg (ceiling-aware,
  NOT tuned on real data).
- expected lift +3-15% relative: CITED@notes/research_drill_training_recipe_improvement_theories_2026-07-13.md
  (deflated P=0.40); this cell tests it and can HARD-FAIL informatively (compose-op washout is a predicted outcome).
- per-fit ~1342s: MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:elapsed_s (12073s/9-fit).

## Compute architecture
class (c) MIXED: split/partition = sequential-CPU graph ops; additive fits = minibatch SGD (batched, neg-chunked)
on GPU; spectral eigenmap = one sparse `eigsh` per seed (Lanczos top-k of A_norm; shared by spec+scramble);
E_derived = one vectorized index_add_ bundle (zero training). Storage SHARDED. device=auto. FULL = 8 SGD refits
(gauss+spec x 3 seeds = 6; scramble+oracle seed-7 = 2). fit-checkpointed (ckpt_every=20). No local FULL/smoke (USER
2026-07-11) -- LOCAL gate = --self-test on a planted CPU grid; FULL on overnight_queue.

## Cardinality / discipline fields
- cell_chunked: false (in-process multi-seed with per-seed write_partial + checkpoint; single cell file).
- EXPECTED_N_UNITS: 3 (seeds [7,13,17]); each seed asserted >= (4 if controls else 3) distinct arm sigs.
- start_marker_written: true; crash_diagnostic_present: true (Exception -> CELL_CRASHED + traceback);
  heartbeat_present: true (_heartbeat.jsonl per unit); defensive_error_checking: passed_all_4_patterns.
- final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
- arms_differ_verified: true (>=4 sigs with controls; >=3 without).
- baseline_in_band: ORACLE must fire (>=3x RANDOM AND headroom>=0.003); gaussian reproduces 0.12821.
- crlb_n/a: no closed-form noise floor; the info-ceiling is the ORACLE (0.137293), stated above; LIFT_MIN < residual
  headroom -> discriminator_reachability = OK.
- calibration_check: adaptive_with_discriminator_gate (bands ceiling-aware, pre-registered, not tuned).
- progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints); progress_cadence: per-seed.
- run_mode default: full (argparse default; --self-test / --memsmoke opt-in; HDLAB_RUN_MODE honored only for bare
  full dispatch). RUN_MODE VERIFICATION post-dispatch: expect run_mode=full, size>5KB, elapsed>1s.

## Gate F (F.1-F.4 ENFORCE) declarations -- machine-checked in --self-test
- F.1 real_code_path: exercised {fit_kge_anchor1, build_spectral_init, build_anchor_compose_codes} at N~300.
- F.2/F.3 substrate_signature: fit_kge_anchor1(..., X_init=..., init_tag=...) bound against the live signature.
  X_init/init_tag are OPTIONAL kwargs (advisory WARN expected) BUT ship WITH the cell (_kge_anchor1_fit auto-SCP
  via Pattern-6) -> guaranteed remote parity, not a drift risk.
- F.4 guard_baseline_valid: the RANDOM-beats-ANCHOR_GAUSS broken guard's baseline (ANCHOR_GAUSS) validated above
  the RANDOM floor (not structurally at floor).
- classes 1-4 (warn): positive_control (ORACLE fires), metric_moves (MRR moves RANDOM->GAUSS->SPEC->ORACLE),
  negative_control_margin (RANDOM + SCRAMBLE not above GAUSS).

## Self-test result (LOCAL gate, VALIDITY_PREFLIGHT_MODE=enforce, exit 0)
MEASURED@data/exp_anchor_compose_spectral_init_cskg_v1_selftest/metrics.json:
  ok=True; ORACLE=0.93169 (fires), RANDOM=0.01338, ANCHOR_GAUSS=0.40467 (== arena bit-identical), ANCHOR_SPEC=0.30981,
  SCRAMBLE=0.33811; n_distinct_sigs=5; init_changed_fit=True; spec_structure=True; scale_matched=True;
  guard_ok_planted=True; validity_preflight_ok=True (6 checks declared, F.1-F.4 ENFORCE).
NOTE: planted-grid LIFT is NEGATIVE (-0.095) -- this is EXPECTED and NOT gated: the planted high-intrinsic-dim
TransE arena is deliberately mis-aligned with graph structure (relation operator necessary), so a structural
eigenmap init is not aligned there. The FULL on the sparse CSKG community graph is where structure may help; the
self-test proves only that the machinery runs + the init changes the fit + spectral structure is present + arena is
answerable. (Per null-hyp-smoke discipline: do not gate the smoke on the discriminator's sign.)
