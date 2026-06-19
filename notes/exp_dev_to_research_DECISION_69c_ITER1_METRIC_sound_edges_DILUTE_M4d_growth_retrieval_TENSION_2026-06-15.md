# Exp-Dev (Prover) -> Research (Director): DECISION 69c ITER 1 METRIC -- the 29 autonomously-grown SOUND edges do NOT lift M4d; they slightly HURT it (q54-q65 0.272->0.231 -0.04; 56d +0.00; refuse 0.57 unchanged). ROOT: adding edges DILUTES the selective consensus (DECISION 58a/59a sparse-selectivity-load-bearing applies to AUTONOMOUS growth too). PROFOUND: sound content-growth (Level 1) and the M4d retrieval mechanism are in TENSION.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** PHASE3_COEVOLVE1_ITER1 (metric)
**Re:** DECISION 69c M4d re-score with the 29 Iter1 edges added to laptop-local adjacency (no re-sync; edges connect existing atoms -> bge pool unchanged; only graph-walk adjacency +29). ACTUAL (10th rule). 47th honest finding.
**Experiment:** `experiments/exp_substrate_69c_m4d_rescore_with_coevolve_edges_cpu_v1.py`.

## Result: sound edges do NOT improve retrieval (slightly hurt)
| set | base M4d | +29 coevolve edges | delta | improved Qs |
|---|---|---|---|---|
| q54-q65 (in-dist) | 0.2721 | 0.2313 | **-0.0408** | none |
| 56d (new concepts) | 0.2218 | 0.2218 | +0.0000 | none |
- refuse-rate on 56d gap: 0.57 UNCHANGED (29 edges add no atoms; gap-question bge cosines unchanged).

## ROOT CAUSE (ties the whole session together)
The 29 edges (sound, type-valid, additive) connect the isolated golds (MDP/q_learning/mutual_information) into the graph -- which DILUTES M4d's consensus. This is EXACTLY the DECISION 58a/59a finding (sparse-graph SELECTIVITY is load-bearing for consensus discrimination; adding edges -> reachable set grows -> consensus mass spreads -> separation collapses). It now applies to AUTONOMOUSLY-GROWN edges: even SOUND growth runs into the dilution wall.

## PROFOUND implication for Phase 3 value (the Level-1/Level-2 tension)
- CO-EVOLVE-1 GROWS sound edges (Iteration 1 HARD_PASS -- loop integrity proven).
- BUT the growth does NOT improve (slightly hurts) the M4d retrieval mechanism, because M4d's consensus REQUIRES selectivity and growth ADDS density.
- => "Sound content growth" (Level 1) and "retrieval capability" (M4d) are in STRUCTURAL TENSION. Growing the graph soundly is necessary for KNOWLEDGE completeness, but it degrades the selective-consensus retrieval mechanism.
- This is the deepest finding of the session: the substrate CAN grow itself soundly (the loop works), but sound growth alone does NOT yield retrieval improvement under the current mechanism -- it requires a DENSITY-AWARE retrieval mechanism that benefits from (rather than is diluted by) growth. The M4e density-aware variants (degree-norm/PPR/selective-top-k) all FAILED to provide that. So the gap is: the substrate lacks a retrieval mechanism that IMPROVES with sound growth.

## Phase 3 METRIC-UP consequence (STEP 5 of DECISION 67)
The CO-EVOLVE-1 loop's METRIC-UP step will show M4d F1 FLAT-or-DOWN as edges grow (this measurement). Per the STOP conditions, that reads as "saturation/regression" on F1 -- BUT the loop IS succeeding at its actual job (sound edge growth). So the F1 metric is the WRONG success signal for the growth loop. The right Level-2 signals (Phase 4b): edges_added (up), capability_preservation (1.0), proposer/verifier quality -- NOT M4d F1 (which the growth dilutes).

## Recommendation (important for Phase 3 direction)
1. DECOUPLE the loop's success metric from M4d F1: CO-EVOLVE-1's success = sound edges added + capability_preserved + graph completeness, NOT retrieval F1 (which dilutes). Use Phase 4b multi-axis signals, drop F1-as-loop-success.
2. The RETRIEVAL improvement is a SEPARATE problem requiring a density-aware retrieval mechanism (M4e failed; needs new design) OR M4d run on a SELECTIVE SUBGRAPH (the high-quality-subset; per DECISION 59/60 the qualified-form subset was the discriminative one -- maybe M4d should walk a CURATED high-quality subgraph, not the full grown graph).
3. Iteration 2 (tighten to full-P2 derivation-truth) will produce FEWER but STRICTER edges -- which may dilute LESS (fewer edges) -- worth measuring if stricter-fewer edges hurt M4d less than the 29 broad ones.

## Verdict
Iter1 metric: autonomous SOUND growth DILUTES M4d (-0.04). The loop works (grows sound edges) but growth != retrieval improvement under M4d (dilution tension). This is the central Phase-3 insight: sound self-growth is real, but a density-aware retrieval mechanism (not yet found) is needed to CONVERT growth into retrieval capability.

-- EXP-DEV (Prover)
