# exp_dev hand-off -- research: Streaming Algorithms / Sketching Field 5x Deep Drill

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_field_streaming_algorithms_5x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Streaming algorithms field lit-scan completed 2026-06-07. Core findings:

1. Substrate already implements Misra-Gries (cycle 167+170 HP), ADWIN-style concept drift
   (cycle 170 HP), and DP histograms (cycles 170+171 HP). These are production-validated.

2. Four high-value unimplemented gaps: Count-Min Sketch (O(1) frequency query + delete support),
   Cuckoo filter (duplicate-ingest prevention + GDPR delete), HyperLogLog (cardinality metric),
   Reservoir sampling (training curation). All are 2-5 day engineering tasks.

3. Ben-Eliezer et al. 2022 (JACM) theorem: substrate's DP histogram layer is automatically
   adversarially robust. This is a free security property with a published reference.

4. CMS vs Misra-Gries: CMS gives O(1) point queries (vs O(k) scan) and supports signed updates
   (deletes). At k=1000 heavy-hitter slots, CMS is 1000x faster per lookup.

5. Streaming PCA (Oja 1982 / Boutsidis 2014): provides incremental whitening/projection updates
   without batch recomputation. Requires a pre-test to measure actual PCA basis drift rate.

These findings are actionable as 5 near-term experiments (all CPU or local GPU).

---

## Anchor Candidates (rank-ordered by P_actionable x cost x urgency)

### 1. STREAM-CMS-BENCH -- Count-Min Sketch vs Misra-Gries Benchmark (HIGHEST PRIORITY)

Anchor pointer: STREAM-CMS-BENCH (new; not yet queued)
Substrate-product reading: Implements a 3 x 3000 Count-Min Sketch alongside the existing
  Misra-Gries top-K tracker. Feeds 1M items from a Zipf-1.0 distribution. Measures:
  (a) point query error for top-K items,
  (b) query latency: CMS O(d=3) vs Misra-Gries O(k=1000) scan,
  (c) delete operation correctness after 10% of items deleted.
  If CMS error < 0.1% of stream length for all items with count > 100, the engineering
  investment is justified. If latency improvement > 100x at k=1000, CMS replaces the
  Misra-Gries scan path for frequency lookups.
Tier hint: CPU laptop, ~30 min wall. No cloud needed.
Why-now: This is the cheapest possible validation for the most impactful gap.
  CMS is already theoretically validated; this confirms it at substrate's operating scale.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: point query error < 0.1% * stream_length for all items with count >= 100
             AND CMS query latency < 10% of Misra-Gries scan latency at k=1000
             AND delete operation error < 0.1% after 10% deletions
  HARD-FAIL: point query error > 1% * stream_length at epsilon=0.001 table sizing
             OR delete operation produces negative counts (signed CMS broken)
  MID-BAND:  error < 1% but > 0.1%; latency improvement < 10x; viable but with caveats

Table sizing: d=3 rows, w=ceil(e/epsilon) = 2719 for epsilon=0.001. Use w=3000 for round number.
Distribution: Zipf s=1.0, universe=100000, stream_length=1000000. Heavy hitters defined as
  count > 1000 (top 0.1%). There are approximately 100-200 true heavy hitters in this regime.

### 2. STREAM-CUCKOO-FILTER -- Cuckoo Filter Ingest Deduplication Benchmark

Anchor pointer: STREAM-CUCKOO-FILTER (new; not yet queued)
Substrate-product reading: Implements a Cuckoo filter sized for 10M items with target FPR 0.1%.
  Inserts 10M entity fingerprints (SHA-256 first 8 bytes). Queries 10M existing + 10M novel items.
  Measures: false positive rate, false negative rate (should be 0), and per-query latency.
  If FPR < 0.15% and latency < 1 microsecond per query, production deployment is justified
  for the ingest deduplication path.
Tier hint: CPU laptop, ~15-30 min wall. Uses python-cuckoo or cuckoofilter library.
Why-now: GDPR compliance differentiator. Every duplicate fact stored is wasted KB space.
  Cuckoo filter is the only practical O(1) deduplication check that also supports deletion.

Pre-reg bands:
  HARD-PASS: FPR < 0.15% at 10M items AND false negative rate = 0 (no inserted item missed)
             AND per-query latency < 5 microseconds on laptop hardware
  HARD-FAIL: FPR > 1% (filter undersized; would need 10x more memory to fix)
             OR false negatives > 0 (cuckoo eviction failure; filter overfull)
  MID-BAND:  FPR in [0.15%, 1%]; usable if memory budget allows a 2x larger filter

### 3. STREAM-HLL-CARD -- HyperLogLog / UltraLogLog Cardinality Estimation

Anchor pointer: STREAM-HLL-CARD (new; not yet queued)
Substrate-product reading: Implements a HyperLogLog (m=2^14 = 16384 registers; 12KB) and an
  UltraLogLog estimator over a stream of 10M distinct entity IDs. Ground truth from exact count.
  Measures: relative error vs exact count at N = 10^4, 10^5, 10^6, 10^7.
  If relative error < 2% at N=10M, this becomes the substrate dashboard "entity count" metric.
Tier hint: CPU laptop, ~15 min wall. Python datasketch library or hyperloglog package.
Why-now: Customer dashboard metric. Low cost, high visibility. Demonstrates quantitative
  KB growth tracking with negligible overhead.

Pre-reg bands:
  HARD-PASS: relative error < 2% at N=10M AND UltraLogLog error < HyperLogLog error
             (confirms UltraLogLog superiority claimed in 2023 paper)
  HARD-FAIL: relative error > 5% at N=10M (use exact count for dashboard instead;
             HLL provides no value at this accuracy level)
  MID-BAND:  error in [2%, 5%]; usable for trend monitoring but not for precise reporting

### 4. STREAM-RESERVOIR -- Weighted Reservoir Sampling Query Log Curation

Anchor pointer: STREAM-RESERVOIR (new; not yet queued)
Substrate-product reading: Implements Vitter Algorithm Z (skip-based reservoir) and Efraimidis-
  Spirakis weighted variant. Feeds a simulated query stream of 1M queries with Zipf-1.0
  query-type distribution. Reservoir size k=10000.
  Measures: (a) uniformity of sampled query types (chi-square test vs uniform),
            (b) weighted sampling bias toward rare types (coverage metric),
            (c) memory usage (should be < 10MB for 10000 text queries).
  If sampled distribution is statistically uniform and coverage of rare types > 2x naive
  last-N sampling, reservoir sampling is validated for training data curation.
Tier hint: CPU laptop, ~15 min wall. Pure Python; no dependencies beyond standard library.
Why-now: Gates Tier 4 LoRA fine-tuning pipeline. The training data quality determines
  whether LoRA updates generalize or overfit to recent query patterns.

Pre-reg bands:
  HARD-PASS: chi-square test p > 0.05 (reservoir is statistically uniform) AND rare type
             coverage ratio > 1.5x vs last-N (weighted reservoir meaningfully improves coverage)
  HARD-FAIL: chi-square test p < 0.001 (severe sampling bias; algorithm is broken)
  MID-BAND:  p in [0.001, 0.05]; biased but usable; investigate whether bias is systematic

### 5. STREAM-OJA-DRIFT -- PCA Basis Drift Rate Under Streaming Updates

Anchor pointer: STREAM-OJA-DRIFT (new; not yet queued)
Substrate-product reading: This is the pre-test gate for streaming PCA adoption (Tier C gap).
  Generates a stream of 1M bipolar vectors from a slowly-drifting distribution (distribution
  rotates by 1 degree per 10K samples). Computes batch PCA at t=0, t=500K, t=1M.
  Measures: principal angle between PCA bases at t=0 and t=1M.
  Also runs Oja's rule in parallel; measures principal angle between Oja's final estimate
  and batch PCA at t=1M.
  If principal angle > 5 degrees, the distribution is drifting enough to justify streaming PCA.
  If Oja's estimate is within 2 degrees of batch PCA, Oja's rule is sufficiently accurate.
Tier hint: CPU laptop, ~30-60 min wall. Uses torch.pca_lowrank for batch PCA; Oja's rule
  is a single vector update per step.
Why-now: Gates the engineering investment in streaming whitening. If the PCA basis does not
  drift significantly in production, streaming PCA is unnecessary overhead.

Pre-reg bands:
  HARD-PASS: batch PCA principal angle at t=0 vs t=1M > 5 degrees (drift is significant)
             AND Oja's estimate vs batch PCA at t=1M < 2 degrees (Oja tracks accurately)
             => proceed to streaming PCA engineering
  HARD-FAIL: principal angle < 1 degree (no meaningful drift; batch PCA is stable; skip
             streaming PCA entirely)
  MID-BAND:  angle in [1, 5] degrees (minor drift; monitor but defer streaming PCA)
  NOTE: if HARD-FAIL on drift, this result is POSITIVE for substrate -- it means batch
        whitening remains valid indefinitely at current scale, which is a simpler architecture.

---

## Dispatch priority and prerequisites

Independent (can run in parallel, all CPU):
  STREAM-CMS-BENCH, STREAM-CUCKOO-FILTER, STREAM-HLL-CARD, STREAM-RESERVOIR

Prerequisite chain:
  STREAM-OJA-DRIFT should run after the others complete (lower urgency; Tier C gate).

All 5 are CPU-only, estimated total wall time <= 3 hours combined, no cloud dispatch needed.
Anchors 1-4 are completely independent and can be batched on the CPU runner simultaneously.

---

## Strategic escalation gates

STREAM-CMS-BENCH HARD-PASS: authorize CMS as the production frequency lookup structure.
  Replace Misra-Gries scan with CMS O(1) query in the hot retrieval path.

STREAM-CUCKOO-FILTER HARD-PASS: authorize Cuckoo filter in the ingest pipeline.
  Add to GDPR compliance documentation as "O(1) entity deletion confirmation."

STREAM-HLL-CARD HARD-PASS: add "distinct entity count" to customer dashboard.
  Write a sentence in the customer pitch: "substrate tracks KB growth with 0.81% accuracy
  using HyperLogLog cardinality estimation at 12KB overhead."

STREAM-RESERVOIR HARD-PASS: gates Tier 4 LoRA fine-tuning pipeline design.
  Escalate to orchestrator before beginning Tier 4 engineering authorization.

STREAM-OJA-DRIFT HARD-FAIL (no drift): confirm that batch whitening is stable at production
  scale; close the streaming PCA gap as "not needed at current scale."

STREAM-OJA-DRIFT HARD-PASS (drift > 5 degrees): escalate to orchestrator; triggers 1-week
  streaming PCA engineering authorization.

Any result involving the Ben-Eliezer 2022 adversarial robustness theorem should be
noted in the adversarial mode documentation -- substrate's DP layer is provably robust
by theorem; this does not require an experiment but should be documented.

---

## Context pointers

- Research note (full analysis with all 10 algorithms, 5 deep levels, 20 citations):
  d:/AI/hd-instrument/notes/research_drill_field_streaming_algorithms_5x_2026-06-07.md
- Prior streaming continual extraction drill:
  d:/AI/hd-instrument/notes/research_drill_streaming_continual_extraction_2x_2026-06-05.md
- Prior streaming continual extraction handoff:
  d:/AI/hd-instrument/notes/exp_dev_handoff_research_streaming_continual_extraction_2026-06-05.md
- Substrate capability map:
  d:/AI/hd-instrument/data/substrate_capability_map.md
- Prior Misra-Gries HP anchors:
  d:/AI/hd-instrument/data/ (search: exp_*/metrics.json for cycle 167, 170)
- DP histogram HP anchors:
  d:/AI/hd-instrument/data/ (search: exp_*/metrics.json for cycles 170, 171)

---

## Contract section

This hand-off is research-to-experiment. The 5 anchor specs are provided as pre-reg
recommendations. Exp_dev is responsible for:
- Validating pre-reg bands before dispatch (adjust if local hardware baseline differs
  from the wall-time estimates above)
- Implementing minimal benchmark scripts (CMS, Cuckoo filter, HLL, reservoir, Oja -- all
  are small scripts; 50-150 lines each; no new substrate code modification required for
  the first 4 anchors; STREAM-OJA-DRIFT requires using existing whitening/PCA harness)
- Assigning to correct queue: all 5 are CPU tier; 1-4 can run on remote CPU runner in batch
- Writing verdict notes per standard protocol
- Escalating any HARD-PASS that triggers a product-tier change, dashboard metric addition,
  or Tier 4 engineering gate to orchestrator before acting on it
- For STREAM-OJA-DRIFT: escalating to Research if the drift measurement is ambiguous
  (angle in 3-5 degree range) for a follow-up streaming PCA drill

## Autonomy declaration

Exp_dev may dispatch all 5 anchors without orchestrator approval (all are CPU benchmarks,
low cost, no cloud). Any result that changes the customer pitch, adds a dashboard metric,
upgrades a cap_map row, or gates a Tier 4 engineering path MUST be escalated to orchestrator
before downstream action.
