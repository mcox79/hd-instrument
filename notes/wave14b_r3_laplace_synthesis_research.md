# R3-Laplace neutral finding — research synthesis

Returned 2026-05-19. Adjudicates the math agent's prediction against
empirical R3-Laplace result (NEUTRAL at K=4 and K=32 vs R10-only).

## TL;DR

Laplace result is **consistent with — and refines — the math agent's
deeper theory**. The agent was right about the variance-explosion
mechanism. They were wrong (by their own decision rule) about what
fixing it would unlock. Properly-smoothed R3 is **redundant with R10's
evidence base, not orthogonal to it**, and the substitution-not-
orthogonality finding is now **over-determined by four independent
arguments**. R3-compound is **closed** for this substrate.

## The bet structure was correct

Math agent factored failure as `harm = variance_explosion + redundancy`:
- Variance term: broken std=1.006 → Laplace std=0.098 (10x reduction).
  At K=32 broken R3 was -0.14 BWT; Laplace term is now ~0. **CONFIRMED.**
- Redundancy term: revealed at ~0 +/- 0.003 after variance fix.

Agent's decision rule explicitly priced this outcome: "BWT in (-0.92,
-0.82): R3 compound at K=32 was implementation-broken; correct R3 is
now silent/no-harm at high K." We landed at -0.866 — squarely in that
bucket. Bet was **structurally correct as Bayesian update**.

This is **refinement, not contradiction** of compound-falsification
theory.

## Substitution over-determined by 4 arguments

1. **Shared evidence base** (info-theory). Both R10 and R3 consume
   identical `concept_active = (idx[:,i]==b_i) & (idx[:,j]==b_j)`.
   Same evidence enters final softmax through two paths. Structurally
   identical to **double-counting in meta-analysis** (Senn 2009):
   non-independent evidence sources don't add information.

2. **Two-stage estimator variance ceiling** (statistical). Two
   estimators sharing nuisance parameters (PPMI concept set from
   corpus A pool) have combined variance reduction bounded by
   *independent component*, not sum (Hardin 2002 sandwich estimator).
   Independent component here is ~0.

3. **Mode-connectivity geometry** (CL theory). Both R10 and replay
   push W toward corpus-A low-loss basin. R3 modifies readout decision
   but readout is computed from same W. All three are projections
   onto the same basin. Verwimp 2021, Goldfarb-Hand 2025
   non-monotonicity in over-parameterized linear regression — our
   exact regime.

4. **Empirical**: Laplace delta = +0.003 at K=32, t-stat rounds to 0.

## DER++ vs R10+R3: estimator independence is the key

DER++ (Buzzega 2020) gets ~1.4-pt marginal from logit-distill + reservoir
replay. **DER++ logits come from a separate TEMPORAL SNAPSHOT** of the
model — past-self ensemble. Different estimator of target distribution.

Our R3 logits come from PPMI on the same pool R10 retrieves over. No
temporal offset, no estimator diversity. "Two readers" share both
corpus and extraction procedure.

**Sharpened prediction**: compound returns iff second intervention
introduces a genuinely independent estimator, not just different
functional form over same statistic.

Achievable via:
- (a) Disjoint concept set (corpus B, triples, MI-selected)
- (b) Temporal snapshot of W itself (DER++-style)

## The +0.154 R3-alone mystery is genuinely UNRESOLVED

Three competing explanations:

| Explanation | R3-Laplace-alone @ K=4 prediction |
|---|---|
| Real K=4 readout-bias effect | +0.10 to +0.16 |
| Broken-normalizer artifact (spikes landed favorably) | +0.00 to +0.04 |
| Variance-explosion random-seed luck | wide spread, mean ~0 |

The K=4 Laplace+R10+replay result (-0.002) does NOT settle this — the
compound test conflates "R3 has no signal" with "R3 is redundant with
replay+R10."

**Decisive experiment**: R3-Laplace ALONE (no replay, no R10) at K=4,
3 seeds, vs no-concept baseline. Cheap (~10 min), decisive.

## Three follow-up experiments ranked

1. **R3-Laplace ALONE at K=4 vs baseline, 3 seeds** — settles +0.154
   mystery. Decisive. **Must run** — leaving it open is intellectually
   dishonest given the headline made it into STATE.
2. **R3 with concepts from corpus B's PPMI** (disjoint evidence base)
   + R10-A at K=32 with replay. Tests if "shared evidence" is the
   binding constraint. +0.03-0.05 if mechanism right, null otherwise.
3. **R3-Laplace + R10 at K=32 with replay=0** — does replay mask
   compound by dominating both signals? Lower priority; Goldfarb-Hand
   predicts substrate basin too narrow even without replay.

Skip K-scaled NUM_CONCEPTS — different rehab axis (sparsity), already
addressed.

## Honest bottom line + publishable framing

R3-compound on this substrate is **closed** (with caveat #1).

**Publishable methodological contribution:**

> "Two interventions on different pipeline stages do not compound when
> they consume the same evidence base, regardless of normalization. We
> show this empirically (R10 retrieval-kernel modifier + R3
> readout-logit modifier with proper Laplace smoothing, n=3 seeds) and
> explain it via three independent theorems: meta-analytic
> double-counting (Senn 2009), two-stage estimator variance ceiling
> (Hardin 2002), and mode-connectivity in over-parameterized continual
> regression (Goldfarb-Hand 2025). Compound returns when the second
> intervention introduces an independent estimator (DER++ via temporal
> snapshot)."

Constructive prescription: for compound, make estimators
**evidence-independent**, not just functionally-different.

## STATE retraction required

Update STATE_2026_05_19.md: retract the standalone +0.154 R3 headline
pending experiment #1. Move R3 row from "Confirmed positives" to "needs
final verification" pending R3-alone-Laplace test.

## Sources

- [Goldfarb-Hand 2025 Replay Can Provably Increase Forgetting](https://arxiv.org/abs/2506.04377)
- [Senn 2009 Overstating the evidence: double counting in meta-analysis](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2653069/)
- [Hardin 2002 Robust variance estimator for two-stage models](https://journals.sagepub.com/doi/pdf/10.1177/1536867X0200200302)
- [Buzzega 2020 DER/DER++ NeurIPS](https://proceedings.neurips.cc/paper/2020/file/b704ea2c39778f07c617f6b7ce480e9e-Paper.pdf)
- [Verwimp 2021 Rehearsal Revealed ICCV](https://ar5iv.labs.arxiv.org/html/2104.07446)
