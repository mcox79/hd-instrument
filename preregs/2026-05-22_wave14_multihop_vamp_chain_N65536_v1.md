# Pre-reg: Wave 14 Multi-hop VAMP-on-Chain Forward-Backward EP at N=65536 v1

**Filed:** 2026-05-22
**Source:** `research_multihop_mechanism_redrill_2026-05-22.md` (Research 19:25 EDT) — top rehab candidate (P=0.40).

## Question

Does tree-exact forward-backward EP (single-pass per direction, NOT loopy iteration) on the substrate's deep-chain composition restore acc_50hop at N=65536, where Resonator (loopy iteration) failed?

Research's structural distinction: chain is a TREE; tree-exact methods (forward-backward) are NOT iterative within hops and don't share Resonator's fixed-point cycling failure mode.

## Hypothesis

H_restores: acc_50hop ≥ 0.50. Single-pass forward + backward beats argmax (0.22) and Resonator (0.20).

H_kill: acc_50hop < 0.30 — all readout-only rehab fails; substrate-level V3 restructuring needed (sparse codebook, clique codes, asymmetric W).

## Pre-declared verdicts

- `VAMPCHAIN_RESTORES` — acc_50hop ≥ 0.50.
- `VAMPCHAIN_PARTIAL` — 0.30 ≤ acc_50hop < 0.50.
- `VAMPCHAIN_INSUFFICIENT` — acc_50hop < 0.30 (escalate to V3).
- `VAMPCHAIN_INCONCLUSIVE` — metric collection error.

## Method

Per chain (start s_0, relations r_1..r_d, target s_d, factbase M):

1. **Forward pass**: at each hop t, compute log_post_t = log_softmax(sims_t) where sims_t = entity_atoms @ M @ (q_state · r_t). Posterior expectation x̂_t = Σ exp(log_post_t)·entity_atoms[idx]; q_state = sign(x̂_t).
2. **Backward pass**: target prior = δ at target_idx. smoothed_post[d] = forward_post[d] + target_prior. For t = d-1 to 0:
   - Compute backward msg: probe_back = M · (sign(x̂_{t+1}) · r_t); sims_back = entity_atoms @ probe_back; backward_log_msg = log_softmax(sims_back).
   - smoothed_post[t] = log_softmax(forward_post[t] + backward_log_msg).
3. **Commit**: pred = argmax of smoothed_post[d]; check vs target_idx.

## Acceptance thresholds

- 0.50 PASS matches Research's median prediction across rehab candidates.
- 0.30 KILL = "tree-exact rehab also fails; substrate-level needed".

## Config

- N=8192 smoke, 65536 full.
- num_entities=200, num_relations=20, num_facts=100.
- hop_depths full: [1, 5, 10, 25, 50].
- n_trials=20, 2 seeds.

## Pre-declared interpretation

- **RESTORES**: tree-exact mechanism class is the right rehab. Substrate-product roadmap unblocked: Lane D agent memory SDK Demo 1 at N=65536 viable with VAMP-on-chain readout. Substrate-physics insight: failure was forward-only / argmax-commit, not the chain itself.
- **PARTIAL**: tree-exact helps; investigate if sparse codebook also reduces hub absorption.
- **INSUFFICIENT**: ALL readout-only rehab falsified. V3 substrate-level redesign required (Research's sparse codebook / clique codes / asymmetric W candidates).

## Not in scope

- Iterative EP (multi-pass forward-backward refinement).
- Sparse-prior denoiser (Bernoulli-Gaussian assumption).
- V3 substrate-level candidates (deferred conditional on this result).
