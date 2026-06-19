# Pre-registration: multi_tenant_arch1_full_v1_n16384

**Filed**: 2026-06-01 by exp_dev
**Anchor name**: multi_tenant_arch1_full_v1_n16384
**Queue**: remote_cpu_queue
**Script**: experiments/exp_multi_tenant_arch1_full_v1_n16384.py

## Context

N=16384 intermediate envelope-extension for PP-13 (Multi-tenant isolation, 0.75-0.90 VALIDATED).

Prior result: multi_tenant_arch1_adversarial_smoke_v1_n4096 -> MT_ARCH1_HARD_PASS
(zero cross-tenant leakage, 5 seeds at N=4096, v317 batch cap_map annotation).

Per notes/routed_completed/exp_dev_n32768_envelope_sizing_dry_run_2026-06-01.md:
  Staged escalation N=4096 -> N=16384 -> N=32768.
  N=4096 HARD_PASS is pre-condition for N=16384 dispatch (confirmed).
  N=16384 HARD_PASS is pre-condition for N=32768 dispatch (this anchor provides it).

Strategic value: PP-13 multi-tenant isolation is part of the primary product narrative
("physics-grade-not-policy-grade" algebraic guarantees). N=16384 validation closes the
gap between proof-of-concept N=4096 and production-scale requirements.

## Scientific question

Does the mathematical zero cross-tenant leakage property hold at N=16384 (log2=14 even)?
Both Pattern-1 (direct key-space query) and Pattern-2 (codebook-collision attack) should
produce zero contamination -- isolation is a linear-algebra property of disjoint W matrices
independent of N. This experiment confirms the expected behavior empirically.

## Design

N=16384, M_per_tenant=256 (alpha=M/N = 0.016), 5 seeds, FULL run.
Two tenants A and B, fully disjoint key/val sets.
Pattern-1: A queries B's key space using W_A -> should yield 0 contamination.
Pattern-2: craft query with partial overlap of A's codebook atoms, query W_B -> should yield
           low max_sim (< 0.8 threshold) due to near-orthogonality at high N.

Memory footprint: W_A = W_B = 16384^2 * 4 bytes = 1 GiB each.
  Total peak: ~2.5 GiB (sequential allocation, W_A freed before Pattern-2).
  Fits within 32 GiB remote CPU (marsh@home).

## Pre-registered threshold bands

**HARD-PASS**: MT_ARCH1_HARD_PASS
  Criteria: contamination_rate_p1 = 0.000 AND contamination_p2 = 0 in ALL 5 seeds.
  Expected: replicates N=4096 result at N=16384 (isolation is N-independent for disjoint W).

**HARD-FAIL**: MT_ARCH1_HARD_FAIL
  Criteria: contamination_rate_p1 > 0 in ANY seed.
  Treatment: cap_map PP-13 BAND-HOLD; route to research for N-scaling contamination analysis.
  Threshold: 0 tolerance (even 1 seed leaking = HARD-FAIL).

**MIDDLE-BAND**: MT_ARCH1_MIDDLE_BAND
  Criteria: contamination_rate_p1 = 0 in all seeds BUT contamination_p2 > 0 in some seeds.
  Treatment: Pattern-1 isolation holds at scale; Pattern-2 borderline; PP-13 BAND-HOLD partial.

## Timeout estimate

W construction O(N^2 * M) at N=16384 M=256:
  numpy matmul (256, 16384) @ (16384, 256).T -> (16384, 16384): ~30-60s per tenant per seed
  2 tenants * 5 seeds * ~45s avg = ~450s base
  Query operations: O(n_query * N^2) = 200 * 16384^2 * 4 bytes ~= additional ~30s
  Total per seed: ~100s. Total 5 seeds: ~500s.
  timeout_s = ceil(1.5 * 100 * 1.0 * 5) = ceil(750) = 750s
  -> PROT-019 floor for _n16384: 21600s
**timeout_s = 21600** (PROT-019 floor)

scaling_exp = 1.0 (W construction is a single matmul per seed; no super-linear depth)

## N-suffix section

N-suffix: _n16384 binds N_FULL = 16384.
smoke N = 1024 (selftest); production N = 16384. Matches anchor name.

## Walk-back gate

Smoke at N_SMOKE=1024 yields near-zero contamination (expected from theory).
Effect size: isolation_confirmed binary (0/1). No d<1.0 borderline case expected.
N x2 not needed (isolation is binary, not a gradient measurement).

## PROT compliance

- PROT-018: N_FULL = 16384 matches _n16384 suffix
- PROT-019: timeout_s = 21600 (PROT-019 floor for _n16384)
- PROT-021: checkpoint key format M{M_cfg}_{run_mode}_seed{seed}; run_config passed
