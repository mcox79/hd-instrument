# Pre-reg: CLOSED-FORM coord-source BUDGET SWEEP (strict-path revival probe, CSKG)

- anchor_name: `anchor_compose_closedform_budget_sweep_cskg_v1`
- cell: `experiments/exp_anchor_compose_closedform_budget_sweep_cskg_v1.py`
- queue: `remote_cpu_queue` (closed-form linear algebra, NO SGD; CPU-appropriate; fills idle CPU)
- run_mode: `full` (seeds 7,13,17 x k_grid {24,64,128,256} = 12 units); device forced cpu on remote_cpu_queue
- date: 2026-07-13

## Question (strict-path revival)
The k=24 closed-form cell landed `STRICT_DEAD_CLOSEDFORM_NEAR_RANDOM`
(MEASURED@data/exp_anchor_compose_closedform_coord_cskg_v1/metrics.json). The decisive VET finding: the closed-form
family's OWN transductive INFO-ORACLE (held-out edges folded IN = the ceiling of what the geometry can represent)
collapsed to CF_ORACLE mrr=0.0087 at k=24 vs the additive-SGD ORACLE 0.137293 (~16x gap), and the inductive CF_ANCHOR
(0.0097) sat right AT that ceiling -- the closed-form geometry could not even REPRESENT the training edges at k=24. So
the k=24 STRICT_DEAD may be a REPRESENTATION-BUDGET artifact, not a family wall. This cell sweeps the budget and
measures the closed-form info-oracle as a FUNCTION of budget to decide: UNCONDITIONALLY dead, or under-budgeted?

## Method (budget sweep; closed-form machinery IMPORTED VERBATIM)
- Sweep the representation budget `k in {24, 64, 128, 256}` on the BIT-IDENTICAL held-out-entity arena (the split
  depends only on the seed, NOT on k, so every k re-scores the SAME held-out query edges; only the coordinate
  dimensionality changes -> k is the ONLY knob). All other closed-form knobs FROZEN at the landed cell's values
  (CF_N_SWEEPS=15, CF_N_JACOBI=3, CF_LAMBDA=0.05, CF_SVD_NITER=6) so the k=24 point REPRODUCES the landed CF_ORACLE.
- The closed-form derivation (`closedform_als_coords`: spectral Laplacian-eigenmap init + closed-form ALS of the TransE
  score, NO gradient descent), the verbatim compose op (`build_anchor_compose_codes`), the score readout
  (`additive_direct_scores`), the arms/controls, and the whole `run_corpus` arena are IMPORTED VERBATIM from the landed
  cell `exp_anchor_compose_closedform_coord_cskg_v1` -> the per-k measurement is bit-identical to the landed run at
  k=24 and the budget is the only thing that varies.
- knobs: HELDOUT_ENTITY_FRAC=0.15, SUPPORT_FRAC=0.5, n_heldout_eval=3000, seeds=[7,13,17], k_grid=[24,64,128,256].

## Arms (per (seed,k) unit; imported verbatim from the closed-form cell)
CLOSEDFORM_ANCHOR (inductive mechanism, secondary) | CLOSEDFORM_MEMORIZE (no-induction control) | CLOSEDFORM_SCRAMBLE
(must-fail, relation ids scrambled) | CLOSEDFORM_ORACLE (positive control / transductive ceiling = the PRIMARY sweep
signal) | RANDOM_CODES (null) | BASELINE_POP (fit-independence sanity).

## Pre-registered bands (primary metric = FILTERED MRR; bands are fractions of the MEASURED additive references)
MEASURED landed anchor (off-disk): CF_ORACLE(k=24)=0.0087, CF_ANCHOR(k=24)=0.0097, RANDOM=0.000483 (per-seed CF_ORACLE
{0.0078,0.0078,0.0105}, low cv -> robust). CITED additive reference: ORACLE_ADDITIVE=0.137293, ANCHOR_COMPOSE=0.12821.
- REPRODUCE-K24 (validity anchor): |CF_ORACLE(k=24) - 0.0087| <= 0.005. Off-tolerance ->
  `INCONCLUSIVE_K24_ORACLE_NOT_REPRODUCED` (untrustworthy sweep: arena/derivation drifted from the landed run).
- STRICT_PATH_VIABLE (`STRICT_PATH_VIABLE_BUDGET_LIMITED`): CF_ORACLE(k_max=256) >= 0.50*0.137293 (=0.06865) AND rise
  CF_ORACLE(256)-CF_ORACLE(24) >= 0.02 (material, budget-driven) AND not broken. => the closed-form family CAN
  represent the arena given budget -> the strict glass-box path is REVIVABLE (a high-budget closed-form source drops
  into AdditiveKGMap's `CoordinateSource` seam).
- STRICT_DEAD_UNCONDITIONAL (`STRICT_DEAD_UNCONDITIONAL_ACROSS_BUDGET`): CF_ORACLE_best (max over k) < 0.15*0.137293
  (=0.02059) at ALL budgets AND rise < 0.02 (genuine plateau). => closed-form spectral+ALS geometry fundamentally
  cannot embed this relational arena at any tested budget; the LEARNED-SGD source is the only viable one; CLOSE the
  strict-glass-box line (documented).
- MIDDLE (`MIDDLE_BAND_PARTIAL_BUDGET_RESPONSE`): oracle rises but sub-half (best in [0.02059, 0.06865)) -> the family
  responds to budget but does not reach viable at k<=256; recommend larger budget / alt estimator before closing.
- SECONDARY (reported, non-gating): CF_ANCHOR(best-k) vs 0.50*0.12821 (=0.0641) -> does the INDUCTIVE compose approach
  the learned anchor at the best budget.
- Gated: `INCONCLUSIVE_TOO_FEW_HELDOUT`; `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` (< 12 units);
  `BROKEN_TEST_CONTROL_BEATS_CLOSEDFORM_ORACLE`.
- HP_SCOPE: VIABLE/DEAD bands apply to the CF_ORACLE(k) trajectory (family-representability). CF_ANCHOR = secondary
  (reported). CF_ORACLE = positive control per k; RANDOM/CF_SCRAMBLE = must-not-clear controls; CF_MEMORIZE =
  no-induction head-to-head; POP = fit-independence sanity.

## Self-test result (MEASURED@data/exp_anchor_compose_closedform_budget_sweep_cskg_v1_selftest/metrics.json; planted arena, k_grid={6,12})
SELFTEST_PASS exit 0 on .venv under `VALIDITY_PREFLIGHT_MODE=enforce`. Top-budget (k=12): CF_ANCHOR beats RANDOM
(anchor_margin=0.05759), scramble fails (scramble_margin=0.02334), oracle_fires=True, arms_differ (>=5 sigs),
pop_at_floor=True. cf_oracle_across_budget=[0.2253, 0.32705] -> the closed-form oracle MOVES with budget
(metric_moves fires). selftest sweep verdict = STRICT_PATH_VIABLE_BUDGET_LIMITED (the planted TransE arena IS
representable by closed-form and the oracle rises with budget -> both bands proven reachable). vp_ok=True (all 7
checks). Proves the sweep runs on the REAL objects across >=2 budgets, the viable bar is achievable in principle, and
relations carry the signal.

## Schema-vet fields
- cardinality_ok: true; EXPECTED_N_UNITS = n_seeds * len(k_grid) = 3*4 = 12; per-(seed,k) >=5 sigs asserted;
  `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if fewer land.
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace).
- except-ordering: `except SystemExit: raise` before `except Exception` (no BaseException / no bare except; grep-clean).
- crlb / info-ceiling: primary metric FILTERED MRR; bands are fractions of the MEASURED additive references (arena
  answerability proven by the additive ORACLE=0.137). discriminator_reachability: OK by construction.
- baseline_in_band: CF_ORACLE fire ratio reported per k; RANDOM/POP near the 1/N floor; k=24 reproduces landed 0.0087.
- sweep_alignment_verdict: ALIGNED -- the swept parameter (k = coordinate dimensionality) is EXACTLY the budget every
  closed-form primitive (SVD rank, ALS solve, readout) experiences; no nominal-vs-effective mismatch.
- discriminating_fraction: the primary axis is a TRAJECTORY (CF_ORACLE vs the additive ceiling), not a per-point band;
  the self-test proves the sweep axis MOVES (metric_moves) and both VIABLE/DEAD bands are reachable.
- discriminator survives scale: analytical -- closed-form derivation is a fixed non-SGD linalg pipeline; the memorize
  null persists at any N; the self-test fires all discriminators across >=2 budgets deterministically.
- arms_differ_verified: true (>=5 of 6 distinct sigs per (seed,k)).
- calibration_check: adaptive_with_discriminator_gate (ORACLE_FIRE_RATIO/ABS + additive-reference fractions + REPRODUCE
  tolerance pre-registered, NOT tuned on real data; k=24 reproduces the landed oracle).
- defensive_error_checking: start_marker + crash_diagnostic + heartbeat + per-(seed,k) failure_class = passed_all_4.
- cell_chunked: false (closed-form is fast + no OOM-prone SGD transient; units in-process; per-unit failure_class
  recorded).
- progress_logging: print_flush_true (line-buffered stdout + per-(seed,k) flush prints); timeout_s 10800 >> 1800.
- real_code_path_exercised (F.1): [run_corpus, closedform_als_coords, build_anchor_compose_codes,
  additive_direct_scores] -- self-test runs run_corpus (imported verbatim) at k in {6,12} across the REAL objects.
- substrate_signature_checked (F.2/F.3): [closedform_als_coords, build_anchor_compose_codes, additive_direct_scores,
  run_corpus, torch.svd_lowrank] -- bound against live signatures with base/portable (positional) kwargs.
- guard_baseline_validated (F.4): [BROKEN_TEST_CONTROL_BEATS_CLOSEDFORM_ORACLE] -- guard fires against CF_ORACLE_best
  (above the RANDOM floor when it fires), NOT POP (structurally ~0 on held-out arenas); validated at self-test.
- composition_edges: closed-form X/D -> build_anchor_compose_codes -> additive_direct_scores: SHAPE_MATCH (reused
  verbatim from the confirmed learned cell).

## Compute architecture
class (b) sequential-CPU with justification: closed-form linear algebra, NO SGD. Per (seed,k) unit = two truncated
randomized SVDs (train + oracle adjacency) + 15 closed-form ALS sweeps (vectorized index_add_) + query-chunked batched
distance readouts (the (nq,N) map never materialized whole; readout size is k-INDEPENDENT so higher k adds no OOM
risk). No gradient training, no OOM-prone transient -> no memsmoke. Storage SHARDED. Landed k=24 3-seed = 140s;
sweep est ~15-45 min on CPU (SVD orthonormalization superlinear in k at k=256); timeout 10800s (3h) headroom on an
unknown-speed remote CPU.

## Dispatch (HANDED OFF -- exp_dev does not run the remote SCP ship; orchestrator ships + REMOTE VERIFY)
`bash tools/orchestrator/queue_add.sh remote_cpu_queue anchor_compose_closedform_budget_sweep_cskg_v1 experiments/exp_anchor_compose_closedform_budget_sweep_cskg_v1.py preregs/2026-07-13_anchor_compose_closedform_budget_sweep_cskg_v1.md 10800`
