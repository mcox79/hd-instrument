# Pre-reg: CLOSED-FORM coord-source inductive-entity ANCHOR_COMPOSE probe (CSKG)

- anchor_name: `anchor_compose_closedform_coord_cskg_v1`
- cell: `experiments/exp_anchor_compose_closedform_coord_cskg_v1.py`
- queue: `remote_cpu_queue` (closed-form linear algebra, NO SGD; CPU-appropriate; CPU idle)
- run_mode: `full` (seeds 7,13,17); device forced cpu on remote_cpu_queue
- date: 2026-07-13

## Question
The code-family sweep landed `CODES_DONT_STRUCTURED_HURTS_LEARNED_NEEDED`
(MEASURED@data/exp_native_code_family_sweep_cskg_v1/metrics.json): fixed STRUCTURED glass-box CODES do not carry the
additive relational geometry. LEARNED-SGD coords ARE needed for the functional path (AdditiveKGMap default). The
remaining STRICT (no-SGD) option is not codes but CLOSED-FORM COORDINATES. Can a closed-form / rule-derived
derivation of base X[N,k]/D[n_rel,k] carry enough relational geometry that the SAME held-out-entity ANCHOR_COMPOSE
compose+direct-distance arena reaches a material fraction of the LEARNED-SGD 0.128?

If viable -> a STRICT-glass-box source drops into AdditiveKGMap's swappable `CoordinateSource` seam. If dead -> the
learned SGD coords are essential and the functional path is the only one (documented).

## Method (closed-form; ALL non-gradient)
- Stage 1 SPECTRAL X: Laplacian-eigenmap embedding = top-(k+1) singular vectors of the symmetric-normalized relational
  adjacency `Dinv A Dinv` (train edges + self-loops), trivial component dropped, via truncated randomized SVD
  (`torch.svd_lowrank`, positional q/niter = portable base call; deterministic under a saved/restored RNG state).
- Stage 2 CLOSED-FORM ALS of the TransE score, n_sweeps of: (a) `D_r = mean(X_t - X_h)` (exact LS minimizer over D
  given X); (b) n_jacobi Jacobi steps of the normal equations of `min_X sum ||X_h + D_r - X_t||^2 + lam||X - X0||^2`.
  All closed-form linear algebra; alternation makes X translationally consistent so D carries real relational signal
  (spectral-only D ~= 0 -> scramble cannot fail; ALS fixes that -- validated on the planted arena, below).
- COMPOSE + SCORE path is IMPORTED VERBATIM from the learned cell (`build_anchor_compose_codes`,
  `additive_direct_scores`) and the SPLIT is `build_heldout_entity_split_ac` at the SAME knobs + SAME seeds -> the
  held-out arena is bit-identical to the learned run; the coord-source is the ONLY knob (isolates the question).
- knobs: k=24 (matches the learned reference k=24), CF_N_SWEEPS=15, CF_N_JACOBI=3, CF_LAMBDA=0.05, CF_SVD_NITER=6,
  HELDOUT_ENTITY_FRAC=0.15, SUPPORT_FRAC=0.5, n_heldout_eval=3000, seeds=[7,13,17].

## Arms
CLOSEDFORM_ANCHOR (mechanism) | CLOSEDFORM_MEMORIZE (no-induction control, held-out at degenerate base row) |
CLOSEDFORM_SCRAMBLE (must-fail, relation ids scrambled) | CLOSEDFORM_ORACLE (positive control / transductive ceiling,
held-out folded in) | RANDOM_CODES (null) | BASELINE_POP (fit-independence sanity).

## Pre-registered bands (primary metric = FILTERED MRR, degree-unbiased rank-vs-ALL)
LEARNED reference (CITED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr):
ANCHOR_COMPOSE=0.12821, ORACLE_ADDITIVE=0.137293, RANDOM=0.000483.
- ORACLE-FIRES (arena answerable by CLOSED-FORM): CF_ORACLE_mrr >= 3x RANDOM_mrr AND headroom >= 0.003. Else
  `INCONCLUSIVE_CLOSEDFORM_ORACLE_UNDERFIT` (closed-form geometry insufficient even transductively = strict-dead by
  geometry insufficiency).
- STRICT_VIABLE (`STRICT_VIABLE_CLOSEDFORM_COORD_SOURCE`): CF_ANCHOR_mrr >= 0.50*0.12821 (=0.0641) AND
  (CF_ANCHOR-RANDOM) >= MIN_SIG 0.002 AND scramble controlled ((CF_SCRAMBLE-RANDOM) <= 0.25*CF_ORACLE_headroom ->
  RELATIONAL not a proximity confound) AND oracle fires AND not broken AND fair-lowmid margin > 0.
- MIDDLE (`MIDDLE_BAND_PARTIAL_CLOSEDFORM_TRANSFER`): 0.15*0.12821 (=0.0192) <= CF_ANCHOR_mrr < 0.0641, oracle fires.
- STRICT_DEAD (`STRICT_DEAD_CLOSEDFORM_NEAR_RANDOM`): CF_ANCHOR_mrr < 0.0192 (~random). Learned coords essential.
- Gated: `INCONCLUSIVE_TOO_FEW_HELDOUT`; `BROKEN_TEST_CONTROL_BEATS_CLOSEDFORM_ORACLE`.
- HP_SCOPE: STRICT bands apply to CLOSEDFORM_ANCHOR only. CF_ORACLE = positive control (must fire); RANDOM/CF_SCRAMBLE
  = must-not-clear-bar controls; CF_MEMORIZE = no-induction head-to-head; POP = fit-independence sanity.

## Self-test result (MEASURED@data/exp_anchor_compose_closedform_coord_cskg_v1_selftest/metrics.json; planted arena)
SELFTEST_PASS exit 0 on .venv. CF_ANCHOR mrr=0.07097, CF_MEMORIZE=0.00359, CF_SCRAMBLE=0.04763, CF_ORACLE=0.32705,
RANDOM=0.01338, POP=0.00825. anchor_margin=0.05759, scramble_margin=0.02334, oracle_fires=True (24x), arms_differ (6
distinct sigs), vp_ok=True. Proves the closed-form code path runs on the REAL objects, the viable bar is achievable
in principle, and relations carry the signal (scramble fails).

## Schema-vet fields
- cardinality_ok: true; EXPECTED_N_UNITS = n_seeds = 3; per-seed arm-cardinality + >=5 sigs asserted.
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace).
- except-ordering: `except SystemExit: raise` before `except Exception` (no BaseException / no bare except; grep-clean).
- crlb / info-ceiling: primary metric FILTERED MRR; bands are fractions of the MEASURED learned reference (arena
  answerability proven by the learned ORACLE=0.137). discriminator_reachability: OK by construction.
- baseline_in_band: CF_ORACLE must fire (>=3x RANDOM AND headroom>=0.003); RANDOM/POP near 1/N floor.
- discriminator survives scale: analytical -- closed-form derivation is a fixed rule; the memorize null persists at any
  N; ORACLE-fires proves the metric can move; self-test fires all discriminators deterministically.
- arms_differ_verified: true (>=5 of 6 distinct sigs per seed).
- calibration_check: adaptive_with_discriminator_gate (ORACLE_FIRE_RATIO/ABS + learned-reference fractions
  pre-registered, NOT tuned on real data; scramble ceiling = fraction of the MEASURED closed-form oracle headroom).
- defensive_error_checking: start_marker + crash_diagnostic + heartbeat + per-seed failure_class = passed_all_4_patterns.
- cell_chunked: false (closed-form is fast + no OOM-prone SGD transient; 3 seeds in-process; per-seed failure_class
  recorded; no fit checkpoint needed).
- progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints).
- real_code_path_exercised (F.1): [closedform_als_coords, build_anchor_compose_codes, additive_direct_scores,
  fit_and_score_closedform] -- self-test constructs/calls all four at N=300.
- substrate_signature_checked (F.2/F.3): [closedform_als_coords, build_anchor_compose_codes, additive_direct_scores,
  torch.svd_lowrank] -- bound against live signatures with base/portable (positional) kwargs.
- guard_baseline_validated (F.4): [BROKEN_TEST_CONTROL_BEATS_CLOSEDFORM_ORACLE] -- guard fires against CF_ORACLE
  (above the RANDOM floor when it fires), NOT POP (structurally ~0 on held-out arenas); validated at self-test.
- composition_edges: closed-form X/D -> build_anchor_compose_codes -> additive_direct_scores: SHAPE_MATCH (both
  (N,k)/(n_rel,k), reused verbatim from the confirmed learned cell).

## Compute architecture
class (b) sequential-CPU with justification: closed-form linear algebra, NO SGD. Per corpus = one truncated randomized
SVD of a sparse (N,N) normalized adjacency + 15 closed-form ALS sweeps (vectorized index_add_) + query-chunked batched
distance readouts (the (nq,N) map never materialized whole). No gradient training, no OOM-prone transient -> no
memsmoke. Storage SHARDED. Estimated FULL wall < 10 min (3 seeds); timeout 1800s headroom (incl. CSKG core build).

## Dispatch
`bash tools/orchestrator/queue_add.sh remote_cpu_queue anchor_compose_closedform_coord_cskg_v1 experiments/exp_anchor_compose_closedform_coord_cskg_v1.py preregs/2026-07-13_anchor_compose_closedform_coord_cskg_v1.md 1800`
