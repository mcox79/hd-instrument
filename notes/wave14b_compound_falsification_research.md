# Triple-compound falsification — research synthesis

Returned 2026-05-19. Unbiased deep research on why random replay + R10
+ R3 don't compound; instead they substitute.

## TL;DR

**Substrate has ONE BWT mechanism (random replay) and ONE retrieval-
augment mechanism (R10 at K>=16). R3 is K=4-specific.** The triple
compound was over-optimistic; mode-connectivity theory predicts CL
mechanisms that all steer W into the same low-loss basin will
substitute, not compound. The substrate-uniqueness story (decompose /
edit / recompose / interpret) is independent and intact.

## Theory: why mechanisms substitute

- **Taxonomy says different** (van de Ven 2022): random replay =
  *replay*, R10 = *context-dependent processing*, R3 = *functional
  regularization*. By taxonomy they should be orthogonal.
- **Geometry says same**. Verwimp 2021 ("Rehearsal Revealed"): successful
  rehearsal works because it keeps post-shift weights inside the OLD
  task's low-loss basin. Mode-connectivity work (Mirzadeh 2020, Kozal
  2024): essentially every CL mechanism (replay, EWC, distillation)
  steers toward the SAME connected low-loss valley of task A. **Three
  mechanisms pushing toward the same basin don't compound -- they
  redundantly correct the same error component.**
- **Provable non-monotonicity**: Goldfarb-Hand 2025 ("Replay Can
  Provably Increase Forgetting"): in over-parameterized continual
  linear regression, forgetting is **non-monotonic in replay count**.
  Our substrate is rank-bounded linear regressor (delta-rule W) → theorem
  applies directly. Triple worse than replay alone (-1.02 vs -0.85)
  matches their geometric mechanism.

## Specific: DER++ precedent (closest analogue)

Buzzega 2020 DER++ is replay + logit distillation = supervised-DL
analogue of our replay + R3. On Seq-CIFAR-10 with 200-example buffer:
- ER baseline: X
- DER (logit-distill alone): +7 over ER
- **DER++ (both): +1.4 over DER**

Even canonical "compound" gives ~10-20% marginal lift, not additive.
Our replay+R3 at K=32 is -0.89 vs replay-alone -0.85 -- a 0.04 LOSS,
well within DER's marginal-noise band but on the wrong side.

**DER++ is "weak compound" precedent, ours is below noise. Substantive
substitute, not compound.**

## Why R3 vanishes at K>=16 (math story)

R3 uses PPMI on pairwise byte positions (i,j) in K-window. The number
of position pairs is K(K-1)/2:
- K=4: 6 pairs
- K=16: 120 pairs
- K=32: 496 pairs

`NUM_CONCEPTS=100` is FIXED. At K=4, 100 concepts saturate 6 pairs ×
256 bytes -- dense, high-frequency co-occurrence captured. At K=16,
those 100 concepts are sampled from ~7.9M possible (i,b_i,j,b_j)
tuples; coverage drops sharply. PPMI's known failure mode: low-count
cells get unstable PMI, PPMI clipping to 0 (Levy-Goldberg 2014).

**R3 per-query expected log-bias scales like coverage, decaying at
least 1/K^2 unless NUM_CONCEPTS scales as K^2.** Need ~1600 at K=16
and ~50000 at K=32 to maintain coverage.

R10 modifies the retrieval kernel multiplicatively through soft-AND
of concept activations across the POOL, not just the query. Pool
entries are themselves long; pool-side concept density rises with K.
**R10 grows where R3 shrinks. Inverse-correlated for principled reasons,
not noise.**

## Why R10+R3 actively interfere (math story)

Both built from the SAME PPMI concept set with the SAME activation
function `(idx[:,i]==b_i) & (idx[:,j]==b_j)`. R10's `s_b = concept_active
@ query_active.T` and R3's `query_active @ vote_logp` use OVERLAPPING
SIGNAL.

When a query activates concept c:
- R10 up-weights pool entries that have target distribution biased
  toward {b1...bm}
- R3 ALSO adds those bytes' log-vote to the W readout

Same evidence counted twice, then mixed by `P = ALPHA P_retr +
(1-ALPHA) P_W`. **Logit double-counting** -- analogous to the
rank-equivalence finding for MIR.

-0.13 BWT drop at K=32 from adding R3 to R10 is consistent with mild
variance-inflation from doubled bias terms.

## Five rescue experiments (ranked by power)

### Rank 1 (highest power) -- Orthogonal-concepts R3

Build R3 concepts from a DISJOINT PPMI set: use triples (i,bi,j,bj,k,bk)
instead of pairs, or use bytes that R10 doesn't activate (low |PMI|).
Predict: if compound real, R3-orthog + R10 > R10 alone by >=0.05 BWT.
If still null, double-counting confirmed, redundancy is geometric.

### Rank 2 -- Replay + R3-only (R10 OFF)

Cleanest 2-way compound test because R3 doesn't touch retrieval.
Predict: small positive (0.03-0.08) if mechanisms truly orthogonal;
null otherwise.

### Rank 3 -- K-scaled NUM_CONCEPTS for R3

Set NUM_CONCEPTS = 100 * (K/4)^2 so coverage stays constant. If R3
returns at K=16/32 with this scaling, K-vanishing story confirmed
(sparsity-driven). If R3 stays null even with matched coverage, the
bias term is genuinely K-incompatible.

### Rank 4 -- R10-prioritized replay

Use R10's concept-fusion score to SELECT which pool entries to replay
(instead of uniform random). Predict: bounded by priority-replay
ceiling (~+0.02 per MIR-canonical), modest.

### Rank 5 -- Pool-loss-priority replay (open MIR axis)

Cheapest exploratory: does ANY priority replay beat uniform on this
substrate?

## Honest bottom line

The substrate has:
- **ONE BWT-recovery mechanism**: random replay (+0.66-0.73 at K=4-32)
- **ONE retrieval-augment mechanism**: R10 at K>=16 (+0.048 to +0.193
  monotone in K)
- **R3 is K=4 specific** (vanishes by K=16 for fixable mathematical
  reasons)

If rescues #1 + #2 are null, write up replay and R10 as SEPARATE
publications, not as a compound stack. The substrate-uniqueness story
(decompose / edit / recompose / interpret) is independent.

**Recommended single experiment to settle compound question**:
orthogonal-concept R3 (triples) + R10 at K=32, with and without replay.

## Sources

- [van de Ven 2022 Three Types of Incremental Learning, Nature MI](https://www.nature.com/articles/s42256-022-00568-3)
- [Goldfarb-Hand 2025 Replay Can Provably Increase Forgetting CoLLAs](https://arxiv.org/abs/2506.04377)
- [Buzzega 2020 DER/DER++ NeurIPS](https://arxiv.org/abs/2004.07211)
- [Verwimp 2021 Rehearsal Revealed ICCV](https://ar5iv.labs.arxiv.org/html/2104.07446)
- [Aljundi 2019 MIR NeurIPS](https://arxiv.org/abs/1908.04742)
- [Kozal 2024 Continual Learning with Weight Interpolation CVPRW](https://arxiv.org/html/2404.04002v2)
- [Provable Effects of Data Replay: Feature Learning Perspective](https://arxiv.org/pdf/2602.02767)
- [Scalable Strategies for CL with Replay 2025](https://arxiv.org/html/2505.12512v1)
