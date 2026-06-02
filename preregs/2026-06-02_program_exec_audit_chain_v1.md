# Pre-registration: program_exec_audit_chain_v1

**Date:** 2026-06-02
**Anchor:** program_exec_audit_chain_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_program_exec_audit_chain_v1.py

## Scientific question (9-Handoff: program execution trace audit)
Can a heteroassociative Hopfield chain record and replay a program execution trace?
Three cells tested:
  A: Noisy content-addressed retrieval (30% bit-flips as cue -> cosine >= 0.80)
  B: Heteroassociative next-step prediction (W_chain += outer(xi_{t+1}, xi_t)/N; >= 0.70)
  C: Audit trail deletion (standard W -= outer(xi,xi)/N; residual_cos < 0.15; delta_acc < 0.10)

## Pre-registered thresholds
- HARD-PASS: cell_A >= 0.80 AND cell_B >= 0.70 AND del_residual < 0.15 AND delta_acc < 0.10
- MIDDLE: (cell_A >= 0.70 OR cell_B >= 0.60) AND del_residual < 0.25
- HARD-FAIL: cell_A < 0.70 OR cell_B < 0.60 OR del_residual >= 0.30

## Calibration note
Heteroassoc chain with W_chain proven in heteroassoc_chain_depth3_v1 (completed).
Deletion standard erasure; noisy probe uses 30% bit-flip rate (empirically robust).

## Smoke result
HARD_PASS: cell_A=0.986, cell_B=1.000, del_residual=0.098 (smoke N=1024, chain_len=5, 2 seeds)
