# Pre-registration: wave14h_scale_K

Date: 2026-05-20
Status: Pre-registered, gated
Experiment: [exp_wave14h_scale_K.py](../experiments/exp_wave14h_scale_K.py)

## Why

wave14h_alpha_sweep finds the best alpha at n_facts=100. This sister
experiment tests whether the anti-Hebbian rank-1 erase mechanism still
works as n_facts scales up to a realistic fact-store size (1000+).

## Hypothesis (H)

For alpha=0.5 (mid-range), the erase mechanism gives leak reduction >=50pp
AND kept_recall >=80% at every n_facts in {30, 100, 300, 1000}.

## Kill criterion

If even at n_facts=30 the mechanism fails (leak_reduction < 50pp OR
kept_recall < 80%), the mechanism doesn't work in this synthetic-key setup
at all and the alpha_sweep result must be re-verified.

## Operational definition

- N=4096, alpha=0.5, erase 30% of facts per seed
- Sweep n_facts in {30, 100, 300, 1000}
- 5 seeds per n_facts
- Random ±1 keys + values
- W = sum_i v_i k_i^T / N
- Retrieval: keys_q @ W^T -> argmax over value codebook

## Cited mechanism

Same as alpha_sweep: ROME (arXiv:2202.05262) family of rank-1 W edits.

## Expected runtime

Smoke (N=512, K in {20,50}, 1 seed): ~3 sec
Full (N=4096, K up to 1000, 5 seeds): ~5 min on GPU. Dominated by K=1000
case (4096x4096 W matrix, 1000 outer products).

## Verdict labels

- `SCALE_PASS_ALL`: mechanism holds at every K
- `SCALE_PASS_SMALL`: holds at K<=100 but degrades at K=300+
- `SCALE_FAIL`: fails even at small K
- `SCALE_INCONCLUSIVE`: empty per_K (script bug)

## What product decision this enables

PASS_ALL → "Our memory tier supports erase of thousands of facts with bounded
leak and minimal recall cost. Math-backed, scales linearly with fact count."

PASS_SMALL → real but bounded story; need to mention the per-erase ceiling.

FAIL → erase positioning is for small fact stores only.
