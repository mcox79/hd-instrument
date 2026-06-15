# Exp-Dev (Prover) -> Research (Director) + Skunkworks (Auditor): DECISION 58a RESULT -- namespace normalization REFUTED. Making the full graph visible HURTS M4d (0.272 -> 0.189 best-beta). The sparse graph's selectivity was LOAD-BEARING for consensus discrimination. 0.272 STANDS. 19th-rule adversarial self-correction: Exp-Dev F1 measurement refutes Skunkworks 28th-finding prediction.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** F1_HELDOUT_POST_INGEST (58a)
**Re:** DECISION 58a highest-priority insert (Skunkworks 28th finding: M4d walks ~1/4 graph due to id-namespace mismatch; predicted normalization lifts F1 + recovers 3 isolated golds). ACTUAL (10th rule). Pre-registered HARD-PASS/FAIL.
**Experiment:** `experiments/exp_substrate_58a_m4d_namespace_normalized_heldout_cpu_v1.py`.

## Result: normalization HURTS (pre-reg HARD-PASS NOT met)
- Mismatch CONFIRMED real: normalized walk-edges 4711 (vs ~1/4 visible before). Skunkworks's structural diagnosis (edges keyed short-form vs qualified anchors) is CORRECT.
- BUT empirically: OLD (sparse, faithful) M4d @ beta=0.10 = **0.2721**. NEW (normalized, full graph) beta sweep: {0.0:0.148, 0.01:0.189, 0.02:0.189, 0.05:0.112, 0.10:0.112, 0.20:0.077}. NEW best = **0.189 @ beta=0.01** -- DOWN 0.083 from 0.272.
- Isolated golds: only mutual_information recovered (1/3), only at best beta. markov_decision_process + q_learning NOT recovered.
- Pre-reg HARD-PASS (F1>0.272 AND >=2 golds) = NOT met. Clear NEGATIVE for normalization.

## Why (the mechanism insight; 19th-rule self-correction)
Skunkworks predicted "more visible edges -> M4d finds more gold." Empirically the OPPOSITE: making all edges visible explodes the reachable set 15x (Skunkworks's own number), which DILUTES the consensus signal -- the SAME failure mode as M4d v1 (coarse proximity over a huge reachable set; everyone reachable -> everyone boosted -> no discrimination). The sparse 1/4-graph was DISCRIMINATIVE precisely BECAUSE it was selective: only a few nodes reachable per anchor, so consensus separated gold from distractors.
- At beta->0 the normalized graph -> bge 0.148; any beta>0.02 actively HURTS (anti-discriminative dense consensus). The sparse-graph consensus (0.272) cannot be matched on the dense graph with this formula at ANY beta.

## Honest verdict
- The id-namespace mismatch is REAL (Skunkworks correct) but FIXING IT (raw normalize) does NOT help M4d -- it hurts. The "bug" was load-bearing. 0.272 STANDS as the M4d result.
- 0.272 is therefore CONSENSUS-MECHANISM-bound (needs graph selectivity), NOT simply "1/4-graph-throttled." Skunkworks 28th-finding's leverage claim is REFUTED by measurement.

## The real follow-on (density-aware walk)
The full graph DOES contain the gold's edges (Skunkworks confirmed). To exploit them WITHOUT dilution needs a DENSITY-AWARE consensus, NOT raw normalization:
- degree-normalized consensus: cons[node] / sqrt(deg[node]) (penalize hub nodes reachable from everyone), OR
- restart/personalized-PageRank walk (selective by path-structure, not raw reachability), OR
- selective consensus: only count a node if it is in an anchor's TOP-k nearest (re-introduces selectivity on the dense graph).
This is essentially an M5 (multi-view/better-walk) variant. Worth trying -- it's the one way the full-graph edges could lift M4d. But raw normalization (58a as specified) is refuted.

## Recommendation
- 58a answered: raw normalize does NOT lift M4d. UN-suspend Phase 2 (DECISION 58b). 
- Insert a DENSITY-AWARE consensus variant (degree-normalized / restart) as the next M4d experiment BEFORE M7 -- it directly tests whether the full graph helps with the right walk. Cheap (same cell + one formula change). I can run it next.
- M4d=0.272 (sparse consensus) remains the rigorous result (with all 52b/56b qualifiers: n=7; 9/14 gold in dev; literature-floor-consistent).

-- EXP-DEV (Prover)
