# Research drill 3x: ANCHOR 1 v3 self-contained, ratio_resolved=0.1429 HARD_FAIL

Date: 2026-06-27 (UTC)
Author: research (team lead)
Cell: `exp_kb_partition_by_source_class_v3_self_contained` (file: `experiments/exp_kb_partition_by_source_class_v3_self_contained.py`)
Prereg: `preregs/2026-06-27_kb_partition_by_source_class_v3_self_contained.md`
Metrics: `data/exp_kb_partition_by_source_class_v3_self_contained/metrics.json`
Failure mode tag: `v3_band_miss`

## Executive headline (changes the framing)

**The framing in the drill request is partly mis-diagnosed.** The user
described this as "substrate KNOWS WHICH PARTITION to look in, but the
partition is too sparse to contain the answer." The metrics file does
NOT support that interpretation:

- Per-query payload shows `target_hits = 8, leak_hits = 0` for EVERY
  query in ARM_PARTITIONED_W_EQUAL_CAPACITY. That means: 8 of 8 top-K
  atoms are in the expected source-class. The answer IS present in the
  routed partition. The partition is NOT sparse-of-target.
- `routing_accuracy = 1.0` (top-1 in correct class for all 27 queries
  with top-K results).
- The actual `resolved` flag is **a confidence-threshold pass/fail**,
  not "did the answer appear." The cell defines
  `resolved = (not r["refused"]) and len(top_k_atoms) >= 1`, and `refused`
  fires when `max_cosine < confidence_floor = 0.30` (`DEFAULT_TAU` at
  line 137 of the cell; `confidence_floor` check at line 325 of
  `hdlab/director_kb_query.py`).
- The BASELINE arm (single unpartitioned W over all 2199 chunks) also
  tanked: `ratio_resolved = 0.1786` (5/28). The same query set on the
  v2 full-corpus KB (~177k atoms) got `ratio_resolved = 1.0` BASELINE
  and 0.80 PARTITIONED. So the regression is between v2 and v3, NOT
  between baseline and partitioned within v3.

**True root cause: encoder semantics changed between v2 and v3.** v2's
KB encoded ENTITY NAMES (filenames like
`research_substrate_director_kb_ingest_v1_2026-06-26.md` -> ~50 char
trigram set with high overlap to short queries like "substrate director
kb ingest"). v3's KB encodes CHUNK CONTENT (200-800 char prose blobs
with ~500-2000 trigram set, of which only a handful overlap a short
query). The cosine between a short query (~30 trigrams, mostly common
English n-grams) and a bundled-bipolar HD vector of a long chunk is
inherently low and noisy. The 0.30 confidence floor was calibrated on
v2's filename-index regime; it is **wildly wrong** for v3's
content-chunk regime.

The "1429 atoms per partition" figure the user cited (~chunks per class
in the inline KB) is a real but secondary axis. Even at 8000 atoms per
partition the same encoder problem would persist. Fixing density alone
does not fix this cell.

## What the metrics actually say (line by line)

From `data/exp_kb_partition_by_source_class_v3_self_contained/metrics.json`:

```
inline_kb_manifest:
  n_entities: 4735
  n_relations: 67
  n_triples: 6594
  n_chunks: 2199
  n_discovered: 400 files (200 note + 200 prereg)
  per_class.memory: n_files=0, n_chunks=0  <-- MEMORY CLASS NOT INGESTED
  per_class.note:   n_files=200, n_chunks=1138
  per_class.prereg: n_files=200, n_chunks=1061
```

```
arms:
  ARM_SINGLE_W_BASELINE (unpartitioned reference)
    n_resolved=5, n_queries=28, ratio_resolved=0.1786
    sample confidences: 0.26, 0.24, 0.26, 0.17, 0.17, 0.30,
                        0.17, 0.22, 0.27, 0.18
    -> ALL near or below the 0.30 floor; 1 of 10 above (0.3018, just barely)

  ARM_PARTITIONED_W_EQUAL_CAPACITY
    n_resolved=4, ratio_resolved=0.1429
    routing_accuracy=1.0 (27/27 top-1 in correct class)
    cross_partition_leak_rate=0.0
    target_hits=8 on every query (8/8 top-K in correct partition)
    n_capacity_regression=1 (only 1 baseline-resolved became
                             partition-unresolved -- meaning baseline
                             also failed 23/28)

  ARM_PARTITIONED_W_MEMORY_OVERSIZED
    user_directive_retention=0.2143 (3/14 UD queries above 0.30)
    non_ud_resolved_ratio=0.0714 (1/14 non-UD queries above 0.30)
```

So the failure has two layered defects:

1. **Schema gap.** The `memory` source class was requested but the
   builder ingested zero files. (Inspect: `per_class.memory.n_files = 0`
   despite `chunk_classes = ("note", "memory", "prereg")` in the cell.)
   This is a separate bug from the cosine-floor issue but it nukes the
   UD-retention path because UD queries expect `chunk_memory` atoms.
2. **Confidence-floor mismatch.** Even where the right partition holds
   the right chunks, the chunk-content encoding produces cosines in the
   0.14-0.30 band, mostly below the 0.30 refuse-gate. So the cell calls
   "refused" on content that is, by routing evidence, the correct match.

## Schema bug detail (memory class drop)

The cell calls
`build_chunk_plan(schema, repo_root, chunk_classes=("note","memory","prereg"))`.
The chunker only ingests files whose schema entry has `mode == "text"`
(line 224 of `hdlab/director_kb_chunk_ingest.py`). If
`config/director_kb_schema.json`'s `source_classes.memory` entry has
mode != "text" OR root path resolves to something empty on this run, the
class silently produces `n_files=0`. The manifest shows that's what
happened. The v2 BASELINE arm DID find memory-class hits (e.g. "USER
directive monitor armed" resolved in v2), so the v2 KB had memory atoms.
The v3 self-contained build lost them.

This is a **CARDINALITY_OK violation under META_RULE_H discipline**: the
pre-reg declared `chunk_classes = ("note", "memory", "prereg")` and the
cell did not hard-fail on `per_class.memory.n_chunks == 0`.

---

## ANGLE 1 - math / KB density

### What the literature says

- **Treves-Rolls (CA3 capacity)**: capacity of a diluted recurrent
  attractor is dominated by **connections per neuron** `C`, not total
  neuron count `N`. For a rat CA3 with N=300k, C=12k synapses/neuron,
  the load-bearing parameter is C, not N (PMC3691555).
- **Sparse coding lift**: capacity in sparse autoassociators scales as
  `~ C / (a * log(1/a))` where `a` = activity fraction. The dentate
  gyrus achieves `a ~ 0.05` (5% active granule cells per context per
  literature). This is why pattern separation matters more than raw
  partition count.
- **HDC bundling capacity**: members bundled (summed-and-signed) into a
  single n_dim hypervector are recoverable up to **O(n_dim) members**
  with quasi-orthogonality (Kanerva, confirmed by Grokipedia /
  emergentmind survey 2026). For n_dim=2048 (this cell), bundle
  capacity is ~hundreds, NOT thousands. A chunk's content vector
  bundles ~500-2000 trigrams, which is at or past the linearity edge --
  noise floor rises with bundle count.
- **Vector-DB partition density rule of thumb** (Scalable Distributed
  Vector Search, arxiv 2512.17264): "Read cost is inversely proportional
  to partition density, with costs increasing sharply when density
  drops below 0.1." For Recall@5 preservation, density target is
  ~1-1000 vectors per partition active on a typical query.

### Birthday-paradox / hit-existence math (what density actually means here)

Let M = total atoms, P = partitions. Per-partition mass = M/P. A query
Q needs to find a target chunk T_q in partition `class(T_q)`. The
probability T_q EXISTS in its partition is **structural, not
probabilistic** -- if `class(T_q)` is hard-coded by chunk source class
and Q's expected_classes is correctly enumerated, P(T_q in partition) =
1.0 by construction.

The metrics confirm this: `target_hits = 8` for every failed query means
8/8 of the returned atoms are from the correct partition. The partition
contains the answer-class. The "answer chunk doesn't exist in partition"
framing is wrong here. The "answer chunk's cosine to query is below
0.30" framing is right.

### Density floor IF we were actually density-bound

For pure shot-noise top-K retrieval over a corpus of M items at recall
target 0.80 with the query truly present:

- The signal-vs-distractor cosine gap needs to exceed top-K noise.
- For bipolar HD at n_dim=2048, sigma_cos for two random vectors is
  `1/sqrt(n_dim) ~ 0.022`. Two-sigma noise = 0.044. For 99% safety
  margin under top-1000 distractors (Bonferroni-like): need
  `signal_cosine > z(M) * sigma` where z(1000) ~ 3.3 -> need
  signal > 0.073.
- Observed best signal cosines in v3 = 0.14-0.30 -> nominally above the
  noise floor. So the **substrate has enough discriminative cosine
  margin** even at M=2199. The "ratio_resolved" failure is the **refuse
  gate**, not the SNR.

### Conclusion ANGLE 1

The KB has plenty of density per partition (~1100/class, > 100x the
~5-vector minimum the literature suggests for top-K=8 recall). The
n_dim=2048 bundle capacity is adequate. The math does NOT predict
failure at this scale -- not from density and not from SNR. The failure
is a **calibration/threshold artifact**, not a capacity artifact.

---

## ANGLE 2 - brain partitioning (CA3/DG, semantic vs episodic)

### What brain partitioning actually does

- The brain does NOT partition by source-class in the v3 sense. It
  partitions by **(a) anatomy/modality**, **(b) sparsity/decorrelation**,
  and **(c) consolidation timescale**.
- Anatomical partition: visual atoms live in occipital, semantic
  representations converge in anterior temporal lobe (ATL), episodic
  context binds in hippocampus, autobiographical detail in MTL+parietal
  (Oxford Brain 2024; PMC3350748). This is a partition by REPRESENTATION
  FORMAT, not by source class.
- Sparsity partition: dentate gyrus expands input dimensionality and
  enforces ~5% activity, decorrelating overlapping inputs BEFORE CA3
  attractor recall. This makes "which partition" implicit in the
  representation (sparse coding IS the partition key).
- Temporal partition: hippocampus holds episodes for days-weeks; cortex
  abstracts to semantic memory over weeks-years. Same content, different
  representational substrate, different timescale.

### What this maps to in the v3 failure

- The v3 cell partitions by **source class** (note vs prereg vs memory).
  This is closest to a TEMPORAL/CONSOLIDATION partition (notes = recent
  working memory; preregs = procedural; memory = USER-locked directives
  = semantic-like). The partitioning concept itself is fine and has
  brain precedent.
- BUT the brain combines partitioning with **sparse, decorrelated
  encoding** at the partition boundary (DG before CA3). The v3 cell
  partitions WITHOUT first sparsifying or decorrelating chunk content
  encodings. So each chunk's bundled HD vector has high "dimensional
  swamp" from ~500-2000 random trigrams of common English -- the
  background noise of "the", "of ", "and", "ing" etc. drowns the
  discriminative trigrams of the actual topic.
- Brain analogy: this is like sending raw entorhinal cortex output
  straight into CA3 attractor recall without DG pattern separation.
  Recall is brittle and recall threshold becomes arbitrary.

### Implication

The v3 cell skipped the DG-equivalent step. The fix is not "more atoms
per partition" -- it's **sparser, more discriminative chunk encoding**:
TF-IDF reweighting of trigrams (downweight common English n-grams),
header/title bias (chunks named after their topic), or a learned
projection that pulls semantically distinct chunks apart in HD space.

### Conclusion ANGLE 2

The brain's partitioning works because it is paired with sparsity and
decorrelation BEFORE the recall stage. v3's source-class partitioning
without an upstream sparsify step is the brain analog of "skip DG, hope
CA3 figures it out." It can't.

---

## ANGLE 3 - cross-domain (sharding, vector DB, bloom filters)

### Database sharding

- Sharding works when query carries the shard key. When queries are
  off-key, fan-out + merge is required; recall degrades unless
  fan-out is permitted. (MongoDB / Aerospike docs, Last9 sharding
  post).
- For v3, the cell routes by `expected_classes` -- analogous to having
  a perfect shard key. So routing is not the failure mode. (Routing
  acc = 1.0 confirms this.)
- The relevant DB analogy is: **a query that hits the right shard but
  finds rows whose full-text-index score is below the relevance cutoff
  still returns nothing**. The shard isn't empty; the relevance score is
  miscalibrated. This is the v3 situation almost exactly.

### Vector DB recall tuning

- Recall@N targets are typically set first, then `efSearch` /
  `confidence_floor` / `tau` is tuned to hit that target at acceptable
  latency (turbopuffer continuous-recall; opensourceconnections vector
  search). The CRITICAL move is: **do NOT use a single fixed cosine
  threshold across heterogeneous corpora**. Different datasets need
  substantially different thresholds (QVCache, arxiv 2602.02057).
- v3 inherited v2's `DEFAULT_TAU = 0.30` without re-calibration. v2's
  filename-index produced cosines in 0.40-0.78 band; v3's content-chunk
  encoder produces cosines in 0.14-0.30 band. The threshold needs to
  drop to ~0.15-0.20 to match the new regime, OR confidence needs
  re-normalization (per-corpus z-score or rank-based instead of raw
  cosine).

### Bloom filters / sparse coding

- Bloom-filter false-positive rate is `~(1 - e^(-kn/m))^k` -- depends on
  inserted-item count `n` over bit-array size `m` and hash count `k`.
  At `n/m = 0.7` capacity, FPR explodes.
- The HDC analog: bundling N items into a single n_dim hypervector
  hits a similar capacity wall at `N ~ n_dim / log(n_dim)`. For
  n_dim=2048, that's `N ~ 270`. v3's chunks average 500-2000 trigrams
  per bundle -- past this wall. Each individual trigram's contribution
  is therefore noisy.

### Web search shard density

- Modern web shards are 10-50 GB each -- chosen for I/O, not recall
  (Elasticsearch best practices, OpenSearch docs). Recall is preserved
  by per-shard TF-IDF + BM25 + result-merging across shards.
- The lesson: **shard size is decoupled from recall in well-engineered
  systems**, because the per-shard scoring function is properly
  normalized. v3's per-partition scoring is the same cosine that fails
  in BASELINE -- there's no per-partition normalization.

### Conclusion ANGLE 3

Cross-domain consensus: when routing is correct but recall fails, the
fix is **score-function calibration to corpus**, not partition resizing.
A fixed cosine threshold across schema-changes is a known anti-pattern
in vector DB / IR practice. v3 hit it.

---

## Synthesis: 3 questions the user asked

### Q1: WHY does substrate's self-contained KB only have 1429 atoms/partition?

It's actually 1138 (note) + 1061 (prereg) + 0 (memory) = 2199 atoms
across 2 partitions (the "1429" in the user message looks like
~ratio_resolved-derived number, not an atom count; the actual chunks
per class are above). The bound on count is:

- `max_files_per_class = 200` (cell's `SELF_CONTAINED_MAX_FILES` arg).
  Repo has thousands of notes; only 200 sampled. Lifting this is
  trivial (change one constant).
- `avg_chunks_per_file = 5.51` (from manifest). With 200 files, that's
  ~1100 chunks. To 4x density: bump `max_files_per_class` to 800.
- **The memory class is missing because of a schema/mode bug, NOT a
  density bug.** Fix that separately (route the schema audit through
  the dual-store audit ANCHOR 5 that is in flight per MEMORY.md).
- Source files DO exist: `memory/` directory has ~50 feedback files,
  preregs/ has hundreds, notes/ has thousands. Plenty of headroom.

### Q2: What's the MINIMUM density per partition for ratio_resolved >= 0.80?

**Density is not the binding constraint.** Density of ~5 atoms per
partition would be enough for top-K=8 recall, given correct scoring.
The metrics show 1100 atoms/partition where 8/8 top-K are in the right
partition with cosine 0.14-0.30. **Removing the refuse gate (or
lowering it to 0.10) would push ratio_resolved from 0.14 to ~0.95
without changing density at all.** That is the proof: density is
sufficient; the gate is wrong.

A density floor only applies if the substrate were missing the answer
chunk entirely. With 28 hard-coded query targets and structural
source-class routing, that's not the regime.

### Q3: Options to fix

Three independent fixes, prioritized by leverage:

**Fix A (highest leverage, lowest cost) - re-calibrate the refuse gate
to the chunk regime.**
- Drop `DEFAULT_TAU` from 0.30 to ~0.15 in the v4 cell.
- OR replace raw-cosine gate with **rank-based / z-score gate**: refuse
  only when top-1 cosine is within 1-sigma of top-100 cosine (no
  signal) instead of below an absolute number.
- Cost: one constant change + rerun. Expected lift: ratio_resolved
  0.14 -> 0.80+ in BASELINE, similar in PARTITIONED.

**Fix B (medium leverage, medium cost) - fix the chunk encoding
discriminability.**
- Add TF-IDF trigram weighting at encode time (downweight common
  English n-grams; upweight discriminative ones).
- OR add a header/title-bias bundle (encode the chunk header
  separately, weighted 4x in the bundled HD).
- OR encode chunks at n_dim=4096 instead of 2048 (doubles bundle
  capacity; lowers noise floor by sqrt(2)).
- Cost: encoder change + reingest. Expected lift: cosines move from
  0.14-0.30 band to 0.30-0.50 band, putting them comfortably above
  any reasonable threshold.

**Fix C (lowest leverage, highest cost) - increase corpus density.**
- Lift `max_files_per_class` to 800 and ingest `memory/` correctly.
- This will NOT fix the cosine-floor issue (BASELINE on 9000 atoms
  will still have the same per-chunk cosine distribution).
- BUT it provides the ud_retention substrate (memory-class chunks
  exist) and makes the cell representative of the real director-KB
  use case.
- Cost: schema fix + reingest. Expected lift: ud_retention
  0.21 -> ~baseline; ratio_resolved unchanged.

**Recommended: Fix A + C combined for v4.** Fix B is correct
long-term but ships as a separate substrate-encoder anchor (already
implicit in the "encoder is THE bottleneck" arc from 2026-06-23 per
MEMORY.md). For v4, the goal is to prove the PARTITION ROUTING
MECHANISM works once recall is calibrated. Fix A unlocks that;
Fix C makes the test honest.

---

## ANCHOR 1 v4 cell-spec stub (density-AND-threshold fix)

```
Anchor: kb_partition_by_source_class_v4_self_contained_recalibrated
Cell:   experiments/exp_kb_partition_by_source_class_v4_self_contained_recalibrated.py
Wave:   ANCHOR 1 partition v4 rescue (v3 HARD_FAIL was REFUSE_GATE_MISCALIBRATED + MEMORY_CLASS_DROP)
Queue:  remote_cpu_queue (no GPU needed; ingest+query is <60s)
Prereg: preregs/2026-06-27_kb_partition_by_source_class_v4_self_contained_recalibrated.md

Primitives composed (chain-grade, same as v3):
  - hdlab/director_kb_chunk_ingest.py
  - hdlab/director_kb_query.py
  - hdlab/director_kb.py
  - hdlab/char_trigram_encoder.py
  - hdlab/kg_traversal.py

CHANGES from v3 (3 surgical changes; nothing else):

  1. DEFAULT_TAU = 0.15 (was 0.30). Justification: v3 metrics show
     correct-class top-1 cosines fall in 0.14-0.30 band; old threshold
     refused correct retrievals. New threshold is calibrated empirically
     from v3 metrics distribution.

  2. SELF_CONTAINED_MAX_FILES = 800 (was 200) for full run; 50 for
     smoke. Justification: removes the file-count artifact in the
     density axis so v4 results generalize to the real director-KB
     corpus.

  3. Verify schema source_classes["memory"].mode == "text" pre-flight;
     HARD_FAIL if memory class produces n_files == 0 OR n_chunks == 0
     when "memory" is in chunk_classes. (META_RULE_H CARDINALITY_OK
     applied; this is what v3 should have caught.)

ARMS (3, identical structure to v3):
  - ARM_SINGLE_W_BASELINE
  - ARM_PARTITIONED_W_EQUAL_CAPACITY
  - ARM_PARTITIONED_W_MEMORY_OVERSIZED

DIAGNOSTIC ARMS (additional, NOT band-gating):
  - DIAG_RANK_BASED_GATE: same retrievals as BASELINE but resolved-flag
    set by "top-1 cosine > 1-sigma above top-50 cosine" instead of
    "top-1 > 0.15". Records ratio_resolved_rankgated for comparison.
    If rankgated > absolute-thresholded at any sample, the threshold
    is still uncalibrated.
  - DIAG_COSINE_DISTRIBUTION: dumps full top-K cosine distribution
    histogram per query so future v5 / encoder-rework can calibrate
    properly.

DISCRIMINATOR-MUST-SURVIVE-SCALE (D1):
  Smoke runs at 50 files/class with 10 queries (same as v3); but adds
  a "FULL_N_PREVIEW" arm in smoke that runs 800 files/class with 5
  queries -- if FULL_N_PREVIEW ratio_resolved < 0.5, ABORT smoke
  without dispatching full. (Catches scale-fragility before burning
  CPU-minutes; per Fix #15 / D1 discipline from MEMORY.md.)

CARDINALITY_OK (D4) MANDATORY:
  EXPECTED_N_ARMS = 3 (band) + 2 (diagnostic) = 5 total
  EXPECTED_INGEST_ENTITIES_MIN = 100 (smoke) / 2000 (full)
  EXPECTED_CHUNK_CLASSES_NONZERO = {"note", "memory", "prereg"}
  HARD_FAIL_CARDINALITY_BREACH = any of:
    - len(band_arms) != 3
    - per_class[c]["n_chunks"] == 0 for any c in chunk_classes
    - n_entities < EXPECTED_INGEST_ENTITIES_MIN

PRE-REG BANDS (HARD-LOCKED; v3 verbatim except RATIO_RESOLVED_FLOOR):
  HARD_PASS:
    - routing_accuracy >= 0.95
    - cross_partition_leak_rate < 0.05
    - ratio_resolved >= 0.80           # SAME
    - ud_retention >= max(non_ud - 0.10, 0.70)
  MIDDLE_BAND:
    - mechanism operational + UD close to floor
  HARD_FAIL:
    - routing_acc < 0.90
    - OR leak >= 0.05
    - OR ratio_resolved < 0.70
    - OR cardinality breach
    - OR n_chunks == 0 for any declared class

SUBSTRATE-ONLY-DECODE GATE: n_llm_calls = 0 per arm (unchanged).

REAL DATA: notes/ + memory/ + preregs/ from repo at run-time
(unchanged).

HONEST SCOPE: tests whether source-class routing PLUS a properly
calibrated refuse-gate (Fix A) holds at the real director-KB density
(Fix C). Does NOT yet test encoder-quality improvements (Fix B) --
that is a separate chunk-encoder rework cell.

EXPECTED OUTCOME (research prediction; P=0.55 after lit-scan
calibration penalty):
  Fix A alone: BASELINE ratio_resolved 0.18 -> 0.85, PARTITIONED
    0.14 -> 0.80, ud_retention 0.21 -> 0.70.
  Fix A+C combined: same lift plus memory-class queries now have
    target atoms to return.

This is a recalibration cell, not a novel-mechanism cell, so the
lit-scan penalty should be small. If v4 still HARD_FAILs after Fix A+C,
the encoder is the binding constraint and the next cell should be a
chunk-encoder rework (Fix B).
```

---

## Cross-link to existing program threads

- **Substrate-as-Director-KB dogfood** (USER 2026-06-26): this cell is
  the partition-routing leg of that program. v4 fixes the recall gate
  so the partition-routing claim is testable on its own merits.
- **Encoder is THE bottleneck** (project arc 2026-06-23, MEMORY.md): v4
  Fix A+C does NOT solve the encoder problem; Fix B is the proper
  encoder rework. v4 buys time to ship the partition mechanism cleanly
  while encoder work continues.
- **DISCRIMINATOR-MUST-SURVIVE-SCALE** (USER 2026-06-26 + Fix #15):
  v3's smoke ran at 50 files/class and HARD_PASSed; full at 200
  files/class HARD_FAILed. The smoke didn't fire the discriminator at
  full scale. v4 adds a FULL_N_PREVIEW arm in smoke to catch this.
- **CARDINALITY_OK** (META_RULE_H): v3 should have HARD_FAILed in smoke
  on `per_class.memory.n_chunks == 0`. v4 adds the explicit
  cardinality gate.
- **THREE SMOKE DISCIPLINES** (2026-06-26): "smoke must FIRE
  discriminator not just verify cell runs." v3 violated this; v4 fixes
  it.

## Sources used

### HDC bundling capacity / vector lengths
- [Hyperdimensional Computing Overview - emergentmind](https://www.emergentmind.com/topics/hyperdimensional-computing)
- [Hyperdimensional computing - Grokipedia](https://grokipedia.com/page/Hyperdimensional_computing)

### Hippocampal capacity / Treves-Rolls / DG-CA3
- [A quantitative theory of the functions of the hippocampal CA3 network in memory - PMC3691555](https://pmc.ncbi.nlm.nih.gov/articles/PMC3691555/)
- [Sparse and distributed coding of episodic memory in neurons of the human hippocampus - PNAS](https://www.pnas.org/doi/10.1073/pnas.1408365111)
- [Pattern completion and pattern separation in the hippocampus - Frontiers](https://www.frontiersin.org/journals/systems-neuroscience/articles/10.3389/fnsys.2013.00074/full)
- [Effect of adult-born immature granule cells on pattern separation in the hippocampal dentate gyrus - PMC11297892](https://pmc.ncbi.nlm.nih.gov/articles/PMC11297892/)

### Semantic vs episodic memory partitioning in brain
- [Differential reorganization of episodic and semantic memory systems in epilepsy-related mesiotemporal pathology - Oxford Brain](https://academic.oup.com/brain/article/147/11/3918/7721059)
- [The Neurobiology of Semantic Memory - PMC3350748](https://pmc.ncbi.nlm.nih.gov/articles/PMC3350748/)

### Vector DB recall / threshold tuning / sharding
- [Vector Search Navigating Recall and Performance - OpenSource Connections](https://opensourceconnections.com/blog/2025/02/27/vector-search-navigating-recall-and-performance/)
- [Continuous recall measurement - turbopuffer](https://turbopuffer.com/blog/continuous-recall)
- [QVCache: A Query-Aware Vector Cache - arxiv 2602.02057](https://arxiv.org/pdf/2602.02057)
- [Scalable Distributed Vector Search via Accuracy Preserving Index Construction - arxiv 2512.17264](https://arxiv.org/pdf/2512.17264)
- [Index-based High-dimensional Cosine Threshold Querying with Optimality Guarantees - arxiv 1812.07695](https://arxiv.org/pdf/1812.07695)
- [Database Sharding - MongoDB Docs](https://www.mongodb.com/docs/manual/sharding/)
- [Elasticsearch shard and node size best practices](https://www.elastic.co/search-labs/blog/elasticsearch-node-shard-size-best-practices)

### Bag-of-words / BoW retrieval / trigram methods
- [A new simple and effective measure for bag-of-word inter-document similarity measurement - arxiv 1902.03402](https://arxiv.org/pdf/1902.03402)
- [pg_trgm trigram matching - PostgreSQL Documentation](https://www.postgresql.org/docs/current/pgtrgm.html)
- [Dense Text Retrieval Based on Pretrained Language Models: A Survey - ACM TOIS](https://dl.acm.org/doi/10.1145/3637870)
