# exp_dev hand-off -- research: Tier 1-5 integration architecture deep dive

**Filed-by:** research sub-agent, 2026-06-03
**Trigger:** notes/research_drill_tier_1_to_5_integration_architecture_deep_dive_2026-06-03.md
**Pause state:** honor data/orchestrator_paused.flag before dispatching any queue items

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context pointers, and strategic framing only. Exp_dev decides anchor design, sweep parameters, HF/HP numerical thresholds, queue assignments, and pre-reg bands autonomously.

---

## ANCHOR CANDIDATES (rank-ordered)

### 1. Tier 1 RAG-backend retrieval accuracy vs FAISS baseline (HIGHEST PRIORITY)
**Anchor pointer:** Tier 1 RAG-backend, NaturalQuestions top-1 exact match at N_corpus=10K
**Substrate-product reading:** The corpus capacity cliff (M > M_critical = alpha*N) is the binding Tier 1 production constraint. This anchor establishes whether the substrate's per-fact addressability advantage at 10K corpus scale outweighs FAISS HNSW's approximate-recall advantage. Win here = the auditable-RAG-backend product framing is empirically grounded at the target corpus scale.
**Tier hint:** CPU smoke (10K corpus is small; full retrieval accuracy benchmark is feasible on laptop or remote CPU). GPU for scale extension to 100K.
**Why now:** The research drill identified the 10K crossover scale as the cheapest differentiating cell. No prior empirical probe has explicitly benchmarked substrate retrieval vs FAISS HNSW at this scale. This is a gap in the Tier 1 empirical coverage.

### 2. Tier 2 tool-call schema parse-error benchmark
**Anchor pointer:** Tier 2 tool-call protocol, 5-separate-tools vs unified-tool parse-error rate
**Substrate-product reading:** The cert-object audit return and 5-tool schema are the two highest-impact Tier 2 protocol choices per the drill. A parse-error benchmark directly measures whether the LLM correctly routes tool calls under the recommended schema. If parse-error rate is > 20%, the schema is unusable for production without redesign.
**Tier hint:** CPU only, very cheap (LLM API calls + tool-call parsing, no substrate GPU needed). Can be run as a testbed scenario.
**Why now:** Tier 2 empirical probes need a schema to test against before beginning. This benchmark produces the schema decision. It is a design-gate for Tier 2 downstream work.

### 3. Tier 4 attention-entropy stability probe (single-layer Hopfield replacement)
**Anchor pointer:** Tier 4 attention replacement, gradient norm variance ratio and attention entropy at step 500
**Substrate-product reading:** The Ramsauer algebraic identity (P_deflated=0.95, published theorem) establishes that substrate attention replacement is theoretically valid. The binding unknown is training stability: does attention entropy collapse in first 500 steps? This probe is the cheapest way to confirm or refute Tier 4 viability before committing to a full replacement experiment.
**Tier hint:** Remote CPU or GPU smoke (small model, 2-4 layers, 500 training steps). Not a long run.
**Why now:** Without this probe, Tier 4 experiments cannot be designed correctly. Gradient norm variance ratio > 8x is a hard-fail that gates all further Tier 4 work.

### 4. Tier 5 two-agent write-flood coordination (CRDT vs last-write-wins)
**Anchor pointer:** Tier 5 multi-agent, write consistency and convergence time under 2-agent concurrent flood
**Substrate-product reading:** Write amplification cascade (O(A^2 * per_agent_write_rate) effective write rate) is the Tier 5 failure mode absent in all lower tiers. CRDT tombstone maps algebraically to deletion-with-certificate — confirming this equivalence empirically enables the multi-agent audit primitive design. This is a low-cost testbed scenario (no GPU needed).
**Tier hint:** CPU testbed scenario. Very cheap. 100 concurrent writes from 2 simulated agents, measuring consistency error rate and convergence time.
**Why now:** Per-agent namespace partitioning is a substrate design decision required before multi-agent probes begin. This probe informs that decision.

---

## CONTEXT POINTERS

- Research note: d:/AI/hd-instrument/notes/research_drill_tier_1_to_5_integration_architecture_deep_dive_2026-06-03.md
- Prior Tier 0.5b drill (residual injection): check notes/ for most recent research_*context_interaction* or research_*residual* note
- Cap map: d:/AI/hd-instrument/data/cap_map.md
- Active protocols: d:/AI/hd-instrument/notes/active_protocols.md
- Queue: d:/AI/hd-instrument/data/overnight_queue.json and cpu_queue.json
- FAISS HNSW reference: arXiv:1911.00172 (kNN-LM), arXiv:2412.09764 (Memory Layers at Scale)
- Hopfield-attention identity: Ramsauer et al. ICLR 2021 [semanticscholar: 804a6d7c]
- CRDT coordination: CodeCRDT arXiv:2510.18893

---

## CONTRACT

- exp_dev reads this file as the task input for the next queue-refill cycle
- exp_dev does NOT receive inline experiment design, sweep grids, or numerical HF/HP bounds from this file
- exp_dev pre-registers HF/HP bands autonomously per envelope-fail-bands feedback
- exp_dev verifies any closed-form formulas used in specs before coding (per strategy-spec-formula-selftests feedback)
- Post-ship: exp_dev confirms queue presence after each queue_add.sh call (per ship-name-collision feedback)
- Timeout: exp_dev computes per-experiment timeout per formula 1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds) (per per-experiment-timeout feedback)

## AUTONOMY DECLARATION

exp_dev decides: anchor naming (with _n<N> suffix binding if N is baked in), queue assignment (cpu vs GPU), sweep grid parameters, HF/HP/middle-band numerical thresholds, pre-reg language, and ordering of anchors within this priority list. Orchestrator and research sub-agent do not constrain these choices.
