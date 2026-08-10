# Pre-registration: exp_focus_pullin_causal_stage2d_context_gated_sharded_store_v1

**Filed by:** exp_dev, 2026-08-10. **Task source:** Director spawn prompt ("STAGE-2D: does wiring
context-gated / sharded storage into KGStore hold recall at CSKG scale") **REDIRECTED mid-design** by
Director message (this turn) after disk-verifying `notes/research_brain_faithful_scale_store_retrieval_
rescue_2026-08-09.md`. The redirect changes the mechanism from read-side-only shortlisting over a
SHARED corrupted W (my original design) to write-AND-read-side K-separate-physical-shard KGStores, plus
a second lever (DG/CA3 sparse coding within-shard) and a real CSKG-native shard key. This pre-reg
reflects the REDIRECTED design; exp_dev owns the final band VALUES per the redirect message.

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "context gated sharded store subject keyed hebbian W crosstalk capacity
rescue modularity concept-neighborhood shard"` -> top hit `skewed_shard_capacity_cpu_v1` cosine=0.2881
(MIDDLE_BAND, single-seed smoke, largest-shard=370, unrelated flat-bundle-capacity mechanism, NOT
KGStore's (s,p)->o relational bind) -- below the 0.30 threshold. **Verdict: genuinely novel** -- no
prior cell tests context-gated/sharded KGStore retrieval at real CSKG scale. Independently, this cell
directly composes THREE already-HARD_PASS-certified-or-built organs per the Director's redirect
(disk-verified by exp_dev this turn, not just trusted from the redirect message):
- `exp_community_bounded_retrieval_scale_invariance_v1` -- HARD_PASS confirmed on disk
  (`data/exp_community_bounded_retrieval_scale_invariance_v1/metrics.json`): TREATMENT fidelity flat
  1.000/1.000/1.000/0.996 across V=580->58000 while CONTROL collapses 0.789->0.023->0.000->0.000 (same
  shape as KGStore's own Stage-2B collapse). This is the mechanism-class precedent for "shard the store,
  not just the search."
- `exp_graph_community_detection_v1` -- HARD_FAIL confirmed on disk (`comm=0.625` ambiguous, ~majority),
  the reason this cell does NOT use automatic community detection and instead uses CSKG's own real
  per-edge `source` provenance field (see "Shard key" below).
- `hdlab/hippocampal_encoder.py` -- `DGProjection`/`CA3AutoAssociator`/`HippocampalEncoder` read on disk,
  confirmed self-tested (14/14 selftests, expand-then-sparsify + sparse-outer-product Hebbian write) but
  never wired to a real store or run past unit scale. This cell is the first real-scale composition.

## What / why (redirected)
Stage-2B (bit-identical baseline reused here) showed KGStore's single `[1024,1024]` dense Hebbian `W`
collapses `relevant_recall` 0.967(1K)->0.700(10K)->0.000(30K+) as more (s,p,o) triples are Hebbian-written
into the SAME matrix -- a write-side crosstalk wall (dense-Hopfield ~0.14N regime), not merely a read-side
false-admission problem. Stage-1.5's context-gate (narrows candidates from a SHARED, still-corrupted W)
and Stage-2C's resonator (falsified, basin-proliferation) do not fix this. The redirected design routes
BOTH ingest and query through K real physical shard stores selected by a coarse, exact, already-on-disk
context key (CSKG's own edge `source` provenance tag), and stacks a SECOND lever (DG/CA3 sparse coding
within each shard, Willshaw/Kanerva capacity class instead of dense-Hopfield) because the real shard-size
distribution (measured below) is severely skewed and shard-count alone is not expected to be sufficient
for the dominant shard.

## IMPLEMENTATION CORRECTION (caught during self-test authoring, BEFORE any compute burned -- disclosed,
not silently fixed). An earlier draft of the design below (superseded, this is the note documenting the
catch) had POSITIVE/relevant queries route via the sampled triple's own TRUE per-edge `source` tag at
query time, with only NEGATIVE queries using `relation_to_majority_shard`. Working through the self-test's
arms-must-differ mechanism check surfaced why that is not a meaningful test: if write-time routing and
read-time routing for a re-derived query BOTH use the identical per-triple label array (whether the REAL
`source` or a SCRAMBLED permutation of it), the two are trivially self-consistent regardless of whether the
label correlates with content -- there is no misrouting mechanism, so `CONTROL_SCRAMBLED_SHARD_KEY` would
not actually collapse (KGStore's E/R are i.i.d. random bipolar codebooks with no baked-in semantic
structure, so crosstalk capacity is a function of shard SIZE, not shard content-coherence, for THIS
substrate -- a scrambled-but-internally-consistent partition performs identically to a real one under a
"query knows its own true label" convention). **Fix, adopted below and implemented (not a retrofit)**:
ALL queries (positive and negative alike) route ONLY via `relation_to_majority_shard[p]` -- the one signal
knowable before you know if/where an answer exists, matching a realistic deployment where you know the
relation type but not private per-fact metadata. Since ~30% of relations are provenance-mixed and, more
importantly, SCRAMBLING destroys the relation<->source correlation ENTIRELY (a pure relation's true edges
get spread near-uniformly across all `K=7` scrambled shards, so relation-majority routing only reaches
`~1/K` of the real content), this creates a genuine, measurable misrouting mechanism for the scramble
control while keeping the real-key arms' routing realistic and non-oracle. Self-test's tiny-scale
mechanism check (`shard_labels_t = p_t % n_shards_t`, 100%-pure by construction, mirroring the real
corpus's 23/33-pure-relation structure) verifies `SCRAMBLE_DID_NOT_DEGRADE_{DENSE,SPARSE}` would fail loud
if this were broken.

## Shard key (measured this session, CITED numbers below are MEASURED@this session's disk read of
`data/cskg_foundation_v1/edges_shard_*.jsonl`, NOT from the Director's redirect message alone --
independently re-verified)
Each raw edge record already carries a `source` field (`{'subject':..., 'relation':..., 'obj':...,
'source': 'VG', 'trust':..., 'subj_core':..., 'obj_core':...}`), confirmed by direct read of
`edges_shard_00.jsonl`. Full distribution across all 16 shards (1,213,912 edges total):
```
AT     696152  0.5735      (ATOMIC; matches Director-cited AT dominance)
VG     257130  0.2118      (VisualGenome; "mostly spatial not causal" per drill note)
CN     214890  0.1770      (ConceptNet)
WD      13812  0.0114      (Wikidata)
FN      12128  0.0100      (FrameNet)
WN      11903  0.0098      (WordNet)
CN|WN    7897  0.0065      (mixed-provenance tag)
```
`K = 7` shards (source_to_idx built via `sorted(set(...))` over observed source strings, PROT-023
compliant). **Honest severity note not in the redirect message, surfaced here:** the distribution is
extremely skewed -- AT alone (696,152 edges) is 23x Stage-2B's own measured HARD_FAIL point (30,000) and
would need EITHER a very large sparse-code expansion OR further sub-partitioning to plausibly clear the
Willshaw-class capacity ballpark; this cell measures (does not assume) whether `ARM_SHARDED_SPARSE`'s
single stacked expansion is sufficient, and reports the AT-shard-specific sub-result even if the overall
weighted recall is lower, so a MIDDLE_BAND ("shard-count alone insufficient AT full skew, sparse coding
delays but does not fully rescue the largest family") is a legitimate, informative, EXPECTED-possible
outcome, not something engineered away.

**Relation-purity check (this session, not in the redirect message):** 23/33 relations map to a SINGLE
source with 100% purity (all `at:*` relations are pure AT; `mw:MayHaveProperty` is pure VG; etc); 10/33
are provenance-mixed (e.g. `/r/LocatedNear` is 99.97% VG / 0.03% CN; `/r/PartOf` splits across
CN/WD/WN/CN|WN). Consequence for routing (declared before running, not decided post-hoc): a REAL
`(s,p,o)` triple carries its own true `source` tag (used directly for POSITIVE/relevant-query routing --
honest, since `source` is a property of the specific fact being recalled, not the answer itself). A
NEGATIVE query `(s,p)` has no real edge and therefore no true source; it is routed via a
`relation_to_majority_shard[p]` lookup table built empirically from THAT SCALE's own ingested
`(relation, source)` co-occurrence counts (argmax shard per relation) -- a disclosed, principled proxy
("route by the relation's dominant provenance when the specific fact's truth is unknown"), not an oracle
that peeks at whether the negative fact exists.

## Reuse contract (imports, not re-transcription)
- `hdlab.kg_traversal.KGStore` -- entity/relation codebook generation (`_bipolar`), FLAT arm's own W.
- `experiments.exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1`: `load_entity_vocab`, `CSKG_DIR`,
  `eval_gate` (FLAT arm's exact evaluator, unmodified), `precheck_kgstore_and_loader`,
  `QUERY_SEED`/`DATA_SEED`/`SHORTLIST_K`/`N_QUERY`/`GATE_THRESH`/`SCALES_FULL` (all reused unmodified for
  bit-identical FLAT reproduction).
- `experiments.exp_focus_pullin_causal_stage2a_multihop_loop_v1.pull_in_multi_exclude` -- DENSE arm's
  final CA3-settle + admission gate (identical call convention to Stage-2B).
- `experiments.exp_focus_pullin_causal_stage15_salted_cardinality_gate_v1.refuse_gate_calibrate_from_
  scores` -- the SPARSE/SCRAMBLED arms' DG-space tau calibration (50/50 internal split; identical PORT
  of `KGStore.refuse_gate_calibrate`'s algorithm Stage-1.5 already validated).
- `hdlab.cleanup_family.iterative_attractor` (aliased `_iterative_attractor`) -- CA3 attractor completion,
  used for BOTH the dense-space (1024-dim) and DG-space (2048-dim) shortlist settle steps; the primitive
  is representation-agnostic (cosine-based relaxation over whatever vectors it is given), matching how
  Stage-1/1.5/2A/2B already use it.
- `hdlab.hippocampal_encoder.DGProjection` -- the Q1-fix sparse expand-then-sparsify encoder, used
  UNCHANGED for both the key-space and value/entity-space sparse projections (two separately-seeded
  instances, since they encode logically different roles even though the input dim is the same 1024).
- `tools.exp_checkpoint`: `unit_key`/`completed_units`/`record_unit`/`load_units` -- per-scale resumable
  checkpointing (MANDATORY per CLAUDE.md multi-unit rule).
**New code in this cell (disclosed, not hidden as "reuse"):** `load_spine_edges_with_source` (re-reads
the same 16 `edges_shard_*.jsonl` files as Stage-2B's own `load_spine_edges`, identical entity/relation
resolution logic, ADDS the `source` column Stage-2B's loader does not capture -- necessary, not a
mechanism change); `DenseShardStore` (K separate `[1024,1024]` dense W's, same bind/accumulate/score math
as `KGStore` generalized from 1-store to K-stores); `SparseHeteroShardStore` (K separate `[dg_dim,dg_dim]`
DG-coded hetero-associative Hebbian stores, generalizing `CA3AutoAssociator`'s auto-associative
sparse-outer-product-write PATTERN to hetero-associative key->value binding -- same Willshaw math, two
different sparse codes instead of one, disclosed generalization not a new primitive).

## Design: 4 arms, same 6 cardinality rungs as Stage-2B where compute allows
`SCALES_FULL = [1000, 5000, 10000, 30000, 100000, 1213912]` (imported from Stage-2B, unchanged).
Compute-proportionality reduction (disclosed): `ARM_FLAT` and `ARM_SHARDED_DENSE` run at all 6 rungs
(cheap, ~100ms/query same order as Stage-2B's own measured cost). `ARM_SHARDED_SPARSE` and
`CONTROL_SCRAMBLED_SHARD_KEY` run at `SPARSE_SCALES = [10000, 100000, 1213912]` only -- this still covers
BOTH scale points the task contract's HARD-PASS/HARD-FAIL bands require (100,000 and 1,213,912), plus one
below/near-cliff sanity point (10,000); the 2 skipped small rungs (1000, 5000) are uninformative for the
SPARSE/SCRAMBLED comparison (FLAT and DENSE already both work fine there) and skipping them saves a
large fraction of the DG-projection + Hebbian-accumulate compute (dominated by the largest rung
regardless). `ARM_FLAT` additionally gets a bit-identical-reproduction SPOT-CHECK (fresh re-run, not
citation) at `FLAT_REPRO_CHECKPOINTS = [1000, 1213912]` (smallest + largest = maximum diagnostic value
per META_RULE_AC/§15-F "do not trust cert docstrings/prior JSON without an empirical rerun in the CURRENT
code state" discipline) against `data/exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1/metrics.json`'s
landed numbers; the other 4 rungs are CITED directly (same deterministic code+data+seed, tagged
`MEASURED@stage2b_landed` not re-derived, per compute-proportionality).

**ARM_FLAT** (baseline, must reproduce the known collapse): Stage-2B's unmodified single-`W` `KGStore` +
`eval_gate`, same `QUERY_SEED`/`DATA_SEED`/`GATE_THRESH=0.28`/`SHORTLIST_K=50`/`N_QUERY=150`.

**ARM_SHARDED_DENSE** (shard-routing lever ONLY, entities stay dense bipolar): `DenseShardStore` with
`K=7` shards keyed by `source`. Ingest: each triple's Hebbian outer-product write goes into
`W_shards[source_idx(triple)]` only (write-side fix, the redirect's load-bearing correction over my
original read-side-only design). Query: relevant queries route via the sampled triple's own true
`source`; negative queries route via `relation_to_majority_shard[p]`. Final admission: SAME
`pull_in_multi_exclude(probe=W_shard@key, shortlist_codebook=E[shortlist], gate=0.28)` as Stage-2B/FLAT
-- ONE variable changed (which `W` a query's key is multiplied against), everything else (codebook,
gate threshold, shortlist size, settle primitive) held fixed for a clean ablation.

**ARM_SHARDED_SPARSE** (shard-routing AND within-shard DG/CA3 sparse coding, the full recommended
architecture): SAME `K=7` shard routing (identical assignment to `ARM_SHARDED_DENSE`, so the routing
variable is held constant between these two arms and ONLY the within-shard representation/store differs).
`SparseHeteroShardStore`: `DG_DIM=2048` (`4x` bipolar's natural dim=512 packing headroom, `2x` KGStore's
`n_dim=1024` -- a resource-constrained choice, see Compute architecture; empirically checked in smoke, not
assumed), `sparsity=0.02` (matches `hdlab/hippocampal_encoder.py`'s own documented DG target ~1-3%, the
existing calibrated default, not re-tuned). Two `DGProjection` instances (`dg_key_proj`, `dg_val_proj`,
distinct seeds): `dg_val_proj` projects the ENTIRE entity codebook `E` (482,588 rows) ONCE at cell
startup into `DG_VAL_CODEBOOK` (fixed, reused across every scale/arm -- DG projection is entity-identity
-dependent only, not ingest-dependent); `dg_key_proj` projects EVERY shuffled triple's `(s,p)`-bound key
vector ONCE (`DG_KEY_CODES_ALL`, computed for the full 1,213,912-row shuffle, then each scale's rung takes
a PREFIX -- exploits the same nested-prefix structure Stage-2B's own scale sweep already relies on, no
redundant recomputation). Ingest: per-shard batched Hebbian accumulate `W_hetero[k] += (DG_VAL_CODEBOOK[o
_idx_in_shard_k].T @ DG_KEY_CODES_ALL[triple_idx_in_shard_k]) / normalizer` (same batched-matmul-per-group
pattern `KGStore.ingest_triples` and this cell's own `DenseShardStore.ingest` already use, generalized to
DG-space vectors). Query (coarse stage, BATCHED per shard for memory-bandwidth reasons -- see Compute
architecture): `probe_dg = W_hetero[shard] @ dg_key_code(query)`; `scores = DG_VAL_CODEBOOK @ probe_dg`;
top-`SHORTLIST_K=50` by DG-space score. Query (fine stage, per-query loop, cheap since shortlist is tiny):
`_iterative_attractor(probe_dg, DG_VAL_CODEBOOK[shortlist], ...)` settle, admission
`cos(probe_dg, DG_VAL_CODEBOOK[candidate]) >= tau_dg`. **`tau_dg` is A NEW, DG-space-native calibration**
(DG-space ternary-sparse cosines have different statistics than 1024-dim dense bipolar cosines, so
Stage-2B's `GATE_THRESH=0.28` does not transfer) -- calibrated via `refuse_gate_calibrate_from_scores`'s
own internal 50/50 split of the SAME 150+150 query draw (no extra queries; recall/false-pull-in are
measured on the held-out EVAL half only, `n=75` each after the split -- same convention Stage-1.5 already
validated for its own adaptive arm). `calibration_check_sparse: adaptive_with_discriminator_gate`.

**CONTROL_SCRAMBLED_SHARD_KEY** (mandatory pairscramble-must-collapse control): identical
`SparseHeteroShardStore` architecture to `ARM_SHARDED_SPARSE` (same `DG_DIM`, same batching, same
DG-space calibration procedure) -- the ONLY difference is the shard LABEL each triple is assigned. For
EACH scale rung independently, `scrambled_labels = rng.permutation(true_labels_for_this_prefix)` (a fresh
permutation of that EXACT prefix's true-label multiset, seeded `SCRAMBLE_SEED + scale`) -- this preserves
the EXACT per-scale shard-size histogram (same `K=7` shard sizes as the real-key arms at every rung, per
the redirect's explicit requirement) while destroying the correspondence between a triple's content
(subject/relation/object) and which physical store holds it. Negative-query routing uses the analogous
`relation_to_majority_shard` table built from the SCRAMBLED labels (expected near-uniform/noisy, since
scrambling is i.i.d. and independent of relation).

## Pre-registered bands (exp_dev-owned per the redirect message; declared here BEFORE running)
All REC/FP checks apply at BOTH `scale=100,000` AND `scale=1,213,912` (the two rungs Stage-2B's FLAT
arm measured `relevant_recall=0.000`) unless stated otherwise.

- **HARD-PASS** (ALL required):
  1. `baseline_repro_check.ok == True` (FLAT spot-check at [1000, 1213912] within `REPRO_TOLERANCE=0.05`
     absolute of Stage-2B's landed `relevant_recall`/`false_pull_in_rate`).
  2. `ARM_SHARDED_SPARSE.relevant_recall >= 0.50` AND `ARM_SHARDED_SPARSE.false_pull_in_rate <= 0.20`
     (Stage-2B's own per-point HARD_PASS bands, reused unmodified per the redirect).
  3. `ARM_SHARDED_SPARSE.relevant_recall - CONTROL_SCRAMBLED_SHARD_KEY.relevant_recall >= 0.30` absolute
     (the real-shard-key-matters discriminator; a matrix-splitting artifact would show up here too if the
     win were spurious).
  4. `ARM_SHARDED_DENSE.relevant_recall - ARM_FLAT.relevant_recall >= 0.20` absolute (the shard-count
     lever alone shows SOME independent recovery, even if below the sparse arm -- the two levers'
     contributions must be separately visible, not just the composed win).
  5. `arms_differ_verified == True` (META_RULE_AF hash-test across all 4 arms' per-probe traces at the
     full-scale rung) AND `cardinality_ok == True` (all expected per-scale units landed).
- **HARD-FAIL** (either triggers):
  1. `ARM_SHARDED_SPARSE.relevant_recall < 0.10` at BOTH `scale=100000` AND `scale=1213912` (the composed
     rescue does not work on REAL CSKG structure even though the mechanism class is certified on
     synthetic planted communities -- escalate to a different real shard key, e.g. `kcore` band, or accept
     a genuine engineering-hard capacity limit for this store shape).
  2. `CONTROL_SCRAMBLED_SHARD_KEY` performs statistically indistinguishably from `ARM_SHARDED_SPARSE`:
     operationalized as `ARM_SHARDED_SPARSE.relevant_recall - CONTROL_SCRAMBLED_SHARD_KEY.relevant_recall
     < 0.10` at BOTH top rungs (a matrix-splitting artifact, not a genuine shard-key effect -- falsifies
     the context-gating explanation specifically even if the composed arm shows some numeric lift).
  3. `baseline_repro_check.ok == False` (the comparison basis itself cannot be trusted).
- **MIDDLE_BAND**: everything else -- e.g. `ARM_SHARDED_DENSE` or `ARM_SHARDED_SPARSE` delays but does
  not fully hold the collapse; the AT-shard-specific sub-result (see "Shard key" honesty note above)
  remains substantially worse than the weighted-average result; or the DENSE-lever-alone requirement (4)
  is not met even though the composed SPARSE arm clears (2)+(3) (motivates reporting the two levers'
  contributions separately rather than only the headline number).

## Compute architecture
(b) sequential/batched-CPU with justification (NOT GPU-batched): `ARM_FLAT`/`ARM_SHARDED_DENSE` use a
per-query Python loop (Stage-2B's own proven pattern, ~100ms/query dominated by streaming the 482,588-row
`E` codebook through a `(n_ent,1024)@(1024,)` matvec -- memory-bandwidth-bound, ~1.98GB/query, matches
Stage-2B's measured ~30s/300-query cost). `ARM_SHARDED_SPARSE`/`CONTROL_SCRAMBLED_SHARD_KEY`'s coarse
DG-space scoring step is BATCHED PER SHARD (not per-query): the dominant cost is streaming
`DG_VAL_CODEBOOK` (`482,588 x 2048` float32, ~3.95GB) through a matmul, and a per-query loop would
re-stream that full codebook on every one of 300 queries (~150ms x 300 = 45s x per scale x per arm, adding
up quickly across 3 scales x 2 arms); grouping a scale's ~300 queries by their (7-way) shard assignment
and doing ONE `(B,2048)@(2048,482588)` matmul per shard amortizes the codebook stream to ONCE per shard
per scale (`~7x` fewer full-codebook streams than per-query) -- this is a throughput optimization, not a
new mechanism (identical Hebbian-recall-then-score math, just reordered to avoid redundant memory
traffic; the same class of optimization Stage-1.5's own `_null_probe_admission_flat` docstring documents
for the identical reason, "iterative_cleanup natively supports a (B,D) query batch against ONE (M,D)
codebook... at M=100,000 with 200 queries [codebook re-streaming] dominated wall time"). The FINAL
shortlist+settle step (`shortlist_k=50` rows) stays a cheap per-query loop (tiny relative to the coarse
pass). `DG_DIM=2048` was chosen as a resource-constrained compromise (memory: `K=7` x `[2048,2048]`
float32 W's = ~118MB total, `DG_VAL_CODEBOOK` = ~3.95GB, well within the measured 10GB available RAM
alongside `E`'s 1.84GB and the dense arms' negligible `[1024,1024]` W's; wall-time: the two ONE-TIME
`DGProjection.encode_batch` calls -- `482,588 x 1024 -> 2048` for entities and `1,213,912 x 1024 -> 2048`
for all shuffled triples' keys -- are `~1e12` and `~2.5e12` flop matmuls respectively, each expected
tens-of-seconds at realistic BLAS throughput; MEASURED at smoke/self-test time, not assumed) -- a larger
`DG_DIM` (e.g. 8192, closer to the hippocampal_encoder docstring's own example) would give more Willshaw-
class capacity headroom but was judged to exceed the foreground wall-time budget for this cell; this is a
DISCLOSED, not hidden, resource trade-off, and a HARD-FAIL/MIDDLE_BAND driven by insufficient `DG_DIM`
(rather than the mechanism class being wrong) is an honest, informative, and explicitly anticipated
possible outcome (see "Shard key" honesty note re: AT's 696,152-edge shard). `OMP_NUM_THREADS=8` (raised
from the project's common `=1` determinism default; this cell's tolerance-based comparisons (`0.05`
`REPRO_TOLERANCE`) do not require bit-exact floating-point summation order, and 16 CPU cores are
available -- MEASURED this session via `os.cpu_count()`). Storage strategy: SHARDED (per META_RULE
STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW -- this cell IS the sharded-vs-bundled discriminator arm).

## Cell-template mandates
- `arms_differ_verified`: True -- FLAT vs DENSE vs SPARSE vs SCRAMBLED per-probe outcome traces
  (SHA256-digest, META_RULE_AF) at the full-scale rung must pairwise differ.
- `final_metrics_atomicity`: `tmp_replace` (top-level) + per-scale-unit resumable checkpointing via
  `tools/exp_checkpoint.py` (`unit_key("scale", scale)`; a unit holds ALL arms' results for that scale,
  so a crash mid-sparse-computation loses at most that one scale's unit, not the whole run).
- `except SystemExit: raise` before `except Exception` (no bare `except:`/`except BaseException:`).
- `crlb_n/a`: empirical cardinality/shard-capacity diagnostic composing two DIFFERENT closed-form regimes
  (dense-Hopfield `~0.14N` for `ARM_SHARDED_DENSE`'s per-shard `W`; Willshaw `~N^2/(log N)^2` for
  `ARM_SHARDED_SPARSE`'s DG-coded `W_hetero`) whose REAL per-shard-family capacity is exactly the open
  empirical question this cell measures, not a single fixed noise floor to check against.
- `HP_SCOPE`: `{sharded_sparse: [relevant_recall, false_pull_in_rate, scramble_margin], sharded_dense:
  [dense_lift_over_flat], flat: [baseline_repro_check]}`.
- `cardinality_ok`: `EXPECTED_N_UNITS = len(SCALES_FULL) = 6` (a per-scale unit is expected for every
  rung; SPARSE/SCRAMBLED sub-results are present only for rungs in `SPARSE_SCALES`, declared per-unit).
- per-unit failure-class instrumentation (no bare except).
- `calibration_check`: FLAT/DENSE = `default_ok_for_this_regime` (`GATE_THRESH=0.28`, Stage-2B's own
  empirically-validated un-retuned threshold, held fixed so shard-routing is the ONE isolated variable
  for the DENSE-vs-FLAT comparison). SPARSE/SCRAMBLED = `adaptive_with_discriminator_gate` (DG-space
  `tau` via `refuse_gate_calibrate_from_scores`, per-scale, logged in metrics).
- `deterministic_seeding`: True -- all RNG via explicit `np.random.default_rng(<int>)` or
  `torch.Generator().manual_seed(<int>)`; scramble permutations seeded `SCRAMBLE_SEED + scale`; source/
  relation index maps via `sorted(set(...))`; no built-in `hash()`, no bare `list(set(...))` ordering.
- `cell_chunked`: False (single script; per-scale checkpointing per above).
- `start_marker_written`/`crash_diagnostic_present`/`heartbeat_present`: True.
- `progress_logging`: `print_flush_true` (declared; estimated `timeout_s` may exceed 1800s at `--full`
  given the DG-projection precompute + 4-arm sweep, so this is MANDATORY per §17, not just good practice).
- Real-code-path preflight (`self_test()`): constructs the REAL `KGStore` (tiny N=16, via
  `precheck_kgstore_and_loader`), the REAL `load_spine_edges_with_source` against a small real CSKG slice
  (no synthetic-only branch for the NEW source-carrying loader), a REAL tiny `DenseShardStore` (n_ent=32,
  n_shards=3) with known-triple recall verification, a REAL tiny `SparseHeteroShardStore` (dg_dim=256)
  with known-triple recall verification, and verifies SCRAMBLED routing degrades correctness at tiny
  scale (arms-differ, real code path, not a synthetic-only branch).

## ADDENDUM: memory-safety correction caught in smoke (disclosed, fixed before --full)
The first smoke run (elapsed_s=696) precomputed DG-key-codes for the FULL 1,213,912-row shuffled triple
list regardless of run_mode (a `[1213912, DG_DIM=2048]` float32 array, ~9.9GB) -- wasteful for `--smoke`
(only needs up to 100,000 rows) and, more seriously, would have combined with `DG_VAL_CODEBOOK` (~3.95GB)
and `E` (~1.84GB) to exceed the measured ~10GB available RAM at the `--full` run's largest (1,213,912)
scale unit, a near-certain OOM that the smoke run's smaller scales did not expose. **Fix**: DG key-codes
are now projected ON THE FLY, in bounded chunks (`SparseHeteroShardStore.ingest_from_triples`, default
`chunk_size=100000`) during ingest, and per-query (only `n_query` rows at a time) during eval
(`eval_gate_sparse_shard`) -- `DG_VAL_CODEBOOK` remains the only large array held persistently (it is
entity-identity-dependent only, fixed size, unavoidable). Re-ran smoke after the fix: IDENTICAL numeric
results (same recall/false_pull_in/tau to full precision -- confirms the fix is memory-pattern-only, not
a behavior change), elapsed_s dropped 696 -> 261. `--full` then completed cleanly in a single foreground
invocation (elapsed_s=693.3, no OOM, no restart needed) -- the multi-call checkpoint-resume contingency
described below was not needed in practice.

## Dispatch
Local, foreground-to-completion (per Director's Ops instruction: "do NOT spawn nested sub-agents and do
NOT wait on background work"). Estimated `--full` wall time (~11-12 min, summed per-arm/per-scale
estimates in the completion report) may exceed one 10-minute Bash-tool foreground call; this cell's
mandatory per-scale-unit checkpointing (`tools/exp_checkpoint.py`) makes it safe to invoke `--full`
across TWO SEQUENTIAL foreground calls if needed (the second call resumes from checkpoint and completes
quickly) -- this is NOT backgrounding (no call returns before its own work is either done or safely
checkpointed) and is disclosed here rather than silently split. `--self-test` and `--smoke` are expected
to complete in well under 2 minutes each (tiny/reduced scale).
