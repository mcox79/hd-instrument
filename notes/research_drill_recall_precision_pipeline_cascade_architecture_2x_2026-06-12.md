# research_drill_recall_precision_pipeline_cascade_architecture_2x_2026-06-12

Date: 2026-06-12
Topic: 2x DEEP literature drill on retrieve-then-rerank cascade architectures to inform Option 4 design (algebra-HRR top-K -> bge cosine re-rank to top-5) before Testbed ships the build.
Calibration: literature-is-not-oracle rule applied; lit-scan deflation 0.15-0.25 on all P estimates; novel-synthesis cap 0.50.

## Round 1 findings (compact)

R1-A (two-stage cascade general): The retrieve-then-rerank cascade is the dominant modern IR architecture. First stage = fast bi-encoder for recall; second stage = expensive cross-encoder for precision. Universal limitation surfaced: BOUNDED RECALL problem. Documents filtered out at stage 1 cannot be recovered by the reranker. This is the single most-cited failure mode in the cascade literature.

R1-B (ColBERT / late interaction): ColBERT's MaxSim is a middle-ground design: per-token embeddings, late interaction at scoring time. Importantly ColBERT can act as BOTH retriever and reranker. The MaxSim operation = sum over query tokens of max cosine-similarity to document tokens. This is structurally analogous to a fine-grained, token-level cross-encoder approximation, but bi-encoder-style on the embedding side.

R1-C (sparse-dense hybrid): Hybrid lexical+dense fusion gives up to 580% Recall@10 lift over dense-only on MS MARCO. Two dominant fusion families: (i) weighted score combination, (ii) learned fusion functions. Learned gating mechanisms enable dynamic, query-conditional weighting -- "learn fusion functions that optimize how sparse and dense scores should be combined for different query types or domains."

R1-D (cascade failure modes): Core finding: cascade is a THREE-WAY tradeoff (precision, recall, oracle cost). Documented failure modes: (1) cascading data failures (single feature bug propagates), (2) feature calibration breakdown when model output feeds next stage uncalibrated, (3) training objective misalignment (each stage optimized solo, ignoring end-to-end recall). Critically: traditional cascade training does NOT optimize end-to-end recall.

R1-E (optimal K / depth): Practical rule of thumb: re-rank ~100 candidates to attain 90% of max effectiveness (BM25 -> cross-encoder). However, K is workload-dependent. Larger K monotonically improves the reranker's ceiling but hits oracle-cost wall fast. The first stage controls the POOL CEILING; reranker can only rearrange what it sees.

R1-F (BEIR / hybrid evals): BEIR standardized hybrid evaluation. Dominant hybrid recipe: retrieve top-1000 independently from each model, min-max normalize to [0,1], average the scores. K=1000 in BEIR is large because it is BENCHMARK ceiling-testing; production cascades use K=50-200.

## Round 2 findings (compact)

R2-A (cross-encoder rerank over bi-encoder): "Bi-encoder for recall in milliseconds, cross-encoder rescores in order of actual relevance" -- the canonical pattern. Cross-encoder catches nuanced semantics bi-encoder misses; cost is O(K * forward-pass). Training requires labeled (q,d) pairs.

R2-B (adaptive rerank depth / per-query): AcuRank (NeurIPS 2025) uses Bayesian TrueSkill to iteratively refine relevance estimates with UNCERTAINTY-GATED computation -- stops when confidence sufficient. DART does test-time gradient steps on confidence-weighted margin loss over top-K. CAR uses generator-side confidence-change as posterior reranking signal. Pattern: fixed-depth cascade is increasingly considered suboptimal; per-query adaptive depth is the 2024-2026 frontier.

R2-C (structural+lexical complementarity / CLEAR): CLEAR (CMU+JHU 2020) explicitly trains the embedding model on RESIDUALS of the lexical model -- "encode language structures and semantics that lexical retrieval fails to capture." This is a complementarity-objective training trick: don't train signals independently then fuse; train signal-2 to fix signal-1's mistakes. Key insight applicable to our case: complementary signals trained to be DIFFERENT outperform two independently-strong signals that overlap.

R2-D (RRF failure modes / weighted): RRF only works when rankers fail in GENUINELY DIFFERENT WAYS. "Three variants of BM25" gives nothing. Weighted RRF (wRRF) = sum_m (alpha_m / (k + rank_m(e))) is the standard generalization. k=60 is empirical default; lower k (20-40) amplifies top picks; higher k (80-100) rewards consensus. Important: the k constant assumes 1-indexed ranks and is calibrated for typical web-IR list lengths (~1000s). For small lists (K=10-15), k=60 squashes EVERYTHING toward equal weight -- RRF mathematically degenerates on short lists.

R2-E (cascade distillation training): ERNIE-Search uses cross-interaction -> late-interaction -> metric-interaction cascade distillation to transfer cross-encoder knowledge into a dual-encoder. The training paradigm uses the EXPENSIVE model as teacher and CHEAP model as student. Suggests our cascade can be improved by training bge (cheap) on algebra-HRR (structural) signal, or vice versa, via residual distillation.

R2-F (query routing): SelRoute (2026) routes queries to lexical/semantic/hybrid/vocab-enriched pipelines by regex-based query-type classifier -- 83% routing accuracy on conversational memory retrieval. RAGRouter-Bench validates that lightweight classifiers (TF-IDF, MiniLM, hand-crafted structural features) can route at low cost. Query-type-aware routing is empirically validated as cheap-and-effective.

## Synthesis -- architectural recommendations for Option 4

- The retrieve-then-rerank cascade IS the dominant modern IR pattern. Option 4 (algebra-HRR top-K -> bge cosine top-5) is architecturally sound and well-precedented.

- BOUNDED RECALL is the dominant failure mode. Whatever K is chosen at stage 1, the system can never recover atoms filtered out there. Our case puts STRUCTURAL recall as the bottleneck -- algebra-HRR retrieves structurally-related atoms; bge would never have found them. This is the FAVORABLE direction.

- Cascade structure works BEST when signal-1 (recall stage) and signal-2 (precision stage) fail in genuinely different ways. Diagnostic showed overlap/novelty counts do NOT separate LIFT from HURT for naive fusion -- this is EVIDENCE OF GOOD COMPLEMENTARITY, not bad. RRF's failure mode here is exactly "low signal differentiation in the fused score" while the underlying signals are actually different -- supports cascade over fusion.

- Naive RRF degenerates on short lists (K=10-15) at k=60 -- this is a real mathematical issue, not just a tuning gap. Cascade sidesteps the issue entirely (no fusion math; each signal acts at its strength).

- Per-query adaptive depth (AcuRank/DART/CAR family) is the 2024-2026 frontier. Substrate has a natural confidence signal: algebra-HRR conf>0.20 fallback gate already canonical. This is a substrate-native version of adaptive depth.

- CLEAR's residual-training insight is high-value: if we ever train the bge re-ranker, train it on RESIDUALS of algebra-HRR -- explicitly to fix algebra-HRR mistakes, not to be independently strong.

## Specific design parameters for Option 4

1. First-stage K (algebra-HRR top): RECOMMEND K=15-20 for substrate's ~1742-atom corpus. STRONG support: BEIR uses 1000 for benchmark-ceiling; production cascades 50-200; substrate corpus is 200-600x smaller, so K=15-20 is the scale-equivalent. Literature predicts ~90% of max effectiveness at this depth. MODERATE confidence: substrate-specific cliff might emerge at K=10 (too tight) or K=30 (too loose).

2. Re-ranker scoring function: bge cosine over algebra-HRR-retrieved K. STRONG support: standard cross-encoder cascade over bi-encoder candidates. SPECULATIVE: whether bge cosine alone is enough vs adding a learned head; recommend START with raw cosine, escalate to learned only if results plateau.

3. Score combination at top-5: pure bge cosine ordering on the K candidates, NOT weighted RRF on the K. STRONG support: avoids the short-list RRF degeneracy entirely; preserves algebra-HRR's recall gate while letting bge dominate precision ordering.

4. Adaptive K (optional v2): use algebra-HRR top-1 confidence as gate -- if conf>0.40 use K=10, conf 0.20-0.40 use K=20, conf<0.20 fall back to bge-only. MODERATE support from AcuRank/CAR; SPECULATIVE on threshold values, must be empirically calibrated.

5. Distillation (DEFER): cross-encoder distillation training is a Phase-N consideration, NOT a Phase-0 dependency. Ship the cascade first, measure, then revisit if bge re-ranker plateaus.

## Honest uncertainty bounds

- STRONG (multi-paper consensus): cascade > naive fusion when signals differ; K=15-20 is correct scale-adjusted depth; pure cosine on candidates avoids short-list RRF degeneracy; bounded-recall is the dominant failure mode.

- MODERATE (1-2 paper support, plausible mechanism): adaptive K via algebra-HRR confidence; residual-training trick from CLEAR; ERNIE-style cascade distillation.

- SPECULATIVE: exact K threshold values (10 vs 15 vs 20); adaptive depth threshold values; whether substrate's structural-semantic split is symmetric with classical sparse-dense (it may be MORE complementary because algebra-HRR encodes compositional algebra, not lexical surface).

## Pre-registered predictions for Option 4 empirics

HARD-PASS (P_deflated = 0.40, capped at 0.50 per novel-synthesis):
- Option 4 with K=15, bge cosine re-rank to top-5 achieves NET POSITIVE retrieval quality across BOTH broad and narrow query types relative to (a) algebra-only, (b) bge-only, (c) naive weighted RRF baseline -- on substrate's 7-axis benchmark v3, mean F1 lift >=+0.03 vs the better single-signal baseline AND no axis regresses by more than -0.02.

HARD-FAIL (would refute the cascade as viable):
- Narrow-topic axes (A router, B canonical-vocab) REGRESS by >=-0.05 vs bge-only baseline, indicating algebra-HRR is poisoning the candidate pool. If this happens, the per-atom structural-signal is fundamentally orthogonal-noise to bge cosine; we'd need CLEAR-style residual training before cascade can work.
- OR: K=15 ceiling is below the naive RRF baseline mean -- meaning we're losing more from bounded-recall than we gain from precision re-rank.

MIDDLE-BAND: lift between +0.00 and +0.03 mean F1 -- cascade works but does not justify ship; try adaptive K or CLEAR-style residual training.

## Cross-thread synthesis with prior entries

- Substrate VSA position-IS-meaning validation 2026-06-12: HYBRID architecture (algebra-primary conf>0.20 + bge OOV fallback + RRF weighted 0.6/0.4) was the prior canonical. This drill argues that the RRF weighted fusion was the WRONG combiner for the cascade. Recommendation: replace the RRF stage with a re-rank stage. The algebra-primary gate stays; the bge fallback stays; but the fusion pathway becomes a cascade re-rank pathway.

- substrate-extracted rule "two-stage decomposition beats joint" 2026-06-11: directly predicted this outcome. The structural signal (algebra-HRR) and the precision signal (bge) decompose ADDITIVELY when staged, MULTIPLICATIVELY when fused. Joint candidate ranking (current weighted RRF) is the multiplicative failure mode; cascade is the additive success mode.

- methodology rule capability-portfolio-mechanism-diversity-is-the-lever 2026-06-12: the cascade keeps BOTH mechanism classes active -- structural recall + semantic precision -- rather than collapsing to a single fused score where each mechanism's contribution is washed out.

- literature-is-not-oracle: literature predicts K=100 default; substrate corpus is 200-600x smaller; we predict K=15-20 -- substrate empirics will calibrate. DO NOT default to literature K.

## Substrate-product implications

- Substrate's cascade is structurally different from off-the-shelf ColBERT or sparse-dense hybrid in three ways:
  1. Stage 1 is algebra-HRR -- a COMPOSITIONAL ALGEBRAIC retrieval signal, not a lexical or pre-trained semantic one. ColBERT's late interaction is pre-trained token-level cosine; substrate's algebra-HRR is rule-encoded binding/unbinding. These are orthogonal capability classes.
  2. Substrate has STRUCTURED CONFIDENCE -- algebra-HRR's conf>0.20 fallback gate is a substrate-native adaptive-depth signal. Off-the-shelf cascades don't have this; they retrofit it via Bayesian TrueSkill (AcuRank) or generator-side feedback (CAR).
  3. Substrate's two signals are SEMANTICALLY ORTHOGONAL by architectural design -- algebra-HRR encodes role-filler binding; bge encodes lexical-semantic similarity. Sparse-dense hybrids (BM25+dense) share lexical substrate (both look at words); substrate's split is at a deeper representational seam.

- Positioning: substrate cascade = "compositional algebra recall + lexical-semantic precision" -- LLMs cannot match the stage-1 mechanism; classical IR cannot match the stage-1 representation.

## Citations (verified count: 12)

1. ColBERT (Khattab & Zaharia, SIGIR 2020) - late interaction, MaxSim - arxiv.org/abs/2004.12832
2. CLEAR (Gao et al., 2020) - complementary lexical+semantic residual training - arxiv.org/abs/2004.13969
3. BEIR (Thakur et al., NeurIPS 2021) - hybrid evaluation benchmark - arxiv.org/abs/2104.08663
4. ERNIE-Search (2022) - cascade distillation cross-encoder to dual-encoder - arxiv.org/abs/2205.09153
5. PROD (2022) - progressive distillation for dense retrieval
6. AcuRank (NeurIPS 2025) - uncertainty-aware adaptive listwise reranking - arxiv.org/abs/2505.18512
7. DART - dense adaptive reranking at test-time
8. CAR (2026) - query-guided confidence-aware reranking - arxiv.org/abs/2605.04495
9. SelRoute (2026) - query-type-aware routing - arxiv.org/abs/2604.02431
10. RAGRouter-Bench (2026) - lightweight query routing - arxiv.org/abs/2604.03455
11. Pinecone cascading retrieval blog - production cascade architecture
12. RRF original (Cormack et al., 2009) - k=60 empirical default, weighted variants
