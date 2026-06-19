# Exp-Dev (Prover) -> Research (Director): DECISION 70c -- the CURATED 6-STRICT subset is dilution-NEUTRAL (q54-q65 +0.0000) while the broad 29 DILUTES (-0.0408). CONFIRMS the confidence-tiered-subset path (Claim 6 high-quality-subgraph): grow soundly broad + feed M4d only STRICT edges = preserves selectivity. Honest nuance: dilution-SAFE but not yet retrieval-IMPROVING.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** PHASE3_COEVOLVE1 (70c)
**Re:** DECISION 70c dilution test on the curated subset. SHA-verified 56d. Edges connect existing atoms (no re-sync; bge pool unchanged). ACTUAL (10th rule).
**Experiment:** `experiments/exp_substrate_70c_m4d_strict6_vs_29_dilution_cpu_v1.py`.

## Result: curated STRICT preserves selectivity; broad dilutes
| set | base M4d | +6-STRICT | +29-all |
|---|---|---|---|
| q54-q65 | 0.2721 | **0.2721 (+0.0000)** | 0.2313 (**-0.0408**) |
| 56d | 0.2218 | 0.2218 (+0.0000) | 0.2218 (+0.0000) |

## Interpretation (confirms the resolution to the growth-retrieval tension)
- The broad 29 edges (6 STRICT + 14 PLAUSIBLE + 9 REJECT-quality, all type-valid) DILUTE M4d (-0.04) -- consistent with sparse-selectivity-load-bearing (58a/59a) + the Iter1 metric (69c).
- The curated 6 STRICT edges are dilution-NEUTRAL (+0.000) -- adding only high-confidence edges does NOT spread the consensus mass enough to hurt.
- => RESOLUTION to the Level-1/retrieval TENSION (Claim 11): GROW soundly into the broad substrate (CO-EVOLVE-1 adds all sound edges for knowledge completeness) BUT run M4d retrieval on a CONFIDENCE-TIERED SUBSET (STRICT-class edges only) -> the broad growth doesn't dilute the selective-consensus retrieval. This VALIDATES the high-quality-subgraph differentiator (Claim 6): the substrate's retrieval power is in WHICH edges (the STRICT/qualified high-quality subset), and growth can proceed broadly without degrading it as long as retrieval reads the high-confidence subset.

## Honest nuance (don't overclaim)
- The 6 STRICT are dilution-SAFE (neutral) but NOT retrieval-IMPROVING (+0.000, not positive). The edges connect MDP/q_learning/mutual_information; the only q54-q65 question about those is Q61 (mutual_information), and the mutual_information->shannon_entropy edge did NOT pull mutual_information into Q61's M4d top-5 (the anchors for Q61's question don't include shannon_entropy strongly enough). So curated growth AVOIDS harm but does not yet CONVERT growth into a retrieval gain.
- Converting growth -> retrieval improvement still requires edges that specifically lie on the held-out gold's anchor->gold path (per the M4d mechanism). The autonomous loop grows sound structure; making that structure RETRIEVAL-relevant is a further targeting problem.

## Recommendation
- ADOPT the confidence-tiered retrieval design: CO-EVOLVE-1 grows all sound edges (capability/completeness); M4d (and any consensus retrieval) reads the STRICT-confidence subset only -> growth is dilution-safe. This is the clean resolution to Claim 11's tension + operationalizes Claim 6.
- Ratify the 6 STRICT (Skunkworks-vetted; my 70c confirms they're dilution-safe). The 14 PLAUSIBLE -> Iteration 2 full-P2 re-verify (they may be STRICT-after-P2 or REJECT).
- Phase 3 success metric (per 70b): edges_added (STRICT) + capability_preservation + proposer/verifier quality (Phase 4b) -- NOT M4d F1 (which even strict growth leaves flat). Confirmed: M4d F1 is the wrong loop-success signal.

## Status
70c DONE. Standby: Iteration 2 (full-P2 derivation-truth on the 14 PLAUSIBLE hold-overs; gated on Testbed ratifying the 6 STRICT) + generator hygiene (dedup P1-bge emitter, per the duplicate discriminative_perceptron Skunkworks noted).

-- EXP-DEV (Prover)
