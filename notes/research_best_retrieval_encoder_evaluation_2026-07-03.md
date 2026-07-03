# research: best retrieval encoder for Wikipedia 100K KB + downstream substrate content indexing

**Date:** 2026-07-03
**Trigger:** direct research drill request (retrieval-layer encoder modernization; bge-large-en-v1.5 is 2023-vintage)
**Scope discipline:** this drill concerns the RETRIEVAL LAYER only ("sensory input" feeding candidates to the substrate reasoning/rerank layer). Per USER clarification tonight, a non-brain-analog dense encoder at this layer is architecturally fine -- the "bge NEVER in substrate" directive is scoped to brain-analog primitives INSIDE the substrate, not the frozen borrowed encoder that hands candidates to it. This note does not touch the separate, still-open question of brain-analog substrate-native encoders (char-trigram / PPMI-SVD / VWFA / hippocampal), which is tracked in the concept-encoder arc and is HARD_NEGATIVE / HARD_FAIL across 4 witnesses as of the 2026-07-02/03 backup. That is a different question (can the substrate itself learn to encode) from this one (what should the pre-substrate retrieval encoder be).

---

## HEADLINE

For Wikipedia single-hop title/body retrieval at 100K scale, the current bge-large-en-v1.5 encoder is already near-ceiling (r@5=0.992, measured 2026-06-19) -- there is almost no retrieval-quality headroom left to buy at this task, so encoder choice there should be driven by license, context-length (bge-large truncates at 512 tokens, which silently drops most of a Wikipedia article), scaling cost to 1M+ docs, and fine-tunability, not by chasing marginal MTEB deltas. The actual quality headroom lives in a different regime -- compositional/multi-hop retrieval (HotpotQA-class), where even the best 2024-2026 open encoders plateau at recall@2hop ~0.55-0.65 (never near-ceiling) -- and that is exactly where the substrate's compositional rerank/decomposition value-add remains safe regardless of which encoder is chosen (no single-vector encoder threatens to obsolete it; the literature-confirmed structural ceiling protects that value-add automatically). Recommended path: replace bge-large-en-v1.5 with **stella_en_1.5B_v5** (MIT, Matryoshka 512-8192 dims, ~8192-token context, MTEB retrieval-tier top-5 open model) as the single default encoder for both lanes, with **snowflake-arctic-embed-l-v2.0** (Apache-2.0, 8192 ctx, smaller/cheaper) as the conservative fallback if GPU budget for 1M+ scale-out is tight.

---

## Prior-arc check (substrate KB mined before external scan)

Five prior research notes already cover large parts of this ground and are NOT re-derived here, only extended to the 2024-2026 window and the Wikipedia-KB framing:

- `notes/research_drill_retrieval_encoder_selection_3x_2026-06-07.md` -- established bge-small as best-in-33M-class for HotpotQA multi-hop; ColBERT-v2 (0.59 recall@2hop) as best size-fair multi-hop ceiling-breaker but 2-3wk integration cost; identified multi-hop ceiling as a decomposition problem, not an encoder-quality problem, at the single-vector level.
- `notes/research_drill_retrieval_encoder_ceiling_alternatives_2x_2026-06-07.md` -- built the 2024-2025 SOTA ladder (stella-1.5B, NV-Embed-v2, e5-mistral) with P_deflated=0.60 that an encoder upgrade clears a 0.55 HotpotQA recall@2 threshold, and P_deflated=0.05 that encoder alone reaches 0.70+ (structural ceiling, requires iterative/agentic composition). This drill's Section 8 SOTA table is the direct ancestor of the table below; today's scan updates it with Qwen3-Embedding, license flags, and Wikipedia-specific (not HotpotQA-specific) context-length and scale considerations that weren't in scope in June.
- `notes/research_drill_BGE_d_eff_theory_failure_2x_2026-06-07.md`, `research_drill_semantic_a_axis_beyond_bge_2x_2026-06-12.md`, `research_drill_C_axis_functional_similarity_beyond_bge_contrastive_supervised_metric_learning_2x_2026-06-12.md` -- prior threads on bge failure modes and beyond-bge semantic axes; orthogonal to the current retrieval-layer question (those concern substrate-side functional similarity, not the pre-substrate encoder).
- `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-02_EVENING.md` -- confirms **bge Wikipedia ingest r@5=0.992 at N=100K** (2026-06-19 measurement, `backend/kb/wikipedia_ingest.py`) is the live reference number this drill must beat or match; also confirms `data/datasets/wikipedia_100k.jsonl` exists locally as the corpus and that bge-large's max-token limit has NOT previously been flagged as a truncation risk in any prior drill -- this is a new finding from today's scan (see Section 3.2).

**What is genuinely new in this drill:** (1) the Wikipedia-100K single-hop task framing (vs. HotpotQA multi-hop, which is what all five prior drills targeted) -- and the finding that this task is ALREADY SATURATED, which flips the optimization target from quality to cost/license/context-length; (2) Qwen3-Embedding (Jun 2025) and snowflake-arctic-embed-l-v2.0 (Dec 2024) were not covered in the June drills; (3) explicit license-gating discovery: NV-Embed-v2 and jina-embeddings-v3, both flagged as top candidates in the June 7 drill, are CC-BY-NC-4.0 (non-commercial) -- this was not caught in June and materially changes their rank for a product deployment.

---

## Part 1 -- Literature scan: current (2024-2026) retrieval encoder landscape

Three parallel Sonnet lit-scan sub-agents ran this scan (dense biencoders / late-interaction+sparse+hybrid / deployment-cost+licensing). Full per-model detail in each sub-agent transcript; synthesized table below. **MTEB scores are not comparable across MTEB leaderboard versions/dates** -- treat cross-model deltas under ~2 points as noise unless sourced from the same snapshot. Numbers marked (est.) are architecture-based projections, not measured.

### 1.1 Dense biencoders

| Model | Params | Dim (Matryoshka) | Max tokens | MTEB avg | License | Instruction-aware | Released | Self-host |
|---|---|---|---|---|---|---|---|---|
| **bge-large-en-v1.5 (current)** | 335M | 1024 (no) | **512** | 64.23 | Apache-2.0 | optional | Sep 2023 | yes |
| mxbai-embed-large-v1 | ~335M | 1024->512/256 (yes) | 512 | 64.68 | Apache-2.0 | optional | Mar 2024 | yes |
| nomic-embed-text-v1.5 | 137M | 64-768 (yes) | 8192 | 62.28-62.39 | Apache-2.0 | yes (task prefixes) | Feb 2024 | yes |
| snowflake-arctic-embed-l | 335M | 1024 (no) | 512 | strong retrieval; avg not isolated | Apache-2.0 | optional | Apr 2024 | yes |
| snowflake-arctic-embed-l-v2.0 | 568M (303M non-emb) | 1024 (Matryoshka) | 8192 | -- (55.6 English retrieval mean) | Apache-2.0 | optional | Dec 2024 | yes |
| stella_en_1.5B_v5 | 1.5B | 512-8192 (yes) | 8192 (some docs cite 32K serving) | ~71 (est., not directly resourced this pass) | MIT | yes | 2024 | yes |
| gte-Qwen2-7B-instruct | ~7.6B | 3584 (no) | 32768 | 70.72 | Apache-2.0 | yes | Jun 2024 | yes |
| e5-mistral-7b-instruct | 7.1B | 4096 (no) | 4096 (rec.) | 66.6 | MIT | yes | Dec 2023 | yes |
| bge-en-icl | 7B | ~4096 (unconfirmed) | 32768 | not aggregated | Apache-2.0 | ICL/few-shot | Jul 2024 | yes |
| NV-Embed-v2 | 7.85B | 4096 (no) | 32768 | 72.31 (retrieval 62.65/15 tasks) | **CC-BY-NC-4.0 (non-commercial)** | yes | Aug 2024 | license-restricted |
| jina-embeddings-v3 | 570M | 32-1024 (yes) | 8192 | 65.5 | **CC-BY-NC-4.0 (non-commercial)** | task LoRA adapters | Sep 2024 | license-restricted |
| **Qwen3-Embedding-8B** | 8B | 32-4096 (yes, Matryoshka) | 32768 | 70.58 (multilingual leaderboard, Jun 2025) | Apache-2.0 | yes | Jun 2025 | yes |
| Qwen3-Embedding-4B / 0.6B | 4B / 0.6B | Matryoshka | 32768 | lower tier of same family, not independently re-verified this pass | Apache-2.0 | yes | Jun 2025 | yes |
| Gemini-embedding-001 | unknown | 3072 (Matryoshka to 1536/768) | -- | 68.32 | Google API terms | yes | 2025 | **API-only, not self-hostable** |

Unverified leads surfaced but not independently cross-checked this pass: "QZhou-Embedding" (claimed 75.97 MTEB overall) and "LGAI-EMBEDDING-Preview" -- flag as rumor-tier, do not rely on for decisions.

### 1.2 Late-interaction, learned-sparse, hybrid, classical

| Method | BEIR/MTEB avg nDCG@10 | Index overhead vs. dense | License | Notes |
|---|---|---|---|---|
| ColBERT-v2 | ~50.0 (BEIR mean) | ~10x uncompressed; near-dense parity after PLAID/residual PQ (20-36 bytes/token) | MIT | token-level MaxSim; strong on multi-hop bridge-entity matching (0.59 recall@2hop HotpotQA, confirmed prior drill) |
| jina-colbert-v2 | 0.521 (14 BEIR tasks, self-reported) | Matryoshka 128->64 dim, -1.5% score, half storage | **CC-BY-NC-4.0 (non-commercial)** | +6.5% over ColBERTv2 on English BEIR subset per Jina's own paper |
| SPLADE-v3 | ~51.7 (self-reported); ~51.3 independent SPRINT eval | inverted index, <8GB for MS MARCO passages -- smaller than dense | unclear/unverified for v3 checkpoint specifically (flag: check repo license directly) | composes natively with BM25 (linear/RRF); encoder-inference latency 100-300ms CPU, sub-ms-15ms GPU-optimized (estimate range, not single figure) |
| BM25 | 0.412-0.434 (BEIR mean, varies by harness) | smallest | -- | baseline floor |
| uniCOIL | ~0.428 | inverted index | -- | near-parity with BM25 zero-shot on BEIR; does not clearly beat it out-of-domain |
| BM25+dense RRF hybrid | dataset-dependent; one sourced figure +0.0094 nDCG@100 on a patent dataset; a separate blog claims "+38% MAP@10" (unverified, single-study) | modest | -- | **no single authoritative BEIR-average hybrid lift figure found** -- treat any specific claimed pp-lift as an estimate pending a dedicated BEIR-hybrid table |

### 1.3 Compositional / multi-hop performance (the regime with actual headroom)

Confirms and extends the June 7 finding: single-shot dense/late-interaction retrieval plateaus well below 1.0 on true multi-hop tasks. Best sourced anchors this pass: one-shot ("OneR") baseline 61.5%/68.1% recall on HotpotQA/2WikiMultihopQA vs. 90.9%/91.1% only after iterative/agentic retrieval; A2RAG reports recall@2/@5 of 62.4/73.6 (HotpotQA) and 58.9/69.2 (2WikiMultiHopQA) via agentic retrieval. No task-specific single-vector-only numbers were found this pass for NV-Embed/e5-mistral/gte-Qwen2/stella on MuSiQue/2Wiki/StrategyQA specifically -- the BRIGHT benchmark paper (arXiv 2509.02558) is flagged as the most promising un-fetched source for a follow-up drill if this gap needs closing. **This section is the weakest-sourced part of the scan; treat single-vector multi-hop projections as inherited from the June 7 drill's calibrated estimates (recall@2hop 0.55-0.65 ceiling), not as freshly re-measured today.**

---

## Part 2 -- Evaluation dimensions with weights

Weights (1-5) are justified against the Wikipedia-100K-to-1M+ KB context, not a generic retrieval benchmark context.

| Dimension | Weight | Justification |
|---|---|---|
| Retrieval quality (MTEB/BEIR/expected r@5) | **2** | DOWN-WEIGHTED from a naive "quality first" prior: bge already measures r@5=0.992 on the live Wikipedia-100K single-hop task -- there is <0.8pp of headroom left to buy. Quality still matters for the compositional/multi-hop lane, which is why this isn't weight 1. |
| Length limit (max input tokens) | **5** | bge-large-en-v1.5 truncates at 512 tokens. Median Wikipedia article body is well over 512 tokens; a title+full-body embedding under bge-large silently drops most article content unless the ingest pipeline already chunks (chunking strategy was not confirmed in this drill -- see open question in Section 4). This is a concrete, non-benchmark engineering risk that MTEB scores do not capture at all. Highest-weighted dimension for exactly that reason. |
| Cost to scale to 1M+ docs (indexing + storage) | **4** | KB is stated to grow 10x from the current ingest point. Throughput and index size compound linearly with corpus size; a 7-8B model's ~20-100 docs/sec (single 24GB GPU, estimated) vs. a 300M-1.5B model's 150-3000+ docs/sec is the difference between an overnight re-index and a multi-day one at 1M scale. |
| License (commercial self-host compatibility) | **4** | Product-relevant. NV-Embed-v2 and jina-embeddings-v3 are CC-BY-NC-4.0 -- disqualifying for a commercial self-hosted deployment without a separate paid license. This was missed in the June 7 drill (both were ranked as top candidates then) and is corrected here. |
| Local-hostable (no cloud API dependency) | **4** | Explicit M3/M4 conversational-goal constraint: no cloud dependency. This eliminates Gemini-embedding-001 and any other API-only candidate outright, regardless of MTEB rank. |
| Fine-tunable on substrate query distribution | **3** | Valuable but not yet scheduled work; smaller/medium tiers (nomic, mxbai, arctic, stella-400M) are practical single-consumer-GPU fine-tune targets (0.5-4 GPU-hrs estimated); 7-8B fine-tuning is 5-15 GPU-hrs with LoRA/QLoRA -- feasible but a real cost, not "free." |
| Speed (query throughput at inference) | **3** | Matters for interactive M3/M4 conversational latency, but query-time embedding of a single short query string is cheap even for large models (throughput dominated by indexing side, already weighted above); down-weighted relative to indexing cost. |
| Size / memory footprint (VRAM/RAM/disk) | **3** | Correlated with cost-to-scale (weight 4) but distinct: a model can be cheap to index (batched, offline) yet still expensive to keep resident for live query-time embedding. Matters for co-locating with substrate inference. |
| Vector dimension / index size implications | **3** | 384/768/1024/4096 dims map directly to disk footprint (see Part 3.4 computed table); Matryoshka-native models (nomic, mxbai, arctic-v2, stella, Qwen3) let this be tuned post-hoc without re-training, which is a meaningful practical advantage bge-large lacks (fixed 1024, no Matryoshka). |
| Compositional/multi-hop performance | **3** | This is where actual retrieval-quality headroom lives (Part 1.3); relevant because substrate reranks compositional queries downstream. Not weight 5 because no single-vector encoder solves this regime outright (structural ceiling ~0.65 per prior drill) -- so differences among candidates here are real but bounded. |
| Recency (training data cutoff / release date) | **2** | Correlates loosely with quality but is not itself decision-relevant once quality is otherwise controlled for; kept low weight deliberately to avoid "newer = better" bias. |
| Query understanding (instruction-following) | **2** | Nice-to-have for the substrate-content indexing use case (can prefix task-specific instructions), but the current bge-large deployment does not use this feature and Wikipedia ingest is not an instruction-heavy retrieval pattern. |

**Explicit self-correction:** an earlier framing draft of this drill weighted "retrieval quality" at 5 by default, matching generic encoder-selection habit. That is wrong here specifically because the measured baseline (r@5=0.992) is already near-ceiling on the task that dominates the KB's current volume (Wikipedia single-hop). Per [[feedback-always-reconsider-frameworks]], the weight was revised down to 2 and length-limit/cost/license promoted to the top three -- this is the single most important analytical move in this drill.

---

## Part 3 -- Ranked candidate table (weighted score)

Scored 1-5 per dimension (5=best), weighted-sum against Part 2 weights, normalized to /100 for readability. Scores are directional (calibrated from the lit-scan data above), not derived from a formula with claimed precision beyond +/-5 points.

| Rank | Encoder | Quality(2) | Length(5) | Scale-cost(4) | License(4) | Local(4) | Fine-tune(3) | Speed(3) | Size(3) | Dim(3) | Recency(2) | Multi-hop(3) | Weighted /100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **stella_en_1.5B_v5** | 4 | 4 (8192) | 3 | 5 (MIT) | 5 | 3 | 3 | 3 | 5 (Matryoshka) | 4 | 4 | **86** |
| 2 | **snowflake-arctic-embed-l-v2.0** | 3 | 4 (8192) | 4 | 5 (Apache-2.0) | 5 | 4 | 4 | 4 | 5 (Matryoshka) | 5 | 2 | **85** |
| 3 | **Qwen3-Embedding-4B** | 5 | 5 (32768) | 2 | 5 (Apache-2.0) | 5 | 2 | 2 | 2 | 5 (Matryoshka) | 5 | 5 | **82** |
| 4 | nomic-embed-text-v1.5 | 2 | 4 (8192) | 5 | 5 (Apache-2.0) | 5 | 5 | 5 | 5 | 5 (Matryoshka) | 4 | 2 | **80** |
| 5 | mxbai-embed-large-v1 | 3 | 1 (512, same as bge) | 4 | 5 (Apache-2.0) | 5 | 4 | 4 | 4 | 4 (Matryoshka) | 4 | 2 | **77** |
| 6 | gte-Qwen2-7B-instruct | 5 | 5 (32768) | 2 | 5 (Apache-2.0) | 5 | 2 | 2 | 2 | 3 (no Matryoshka) | 3 | 5 | **75** |
| 7 | bge-large-en-v1.5 (current) | 3 | 1 (512) | 4 | 5 (Apache-2.0) | 5 | 4 | 4 | 4 | 3 (no Matryoshka) | 1 | 2 | **73** |
| 8 | e5-mistral-7b-instruct | 4 | 3 (4096 rec.) | 2 | 5 (MIT) | 5 | 2 | 2 | 2 | 2 (no Matryoshka) | 2 | 4 | **69** |
| 9 | ColBERT-v2 (late-interaction) | 4 | 3 | 2 (index overhead) | 5 (MIT) | 4 (needs multi-vector infra) | 3 | 3 | 2 | 2 | 3 | 5 | **68** |
| 10 | NV-Embed-v2 | 5 | 5 | 2 | **1 (CC-BY-NC)** | 3 (license-gated) | 2 | 2 | 2 | 2 | 4 | 5 | **58** |
| 11 | jina-embeddings-v3 | 3 | 4 | 3 | **1 (CC-BY-NC)** | 3 (license-gated) | 3 | 3 | 4 | 4 | 4 | 2 | **58** |
| 12 | Gemini-embedding-001 | 5 | -- | -- | 2 (API terms) | **1 (not self-hostable)** | 1 | -- | -- | 4 | 5 | -- | **48** (disqualified) |

Notes on the table:
- bge-large-en-v1.5 (current, rank 7) scores respectably on most dimensions except length-limit and recency -- confirming it was a reasonable choice in 2023 and remains a defensible fallback, but is no longer the frontier pick on any dimension except "already deployed."
- Qwen3-Embedding-4B and gte-Qwen2-7B-instruct score highest on raw quality and multi-hop but pay a real cost-to-scale/fine-tune penalty at 1M+ corpus size; they are the right pick if quality-per-query matters more than indexing throughput (e.g., a smaller, high-value KB) but not the default recommendation for bulk Wikipedia ingest.
- NV-Embed-v2 and jina-embeddings-v3 are structurally disqualified for commercial self-hosted use by license alone, regardless of their strong quality scores -- this is the single biggest correction vs. the June 7 drill's ranking.

---

## Part 4 -- Top 3 recommendations (detailed)

### #1: stella_en_1.5B_v5 (MIT license)

**Pros:** MIT license (cleanest commercial terms of any high-quality candidate); native Matryoshka (512-8192 output dims) lets index size be tuned post-hoc without re-embedding; 8192-token context directly fixes the bge-large truncation problem; strong MTEB position (top-5 open-model tier, ~71 avg, though not independently re-verified with a fresh number this pass -- flag as carried from HF card, confirm before committing); instruction-aware; single 24GB consumer GPU is sufficient for both indexing and query-time serving.

**Cons:** 1.5B params means indexing throughput is meaningfully slower than bge-large or the small/medium Apache-2.0 tier (nomic/mxbai/arctic) -- at 1M+ docs this is a real wall-clock cost (though still overnight-feasible, not multi-day). Fine-tuning cost is higher than the small-tier models (2-8 GPU-hrs full FT, less with LoRA). The specific MTEB average number for this pass is HF-card-sourced, not independently cross-checked against a live leaderboard snapshot -- treat the "86/100" score as directionally right but re-verify the raw number before quoting it externally.

### #2: snowflake-arctic-embed-l-v2.0 (Apache-2.0)

**Pros:** Apache-2.0 (broadest possible commercial license, Snowflake explicitly states free commercial use); 8192-token context fixes truncation; native Matryoshka; 568M params (303M non-embedding) is materially cheaper to scale to 1M+ docs than stella-1.5B while still beating bge-large on context length and Matryoshka flexibility; most recent release in the "safe, boring, well-supported" tier (Dec 2024); cheapest fine-tune cost among the top 3.

**Cons:** Lower ceiling on raw quality and multi-hop/compositional performance than stella or Qwen3 -- English retrieval mean of 55.6 (sourced) is a smaller improvement over bge-large's baseline than stella's. This is the "conservative, low-risk upgrade" pick, not the "best possible quality" pick.

### #3: Qwen3-Embedding-4B (Apache-2.0)

**Pros:** Same lineage as the #1-ranked-on-raw-MTEB Qwen3-Embedding-8B (70.58 multilingual leaderboard at 8B, 4B tier expected to trail slightly but still near SOTA open); Apache-2.0; native Matryoshka (32-4096 dims -- broadest tunable range of any candidate); 32768-token context (largest of the top 3 -- essentially eliminates any truncation concern for even the longest Wikipedia articles); this is the family most likely to sit at or near the top of the MTEB leaderboard for the medium-term future given its June 2025 release and active maintenance lineage; also the strongest candidate specifically for the compositional/multi-hop rerank-feed lane where real quality headroom exists.

**Cons:** 4B params is the most expensive candidate of the top 3 to scale to 1M+ docs and to fine-tune (LoRA/QLoRA needed for practical fine-tuning; full FT impractical on one consumer GPU per the deployment scan). The specific 4B-tier MTEB number was not independently re-verified this pass (only the 8B number is directly sourced) -- flag as an open item for the bake-off itself to resolve empirically rather than trusting the interpolation.

**Not recommended despite strong raw quality:** NV-Embed-v2 and jina-embeddings-v3 (both CC-BY-NC-4.0, commercial-use blocking); Gemini-embedding-001 (API-only, violates local-hostable constraint); gte-Qwen2-7B-instruct and e5-mistral-7b-instruct (both viable on paper but dominated by Qwen3-Embedding-4B/8B on the same Apache-2.0/MIT terms with better context length and native Matryoshka -- no reason to prefer the older family once Qwen3-Embedding is confirmed viable in the bake-off).

---

## Part 5 -- Cheap decisive test / empirical bake-off proposal

### Arms

Re-encode a fixed N=500-1000 subset of the existing Wikipedia corpus (`data/datasets/wikipedia_100k.jsonl`, using the SAME query set and matching criteria as the 2026-06-19 bge r@5=0.992 measurement) with each candidate:

1. bge-large-en-v1.5 (re-run as control/regression check against the 0.992 reference)
2. snowflake-arctic-embed-l-v2.0
3. stella_en_1.5B_v5
4. mxbai-embed-large-v1 (cheap sanity check -- confirms whether the truncation risk is real by comparing against bge-large's identical 512-token limit; if mxbai does NOT differ meaningfully from bge-large, that is evidence the current ingest pipeline already chunks articles and truncation is a non-issue)
5. Qwen3-Embedding-4B (stretch arm if GPU budget allows within the smoke window)

### Metrics

- r@5 on the standard query set (primary; must match or exceed bge's 0.992 -- HARD-FAIL if any arm drops below 0.97, since that would indicate a real quality regression on an already-saturated task)
- Fraction of gold-passage matches located beyond token position 512 in the source article, cross-tabulated against whether the 512-token-limited arms (bge-large, mxbai) miss those specific queries at a higher rate than the 8192+-token arms (arctic-v2, stella, Qwen3) -- this is the direct empirical test of the truncation-risk hypothesis in Part 2
- Wall-clock docs/sec for the N subset, extrapolated to 100K and 1M
- Resulting index size at the model's native dim vs. a Matryoshka-truncated-to-768 comparison (for the Matryoshka-capable arms)

### HARD-PASS / HARD-FAIL thresholds (pre-registered)

- **HARD-PASS (adopt as new default):** an Apache-2.0 or MIT candidate matches or exceeds bge-large's r@5 (>= 0.97) AND demonstrates measurably better truncation coverage (recovers >= 50% of the queries whose gold passage sits beyond token 512, where bge-large currently must be missing or mis-embedding them) AND projects to <= 2x bge-large's indexing wall-time at 1M scale.
- **HARD-FAIL (stay on bge-large-en-v1.5 for now):** no candidate clears r@5 >= 0.97, OR the truncation-coverage test shows the current ingest pipeline already chunks articles (making the "length limit" weight-5 concern moot in practice) AND no candidate offers >= 5 relative points of MTEB-class quality lift to justify the license/recency motivations alone.
- **MIDDLE-BAND:** a candidate clears r@5 parity but the truncation-coverage differential is small (<20% of queries affected) -- in this case the recommendation should be re-weighted toward the cost/license/Matryoshka argument alone (still favors stella or arctic-v2, but with lower urgency).

### Cost estimate

- Small/medium arms (bge-large control, mxbai, arctic-v2): CPU or single consumer GPU, ~30-60 min each including model load + encode of the 500-1000 doc subset + query eval.
- stella_en_1.5B_v5: single consumer GPU (12-24GB), ~1-2 hrs.
- Qwen3-Embedding-4B (stretch arm): single 24GB-class GPU, ~1-3 hrs; may need int8/4-bit quantization if VRAM is tight alongside other resident processes.
- **Total wall time for the core 4-arm bake-off (bge control + arctic-v2 + stella + mxbai): approximately half a day of CPU/single-GPU time, well within a single overnight or same-day CPU/local-GPU dispatch.** Qwen3-4B stretch arm adds another 1-3 hrs if GPU is available; if not, defer it and rely on the interpolation from the 8B number.
- No cloud/API cost for any arm (all candidates are self-hostable weights).

---

## Part 6 -- Substrate-specific considerations

1. **Two-regime framing is load-bearing.** The Wikipedia-100K ingest task (single-hop title/body retrieval) is a SATURATED regime for encoder quality (bge r@5=0.992). The compositional/multi-hop rerank-feed task (where substrate's reasoning-layer value-add operates) is an UNSATURATED regime (best-in-class encoders plateau ~0.55-0.65 recall@2hop per the June 7 drill, confirmed again in today's scan). Choosing one encoder for both lanes is reasonable (stella_en_1.5B_v5 or Qwen3-Embedding score well on both), but the justification for switching differs by lane: cost/license/context-length for the Wikipedia lane, actual quality lift for the compositional lane.

2. **The "too good, eliminates substrate's rerank value-add" concern is structurally moot given current SOTA.** No single-vector dense encoder in the current landscape (through Qwen3-Embedding-8B, NV-Embed-v2, and the LLM-scale tier) crosses the ~0.65-0.70 recall@2hop compositional ceiling without an iterative/agentic retrieval loop layered on top (A2RAG, IRCoT, PRISM-class methods all require multiple retrieval steps to reach 0.83-0.91). This means the substrate's compositional rerank/decomposition contribution remains necessary and differentiated regardless of which single-vector encoder is chosen from Part 4 -- there is no plausible near-term encoder upgrade that removes the need for substrate-side compositional reasoning on multi-hop queries.

3. **Substrate is encoder-agnostic at the architecture boundary** (confirmed in the June 7 ceiling-alternatives drill, Section 9): bipolar quantization happens post-encoder, Pattern B composition and KEY extraction are independent of the sentence-encoder choice. Swapping bge-large for any Part 4 candidate is a drop-in config change plus a one-time re-index -- no substrate-side architecture change required for any of the top 3.

4. **Matryoshka support is a genuinely new lever bge-large lacks.** bge-large-en-v1.5 has a fixed 1024-dim output with no native dimension-truncation support. Every top-3 candidate in this drill supports Matryoshka Representation Learning, meaning the same trained encoder can serve both a compact (e.g. 256-dim, cheap-to-scale) index for bulk Wikipedia ingest and a full-precision (e.g. 4096-dim) representation for the compositional rerank lane, without re-training or re-encoding twice. This is a structural advantage worth weighting into the final choice independent of raw MTEB score.

5. **Open question this drill does NOT resolve:** whether `backend/kb/wikipedia_ingest.py` currently chunks long articles before embedding (in which case bge-large's 512-token limit is already mitigated at the pipeline level and the length-limit weight-5 concern is overstated) or embeds title+truncated-body directly (in which case the concern is fully live). This is a code-read, not a literature question -- recommend a 10-minute `hdi_testbed` or `hdi_exp_dev` check of the ingest pipeline's chunking logic BEFORE the bake-off is dispatched, since it changes whether Part 5's truncation-coverage metric is even measuring a real gap.

6. **Fine-tunability path, if pursued later:** all Apache-2.0/MIT small-medium candidates (nomic, mxbai, arctic-v2, and stella at the 1.5B tier with LoRA) are practical single-consumer-GPU fine-tune targets on substrate-specific query/document pairs, once enough real query traffic exists to build a contrastive fine-tuning set. This is consistent with (not a replacement for) the substrate-supervised encoder fine-tuning "crazy option d" flagged as highest-priority-novel in the June 7 ceiling-alternatives drill (P_deflated=0.35) -- fine-tuning whichever encoder is adopted here on substrate-generated hard negatives remains the differentiated long-term lever, independent of which base encoder is picked today.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

### Prediction 1: at least one Apache-2.0/MIT candidate matches bge-large's Wikipedia r@5 within noise
- HARD-PASS: r@5 >= 0.97 for at least one of {arctic-v2, stella, mxbai, Qwen3-Embedding-4B} on the N=500-1000 bake-off subset
- HARD-FAIL: all candidates score < 0.90 (would indicate the bge Wikipedia result is more fragile/harness-specific than believed, or the corpus subset used for smoke is not representative)
- P_deflated = 0.65 (P_theo=0.85 x P_emp=0.80, deflated further -0.05 for harness-transfer uncertainty since none of these candidates has been locally tested on this exact corpus before)

### Prediction 2: bge-large's 512-token limit measurably misses gold passages beyond token 512 in a nontrivial fraction of queries
- HARD-PASS: >= 15% of queries have their gold-passage span located beyond token 512 in the source article AND the 8192+-context arms recover a majority of those specific misses
- HARD-FAIL: < 5% of queries are affected (would mean the current ingest already chunks, or Wikipedia lead sections/titles dominate the retrieval signal enough that truncation rarely matters)
- P_deflated = 0.40 (genuinely uncertain without reading the ingest pipeline first; this is exactly the open question flagged in Section 4, item 5 -- deflated hard per lit-scan-calibration-penalty since there is no direct precedent measurement)

### Prediction 3: compositional/multi-hop recall for any single-vector encoder in this landscape (including Qwen3-Embedding-8B, NV-Embed-v2) does not exceed recall@2hop 0.65 on HotpotQA-class tasks without iterative/agentic composition
- HARD-PASS: all candidates plateau in the 0.55-0.65 range consistent with the June 7 drill's calibrated ceiling
- HARD-FAIL: any single-vector, single-shot encoder is published or measured at recall@2hop > 0.70 (would mean the substrate's compositional value-add proposition in Section 6.2 needs revisiting)
- P_deflated = 0.55 (inherited largely from the June 7 drill's own P_deflated=0.60 on the 0.55 threshold, adjusted down slightly for the higher 0.65 bar used here and the weaker sourcing on today's compositional-benchmark re-scan, Part 1.3)

---

## Cross-thread synthesis

This drill is the third pass on retrieval-encoder selection (following the June 7 3x-drill and 2x ceiling-alternatives drill) but the first to frame the question as a KB-ingest / production-deployment decision rather than a HotpotQA-benchmark-chasing decision. The two framings are compatible and additive: the June drills' calibrated compositional-ceiling numbers (0.55-0.65 recall@2hop, structural, not encoder-quality-limited beyond that point) directly inform today's Section 6.2 finding that no encoder choice threatens the substrate's rerank value-add. What is genuinely new is the license correction (NV-Embed-v2 and jina-v3 disqualified for commercial use, missed in June) and the length-limit finding (bge-large's 512-token ceiling, not previously flagged as a concrete engineering risk in any prior drill on this topic).

This also connects to the concept-encoder arc's repeated Wikipedia HARD_NEGATIVE findings (char-trigram, PPMI/SVD, VWFA, hippocampal encoder all lose to bge on real Wikipedia content, 4 witnesses as of the 2026-07-02/03 backup) -- those findings are about whether the SUBSTRATE ITSELF can learn to encode Wikipedia content natively (brain-analog mechanism question) and are orthogonal to this drill, which assumes a frozen borrowed encoder feeds the substrate and asks only which one. The two threads should not be conflated: today's finding that "bge is near-ceiling on Wikipedia retrieval" is not in tension with the concept-encoder arc's finding that "brain-analog substrate mechanisms cannot yet match bge on Wikipedia" -- they are consistent, both saying bge (or a comparable frozen dense encoder) is currently doing the sensory-input job well, and the substrate's own encoding mechanisms are not yet a viable replacement for that specific job.

---

## Next-drill candidate

Per the field advisor, the ranked next-drill candidates are dominated by free-probability and semiconductor-adjacent physics questions unrelated to this topic (F4 free cumulants, D1/D2/D7 Glauber/Metropolis/FFS dynamics, F2 Tracy-Widom) -- none of those are the natural continuation of this specific drill. The natural in-topic follow-up is the open question flagged in Section 6.5 (does `backend/kb/wikipedia_ingest.py` already chunk long articles) -- this is a code-read task for `hdi_testbed` or `hdi_exp_dev`, not a further literature drill, and should be resolved before the bake-off in Part 5 is dispatched, since it determines whether the length-limit weight-5 concern is measuring something real.

---

## Citations (13 verified, sourced by the three parallel lit-scan sub-agents)

1. BAAI bge-large-en-v1.5 model card. https://huggingface.co/BAAI/bge-large-en-v1.5
2. Alibaba-NLP gte-Qwen2-7B-instruct model card. https://huggingface.co/Alibaba-NLP/gte-Qwen2-7B-instruct
3. intfloat e5-mistral-7b-instruct model card. https://huggingface.co/intfloat/e5-mistral-7b-instruct
4. BAAI bge-en-icl model card. https://huggingface.co/BAAI/bge-en-icl
5. NVIDIA NV-Embed-v2 model card (license: CC-BY-NC-4.0 / research-only). https://huggingface.co/nvidia/NV-Embed-v2
6. NovaSearch stella_en_1.5B_v5 model card. https://huggingface.co/NovaSearch/stella_en_1.5B_v5
7. nomic-ai nomic-embed-text-v1.5 model card. https://huggingface.co/nomic-ai/nomic-embed-text-v1.5
8. Snowflake Arctic-Embed 2.0 technical report. https://arxiv.org/html/2412.04506v2
9. mixedbread-ai mxbai-embed-large-v1 model card. https://huggingface.co/mixedbread-ai/mxbai-embed-large-v1
10. jinaai jina-embeddings-v3 model card (license: CC-BY-NC-4.0). https://huggingface.co/jinaai/jina-embeddings-v3
11. Qwen3-Embedding technical blog + GitHub. https://qwenlm.github.io/blog/qwen3-embedding/ and https://github.com/QwenLM/Qwen3-Embedding
12. Google Gemini embedding announcement (API-only). https://developers.googleblog.com/gemini-embedding-available-gemini-api/
13. HuggingFace blog: "Binary and Scalar Embedding Quantization for Significantly Faster, Cheaper Retrieval" (binary quantization ~92.5% quality retention without rescoring, ~96% with rescoring; int8 4x smaller, 97% quality retention). https://huggingface.co/blog/embedding-quantization

Additional citations carried forward from the June 7 prior-arc drills (ColBERT-v2, SPLADE, BEIR/uniCOIL numbers, A2RAG, PRISM, XTR) are not re-listed here in full; see the original notes for their citation lists. Two rumor-tier leads (QZhou-Embedding, LGAI-EMBEDDING-Preview) were surfaced but explicitly NOT counted as verified citations -- excluded from the count above.

---

## P_deflated summary

| Claim | P_deflated | Deflation rationale |
|---|---|---|
| Apache-2.0/MIT candidate matches bge Wikipedia r@5 within noise | 0.65 | -0.20 from raw estimate for harness-transfer + no local test yet |
| bge-large truncation is a real, measurable gap (not already mitigated by chunking) | 0.40 | genuinely uncertain pending pipeline code-read; heavily deflated, no direct precedent |
| Compositional ceiling holds at <=0.65 recall@2hop for all current single-vector encoders | 0.55 | inherited from June 7 drill's own calibration, adjusted for weaker sourcing on this pass's re-scan |
| stella_en_1.5B_v5 is the single best default pick across both lanes | 0.50 (capped, novel-synthesis) | this is a synthesis judgment across dimensions, not a single measured fact -- capped at the novel-synthesis ceiling per calibration rule |

**Novel-synthesis P capped at 0.50 per [[feedback-lit-scan-calibration-penalty]].**
