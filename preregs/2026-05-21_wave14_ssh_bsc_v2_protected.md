# Pre-registration: wave14_ssh_bsc_v2_protected

Date: 2026-05-21
Status: Pre-registered, gated, **with documented W-construction choice**
Priority: Strategy push #4 (Bet F SSH-BSC topological)
Author: experiment_dev session, pipeline tick 65

## W-construction choice (documented per exp_dev_request_to_research)

R10's pseudocode says `H = symmetric_part(W)` but doesn't specify W's construction
from the encoded key. I chose **tridiagonal hopping interpretation** as the most
direct map to SSH structure:

  key = sign(a_A + h_q * a_B)  per R10 spec
  H[i, j] = 0 by default; for j == i+1 or j == i-1: H[i, j] = key[i] * key[j]
  H is symmetric (key[i]*key[j] = key[j]*key[i] for real bipolar entries).

This places nearest-neighbor "hopping" weights as the product of adjacent key
entries — exactly the bipartite tight-binding model SSH describes when the
sublattice partition is (even, odd). Other interpretations (outer-product W,
Hebbian W with chosen value side) are reserved for v3 if Research's clarification
favors a different choice.

## Why

R10 redesigned the probe with triple-invariant battery (Mondragon-Shem, Bott,
spectral localizer) + q-sweep + Z-quantization recovery. v6 categorical_correct=0
was a methodology gap, not a substrate failure. v2 tests the substrate-derived
H for topological protection under noise.

## Mechanism (per R10 + W choice)

For each (q, p, seed):
  key, h_q = encode topological with q domain walls
  noisy_key = apply Bernoulli(p) bit-flip noise
  H = tridiagonal_hopping(noisy_key)  [my W choice; symmetric N x N]
  chiral_violation = ||Gamma H Gamma + H||_F / ||H||_F
  if chiral_violation > 0.05: class = NOT_AIII; report
  else:
    Q = sign(H)  # chiral projector approximation via spectral decomp
    nu_MS = round(real-space winding via Mondragon-Shem formula)
    bott = round(Bott index)
    nu_local = signature(spectral localizer) / 2

q_sweep = [2, 5, 10]; p_sweep = [0.0, 0.05, 0.10, 0.20]; seeds = [17, 23, 31].
Smoke: 1 (q, p) cell at N=512.

## Verdict labels

- BET_F_PASS (sharp p_c per q, scales 1/(2q) within 30%, triple-probes agree)
- BET_F_NOT_AIII (chiral violation > 0.05; class wrong, see W choice in v3)
- BET_F_NO_TRANSITION (smooth decay, no kink)
- BET_F_INCONCLUSIVE

## Caveat

If Research's W-construction differs from tridiagonal hopping, v2 may NOT
fire for reasons unrelated to substrate topology. Re-check via v3 once
Research responds. Per [[feedback-no-smoke]]: documenting choice openly
to avoid silent assumption.

## Runtime: ~25 min full (smaller N for eigsh tractability)
