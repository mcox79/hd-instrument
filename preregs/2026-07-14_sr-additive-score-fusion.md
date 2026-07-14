# Pre-registration: SR-compose x ANCHOR_COMPOSE score-level fusion (sr_additive_score_fusion_cskg_v1)

Date: 2026-07-14
Status: Pre-registered, SELFTEST_PASS locally, ready for remote dispatch (overnight_queue, GPU)
Experiment file: [exp_sr_additive_score_fusion_cskg_v1.py](../experiments/exp_sr_additive_score_fusion_cskg_v1.py)
Trigger: [exp_dev_handoff_research_sr_compose_close_gap_to_additive_map_2026-07-14.md](../notes/exp_dev_handoff_research_sr_compose_close_gap_to_additive_map_2026-07-14.md)
Drill: [research_sr_compose_close_gap_to_additive_map_2026-07-14.md](../notes/research_sr_compose_close_gap_to_additive_map_2026-07-14.md)

## Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01)

Not run via `tools/substrate_query.sh` this cycle (tool unavailable in this shell context); prior-work
grounding instead comes directly from the two SOURCE cells this fusion combines, both already landed/VET-confirmed
on disk and cited exhaustively below (`exp_graph_spectral_compose_sr_ppmi_nystrom_v1`,
`exp_anchor_compose_inductive_entity_cskg_v1`), plus the research drill's own lit-scan
(`research_sr_compose_close_gap_to_additive_map_2026-07-14.md`, 6 on-disk + 31 external citations). This cell is
NOT a rediscovery: no prior cell in this repo fuses SR-compose and ANCHOR_COMPOSE scores (grepped
`experiments/exp_*fusion*` and `experiments/exp_*sr*additive*` -- no hits before this cell). Novel combination of
two already-proven mechanisms, per the hand-off's own framing.

## Hypothesis (H)

SR-compose (Bellman/local-recursive graph-spectral codebook) and ANCHOR_COMPOSE (additive/TransE map-builder) have
COMPLEMENTARY, not merely correlated, failure profiles on the held-out-entity CSKG-core arena -- SR strong on
cold/sparse-support entities where ANCHOR is measurably weakest (per the sibling degree-stratified frontier-levers
note), ANCHOR strong overall. A non-learned, glass-box SCORE-LEVEL fusion (weighted-sum or reciprocal-rank fusion
over the two methods' independently-real per-query rankings) should therefore be able to exceed ANCHOR_COMPOSE
alone, not merely track the stronger arm.

## Scope correction (exp_dev finding, surfaced before dispatch)

The hand-off framed this as "near-zero cost... pure post-hoc scoring pass over two already-computed score
matrices." On reading both source cells' on-disk artifacts, NEITHER persists per-query score vectors or fit
checkpoints (`data/exp_graph_spectral_compose_sr_ppmi_nystrom_v1/` and
`data/exp_anchor_compose_inductive_entity_cskg_v1/` each contain ONLY `metrics.json` -- MEASURED@ls of both dirs,
2026-07-14). `cleanup_seed_checkpoints` deletes the additive fit's SGD checkpoints on successful completion
(`experiments/_fit_checkpoint.py:140`). A genuine score-level fusion therefore requires RE-DERIVING both methods'
per-query scores on the identical query set -- this cell does that by reusing the exact fit/compose/score
functions VERBATIM (zero new mechanism), but the ANCHOR side needs one re-fit of the additive TransE scaffold via
SGD (GPU), making this a GPU-bound cell, not the CPU-only cell the hand-off's cost framing anticipated. Routed to
`overnight_queue` accordingly (see Compute architecture below).

## Split-alignment prerequisite (the hand-off's one flagged real risk)

CHECKED, not assumed. Both source cells' per-seed `n_train`/`n_heldout_entities`/`n_support`/`n_query_total`/
`n_cold` are IDENTICAL on disk for every shared seed (seed=7: n_train=359692, n_heldout_entities=3862,
n_support=36254, n_query_total=36333, n_cold=154 in BOTH
`data/exp_graph_spectral_compose_sr_ppmi_nystrom_v1/metrics.json:per_seed[0]` and
`data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:per_seed[0]`; seed=13 and seed=17 match likewise).
Source-read confirms WHY: `exp_graph_spectral_entity_codes_cskg_v1.prepare_corpus` calls
`base.build_heldout_entity_split_ac` (`experiments/exp_native_bind_compose_inductive_entity_cskg_v1.py:248`), whose
docstring states it is "COPIED VERBATIM from
experiments.exp_anchor_compose_inductive_entity_cskg_v1.build_heldout_entity_split_ac" including the identical
`n_heldout_eval` subsample RNG (`np.random.default_rng(seed*777+3)`). Given the same (pool_lbl, cfg, seed) the two
cells' `query_int` arrays are bit-identical BY CONSTRUCTION. This cell additionally asserts it EMPIRICALLY per seed
at FULL runtime (`verify_split_alignment`, rebuilds the split independently via
`exp_anchor_compose_inductive_entity_cskg_v1.build_heldout_entity_split_ac` and asserts `np.array_equal` against
the SR side's `prep["query_int"]`/`support_int`/`train_int`) -- `INCONCLUSIVE_FUSION_PRECONDITION_FAILED` if it ever
breaches, rather than trusting the argument alone.

## Fusion rules (glass-box, non-learned; whole curve reported, not a cherry-picked point)

- `FUSE_SUM(w)`: `score_fused = (1-w)*normalize_rows(sc_ANCHOR) + w*normalize_rows(sc_SR)`, per-query min-max
  row normalization (standard CombSUM-style IR fusion), swept over `W_GRID = [0.0, 0.25, 0.5, 0.75, 1.0]`.
- `FUSE_RRF`: reciprocal-rank fusion, `1/(60+rank_ANCHOR) + 1/(60+rank_SR)` (Cormack, Clarke & Buettcher 2009
  standard constant, zero tuning).
- Must-fail controls: `FUSE(ANCHOR, SR_SCRAMBLE)`, `FUSE(ANCHOR_SCRAMBLE, SR)`, `FUSE(ANCHOR, RANDOM_CODES)` at
  both w=0.5 and RRF -- must NOT exceed ANCHOR_COMPOSE alone by more than `MUST_FAIL_EPS=0.005`.
- Self-fuse sanity: `FUSE(ANCHOR, ANCHOR)` at w=0.5 -- must EQUAL ANCHOR_COMPOSE within `SELF_FUSE_TOL=0.003`
  (exact monotonic-rescale identity, not merely a bound).

## Pre-registered bands (picked BEFORE the run)

`ADD_ALONE`/`SR_ALONE` below are the RE-MEASURED values from this run's own re-fit (self-consistent gate even if
SGD noise across independent GPU runs shifts ANCHOR_COMPOSE slightly from its historical value), cross-checked
against the CITED historical constants via reproduction tolerances.

- **HARD-PASS**: `best_fused_mrr` (over `{w=0.25, w=0.5, w=0.75, RRF}`) `>= ADD_ALONE + 0.02` AND all must-fail
  fused controls `<= ADD_ALONE + 0.005` AND self-fuse identity holds (`<= 0.003` from ADD_ALONE) AND both source
  mechanisms reproduce their CITED historical MRR (ANCHOR within `0.03` of `0.12821`; SR_COMPOSE_NYS within `0.01`
  of `0.073825`) AND split-alignment holds for every seed.
- **HARD-FAIL**: `best_fused_mrr <= ADD_ALONE` (no lift) AND SR_COMPOSE_NYS/SR_COMPOSE_FLAT does NOT beat
  ANCHOR_COMPOSE in ANY degree-stratified support-bucket (`cold`/`d1`/`d2_3`/`d4_7`/`d8plus`, min population
  `MIN_STRAT_Q=8`) -- a genuine negative: the two methods' errors are too correlated to gain from fusion.
- **MIDDLE-BAND**: `0 < lift < 0.02` -> degree-stratify; report as real-but-small/concentrated (cold/d1) if so.
- **INCONCLUSIVE**: reproduction mismatch, split misalignment, must-fail control violated, or self-fuse sanity
  fails -- any of these means the fusion numbers cannot be trusted regardless of the headline lift
  (`INCONCLUSIVE_FUSION_PRECONDITION_FAILED`).

## Cited mechanism / paper

- Dayan 1993 (SR = local Bellman fixed point); Stachenfeld, Botvinick & Gershman 2017 (hippocampus as predictive
  map) -- WHY SR-compose is a genuine local-recursive estimate, not an approximation (motivates the SOURCE cell,
  cited here for why SR carries independent, non-redundant signal).
- GraIL (Teru et al., ICML 2020) and InGram (arXiv:2305.19987) -- structural+relational fusion beats either alone,
  concentrated where the relational-only method is weakest (motivates the complementarity hypothesis H above).
- "Unpacking Positional Encoding in Transformers: A Spectral Analysis of Content-Position Coupling"
  (arXiv:2505.13027) -- naive additive EMBEDDING-space fusion of a structural and a content code is a documented
  failure mode; motivates doing fusion at SCORE level (this cell) instead.
- Cormack, Clarke & Buettcher, "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods,"
  SIGIR 2009 -- the RRF formula + standard `k=60` constant used verbatim.

## SCHEMA-VET / cell-template gates (self-verified before dispatch)

- `arms_differ_verified`: sig-hash per arm at FULL (>= 17 distinct sigs required out of 20 arms); 3 pairs
  DECLARED-exempt (`FUSE_SUM_w000`==`ANCHOR_COMPOSE`, `FUSE_SUM_ANCHOR_SELF_w050`==`ANCHOR_COMPOSE`,
  `FUSE_SUM_w100`==`SR_COMPOSE_NYS`) -- intentional monotonic-rescale identities, not bugs.
- `final_metrics_atomicity`: `tmp_replace` (via `_seed_checkpoint.write_metrics` + `os.replace`).
- `except SystemExit: raise` before `except Exception` (no bare `except:` / `except BaseException:` -- grep-gate
  verified clean before dispatch).
- `crlb_n/a` (no classical CRLB form applies); `discriminator_reachability`: HARD-PASS threshold
  (`ADD_ALONE + 0.02 ~= 0.148`) sits strictly below the MEASURED `ORACLE_ADDITIVE` ceiling (`0.137293` CITED... note
  the ceiling is actually BELOW the naive HARD-PASS arithmetic sum, see Pre-mortem #1) -- reachability caveat
  flagged explicitly in Pre-mortem below, not hidden.
- `baseline_in_band`: both re-measured `ADD_ALONE` and `SR_ALONE` must reproduce their CITED values (reproduction
  gate, not silent pass-through).
- `discriminator survives scale`: option B (analytical) -- both source mechanisms are ALREADY chain-grade
  MEASURED at FULL scale (independently scramble-verified real); this cell does not re-prove either mechanism
  fires, only whether combining them lifts the ceiling, which is fundamentally a FULL-scale question (needs
  CSKG's actual measured degree heterogeneity). Self-test instead proves the FUSION ARITHMETIC (not the joint
  discriminator) is implemented correctly, on real score tensors from AC's own planted TransE arena --
  SELFTEST_PASS locally (12.8s): `anchor_mrr=0.40467` (bit-reproduces the parent ANCHOR cell's own self-test value
  exactly), `self_fuse_mrr=0.40467` (exact identity), `fuse_with_random_mrr=0.15937` and `rrf_with_random_mrr=0.09169`
  (both far below `anchor_mrr`, must-fail holds with a wide margin), `scramble_mrr=0.13595` (also bit-reproduces).
- `HP_SCOPE`: `{ANCHOR_COMPOSE: [reproduce_add], SR_COMPOSE_NYS: [reproduce_sr], FUSE_SUM_w025/w050/w075/FUSE_RRF:
  [hard_pass_lift], FUSE_SUM_*_SRSCR/*_RANDOM/FUSE_RRF_*_SRSCR/*_RANDOM: [must_fail_le_add_alone],
  FUSE_SUM_ANCHOR_SELF: [self_fuse_identity]}`.
- `cardinality_ok`: `EXPECTED_N_UNITS = 3` (seeds); each seed must produce all 20 arms + split-alignment pass.
- per-unit failure-class instrumentation: no bare except; per-seed `failure_class` recorded in `seed_failures`.
- `calibration_check`: `default_ok_for_this_regime` -- every band/constant (`LIFT_ABS`, `MUST_FAIL_EPS`, `K_RRF`,
  `W_GRID`, `REPRODUCE_TOL_*`) pre-registered above, not tuned on real data; the CSKG-core + held-out split config
  is copied verbatim from both parent cells (`heldout_entity_frac=0.15`, `support_frac=0.5`, `k_core=12`,
  `n_heldout_eval=3000`, `seeds=[7,13,17]`).
- §15-F (`real_code_path_and_signature_preflight`): self-test constructs the REAL `fit_kge_anchor1` +
  `build_anchor_compose_codes` + `additive_direct_scores` + `KGStore`/`build_store_with_codes`/`ingest_triples`
  objects at tiny scale (ENFORCE mode; a declared-and-failing check would have raised and blocked this ship --
  none did). Signature checks bind against the LIVE `inspect.signature` for all 4 reused callables; only advisory
  (non-blocking) WARNs fired for version-specific optional kwargs (`lr`, `n_neg`, `batch_size`, `neg_chunk`, `ckpt`,
  `reciprocal`, `rel_perm`, `chunk`) -- all have stable defaults and are portable across the local/remote drift the
  advisory warns about.
- `progress_logging`: `print_flush_true` (line-buffered stdout + per-seed flush prints + `_heartbeat.jsonl`);
  required because `--timeout 10800 >= 1800`.

## Compute architecture

Class (c) MIXED. ANCHOR-side additive fit = minibatch SGD, GPU-batched (`device=auto/cuda`), ONE fit per seed
(ADDITIVE only -- the parent cell's ROTATE and ORACLE arms are skipped, not needed for the fusion question; their
CITED historical ceilings are reused for context instead of re-measured). SR-side = closed-form randomized-SVD,
CPU, reused wholesale via `SR.score_all_arms` (matches the SR cell's own hardcoded `device=cpu` path). Fusion
arithmetic (`normalize_rows`/`ranks_from_scores`/weighted-sum/RRF) = vectorized torch ops over already-computed
`(nq,N)` score tensors, no training, seconds. Storage: SHARDED throughout (per-entity additive codes on the
ANCHOR side; SR side reuses its own native per-entity Hebbian KGStore codes) -- no bundled global fact store
anywhere in this cell.

## Timeout justification (REQUIRED per exp_dev discipline)

`FULL_CFG` reuses the ANCHOR cell's exact hyperparameters (`k=24, epochs=500, n_neg=128, batch=8192, neg_chunk=16`)
-- MEASURED@`data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:elapsed_s=12073.5` for 3 seeds x 3
model-fits (ADDITIVE+ROTATE+ORACLE). This cell fits only 1 of those 3 models per seed -> estimated
`~12073.5/3 ~= 4025s`. SR side reused wholesale, MEASURED@`data/exp_graph_spectral_compose_sr_ppmi_nystrom_v1/
metrics.json:elapsed_s=1651.9` for 3 seeds. Fusion/degree-stratification overhead is vectorized torch ops on
`(3000, 25752)` tensors, estimated `< 2 min` total. **Estimated FULL wall time: ~4025 + 1652 + ~120 ~= 5800s
(~97 min).** `--timeout 10800` (3h) gives ~1.9x safety margin for GPU-host variance, cold-start, and CSKG
provenance-rebuild overhead (should be cache-hit from the two parent cells' prior runs).

## Pre-mortem (top 3 failure causes)

1. **HARD-PASS arithmetic sits ABOVE the naive oracle-additive-only headroom, so the bar may be tighter than
   first stated.** `ADD_ALONE + 0.02 ~= 0.148` is actually SLIGHTLY above `ORACLE_ADDITIVE=0.137293` (the
   best-possible-in-arena ceiling if held-out codes were fully learned/folded-in) -- meaning the naive per-arm
   ceiling comparison undersells how hard HARD-PASS actually is: fusion would have to do better than what
   full transductive knowledge of the held-out entity's own edges achieves. This is NOT necessarily impossible
   (the two channels combine INFORMATION the single-oracle-fold-in setup does not have access to under a
   different combination), but it is a genuine reason to expect HARD-PASS is the harder bar to clear versus
   MIDDLE-BAND, and to treat any HARD-PASS result with extra scrutiny (verify it isn't a fusion-arithmetic
   artifact before headlining it).
2. **The two methods' errors may be too correlated on THIS specific graph.** Both mechanisms ultimately draw on
   the same underlying local-neighborhood structure (SR = transition-weighted neighbor aggregate; ANCHOR = mean
   of neighbor tail-estimates) -- if their failure modes correlate more than the GraIL/InGram literature precedent
   suggests (those papers combine genuinely orthogonal signal sources: subgraph logical rules vs. learned
   embeddings, not two flavors of neighbor-averaging), fusion could land in HARD-FAIL. This is exactly the
   informative-negative case the hand-off pre-registers for, not a design flaw.
3. **GPU re-fit noise could push `ADD_ALONE` far enough from `CITED_ADD_COMPOSE=0.12821` to trip
   `INCONCLUSIVE_FUSION_PRECONDITION_FAILED`** despite identical hyperparameters/seeds, since Adam + minibatch
   SGD on CUDA is not bit-reproducible across separate processes/driver versions. `REPRODUCE_TOL_ADD=0.03` is set
   generously (vs `REPRODUCE_TOL_SR=0.01` for the closed-form SR side) to absorb this, but a genuinely different
   GPU/driver stack on the remote host could still land outside tolerance -- if so, report as
   INCONCLUSIVE_REPRODUCTION_MISMATCH and re-derive the split-alignment/hyperparameter parity before re-dispatch,
   not silently accept a drifted ADD_ALONE as the new gate reference.

## Expected wall time

~97 minutes estimated (see Timeout justification); `--timeout 10800` (3h) ships with margin.

## Dispatch

`bash tools/orchestrator/queue_add.sh overnight_queue sr_additive_score_fusion_cskg_v1 experiments/exp_sr_additive_score_fusion_cskg_v1.py preregs/2026-07-14_sr-additive-score-fusion.md 10800`

Routed to `overnight_queue` (GPU) because the ANCHOR-side additive fit needs SGD (contrast: a pure-CPU
`remote_cpu_queue` cell would be appropriate only if BOTH mechanisms re-scored off saved codes with no re-fit,
which is not the case here -- see Scope correction above).
