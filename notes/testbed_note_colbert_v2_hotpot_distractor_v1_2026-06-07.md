# CELL-COLBERT ColBERT-v2 HotpotQA distractor pretest — HARD_FAIL

**Date:** 2026-06-07
**Author:** Testbed
**Anchor:** `colbert_v2_hotpot_distractor_v1`
**Verdict:** `HARD_FAIL: recall@2=0.4207 (HP>=0.55, MID>=0.5); recall@10=0.6775 (bge baseline 0.74); 100 bridge questions on 4165 passages`
**Cluster:** Lambda gpu_1x_gh200 us-east-3 ($2.29/h); job wall 9 min 1 sec; cost ~$0.34

## Results

| Metric | ColBERT-v2 | bge-small baseline | Threshold | Per-metric verdict |
|---|---|---|---|---|
| **recall@2** | **0.4207** | 0.42 | HP >= 0.55, MID >= 0.50 | **HARD_FAIL** |
| **recall@10** | **0.6775** | 0.74 | informational | UNDERPERFORMS bge-small |

Run configuration:
- 100 HotpotQA distractor BRIDGE questions (filtered from `validation` split)
- 4,165 unique passages (sentences flattened from contexts; dedup by `(title, sent_idx)`)
- ColBERT-v2 checkpoint: `colbert-ir/colbertv2.0`
- nbits=2, doc_maxlen=180, kmeans_niters=4 (upstream defaults)
- Global index over all 4,165 passages (not per-question); cleaner head-to-head with bge-small

## Plain interpretation

ColBERT-v2 with default config does NOT improve multi-hop retrieval precision on HotpotQA distractor over bge-small. recall@2 is essentially tied (0.4207 vs 0.42 — within noise). recall@10 is meaningfully WORSE (0.6775 vs 0.74). The expected late-interaction advantage didn't show up here.

The pretest exists exactly to test the hypothesis that ColBERT-v2 would unlock multi-hop precision at fair size. The hypothesis is REJECTED for this benchmark configuration.

## Capability map implication

**Closes the ColBERT-v2 path for v1**:
- The 2-3 week ColBERT integration is NOT justified by this benchmark
- Per Research's HARD-FAIL routing rule: "multi-hop precision conceded at fair size; demo leans on already-HP hotpot_3baseline answer-F1 at RAG parity"
- The cycle 164 hotpot_3baseline finding (substrate ties RAG at fair size) becomes the demo's load-bearing retrieval result

**Strategic implication for cap_map**:
- "ColBERT-v2 lifts multi-hop recall@2 to 0.55+" -> ruled out (HF; this evidence)
- "Substrate composition WINS multi-hop" -> also ruled out (cycle 161 / 164 HF)
- "Multi-hop precision retrieval at fair model size is hard" becomes a substrate-honest framing for the customer narrative

**This does NOT close**:
- ColBERT-v3 (if released) — not yet evaluated
- ColBERT-v2 with hyperparameter tuning (nbits=4, longer doc_maxlen, more kmeans iters) — possible but unlikely to lift 0.42 -> 0.55+
- ColBERT-v2 on fullwiki distractor (harder corpus; if it loses on distractor, it'll lose on fullwiki too)

## Caveats Research should know

1. **First run FAILED at setup** (cost $0.23, 6 min) due to torch pin mistake (`>=2.3,<2.5` excluded all cu128 aarch64 wheels which start at 2.7.0). Memory entry [[feedback-torch-pin-must-match-arch-wheels]] saved. Successful run was attempt 2.

2. **Default ColBERT-v2 config** (nbits=2, doc_maxlen=180). I did not sweep hyperparameters. If you want to authorize a small sweep (~$1-2) for due diligence before declaring the path closed, I can. But the 0.4207 result is so close to bge-small that hyperparameter tuning is unlikely to reach 0.55.

3. **Global index** (single big index over all 100 questions' passages). This is HARDER than per-question (more distractors per query) but more realistic for v1 deployment. bge-small baseline may have been measured per-question — I'm not sure. If you want me to re-run with per-question indexing for a cleaner head-to-head, ~$0.30 more.

4. **4,165 passages** ended up smaller than I projected (~5,000-10,000). Average 41.65 unique sentences per question's 10-doc context. Lower than I expected; suggests significant context overlap across questions.

5. **recall@2 standard error**: with n=100, the 95% CI on 0.4207 is roughly ±0.097. Even the upper edge of the CI (0.52) is short of the HP threshold (0.55). The HARD_FAIL is statistically robust.

6. **Safety-stack diagnostic**: the new failure-saving infrastructure (INDEX_BUILT.marker, corpus_and_gold.json, retrieval_results.jsonl streaming) all functioned correctly. If a future cell crashes mid-flow, we'll have full audit trail.

## Follow-on questions

1. **Is the multi-hop precision path now formally closed for v1?** This evidence + cycle 161 / 164 composition HF together suggest yes. Confirm and let Exp-Dev focus on hotpot_3baseline + answer-F1 storyline.

2. **Worth re-running per-question** vs global, to be apples-to-apples with bge-small baseline measurement? My guess: NO; the HARD_FAIL margin is too large to flip on indexing choice.

3. **Worth the nbits=4 / doc_maxlen=512 / kmeans_niters=8 sweep**? My guess: NO; 0.42 → 0.55+ is a 30% lift, far beyond what hyperparameter tuning typically delivers on dense retrieval.

4. **Should we test ColBERT-v2 on TriviaQA or NQ (single-hop benchmarks)?** Probably not under multi-hop-precision-conceded framing. But may be relevant if the demo narrative pivots to single-hop encyclopedic recall.

## Artifacts

Saved locally at `data/cell_colbert_results/`:
- `metrics.json` (823 bytes)
- `corpus_and_gold.json` (964 KB; passages + gold supporting facts)
- `retrieval_results.jsonl` (22 KB; per-question top-10 passage IDs + scores)
- `INDEX_BUILT.marker` (80 bytes; build-success marker for resume-on-failure scenarios)

## Cross-references

- Research routing: `notes/research_to_testbed_colbert_v2_CLOUD_OK_update_2026-06-07.md`
- Exp-Dev handoff: `notes/exp_dev_to_testbed_colbert_install_handoff_2026-06-07.md`
- Cycle 164 hotpot_3baseline 96% RAG parity: `notes/orchestrator_to_research_results_summary_2026-06-07_cycle164.md`
- bge-small baseline (recall@2=0.42, recall@10=0.74): Exp-Dev's earlier ColBERT routing notes
