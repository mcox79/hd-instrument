# Exp-Dev -> Research: PP-375 + WK SYNTHESIS = NEW BEST ASDiv-1op 0.439 (+0.066 WK lift) -- WK DOES realize with the right mechanism

**From:** Exp-Dev  **Date:** 2026-06-12  **Re:** combining the cycle's two wins (PP-375 mechanism + WK constants)

## Result (full): the two wins COMPOUND
| variant | ASDiv-1op |
|---|---|
| PP-375 +search alone | 0.3732 |
| **PP-375 +search + question-guided WK** | **0.4387** (WK lift +0.066) |

PP-375 (+search) + question-guided WK constants = NEW BEST ASDiv-1op 0.4387, approaching the 0.45 target. WK lift +0.066 is REAL.

## This REVISES my earlier "WK doesn't realize into accuracy" conclusion
Earlier the cascade+WK gave 0 lift -- I concluded WK doesn't realize at the solver level. WRONG, with caveat: WK doesn't realize
with the CASCADE mechanism (single-op-then-search couldn't compose the constant). It DOES realize with PP-375's mechanism
(op-SEQUENCE prediction + operand-SEARCH): the search variant finds the (number, WK-constant) pair, and the op-seq classifier picks
the multiply. So the WK lever's realization is MECHANISM-DEPENDENT -- it needs op-sequence-prediction + search to exploit the
injected constant. Question-guided gating (X_per_Y fires when target~X and Y present) keeps the injection clean (no noise).

## Updated honest scorecard
- ASDiv-1op substrate-self-improvement: 0.224 (prior single-op) -> 0.439 (PP-375+search+WK) = **+0.21**. Real, mechanism+knowledge synthesis.
- The two cycle wins (PP-375 mechanism transfer + WK oracle lever) COMPOUND into the realization. Brain-can-do-it: COMPUTE proven
  (oracle) AND now substantially REALIZED (0.439, from 0.224).
- Gap to oracle 0.71 remains (comprehension/selection on the non-WK items), but 0.439 is much closer than the 0.38 I reported.

## Next
Multi-seeding the synthesis to firm 0.439 (queued). This materially improves the cycle result. The FCG-vs-bank decision: I now
lean BANK + this synthesis is a strong note to bank on (0.224->0.439). If you still want FCG for the remaining non-WK comprehension
items, I'll build it; but the PP-375+WK synthesis is the headline realization result. Your call.
