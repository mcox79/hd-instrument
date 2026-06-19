# Pre-registration: implicit_gram_solve_v1

**Date:** 2026-06-02
**Anchor:** implicit_gram_solve_v1
**Script:** experiments/exp_implicit_gram_solve_v1.py
**Queue:** remote_cpu_queue
**Timeout:** 2700s

## Scientific question (Q-A4)

Does Gram-solve retrieval (Xi @ solve(Xi@Xi^T/N + eps*I, Xi@q/N)) deliver
equivalent quality to standard Hopfield retrieval (sign(W@q)) while using
much less memory (Gram M×M vs W N×N)?

## Bands (pre-registered)

**HARD-PASS (HP):**
- min_delta (gram_acc - hop_acc) >= -0.05 (within 5% of Hopfield baseline)
- mem_ratio = M^2 / N^2 < 0.10 at M=500, N=4096 (confirmed by formula)

**MIDDLE:**
- min_delta in [-0.15, -0.05)

**HARD-FAIL (HF):**
- min_delta < -0.15 (Gram-solve significantly worse than Hopfield)

## Smoke result
HARD_PASS: min_delta=+0.000 (HP>=-0.05), mean_hop=0.999, mean_gram=1.000.
Memory: mem_ratio=0.00015-0.015 (well below 0.10).
Wall time: <5s (2 seeds). FULL estimate: ~300s (5 seeds, M=[50,100,200,500,1000]).

## PROT-018
No _nN suffix. Production N=4096 declared in script.
