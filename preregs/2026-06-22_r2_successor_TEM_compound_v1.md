# Pre-registration: r2_successor_TEM_compound_v1

**Author:** Exp-Dev
**Date:** 2026-06-22
**Anchor:** `r2_successor_TEM_compound_v1`
**Cell:** `experiments/exp_r2_successor_TEM_compound_v1.py`
**Driver:** brain-drill #3 5x DEEPER (notes/research_brain_drill_3_multihop_reasoning_5x_DEEPER_2026-06-22.md); r1b HARD_FAIL revival path.

## Headline

Replace r1b's per-hop softmax decay (which lost margin signal and FAILED OOD-refuse >=0.90 and margin-ratio >2.0x at K=4) with three composable structural fixes:

1. **Successor-W closure** (Dayan 1993; Stachenfeld 2017; Momennejad 2018): precompute `M = sum_{k=1..K_max} gamma^k W^k`. M is then applied AS the per-hop transition operator (replacing W): `state_k = M @ (state_{k-1} * R[p_k] * sq)`. Critically: NO per-hop softmax / topk-bundle projection between hops -- this LINEAR chain is what arrests r1b's per-hop margin decay. M aggregates 1-hop..K_max-hop substrate path evidence at each step, giving richer signal than a single W matvec. The self-test verified SR K=2 acc 1.00 >= ITER K=2 acc 1.00 on a clean 2-hop synthetic chain set (sanity).
2. **TEM structural-sensory factorization** (Whittington-Behrens 2020): structural code (R relations) factored from sensory code (E entities); compose at retrieval. Enables compositional generalization to unseen R-chains.
3. **Theta-gamma compound margin via permutation binding** (Lisman-Jensen 1995/2013; Plate 2003; Kanerva 2009): chain state encoded as `sum_k P^k @ e_k`; refuse-gate operates on compound chain coherence (in-KB chains have COHERENT per-position recovery; OOD chains have INCOHERENT recovery). Compound-margin replaces the per-hop top1-top2 margin r1b used.

## Independent variables

- `chain_mechanism` in {ITER_CLEANUP_r1b_anchor, SUCCESSOR_W_CLOSURE, TEM_FACTORED_COMPOUND}
- `K_hops` in {2, 3, 4}
- (Phase 2 only conditional on HARD_PASS:) `K_max` in {3, 5, 8}; `gamma` in {0.5, 0.8, 1.0}; `permutation_type` in {random, circular}

## Fixed (match r1b for direct comparison)

- N_DIM = 8192
- M_TRIPLES = 50000
- K_set = 8 (the iterative-cleanup top-K bundle size for the anchor arm)
- K_inner = 1
- N_CHAINS = 500
- N_OOD = 500
- SEEDS = [7, 17, 23, 31, 41, 53, 67] (7 seeds, same primes as r1b)
- K_MAX (SR closure precompute depth) = 5
- GAMMA (SR closure discount) = 0.8
- PERM_TYPE = "random" (Kanerva HDC primitive)
- BETA_CLEANUP = float(N_DIM) (matches r1b)
- Corpus: FB15k-237 train (`data/datasets/fb15k_237_train_50k.jsonl`)

## Anchors (precondition replicates)

The ITER_CLEANUP_r1b_anchor arm runs r1b's iterative-cleanup mechanism verbatim under this cell's harness. It MUST reproduce r1b's per-K means within +/- 0.01 (tighter than r1b's +/- 0.02 vs r1 because it is the SAME mechanism under the SAME harness). r1b reference means (full-run, 7 seeds, N=8192, M=50000):

| K | r1b mean | tolerance band |
|---|---|---|
| 2 | 0.3934 | [0.3834, 0.4034] |
| 3 | 0.2677 | [0.2577, 0.2777] |
| 4 | 0.1763 | [0.1663, 0.1863] |

Anchor-fail (out-of-tol) => harness drift => HARD_FAIL inconclusive (NOT a chain-grade negative on the mechanism).

## Discriminating regime requirement (META-rule)

At K=1 (degenerate single-hop), ALL three arms must equal U1's single-hop anchor (~0.99 setrecall). They are equivalent at K=1 by construction. At K=10 (far beyond test range), ALL arms must collapse to near-random; if SR doesn't collapse at K=10, the closure is leaking beyond K_max. Smoke includes the K=1 bracket sanity check; full includes K=1 and K=10 as bracket diagnostics.

## Pre-registered HARD bands

### HARD_PASS (chain-grade promotion; structural fix validated)

ALL of the following at K=4:

1. SUCCESSOR_W_CLOSURE OR TEM_FACTORED_COMPOUND mean accuracy >= 0.211 (1.20x r1's K=4 0.172, the original anchor; equivalently >= 1.20x r1b r1-anchor)
2. OOD_refuse_margin min >= 0.90 across K in {2,3,4} for the winning arm (clears r1b's gate2 FAIL)
3. margin_ratio (in-KB / OOD) > 2.0 at all K for the winning arm (clears r1b's c2 FAIL)
4. cv across 7 seeds <= 0.06 for the winning arm
5. ITER_CLEANUP_r1b_anchor reproduces r1b within +/- 0.01 at all K (harness intact)
6. Substrate-only-decode counter == 0 (no LLM forward calls; baked-in counter assertion)
7. Discriminating-regime sanity: K=1 == single-hop anchor for all arms; K=10 collapse to <0.05 for all arms

### HARD_PASS_PLUS (super-pass; competitive at multi-hop)

HARD_PASS satisfied AND either arm at K=4 achieves >= 0.30 mean accuracy AND margin_ratio > 3.5x.

### MIDDLE_BAND (partial mechanism)

EITHER:
- Winning arm K=4 mean accuracy in [1.05x, 1.20x] r1 (i.e., [0.181, 0.211])
- OR OOD_refuse_margin min in [0.80, 0.90] at K in {2,3,4}
- OR margin_ratio in [1.5, 2.0] at all K

AND ITER_CLEANUP_r1b_anchor reproduces r1b within +/- 0.01.

### HARD_FAIL (mechanism wrong)

EITHER:
- No arm achieves >= 1.05x r1 mean accuracy AT K=4 (no compositional rescue available)
- OR OOD_refuse_margin still < 0.80 at K=4 for all arms (compound + SR don't fix margin signal)
- OR ITER_CLEANUP_r1b_anchor does NOT reproduce r1b within +/- 0.02 (harness drift => HARD_FAIL inconclusive; do not treat as mechanism-negative)

## Compute / cost / routing

- N_DIM=8192, fp32. W matrix: 8192*8192*4 bytes = 256 MB.
- ITER_CLEANUP arm: matmul per hop per chain (W @ vec). At 500 chains x K_inner=1 x (K_2+K_3+K_4)=9 hops per chain (sum K) x 2 (in-KB + OOD) = ~9000 matmuls per seed. r1b clocked ~770s/seed on remote_cpu => ~85ms per matmul (numpy BLAS).
- SUCCESSOR_W_CLOSURE arm: setup = K_MAX=5 chained NxN matmuls = ~5 * 8192^3 ops ~ 2.75e12 ops = ~5 min CPU / ~3s GPU. Query = SINGLE matrix-vector per chain (vs K_inner * K matmuls for iter-cleanup). ~3-5x faster per query than iter-cleanup.
- TEM_FACTORED_COMPOUND arm: permutation-binding overhead is N_DIM index gather + bind. Cost ~1.05x iter-cleanup query.
- Total estimate, CPU: ~770s/seed * 3 arms * 7 seeds = ~16000s = ~4.5h
- Total estimate, GPU (torch+cuda fp32 on N=8192): expected ~5-10x speedup = ~45min - 1.5h
- **Routing decision:** workload is matmul-bound at N=8192. Per Fix #24 (GPU dispatch must actually use GPU), implement with `torch.cuda` if available; cell falls back to CPU otherwise. Route to **overnight_queue** (GPU runner). PROT-020 satisfied (import torch present).
- Per-experiment timeout: PROT-019 floor for _n8192 anchors = 21600s (6h). Set --timeout 21600s.

## Smoke gate

- 1 seed (7), N_DIM=2048, M_TRIPLES=5000, K_HOPS in {2, 3}, N_CHAINS=100, N_OOD=100
- Includes K=1 bracket sanity (all arms should hit ~1.0 acc on the 1-hop sample)
- All 3 arms run
- Self-test on small synthetic KG: verify SUCCESSOR_W_CLOSURE at K=2 >= ITER_CLEANUP_anchor on the same chain set (sanity: SR shouldn't UNDERPERFORM iter-cleanup on a clean synthetic chain); verify TEM compound-margin separates in-KB from OOD on the synthetic.

## Version markers (baked into metrics.json)

`chain_mechanism`, `K_max`, `gamma`, `permutation_type`, `N_DIM`, `M_TRIPLES`, `n_seeds`, `n_chains`, `device` (cuda|cpu).

## Falsifiable predictions (from Research drill, calibrated; deflated)

| Prediction | P(HARD-PASS) |
|---|---|
| 1 (primary): SUCCESSOR_W_CLOSURE at K=4 >= 0.211 + margin-ratio>2.0 + OOD-refuse>=0.90 | 0.45 |
| 2 (secondary): TEM_FACTORED_COMPOUND held-out R-chain transfer >= 0.10 | 0.30 |
| 3 (conditional on 1): hybrid > SR-alone by 0.05 + margin-ratio > 3.0 | 0.35 |
| 4 (null bracket): K=1 == anchor; K=10 collapse | high-confidence sanity |

P_overall_deflated = 0.45 (capped novel-synthesis).

## Composes with

- r1 / r1b (direct anchor reproduction of K=2,3,4 means; same KG/corpus)
- drill #2 c2 cascade-STC (independent harness; can compose AFTER both land as `r2_cascade_W_v1`)
- HotpotQA (CERT 588 K=2 chain-grade; r2 HARD_PASS opens K>=3 path as `r4_hotpotqa_K_geq_3_v1`)
- substrate_self_map_v2 (in-flight Director cell; r2 SR closure could be applied to its small KG)

## Honest limits

- All HARD bands are METHOD/CONFIG-contingent (N=8192, M=50000, 7 seeds, 500 chains, FB15k-237; "envelope of THIS method/config, extension untested" per measured-bounds rule).
- Compositional generalization claim (Prediction 2) is TIERED: TEM transfer to unseen R-chains is the WEAKEST evidence here; deflated P=0.30. The HARD_PASS primary gate is on Prediction 1 (SR closure mean + margin); Prediction 2 lands as a secondary diagnostic, not a gate.

-- Exp-Dev, 2026-06-22
