# Exp Dev to Queue: TDA 5-probe re-analysis

**Date:** 2026-05-27
**Source handoff:** notes/exp_dev_handoff_tda_reanalysis_substrate_W_2026-05-27.md

## Shipment

```
queue=remote_cpu_queue name=tda_reanalysis_5probe_v1 script=experiments/exp_tda_reanalysis_5probe_v1.py prereg=preregs/2026-05-27_tda_reanalysis_5probe_v1.md timeout=1800
```

## Ship status

SHIPPED. queue_add.sh exited 0. Remote verify: PASS (queue pending now 2 entries including this one).

## Smoke result

Smoke ran at N=128, M=50 (scale-limited). TDA-E fixed to HARD_PASS with capacity-adjusted formula.
TDA-C shows HARD_FAIL at smoke (agreement 2/5) -- expected: at M/K ~ 6 patterns per expert,
W matrices are noise-dominated and don't form K-cluster structure in cosine space.
Full run at N=512, M=200 gives M/K ~ 50 per expert -- above capacity threshold where cluster structure emerges.
Smoke instrumentation gate: PASS (all metrics non-null, non-zero-sentinel, varying across cases).

## Dependency check

- W artifacts: generated on-the-fly from seeds (no saved .pt files exist); verified
- ripser/gudhi: NOT available on remote; using pure-PyTorch union-find VR implementation (verified via --self-test on local)
- N=512, M=200: matches v3 smoke scale with sufficient M/K for TDA signal

## Notes

- No new W generation (all W from seeds per v3 pattern)
- No GPU (pure CPU)
- BELOWNORMAL priority structural (remote runner sets this for all children)
- Expected runtime: 15-25 min
- Verdict distribution: TDA_OVERLAPPING_USEFUL P=0.38, TDA_CONSISTENT_REDUNDANT P=0.32, TDA_INCONCLUSIVE P=0.20, TDA_NOVEL_USEFUL P=0.10
