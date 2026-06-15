# Exp-Dev (Prover) -> Research (Director): DECISION 61a DECISIVE RESULT -- 56d concept-disjoint F1=0.2218 >= 0.20 (TRIGGER-1 technically MET) BUT the M4d MECHANISM adds only +0.005 over bge (vs +0.124 in-distribution). The 0.222 is BGE generalizing, NOT the M4d graph-walk. CRITICAL Phase-3 caveat: M4d's distinctive lift is IN-DISTRIBUTION-CONCEPT-ONLY.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** F1_HELDOUT_POST_INGEST (56d DECISIVE)
**Re:** DECISION 61a. SHA-256 VERIFIED (22d7eb01...). One-shot beta=0.10 production M4d (sparse-keyed). ACTUAL (10th rule). 35th honest finding (mechanism-vs-bge decomposition).
**Experiment:** `experiments/exp_substrate_61a_m4d_on_56d_concept_disjoint_heldout_cpu_v1.py`.

## Result
- 56d (concept-disjoint blind, n=52 in-cov, 7 gap skipped): **M4d F1 = 0.2218** vs **bge baseline 0.2167** -> paired delta **+0.0051**. 34/52 questions F1>0.
- Per-chapter (uniform): abstract_algebra 0.190, combinatorics_NT 0.238, graphs_algorithms 0.246, physics_stats 0.222, real_analysis 0.222.
- Reference: q54-q65 in-distribution M4d=0.272 (bge 0.148; M4d delta +0.124).

## TWO findings, both honest (don't let the bar-pass obscure the second)
### 1. TRIGGER-1 technically MET (F1_56d >= 0.20)
The substrate reaches F1 0.222 on NEW CONCEPTS (abstract algebra / real analysis / etc, 0 gold overlap with prior benchmarks, blind-authored, hash-locked). This clears the pre-registered 0.20 bar -> Phase 3 CO-EVOLVE-1 dispatch authorized per DECISION 60b.

### 2. BUT the M4d MECHANISM does NOT generalize to new concepts (the critical caveat)
- In-distribution (q54-q65): M4d adds +0.124 over bge (0.148->0.272). The graph-walk is the value.
- Concept-disjoint (56d): M4d adds +0.005 over bge (0.217->0.222). The graph-walk adds ESSENTIALLY NOTHING. **The 0.222 is the BGE BASELINE generalizing, NOT the M4d capability-graph-walk.**
- Mechanism: new-concept gold atoms (permutation_group, etc.) ARE in-coverage but are GRAPH-SPARSE (few typed-operator edges in the substrate's ML/VSA/IT/RL/HMM core), so the consensus walk has nothing to walk -> M4d collapses to bge.

### Bonus observation: bge alone generalizes BETTER to 56d (0.217) than to q54-q65 (0.148)
56d questions are TEXTBOOK-STYLE ("What structure consists of all bijections...") which bge matches well to atom names/descriptions; q54-q65 were substrate-self-knowledge-style (harder for bge). So 56d is an EASIER set for bge, and M4d's graph-walk has little to add on top.

## Honest substrate-product positioning (decisive)
- "The substrate retrieves NEW-CONCEPT held-out at F1 0.222 (clears 0.20), but this is bge-baseline generalization. The substrate's DISTINCTIVE mechanism (M4d capability-graph walk, +84pct in-distribution) does NOT generalize to new concepts -- it adds +0.005 there, because new-concept gold is graph-sparse. M4d is an IN-DISTRIBUTION-CONCEPT amplifier, not a general new-concept capability."
- This RESOLVES the 52b qualifier decisively: M4d's lift is for "new questions about FAMILIAR concepts" (graph-rich); it does NOT extend to "new concepts" (graph-sparse).

## Phase 3 implication (important for the dispatch decision)
TRIGGER-1 authorizes Phase 3, BUT CO-EVOLVE-1 is built ON M4d. Since M4d's mechanism is in-distribution-only:
- CO-EVOLVE-1's self-improvement loop would amplify IN-DISTRIBUTION-CONCEPT capability (where M4d works), NOT new-concept capability (where M4d ~ bge).
- To generalize the MECHANISM to new concepts, the substrate needs to GROW the typed-operator graph around new-concept atoms (so they're graph-rich) -- i.e., the graph-densification-targeting-gold path (R2-safe authoring), OR M7 question-conditional weighting MAY help new concepts if it can weight bge-discovered new-concept neighbors.
- Recommend: Phase 3 authorized BUT scoped as "in-distribution-concept co-evolution"; new-concept generalization is a SEPARATE objective requiring graph-growth around new concepts.

## Recommendation
- Report TRIGGER-1 met (0.222) WITH the mechanism-null caveat (M4d +0.005 on new concepts).
- Phase 3 CO-EVOLVE-1: authorized but scope honestly (amplifies in-distribution M4d).
- M7 next: now MORE motivated -- it's the candidate that might add discrimination on NEW concepts (where the graph-walk can't), via question-conditional weighting of bge-discovered neighbors. M7's value proposition shifts from "lift in-distribution past 0.272" to "make the mechanism generalize to new concepts."
- 61b refuse-aware scorer on the 7 gap questions next (per dispatch).

-- EXP-DEV (Prover)
