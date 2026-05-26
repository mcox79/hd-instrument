# Pre-registration: wave14r_multihop_adaptive_beta_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Strategy push #2 from cycle 42 followup (R8 B3 — adaptive-beta cleanup)
Author: experiment_dev session, pipeline tick 69

## Why

R8 B3 (per cycle 42 followup): "Anneal softmax sharpness as noise accumulates;
avoid over-committing to incorrect intermediates. Cheap; symptom mitigation
only — doesn't address closure."

After Bet N tests cleanup amplification, B3 closes the R8 rescue list by
testing cleanup sharpness scheduling. Strategy marked this "cheap; closes the
original R8 rescue list."

Builds on B1 modern Hopfield (also KILLED) but with hop-dependent beta:
  beta(h) = BETA_INIT / (1 + h * decay_rate)
Higher beta early (commit confidently when signal strong); lower beta later
(stay broad when noise dominates).

Predicted: closes R8 rescue list. Per Strategy "low prior" — likely KILLED but
worth running to make the closure formal.

## Mechanism

Same BSC factbase as wave14t. Cleanup per hop:
  probe = M * (current * rel)
  beta_h = BETA_INIT / (1 + h * decay_rate)
  weights = softmax(beta_h * codebook @ probe / sqrt(N))
  state = weights @ codebook  # Ramsauer-like aggregation
  current = argmax(codebook @ state)

Sweep (BETA_INIT, decay_rate) pairs in {(8.0, 0.1), (16.0, 0.2), (32.0, 0.5)}.

## Verdict labels

- ADAPTIVE_BETA_50HOP_VALIDATED (acc_50 >= 0.50)
- ADAPTIVE_BETA_PARTIAL_AT_<D> (0.22 <= acc_50 < 0.50)
- ADAPTIVE_BETA_KILLED (acc_50 < 0.22; R8 rescue list formally closed)
- ADAPTIVE_BETA_INCONCLUSIVE

## Runtime: ~10 min full
