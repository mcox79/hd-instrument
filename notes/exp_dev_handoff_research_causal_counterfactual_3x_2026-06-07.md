# exp_dev hand-off -- research: substrate gap causal and counterfactual reasoning (3x)

**Filed-by**: research sub-agent, 2026-06-07
**Trigger**: notes/research_drill_substrate_gap_causal_counterfactual_3x_2026-06-07.md -- do() intervention isomorphism with rank-1 downdate confirmed; local counterfactual replay mechanism fully specified; cheap decisive test ready.

**Pause state**: check data/orchestrator_paused.flag before dispatching. Do not ship if flag present.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands TASK + WHY + CONTRACT + AUTONOMY. exp_dev decides anchor names, sweep parameters, threshold formulas, queue routing, and pre-reg bands.

---

## Anchor candidates (rank-ordered)

### 1. Local counterfactual replay accuracy probe (HIGHEST PRIORITY -- CPU, ~2 min)

**What**: construct a synthetic knowledge graph with 100 entities, 500 facts, and 5 causal chains of length K=5 stored in substrate W at N=1024. For each chain, substitute one fact (the "intervention") in the middle of the chain via rank-1 downdate + rank-1 write into a query-scoped W_tmp. Re-run K-hop from chain start on W_tmp. Measure fraction of runs where K-hop in W_tmp reaches the correct modified conclusion.

**Why**: this is the minimum viable falsification test for the local counterfactual replay mechanism. The research note establishes that rank-1 downdate (Cycle 149 validated) IS algebraically equivalent to Pearl's do(X=x) intervention for single-variable substitution. This probe confirms or refutes whether that algebraic equivalence translates to correct retrieval in practice at substrate scale. P_deflated=0.60.

**Tier hint**: CPU local, N=1024, ~2 minutes wall. Zero cloud cost. Laptop queue.

**Pre-reg bands (for exp_dev to formalize)**:
- HARD-PASS: >= 80% correct counterfactual conclusions across 100 chains.
- MIDDLE-BAND: 50-79% correct.
- HARD-FAIL: < 50% correct (substrate broken for counterfactual replay).

**Cap_map pointer**: opens new row candidate "local counterfactual replay via query-scoped rank-1 W modification." Currently no cap_map row exists for causal/counterfactual capability. HARD-PASS warrants a new row at 🔬 status.

**Substrate-product reading**: if local counterfactual replay works at >= 80% accuracy with < 10ms latency, the substrate exposes a "what if?" API directly applicable to EU AI Act Article 12 compliance (post-hoc decision audit) with a hard regulatory deadline of August 2026. This is the highest-urgency commercial use case for the causal gap.

---

### 2. Causal direction marker disambiguation probe (secondary -- CPU, ~5 min)

**What**: store 50 causal pairs (A causes B) and 50 correlational pairs (A co-occurs with B) in W at N=4096 using Mechanism A direction vectors (CAUSE_OF and CORRELATED_WITH role vectors initialized quasi-orthogonally at random). Query "what causes Y?" for each Y. Measure precision and recall of causal vs correlational retrieval.

**Why**: Mechanism A (causal binding extension) requires that direction vectors CAUSE_OF and EFFECT_OF are reliably distinguishable in substrate's approximate retrieval. If they fail to disambiguate at N=4096, Mechanism A is ruled out and the engineering path shifts entirely to Mechanism C (hybrid external layer). P_deflated=0.68.

**Tier hint**: CPU local, N=4096, ~5 minutes wall. Laptop queue.

**Pre-reg bands (for exp_dev to formalize)**:
- HARD-PASS: precision > 0.85 for causal pair retrieval.
- MIDDLE-BAND: precision 0.60-0.85.
- HARD-FAIL: precision < 0.60 (direction vectors do not disambiguate).

**Cap_map pointer**: if HARD-PASS, supports Mechanism A schema extension. If HARD-FAIL, closes Mechanism A and routes to Mechanism C planning.

---

### 3. Rank-1 W modification side-effect interference probe (secondary -- CPU, ~3 min)

**What**: store 200 facts in W at N=4096. Perform rank-1 downdate + rank-1 write on 1 fact (single intervention). Re-query all 199 OTHER facts via standard retrieve operation. Measure mean cosine similarity degradation on the non-targeted facts before vs after the W modification.

**Why**: Mechanism B (intervention as W modification) requires that modifying W for one fact does not substantially degrade retrieval quality for all other stored facts. If interference exceeds 20%, the W-mutation approach is impractical for production (too destructive). P_deflated=0.72 that degradation is below 20%.

**Tier hint**: CPU local, N=4096, ~3 minutes wall. Laptop queue.

**Pre-reg bands (for exp_dev to formalize)**:
- HARD-PASS: mean cosine similarity degradation < 5% on non-targeted facts.
- MIDDLE-BAND: 5-20% degradation.
- HARD-FAIL: > 20% degradation (W modification too destructive for practical counterfactual queries).

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_gap_causal_counterfactual_3x_2026-06-07.md
- Cycle 149 rank-1 downdate validation: search data/ for exp_cycle149 metrics; the downdate math is the algebraic basis for Mechanism B.
- Cycle 137 K-hop validation (K=20, 100%): the K-hop replay on W_tmp inherits this validation.
- Cycle 145 compositional K-hop verifier: the chain verification primitive used in the counterfactual comparison step (Step 5 of the formal procedure).

---

## Contract section

exp_dev owns: anchor names, sweep parameter choices, exact threshold formulas, queue routing (CPU vs GPU), pre-reg band specification, script implementation.

Research has provided: mechanism specification, algebraic derivation, P_deflated estimates, pre-reg threshold GUIDANCE (not specification), queue tier hints, commercial framing.

---

## Autonomy declaration

exp_dev has full autonomy over experiment implementation details. The three anchor candidates above are RANKED RECOMMENDATIONS, not mandatory sequencing. If exp_dev identifies a cheaper or more decisive test that probes the same mechanism, prefer that. The priority order is: local counterfactual accuracy (anchor 1) > direction disambiguation (anchor 2) > side-effect interference (anchor 3). Anchor 1 is the most commercially urgent given the Article 12 deadline pressure.
