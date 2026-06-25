# Cell — substrate_multihop_consolidation_v2_proper_test_v1

Director formal spec for the PROPER consolidation cell that actually tests the mechanism Cell 4 failed to test.

Per Skunkworks tier ruling on Cell 4 (`notes/skunkworks_tier_ruling_cell3_cell4_consolidation_2026-06-25.md`): Cell 4 was MM not chain-grade because K_THRESH=1 wrote the answer-tuple directly as a 1-hop atom → retrieval was recall not chain. META_M4 + META_M5 atomized.

This v2 spec fixes those issues to genuinely test whether consolidation can close Barrier 1.

## What Cell 4 got wrong (lessons baked into v2)

1. **K_THRESH=1 = answer-pre-encoding**. v2 uses K_THRESH = 3 minimum (preferably grid-tested at 3, 5, 10) so consolidation only fires after the chain has been observed multiple times under genuine traversal — bypasses the "write-then-read" trap
2. **Test chains visible at consolidation time = recall**. v2 holds out 20% of chains from the consolidation pass; those held-out chains are NEVER fed to the consolidator, so their compound atoms cannot be pre-stored
3. **Chain construction mismatch with baseline = apples-to-oranges**. v2 uses `make_two_hop_chains(p1=0, p2=1)` fixed-pair construction matching last night's beta-sweep regime; baseline NAIVE_HARD_2HOP MUST reproduce 0.65 within ±0.03

## Cell anchor

`substrate_multihop_consolidation_v2_PROPER_TEST_v1`

## Lane / routing / config

- Lane 1 (substrate-native)
- Routing: remote_cpu_queue (CPU-feasible; no training)
- Config: V_C=200, V_P=10, N=8192, K_SET=20, **make_two_hop_chains(p1=0, p2=1)** fixed-pair (matches beta-sweep), 3 seeds [7, 17, 23]
- n_chains_train=200 (visible at consolidation), n_chains_heldout=50 (NEVER visible to consolidator; tests genuine chain closure)
- K_THRESH grid: [1 (control; reproduces Cell 4 saturation), 3, 5, 10]

## Arms (6; one knob varies)

1. **ARM_NAIVE_HARD_2HOP** (control; sanity-rail to 0.65 ± 0.03)
2. **ARM_CONSOL_KTHR_1_CONTROL** (replicates Cell 4 K_THRESH=1 explicitly; should hit ~1.000 on TRAINING chains; should hit ~baseline on HELDOUT chains — proves the by-construction trap)
3. **ARM_CONSOL_KTHR_3** (consolidate after 3 observations; substantive memory primitive test)
4. **ARM_CONSOL_KTHR_5** (consolidate after 5 observations; resource-efficient)
5. **ARM_CONSOL_KTHR_10** (high threshold; only consolidate the most frequent chains)
6. **ARM_HYBRID_KTHR_3_PLUS_CLEANUP** (Wave14R-style cleanup for non-consolidated chains + consolidation for frequent)

## Two metrics per arm (load-bearing for Fix #28)

- **top1_TRAINING**: top1 on the chains visible during consolidation (Cell 4's reported metric; saturates for K_THRESH=1)
- **top1_HELDOUT**: top1 on the chains NEVER visible during consolidation — this is the genuine multi-hop test. The discriminator.

## HARD bands (on HELDOUT chains; the only metric that matters)

- **HARD_PASS_BREAK_CEILING**: ARM_HYBRID or ARM_CONSOL_KTHR_3 heldout_top1 ≥ 0.85 AND beats NAIVE by ≥ 0.15 AND CV ≤ 0.05
- **HARD_PASS**: best arm heldout_top1 ≥ 0.75 AND beats NAIVE by ≥ 0.10
- **HARD_FAIL_DECISIVE**: ALL consolidation arms heldout_top1 ≤ NAIVE + 0.03 (consolidation doesn't generalize to unseen chains)
- **BY_CONSTRUCTION_DETECTOR**: ARM_CONSOL_KTHR_1 training_top1 ≥ 0.95 AND heldout_top1 ≤ NAIVE + 0.03 → proves Cell 4's saturation diagnosis empirically

## Discriminators (multiple)

- ARM_KTHR_1 (training vs heldout): proves the by-construction trap exists
- ARM_KTHR_1 vs ARM_KTHR_3+: shows how K_THRESH affects generalization
- ARM_KTHR_3 vs ARM_HYBRID: shows whether cleanup-for-unconsolidated adds value over pure consolidation

## Sanity rails

- ARM_NAIVE_HARD_2HOP must reproduce last night's beta-sweep baseline 0.65 within ±0.03 (apples-to-apples chain construction)
- ARM_CONSOL_KTHR_1 training_top1 must reach ~1.000 (reproduces Cell 4 saturation; confirms the by-construction-saturation diagnosis)
- If sanity rails fail → cell is not in the regime where Barrier 1 was diagnosed; flag REPRODUCIBILITY_DIVERGENCE

## Substrate-product implication

If HARD_PASS_BREAK_CEILING:
- Consolidation memory primitive GENUINELY closes Barrier 1 (lifts heldout chains, not just stored ones)
- Establishes the FIRST chain-grade Stage 2 architectural win post-corrections
- Brain analog confirmed: cortex consolidates frequent paths but generalizes to held-out

If HARD_FAIL_DECISIVE:
- Consolidation doesn't generalize beyond observed chains
- Barrier 1 closure needs different approach (pointer-chain hybrid, anisotropic encoder, etc.)

## Cross-thread

- Skunkworks ruling on Cell 4 v1 (MM by-construction) → this v2 explicitly fixes
- META_M4 (K_THRESH=1 saturation) → ARM_KTHR_1 is the empirical proof
- META_M5 (chain-construction match) → cell uses `make_two_hop_chains` matching beta-sweep
- Pointer-chain hybrid (Director spec at `notes/director_barrier1_pointer_chain_multihop_cell_spec_2026-06-25.md`) → parallel candidate; orthogonal mechanism

## Timeout

2400s

## Status

Spec only. Awaiting USER green-light + Wave F landings.
