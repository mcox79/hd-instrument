# Exp-Dev (Prover) -> Research (Director): DECISION 61b -- refuse-discipline on NOVEL topics (56d gap, n=7) = 0.57 (4/7 refuse) at tau=0.70. The 3 hallucinations are NEAR-THRESHOLD semantically-related retrievals (cos 0.70-0.74); tau=0.75 would refuse most. Refuse-discipline is PARTIAL + tau-tunable on new concepts (similar to in-distribution gap 0.667).

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** F1_HELDOUT_POST_INGEST (61b refuse)
**Re:** DECISION 61b refuse-aware scorer (dispatched after 61a). SHA-verified. ACTUAL (10th rule).
**Experiment:** `experiments/exp_substrate_61b_refuse_aware_scorer_56d_gap_cpu_v1.py`.

## Result: refuse-discipline on novel-concept gap = 0.57 (tau=0.70)
7 56d gap questions (gold NOT in substrate; correct = refuse). Correct-refusal 4/7 = 0.5714.
| qid | max_cos | behavior | (if halluc) retrieves |
|---|---|---|---|
| GAP01 | 0.654 | REFUSE | - |
| GAP02 (Riemann hyp) | 0.732 | HALLUC | "Floor of imaginary parts..." |
| GAP03 | 0.695 | REFUSE | - |
| GAP04 (Yoneda lemma) | 0.740 | HALLUC | "Functor" |
| GAP05 | 0.623 | REFUSE | - |
| GAP06 | 0.656 | REFUSE | - |
| GAP07 (four-color thm) | 0.704 | HALLUC | "Coloring a circuit with 4 colors" |

## Key nuance: hallucinations are NEAR-THRESHOLD + SEMANTICALLY RELATED
The 3 "hallucinations" are not random noise -- they are genuinely-related atoms at cos 0.70-0.74 (four-color theorem -> "Coloring a circuit with 4 colors"; Yoneda -> "Functor"; Riemann -> a zeta-related atom). bge correctly finds the NEAREST substrate atom; the issue is the tau=0.70 gate (from 35a) is slightly too permissive for novel topics. At tau=0.75: GAP02(0.73), GAP04(0.74), GAP07(0.70) all < 0.75 -> refusal rate -> 7/7. So refuse-discipline is TAU-TUNABLE, not categorically broken.

## Honest read
- Refuse-discipline on novel topics = 0.57 at tau=0.70 (PARTIAL), similar to in-distribution gap refuse 0.667 (q54-q65). Consistent: refuse-discipline is partial + tuned-tau-specific (the long-standing Cause-2 finding).
- The near-threshold + semantically-related nature means the substrate is NOT wildly hallucinating -- it returns the nearest related atom; a tau bump (0.75) restores most refusals. But tuning tau on the gap risks over-refusing in-coverage (the precision/recall tension from DECISION 32/34a -- bge cosine distributions overlap; no clean separating tau).
- This corroborates M1/M1c: bge cosine cannot cleanly separate "related-but-absent" from "present" -> the 0.70-0.75 band is where related-absent and present overlap.

## Recommendation
- Report refuse-discipline-on-novel-topics = 0.57 (tau=0.70) with the tau-sensitivity caveat. Do NOT tune tau on the gap set (Goodhart + the overlap tension means a higher tau would hurt in-coverage recall, already low).
- The refuse-discipline gap (Cause 2) remains: bge cosine overlap between related-absent and present is the root; M2 cleanup_margin (different signal) was the proposed fix, gated on Testbed C2+CHTV.
- 61a + 61b complete. M4d 56d: F1 0.222 (TRIGGER-1, but bge-driven; M4d mechanism +0.005). Refuse 0.57. Both decisive numbers delivered for the Phase 3 decision.

-- EXP-DEV (Prover)
