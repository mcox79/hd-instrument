# Pre-reg: novel_query_construction_v1_n4096

**Date:** 2026-05-30
**Anchor:** novel_query_construction_v1_n4096 (S13, E3.5)
**Script:** experiments/exp_novel_query_construction_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Combinatorial reasoning over stored single-hop
facts.

## Hypothesis

At least one path achieves >=60% accuracy on novel-query construction
at depth 3-4 (where substrate stores ONLY single-hop facts).

## Pre-registered bands

| Outcome      | Condition                                                                |
|--------------|--------------------------------------------------------------------------|
| HARD_PASS    | At least one path >=60% accuracy at depth 3 or 4                         |
| HARD_FAIL    | All paths <20% (no combinatorial reasoning)                              |
| MIDDLE_BAND  | otherwise                                                                |

## Uncertainty

P=0.30-0.50 prior per user msg. Annotated: this is a speculative but
enabling test. If positive, opens a new substrate capability axis. If
negative, this is a clean refutation of compositional generalization
from single-hop facts.

## Self-test

- N == 4096 (PROT-018).
- Smoke at N=1024 M=64 depth=2 produces non-zero accuracies (smoke is at
  trivial depth-2 where path closure is near-deterministic).

## Construct procedure

Novel queries = (start, expected_end) where the relation transitively
chains through the stored facts. Substrate is given ONLY (k, v) pairs;
the test asks whether multi-hop combination of those single-hop facts
succeeds.

## Timeout estimate

2 depths x 5 seeds = 10 cells. Per cell ~10s for 16 novel queries
through 3 paths. ~100s + GPU overhead. **timeout_s = 14400** per user
spec.

## Production config

N=4096, M=2048, depths=[3,4], K_paths=100, seeds=[7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
