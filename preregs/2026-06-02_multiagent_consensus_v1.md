# Pre-registration: multiagent_consensus_v1

**Date:** 2026-06-02
**Anchor:** multiagent_consensus_v1
**Queue:** remote_cpu_queue

## Hypothesis
W-averaging over K agents implements substrate majority-vote protocol: the majority-written
pattern wins in >= 85% of seeds for both K=5 (3/5 majority) and K=7 (4/7 majority).

## Pre-registered thresholds
- HARD-PASS: win_rate_A >= 0.85 AND win_rate_B >= 0.85.
- MIDDLE: 0.65 <= win_rate_A < 0.85.
- HARD-FAIL: win_rate_A < 0.65.

Theory: majority coefficient (3/5 vs 2/5) = 1.5x signal advantage. Should dominate at N=4096.

## Smoke result
N=4096, M_per_agent=20, 2 seeds:
- cell_A win_rate=1.000 (K=5, 3 majority)
- cell_B win_rate=1.000 (K=7, 4 majority)
- HARD_PASS smoke. Smoke wall: 4.5s.

## Timeout estimate
Smoke wall: 4.5s / 2 seeds = 2.25s/seed.
Full: 5 seeds. wall = 1.5 * 2.25 * 5 = 16.9s. timeout=150s.
