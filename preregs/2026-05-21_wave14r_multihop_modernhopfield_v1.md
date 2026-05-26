# Pre-registration: wave14r_multihop_modernhopfield_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: R8 rescue list candidate B1 (after A1/C1 both KILLED)
Author: experiment_dev session, pipeline tick 61

## Why

A1 (wave14r_multihop_FHRR_v1) -> MULTIHOP_FHRR_KILLED
C1 (wave14r_multihop_hybrid_v1) -> MULTIHOP_HYBRID_KILLED

Both R8 binding-side rescues failed. B1 is R8's cleanup-side rescue: swap
argmax cleanup for Ramsauer 2020 modern Hopfield exponential-energy
retrieval. Tests whether stronger per-hop cleanup compensates for the
closure-induced noise that argmax couldn't resolve. R8 literature predicts:
only partially helps.

If B1 also KILLED: all three R8 candidates fail. Multi-hop d=25 cliff is
genuinely a substrate-architectural limit, not a cleanup-or-binding-algebra
issue. Time to escalate to Strategy for next-step direction.

## Mechanism

Same BSC storage as wave14t. Per-hop cleanup change:
  probe = M * (current * rel)
  # OLD: current_idx = argmax(codebook @ probe)
  # NEW: iterate Ramsauer update:
  #   weights = softmax(beta * codebook @ state)
  #   state_new = codebook.T @ weights
  #   (3-5 iterations to convergence)
  # current_idx = argmax(codebook @ state_final)

beta starts at 8 (matches BETA from base substrate); sweep 2/8/32/128 in
full mode to find optimal sharpness.

## Verdict labels

- MULTIHOP_HOPFIELD_50HOP_VALIDATED (acc_50 >= 0.80)
- MULTIHOP_HOPFIELD_PARTIAL_AT_<D> (0.40 <= acc_50 < 0.80)
- MULTIHOP_HOPFIELD_KILLED (acc_50 < 0.40)
- MULTIHOP_HOPFIELD_INCONCLUSIVE

## Runtime: ~10 min full multi-seed
