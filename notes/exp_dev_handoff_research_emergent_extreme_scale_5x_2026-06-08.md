# exp_dev hand-off -- research: substrate emergent properties at extreme scale

Filed-by: research sub-agent (2026-06-08)
Trigger: notes/research_drill_substrate_emergent_extreme_scale_5x_2026-06-08.md
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

Five empirical anchors are proposed to convert extreme-scale categorical claims from
"observed at validated scale" into confirmed scaling laws. All five are within sprint
range. Anchors E1 and E5 require GPU; E2, E3, E4 are CPU-only. The recommended
sequencing is E2 first (cheapest, $0, highest confidence), then E5 and E3 in parallel
(both $0, local GPU), then E4 (CPU multi-hop pipeline), then E1 (cloud GPU, $50-80).

The research note identifies the encoder drift reindexing cost as the highest-risk
production failure mode for 1B-scale deployment. E2 directly characterizes this. No
current PP row covers reindexing cost at scale; E2 creates that anchor.

---

## Anchor Candidates (rank-ordered by P_actionable x compute-cost x strategic leverage)

### 1. E2 -- Encoder drift critical radius at 10M facts (HIGHEST PRIORITY)

Anchor pointer: SCALE-DRIFT-E2 (new; not yet queued)
Substrate-product reading: Maps recall@1 degradation vs encoder drift distance (cosine)
  at 10M-fact corpus. Determines the critical drift radius beyond which re-indexing
  is required. Directly sets the production maintenance cadence for any scale deployment.
  PP-169 validated detection; E2 converts detection into a recall-loss characterization.
  This is a new cap_map row candidate (PP-next): "encoder drift tolerance threshold."
Tier hint: Local GPU; ~4 hours wall; uses existing encoder infrastructure
Why-now: Cheapest anchor ($0 cloud cost). High confidence (P_deflated=0.62). Directly
  actionable for product: sets the encoder replacement policy before 1B-scale deployment.
  Blocks no other anchor; can run immediately.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: Recall@1 degradation onset at drift >= 0.20 cosine; rate > 2pp per 0.05
             drift unit; pattern consistent across >= 3 encoder pairs
  HARD-FAIL: No measurable recall degradation at drift <= 0.50 (positive finding --
             implies substrate is drift-tolerant; would flip the maintenance policy)
  MID-BAND: Degradation onset at drift 0.30-0.50 (re-encoding needed only for large drifts)

Inputs required: Production encoder (Llama-1B BASE or Pythia); 2 fine-tuned encoder
  variants (standard NLP fine-tuning targets: NLI + classification); 10M-fact synthetic
  corpus (random text from Common Crawl or Wikipedia subset); existing recall@1 harness.

### 2. E5 -- O(1) retrieval latency scaling law: 10M, 30M, 100M facts (HIGH PRIORITY)

Anchor pointer: SCALE-O1-E5 (new; not yet queued)
Substrate-product reading: Measures mean + p99 retrieval latency at 3 corpus sizes to
  fit a scaling curve and confirm O(1) vs O(log N) vs O(N) latency. PP-98 and PP-166
  provide 100M data points; E5 adds 10M and 30M to fit the curve properly. Converts
  "we observed sub-ms at 100M" into "retrieval is O(1) in corpus size" as a confirmed
  scaling law. Directly supports the categorical positioning claim against HNSW/IVF
  (which are O(log N) and degrade significantly at 1B scale).
Tier hint: Local GPU (RTX 3090 or equivalent); ~6 hours wall; uses existing substrate
  retrieval harness
Why-now: $0 cost. Converts existing data points (PP-98, PP-166) into a scaling law.
  High P_deflated (0.58) among extreme-scale claims. Runs in parallel with E2.

Pre-reg bands:
  HARD-PASS: Latency fits O(1) model (flat) with < 2x variation across 10x N range;
             p99 < 5ms at all three corpus sizes on same hardware
  HARD-FAIL: Latency grows O(log N) or faster -- indicates approximation, not true O(1)
  MID-BAND: Latency flat for 10M-100M but shows uptick at 100M (may indicate VRAM limit)

### 3. E3 -- Cross-shard latency scaling law (MEDIUM PRIORITY)

Anchor pointer: SCALE-SHARD-E3 (new; not yet queued)
Substrate-product reading: Measures K=12 multi-hop latency vs shard count (4, 8, 16,
  32 shards) with random vs per-subject partitioning. Determines whether per-subject
  sharding (PP-134/147) keeps latency O(shard_count) or whether routing overhead grows
  faster. Sets the maximum practical shard count for multi-hop queries.
Tier hint: Local CPU multi-process simulation; ~2 hours wall; uses existing multi-hop
  harness
Why-now: $0 cost. Directly sets engineering constraint for distributed deployment design.
  Can run on CPU without GPU.

Pre-reg bands:
  HARD-PASS: Latency grows O(shard_count^1.0) or sublinearly with per-subject sharding;
             p99 < 10ms at 32 shards for K=12 queries
  HARD-FAIL: Latency grows O(shard_count^1.5) or faster -- routing overhead dominates,
             shard count must stay below 8 for latency targets
  MID-BAND: Linear scaling confirmed but absolute latency exceeds 10ms at 32 shards
             (acceptable for non-interactive workloads)

### 4. E4 -- K=20+ multi-hop chain success rate (MEDIUM PRIORITY)

Anchor pointer: SCALE-KHOP-E4 (new; not yet queued)
Substrate-product reading: Extends the K=12 validated result (PP) to K=15, 20, 25.
  Measures chain integrity (fraction of full-length successful retrievals) at each K.
  The error-compounding math predicts K_max for 90% chain success as a function of
  per-hop miss rate epsilon. E4 measures epsilon empirically and calibrates K_max.
  Directly sets the multi-hop depth claim in product positioning.
Tier hint: Local CPU; ~3 hours wall; uses existing HotpotQA multi-hop pipeline
Why-now: $0 cost. HotpotQA pipeline already exists. The K=12 result is validated; K=20
  extension is a straightforward sweep. Settles the K-horizon question.

Pre-reg bands:
  HARD-PASS: K=20 achieves >= 80% chain integrity; per-hop epsilon < 0.01 confirmed
  HARD-FAIL: K=15 drops below 70% chain integrity -- K-hop product claim capped at K<=12
  MID-BAND: K=15 at 80%, K=20 at 60-80% (partial extension; K=15 is the new claim)

### 5. E1 -- Codebook capacity at 1B facts (LOWER PRIORITY -- cloud GPU required)

Anchor pointer: SCALE-CAP-E1 (new; not yet queued)
Substrate-product reading: Generates 1B synthetic fact vectors and stores them in
  substrate at N=4096, M=65536 codebook. Measures recall@1 at 500M and 1B facts.
  This is the gate experiment for all 1B-scale product claims. If recall fails before
  1B, M must grow with N_facts and the fixed-M architecture requires a redesign.
  If recall holds at 1B, the O(1) and linear-storage claims are jointly confirmed.
Tier hint: Cloud GPU (A100 80GB required for W matrix); ~8 hours wall; ~$50-80 cost
Why-now: Highest strategic leverage but highest compute cost. Recommend running after
  E2+E5 confirm the architecture holds at 100M scale. E1 is the final gate for 1B claims.

Pre-reg bands:
  HARD-PASS: Recall@1 >= 0.90 at 1B facts (same threshold as 100M validated)
  HARD-FAIL: Recall@1 < 0.70 at 500M facts (capacity cliff before 1B -- M must grow)
  MID-BAND: Recall@1 in [0.70, 0.90] at 1B -- capacity is approaching limit;
             M increase to 131072 would extend capacity

---

## Context pointers

- Research note (full analysis): notes/research_drill_substrate_emergent_extreme_scale_5x_2026-06-08.md
- Prior validated scale: PP-98 (100M facts), PP-145 (Wikipedia 1M), PP-127 (sharding)
- Prior latency data: PP-150, PP-166 (sub-ms O(1) at validated scale)
- Prior encoder drift detection: PP-169 (100% detection + 0 FP at 0.20-0.50 drift)
- Prior sharding data: PP-134, PP-147 (per-subject + per-relation sharding validated)
- Prior multi-hop data: PP (K=12 at 99% recovery -- confirm exact PP number)
- LLM scaling laws reference: arxiv 2406.15720 (EMNLP 2024) -- 1000B params for Wikidata
- Structured memory vs long-context reference: arxiv 2603.04814 (2025) -- 252x cost advantage
- Cross-shard failure mode reference: arxiv 2601.12499 (Weakest Link Effect, multi-hop)
- Encoder drift production reference: DriftLens 2024 (embedding-space drift monitoring)

---

## Contract section

Research has characterized 5 emergent properties at 1B+ scale with P_deflated estimates
and proposed 5 ranked empirical anchors. The research note contains hard-pass and
hard-fail bands for each anchor. exp_dev is responsible for:
  (1) Validating anchor designs against current substrate harness API
  (2) Refining pre-reg bands based on current empirical baselines
  (3) Assigning to correct queue (local CPU, local GPU, or cloud)
  (4) Not dispatching E1 (cloud) until E2 and E5 have run and confirm architecture holds

Research does NOT prescribe implementation details, sweep grids, or queue assignments.
Those are exp_dev's autonomous domain per [[feedback-no-experiment-design-in-prompts]].

---

## Autonomy declaration

exp_dev acts autonomously on all 5 anchors subject to pause gate check. Sequencing
recommendation is E2 -> (E5 parallel E3) -> E4 -> E1. exp_dev may reorder based on
queue state and current runner availability. Research does not need to be consulted
before dispatch unless a new finding changes the strategic context.
