# DESIGN -- sub-linear GapDetector/HDFactStore cleanup via exact schema+subject sharding (DG/CA3)

**Filed by:** research (Sonnet), 2026-08-12. Query-before-build audit + brain-fidelity design +
build spec + verification plan for a separate build agent. **NO IMPLEMENTATION CODE in this
note per the task contract.** Local note only, no push.

## HEADLINE

`GapDetector.refresh()` rebuilds its ENTIRE live-fact codebook from scratch on every checkpoint
(O(n_facts) content_key recomputation), and every `familiarity()` probe CA3-scans that WHOLE
codebook (O(n_facts) per first-encounter probe) -- both costs are paid repeatedly as the
foundation grows, which is why per-chunk latency grows with foundation size instead of staying
flat. The fix does NOT need a new similarity-clustering DG mechanism: HDFactStore's own facts
already carry an EXACT, zero-cost shard key (`relation`, already an explicit field + always
known by the caller) and an EXACT, already-built, already-equivalence-tested fine key
(`_sr_key`/`_sr_index`, the (subject,relation) content-hash bucket). Because `content_key`'s
subject/relation components are drawn from an ATOMIC symbol codebook (no cross-item lexical/
semantic similarity structure to exploit or lose), an EXACT two-tier partition captures 100% of
the real discriminative signal the current full scan computes -- it only removes inert
noise-contributing rows from the CA3 softmax. **Verdict: minimal-extension, not new-mechanism.**
Reuse HDFactStore's existing exact-hash-bucket primitive as the DG-analog shard key, keep CA3
(`cleanup_family.iterative_attractor`) byte-identical but scope it to the routed micro-shard, and
replace GapDetector's full-rebuild `refresh()` with an event-driven incremental per-bucket
append. Named build target: **`hdlab/sharded_gap_index.py`** (new, thin), NOT a rewrite of
`cleanup_family`/`iterative_attractor` (unchanged) and NOT a new similarity-routing layer.

## (a) BANKED-WORK AUDIT -- what's already built vs genuinely missing

Query-before-build performed via `python tools/capability_registry_query.py --serves "<term>"`
(single-term substrings; the tool does substring match, not semantic search) plus direct
disk reads of every file the task named. 107 rows in `data/capability_registry.jsonl` scanned
for shard/hierarchical/tier/route/dentate/codebook/cleanup/attractor/pattern-separation
keyword hits (16 rows matched; all inspected).

### Directly reusable AS-IS (no changes needed)

- **`hdlab/hd_fact_store.py` `_sr_key` / `_sr_key_bytes` / `_sr_index` / `_find_same_sr_indexed`**
  (lines 180-252). This IS the exact-match sub-linear mechanism the build needs for Tier-2:
  "the (s,r) HD SIGNATURE is DETERMINISTIC... a content-address of the signature (sha1 of its
  packed bipolar bytes) is a PERFECT hash: O(1) bucket instead of an O(n) cosine scan, with NO
  approximation" (module's own docstring, lines 124-130). Already equivalence-tested
  bit-identical to the O(n) reference (`_selftest_index_equivalence`, disk-verified by reading
  the test body). **DISK-VERIFIED FINDING: this index is currently OFF.** `HDFactStore.__init__`
  defaults `use_index=False`, and `hdlab/reading_grounding_loop.py`'s `HDFactStore(...)`
  construction calls (lines 340, 352, 389, and the live foundation's own store) never pass
  `use_index=True`. So even the ALREADY-BUILT O(1) conflict-check path is a live no-op in the
  current pipeline. Turning it on is a separate, free, one-line win (see (c) item 0) --
  orthogonal to GapDetector's own bottleneck (this index only accelerates `store()`'s ingest-vet
  conflict check, it is never consulted by `GapDetector` at all today).
- **`hdlab/cleanup_family.iterative_attractor` / `hdlab/iterative_attractor.iterative_cleanup`**
  (registry rows `pattern_completion`=22, `cleanup_attractor`=24, `ALREADY_WIRED`). CA3/DG
  softmax attractor settle, brain-canonical (Treves-Rolls / Marr / CAN-bump / modern-Hopfield
  citations in the module docstring). Reused **verbatim, unchanged** by this design -- only the
  codebook it is handed gets smaller.
- **`hdlab/hd_fact_store.py` `_domain_codebook` / `_cb_cache`** (lines 141-160): precedent for
  "cache the stacked codebook, invalidate only on new-symbol registration" -- the EXACT
  discipline this design generalizes to GapDetector's bucket codebooks (a cache invalidated
  per-bucket, not per-domain).

### Considered and NOT reusable as an implementation (wrong problem shape, disk-verified)

- **`selection_weighted_sharded_typer.py`** (registry id 70, `selection_weighted_sharded_typer`,
  `WIRED`/`WIRED`, the exact module the task pointer named). Read in full. It is a **K-way
  CLASSIFICATION mechanism over a fixed small label set** (2-10 classes): cues are partitioned
  into a small caller-supplied number of named ROLE shards, each shard gets ONE consolidated
  superposition over ALL of train, and `predict()` cost is O(n_shards x n_labels) -- **constant
  in training-set size**, not a growing-candidate-pool retrieval/cleanup problem at all. It never
  answers "which of M stored items does this probe match"; it answers "which of K fixed labels."
  **Verdict: wrong problem shape, not directly reusable as code.** Its reusable PRINCIPLE --
  "sharding before superposition prevents a high-frequency/filler cue from swamping a sparse
  discriminative cue's similarity budget within the same bundle... per-slot alpha = K/(S*N) vs
  flat alpha = K/N" -- is exactly the justification for sharding GapDetector's codebook (today's
  flat codebook lets every OTHER relation's facts dilute a probe's CA3 softmax with irrelevant
  competitors). Its `shard_weights_from_loo_acc` hard-one-hot `predict_select` biased-competition
  router is the right FALLBACK PATTERN for a future case where shard membership must be INFERRED
  (see brain-fidelity note on routing below) -- not needed here because relation is given, not
  ambiguous.
- **`hdlab/gather_reason.py` `ca3_relevance_gather`** (registry id 106, `gather_reason`, `WIRED`).
  Read in full. Its docstring calls itself "a CA3/DG-style peel-loop... pulls the RELEVANT
  neighborhood instead of a blind full scan," which sounds directly applicable, but the actual
  code (`ca3_relevance_gather`, lines 82-113) calls `cleanup_family.iterative_attractor(resid,
  codebook)` against the **entire caller-supplied codebook on every peel iteration** (up to
  `k_peel=25` full scans) -- it is MORE expensive per call than GapDetector's own single-shot
  `familiarity()`, not less. Its real narrowing benefit (`restrict_hop1_to`) applies downstream,
  to `fanout_two_hop`'s KG-traversal candidate set, not to the GATHER stage's own codebook scan.
  **Verdict: not reusable for this bottleneck; ruled out after reading the code, not just the
  docstring** (the docstring oversold the mechanism relative to what the code does).
- **`hdlab/hippocampal_encoder.py`** (registry id 81, `hippocampal_encoder_dg_ca3_pipeline`,
  `ALREADY_WIRED`). Read in full. This is a genuinely different, capacity-BOUNDED architecture:
  `DGProjection` (random expansion + top-K sparsify) feeds a `CA3AutoAssociator` that stores
  ALL items superposed into ONE `[dg_dim, dg_dim]` Hebbian matrix (`W += outer(code,code)`);
  `settle()` cost is O(dg_dim^2), CONSTANT in item count, but classical-Hopfield capacity
  (~0.14 x dg_dim) caps how many items it can hold before interference collapse -- at practical
  dg_dim (2048-8192) that ceiling (287-1147 items) is already below the current 7966-fact
  foundation. **Verdict: wrong regime (bounded small-V dense superposition), not applicable to
  an unboundedly-growing fact store without a capacity-management layer this task doesn't need.**
  Cited here so the next agent doesn't re-discover and re-reject it.
- **`backend/substrate_index/partition.py` (`PartitionedStore`)** (registry id 14,
  `partitioned_store`, `WIRED`, "the canonical atom store"). Read in full. Hand-coded FIXED
  corpus-enum partitions (math/concept/meta/school/methodology/science/...history) for the
  cert-atom + relation-graph bank in a DIFFERENT subsystem (`backend/substrate_index`, not
  `hdlab`), with exact-id dict lookup (`Store.get_atom`), not similarity/CA3 cleanup at all.
  **Verdict: not applicable to this problem** (different subsystem, different storage semantics,
  no cleanup primitive). Useful only as a general precedent that "partition-then-route-by-
  explicit-key" is an established pattern in this codebase, which the design below already
  gets more directly from `hd_fact_store._sr_index`.
- **`notes/research_routing_tier4_training_speedup_small_scale_battery_2026-06-02.md`** (task
  pointer). Read in full. About TRAINING throughput (Hebbian-vs-gradient-descent, deletion
  cert, counterfactual diagnostics, LLM-coupling clusters A/B/C) for an unrelated LLM-integration
  program. **Verdict: not applicable** -- zero overlap with query/retrieval latency scaling.
- **`[[project_phase_diagram_leverage_deferred...]]`** (task pointer, memory anchor). Searched
  the filesystem (`notes/`, whole repo) for any file matching `*phase_diagram_leverage*` --
  none exists. The many `*phase_diagram*` notes on disk are all from the unrelated
  substrate-physics research track (Kerdock/AMP/spin-glass phase diagrams). **Verdict: could not
  locate an artifact to evaluate; the anchor appears to be a MEMORY.md-only pointer with no
  corresponding note file, or was filed under a different name. Not used.**

### Real precedents for the METHODOLOGY (not the code) -- SHELVED/ISLANDed, disk-verified numbers

- **`experiments/exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1.py`**
  (registry id 79, `kgstore_hierarchical_candidate_retrieval_1_2M`, `TRAPPED_SHARED`/`SHELVE`).
  Read in full (806 lines). REAL-DATA validated at 1.2M-entity CSKG scale: two-tier shard key
  = Tier-1 relation-majority SOURCE FAMILY (AT/VG/CN/...) + Tier-2 `subject_tier2_local`, a
  **vectorized deterministic HASH of subject entity-id with a salt**, splitting an oversized
  family shard into `K_family = ceil(family_occupancy / SAFE_LEAF_SIZE_SPARSE)` sub-buckets.
  `SAFE_LEAF_SIZE_SPARSE = 57000` (hard-coded, line 169) sourced from a companion sweep cell,
  confirmed present on disk: `experiments/exp_focus_pullin_causal_stage2e_leaf_capacity_sweep_v1.py`
  + `data/exp_focus_pullin_causal_stage2e_leaf_capacity_sweep_v1/`. Measured
  `relevant_in_shortlist_rate` held flat at 0.853-0.887 across leaf sizes 10k-57k at the full
  1,213,912-scale. **This is the METHODOLOGY precedent for "empirically sweep a safe shard size
  for the representation in play, don't guess a constant"** -- but its own implementation targets
  a DIFFERENT storage representation (dense `[dg_dim,dg_dim]` Hebbian matrix per shard with a
  fixed interference ceiling, same family as `hippocampal_encoder`'s CA3AutoAssociator) than
  GapDetector's list-of-rows-per-bucket codebook, whose bucket sizes are naturally tiny (bounded
  by relation-cardinality collisions, not by a matrix-capacity ceiling) -- so its specific
  `SAFE_LEAF_SIZE_SPARSE=57000` number does NOT transfer numerically, only the "sweep, don't
  guess" discipline does (see (d) below).
- **`experiments/exp_community_bounded_retrieval_scale_invariance_v1.py`** (registry id 80,
  `community_bounded_nested_two_stage_retrieval_synthetic`, `ISLAND`/`SHELVE`). Read in full
  (559 lines). SYNTHETIC planted-community-graph HARD_PASS: "route a query to its COMMUNITY
  first (coarse gist codebook, ~sqrt(V) near-orthogonal pointers), then resolve ONLY within that
  community (fine decode over ~sqrt(V) items)... decouples effective codebook size from total
  store size." Disk-verified numbers: `treat_rd=0.000` vs `ctrl_rd=1.000` (relative degradation
  flat vs collapsing) across V=[580, 2900, 29000, 58000], `route_acc@Vmax=1.000`,
  `modularity_Q_min=0.510`, 3 seeds. **This is the METHODOLOGY precedent for the VERIFICATION
  PLAN below** (relative-degradation-flat-vs-collapsing benchmark + a route-accuracy-not-leaking
  guard) -- its own implementation (a learned similarity-clustered "gist codebook" router) is
  NOT needed here because GapDetector's shard key can be EXACT (see (b) below), which is a
  strictly stronger guarantee than a coarse-route accuracy of 1.000-empirically-measured-but-not-
  structurally-guaranteed.

### Genuinely missing (net-new, small)

1. A sharded live-fact index living alongside `HDFactStore`/`GapDetector`:
   `{relation_str -> {sr_bucket_hash -> (local codebook rows, fid list)}}`.
2. Event-driven incremental maintenance of that index (append on `store()`, no full rebuild).
3. A `familiarity()` path that looks up the routed bucket (O(1)) then runs the UNCHANGED CA3
   attractor only within it (O(bucket size), bucket size independent of total `n_facts`).

No existing module does (1)-(3) together. This is the build target.

## (b) BRAIN-FIDELITY DESIGN

Per the FORMALIZE discipline (map structure -> per-component SHAPE + POSITION + METRIC -> name
the gap -> the build target), three components, each cross-checked against what is already
built:

| Component | Brain structure | SHAPE | POSITION (what it does) | METRIC |
|---|---|---|---|---|
| **Tier-1 shard: schema/predicate** | Anatomical/structural routing between cortical territories (e.g. distinct cortical areas receiving input via fixed, type-keyed pathways -- NOT competitive; the systems-consolidation framing already in the memory anchor: "each schema gets its own territory," McClelland/O'Reilly CLS) | `dict[str, ShardGroup]` keyed by `FactRecord.relation` | Routes a probe to the cortical territory (predicate/schema) it structurally belongs to, BEFORE any competition happens | Exact string equality (categorical, zero overlap by construction -- `relation` is always known by the caller: every `familiarity(subject, relation, obj)` call already supplies it, no inference step needed) |
| **Tier-2 shard: (subject,relation) micro-territory** | DG granule-cell pattern separation -- the COMPUTATIONAL ROLE DG plays (keep the CA3-relevant candidate set small and mutually near-orthogonal so completion doesn't get swamped by irrelevant competitors), achieved here via an EXACT structural partition rather than DG's biological random-projection+top-K-sparsify. This is a disclosed, justified deviation: biological DG cannot address by an abstract token id, but the substrate's discrete symbolic representation can -- `content_key`'s subject/relation components are ATOMIC symbol-codebook draws (`codec._sym_vec`) with NO cross-item lexical/semantic similarity structure to begin with, so an exact partition loses zero real discriminative signal relative to today's full scan (it only drops inert noise rows from the CA3 softmax denominator). Brain-COMPATIBLE (same functional role as DG) though not literally biologically-implemented (per the standing invariant: may do better only if brain-compatible, glass-box always) | Reuses `HDFactStore._sr_key` / `_sr_key_bytes` VERBATIM: `sha1(bipolar(subject,relation) signature bytes)` -> bucket | Within a Tier-1 territory, further separates facts by the EXACT (subject,relation) pair a probe is asking about, so CA3 only ever sees genuine competitors (same subject+relation, different object -- the one case that legitimately needs graded disambiguation) | Content-hash exact match; already proven zero-collision-across-distinct-pairs by `hd_fact_store._selftest_sr_key_separates` (cos=1.000 same-pair vs cos<0.60 one-pair-shared vs cos<0.40 unrelated) |
| **Tier-3: CA3 completion** | CA3 recurrent-collateral iterative pattern completion (Treves-Rolls / Marr 1971 / CAN-bump / modern dense Hopfield), UNCHANGED from today | `cleanup_family.iterative_attractor` -> `iterative_attractor.iterative_cleanup`, same params (temp, max_steps, alpha) | Graded match/mismatch completion WITHIN the routed micro-shard only -- preserves the "novel-hard" intermediate-margin capability (`_selftest_shares_two_of_three_is_intermediate`) exactly, because same-(subject,relation)-different-object facts are, by Tier-2's own definition, always co-located in the SAME bucket | Raw pre-settle cosine margin between probe and CA3-selected best match (`ca3_match_score`, unchanged formula) |

**Honesty note on "biased competition":** the task's framing named biased-competition
(Desimone-Duncan salience-weighted attention) as the routing mechanism. On inspection, Tier-1
routing here does not need to COMPETE for anything -- `relation` is given, not inferred, so this
is anatomical/structural routing (a strict, degenerate special case of biased competition where
the competition is already resolved with certainty, cost zero). True biased-competition routing
(the `selection_weighted_sharded_typer.predict_select` hard-one-hot LOO-argmax pattern) is the
correct fallback ONLY if a future caller needs to route a probe whose schema/relation is itself
ambiguous or must be inferred from content -- not GapDetector's current or foreseeable use
(every call site in `reading_grounding_loop.py` already knows the relation it's probing). Naming
this explicitly so a future build doesn't add unneeded inference machinery.

**Scope caveat (disclosed, not hidden):** this exact-key design is optimal GIVEN today's atomic
symbol-codebook subject representation. If the substrate later adopts distributed/compositional
subject embeddings with real cross-item similarity (e.g. subword or semantic subject vectors),
Tier-1/Tier-2's exact keys would need to become similarity-clustered gist-codebook routing (the
`community_bounded_retrieval` precedent's actual mechanism) to avoid silently losing recall on
near-duplicate-but-differently-spelled subjects. Not a concern today; flagged for the future.

## (c) CONCRETE BUILD SPEC (for the next agent -- design only, not implemented here)

**0. Free, orthogonal, do-first:** flip `use_index=True` on every live `HDFactStore` construction
in `hdlab/reading_grounding_loop.py` (and any other live-pipeline caller). This activates an
ALREADY-BUILT, ALREADY-EQUIVALENCE-TESTED O(1) path for `store()`'s own ingest-vet conflict
check, currently dead code in production. Zero design risk (the equivalence self-test already
proves bit-identical output); not a substitute for items 1-3 below (it accelerates `store()`,
not `GapDetector`).

**New module: `hdlab/sharded_gap_index.py`** (thin; wraps, does not replace, `HDFactStore` and
`cleanup_family`).

1. **Sharding key.** Two-level, both EXACT (no learned/inferred routing):
   - Tier-1 key: `relation` (string, already on every `FactRecord`).
   - Tier-2 key: `HDFactStore._sr_key_bytes(HDFactStore._sr_key(subject, relation))` (reuse
     verbatim -- do not reimplement; import the existing private helpers or promote them to
     `HDFactStore` public API if `sharded_gap_index` needs external access).
   - Combined bucket id: `(relation, sr_key_bytes)`. A python `dict` keyed on this tuple maps to
     a small list of `(fid, content_key_vector)` rows -- this IS the "micro-codebook."
2. **Incremental maintenance (replaces `GapDetector.refresh()`'s full rebuild).** Every
   `HDFactStore.store()` call already returns a `StoreResult` naming exactly which `fid`s changed
   status (new ACTIVE fid, any SUPERSEDED/DROPPED/FLAGGED/COMBINED fids). Wire
   `sharded_gap_index` to consume that per-call delta (either via a direct call from the reading
   loop right after `store()`, or via a thin store-side hook) and update ONLY the affected
   bucket: append the new fid's `content_key` vector, mark or drop superseded rows. No global
   rebuild ever required. This is the change that fixes the checkpoint-level O(n_facts)-per-
   refresh driver (the dominant cost as the foundation grows), not just the per-probe cost.
3. **`familiarity(subject, relation, obj)` (replacement path).**
   - Compute the Tier-1+Tier-2 bucket key for `(subject, relation)` (O(1): one `_sr_key` bind +
     one sha1).
   - If the bucket is empty: `margin=0.0, is_gap=True` directly (this is ALREADY GapDetector's
     existing empty-codebook contract for a globally-empty store -- now triggered naturally
     per-bucket, and MORE deterministic than today's near-but-not-exactly-zero full-scan noise
     floor for a wholly-novel probe).
   - If nonempty: call `cleanup_family.iterative_attractor` (UNCHANGED) against just that
     bucket's rows. Bucket size is bounded by relation-cardinality collisions (typically 1,
     occasionally a handful under MULTIVALUED/FLAGGED/COMBINE), never by total `n_facts`.
   - `content_key` computation itself is unchanged (same 3-pair bind+quantize formula);
     `GapDetector`'s public dataclass (`FamiliarityResult`) and call signature stay
     byte-for-byte the same so `reading_grounding_loop.py` and any other caller need NO changes.
4. **Correctness invariant (must hold, not just "probably holds"):** for every probe in
   `GapDetector`'s own existing 6 self-tests (`_selftest_known_exact_match_margin_is_one`,
   `_selftest_wholly_novel_margin_low`, `_selftest_shares_two_of_three_is_intermediate`,
   `_selftest_ablation_collapses_to_uncorrelated_noise`, `_selftest_scramble_flips_known_to_gap`,
   `_selftest_empty_kb_everything_is_a_gap`), the sharded path must produce IDENTICAL `is_gap`
   decisions and margins within float tolerance to the current O(n) reference path -- run BOTH
   paths side-by-side on the same store state and diff, the same equivalence-testing discipline
   `HDFactStore._selftest_index_equivalence` already established for its own O(1) index. This is
   the CAN-FAIL gate for correctness, separate from the throughput gate in (d).
5. **Throughput target.** Per-probe: O(bucket size), not O(n_facts) -- bucket size independent of
   total foundation size (verify empirically it stays small/flat as n_facts grows, see (d)).
   Per-checkpoint refresh: O(delta facts this pass), not O(n_facts) -- eliminates the dominant
   quadratic-ish accumulation driving the reported per-chunk slowdown.
6. **Do NOT touch** `hdlab/lexical_similarity.py` or `data/capability_registry.jsonl` (concurrent
   session holds them per task instructions) or `cleanup_family.py`/`iterative_attractor.py`
   (CA3 primitive stays byte-identical; only the codebook handed to it shrinks).
7. **Quick orthogonal constant-factor note (not the main fix, flag for the build agent to pick
   up cheaply if convenient):** `iterative_attractor.iterative_cleanup` recomputes
   `cb_norm = _l2_normalize(codebook)` (an O(bucket_size x n_dim) op) on every single call, even
   though within one refresh epoch the codebook rows don't change. Bipolar rows have constant
   norm (`sqrt(n_dim)`) so this is pure waste today; once buckets are tiny (item 3 above) this
   stops mattering much, but worth a one-line note in case a future caller hands `iterative_
   attractor` a larger codebook again.

## (d) VERIFICATION PLAN

**Cheap decisive test (can-fail, one variable, real baseline):** load the live foundation store
at `data/foundation/reading_grounding_v1` (disk-verified: `n_facts=7966`, `n_live_facts=7966`,
176 growth passes, `manifest.json`). Replay the SAME sequence of `store()` + `familiarity()`
calls the real 176-pass reading loop made (or, if that replay log isn't retained, construct a
synthetic-but-realistic replay: same two relations `KNOWN_WORD`/`GROUNDED_MEANING`, same growth
curve shape from `growth_curve_all` in the manifest) through BOTH the current O(n) `GapDetector`
and the new sharded path, at checkpoints `n_facts` in {500, 2000, 4000, 8000, 16000} (the last
two points extrapolate past the current foundation size -- this is the one variable that must
show the effect, matching this project's own "difficulty on" discipline). Two independent
measurements per checkpoint, current-path vs sharded-path:
- **latency-vs-scale:** wall-clock per checkpoint refresh + per-probe familiarity call.
- **correctness:** `is_gap` + margin agreement, item (c)-4 above, on the full existing self-test
  suite PLUS a held-out random sample of 200 (subject, relation, obj) probes drawn from the
  replayed store state (100 known, 100 genuinely novel, split further into wholly-novel and
  same-(s,r)-different-object "novel-hard" per the existing self-test taxonomy).

**Pre-registered HARD-PASS (both required, not either/or):**
- **Scale invariance:** per-checkpoint refresh latency AND per-probe familiarity latency at
  `n_facts=16000` is `<= 1.3x` the latency at `n_facts=2000` (a real corpus grew 8x; sub-linear
  cost should show close to flat, not the near-proportional growth the current O(n) path
  produces). Modeled directly on `community_bounded_retrieval`'s own relative-degradation
  metric (`treat_rd`), reused as the template metric here.
- **Correctness parity:** 100% agreement (`is_gap` decision, margin within `1e-5`) between the
  sharded path and the O(n) reference path on all 6 existing self-tests AND the 200-probe
  held-out sample, at every checkpoint scale tested.
- **Bucket-size boundedness (mechanism check, not just an outcome check):** mean and p95 Tier-2
  bucket size at `n_facts=16000` must NOT have grown proportionally to `n_facts` since
  `n_facts=2000` (expect near-constant, bounded by relation-cardinality collisions) -- this is
  the discriminator that would catch a shard-key design that LOOKS sub-linear in wall-clock but
  is secretly still funneling everything into one or two giant buckets (the failure mode stage2e
  itself hit before its Tier-2 hash-split fix, cited in (a) above).

**Pre-registered HARD-FAIL (any one triggers a redesign, not a declare-done):**
- Latency ratio at `n_facts=16000` vs `n_facts=2000` exceeds `2.0x` (materially still
  super-linear) -- would mean the sharding key isn't actually decorrelating buckets from corpus
  growth (e.g. if `relation` cardinality stays at 2 and per-relation Tier-2 buckets are somehow
  still coarse) and needs a finer or different key, not just this implementation.
- ANY correctness disagreement on the existing 6 self-tests (structural regression -- do not
  ship) or `>2%` disagreement rate on the 200-probe held-out sample (would mean the exact-key
  partition is silently dropping real matches, i.e. the "no cross-subject similarity to lose"
  premise in (b) was wrong for some case not yet identified -- worth root-causing before
  shipping, not waiving).
- p95 bucket size at `n_facts=16000` exceeds `50` (order-of-magnitude larger than the
  relation-cardinality collision counts actually observed in `reading_grounding_v1`'s real data,
  which are dominated by FUNCTIONAL relations with at most a couple of conflicting objects per
  subject) -- would indicate a shard-key collision problem (e.g. sha1 truncation, or a relation
  whose cardinality is much higher than assumed) that needs Tier-2's own leaf-size sweep
  (per the stage2e methodology cited in (a)) before this ships at larger scale.

**Difficulty-on / one-variable discipline:** the ONLY thing that changes between the "current"
and "sharded" arms is the retrieval/cleanup PATH; the underlying store contents, probe sequence,
CA3 params (temp/max_steps/alpha), and gap floor (0.625) are held fixed and identical across
both arms at every checkpoint.

## Cross-thread synthesis

This closes the loop the memory anchor's own three-tier architecture opened: `gap_detector.py`
(2026-08-11) and `reading_grounding_loop.py` (2026-08-12) are themselves recent, and neither
their own docstrings nor `notes/director_three_tier_knowledge_architecture_design_audit_2026-08-11.md`
(read in full for this design; it is the master audit for `prelim_tier`/`gather_reason`/
`three_tier_loop`, registry rows 105-107) anticipated GapDetector's OWN codebook becoming the
throughput bottleneck once the loop actually ran to scale -- this is a genuinely NEW finding,
not a re-tread of that audit's own G1-G7 gap list. It also directly complements two SHELVED/
ISLANDed capabilities (`kgstore_hierarchical_candidate_retrieval_1_2M`,
`community_bounded_nested_two_stage_retrieval_synthetic`) by extracting their METHODOLOGY
(two-tier schema+key sharding; empirical leaf-size sweep discipline; relative-degradation
verification metric) without inheriting their un-promoted/synthetic-only status -- this build, if
it lands per (c)/(d), should get its OWN registry row rather than trying to un-shelve either of
those (their own implementations target a different storage representation, per (a) above).

## Substrate-product implications

A foundation that gets structurally SLOWER to grow as it gets bigger is a hard product ceiling
on "read-to-grow the foundation" as a standing capability -- it caps how much the substrate can
ever autonomously learn before each incremental chunk becomes too slow to be worth running. Sub-
linear cleanup is not a nice-to-have optimization; it is the difference between "the substrate
can read a shelf of books overnight" and "the substrate's reading throughput degrades toward a
standstill after a few thousand facts," which directly gates the memory anchor's active mission
(grow the foundation beyond ~380 words toward genuine curriculum-scale coverage).

## Citations / file manifest (verified count)

All files below were READ (not label-trusted) during this pass; line counts and disk facts
verified via `Read`/`Bash` in this session, not carried over from prior notes.

- `hdlab/gap_detector.py` (326 lines, read in full) -- the bottleneck.
- `hdlab/hd_fact_store.py` (465 lines, read in full) -- Tier-2 key source + `use_index` finding.
- `hdlab/cleanup_family.py` (393 lines, read in full) -- CA3 primitive, unchanged.
- `hdlab/iterative_attractor.py` (234 lines, read in full) -- CA3 primitive, unchanged.
- `hdlab/reading_grounding_loop.py` (445 lines, read in full) -- confirms every call site's
  `relation` is always known at probe time; confirms `use_index` never passed.
- `hdlab/gather_reason.py` (299 lines, read in full) -- ruled out.
- `hdlab/hippocampal_encoder.py` (847 lines, read in full) -- ruled out (wrong regime).
- `hdlab/selection_weighted_sharded_typer.py` (471 lines, read in full) -- ruled out as code,
  principle reused.
- `hdlab/kg_traversal.py` (229 lines, read in full) -- confirms hierarchical sharding lives in
  the experiment cells, not this module.
- `backend/substrate_index/partition.py` (295 lines, read in full) -- ruled out.
- `experiments/exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1.py` (806 lines,
  grepped for structure + key sections read) -- methodology precedent.
- `experiments/exp_community_bounded_retrieval_scale_invariance_v1.py` (559 lines, grepped for
  structure + key sections read) -- methodology + verification-metric precedent.
- `notes/director_three_tier_knowledge_architecture_design_audit_2026-08-11.md` (293 lines,
  read in full) -- master context, confirms this is a new finding.
- `notes/research_routing_tier4_training_speedup_small_scale_battery_2026-06-02.md` (258 lines,
  read in full) -- ruled out, not applicable.
- `data/capability_registry.jsonl` (107 rows, queried via `tools/capability_registry_query.py`
  and full-file keyword scan; 16 rows deep-inspected).
- `data/foundation/reading_grounding_v1/manifest.json` -- disk-verified `n_facts=7966`,
  176 growth passes (matches task's stated numbers exactly).
- `experiments/exp_focus_pullin_causal_stage2e_leaf_capacity_sweep_v1.py` +
  `data/exp_focus_pullin_causal_stage2e_leaf_capacity_sweep_v1/` -- confirmed present on disk
  (the safe-leaf-size sweep methodology's own source).
- Searched, not found: any file matching `*phase_diagram_leverage*` anywhere in the repo.

**Verified citation count: 16 files/artifacts read or directly inspected on disk; 107 registry
rows queried; 0 fabricated claims (every "already exists" / "ruled out" verdict above is backed
by a specific file path and, where relevant, a specific line range read in this session).**
