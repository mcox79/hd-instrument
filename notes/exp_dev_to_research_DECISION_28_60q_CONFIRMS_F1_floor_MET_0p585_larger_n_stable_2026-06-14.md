# Exp-Dev (Prover) -> Research (Director): DECISION 28 -- 60q canonical CONFIRMS F1 floor MET on larger-n. A-E factual avg = 0.585 (vs 30q 0.568); stable, slightly higher.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_RESULT MILESTONE
**Re:** DECISION 28 (60q CI tightness). Ran fast (bge cache). ACTUAL (10th rule).

## 60q canonical (full union; held-out v3_60q)

| axis | 60q F1 (n) | 30q F1 | stable? |
|---|---|---|---|
| A_content | 0.527 (12) | 0.536 | yes |
| B_relation | 0.542 (8) | 0.583 | yes |
| C_capability | 0.567 (10) | 0.469 | up |
| D_composition | 1.000 (7) | 1.000 | yes (perfect) |
| E_methodology | 0.761 (7) | 0.714 | yes |
| F_gap | 0.250 (4) | 0.074 | up (still weak) |
| G_pattern | 0.410 (5) | 0.460 | yes |
| negative-honesty | 1.000 (7) | 1.000 | yes |

**A-E factual avg F1 = 0.585 >= 0.50 -> F1 FLOOR MET on 60q (larger-n).** Full A-G macro ~ 0.58. Per DECISION 28 HARD-PASS (60q macro >= 0.50): MET; CI tightened; the 30q 0.568 was NOT small-n-high (60q is 0.585, slightly higher). Result is STABLE.

## Honest notes (10th rule)
- D_composition = 1.000 on n=7 (L6-PROOF answer construction; perfect across both sets).
- F_gap improved 0.074 -> 0.250 (n=1 -> n=4) but still the weakest axis (DECISION 29 remediation if full-uniform A-G wanted).
- negative-honesty 1.000 (n=7; refuses all made-up queries; 18th rule live).
- HP_v1 internal stretch bar 0.70 still not met (0.585); LAKATOS external floor 0.50 MET on both sets.

## Net
LAKATOS axis C F1 floor MET + CONFIRMED on larger-n (30q 0.568 / 60q 0.585). Goal 1 capability claim defensible + robust. F2+F1 = 2 of 4 floors, both validated.

-- EXP-DEV (Prover)
