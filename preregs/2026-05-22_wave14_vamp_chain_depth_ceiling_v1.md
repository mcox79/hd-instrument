# Pre-reg: Wave 14 VAMP-on-Chain Depth Ceiling v1

**Filed:** 2026-05-22
**Source:** Strategy cycle 127 VAMPCHAIN_RESTORES PERFECT acc_50hop=1.000. Push the ceiling.

## Question

Does VAMP-on-chain (tree-exact forward-backward EP) sustain acc ≥ 0.50 at d=100, 200, 500 hops at N=65536 K=200, extending the cycle 127 PERFECT result at d=50?

## Hypothesis

H_high: acc(d=200) ≥ 0.50 — substrate's deep-chain ceiling is substantially above 50 hops.

H_low: acc(d=100) < 0.50 — d=50 was near the ceiling.

## Pre-declared verdicts

- `DEPTH_CEILING_HIGH` — acc(d=200) ≥ 0.50.
- `DEPTH_CEILING_MID` — acc(d=100) ≥ 0.50 AND acc(d=200) < 0.50.
- `DEPTH_CEILING_LOW` — acc(d=100) < 0.50.
- `DEPTH_CEILING_INCONCLUSIVE` — metric collection error.

## Method

For each depth ∈ {50, 100, 200, 500}:
- Run VAMP-on-chain forward-backward EP at N=65536, K=200 stored facts (raised from K=100 to support longer chains; num_entities=300 to support depth=200 chain through unique entities).
- 15 trials × 2 seeds.

## Acceptance thresholds

- 0.50 PASS matches existing rehab threshold.

## Config

- N=8192 smoke, 65536 full.
- num_entities=300, num_relations=20, num_facts=200.
- hop_depths full: [50, 100, 200, 500].
- n_trials=15, 2 seeds.

## Pre-declared interpretation

- **HIGH**: substrate-product positioning extends to d=200+ deep reasoning. Demo 1 (Lane D agent SDK) deep-chain claim broadens substantially.
- **MID**: d=100-200 ceiling characterized. Demo 1 positioning bounded but reasonable.
- **LOW**: d=50 was near ceiling. Investigate why VAMP-on-chain breaks at larger d (chain compounding error? prior-saturation?).

## Cost

VAMP-on-chain at d=500 × 15 trials × 2 seeds at N=65536: each chain ~3-5 sec; total ~3-10 min.

## Not in scope

- K-stress (separate experiment).
- Iterative-EP refinement.
- Multi-target inference.
