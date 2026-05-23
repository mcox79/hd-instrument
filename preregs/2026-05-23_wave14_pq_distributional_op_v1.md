# Pre-reg: P(q) distributional order parameter (Strategy 09:45 PRIORITY A)

Test Research's distributional-OP hypothesis. 50-seed q_overlap measurement at N=65536, K=100, depth=50, n_starts=100; report mean, std, skewness, bimodality, fraction above 0.85.

## Verdicts
- `PQ_DIST_OP_PASS` — mean >= 0.85 AND std < 0.05 (substrate has distributional OP; Gap 2 was tool-not-substrate).
- `PQ_DIST_OP_WIDE` — mean >= 0.85 but std >= 0.05 (non-self-averaging high mean).
- `PQ_DIST_OP_BIMODAL` — P(q) bimodal (hidden symmetry breaking; 2 phases).
- `PQ_DIST_OP_FAIL` — mean < 0.85 (substrate genuinely lacks OP).
