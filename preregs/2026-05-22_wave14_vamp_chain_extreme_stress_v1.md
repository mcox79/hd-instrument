# Pre-reg: Wave 14 VAMP-on-Chain Extreme Stress v1

**Filed:** 2026-05-22
**Source:** Cycle 128 VAMP-on-chain DEPTH_CEILING_HIGH (PERFECT through d=200, cliff at d=500) + K_STRESS_AGENT_READY (PERFECT through K=5000). Push further.

## Question

What is the substrate's K-ceiling beyond K=5000 (test K=10000, 50000, 100000) AND where exactly does the depth cliff land between d=200 and d=500 (test d=300, 400)?

## Hypothesis

H_high: K_ceiling ≥ 10000 AND depth_ceiling ≥ 400.

H_bounded: K_ceiling at ~5000 OR depth_ceiling at ~200 (cliffs near previously-tested).

## Pre-declared verdicts

- `EXTREME_HIGH` — K_ceiling ≥ 10000 AND depth_ceiling ≥ 400.
- `EXTREME_MID` — K_ceiling ≥ 5000 AND depth_ceiling ≥ 200.
- `EXTREME_BOUNDED` — tighter bounds than confirmed.
- `EXTREME_INCONCLUSIVE` — metric collection error.

## Method

**Axis 1 (K-stress at d=50)**: K ∈ {5000, 10000, 50000, 100000}. num_entities=K.
**Axis 2 (depth-cliff at K=200)**: d ∈ {200, 300, 400, 500}.
10 trials per (K, d) cell, single seed=17.

## Acceptance thresholds

- 0.5 PASS per cell.
- Ceiling = max value where PASS.

## Config

- N=8192 smoke, 65536 full.
- num_relations=20.
- Single seed=17 (cost-driven; multi-seed only if interesting).

## Pre-declared interpretation

- **HIGH**: VAMP-on-chain ceiling characterization shows massive substrate-product headroom. Demo 1 deep-chain claim extends to enterprise-scale (K=10K-50K facts) AND multi-step reasoning (200+ hops).
- **MID**: previously-tested ceilings confirmed; no further extension. Still substantially exceeds initial cycle 127 K=100 d=50 baseline.
- **BOUNDED**: substrate has tighter ceilings than expected; useful for honest positioning of Demo 1.

## Cost

K=100000 codebook at N=65536: ~6.5GB for codebook (bipolar float32). Fits in 16GB. Per-chain cost: matmul over 100K patterns, ~1-3s/chain. 10 trials × 4 K values × 2 axes = ~10-20 min total.

## Not in scope

- Joint K-stress + depth stress (single-axis only).
- Multi-seed (single seed cost-driven scan).
- K > 100000.
