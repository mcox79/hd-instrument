# exp_dev hand-off -- research: iterative multi-hop reasoning, where it works (5x drill)

**Filed:** 2026-06-08 by research sub-agent.

**Trigger:** Research note at:
  d:/AI/hd-instrument/notes/research_drill_iterative_multihop_where_it_works_5x_2026-06-08.md

**Pause state:** CHECK `data/orchestrator_paused.flag` before dispatching queue-triggering experiments. Annotation-only actions (cap_map bumps, notes) are always allowed.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Research finding in one sentence

Iterative multi-hop works reliably when each hop is grounded in clean discrete signal (graph edges, explicit text, game state). It fails when grounded in cosine similarity over reformulated dense embeddings. Substrate's synthetic K-hop success and HotpotQA fuzzy-embedding failures are both predicted by this principle, confirmed across 32 citations spanning NLP, classical AI, KG QA, agentic systems, and cross-domain non-AI fields.

---

## Anchor candidates (rank-ordered; exp_dev picks per queue policy)

### 1. SUBSTRATE-KG-TRIPLES-KHOP -- real KG encoding and K-hop traversal
- Anchor pointer: Research note Section "Strategic Implications" item 1; also PP-11 (K=12 recovery = 0.987) as prior baseline.
- Substrate-product reading: encode a subset of a public KG (e.g., NELL-595 or Freebase-mini) as VSA entity-relation-entity triples. Run 2-hop and 3-hop queries. Measure recall@K against gold paths. This is the lowest-risk extension of what already works in synthetic clean-binding regime. If VSA triple encoding is faithful on real KG data, this opens KG QA as a substrate product capability.
- Tier hint: local CPU or Remote CPU (small KG subset, N=1024 or N=4096, no GPU needed at evaluation scale).
- Why now: PP-11 synthetic result is the green light. Real-KG pre-test is the gate before product claim. 1-2 hour local test per feedback-drill-pretest-required.

### 2. SUBSTRATE-BRIDGE-EXTRACTION-PIPELINE -- small LLM + substrate K-hop on HotpotQA
- Anchor pointer: Research note Section "Strategic Implications" item 2; BridgeRAG (arXiv 2604.03384) mechanism as reference design; IRCoT (ACL 2023) as structural template.
- Substrate-product reading: use Llama-3.1-8B (or Pythia-160M for Pythia-sanity-check-first) to extract the bridge entity from hop-1 results. Feed the named bridge entity as the explicit second-hop query into substrate retrieval. Measure recall@2 on HotpotQA dev. Expected: recall@2 jumps from current 0.31-0.37 to >= 0.55. This directly tests whether the failure was grounding-signal cleanness (fixable) or something else (not fixable without architecture change).
- Tier hint: Pythia-160M local pre-test first (3 min, $0). If Pythia confirms bridge extraction is working, escalate to Llama-3.1-8B run.
- Why now: 5 HFs today on fuzzy-embedding iterative; this is the principled rescue path with lit-validated mechanism (BridgeRAG April 2026 SOTA).
- MANDATORY: run Pythia sanity check per feedback-pythia-sanity-check-before-cloud before any cloud dispatch.

### 3. SUBSTRATE-PPR-SPREADING-ACTIVATION -- PPR-equivalent over substrate stored triples
- Anchor pointer: Research note Section "Strategic Implications" item 1 (PPR-style); HippoRAG (NeurIPS 2024) as reference architecture; Personalized PageRank spreading activation mechanism.
- Substrate-product reading: implement K-hop spreading activation over substrate triple store where each spreading step is a VSA K-hop lookup from seed entities. Measure convergence depth (K required for full coverage of 2-hop neighborhood) and retrieval recall@K. Directly analogous to HippoRAG's PPR over knowledge graph, but implemented entirely in VSA without a separate graph index.
- Tier hint: local CPU smoke first, then Remote CPU for scaling.
- Why now: HippoRAG shows PPR over graph equals or beats IRCoT iterative at 10-30x lower cost. Substrate's K-hop is already the same operation. Low-risk high-yield extension.

### 4. SUBSTRATE-BEAM-RETRIEVAL -- K-beam iterative chain over stored bindings
- Anchor pointer: Research note Section "Engineering-tractable extensions" item 7; Beam Retrieval (Zhang et al. 2023, +44.6% EM on MuSiQue).
- Substrate-product reading: maintain K=3 candidate partial chains in parallel. At each hop, expand each chain by one K-hop step, score by accumulated binding consistency, prune to K survivors. Directly mirrors Beam Retrieval's success on MuSiQue but implemented in VSA over stored triples.
- Tier hint: local CPU. Smoke with K=2, chains of length 2.
- Why now: Beam Retrieval's +44.6% EM gain is the largest single improvement on MuSiQue in the lit. The VSA implementation is deterministic and cheap to prototype.

### 5. SUBSTRATE-LEGAL-CITATION-DEMO -- citation tracing use case prototype
- Anchor pointer: Research note Section "Customer pitch updates" item 1; citation snowballing literature (SYMBALS, PMC 2021).
- Substrate-product reading: load ~500 paper citation records as VSA (paper_id, cites, paper_id) triples. Run forward/backward snowballing via K-hop: starting from a seed paper, retrieve all papers it cites (backward) and all papers that cite it (forward). Verify completeness against a known citation set. This is a customer-demo-grade prototype requiring no LLM, no fuzzy retrieval -- just substrate K-hop over clean bindings.
- Tier hint: local CPU. Very fast, no GPU needed.
- Why now: legal/medical citation tracing is a defensible near-term customer pitch where substrate's discrete-grounding advantage is real and demonstrable.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_iterative_multihop_where_it_works_5x_2026-06-08.md
- Prior multi-hop empirical context: production architecture note (notes/production_architecture_locked_2026-06-07.md)
- Post-compaction brief: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
- Multi-hop revive priority: memory file project_multihop_revive_priority.md
- PP-11 baseline (K=12 clean binding recovery = 0.987): referenced in evening brief cycles 170-175
- BridgeRAG reference paper: arXiv 2604.03384 (April 2026, best published training-free MHQA)
- HippoRAG reference paper: arXiv 2405.14831 (NeurIPS 2024, PPR-based KG retrieval)
- IRCoT reference paper: arXiv 2212.10509 (ACL 2023, +11-21 recall with LLM CoT bridge)

---

## Contract

exp_dev owns: anchor names, threshold bands, N/M/K parameters, queue routing, smoke gate, ship decision, post-ship remote verify.

Research owns: anchor candidates ranked by P_deflated, structural rationale, context pointers.

Orchestrator owns: pause gate check, cross-queue coordination, verdict routing after results.

---

## Autonomy declaration

exp_dev may dispatch any anchor from this list without further orchestrator approval, subject to:
1. Pause gate (data/orchestrator_paused.flag absent)
2. Pythia sanity pre-test BEFORE any cloud dispatch involving LLM integration (item 2 above)
3. Local CPU pre-test for items 1, 3, 4, 5 before Remote CPU or cloud escalation
4. Standard smoke gate (pre-reg threshold bands before dispatch)
5. Cost envelope: items 1, 3, 4, 5 are local CPU only; item 2 requires explicit cloud auth if Pythia pre-test passes and recalls justify escalation
