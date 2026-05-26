# Pre-registration: wave14r_R31_S1_pyrkov_cgle_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Strategy push (Bet N rehab axis #6; R31 S.1)
Author: experiment_dev session, pipeline tick 82

## Why

Per Strategy push (20:35 EDT): R31 S.1 Pyrkov-Byrnes-Cherny 2020 dissipative-
attractor cleanup. Soliton-as-Hopfield-attractor with explicit basin width.
This is Bet N rehab axis #6 (the 6th Bet N rehab axis tested).

## Mechanism

Iterative basin-attractor cleanup at each hop:
  state_0 = probe = M * (current * rel)
  for k in 1..K_iter:
    sims = codebook @ state_{k-1}
    weights = softmax(sims / lambda)
    state_k = weights @ codebook + epsilon * noise
    state_k = sign-quantize
  cleaned = argmax(codebook @ state_K)

Sweep K_iter in {1, 5, 10, 20}, lambda in {0.5, 1.0, 2.0}.

## Multi-probe success criteria

- acc_50hop >= 0.50 (multi-hop test)
- Bet C capacity preserved (substrate-internal sanity)
- Monotone improvement over k or lambda (rules out single-config artifact)
- 3 seeds

## Verdict labels

- BET_N_R31_S1_PASS (acc_50 >= 0.50 with monotone improvement)
- BET_N_R31_S1_PARTIAL (0.22 < acc_50 < 0.50)
- BET_N_R31_S1_KILLED (acc_50 <= 0.22 at all configs; axis #6 closes)
- BET_N_R31_S1_INCONCLUSIVE

## Runtime: ~15 min
