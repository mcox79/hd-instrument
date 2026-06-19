# Pre-reg: Wave 14 VAMP-on-Chain K-Stress at N=65536 v1

**Filed:** 2026-05-22
**Source:** Strategy cycle 127 VAMPCHAIN_RESTORES PERFECT at K=100; Product Demo 1 (Lane D agent memory SDK) targets agent-realistic K=1K-10K.

## Question

Does VAMP-on-chain at N=65536 d=50 sustain acc ≥ 0.50 as stored fact count grows from K=100 → K=500 → K=1000 → K=5000?

## Hypothesis

H_agent_ready: K=5000 acc ≥ 0.50 — substrate supports agent-realistic deep-chain memory.

H_small_only: K=500 PASS but K=5000 < 0.50 — Demo 1 positions as small-cardinality only.

## Pre-declared verdicts

- `K_STRESS_AGENT_READY` — K=5000 acc ≥ 0.50.
- `K_STRESS_SMALL_AGENT` — K=500 acc ≥ 0.50 AND K=5000 < 0.50.
- `K_STRESS_LIMITED` — K=500 acc < 0.50.
- `K_STRESS_INCONCLUSIVE` — metric collection error.

## Method

For each K ∈ {100, 500, 1000, 5000} at N=65536, d=50:
- num_entities = K (so entities used by chain are diverse).
- Build factbase M with depth+1 chain entities, K-depth distractor facts.
- Run VAMP-on-chain forward-backward EP.
- 15 trials × 2 seeds.

## Acceptance thresholds

- 0.50 PASS matches existing multi-hop rehab threshold.

## Config

- N=8192 smoke, 65536 full.
- depth=50 (matches cycle 127 baseline).
- num_relations=20.
- K_grid full: [100, 500, 1000, 5000].
- n_trials=15, 2 seeds.

## Pre-declared interpretation

- **AGENT_READY**: Demo 1 Lane D agent memory SDK positions at full agent-realistic K=5000+. Substantial substrate-product implication.
- **SMALL_AGENT**: Demo 1 narrows to small-cardinality agent memory (~500 facts). Still useful but bounds positioning.
- **LIMITED**: VAMP-on-chain doesn't scale past K=100. Substrate-product positioning narrower than predicted.

## Cost

K=5000 codebook + factbase + chain query: ~5-10s per chain. Total ~5-15 min.

## Not in scope

- K > 5000 (cost prohibitive at depth=50).
- Depth + K joint sweep (separate experiments).
- Codebook structure beyond random ±1.
