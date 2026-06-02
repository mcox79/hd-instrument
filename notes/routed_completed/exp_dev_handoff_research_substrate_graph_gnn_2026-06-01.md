# exp_dev hand-off -- research: substrate-graph-gnn

**Filed-by:** research sub-agent (Sonnet), 2026-06-01
**Trigger:** notes/research_substrate_graph_gnn_2026-06-01.md
**Pause state:** check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file hands TASK + WHY + CONTRACT + AUTONOMY to exp_dev. It does NOT specify anchor names, sweep grids, threshold formulas, HF numerical bounds, or pre-committed cap_map decisions. exp_dev designs those.

---

## Anchor candidates (rank-ordered, cheapest first)

### Anchor 1 -- Graph deletion certificate (laptop CPU, ~60s smoke)
**Pointer:** Cap row PP-9 (deletion certificate) + graph-reasoning application identified in research note.
**Substrate-product reading:** Rank-1 erase on edge bindings -- the same algebraic primitive as fact deletion, applied to knowledge graph edges. This verifies that the PP-9 deletion cert generalizes to graph-structured data without new infrastructure.
**Tier hint:** Laptop CPU smoke. M=100-200 edge vectors, N=4096. Well under capacity cliff. No GPU needed.
**Why now:** The research note identified this as the cheapest possible validation (60-second CPU). It closes the question of whether PP-9 generalizes to KG edges before any larger graph experiment is designed. Pre-registers HP1 from research note.

### Anchor 2 -- Multi-hop retrieval SNR sweep (laptop CPU, ~5 minutes)
**Pointer:** Cap rows (multi-hop reasoning, pool retrieval) + graph-reasoning note Sec 3 Win 2.
**Substrate-product reading:** Empirical SNR as function of (N, M_r, k) for k in {1,2,3,4}. Validates or refutes the theoretical ceiling at k=3. If SNR stays above threshold at k=3 and collapses at k=4, this defines the 2-hop product window.
**Tier hint:** Laptop CPU. Algebraic + retrieval test, no training needed.
**Why now:** The research note pre-registers HF1 (k=4 SNR < 1.5) and HP2 (k=2 SNR > threshold). This anchor is the definitive test of the multi-hop operating window, which determines the product's graph-reasoning scope.

### Anchor 3 -- Subgraph cardinality trace formula (laptop CPU, ~10 minutes)
**Pointer:** Cap row (audit/provenance) + research note Sec 3 Win 4 + homomorphism counts literature.
**Substrate-product reading:** Does xi_v^T W_r^k xi_v correlate with exact triangle/path counts? If HP3 passes (r > 0.65), substrate has a subgraph-cardinality primitive with no GNN equivalent, enabling graph-membership audit certificates.
**Tier hint:** Laptop CPU. 100-node synthetic graph, M=300 edge vectors.
**Why now:** Third cheapest cell. Validates the trace formula claim before any product framing of the k-hop membership certificate feature.

---

## Context pointers (file paths, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_substrate_graph_gnn_2026-06-01.md
- CSP-with-learning note (graph-CSP synthesis): d:/AI/hd-instrument/notes/research_csp_with_learning_2026-06-01.md
- Cap map (PP-9 deletion cert, PP-15 multi-tenant): d:/AI/hd-instrument/notes/substrate_capability_map.md
- Post-compaction brief: d:/AI/hd-instrument/notes/orchestrator_post_compaction_brief.md
- Active protocols: d:/AI/hd-instrument/notes/active_protocols.md

---

## Contract

exp_dev owns: anchor naming, sweep grids, threshold formulas, HF/HP/MID bands, queue choice, timeout estimates, cap_map annotation decisions.
Research handed off: the capability hypothesis, the competing lit-scan context, the product framing, and the rank-ordered anchor list.

## Autonomy declaration

exp_dev has full autonomy to reorder, merge, split, or discard these anchors based on current queue state, runner availability, and strategic priorities. The research note provides the scientific justification; exp_dev provides the experimental design.

<!-- routing-completed: Acted-on 2026-06-01: handoff to Round 10 dispatch -->
