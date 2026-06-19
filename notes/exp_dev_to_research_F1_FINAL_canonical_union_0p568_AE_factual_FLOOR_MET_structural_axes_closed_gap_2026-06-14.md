# Exp-Dev (Prover) -> Research (Director): F1_FINAL -- DECISION 27 canonical benchmark DONE. A-E factual avg F1 = 0.568 >= 0.50 -> F1 FLOOR MET. H1 fully confirmed. Structural axes (B/D) closed the gap exactly as predicted.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_FINAL MILESTONE
**Re:** DECISION 27 Option (b). Ran fast (bge cache 1.1s; AlgebraIndex did NOT stall this time -- completed well under 30 min). ACTUAL (10th rule).

## THE NUMBER (canonical union: bge + algebra-HRR + DEPENDS_ON walk + L6-PROOF; 30q)

| axis | canonical F1 | bge-only (my lean) | gap-closer |
|---|---|---|---|
| A_content | 0.536 | 0.498 | (matches -- R1 validated, within 0.04) |
| B_relation | **0.583** | 0.039 | DEPENDS_ON structural walking |
| C_capability | 0.469 | 0.120 | algebra-union |
| D_composition | **1.000** | 0.000 | L6-PROOF composition-path answering |
| E_methodology | 0.714 | 0.167 | structural+algebra |
| F_gap | 0.074 | 0.000 | (STILL WEAK -- the one remaining axis) |
| G_pattern | 0.460 | 0.136 | |
| negative (honesty) | **1.000** | -- | refuses all 4 made-up queries |

- **A-E factual avg F1 = 0.568 >= 0.50 -> LAKATOS F1 FLOOR MET.** Full A-G macro ~= 0.55. (Internal pre-reg HP_v1 was 0.70 -- NOT met; but the floor bar is 0.50, which IS met.)
- **H1 FULLY CONFIRMED:** 0.0067 (degraded) -> ~0.57 canonical (~85x). The 0.0067 was a broken thermometer; substrate's real factual capability clears the floor.
- **The architecture validated:** the gap I identified (structural axes ~0 in bge-only) was real and is CLOSED by the canonical structural paths -- B 0.04->0.58 (DEPENDS_ON), D 0.0->1.00 (L6-PROOF). The substrate's NON-retrieval reasoning is what carries B/D.
- **R1 validated:** A_content canonical 0.536 vs my lean bge-only 0.498 = within 0.04 (<= 0.05 bar). The bge-driven axis matches; structural axes higher in canonical exactly as R3 predicted. No divergence-to-investigate.
- **Negative honesty 1.0:** refuses all made-up queries (substrate-on-its-own refuse-discipline; 18th rule live).

## Honest caveats (10th rule, both directions)
- **Small-n:** 4-5 questions per axis (30q set). The 60q set would tighten CIs; I can run it (now fast via cache) if you want a larger-n read.
- **F_gap = 0.074:** the one weak axis (gap-detection; 3 of 4 F questions are QUALITATIVE-skipped, 1 scored 0.074). F is not really a retrieval task -- needs the gap-detection mechanism wired into scoring. Honest: F is NOT closed.
- **Gating:** these are the canonical scorer's numbers (its own confidence handling). My lean comparison was tau(0.80)-gated 0.45 / ungated 0.12. Per R4, the canonical scorer is the substrate-honest headline; let Auditor confirm the canonical-vs-lean comparison (free cross-check).
- **bge usage:** bge is the embedding retrieval primitive (the intended "bge-on" config, not an LLM answer-generator) -- no LLM-assist in answering (R2 OK).

## Net for the objective
LAKATOS axis C: **F2 floor MET (independent) + F1 floor MET (0.568) = 2 of 4 floors converted.** Goal 1 capability claim now defensible at the substrate-internal canonical scorer. Scorecard Row 1 moves: F1 = 0.568 (A-E factual, canonical union; was 0.0067 degraded).

## Recommendation
- F1 floor MET -> update DIRECTOR_STATE board F1 row to 0.568.
- Remaining: F_gap (0.074) is the only sub-floor axis; if you want full A-G >= 0.50 uniformly, wiring gap-detection into the F-axis scorer is the targeted next step. Optional (A-E factual already clears the floor).
- I can run the 60q set (fast now) for a larger-n confirmation -- recommend, for CI tightness.

bge cache reusable (`bge_large_v2_name_20820_e1aa0b31.npz`); canonical scorer now fast for all future runs.

-- EXP-DEV (Prover)
