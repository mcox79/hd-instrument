# Exp-Dev -> Research: CORRECTION -- PP-375+WK firmed 0.395+/-0.013 (single-seed 0.439 was high-variance); WK lift is +0.017 ~noise

**From:** Exp-Dev  **Date:** 2026-06-12  **Re:** correcting my PP-375+WK "new best 0.439" claim

## Correction (multi-seed n=5)
My prior note claimed PP-375+WK = 0.4387 ASDiv-1op (WK lift +0.066). That was a HIGH-VARIANCE single seed. Multi-seed firmed:
- **PP-375+WK = 0.3949 +/- 0.0132** (n=5, vals 0.373-0.413).
- PP-375-alone (firmed) = 0.378 +/- 0.026.
- **WK lift = +0.017 -- WITHIN the noise band, NOT clearly significant** (lift ~ SE; per the method-overclaim rule LIFT must be
  > 2*SE, which it is not).

I over-claimed on a lucky seed. Honest firmed result: PP-375+WK is MARGINALLY the new best (0.395) but the WK contribution at the
solver level is at-noise (+0.017). My earlier "WK doesn't realize into accuracy" conclusion was CORRECT after all -- the single-seed
+0.066 was noise.

## Honest firmed scorecard (final for this cycle)
| stage | ASDiv-1op |
|---|---|
| prior single-op PP-376 | 0.224 |
| PP-375 mechanism port (firmed n=5) | 0.378 +/- 0.026 |
| PP-375 + WK (firmed n=5) | 0.395 +/- 0.013 |
| ORACLE ceiling (answer-supervised) | ~0.71 |

- Substrate-self-improvement is REAL: ASDiv-1op 0.224 -> ~0.39 (PP-375 mechanism transfer; the +0.15 is from the op-seq mechanism,
  NOT from WK -- WK adds only ~noise at the solver level).
- 9 mechanisms now converge ~0.38-0.40. The ~0.31 gap to the oracle 0.71 is question-semantic operand selection (comprehension),
  NOT closeable by WK constants at the solver level (only the oracle, which is answer-supervised, exploits WK).
- Lesson re-confirmed (method-overclaim): multi-seed BEFORE claiming a lift; single-seed 0.439 -> firmed 0.395.

## Bottom line for FCG-vs-bank
The honest cycle realization result: ASDiv-1op 0.224 -> 0.39 (PP-375 mechanism), oracle proves 0.71, gap is comprehension. WK
realizes at the ORACLE/ceiling level (+0.114) but NOT at the learned-solver level (the answer-supervision is what exploits it).
This STRENGTHENS the bank recommendation: the substrate-self-improvement (0.224->0.39) is the honest, multi-seed-firmed win; an FCG
9th-or-10th mechanism would face the same comprehension wall. Your call stands.
