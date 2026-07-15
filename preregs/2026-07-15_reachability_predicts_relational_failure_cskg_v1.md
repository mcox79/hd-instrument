# Pre-registration: REACHABILITY-AUDIT PREDICTIVE-DIAGNOSTIC TEST

- **Cell:** `experiments/exp_reachability_predicts_relational_failure_cskg_v1.py`
- **Tool:** `hdlab/reachability_audit.py` (the reusable reachability-audit; glass-box, no LLM)
- **Anchor:** `reachability_predicts_relational_failure_cskg_v1`
- **Queue / device:** SMOKE -> `remote_cpu_queue` (discriminator-preview: full induced graph, 1 seed, reduced epochs)
  | FULL -> `remote_cpu_queue` (2 seeds [7,13]) | device=cpu (task-specified; CPU-appropriate scale).
  NO LOCAL COMPUTE: authored + syntax/import-checked locally only; self-test + smoke + full all run REMOTE.
- **Gates:** the grounding deliverable of `notes/drill_grounding_scoping_is_it_subsumed_by_foundation_hub_or
  _separate_2026-07-15.md` -- grounding is largely SUBSUMED by the measured-attribute foundation, with ONE residual
  gap (identity != grounding: a bare canonical id with no reachable measured/grounded content = an ungrounded
  name-tag = a closed-relational-island). The fix = a cheap reachability-audit that doubles as a predictive
  diagnostic. This cell VALIDATES the diagnostic claim.

## Prior-work check (substrate-KB concept-query, mandatory pre-authoring)
`bash tools/substrate_query.sh "reachability audit measured-attribute grounding relational-inference entity
connectivity degree hub"` -> top hit cosine=0.3008 (`notes/research_drill_teacher_free_semantic_bootstrapping_from
_sparse_kb_2026-07-04.md::chunk015`), a KB-density / semantic-bootstrapping note predicting semantic-neighbor
structure emerges at higher KB density. RELATED theme (relational-structure richness) but a DIFFERENT question (that
note is about density-threshold emergence of semantic structure; this cell asks whether per-entity graph reachability
predicts relational-readout FAILURE at CURRENT density). All other hits < 0.30 (token-similarity noise:
relativity/reactivity/retentivity). **Verdict: genuinely NOVEL -- no prior reachability-audit CELL exists. The
degree-control methodology + the transductive-holdout + additive-KGE machinery are reused verbatim from the VET-run
`bucket_diversity_degree_controlled_inference_cskg_v1` cell; the covariate (reachability, not bucket-diversity) and
the diagnostic claim are new.**

## The tool (`hdlab/reachability_audit.py`) -- TWO modes
- **(a) MEASURED-REACHABILITY** (`measured_reachability`): per-entity count of GROUNDED entities reachable within k
  hops. On the CURRENT substrate the grounded set is EMPTY (metadata 100% empty per
  `project_substrate_has_zero_grounded_measured_attribute_data_pure_symbol_graph_2026-07-10`) -> returns all zeros
  (inert). Wired + STUB-READY: pass a real `grounded_mask` (Costanzo/BioGRID-linked entities) to certify
  measured-reachability. The self-test proves the traversal is correct by injecting a synthetic grounded set.
- **(b) RELATIONAL-REACHABILITY** (`k_hop_reachable_mass`, `distance_to_hub`, `mean_neighbor_degree`): runs NOW on the
  existing reduced-CSKG. Proxy anchors for "reaches rich relational structure". This cell tests mode (b)'s diagnostic
  power against the substrate's own relational readout.

## Arena (reused verbatim from the VET bucket_diversity cell)
Induced 6-bucket CSKG-relations subgraph (`load_induced_triples(BUCKET_MAP)` over
`data/substrate_index/concept/relations.jsonl`; CN_DESIRES structurally empty -> realized 6 buckets). Standard
TRANSDUCTIVE held-out-EDGE split (`build_holdout_split`; every entity stays in the graph so its OWN reachability can
be measured strictly from TRAIN-remaining edges -- no query leakage). Additive/TransE KGE fit
(`fit_kge_anchor1`, CE self-adversarial + N3 + reciprocal), readout `additive_direct_scores` (score = -||X_h+D_r-X_t||),
per-query filtered RR `filtered_rr_per_query`. MEASURED@data/exp_bucket_diversity... (same machinery): induced
edges ~91673, entities ~71953 (~62177 out-degree>=1) -- so MIN_ENTITIES=200 query-heads is amply cleared.

## Per-entity quantities (all from TRAIN-remaining edges)
For each QUERY-HEAD entity: `y` = mean filtered RR (its relational-inference accuracy), `z` = undirected TRAIN degree
(the confound = its frequency as a connected node), `R` = k-hop reachable mass at k=2 (the reachability anchor).

## The diagnostic test
- **PRIMARY (gated):** partial Spearman(R, y | z) -- rank correlation of reachability with accuracy CONTROLLING for
  degree. Significance = within-degree-stratum permutation null (`perm_p_partial_stratified`, N_PERM=500): shuffle R
  only among entities of SIMILAR degree (DEG_STRATA_BINS=10 quantile strata); a real partial-rho beating this null is
  signal BEYOND degree. This is the decisive "beyond a degree/frequency confound" control.
- **SECONDARY (reported, non-gating):** partial Spearman(distance_to_hub, y | z) [expected NEGATIVE]; partial
  Spearman(mean_neighbor_degree, y | z) [expected POSITIVE]; raw uncontrolled Spearman(R, y) and Spearman(deg, y)
  [show how much degree alone explains]; bottom-vs-top RR-decile mean reachability (the 6-instance
  relational-failure-track-record tie-in: are the failures the low-reachability entities?).

## SIGN CONVENTION
Reachability defined so HIGHER = better-connected/more-grounded. HARD_PASS expects a POSITIVE partial rho (more
reachable -> higher accuracy) = reachability predicts FAILURE (low reachability -> low accuracy; the task's "negative
correlation" phrasing on the failure axis). distance_to_hub (higher = more peripheral) is the mirror, expected
NEGATIVE.

## Arms + must-fails
- MAIN (fitted additive scorer -> produces y) | RANDOM_CODES (null floor) | RELATION_SCRAMBLE (must-fail control:
  D rows permuted; relational signal must collapse) | BASELINE_POP (frequency incumbent; reported, not gated).
- ARENA_FIRES: MAIN_mrr >= 3x RANDOM_mrr AND (MAIN - RANDOM) >= 0.01 (arena answerable; else INCONCLUSIVE).
- SCRAMBLE_CONTROLLED: (SCRAMBLE - RANDOM) <= 0.25*(MAIN - RANDOM).
- Two seeds (7,13) drive BOTH split AND fit; verdict requires sign-consistency AND significance across BOTH.

## PRE-REGISTERED BANDS (picked BEFORE the run; effect-size thresholds, NOT tuned on outcome -- run not executed)
- `HARD_PASS_REACHABILITY_PREDICTS_RELATIONAL_FAILURE`: arena_fires AND scramble_controlled AND both seeds
  n_entities >= MIN_ENTITIES(200) AND BOTH seeds: partial_rho > 0 (correct sign) AND partial_rho >= RHO_HARD(0.10)
  AND perm_p <= P_SIG(0.05). => the audit's diagnostic claim HOLDS beyond degree.
- `MIDDLE_REACHABILITY_WEAK_OR_LARGELY_DEGREE`: arena+scramble+entities OK AND both seeds correct sign AND both
  perm_p <= P_MID(0.15) AND both |partial_rho| >= RHO_MID(0.04), but not meeting HARD. => reachability correlates but
  its beyond-degree component is weak.
- `REFUTE_REACHABILITY_DOES_NOT_PREDICT_BEYOND_DEGREE`: arena+scramble+entities OK AND NOT correct-sign-significant
  (any seed wrong sign OR both |partial_rho| < RHO_MID OR any perm_p > P_MID OR seed sign-disagreement). => the
  diagnostic claim is UNSUPPORTED; reachability failure-prediction is a degree artifact. HONEST NEGATIVE, valuable.
- `INCONCLUSIVE_ARENA_DID_NOT_FIRE` / `INCONCLUSIVE_SCRAMBLE_NOT_CONTROLLED` / `INCONCLUSIVE_INSUFFICIENT_ENTITIES`:
  fail-closed when the arena or entity population is not sound enough to trust any correlation call.

## Compute architecture
class (a) batched: ONE transductive additive-KGE fit (vectorized torch minibatch SGD, CPU) per seed -- SAME config as
bucket_diversity FULL (k=16, epochs=150, n_neg=64, batch=8192, neg_chunk=16), which ran within budget. The KGE fit is
the mechanism whose per-entity failures we diagnose, so it is NOT over-build (compute-proportionality: there is no
cheaper way to obtain per-entity relational-inference accuracy than running the actual readout; the heavy method is
justified because the CLAIM is the substrate's own per-entity accuracy). Reachability traversal (k-hop BFS,
multi-source BFS, partial Spearman, stratified permutation) is CHEAP (seconds), dwarfed by the fit. Storage SHARDED.
Readout query-chunked batched matmul. device=cpu. Seeds sequential in one process.

## SCHEMA-VET fields
- `arms_differ_verified: true` (MAIN/RANDOM/SCRAMBLE score-signature hashes >= 3 distinct, self-test + per-seed).
- `final_metrics_atomicity: tmp_replace` (write_metrics + os.replace).
- `except SystemExit before except Exception`; no BaseException / no bare except.
- `crlb_n/a`: no closed-form noise floor for a partial-rank-correlation test; feasibility via arena_fires gate +
  MIN_ENTITIES population floor known before the run.
- `baseline_in_band`: arena_fires IS the baseline-in-band check (RANDOM near floor; MAIN clears it).
- `discriminator survives scale`: option (C) discriminator-preview -- SMOKE runs the FULL induced graph (full N/edges,
  1 seed, reduced epochs) to preview arena_fires + entity population + a non-degenerate partial-rho pipeline BEFORE
  the 2-seed FULL commits compute.
- `HP_SCOPE`: arena_fires + scramble_controlled apply to ALL seeds; HARD/MIDDLE/REFUTE bands apply to the cross-seed
  aggregate of the partial-rho.
- `cardinality`: EXPECTED_N_UNITS = n_seeds (2 FULL / 1 SMOKE); per-seed failure halts with failure_class.
- `calibration_check: default_ok_for_this_regime` -- split knobs + fit hyperparams inherited unchanged from the VET
  bucket_diversity cell; RHO/P bands are correlation-convention effect-size thresholds, NOT tuned on the outcome.
- `real_code_path`: self-test constructs the REAL reachability tool + REAL fit/score/RR/partial-rho pipeline at N~150,
  AND exercises mode-(a) measured_reachability with a synthetic grounded set (traversal-correctness proof) + asserts
  inert-when-empty.
- `substrate_signature`: fit_kge_anchor1 bound against live signature (base/portable kwargs).
- `deterministic_seeding: true` (fixed int seeds; sorted iteration; np.random.default_rng only; PROT-023 source-scan).
- `progress_logging: print_flush_true` (line-buffered stdout + per-seed flush).

## ETA
Dominated by the KGE fit, same scale as bucket_diversity FULL (~90K edges, 1 fit/seed, k=16/epochs=150). SMOKE
(1 seed, epochs=40) previews wall time; FULL --timeout computed as ceil(1.5 * smoke_wall_s * (150/40) * (2/1)),
capped at 14400s. Provisional FULL --timeout = 10800s (3h) pending the remote SMOKE wall measurement.
