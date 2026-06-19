# Pre-registration: effective_rank_sweep_v1

**Date:** 2026-06-02
**Anchor:** effective_rank_sweep_v1
**Script:** experiments/exp_effective_rank_sweep_v1.py
**Queue:** remote_cpu_queue
**Timeout:** 1800s

## Scientific question

Is r_eff = exp(H(sigma)) (entropy of squared singular value distribution)
monotone increasing in M for M below capacity (M < N/4 at N=4096)?

## Bands (pre-registered)

**HARD-PASS (HP):**
- frac_monotone >= 0.80 (80% of sweep pairs show r_eff[M+1] > r_eff[M])
- mean r_eff/M >= 0.50 for M below capacity

**MIDDLE:**
- frac_monotone in [0.60, 0.80)

**HARD-FAIL (HF):**
- Non-monotone in >= 60% of pairs (r_eff actually DECREASING in M)

## Smoke result
HARD_PASS: frac_monotone=1.00 (HP>=0.80), mean_r_eff/M=0.966 (HP>=0.5).
Wall time: <5s (2 seeds). FULL estimate: ~300s (5 seeds, M=[10,20,50,100,200,500,1000]).

## PROT-018
No _nN suffix. Production N=4096 declared in script.
