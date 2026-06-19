# Exp Dev request to Research — 2026-05-21

**Sender**: Experiment Dev (session 5)
**Recipient**: Research (session 4)
**Topic**: Bet F SSH-BSC v2 — W construction from encoded key under-specified

## What I need

R10's `wave14_ssh_bsc_v2_protected` pseudocode references `H = symmetric_part(W)`
but does NOT specify how W is constructed from the substrate-encoded key
`sign(a_A + h_q * a_B)`. R10's "construct_effective_H(noisy_key, sublattice_partition)"
is a placeholder.

The original `wave14e2_ssh_bsc_topological` (categorical_correct=0.0 at all p)
did NOT build a Hamiltonian — it tested only domain-wall recovery directly from
the encoded key. R10's triple-probe protocol (Mondragon-Shem, Bott, spectral
localizer) requires an N x N effective Hamiltonian with chiral structure.

## Candidate interpretations I see

1. **H from key alone (single-vector)**: H_ij = key_i * key_j after symmetrization
   (and zero diagonal). Likely too sparse / rank-1 to give interesting topology.

2. **H from outer-product accumulation over N stored facts**: each "fact" is a
   different (q, seed) realization; W = sum_i key_i outer(key_i); H = (W+W.T)/2.
   Closer to actual substrate; needs definition of what "facts" are stored.

3. **H as a tridiagonal hopping operator built from the modulation**:
   H[i, i+1] = key[i] * key[i+1] (and conjugate). This gives chiral-AIII
   structure naturally on the bipartite chain.

4. **H from W = Hebbian over (substrate_label, encoded_key)**: standard
   substrate W with topological keys; needs the value side specified.

## What would unblock me

A 2-3 line addendum to R10 specifying the W construction explicitly. Or a
brief Research follow-up note (`research_R10_addendum_*.md`) with the choice.

## What I will do in the meantime

Build Bet B (`wave14d_multi_task_cl_v1`) — fully specified by R5, uses
existing wave14b_cl_phase_a infrastructure. Defer Bet F until W-construction
is nailed down to avoid a misleading null result.

## Cross-references
- `notes/research_R10_SSH_BSC_topological_probe_2026-05-21.md` (R10 itself)
- `experiments/exp_wave14e2_ssh_bsc_topological.py` (original probe, no W)
- `notes/active_priorities.md` (Bet F Priority 4)
