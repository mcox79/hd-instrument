# Replay prioritization alternatives — research agent synthesis

Returned 2026-05-19. Math survey on prioritization mechanisms that
could beat random replay in our setup (where R7 showed concept-tagged
replay loses by 0.53 bpc).

## Evaluation lens

Methods that beat random in supervised CL satisfy at least one of:
- (a) act on *current* model state (closed-loop), not just sample identity
- (b) push toward *coverage* of input or gradient distribution
- (c) match a *distributional* target

Static structural tags satisfy none. **That's why concept-tagging failed.**

## Top 3 recommendations

### Rank 1 — A7. MIR (Maximally Interfered Retrieval) on the delta-rule update

**Operation:** virtual W' = W - alpha * grad(batch_B). For each pool
entry i compute loss(c_i, W') - loss(c_i, W). Pick top-K positive
(most-increased loss).

**Why it beats random:** literature-strongest method for small-buffer
supervised CL (Aljundi 2019 NeurIPS). Closed-loop by construction.

**Cost:** our linear delta-rule makes virtual W' free. One extra forward
pass on pool A per batch: 4M ops, ~5 ms. Phase B inflation ~15%.

**All compat checks pass.** Strongest single-bet candidate.

**Test (<1h GPU):** Predict BWT in (-0.90, -1.10), beats random by
0.10-0.30 bpc.

### Rank 2 — B11. Top-K sparse codes + stale-dim replay

**Operation:** convert ctx to top-K=200 sparse codes. Per-dim freshness
= updates_to_dim_since_last_step. Replay = entries that activate most
stale dims.

**Why it could beat random:** the only Group B candidate with concrete
mechanism specific to our regime. **Bricken 2023 (arXiv 2303.11934)**
shows SDM/top-K activations natively prevent forgetting without replay
at all. Adding stale-dim replay on top is plausibly strictly better.

**Cost:** substrate rewrite — well-trodden, decompose/edit operations
port. Top-K activation makes prioritisation cheaper not more expensive
(O(P*K) instead of O(P*N)).

**Test:** Predict random-on-sparse already beats random-on-dense by
0.2+ bpc; stale-dim replay adds another 0.1-0.3.

### Rank 3 — A2/A3 (tied). Loss-weighted k-DPP / Facility-location coreset

**Cheapest formal coverage objectives.** A1 (Wasserstein) is most
principled distribution-matcher but A2/A3 are operationally equivalent
at our scale and 10x cheaper.

**Right baseline for "is coverage the missing ingredient?"** If these
don't beat random by >=0.05 bpc, prioritization door closes structurally
and MIR's win is purely about closed-loop dynamics, not coverage.

**Cost:** A2 greedy DPP MAP at k=32, P=1024: ~33k inner products,
<50 ms. A3 facility-location greedy: ~20 ms.

## Other candidates

- **A1 Optimal-transport / Wasserstein**: principled but ~10x cost of
  A2/A3 with similar mechanism. Skip in favor of A2.
- **A4 Fisher-information priority**: static parameter-importance;
  modest improvement expected (between concept-tag and random).
- **A5 Influence-function priority**: simpler MIR; covered by A7.
- **A6 SGLD noise priority**: mechanism weak; skip.
- **A8 GSS (gradient sample selection)**: matches MIR empirically; A7
  is the cleaner test.
- **A9 SM-2 spaced repetition**: won't help in our 15-epoch x cycling
  Phase B (every entry seen ~7x).
- **A10 Population ensemble**: ensembling rescues weak signals;
  tunable.

## Group B candidates (deferred)

- **B12 Hyperbolic**: only if pool is hierarchical (byte-LM isn't
  strongly).
- **B13 Persistent homology**: static signal, same failure mode as
  concept-tagging.
- **B14 Hopf antipode orbits**: no mechanism aligned with loss landscape.
- **B15 Free-probability cumulants**: degenerates to DPP for commutative
  BSC.
- **B16 Tomita-Takesaki orbits**: trivial in finite-dim BSC (Delta=1);
  needs type-III factors. Vacuous at our scale.

## Brutal honesty

Across all 16 candidates, only three have defensible mathematical
mechanism to beat random at our scale: **A7 (MIR), B11 (sparse codes +
stale-dim), A2/A3 (formal coverage)**. Everything else either:
- reduces to static tag (concept-tagging failure mode)
- degenerates in BSC (B15, B16)
- has no demonstrated ML wins (B12, B13, B14)

Honest expected outcome: **MIR beats random by 0.1-0.3 bpc** — that's
the headline. Sparse codes are a separate substrate bet worth running
independently.

## Recommended order

1. **A7 MIR**: cheapest, best literature support, no substrate change
2. **A2/A3 DPP/facility-location**: tests if coverage alone is the
   answer (decides MIR's mechanism)
3. **B11 sparse codes**: separate substrate bet, run in parallel

## Sources

- [Aljundi MIR 2019](https://arxiv.org/abs/1908.04742)
- [Aljundi GSS 2019](https://arxiv.org/abs/1903.08671)
- [Chaudhry tiny-memory ER 2019](https://arxiv.org/abs/1902.10486)
- [Buzzega DER/DER++ 2020](https://arxiv.org/abs/2004.07211)
- [Bricken SDM Continual Learner 2023](https://arxiv.org/abs/2303.11934)
- [Chen Fast Greedy DPPs 2018](https://arxiv.org/abs/1709.05135)
- [FDMat coresets via OT AAAI 2024](https://ojs.aaai.org/index.php/AAAI/article/view/28771)
- [SuRe Surprise-Driven Replay 2025](https://arxiv.org/pdf/2511.22367)
- [ER-PASS submodular replay MDPI 2025](https://www.mdpi.com/2072-4292/17/18/3233)
- [Sun information-theoretic CL bounds 2025](https://arxiv.org/abs/2507.12043)
