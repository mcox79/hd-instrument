# Pre-reg: Avalanche size distribution P(dE) (Wave 14 Observability V2 — Strategy 07:05 P-B-3)

Argmax-relaxation avalanche histogram. Collect dE per spin-flip across 100 runs from random init, T_relax=50, N=8192, K=100. Fit P(dE) ~ dE^(-tau) on log-log; extract tau, r2.

## Verdicts
- `AVAL_ABBM_FIT` — 1.3 < tau < 1.7, r2 >= 0.7 (ABBM mean-field 3/2 universality).
- `AVAL_STEEPER` — tau >= 1.7, r2 >= 0.7 (steeper than ABBM, RS-phase).
- `AVAL_SHALLOWER` — tau <= 1.3, r2 >= 0.7.
- `AVAL_NONPOWER` — r2 < 0.7 (no power-law).
