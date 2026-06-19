# Pre-registration: wave14_ssh_bsc_v3_protected

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Bet F v3 — R10 Option 2 W-construction (Research unblocked v63)
Author: experiment_dev session, pipeline tick 75

## Why

R10 addendum (Research session) landed 16:00 EDT — picks Option 2 W:
  W = (1/N_facts) * sum_mu k_mu outer k_mu
where each k_mu = sign(a_A + h_q^mu * a_B) is a topologically-modulated
key with q^mu domain walls.

My v2 used Option 3 (tridiagonal hopping) which R10 explicitly REJECTED
as non-substrate-physics. v2 = BET_F_NO_TRANSITION was the wrong-W result.
v3 implements Option 2 exactly per R10's pseudocode.

## Mechanism (per R10 addendum)

For each (q, p_noise, seed):
  a_A = bipolar +/-1 on even sites, zero on odd (sublattice partition)
  a_B = bipolar +/-1 on odd sites, zero on even
  W = zeros(N, N)
  for mu in range(N_facts):
    sample (q_mu, seed_mu)
    h_q_mu = winding_mask with q_mu domain walls
    k_mu = sign(a_A + h_q_mu * a_B)
    W += outer(k_mu, k_mu)
  W /= N_facts
  H = W  (already symmetric since each outer is symmetric)
  apply Bernoulli(p) bit-flip noise to the SUBSTRATE (perturb stored keys)

Triple probes per R10: Mondragon-Shem winding nu_MS, Bott index, spectral localizer.

## Verdict labels (inherited from R10 spec)

- BET_F_PASS (sharp p_c per q, scales 1/(2q) within 30%, triple-probes agree)
- BET_F_NOT_AIII (chiral violation > 0.05; W choice still wrong)
- BET_F_NO_TRANSITION (smooth decay; topology absent)
- BET_F_INCONCLUSIVE

## Runtime: ~30 min full (N=1024, N_facts=500, q in {2,5,10}, p sweep, 3 seeds)
