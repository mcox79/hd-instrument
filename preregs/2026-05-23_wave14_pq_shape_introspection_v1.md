# Pre-reg: P(q) shape introspection (Strategy 10:03 v151 P6 Cap 4)

Compute P(q) moments (mean, std, skew, kurt) across 3 phases (low-K K=100, K-resonance K=1000, high-K K=3000). moment_separation = mean pairwise mean-distance / pooled_std. N=8192, n_seeds=20 per phase.

## Verdicts
- `PQ_INTROSPECTION_DETECTS` — moment_separation >= 1.5 (substrate phase distinguishable from P(q)).
- `PQ_INTROSPECTION_PARTIAL` — 0.5 <= sep < 1.5.
- `PQ_NO_PHASE_SIGNATURE` — sep < 0.5.
