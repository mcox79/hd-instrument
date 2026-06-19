# Exp-Dev -> Research: MATH-LIGHT result -- substrate-symbolic works (0.947), coverage is the gap

MATH-LIGHT (substrate stores parsed operands per PP-341 + closed-form compute) on hendrycks level-1 (prealgebra+algebra, n=221):
- **accuracy on covered subset = 0.947** (18/19) -- substrate-symbolic solving is HIGHLY accurate where it applies.
- **substrate recall-fidelity = 1.000** -- perfect operand store/recall (the PP-341 role holds).
- **coverage = 0.086** (19/221) -- only ~9% of level-1 are clean-symbolic (arithmetic/linear-eq); the rest are WORD-PROBLEMS.

Verdict MIDDLE (coverage 0.086 < 0.15 gate; accuracy 0.947 and fidelity 1.0 decisively pass).

## Finding (confirms your direction)
The substrate-symbolic capability is REAL + high-accuracy. The bottleneck is COVERAGE -- word-problems dominate level-1 and
need the NL-extraction stage. This directly justifies your **substrate-only word-problem extraction pipeline** (POS tagger +
dep-parse + quantity extraction -> substrate symbolic solve). MATH-LIGHT is the existence proof that the symbolic-solve BACK
END works (0.947); the word-problem FRONT END (extraction) is the next build to expand coverage.

Honest architecture note: per PP-341, substrate's role here = operand storage/recall (fidelity 1.0); the compute is closed-form.
Not a black-box solver. The word-problem pipeline would add the substrate POS/parse front-end.

Recommend: proceed to the word-problem extraction pipeline (your Day 2-3 item) as the coverage-expander. MATH-LIGHT MIDDLE
(coverage-limited) is the honest baseline.
