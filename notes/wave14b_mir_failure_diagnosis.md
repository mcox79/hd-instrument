# MIR-loses-to-random diagnosis — research agent synthesis

Returned 2026-05-19. Follow-up to mir_canonical losing to random by
0.13 bpc (worse than soft-MIR's 0.02 loss).

## TL;DR

**"Easy-examples anti-pattern" is real but not the dominant failure.**
The dominant failure: on rank-1 delta-rule with BSC +-1 codes and
cosine retrieval, MIR's priority signal **mathematically collapses
to cosine-similarity-to-current-batch** -- the same signal the
retrieval branch already uses.

Result: MIR top-K picks pool entries that are already correctly
handled by retrieval; replay over-fits W toward redundant work,
leaving the rest of the pool unrehearsed.

**Priority is anti-correlated with marginal utility.**

## The math

Trace through the canonical re-score:

1. `dW = (residual^T @ ctxs_b) / N` -- rank-B perturbation
2. `W' = (1 - decay) * W + alpha * dW`
3. Change in pool entry's query under W -> W':
   `Delta q_i ~ alpha * c_i @ dW^T = (alpha/N) * (c_i @ ctxs_b^T) @ residual`
4. Magnitude is dominated by **<c_i, ctxs_b>** summed over batch.
5. With c_i, ctxs_b both +-1 BSC vectors in dim 4096, this is
   exactly Hamming-near-by score, modulated by residual sign.

**score(c_i) ~ (alpha/N) * Sum_b <c_i, ctx_b> * g_b**

The cosine-to-batch term dominates the residual projection term
in magnitude.

**Consequence**: MIR top-K = "pool entries whose contexts are most
similar to current batch contexts." Eval/retrieval uses the EXACT
SAME cosine. So replay is over-fitting on retrieval's existing work.

## Literature anchor

**Goldfarb-Hand et al. 2025 "Replay Can Provably Increase Forgetting"**
(arXiv 2506.04377): in over-parameterized continual linear regression
(noiseless), **random replay strictly increases forgetting in
expectation** for some task distributions. Non-monotonicity in
replay count is provable.

Our substrate is over-parameterized (N=4096, pool=1024) and
effectively linear (rank-1 delta-rule, no curvature). This is the
closest published analogue to "replay hurts here."

## H1-H4 verdict

- H1 (rank-1 dW collapse to cosine): **CONFIRMED**, strongest factor
- H2 (BSC pre-saturation): partial; secondary
- H3 (linear regime, double-counting retrieval): **CONFIRMED**, strongest
- H4 (replay concentration): confirmed, secondary

**Soft-MIR's random sub-sample of top-4K was accidentally adding
diversity that helped.** Removing it (canonical det-top-K) made
things worse -- exactly what H1+H3 predict.

## Three rescues (each <=1h GPU on existing harness)

### Rescue A -- Adversarial MIR (argmin instead of argmax)
```python
_, top_idx = torch.topk(-score, n_replay)
```
If A wins: priority is inverted on this substrate (sketchy).
If A ties random: priority signal carries zero info; only diversity
matters.

### Rescue B -- Cosine-deconfounded MIR
```python
sims_to_batch = (pool_ctx @ ctxs_b.T) / N
confound = sims_to_batch.mean(dim=1)
score_clean = score - score.std() * confound / confound.std().clamp(min=1e-6)
_, top_idx = torch.topk(score_clean, n_replay)
```
**Sharpest mechanism test.** Three outcomes:
- B beats random by >=0.05 -> true interference signal exists hidden
  under cosine confound. **Deconfound + ship.**
- B ties random -> priority signal is a coin flip after deconfounding.
  Pure diversity is what matters.
- B still loses -> second-order interference is genuinely absent in
  this regime. Need non-linear W.

### Rescue C -- MIR + greedy diversity (DPP-thin)
Top-2K candidates, greedy-thin by gradient/context angle to K.
Tests whether H4 (concentration) is the dominant failure.

## Decision matrix

| A | B | C | Diagnosis |
|---|---|---|---|
| no | no | no | priority replay genuinely impossible on this substrate -- H3 wins, need non-linear W |
| no | yes | no | true MIR signal exists, was confounded -- fix is deconfound |
| no | no | yes | concentration was the killer -- ship MIR+DPP |
| no | yes | yes | both confound and concentration matter -- ship deconfounded + DPP |
| yes | * | * | priority signal inverted -- investigate further |

## Genuinely closed

- Static concept-tag priority (R7+F1 closed earlier)
- Aljundi-canonical MIR via virtual rank-1 step on THIS substrate
- "MIR can beat random replay here without substrate or score-fn changes"

## NOT closed

- Priority replay in general (Aljundi GSS / EDER / RAER / PGR / Goldilocks
  show priority can beat random with deconfounding, diversity, or
  storage-side selection)
- Interference-priority on a non-linear W (would restore curvature)
- "Middle-difficulty" priority (Goldilocks-style; replaces signal entirely)

## Sources

- [Goldfarb-Hand Replay Can Provably Increase Forgetting 2025](https://arxiv.org/abs/2506.04377)
- [Ding Understanding Forgetting in CL with Linear Regression 2024](https://arxiv.org/abs/2405.17583)
- [Pan Understanding Limitations of PER 2022](https://arxiv.org/abs/2007.09569)
- [Hacohen-Tuytelaars Goldilocks 2024](https://arxiv.org/abs/2406.09935)
- [Aljundi GSS 2019](https://proceedings.neurips.cc/paper/2019/file/e562cd9c0768d5464b64cf61da7fc6bb-Paper.pdf)
- [EDER Efficient Diversity Replay 2024](https://arxiv.org/html/2410.20487v2)
- [Prioritized Generative Replay ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/74b7956113fdf0ec87288f351a1d8a34-Paper-Conference.pdf)
