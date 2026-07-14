# Pre-registration: BUCKET-DIVERSITY DEGREE-CONTROLLED INFERENCE TEST (Part C)

- **Cell:** `experiments/exp_bucket_diversity_degree_controlled_inference_cskg_v1.py`
- **Anchor:** `bucket_diversity_degree_controlled_inference_cskg_v1`
- **Queue / device:** SMOKE -> `local_cpu_queue` (discriminator-preview, full induced graph, 1 seed, reduced epochs) |
  FULL -> `remote_cpu_queue` (2 seeds [7,13]) | device=cpu (task-specified; CPU-appropriate scale).
- **Gates:** Part C of `notes/research_dense_kg_prior_art_and_source_depth_2026-07-14.md` (arXiv:2508.15291 caveat
  replication test); directly gates the >=4-5-of-7-bucket density-optimum premise in
  `research_ideal_foundation_spec_size_density_optimum_2026-07-14.md` Section 1.

## Prior-work check (substrate-KB concept-query, mandatory pre-authoring)
`bash tools/substrate_query.sh "relation type bucket diversity degree controlled held-out inference MRR retrieval"`
-> top hit cosine=0.3086 (`notes/exp_dev_handoff_research_p9_mechanism_diagnosis_2x_2026-06-10.md::chunk010`,
"FREQUENCY-CONTROLLED HELD-OUT"): proposes degree-matching held-out RELATIONS to training relations for a
cross-relation-transfer Hits@10 test. RELATED METHODOLOGY (same general degree-control discipline this cell also
applies) but a DIFFERENT QUESTION (that note controls degree across relation TYPES; this cell controls degree
across an ENTITY's bucket DIVERSITY). 3rd hit cosine=0.2959 (slipnet relation-type cross-activation interference)
is thematically adjacent to the arXiv fragmentation mechanism but a different substrate (spreading activation, not
bind/unbind additive KGE) and below the 0.30 read threshold. **Verdict: genuinely NOVEL for the specific
bucket-diversity-vs-inference-quality question on this substrate; the degree-control methodology has precedent.**

## Mechanism under test
Does per-concept relation-type-BUCKET DIVERSITY help, hurt, or leave unchanged held-out relation-inference quality
on our glass-box additive-KGE substrate, once DEGREE is controlled for (matched within a degree stratum)? Directly
tests whether arXiv:2508.15291's finding (Node-level Maximum Relation Diversity INVERSELY correlated with
link-prediction MRR/Hit@1 in fused dense-embedding models FB15k-237/WN18RR/CoDEx) transfers to a structurally
DIFFERENT readout: our additive scorer separates relation and entity via bind/unbind (score = -||X_h+D_r-X_t||)
rather than fusing all relations into one dense per-entity embedding.

**7-bucket semantic map** (director's audit mapping; LEXICAL relations excluded from graph + vocabulary):
IS_A/HYPERNYM->taxonomic, CN_HAS_PROPERTY->property, PART_OF/CN_HAS_A->part_whole,
CN_USED_FOR/CN_CAPABLE_OF->functional, CN_CAUSES/CN_MOTIVATED_BY_GOAL->causal, CN_AT_LOCATION->spatial,
CN_DESIRES->social. SYNONYM/RELATED_TO/ANTONYM = lexical, excluded entirely (not fed to the graph or bucket
vocabulary).

**MEASURED@this session** (`data/substrate_index/concept/relations.jsonl`, direct count):
- total lines: 189654. Induced (bucket-map-only) edges: 91673. Unique entities in induced graph: 71953
  (62177 with out-degree >= 1).
- **CN_DESIRES has ZERO edges in the active partition** -> the "social" bucket is STRUCTURALLY EMPTY here.
  Realized max diversity is 6 of 7 buckets, not 7. Reported as a finding, not hidden.
- Joint (full out-degree bin x diversity group) counts (full-graph, pre-split; post-split train-degree numbers
  will differ slightly and are what the cell actually measures):
  `d3_5`: div1~213, div2~533, div3plus~350. `d6_8`: div1~19, div2~169, div3plus~295-312. `d9_14`: div1~2 (thin).
  `d15plus`: div1~3 (thin). HYPOTHESIZED@this-prereg (computed from full pre-split degree, not yet post-split).

## Split design (standard TRANSDUCTIVE held-out-EDGE split, NOT held-out-entity)
Every entity stays in the graph; for src entities with full out-degree >= `MIN_SPLIT_DEGREE=5`, hold out
`round(0.3*d)` (clamped to [1,4], capped at d-1) of that entity's OWN out-edges as QUERY; all remaining edges
(including ALL edges of entities below the threshold) are TRAIN. Post-split TRAIN out-degree and TRAIN bucket-set
size (computed ONLY from the entity's remaining train edges, never from its held-out query edges -- avoids
leaking the very thing being predicted) are the two covariates used for stratification. This design isolates
DIVERSITY from raw DEGREE: an entity with 6 edges all-taxonomic vs 6 edges spanning 6 buckets = same degree,
different diversity.

- Degree strata (TRAIN out-degree): `d3_5=[3,5]`, `d6_8=[6,8]`, `d9_14=[9,14]`, `d15plus=[15,inf)`.
- Diversity bins (TRAIN distinct-bucket count): `div1` (single bucket), `div2`, `div3plus` (>=3 buckets).
- **PRIMARY_STRATA = [d3_5, d6_8]** (both div1/div3plus groups clear `MIN_STRATUM_N=10`); `d9_14`/`d15plus` are
  SECONDARY (reported on the curve, excluded from the gated aggregate decision -- their div1 population is too
  thin, itself a finding: single-bucket entities become rare once degree >= 9 in this partition).

## Arms
| Arm | What | Role |
|---|---|---|
| MAIN | fitted additive scorer (X,D), transductive fit on TRAIN | headline |
| RANDOM_CODES | random X,D, no fit | null floor (arena-fires gate) |
| RELATION_SCRAMBLE | MAIN's X, D rows permuted (non-identity perm) at score time | must-fail (relation-identity broken) |
| BASELINE_POP | frequency incumbent (`pop_hits`) | reported for context, not gated |

Scorer = `experiments._kge_anchor1_fit.fit_kge_anchor1` (the SAME additive/TransE-style KGE recipe the
anchor_compose family uses: CE self-adversarial + N3 + reciprocal). Hyperparameter DEFAULTS unchanged (A1_LR,
A1_GAMMA, A1_N_NEG, A1_ADV_TEMP, A1_N3_LAMBDA) -- no new recipe invented. This IS a genuinely NEW split/regime for
this primitive (transductive edge-holdout on the 6-bucket induced subgraph, not the held-out-ENTITY split the
anchor_compose family uses), so Gate-D's literal "reproduce prior chain-grade result at test regime" does not
apply -- declared explicitly: `positive_control_arms: n/a_novel_split_no_prior_atom` (no prior same-regime MEASURED
atom exists to reproduce; what IS reused unchanged is the scorer's hyperparameter defaults).

## Controls / must-fails
- **ARENA_FIRES**: `MAIN_mrr >= 3x RANDOM_mrr AND (MAIN_mrr - RANDOM_mrr) >= 0.01`. If this fails, verdict =
  `INCONCLUSIVE_ARENA_DID_NOT_FIRE` regardless of any lift number.
- **SCRAMBLE_CONTROLLED**: `(SCRAMBLE_mrr - RANDOM_mrr) <= 0.25 * (MAIN_mrr - RANDOM_mrr)`.
- **STRATIFIED PERMUTATION NULL** (the decisive control for the actual density-optimum question): within each
  PRIMARY stratum, shuffle which entities carry the div1/div3plus LABEL (entity-level shuffle, preserving REAL
  group sizes so an entity's multiple queries move together) `N_PERM=500` times; recompute the pooled lift
  (div3plus_mean_RR - div1_mean_RR) each time. `p_perm` = fraction of `|null lift| >= |real lift|`. Establishes the
  noise floor for "a lift this size could arise from degree-stratified grouping alone" at the ACTUAL per-stratum
  sample sizes.
- **Two independent seeds (7, 13)** drive BOTH the holdout split AND the KGE fit -- two independent replicate
  measurements. Final verdict requires sign-consistency AND significance across BOTH seeds.

## PRE-REGISTERED BANDS (picked BEFORE the run)
`aggregate_lift` = weighted mean (weight=min(n_div1,n_div3plus)) of per-PRIMARY-stratum lift, restricted to strata
where BOTH groups clear `MIN_STRATUM_N=10`. `p_perm_aggregate` = MAX (most conservative) per-stratum p_perm among
qualifying strata. Both computed PER SEED, then combined:

- **HELPS** (density-optimum premise SURVIVES the arXiv caveat here): BOTH seeds `aggregate_lift >= +0.02`, BOTH
  seeds `p_perm_aggregate <= 0.15`, same sign both seeds. -> verdict `BUCKET_DIVERSITY_HELPS_DEGREE_CONTROLLED`.
- **HURTS** (arXiv:2508.15291 fragmentation REPLICATES on our substrate -- informative negative, do NOT force the
  density-optimum story): BOTH seeds `aggregate_lift <= -0.02`, BOTH seeds `p_perm_aggregate <= 0.15`, same sign.
  -> verdict `BUCKET_DIVERSITY_HURTS_DEGREE_CONTROLLED_ARXIV_CAVEAT_REPLICATES`.
- **NEUTRAL**: arena fires + scramble controlled, but lift/significance/sign do not jointly satisfy either band.
  -> `BUCKET_DIVERSITY_NEUTRAL_DEGREE_CONTROLLED`.
- **Fail-closed labels** (arena/population not sound enough to trust a call): `INCONCLUSIVE_ARENA_DID_NOT_FIRE`,
  `INCONCLUSIVE_SCRAMBLE_NOT_CONTROLLED`, `INCONCLUSIVE_INSUFFICIENT_STRATA`, `INCONCLUSIVE_SEED_DISAGREEMENT`.

## Compute architecture
Class **(a) batched**: single transductive additive-KGE fit (vectorized torch minibatch SGD, CPU device) per seed
-- no held-out-entity oracle folding, no lever-comparison multiplicity (unlike anchor_compose_magnitude_opt's 4
fits/seed). ~90K train edges vs that reference cell's ~460K edges/4-fits/2-seeds MEASURED elapsed_s=12073
(MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:elapsed_s) -- substantially cheaper.
Readout query-chunked batched matmul (SCORE_CHUNK=256). Permutation test is pure array relabeling (no re-fit,
effectively free compute). Storage SHARDED (each entity its own row in X). device=cpu (task-specified).

## Self-test (Gate F.1/F.2 real-code-path; MEASURED this session)
Tiny planted TransE-consistent arena (n_ent=150, 6 synthetic relations 1:1 mapped to synthetic buckets,
greedy-without-replacement tail selection so repeated-relation low-diversity entities don't degenerate to
duplicate-edge dedup collapse). Runs the IDENTICAL pipeline the FULL run uses: real `build_holdout_split`, real
`fit_kge_anchor1`, real `additive_direct_scores`, real `filtered_rr_per_query`, real `permutation_test_stratum` /
`aggregate_across_strata` / `verdict_from_gates`. Does NOT assert a HELPS/HURTS direction (the open question this
cell exists to answer) -- only that MAIN beats RANDOM (arena fires), SCRAMBLE collapses, both div1 and div3plus
groups are non-empty in >=1 stratum, and permutation p-values are valid probabilities in [0,1].

**MEASURED@data/exp_bucket_diversity_degree_controlled_inference_cskg_v1_selftest/metrics.json** (this session,
after fixing a degenerate-edge-dedup bug in the planted-arena generator -- see below): `SELFTEST_PASS`, elapsed
5.7s, `arena_fires=True`, `scramble_controlled=True`, `arms_differ=True` (3 distinct sigs), `validity_preflight_ok
=True`, all 6 declared preflight checks (real_code_path, substrate_signature, metric_moves,
negative_control_margin, guard_baseline_valid, full_gates_exercised) passed.

**Bug caught + fixed during self-test authoring**: the first planted-arena draft computed a pure
TransE-argmin nearest-tail per edge; for LOW-diversity entities (all edges drawing the SAME relation), every
edge's argmin target was IDENTICAL (same h, same r -> same nearest t every time), so `d` nominally-distinct edges
collapsed to 1 after `list(dict.fromkeys(edges))` triple-level dedup -- every low-div entity's post-dedup degree
fell to 1, below `MIN_SPLIT_DEGREE`, so ZERO div1 entities ever reached the split-eligible pool (first self-test
run: `any_stratum_has_both_groups=False`, all 102 test queries came from div3plus entities only). Fixed by
greedy-without-replacement tail selection (exclude already-used tails from the argmin search per entity) so
repeated-relation entities still get `d` genuinely distinct edges. Re-ran: `SELFTEST_PASS`.

**Advisory (non-blocking) F.3 note**: `assert_signature_compatible` on `fit_kge_anchor1` emits a WARN for
optional kwargs (`batch_size, ckpt, lr, n_neg, neg_chunk, reciprocal`) since they have defaults in the live
signature. These are the SAME kwargs the anchor_compose_magnitude_opt production cell already relies on (shared
recipe, not a new invented interface) -- advisory only, does not block; verified present in `_kge_anchor1_fit.py`
on this local checkout.

## CELL-TEMPLATE MANDATORY declarations
- `arms_differ_verified`: True (MAIN/RANDOM/SCRAMBLE score-signature hashes; self-test measured 3/3 distinct).
- `final_metrics_atomicity`: `tmp_replace` (via `experiments._seed_checkpoint.write_metrics` + `os.replace`).
- `except SystemExit: raise` BEFORE `except Exception` (no `BaseException`, no bare `except`) -- grep-verified
  clean (`grep -nE "except\s+BaseException|except\s*:"` -> no matches).
- `crlb_n/a`: no closed-form noise floor for a stratified-permutation MRR-lift test; feasibility established
  empirically via the arena_fires gate (MAIN must clear RANDOM by a fixed ratio+absolute margin) and via MEASURED
  population counts per stratum (min group size known BEFORE the run).
- `baseline_in_band`: the arena_fires gate IS the baseline-in-band check (RANDOM/POP near floor; MAIN clears it).
- **Discriminator survives scale = option (C) discriminator-preview**: SMOKE runs the FULL induced graph (full N,
  full edge set) at reduced epochs / single seed specifically to preview arena_fires + non-empty PRIMARY strata
  BEFORE the 2-seed FULL commits full compute.
- `HP_SCOPE`: arena_fires + scramble_controlled apply to ALL seeds unconditionally; HELPS/HURTS bands apply to the
  cross-seed aggregate only.
- `cardinality_ok`: `EXPECTED_N_UNITS = n_seeds` (2 for FULL, 1 for SMOKE); a seed failure halts with
  `failure_class` recorded, cardinality breach -> `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
- `calibration_check`: `default_ok_for_this_regime` -- `MIN_SPLIT_DEGREE`/`HOLDOUT_FRAC`/`DEGREE_STRATA`/
  `MIN_STRATUM_N` are pre-registered from a direct MEASURED count of the real partition's degree/diversity joint
  distribution (this session), NOT tuned on the retrieval outcome.
- `progress_logging`: `print_flush_true` (line-buffered stdout; per-seed flush prints). FULL `timeout_s` is
  expected < 1800s per seed based on scale comparison to the reference cell, but SMOKE wall-clock will confirm
  before the FULL `--timeout` is finalized.
- All numbers above tagged MEASURED@ / HYPOTHESIZED@ / CITED@ per META_RULE_AC.

## Dispatch
- SMOKE: `local_cpu_queue`, name `bucket_diversity_degree_controlled_inference_cskg_v1_smoke`, single seed=7,
  k=12/epochs=40/n_neg=32/batch=4096 -- discriminator preview on the FULL induced graph. Timeout set generously
  (3600s) pending measurement; wall-clock used to calibrate the FULL timeout.
- FULL: `remote_cpu_queue` (per role's push-authorization constraint, exp_dev files the cell and returns the exact
  `queue_add.sh` command rather than shipping it directly), 2 seeds [7,13], k=16/epochs=150/n_neg=64/batch=8192,
  `ckpt_every=20` (outage-resumable). Timeout computed from measured SMOKE wall-clock (see completion report).
