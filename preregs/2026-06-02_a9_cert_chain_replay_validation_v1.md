# Prereg: a9_cert_chain_replay_validation_v1

**Date:** 2026-06-02
**Anchor:** a9_cert_chain_replay_validation_v1
**Queue:** remote_cpu_queue

## Scientific question
Cert chain (K=100 writes, N=1024) replays to W_orig within relative Frobenius error < 1e-10.

## Pre-registered thresholds
- HP1: replay_rel_err < 1e-10 (algebraic identity; float64 deterministic).
- HP2: retrieval accuracy from replayed W >= 0.90.
- HP3: cert chain length = K = 100 exactly.
- HARD-PASS: all 3 HP in >= 4/5 seeds.
- HARD-FAIL: replay_rel_err > 1e-4.
- MIDDLE: rel_err in [1e-10, 1e-4] (float32 range).

## Timeout estimate
smoke_wall_s = 0.02s at N=256 K=30. FULL N=1024, K=100, 5 seeds: estimated 5s per seed.
timeout_s = ceil(1.5 * 5 * 5) = **60s**.
