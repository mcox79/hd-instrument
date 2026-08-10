# Pre-reg: focus_pullin_causal_stage2g_deeper_leaf_split_v1

## Question
Stage-2F (HARD_FAIL, `data/exp_focus_pullin_causal_stage2f_dense_rescore_fine_decode_v1/metrics.json`)
composed a dense-rescore fine-decode (helped 0.213 -> 0.267 at 1,213,912) on top of Stage-2E's hierarchical
sparse+dense sharded store, but still landed `relevant_recall=0.267` / `margin=0.227` at 1,213,912 -- below
the HARD-PASS bar (recall>=0.50, margin>=0.30). Diagnosis (MEASURED@data/exp_focus_pullin_causal_stage2f_
dense_rescore_fine_decode_v1/metrics.json:per_scale.1213912.hierarchical_dense_rescore.diagnose_split_dg_decode):
loss is 100% WRONG_ARGMAX (correct_refused=0, wrong_argmax_frac=0.75), worsening from 0.352 (100K) to 0.75
(1.2M) as max leaf occupancy grows from ~4,274 to 51,873 triples/leaf. Does SUB-SPLITTING the oversized
leaves further (smaller TARGET_LEAF_SIZE, more tier-2 shards per family) reduce per-leaf write-count
crosstalk enough to clear HARD-PASS at 1,213,912 while holding the already-passing 100K point, or does the
fine-decode wall persist even at the finest leaf granularity tractable given per-entity fan-out limits (a
structural floor, not an engineering one)? THIS IS THE LAST PLANNED STORE ITERATION per task contract --
either a clean HARD-PASS here, or an honest HARD-FAIL that ends the store-tuning arc and reframes final
single-item selection as the context-validating LOOP's job (candidate-retrieval / shortlist-hit is already
solved: 0.853 @ 1,213,912).

## Prior-work check (mandatory, USER-locked 2026-07-01)
`bash tools/substrate_query.sh "leaf granularity sub-splitting shard crosstalk per-leaf write count Hebbian
store capacity fine decode single argmax"` run this session. Top hit cosine=0.248 (BELOW the 0.30
threshold) -- `notes/research_drill_optimal_shard_granularity_5x_2026-06-08.md` (offline "sleep defrag"
auto-clustering pitch for shard granularity, a DIFFERENT mechanism: adaptive re-clustering by co-access
density, not a direct K_FAMILY leaf-size sweep on the DG-CA3 hierarchical shard store). 2nd hit cosine=0.245
-- `exp_community_of_communities_nested_retrieval_v2` cert atom (2-tier nested community routing,
conceptually the SAME family as Stage-2E's tier-1/tier-2 design that THIS cell already builds on, cited
directly in Stage-2E's own docstring -- not a new discovery here, already-integrated precedent). No hit
above 0.30. Proceeding as a genuine, non-duplicative extension of Stage-2E/2F within this lineage.

## Mechanism (brain-fidelity framed)
Unchanged from Stage-2F except ONE variable: `TARGET_LEAF_SIZE` (Stage-2E hardcoded 57,000, derived from a
single leaf-capacity-sweep measurement). This cell generalizes `K_FAMILY` into a function of
`TARGET_LEAF_SIZE`: `K_family = 1` if measured family occupancy <= target, else
`ceil(occupancy / target) + 1` (the same +1 hash-imbalance safety margin Stage-2E measured and applied to
AT/VG/CN, now applied uniformly since we don't have fresh per-family fan-out audits at every new K -- more
conservative, cheap since small families stay tiny either way). Family occupancy is measured fresh from the
loaded 1,213,912-edge corpus (not hardcoded), so this reproduces Stage-2E's own K_FAMILY={AT:14,VG:6,CN:5,
WD:1,FN:1,WN:1,CN|WN:1} EXACTLY at target=57,000 (verified: AT ceil(696152/57000)+1=14, CN
ceil(214890/57000)+1=5, VG ceil(257130/57000)+1=6 -- matches Stage-2E's landed K_FAMILY bit-for-bit,
confirming the generalization is a strict superset of the existing mechanism, not a new one).

Brain analog (unchanged from Stage-2F, now with a finer dial): DG/CA3 pattern separation over a SMALLER
population of granule cells per hippocampal "lamella" reduces interference between memory traces sharing
that lamella -- physically fewer engrams per local circuit means less catastrophic interference at write
time. This cell asks whether the brain's actual lamella-count (effectively very fine-grained, thousands of
small independent circuits, not ~29 large ones) is closer to what this substrate needs -- i.e. whether our
"leaves" are simply still too coarse relative to hippocampal reality, or whether crosstalk at this
comparison-set size (k_eff=50 fine-decode candidates) is dominated by something OTHER than raw per-leaf
write count (in which case finer splitting will plateau, not clear the gate) -- this cell distinguishes the
two by MEASURING the recall-vs-leaf-size curve, not assuming which applies.

## Compute architecture
- Storage/routing: reuses Stage-2D/2E/2F's exact primitives verbatim (imported, not re-transcribed):
  `SparseHeteroShardStore`, `DenseShardStore`, `build_dg_projections`, `precompute_dg_val_codebook`,
  `build_relation_majority_shard`, `compute_ingest_shard_ids_real/scrambled`, `compute_query_shard_ids`,
  `build_family_shard_layout`, `_vectorized_entity_hash`, `subject_tier2_local`, `_iterative_attractor`
  (DG-decode diagnose-split), `refuse_gate_calibrate_from_scores`. The fine-decode mechanism (dense-rescore
  over the SAME DG-shortlisted ~50 candidates, global-tau accept -- Stage-2F's PRIMARY metric per its
  measured ADDENDUM-2 pivot, context-gate NOT reintroduced here since Stage-2F already measured it
  regresses) is bit-identical, imported from Stage-2F's `_batched_score_settle_dense_rescore` /
  `eval_gate_hierarchical_dense_rescore`.
- NEW: `derive_k_family_map(occupancy: Dict[str,int], target_leaf_size: int) -> Dict[str,int]` -- the ONE
  new function, a pure closed-form derivation from measured occupancy, no new storage/routing code.
- NEW: `run_leaf_target_unit(...)` -- a thin wrapper around Stage-2F's existing per-scale ingest+eval
  sequence, parameterized by an explicit `k_family_map`/`base_offset`/`total_shards`/`salt_base` instead of
  Stage-2F's module-level `K_FAMILY` global (avoids monkey-patching an imported module's globals across
  sweep points -- cleaner, avoids shared-mutable-state bugs between sweep points run in the same process).
- Memory management (NEW, load-bearing at finer targets): at `target_leaf_size=10,000`, `n_shards~131`
  (vs 29 at baseline), so `SparseHeteroShardStore.W_shards` is `[131,2048,2048]` float32 ~= 2.05GiB and
  `DenseShardStore.W_shards` is `[131,1024,1024]` float32 ~= 0.55GiB, PER ARM. Composed+scrambled arms
  built sequentially within one unit; explicit `del` + `gc.collect()` between arms (not present in Stage-2F,
  which never exceeded 29 shards / ~0.6GiB combined) keeps peak memory to ~1 arm's stores + the shared
  E/R/dg_val_codebook (~6GB) at a time, well within the measured 14.4GB available RAM (THEORETICAL,
  measured via `systeminfo`/`wmic` this session before committing to the finest sweep point).
- Batched GPU: NOT used (CPU numpy/torch, matches Stage-2D/2E/2F precedent) -- same sequential-CPU
  justification as Stage-2F (inherited certified infra + genuine per-unit checkpoint dependency).
- Storage strategy: sharded (unchanged).

## Leaf-size sweep (mandatory declaration)
`TARGET_LEAF_SIZES = [57000, 25000, 15000, 10000]`. The 57,000 point is CITED, not re-run
(MEASURED@data/exp_focus_pullin_causal_stage2f_dense_rescore_fine_decode_v1/metrics.json:per_scale --
compute-proportionality: Stage-2F's K_FAMILY IS this cell's derive_k_family_map(occupancy, 57000) output
bit-for-bit, re-running it would burn ~455s reproducing numbers already on disk). Fresh compute: {25000,
15000, 10000} x {100000, 1213912} scales x {composed, scrambled_tier2} arms = 12 fresh (scale, target, arm)
combinations, checkpointed per (target, scale) unit (6 units) via `tools/exp_checkpoint.py`.
`10,000` is the practical floor for this sweep: CN's measured max single-entity fan-out is 6,081
(MEASURED@Stage-2E module docstring, this session's `np.bincount` hub-audit, not re-measured here) -- a
single mega-fan-out entity's edges cannot be split across leaves (tier-2 routes by whole-subject hash), so
any target below ~6,000-7,000 would silently fail to shrink that family's largest leaf at all. 10,000
leaves ~1.6x headroom above that floor; a 5th, even-finer point was considered and dropped as unlikely to
add information (per the honest-HARD_FAIL discipline -- this cell reports the curve at the 4 points, it
does not grind toward a manufactured PASS).

## HARD-PASS / HARD-FAIL / MIDDLE bands (declared BEFORE running, per task contract, EXACT Stage-2F gate)
- **HARD-PASS**: at the BEST-performing tested `TARGET_LEAF_SIZE`, `relevant_recall` (dense-rescore,
  global tau) >= 0.50 at BOTH 100,000 AND 1,213,912, AND scramble margin >= 0.30 at both, AND
  `false_pull_in_rate` <= 0.20 at both, AND no regression at 100K vs Stage-2E's landed 0.6133 composed
  recall (tolerance 0.05), AND `arms_differ_verified`, AND `cardinality_ok`.
- **HARD-FAIL**: `relevant_recall` at 1,213,912 remains < 0.30 at the FINEST tested granularity (10,000) --
  deeper splitting did not rescue the fine-decode wall; per the task's brain-fidelity framing this is
  reported PLAINLY as "single-argmax is a stricter-than-brain bar; candidate-retrieval (0.853 shortlist-hit)
  is the store's actual job and is already solved" -- NOT ground further (no ensemble-vote epicycles).
- **MIDDLE_BAND**: partial lift (e.g. clears 0.30 but not 0.50 at 1,213,912 at the finest point, or clears
  recall but not margin) -- reported honestly with the full curve, no forced binary framing.
- Task contract also specifies: HARD-FAIL if recall stays <0.30 at 1.2M at the finest granularity tested
  (matches above). This pre-reg additionally treats "recall improves monotonically with finer leaf size but
  plateaus below 0.50 even at the practical fan-out floor" as its own labeled sub-case within HARD-FAIL/
  MIDDLE_BAND (not a new band) -- the recall-vs-leaf-size curve itself is the primary deliverable regardless
  of which band the number lands in.

## Routing/shortlist-accuracy trend (mandatory secondary report, per task contract)
`relevant_in_shortlist_rate` (DG-space coarse retrieval hit-rate, unchanged mechanism from Stage-2E) is
reported at every (target, scale) point. Stage-2E's own certified precedent
(`exp_community_of_communities_nested_retrieval_v2`, cited in prior-work check above) showed 2nd-tier
routing holds fidelity flat as shard count grows within its tested range -- this cell explicitly VERIFIES
that holds here too (routing accuracy must not degrade faster than decode improves) rather than assuming
it from the cited precedent's different regime.

## Discriminator-must-survive-scale (mandatory declaration)
This cell computes fresh points DIRECTLY at the two task-contract scales (100,000 and 1,213,912) -- there
is no separate smaller-scale "smoke" to gate on before committing compute, since the entire question is
scale/leaf-size-dependent by construction and a smaller-scale probe would not exercise the crosstalk
mechanism under test. Per exp_dev's DISCRIMINATOR-MUST-SURVIVE-SCALE rule, this is option (A) (full-N
directly) COMBINED with per-unit checkpointing as the safety net: `--self-test` (tiny synthetic,
real-code-path) is the pre-flight mechanism-fires gate; `--full` IS the discriminator-preview, run
foreground-to-completion with per-(target,scale)-unit checkpoints inspected as they land (each unit's
result is read and sanity-checked before the next is dispatched, so a badly-wrong first point halts the
sweep before burning the rest of the compute budget -- not a blind batch dispatch).

## Self-test / full contract
- `--self-test`: tiny (n_ent=48) synthetic BIGFAM(K=3)/SMALLFAM(K=1) corpus (Stage-2E/2F's exact fixture);
  constructs REAL `KGStore`, `SparseHeteroShardStore`, `DenseShardStore` (real_code_path, gate F.1);
  verifies `derive_k_family_map` reproduces Stage-2E's exact K_FAMILY at target=57000 on the REAL CSKG
  family-occupancy dict (loaded via `precheck_source_field`/family occupancy helper, not re-derived by
  hand); verifies the mechanism activates + differs (arms-differ hash) at 2 tiny target values; verifies
  scramble degrades recall.
- No `--smoke` mode (see Discriminator section) -- `--full` runs the checkpointed sweep directly.
- `--full`: `TARGET_LEAF_SIZES=[25000, 15000, 10000]` (57000 cited from Stage-2F, loaded not recomputed) x
  `SCALES=[100000, 1213912]`, per-(target,scale) checkpointed via `tools/exp_checkpoint.py`
  (unit_key = "leaf|<target>|<scale>"), resumable across separate foreground Bash invocations (each unit
  ~50-360s depending on scale, well under any single invocation's timeout).

## Mandatory fields (per exp_dev canonical instructions)
- `arms_differ_verified: bool` (composed vs scrambled digest-differ, at self-test AND at full, per unit)
- `cardinality_ok: bool` (EXPECTED_N_UNITS = len(TARGET_LEAF_SIZES_FRESH) * len(SCALES) = 6)
- `final_metrics_atomicity: "tmp_replace"` (top-level) + per-unit via `record_unit`/`tools/exp_checkpoint.py`
- `cell_chunked: false` (sweep axis = leaf-target x scale, not seed)
- `start_marker_written: true`, `crash_diagnostic_present: true`, `heartbeat_present: true`
- `deterministic_seeding: true` (all seeds inherited from Stage-2B/2E/2F constants; `derive_k_family_map`
  is a pure closed-form function of measured occupancy, no RNG; no `hash()`-derived ordering)
- `calibration_check: "adaptive_with_discriminator_gate"` (dense-space tau via
  `refuse_gate_calibrate_from_scores`, per-(target,scale,arm), 50/50 internal split -- identical mechanism
  Stage-2F uses, no context-gate reintroduced per Stage-2F's measured negative finding)
- `progress_logging: "print_flush_true"` (per-unit wall time up to ~360s at 1,213,912; total sweep
  estimated ~1,100-1,300s across all 6 fresh units, run across multiple foreground Bash invocations)
- `hp_scope`: `{hierarchical_dense_rescore: [relevant_recall, false_pull_in_rate, scramble_margin,
  no_regression_100k, relevant_in_shortlist_rate]}`
- `crlb_n/a`: empirical leaf-capacity diagnostic (same class as Stage-2E/2F); no closed-form CRLB for
  restricted-comparison-set (k_eff=50) discriminability vs per-leaf write count in this codebase.

## Runtime estimate (HYPOTHESIZED, from Stage-2F's measured per-arm ingest/eval times)
Stage-2F: 1,213,912-scale composed sparse ingest=128.5s, scrambled=165.6s; dense ingest ~15-17s each;
eval ~15-17s each; 100,000-scale ingest ~10-11s each arm, eval ~14s each. Per (target,scale=1213912) unit
(composed+scrambled): ~130+17+15 + 166+17+15 = ~360s. Per (target,scale=100000) unit: ~10+1.5+14 +
11+1.4+14 = ~52s. 3 fresh targets x (360+52) = ~1,236s total fresh compute (~20.6 min), plus one-time data
load + DG_VAL_CODEBOOK precompute (~90-120s per Stage-2E/2F's own breakdown, done ONCE and reused across
all sweep points -- the main efficiency gain over re-running Stage-2F 3x with a monkey-patched K_FAMILY).
Ingest time is NOT expected to scale much with shard count (same total edge count processed; more shards
means more (but smaller) per-shard matmul chunks in the existing sort-and-segment ingest loop) -- this is
an analytical prediction, verified empirically as each unit lands (if ingest time balloons unexpectedly at
finer targets, that itself is a reportable finding, not silently absorbed).
