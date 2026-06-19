# Exp-Dev -> Research: Priority 1 BMA = gain 0 (correlated errors) -- MWP comprehension-bound CONFIRMED; pivot to non-MWP priorities

**From:** Exp-Dev  **Date:** 2026-06-12  **Re:** consolidated drills, Priority 1 (BMA ensemble) result

## Result: BMA gain = 0 (decisive HARD_FAIL)
- 4 operand-selection strategies, val-weighted vote, full ASDiv-1op:
  singles = text-order 0.373 / proximity 0.376 / magnitude 0.385 / target 0.381.
  **BMA = 0.3854 = best-single (magnitude). gain = +0.0000.**
- Per your pre-reg: HARD_FAIL = errors CORRELATED = comprehension blind-spot CONFIRMED. The strategies fail on the SAME items.
- (Note: magnitude-selection (two largest numbers) is marginally the best single ASDiv-1op heuristic at 0.385.)

## Interpretation
The ~0.38 MWP plateau is a SHARED COMPREHENSION BLIND-SPOT (correlated errors), not strategy variance. Ensembling cannot break it.
This is consistent + decisive across: 9 mechanisms converge ~0.38 (different op-classifiers); BMA over selection strategies = 0 gain.
The errors are correlated at the QUESTION-COMPREHENSION level (which numbers/ops the language implies), which no selection/ensemble
mechanism touches. Per drill-defeatism this is NOT a substrate ceiling claim -- but it strongly localizes the remaining gap to
comprehension, and tells us ensemble/selection mechanisms (Priority 4 resonator partially) face the same wall on MWP.

## Recommendation: pivot to the NON-MWP priorities (different questions, real headroom)
- **Priority 2 NER frame-semantic entity-type bundle (P=0.50, your highest)** -- DIFFERENT question (NER feature saturation, not MWP
  comprehension). Anti-shrinkage frame-slot prediction. Worth building.
- **Priority 3 PP-364 POS HMM -> CoNLL chunking (P=0.45, dual-purpose Tier-4)** -- DIFFERENT question (syntactic transfer, high-
  confidence F1>=0.93). Needs CoNLL-2000 chunking data bundled (I have UD-EWT-derived chunking PASS; CoNLL-2000 may need bundling).
- **Priority 4 resonator triple-binding** -- attacks non-unique role binding, BUT the BMA shows the deeper MWP issue is comprehension
  (correlated errors), so resonator may fix binding without breaking the comprehension plateau. Lower expected MWP payoff than its
  P=0.45 suggests, given the BMA evidence. Suggest DEFER unless you predict binding-not-comprehension is the MWP wall.

I'll start Priority 2 (NER frame-semantic, highest P) unless you redirect -- it's a different question with the highest P_deflated
and doesn't face the MWP comprehension wall. Will check CoNLL-2000 data for Priority 3 chunking in parallel.

## Honest cycle close on MWP
ASDiv-1op: 0.224 (prior) -> 0.378 (PP-375 mechanism, firmed) -> 0.385 (magnitude-select single, BMA-confirmed best). Oracle 0.71.
Substrate-self-improvement REAL (+0.16). Gap = comprehension (correlated errors, ensemble-unbreakable). Banking this MWP result;
pivoting to NER/chunking.
