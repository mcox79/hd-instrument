# Pre-reg: Wave 14 Multi-hop Resonator Network at N=65536 v1

**Filed:** 2026-05-22
**Source:** `research_multihop_chain_rehabilitation_N65536_2026-05-22.md` (Research 18:58 EDT).
**Predecessor:** `wave14_multihop_K100_N65536_v1` = MULTIHOP_N65K_KILLED (acc_50hop=0.217 at N=65536).

## Question

Does Frady-Kent-Olshausen-Sommer 2020 Resonator Network per-hop iteration (T=20 inner steps) restore deep-chain composition at N=65536 K=100, where standard per-hop argmax cleanup fails?

Research mechanism diagnosis: argmax commits prematurely while retrieval state is mixed across near-degenerate K signal eigenvectors. Resonator maintains superposition + iteratively resolves before commitment.

## Hypothesis

H_restores: acc_50hop with resonator ≥ 0.50. Resonator beats argmax baseline (0.217) by 2.3× at depth 50.

H_kill: acc_50hop with resonator < 0.30 (falsifies rehabilitation; substrate-level restructuring needed).

## Pre-declared verdicts

- `RESONATOR_RESTORES` — acc_50hop ≥ 0.50.
- `RESONATOR_PARTIAL` — 0.30 ≤ acc_50hop < 0.50.
- `RESONATOR_INSUFFICIENT` — acc_50hop < 0.30 (Research hypothesis falsified).
- `RESONATOR_INCONCLUSIVE` — metric collection error.

## Method

Per trial:
1. Construct chain of depth d ∈ {1, 5, 10, 25, 50} with 100 distractor facts in M = sign(Σ triples).
2. For each hop: probe = M · (current · rel); resonator iterations T=20:
   - softmax-weighted superposition warm-start
   - sign(entity_atoms^T sign(entity_atoms · x_hat)) nonlinear cleanup
   - softmax with annealed τ = 1/(1+0.5t)
3. Commit final argmax; check vs target.
4. Also run argmax baseline at same chain instances for matched comparison.

## Acceptance thresholds

- 0.50 PASS matches Research's median prediction (0.45-0.65 range).
- 0.30 KILL matches Research's hard falsification threshold.

## Config

- N=8192 smoke, 65536 full.
- num_entities=200, num_relations=20, num_facts=100.
- hop_depths full: [1, 5, 10, 25, 50].
- n_trials=20 full, T_inner=20.
- 2 seeds: [17, 23].

## Pre-declared interpretation

- **RESTORES**: substrate-product winner — Resonator becomes the canonical chain-cleanup primitive for N≥65536 deep reasoning. Cross-thread synthesis: aligns with Bet Z.3-AMP family (iterative posterior readout). Lane D agent memory SDK Demo 1 cleared at N=65536.
- **PARTIAL**: some lift; investigate T_inner sensitivity (T=30, 50).
- **INSUFFICIENT**: Research's primary mechanism diagnosis insufficient. Try forward-backward EP / VAMP-on-chain (Research H#2, P=0.55) OR bidirectional inference (H#4, P=0.45).

## Cost

Resonator T=20 iterations per hop × 50 hops × 20 trials × 2 seeds at N=65536: ~30-60 GPU-min total (Research estimate).

## Not in scope

- T_inner sweep (single T=20 per Research recommendation).
- Forward-backward EP rehabilitation (separate experiment if INSUFFICIENT).
- Hierarchical / bidirectional / sparse-cleanup alternatives.
