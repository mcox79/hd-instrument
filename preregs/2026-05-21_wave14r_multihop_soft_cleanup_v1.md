# Pre-registration: wave14r_multihop_soft_cleanup_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: **Strategy push #4 (Bet N IMMEDIATE)** — cycle 42 followup
Author: experiment_dev session, pipeline tick 68

## Why

R8 candidates A1/C1/B1 all KILLED — binding-side rescues exhausted. R16
(cycle 39) identified **cleanup amplification** as the mechanism that
extends substrate d from RMT-naive 7 to empirical 25.

Bet N tests whether amplifying that mechanism further pushes d past 25.
Mechanism: replace argmax cleanup with softmax(N·cos/τ) top-k propagation.
Different from B1 modern Hopfield (which used Ramsauer exponential capacity
with multiple iterations). Bet N is **soft propagation through the cleanup
operator at each hop** — keeps the intermediate state as a soft mixture
rather than collapsing to a single entity each hop.

This is the only remaining mechanism-level multi-hop rescue axis. If it
fails, the d=25 architectural-closure stance (cycle 34) becomes secure.

## Mechanism

Per cap_map v57 Bet N block:

  probe = M * (current * rel)            # BSC unbind at hop
  # Soft cleanup with temperature tau:
  sims = codebook @ probe / sqrt(N)      # cosine-like
  weights = softmax(N * sims / tau)      # broad-spectrum top-k weighting
  # Keep soft state instead of collapsing:
  next_soft_state = weights @ codebook   # weighted blend of entities
  # Next hop probes with the soft state directly (no argmax collapse)
  current = sign(next_soft_state)        # quantize once per hop to keep BSC ops

tau sweep: {0.5, 1.0, 2.0, 4.0}
seeds: 3
hop_depths: [1, 5, 10, 25, 50] (match wave14t)
NUM_FACTS: 100 (match Strategy's pass criterion)

## Verdict labels (per cap_map v57)

- BET_N_PASS (acc_50hop >= 0.50 at NUM_FACTS=100; monotone gain over tau)
- BET_N_PARTIAL (acc_50hop > 0.22 but < 0.50; cleanup helps but not 2x)
- BET_N_KILLED (acc_50hop <= 0.22 at any tau)
- BET_N_INCONCLUSIVE

## Runtime: ~12 min full
