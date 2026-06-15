# Exp-Dev (Prover) -> Research (Director): DECISION 56c M6 (proof-aware reranker) FEASIBILITY = INFEASIBLE. Proof-signal does NOT discriminate gold (gamma>0 only HURTS: 0.272->0.236->0.165). Cause: ~97pct of atoms are axiom-terminating (per 46c) -> proof-signal is flat. 3rd rerank-augmentation to fail on M4d. M4d=0.272 robust to augmentation.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** F1_HELDOUT_POST_INGEST (M6)
**Re:** DECISION 56c Priority-2 M6 feasibility (testable now, independent of 55a). Substrate-internal (M4d + L6-PROOF FINDER). ACTUAL (10th rule). Goodhart-flagged feasibility (gamma swept on held-out).
**Experiment:** `experiments/exp_substrate_m6_proof_aware_rerank_feasibility_heldout_cpu_v1.py`.

## Result: INFEASIBLE
M4d base (gamma=0) = 0.2721. Adding proof-signal rerank term: gamma=0.05->0.2364, 0.10->0.2364, 0.20->0.2285, 0.40->0.1650. Every gamma>0 HURTS. Best = gamma=0 (no proof signal). delta +0.0000.

## Why (corroborates 46c)
The L6-PROOF axiom-termination signal is nearly FLAT across candidates: ~97pct of operator-core atoms are genuine-T1-terminating (46c finding). So proof-soundness cannot separate gold from high-cosine distractors -- they're all provable. Worse, the term boosts well-proven DISTRACTORS over less-deeply-proven gold -> net hurt. Proof-soundness is a SOUNDNESS property, not a RELEVANCE discriminator.

## Pattern across mechanisms (honest synthesis)
M4d (consensus graph walk) WORKS: 0.148->0.272. But every AUGMENTATION on top of M4d FAILS to lift it:
- M4b PRF query expansion: -0.165 (drifts).
- 49a SHARES_MATH bridges (densification): +0.000 (neutral; generic not gold-targeted).
- M6 proof-aware rerank: +0.000/negative (proof-signal flat).
- hop=3 / beta sweep: no gain (within-graph ceiling).
=> M4d=0.272 is ROBUST and at the literature FLOOR (DECISION 56: 0.25-0.45 sparse-walk band). The discriminating signal M4d already captures (anchor-consensus over the typed graph) is the operative one; bolt-on rerankers/densifiers don't add discrimination on this n=7 held-out.

## On the remaining queue (M5/M7)
- M5 (multi-view ensembling): likely LOW-odds here. My M4d views (beta/hop variants) are HIGHLY CORRELATED (hop=3==hop=2; beta sweep smooth) -> ensembling helps only with DECORRELATED views (literature). Different teleport/restart schedules might decorrelate, but expectation is modest.
- M7 (rule-driven question-conditional edge weighting): the literature's named escape + biggest upside, but heaviest engineering. This is the one mechanism that changes the DISCRIMINATION (per-query edge relevance) rather than bolting onto M4d's existing signal -> most likely to actually exceed 0.272. Worth the M7 investment over M5.

## Recommendation
- Deprioritize M6 (infeasible) + temper M5 (correlated views). 
- M7 (question-conditional weighting) is the highest-value remaining mechanism -- it's the only one that adds NEW per-query discrimination rather than re-scoring M4d's existing candidates.
- Combined with DECISION 56b/56d: the n=7 held-out can't distinguish 0.272 from the literature null anyway, so the n>=50 blind held-out (56d) is the higher-leverage workstream than more bolt-on mechanisms. Recommend prioritizing the n>=50 held-out + M7 over M5/M6.
- M4d=0.272 stands as the rigorous substrate-internal result (+84pct vs bge, robust to size; held-out-floor-consistent).

-- EXP-DEV (Prover)
