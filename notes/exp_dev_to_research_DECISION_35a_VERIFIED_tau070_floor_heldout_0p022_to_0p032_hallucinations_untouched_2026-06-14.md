# Exp-Dev (Prover) -> Research (Director): DECISION 35a VERIFIED in canonical union scorer -- tau=0.70 floor lifts held-out A-E F1 0.022->0.032 (precision win); the two worst hallucinations UNTOUCHED (above floor) exactly as M1b predicted.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_HELDOUT_DECOMPOSED (35a verify)
**Re:** DECISION 35a shipped tau=0.70 in answer_type_A_union. Re-scored held-out q54-q65 with the patched canonical union scorer. ACTUAL (10th rule).

## Result: 0.022 -> 0.032 A-E factual avg F1 (modest precision win; soundness UNCHANGED)

| q | pre-floor | post-floor (tau=0.70) | effect |
|---|---|---|---|
| Q54-A | tp0 fp5 fn5 | tp0 fp0 fn5 | -5 FP (noise removed) |
| Q61-A | tp1 fp4 fn4 F1=0.20 | tp1 fp1 fn4 **F1=0.29** | +0.09 F1 (precision) |
| Q63-A | tp0 fp5 fn5 | tp0 fp1 fn5 | -4 FP |
| Q59-F | tp0 **fp26** fn4 | tp0 **fp26** fn4 | UNCHANGED (above floor) |
| Q_neg_2 | tp0 **fp5** fn0 | tp0 **fp5** fn0 | UNCHANGED (above floor) |

A-E factual avg F1: **0.022 -> 0.032**. HP_v1 bar 0.70 still UNMET (expected; this is a light helper not the floor-closer).

## Confirms M1b mechanistically
- The floor removes LOW-confidence FP noise (Q54/Q61/Q63 cleaned up) -> small precision/F1 lift.
- It does NOT touch the worst hallucinations (Q59-F 26 FPs; Q_neg_2 5 FPs) because those are HIGH-confidence (top1>=0.73, many atoms >=0.70) -- the inverted-confidence finding. A confidence floor structurally cannot catch high-confidence hallucinations.
- 35a stands exactly as scoped: capability/precision helper, NOT a soundness fix.

## Note on metric reconciliation (honest)
- This 0.032 is the canonical UNION scorer A-E avg vs FULL gold (coverage-capped). The Director's "0.074->0.128" was my bge-ONLY cell vs PRESENT-gold subset. Both say the same thing: modest lift, no soundness fix. Different denominators (full-gold-union vs present-gold-bge-only); not a contradiction.

35a VERIFIED + committed (BGE_CONFIDENCE_FLOOR=0.70). No further action on 35a. Holding for USER M4 decision (DECISION 35b) + Testbed C2+CHTV (M2 gate).

-- EXP-DEV (Prover)
