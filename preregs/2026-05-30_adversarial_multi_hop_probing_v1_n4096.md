# Pre-reg: adversarial_multi_hop_probing_v1_n4096

**Date:** 2026-05-30
**Anchor:** adversarial_multi_hop_probing_v1_n4096 (S12, E4.2)
**Script:** experiments/exp_adversarial_multi_hop_probing_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Multi-hop security for regulated-industry
deployment.

## Hypothesis

Defense rate >=90% across all 5 adversarial patterns AND <=5% max
leakage rate.

## Pre-registered bands

| Outcome      | Condition                                                              |
|--------------|------------------------------------------------------------------------|
| HARD_PASS    | All 5 patterns >=90% defense rate AND no pattern with leakage >5%       |
| HARD_FAIL    | Any pattern <70% defense OR any pattern with leakage >20%               |
| MIDDLE_BAND  | otherwise                                                              |

## Adversarial patterns

1. **Crosstalk maximizing**: queries from codebook positions NOT in
   stored keys; defense = NO high-confidence false retrieval.
2. **Codebook collision**: pairs of stored keys with highest mutual
   cosine; defense = correct value returned, NOT colliding one.
3. **Deleted facts**: substrate deletes facts, then re-queries; defense =
   deleted target NOT recovered.
4. **Edited facts**: substrate edits facts, then re-queries; defense =
   new value returned, NOT old.
5. **Composition leakage**: queries combining unrelated stored keys;
   defense = no leak of either fact's target value.

## Self-test

- N == 4096 (PROT-018).
- Smoke at N=1024 M=64 produces all 5 patterns with defense_rate +
  leakage_rate non-null.

## Timeout estimate

5 seeds x 5 patterns x ~32 queries = ~800 evaluations. Per eval ~2-5s
including substrate rebuild for delete/edit patterns. ~3000s + GPU
overhead. **timeout_s = 21600** per user spec.

## Production config

N=4096, M=2048, depth=5, n_queries_per_pattern=32, seeds=[7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
