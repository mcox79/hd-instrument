# Pre-registration: Wave 3a.5 — Catastrophic forgetting mitigations

Date: 2026-05-18
Status: Pre-registered, queued after Wave 3a
Experiment file: [exp_continual_mitigations.py](../experiments/exp_continual_mitigations.py)
Runner: [run_mitigation_chunks.py](../experiments/run_mitigation_chunks.py)

## Hypothesis (H)

The +2.15 bpc catastrophic forgetting observed on FHRR/sequential_AB in
Wave 3a is decomposable into three architectural mechanisms:

H1: Multiplicative weight decay contributes ≥ 1.0 bpc to forgetting. Turning
off decay during Phase 2 (`decay_off_P2`) should recover ≥ 1.0 bpc of A.

H2: W overwriting (new B-target updates pushing W away from A's mapping)
contributes ≥ 0.5 bpc. Freezing W during Phase 2 (`W_frozen_P2`) should
recover ≥ 0.5 bpc beyond the `decay_off_P2` recovery.

H3: Pool overwriting (Phase 2's ring buffer replacing A pool with B
contexts) contributes ≥ 0.1 bpc. Dual pool (`dual_pool`) should recover
that much.

H4 (substrate-level): SBC's sparse codes produce less interference than
FHRR/BSC at baseline (no mitigation). SBC baseline forgetting < FHRR
baseline forgetting by ≥ 0.5 bpc.

## Cited mechanisms / papers

- Yildiz et al. 2024 arXiv:2402.17400 — continual pretraining forgetting
  curves. Standard practice: anchor forgetting on bpc_best(A).
- Bricken et al. 2023 arXiv:2303.11934 *Sparse Distributed Memory is a
  Continual Learner* — substrate-level claim that sparse codes
  pattern-separate.
- Kirkpatrick et al. 2017 *Elastic Weight Consolidation* — penalize
  changes to important weights. We test simpler `W_frozen_P2` here.
- Robins 1995 *Catastrophic forgetting and rehearsal* — pool replay /
  dual pool is the simplest classical defense.

## Operational definition

For each (substrate, mitigation) cell, run sequential_AB with the
mitigation active during Phase 2 only:

- **`baseline`**: no mitigation. Replicates Wave 3a sequential_AB.
- **`decay_off_P2`**: `decay = 0` during Phase 2 batches; otherwise identical.
- **`W_frozen_P2`**: W is read but NOT updated during Phase 2; pool can
  still be written.
- **`dual_pool`**: Phase 2 writes to a separate `pool_B`; `pool_A` is
  preserved. Pool retrieval at test time combines both, weighted by
  occupancy.

Factorial: 3 substrates × 4 mitigations = 12 chunks.
Chunked runner with incremental save per (substrate, mitigation).

## Falsification criteria (machine-readable)

For each hypothesis, support requires the predicted recovery; reject if
the recovery is within ±0.1 bpc of the baseline (no effect).

H1: |forgetting(FHRR, decay_off_P2) − forgetting(FHRR, baseline)| ≥ 1.0
H2: |forgetting(FHRR, W_frozen_P2) − forgetting(FHRR, decay_off_P2)| ≥ 0.5
H3: |forgetting(FHRR, dual_pool) − forgetting(FHRR, baseline)| ≥ 0.1
H4: forgetting(SBC, baseline) < forgetting(FHRR, baseline) by ≥ 0.5

## Pre-mortem (top 3 failure modes)

1. **`W_frozen_P2` produces unusable predictions** — if W can't update,
   the system can't learn B at all, and B_after_P2 stays at random
   (~5 bpc). The "B never gets learned" result is the same as "I never
   tried to learn B" — uninformative. Mitigation: report B_after_P2
   alongside A_after_P2; if B stays at random, the test is
   unfortunately a "what does pool alone do" measurement, not a
   forgetting decomposition.

2. **`dual_pool` doesn't help because pool's contribution is small** —
   we already measured (α sweep) that pool contributes ~0.20 bpc.
   Even preserving the pool perfectly recovers at most 0.20 bpc, not
   the 2.15 bpc gap. Likely outcome: H3 supported with the small
   predicted effect (~0.1 bpc). This is informative but not headline.

3. **`decay_off_P2` causes W to explode** — without decay, W grows
   unboundedly during Phase 2's 120K updates. May crash or diverge.
   Mitigation: track ||W|| Frobenius; if W explodes, retry with a
   moderate decay (e.g., 1e-5) rather than zero.

## Parameter-matched non-bio control

Each substrate × baseline cell already serves as control. The
**comparison across mitigations within a substrate** isolates the
architectural component being tested.

The Wave 3a sequential_AB results we already have (FHRR baseline +2.15)
are the matched baseline.

## Expected wall time

- Phase 1 (A training, 15 epochs): same as A_only ~60-100s per substrate
- Phase 2 (B training, 15 epochs): same as B_only ~300-700s per substrate
- Total per cell: ~5-12 min depending on substrate
- 12 cells = ~1.5-2 hours total

## Decision tree

| Outcome | Interpretation | Next step |
|---|---|---|
| H1 supported (decay_off recovers ≥1.0) | Decay alone is the dominant forgetting mechanism. | Test smaller decay values (1e-5, 1e-6) as a less drastic fix. |
| H1 rejected | Decay isn't doing most of the damage; overwriting is. | Investigate why; could be substrate-specific. |
| H2 supported (frozen_W recovers another ≥0.5) | New B-target updates are pushing W away from A. | Mitigation: per-byte W updates only modify relevant rows? |
| H3 supported (dual_pool recovers ≥0.1) | Pool retention matters proportional to pool's overall contribution. | Larger pool sizes during Wave 4+. |
| H4 supported (SBC baseline forgets less than FHRR) | Sparse codes empirically pattern-separate at our scale. | Validates Bricken 2023. Big result. |
| H4 rejected (SBC ≈ FHRR baseline forgetting) | Pattern separation doesn't help at our N. Bottleneck is architectural, not substrate. | Substrate doesn't matter for continual learning at this scale. |

## What we'll learn

- **Decomposition of the +2.15 bpc forgetting** into mechanisms.
- **Whether substrate sparsity matters** for continual learning at our scale.
- **What's the lowest-effort architecture mitigation** that helps most.

This experiment is diagnostic + mechanistic, not just descriptive. The
findings directly inform whether future Wave 4-7 architectures need
explicit forgetting mitigations baked in.
