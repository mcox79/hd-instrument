# exp_dev hand-off -- research: multi-hop retrieval precision closure

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: research drill deliverable (see notes/research_drill_multihop_precision_closure_3x_2026-06-07.md)
Pause state: respect data/orchestrator_paused.flag; do not dispatch if paused

Per [[feedback-no-experiment-design-in-prompts]]: this file names candidates and sequencing only. Exp-dev designs the actual experiment scripts.

---

## Anchor candidates (rank-ordered)

### 1. ColBERT-v2 bare pre-test (gating experiment)
- Anchor pointer: colbert_bare_hotpot_pretest
- Substrate-product reading: if recall@2 >= 0.55, this gates the full ColBERT integration path (2-3 week engineering); if < 0.50, gating hard-fail triggers benchmark pivot
- Tier hint: GPU runner (Ragatouille index build requires GPU); short wall ~2-3 hours
- Why now: this is the single highest-leverage untested experiment; all downstream ColBERT candidates gate on this result; no other path to 0.70 is available without it

### 2. BM25 + bge-small RRF hybrid pre-test
- Anchor pointer: bm25_dense_hybrid_hotpot_pretest
- Substrate-product reading: cheap +0.05-0.10 lift on recall@2; composites with Pattern B pair verification; improves coverage from 0.74 to ~0.80 recall@10 which is the input to substrate pair selection
- Tier hint: CPU runner; no GPU required; ~2-3 hours
- Why now: cheapest candidate (0.5-1 day); can run in parallel with queued substrate tests; provides floor lift regardless of other outcomes

### 3. Substrate Pattern B pair verification (already queued -- read verdict first)
- Anchor pointer: substrate_pattern_b_pair_verify (already in queue per task description)
- Substrate-product reading: if pair selection accuracy >= 0.55, this is the fast path to 0.60+ without ColBERT; if hard-fails, confirms substrate's role is answer-quality not retrieval precision
- Tier hint: read queued result before dispatching anything new on this path
- Why now: already queued; verdict arriving; do not re-queue; read the result and route accordingly

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_multihop_precision_closure_3x_2026-06-07.md
- Empirical state: bge-small recall@2 = 0.42; recall@10 = 0.74; cross-encoder, vector bridge, iterative K-hop, LLM-decomp 1.5B all hard-failed
- Pre-reg thresholds in research note: ColBERT HARD-PASS >= 0.55, HARD-FAIL < 0.50; BM25 hybrid HARD-PASS >= 0.52; Pattern B pair accuracy HARD-PASS >= 0.65

---

## Contract

Exp-dev reads this file and the research note. It designs the experiment scripts per its own protocol (smoke gate, pre-reg bands, queue_add). It does not ask the orchestrator for design approval; it ships.

## Autonomy declaration

Exp-dev has full autonomy to: sequence the three candidates above, design the pre-test scripts, set per-cell fail bands, and dispatch to the appropriate queue (GPU for ColBERT, CPU for BM25 hybrid). It should NOT dispatch LLM-decomp at 3B (candidate 1 in research note) -- the research note pre-registers this as expected-fail; it is not worth engineering time without a 50-question CPU pre-test first.
