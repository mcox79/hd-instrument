# Prereg: csp_hebbian_coexist_v1

**Filed:** 2026-06-01
**Anchor:** csp_hebbian_coexist_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_csp_hebbian_coexist_v1.py

## Hypothesis

W = W_csp + W_data can simultaneously (a) converge to a planted bipartite MAX-CUT
encoded in W_csp and (b) retrieve M=20 independently stored Hebbian patterns.

## Pre-registered bands

- HARD-PASS: cut_ratio >= 0.80*OPT on >= 4/5 seeds AND retrieval_accuracy >= 0.90 on >= 4/5 seeds.
- MIDDLE: one objective passes HP, the other is middling (0.50 to HP threshold). MODAL EXPECTED.
- HARD-FAIL: cut_ratio < 0.50*OPT on >= 3/5 seeds OR retrieval_accuracy < 0.50 on >= 3/5 seeds.

P(HP)=0.35, P(MID)=0.40, P(HF)=0.25.

## Design

N=1024, M_data=20 (alpha~0.020), W_csp = planted bipartite. 20 restarts, 200 steps. 5 seeds.

## Timeout estimate

smoke_wall_s ~ 10s, timeout_s = 300 (floor).

## N-suffix note

No _nN suffix. Production N = 1024; CSP-with-learning test at M << alpha_c*N.
