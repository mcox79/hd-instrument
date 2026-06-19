# exp_dev hand-off -- research: substrate as open-ended planner (2x drill)

**Filed-by:** research sub-agent
**Date:** 2026-06-08
**Trigger:** d:/AI/hd-instrument/notes/research_drill_substrate_planning_open_ended_2x_2026-06-08.md

**Pause state block:** CHECK `data/orchestrator_paused.flag` before dispatching any queue-triggering experiments. Annotation-only actions (cap_map bumps, notes) are always allowed.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHOR CANDIDATES + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Research finding in one sentence

Substrate's K-hop traversal maps directly onto forward-chaining in classical planning, one MCTS rollout step, beam retrieval for proof search, and episodic RL memory -- the single cheapest gate across all five domains is a 30-min local CPU test of K-hop on a real knowledge graph, which determines whether the synthetic clean-binding results transfer to real heterogeneous data.

---

## Anchor candidates (rank-ordered; exp_dev picks per queue policy)

### 1. SUBSTRATE-KG-PLANNING-GATE -- K-hop forward-chain on real KG triples (decisive gate)
- Anchor pointer: Research note Section "Cheap decisive test" and Cell P1.
- Substrate-product reading: encode 500-2000 entity-relation-entity triples from a public KG (NELL-595 subset or Wikidata-mini). Run 2-hop and 3-hop queries as forward-chain planning steps. Measure recall@1 and recall@10 against gold paths. This is the binary gate for the entire planning capability cluster: if it passes, 4 more planning anchors are authorized; if it fails, planning requires redesign before further engineering.
- Tier hint: local CPU. Very fast, no GPU needed. N=4096 or N=1024 smoke first.
- Why now: PP-119 (K=12, recall@1=0.987 synthetic) is the green light; real KG grounding is the gate. Costs $0 and <30 min. Every other planning cell depends on this gate.
- MANDATORY first: run this before any other planning-domain anchor.

### 2. SUBSTRATE-MCTS-VALUE-LOOKUP -- Q-value retrieval for toy grid planning
- Anchor pointer: Research note Section "Domain 2: Tree/graph search" and Cell P2.
- Substrate-product reading: encode (state, action, Q_value) triples for a small grid navigation task. At inference, retrieve Q-value for a query (state, action) pair via K-hop. Measure Q-value MAE and correct-state retrieval rate vs ground truth. Validates substrate as the value-lookup component inside an MCTS loop.
- Tier hint: local CPU smoke first. Small state space (16-64 states), no GPU needed.
- Why now: MCTS-RAG (arXiv 2503.20757, 2025) shows 20% improvement using retrieval inside MCTS. Substrate is the retrieval layer. Cheapest empirical validation of Domain 2.
- Gated by: SUBSTRATE-KG-PLANNING-GATE passing (Cell P1 HARD-PASS).

### 3. SUBSTRATE-LLM-HYBRID-VERIFIER -- substrate verifies LLM plan steps (GNNVerifier pattern)
- Anchor pointer: Research note Section "Domain 3: LLM + substrate hybrid planning" Pattern A and Cell P3.
- Substrate-product reading: on a toy sequential task (5-step blocksworld or instruction-following), LLM generates candidate next actions; substrate K-hop checks whether the action's preconditions are satisfied in the encoded current state. Compare task-completion rate and token usage vs LLM-only CoT. Validates the audit-chain planning product pitch.
- Tier hint: local CPU or Remote CPU. Pythia-160M for LLM component (Pythia-sanity-check-before-cloud rule applies). No cloud until Pythia smoke confirms bridge works.
- Why now: GNNVerifier (arXiv 2603.14730, 2026) and KG-Agent (2025) both validate the hybrid pattern at product scale. Substrate's version is cheaper and auditable.
- Gated by: SUBSTRATE-KG-PLANNING-GATE (Cell P1) and agentic-memory-layer Cell 1 (AUC >= 0.85) from notes/exp_dev_handoff_research_agentic_memory_layer_2x_2026-06-07.md.

### 4. SUBSTRATE-EPISODIC-RL-MEMORY -- kNN memory for CartPole or gridworld RL
- Anchor pointer: Research note Section "Domain 4: RL + substrate" and Cell P4.
- Substrate-product reading: in a CartPole or 5x5 gridworld RL episode, store (state, action, reward) tuples as VSA bindings. At each step, retrieve top-k nearest prior experiences for the current state to inform action selection. Compare cumulative reward vs flat L2 kNN memory (same capacity) after 500 episodes. Tests whether VSA binding structure over flat kNN adds value at small scale.
- Tier hint: local CPU. Standard RL libraries (gym). No GPU needed at this scale.
- Why now: Mem-alpha (arXiv 2509.25911, 2025) and memory-augmented RL for small LLMs (arXiv 2504.02273, 2025) both show episodic memory accelerates RL. VSA structure vs flat kNN is the delta being tested here.
- Gated by: SUBSTRATE-KG-PLANNING-GATE (Cell P1).

### 5. SUBSTRATE-LEMMA-RETRIEVAL -- lemma library retrieval for proof search
- Anchor pointer: Research note Section "Domain 5.2: Mathematical proof search" and Cell P5.
- Substrate-product reading: encode 200 mathematical lemmas as VSA bindings (lemma_statement, lemma_proof, lemma_type). Run 50 held-out proof-goal queries; retrieve top-5 relevant lemmas. Measure recall@5 against human-annotated relevant lemmas. Validates substrate as the retrieval backend for a Lean 4 proof assistant or math competition tool.
- Tier hint: local CPU. Lemma embeddings can be produced by Pythia-160M or sentence-transformers before VSA encoding. No GPU needed.
- Why now: AlphaProof (Nature 2025) explicitly notes that long hierarchical proofs are the bottleneck; retrieval-augmented proof search (arXiv 2508.06931, 2025) validates retrieval as the fix. Substrate's role is the O(1) retrieval layer with full audit trail.
- Gated by: SUBSTRATE-KG-PLANNING-GATE (Cell P1).

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_planning_open_ended_2x_2026-06-08.md
- K-hop empirical baseline: PP-119 (K=12, recall@1=0.987, synthetic) and PP-161 (cyclic graphs) from production architecture context.
- Iterative multi-hop handoff (shares anchor 1 structure): d:/AI/hd-instrument/notes/exp_dev_handoff_research_iterative_multihop_where_it_works_5x_2026-06-08.md
- Agentic memory layer handoff (Pattern B integration): d:/AI/hd-instrument/notes/exp_dev_handoff_research_agentic_memory_layer_2x_2026-06-07.md
- Post-compaction brief: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
- Multi-hop revive priority: memory file project_multihop_revive_priority.md

---

## Contract section

- This hand-off is exp_dev-actionable: it proposes concrete anchors gated by a cheap decisive test.
- SUBSTRATE-KG-PLANNING-GATE (anchor 1) is the precondition for all other planning anchors.
- If Cell P1 HARD-FAIL (recall@1 < 0.40 on real KG), escalate to Research for redesign before proceeding to anchors 2-5.
- If Cell P1 MID-BAND (recall@1 in [0.50, 0.75)), proceed to anchor 2 only and add K=3 beam retrieval to the design.

## Autonomy declaration

exp_dev has full autonomy over: which anchor to ship first (within the gating order above), exact N/M/K grid, seed count, threshold bands, queue choice, smoke-vs-full split, anchor naming, and cost envelope. No experiment design parameters are pre-committed in this file per [[feedback-no-experiment-design-in-prompts]].
