# Pre-reg: Wave 14 Multi-hop Per-Hop Sparse Cleanup at N=65536 v1

**Filed:** 2026-05-22
**Source:** Research 18:58 rehabilitation H#3 (Krotov-Hopfield + Mofrad 2021; P=0.50).
**Predecessor:** RESONATOR_INSUFFICIENT (this cycle).

## Question

Does per-hop sparse-superposition cleanup (softmax-weighted top-K state instead of hard argmax commit) restore deep-chain composition at N=65536?

Cheaper alternative to full Resonator iteration (T=20 inner steps) — one-pass per-hop top-K softmax with τ=0.5.

## Hypothesis

H_restores: acc_50hop ≥ 0.50 — softening avoids premature commitment without iterative cost.

H_kill: acc_50hop < 0.30 — softening alone insufficient.

## Pre-declared verdicts

- `SPARSE_RESTORES` — acc_50hop ≥ 0.50.
- `SPARSE_PARTIAL` — 0.30 ≤ acc_50hop < 0.50.
- `SPARSE_INSUFFICIENT` — acc_50hop < 0.30.
- `SPARSE_INCONCLUSIVE` — metric collection error.

## Method

Per hop:
1. probe = M * (current * rel).
2. top-K=5 entities by sims = entity_atoms @ probe.
3. softmax(top-K sims, τ=0.5).
4. soft state = Σ w_k · entity_atoms[idx_k]; sign-quantize.
5. Use soft state as `current` for next hop.

Final: argmax sim with entity codebook.

## Acceptance thresholds

- 0.50 PASS matches Research's median prediction across rehabilitation mechanisms.

## Config

- N=8192 smoke, 65536 full.
- num_entities=200, num_relations=20, num_facts=100.
- hop_depths full: [1, 5, 10, 25, 50].
- top_K=5, τ=0.5.
- n_trials=20, 2 seeds full.

## Pre-declared interpretation

- **RESTORES**: cheapest rehabilitation mechanism works. Substrate-product winner — minimal compute overhead, single-pass.
- **PARTIAL**: softening partially helps; full Resonator iteration needed.
- **INSUFFICIENT**: single-pass softening insufficient; need iterative mechanism class.

## Cost

O(K·N) per hop = 5·65536 ≈ 3×10^5 ops/hop. 50 hops × 20 trials × 5 depths × 2 seeds = ~10^9 ops total. ~30-60 sec runtime.

## Not in scope

- top_K sweep (single top_K=5).
- τ sweep (single τ=0.5).
- Iterative variant (that's Resonator H#1).
