# Prereg: q_b1_heteroassoc_chain_cert_v1_n4096

**Date:** 2026-06-02
**Anchor:** q_b1_heteroassoc_chain_cert_v1_n4096
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_q_b1_heteroassoc_chain_cert_v1_n4096.py

## Scientific question

Q-B1 at N=4096: Does heteroassociative directed-chain depth-3 retrieval achieve fidelity
>= 0.80, AND can any single directed binding be exactly algebraically deleted (zero residual)?
Tests reasoning-chain primitive + deletion certificate. Orthogonal to capacity work.

## Pre-registered bands

HARD-PASS:
  depth-1 fidelity >= 0.90 (cosine_sim between retrieved and target at depth 1)
  depth-3 chain fidelity >= 0.80
  deletion_sim <= 0.50 (link broken after deletion)

MIDDLE:
  depth-1 >= 0.90 but depth-3 in [0.60, 0.80)

HARD-FAIL:
  depth-3 fidelity < 0.60

COMPOSITION CLASSIFICATION: HANDOFF (per-hop independence).

## Smoke result (pre-ship gate)

Run: N=4096, 5 chains, M_bg=10, 2 seeds, 20 trials.
Result: HARD_PASS. depth1=0.997, depth3=0.996, deletion_sim=-0.005.
Elapsed=17.1s.

Walk-back: far above HP thresholds (d >> 1). No walk-back.

## Timeout estimate

Smoke: 17.1s at N=4096, 5 chains, 2 seeds, 20 trials, M_bg=10.
FULL: N=4096, 15 chains, 5 seeds, 50 trials, M_bg=30.
scaling_exp = 1.5 (matrix builds + retrieval operations).
timeout_s = ceil(1.5 * 17.1 * (5/2)^1 * (15/5)^1 * (50/20)^1) = ceil(1.5 * 17.1 * 2.5 * 3 * 2.5)
          = ceil(481) = 600s. Rounded to 1800s (heteroassoc matrix build at N=4096 with M_bg=30).

## N-suffix binding (PROT-018)

Anchor name contains _n4096; script production N=4096 confirmed.

## Cap_map connection

Validates Q-B1 heteroassociative reasoning chain + deletion cert at N=4096.
Row: heteroassociative binding / directed chain (🔬 pending).
