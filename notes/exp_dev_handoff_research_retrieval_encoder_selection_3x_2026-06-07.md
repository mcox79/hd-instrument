# exp_dev hand-off -- research: retrieval encoder selection 3x drill

**Filed:** 2026-06-07 by research sub-agent
**Trigger:** notes/research_drill_retrieval_encoder_selection_3x_2026-06-07.md
**Pause state:** check data/orchestrator_paused.flag before dispatching

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, threshold bands, queue choice, anchor name, ETA, smoke profile. Research does NOT specify numerical parameters beyond what is in the pre-test protocol in the research note.

---

## What this drill found (summary for exp_dev)

Three anchor candidates are ready for empirical pre-test. They are sequenced cheapest-first per PROT-004. All are CPU-only. The research note documents the full stack ranking, P_deflated estimates, and pre-test protocols.

Key context:
- bge-small-en-v1.5 (33M) is confirmed as the production retrieval encoder (recall@2hop=0.42 bare, recall@10=0.74, substrate whitening does not add lift on this encoder)
- The HotpotQA 2-hop gap to 0.70 is a multi-hop reasoning problem, not a retrieval-coverage problem
- Facts ARE in the top-10 pool; similarity/ranking alone cannot select them; decomposition is required
- Three embedding-based multi-hop methods all tested and plateau at 0.34-0.40 (all below bge-small naive 0.42)

---

## Anchor candidates (rank-ordered; exp_dev picks from these)

### 1. Entity-bridge decomp pre-test (PRE-TEST A in research note)
- Anchor pointer: notes/research_drill_retrieval_encoder_selection_3x_2026-06-07.md, Part 3 Pre-test A
- Substrate-product reading: uses spaCy NER to extract the bridge entity from hop-1 passage, re-queries bge-small for the entity as a sub-question; tests whether entity-level decomp closes the recall@2hop gap from 0.42 toward 0.70; directly tests the K-hop relay concept
- Tier hint: CPU (spaCy NER + bge retrieval, no GPU needed)
- Why now: cheapest decisive test; 2hr CPU; $0; confirms whether NER decomp is sufficient or LLM-quality decomp is required; gates the LLM-decomp build decision

### 2. gte-base-en-v1.5 coverage comparison (PRE-TEST B in research note)
- Anchor pointer: notes/research_drill_retrieval_encoder_selection_3x_2026-06-07.md, Part 3 Pre-test B
- Substrate-product reading: same n=50 smoke as hotpot_substrate_bge_v1 but with gte-base-en-v1.5; tests whether moving to 110M pushes recall@10 above 0.74 (bge-small ceiling); relevant only if a higher-coverage encoder would change the decomp loop outcome
- Tier hint: CPU (same setup as existing bge-small smoke)
- Why now: 1hr CPU; $0; quick confirmation of whether 110M is worth the overhead; if recall@10 stays below 0.78, bge-small is the answer and no encoder upgrade is needed

### 3. LLM-decomp loop (FINAL-FORM north-star experiment; after pre-tests A+B)
- Anchor pointer: notes/research_drill_retrieval_encoder_selection_3x_2026-06-07.md, Part 4 Prediction 4
- Substrate-product reading: small LLM (1B or 3B) splits a 2-hop question into two single-hop sub-questions; bge-small retrieves each; measures recall@2hop; this is the complete v1 demo recipe -- substrate K-hop relay + LLM decomposer + bge retrieval vs bare LLM
- Tier hint: GPU (LLM inference at scale; n=100)
- Why now: this is the north-star test; gates the v1 demo claim; sequenced AFTER pre-tests A and B to confirm the retrieval layer is solid before adding LLM complexity

---

## Context pointers

- Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_retrieval_encoder_selection_3x_2026-06-07.md
- Exp-Dev routing note (empirical ladder + 4 updates): d:/AI/hd-instrument/notes/exp_dev_to_research_URGENT_llama_not_retrieval_encoder_2026-06-07.md
- Cycle 156 smokes (bge vs MiniLM vs Llama-base): look up hotpot_substrate_bge_v1, hotpot_bge_recall_at_k_v1, hotpot_bge_rerank_v1 in queue history

---

## Contract

exp_dev is authorized to design and dispatch the pre-test anchors above. exp_dev decides:
- Exact n, threshold bands, queue routing, anchor naming
- Whether to batch pre-tests A+B together (both are CPU; batching saves setup time)
- Whether to skip pre-test B if A gives a HARD-PASS (then 110M comparison is unnecessary)

exp_dev is NOT authorized to:
- Re-run any Llama-1B-base retrieval tests (disqualified; waste of cycles)
- Design the LLM-decomp loop (anchor 3) before pre-tests A and B are complete
- Change the encoder away from bge-small without pre-test confirmation that an alternative is materially better

## Autonomy declaration

exp_dev owns all implementation details for these anchors. The research note provides theoretical bounds and P_deflated estimates; exp_dev converts those to concrete experiments.
