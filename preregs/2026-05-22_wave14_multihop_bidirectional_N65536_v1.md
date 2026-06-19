# Pre-reg: Wave 14 Multi-hop Bidirectional Chain Inference at N=65536 v1

**Filed:** 2026-05-22
**Source:** `research_multihop_chain_rehabilitation_N65536_2026-05-22.md` (Research 18:58 EDT) — rehabilitation mechanism #4 (Mofrad 2021 Viterbi-on-chain).
**Predecessor:** RESONATOR_INSUFFICIENT (this cycle, acc_50hop=0.200 — worse than argmax baseline 0.250).

## Question

When forward-only resonator iteration fails at N=65536, does bidirectional chain inference (forward pass + backward pass from target, combined via joint scoring) restore deep-chain composition?

Research's P=0.45 estimate (lower than Resonator's P=0.65; bidirectional is the next-most-promising after Resonator falsified).

## Hypothesis

H_restores: acc_50hop bidirectional ≥ 0.50. Backward messages correct premature forward commitments.

H_kill: acc_50hop < 0.30 — Mofrad-class also fails. Substrate may need fundamental architecture change.

## Pre-declared verdicts

- `BIDIR_RESTORES` — acc_50hop ≥ 0.50.
- `BIDIR_PARTIAL` — 0.30 ≤ acc_50hop < 0.50.
- `BIDIR_INSUFFICIENT` — acc_50hop < 0.30.
- `BIDIR_INCONCLUSIVE` — metric collection error.

## Method

Per chain (start s_0, relations r_1...r_d, target s_d):
1. **Forward pass**: standard chain top-K=5 cleanup per hop (commit to top-1 for next probe, but record top-5 with similarities).
2. **Backward pass**: starting from target s_d, query reverse chain using inverse relations; record top-K=5 per hop.
3. **Combine**: for each hop position i, joint score = forward_sim[idx] + backward_sim[idx] for idx in union(top-K_fwd, top-K_bwd); pick argmax.
4. Final chain prediction = combined hop-d entity.
5. Compare to target.

Note: backward pass assumes target known a priori (compositional query templates). For substrate-novel test, we know targets by construction.

## Acceptance thresholds

- 0.50 PASS matches Research's median prediction across all rehabilitation candidates.
- 0.30 KILL = "Mofrad-class also fails, substrate-level restructuring needed".

## Config

- N=8192 smoke, 65536 full.
- num_entities=200, num_relations=20, num_facts=100.
- hop_depths full: [1, 5, 10, 25, 50].
- top_K=5, n_trials=20 full.
- 2 seeds.

## Pre-declared interpretation

- **RESTORES**: Mofrad 2021 viable for chain rehabilitation. Substrate-product narrative: "deep-chain composition via Viterbi-on-chain bidirectional inference at N=65536". Demo 1 Lane D agent memory SDK can position deep-chain reasoning at N=65536.
- **PARTIAL**: partial lift; try forward-backward EP/VAMP (Research H#2 P=0.55, costlier implementation).
- **INSUFFICIENT**: both Resonator AND Bidirectional fail. Substrate's deep-chain at N=65536 is genuinely broken; needs hierarchical multi-scale binding (H#5) or substrate-level redesign.

## Not in scope

- Forward-backward EP / full VAMP-on-chain (separate experiment if BIDIR fails).
- Hierarchical multi-scale binding (substantial; deferred).
- Multi-target inference (single target per chain).
- Damping / iteration tuning on combine step.
