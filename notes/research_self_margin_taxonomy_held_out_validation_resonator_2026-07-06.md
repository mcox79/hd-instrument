# RESEARCH — Held-out validation of the self-margin taxonomy (Candidate A: resonator capacity)

**Date:** 2026-07-06
**Author:** research (Sonnet 5)
**Trigger:** Director ask to resolve the CG_META candidacy of
`reference_self_margin_taxonomy_splits_by_decode_regime_2026-07-06` (assessed in
`research_self_margin_taxonomy_synthesis_cg_meta_assessment_2026-07-06.md` as "CG_META-candidate, not yet
cert-tierable" due to in-sample circularity: every capability used to build the 3-family taxonomy was also used
to test it). That note sketched a concrete held-out test and pre-registered two predictions before any
recompute. This note EXECUTES Candidate A (the primary, richer-data half of that test) exactly as specified:
zero new trials, pure off-disk recompute against already-landed FULL metrics, prediction committed before the
fit is computed.

**Verification method:** `exp_resonator_capacity_gpu_v1`'s own script
(`experiments/exp_resonator_capacity_gpu_v1.py`) and `metrics.json` read directly off disk; secondary check of
`exp_capacity_cliff_graceful_full_v3`'s `metrics.json` and its ancestor script
(`experiments/exp_capacity_cliff_graceful_v1.py`). All numbers below are recomputed live in this drill
(`.venv/Scripts/python.exe`, numpy/scipy), not carried over from memory text.

---

## PRE-REGISTRATION (committed BEFORE the recompute below — do not revise after seeing the fit)

Per the synthesis note's Candidate A spec: `exp_resonator_capacity_gpu_v1` (K-way resonator-network
factorization; landed HARD_FAIL, `K2`:1.0, `K3`:0.7, `K4`:0.142 at `N=4096`, `M=30`) is predicted to be a
**superposition-crowded argmax decode**, i.e. ORDER-STATISTIC family (structurally the same regime as FHRR's
`K_crit`), with the synthesis note's own honestly-flagged ambiguity that it might instead be PRODUCT-LAW CHAIN
(iterative multi-factor search, factors resolved in sequence). **Both are ORDER-STATISTIC-family-adjacent, not
COLLISION-COUNT, not RESISTOR — that three-way exclusion is what this drill tests.**

Reading the resonator's own code (unit-magnitude complex phasor codebooks, elementwise-product binding,
`M=30`-ary codebook per factor, `K in {2,3,4}` factors, `N=4096`, iterative alternating-projection decode up to
`MAXIT=60`), I commit to the following SPECIFIC, mechanistically-derived predictions before touching the K3/K4
numbers as a fitting target:

1. **Order-statistic (flat) model.** At the "all other `K-1` factors exactly correct" fixed point, unbinding
   is EXACT for unit-magnitude phasors (`book * conj(book) = 1` elementwise), so the residual correlation
   `sc = books[k] @ conj(rr)` has a deterministic signal term `sc[true_k] = N` competing against `M-1 = 29`
   CLT-Gaussian competitors with mean 0, variance `N/2` (`Var[cos(uniform phase)] = 1/2`). This is EXACTLY the
   same `Phi(mu+z)^(m-1)`-type single-shot order-statistic machinery already coded 3x on this substrate
   (RNS, FHRR, reasoning-depth). **Prediction, committed now:** since `N=4096` and the competitor std is only
   `sqrt(N/2) = 45.25` (a z-score of ~90.5), the single-factor margin is essentially certain (`P approx 1`)
   REGARDLESS of `K` — i.e. this family predicts a FLAT, near-ceiling success curve across `K in {2,3,4}`,
   with joint success `= p_single^K approx 1` for all three.
2. **Product-law-chain model (the named ambiguity).** If instead the right frame is sequential/composed
   resolution across the `K` factors (or across the `C(K,2)` pairwise couplings introduced as `K` grows), the
   model is `P = p_hop^h(K)` for some per-hop probability `p_hop` and hop-count `h(K)` (candidates: `h=K`,
   `h=K-1`, `h=C(K,2)`), fit `p_hop` from the `K3` point (the only non-saturated calibration point available)
   and predict `K4` out of sample — the standard promotion-path discipline used for control-branching and
   reasoning-depth in this session.

**Committed HARD-PASS / HARD-FAIL bands (identical to the synthesis note's Candidate A pre-registration):**
HARD-PASS if per-cell ratio-error `<=1.5x` at all non-saturated cells (K3, K4) AND aggregate mean-ratio in
`[0.80,1.25]`. HARD-FAIL if aggregate mean-ratio outside `[0.60,1.70]` OR any cell `>2.0x` OR the classification
requires revision after seeing the fit.

---

## (a) HEADLINE

**HELD-OUT TEST RESULT: HARD-FAIL, as the synthesis note's own pre-registered contingency anticipated.**
Both the flat order-statistic model and every product-law-chain variant tried (hop-count `= K`, `= K-1`, or
`= C(K,2)`) predict a K4 success rate 3.4x-7.1x HIGHER than the measured `0.142`, and the flat model's aggregate
mean-ratio across the two non-saturated cells is `4.24` — nearly 2.5x past the `[0.60,1.70]` HARD-FAIL boundary,
and the single worst cell (`K4` under the flat model) misses by `7.06x`, more than 3x past the `2.0x` HARD-FAIL
bound. **Neither of the two families the taxonomy predicted (order-statistic, product-law-chain) reproduces the
observed cliff shape out-of-sample, and no revision of either family is attempted here (that would itself be a
second, independent HARD-FAIL trigger per the pre-registration).** Per the Director's explicit instruction, this
is reported honestly and not rescued: **the self-margin taxonomy is DESCRIPTIVE, not yet PREDICTIVE, and does
NOT earn CG_META promotion on this evidence. It remains filed as the reference it already is
(`reference_self_margin_taxonomy_splits_by_decode_regime_2026-07-06`); no CG_META atom should be minted.**

---

## (b) Cheap decisive test (executed this drill, zero new trials)

Reused exactly the machinery named in the synthesis note's own "cheap decisive test" section: the resonator's
own config (`N=4096`, `M=30`, `K in {2,3,4}`) plugged into (1) the standard `Phi`-style order-statistic margin
(here computed directly via the deterministic-signal-vs-CLT-Gaussian-competitor argument, equivalent to the
`hermgauss` quadrature machinery used in RNS/FHRR/reasoning-depth in the degenerate case where the signal term
has zero variance) and (2) three natural product-law-chain hop-count parametrizations. Recomputed live:

```
z-score (signal N=4096 vs competitor std sqrt(N/2)=45.25):        90.51
single-factor order-statistic success prob (predicted):            1.0000  (indistinguishable from ceiling)

Flat order-statistic joint-success prediction by K:
  K=2: predicted=1.0000  actual=1.0000  ratio(pred/actual)=1.000x   [SATURATED -- excluded from the gate,
                                                                       same convention as RNS/FHRR ceiling corners]
  K=3: predicted=1.0000  actual=0.7000  ratio(pred/actual)=1.429x   [within 1.5x alone, but see aggregate]
  K=4: predicted=1.0000  actual=0.1417  ratio(pred/actual)=7.059x   [FAILS 1.5x HARD-PASS; FAILS 2.0x HARD-FAIL]
  Aggregate mean ratio (K3, K4): 4.244                              [FAILS [0.80,1.25]; FAILS [0.60,1.70] HARD-FAIL band]

Product-law-chain variants (p_hop fit from K3, predicted at K4, out-of-sample):
  hops=K       (K3 hops=3, K4 hops=4):  fitted_p=0.8879  pred_K4=0.6215  actual=0.1417  ratio=4.387x  [FAIL]
  hops=K-1     (K3 hops=2, K4 hops=3):  fitted_p=0.8367  pred_K4=0.5857  actual=0.1417  ratio=4.134x  [FAIL]
  hops=C(K,2)  (K3 hops=3, K4 hops=6):  fitted_p=0.8879  pred_K4=0.4900  actual=0.1417  ratio=3.459x  [FAIL]
```

Every parametrization tried converges on the SAME qualitative finding: the real mechanism's `K3 -> K4`
collapse is steeper than ANY stationary-margin or geometric-chain-decay model predicts, by a consistent
factor of roughly 3.4x-7.1x. This convergence across four independent model attempts (one order-statistic, three
chain variants) is itself evidence the mismatch is structural, not an artifact of picking the wrong hop-count
convention.

---

## (c) Falsifiable predictions (restated with the now-measured result)

**HARD-PASS criterion (not met):** per-cell ratio-error `<=1.5x` at K3 AND K4, aggregate mean-ratio in
`[0.80,1.25]`, classification not revised after the fit. — K4 alone misses by 4.7x past the 1.5x bar under the
flat model (7.06x observed); no variant tried clears it.

**HARD-FAIL criterion (MET, on TWO independent grounds):**
- Aggregate mean-ratio outside `[0.60,1.70]`: measured `4.244` (flat model) — met.
- Per-cell ratio-error `>2.0x` at a non-saturated cell: `K4` measured `7.059x` (flat model), `3.46x-4.39x`
  (all three chain variants) — met, independently, under every family attempted.

Both independent HARD-FAIL triggers fire. Per the pre-registration's own third bullet ("either classification
requires revision after the fit is seen... that outcome specifically falsifies the CLASSIFIER's prospective
value") — I am NOT revising the classification, NOT inventing a fourth family, and NOT relaxing the tolerance
to rescue this. That is the honest, called-for outcome given the instruction not to rescue a failed held-out
test.

---

## (d) Cross-thread synthesis

- **Why the mechanism resists, mechanistically (an honest diagnosis, not a rescue attempt):** the resonator's
  own dynamics show that IF the joint fixed point ("all K-1 other factors exactly correct") is reached, the
  remaining single-factor margin is essentially certain (`z approx 90`) — meaning the observed `K3=0.7`,
  `K4=0.142` collapse is NOT a margin-shrinkage phenomenon at all (unlike RNS's sub-block margin, FHRR's
  crosstalk-variance margin, or reasoning-depth's per-hop capture probability, all of which degrade via a
  shrinking SNR at a STATIC or GEOMETRICALLY-COMPOSED decision). It is a **convergence-basin phenomenon**: the
  iterative alternating-projection search (starting from the mean-of-codebook initial guess, not the truth)
  must find the ONE correct joint configuration among `M^K - 1` competing joint hypotheses via a nonlinear
  recurrent map, and the number of locally-stable spurious joint fixed points plausibly grows combinatorially
  with `K` — a qualitatively different failure class from all 3 named families, closer to the multi-basin /
  spin-glass mean-field convergence dynamics this session's own field-advisor flags as a SEPARATE, currently
  0%-yield, already-closed field (`dynamics`, Arnold-tongue REFUTED) rather than to the order-statistic/
  collision-count/product-law-chain trio. I am NOT claiming this diagnosis IS a new closed form (that would be
  exactly the "revision after seeing the fit" the pre-registration forbids) — I am reporting it as the reason
  the taxonomy's three families do not apply here, consistent with (not contradicting) this session's own
  "three RESISTORS, three different reasons" framing in the synthesis note. This would be a genuine 4TH
  resistor class if promoted later, but that promotion is out of scope for THIS held-out-validation drill.
- **Secondary check (`exp_capacity_cliff_graceful_full_v3`, weaker test, non-decisive):** this cell's
  `metrics.json` stores only per-seed pass/fail gates (`monotone`, `graceful`, `R_at_013=1.0` in all 5 seeds),
  not a raw per-alpha curve, so a genuine ratio-error test across a range is not possible from what's on disk
  without a fresh dispatch (out of scope for a zero-new-trials cycle). What IS checkable: `R_at_013=1.0` is
  consistent with the standard Hopfield mean-field crosstalk argument (`Perror per bit = Phi(-1/sqrt(alpha))`,
  `alpha=0.13` -> per-bit error `~0.28%`, predicting near-ceiling pattern-level retrieval) — but this is a
  near-ceiling, non-discriminating comparison (both predicted and measured pinned at `~1.0`, exactly the kind
  of saturated corner RNS/FHRR themselves exclude from their own ratio-error gates), AND it is a confirmation of
  40-year-old established Hopfield capacity theory (Amit-Gutfreund-Sompolinsky 1985; the cell's own 2026-06-01
  pre-reg cites `alpha_c=0.138` directly from that theory), not a fresh exercise of THIS session's order-
  statistic quadrature toolkit. This secondary check is honestly reported as **inconclusive/non-discriminating**,
  not as independent confirmation — the decisive result of this drill rests on the resonator cell's 3-point
  K-sweep, which is the richer, genuinely-novel-to-this-session test case, exactly as the synthesis note framed
  it ("plausibly CG-tractable... named ambiguity... that specific, falsifiable, three-way exclusion is the
  actual test").
- Directly resolves the open question left by `research_self_margin_taxonomy_synthesis_cg_meta_assessment_
  2026-07-06.md` section (d)/(f): the HARD-FAIL branch of that note's own pre-registered falsifiable-prediction
  table is the one that fired. Does not reopen any of the 3 previously-closed RESISTOR rows (encoder,
  generalization, autonomous-decomposition) — this drill adds a 4th data point of the SAME kind (a capability
  whose collapse mechanism does not fit the 3-family taxonomy), independently arrived at via mechanistic
  derivation from the resonator's own code, not by inheriting any prior RESISTOR's reasoning.

---

## (e) Substrate-product implications

- **The taxonomy's ship-now value survives this result, narrowed:** the classification checklist
  (decode-mode -> family; margin-closed-form-or-not -> tier) remains a useful, cheap pre-flight step for
  capabilities whose collapse IS a stationary or chain-composed collision probability (5 confirmed CG cases
  in-sample) — but this drill shows it does NOT yet generalize to capabilities whose collapse is driven by
  ITERATIVE RECURRENT CONVERGENCE DYNAMICS (multi-factor resonator-style search), a mechanism class the
  taxonomy was never built to cover and, per this held-out test, cannot currently classify correctly. The
  honest product claim narrows from "classifies any decode-driven capability's collapse family" to "classifies
  SINGLE-SHOT or SEQUENTIALLY-COMPOSED argmax-decode capabilities' collapse family — untested and, on this
  evidence, NOT yet reliable for iterative/recurrent joint-search decode mechanisms (resonator-style
  factorization)."
- **No CG_META atom should be filed.** The taxonomy stays a reference (`reference_self_margin_taxonomy_
  splits_by_decode_regime_2026-07-06`), not a cert-tiered meta-law. Any future attempt to extend it to
  resonator-style iterative decode would need a genuinely new theory (a self-consistent mean-field / basin-
  counting argument), which is a real, identifiable, and potentially valuable follow-up research direction —
  but it is a NEW derivation project, not a promotion of the existing taxonomy, and should be scoped and
  pre-registered as such if pursued.
- This is a useful, concrete instance of the standing discipline "research every finding (middle/negative
  especially) for mechanism + envelope-push": the negative result here is not "the taxonomy is useless" — it
  precisely delineates WHERE the taxonomy's 3 families stop applying (recurrent/iterative joint search) and
  names the qualitatively different mechanism class responsible, which is itself the envelope-push (a mapped
  4th failure-mode candidate for a future, separately-scoped derivation cycle), without overclaiming a fix.

## (f) Citations (verified count)

Internal off-disk verification drill (zero new trials, per Director instruction) — no external lit-scan
dispatched this cycle (the mechanism derivation is a direct read of this substrate's own code, not a literature
claim). Verified on-disk sources:
- `experiments/exp_resonator_capacity_gpu_v1.py` (full script read, mechanism derived directly from the binding/
  unbinding code).
- `data/exp_resonator_capacity_gpu_v1/metrics.json` (HARD_FAIL, `K2:1.0, K3:0.7, K4:0.142`, `N=4096`).
- `experiments/exp_capacity_cliff_graceful_v1.py` (ancestor script; `N`, `alpha` grid, retrieval-dynamics
  mechanism read directly).
- `data/exp_capacity_cliff_graceful_full_v3/metrics.json` (HARD_PASS, 5/5 seeds, `R_at_013=1.0` all seeds).
- `preregs/2026-07_resonator_capacity_gpu_v1.md` (minimal; anchor/queue only, no additional theory).
- `notes/research_self_margin_taxonomy_synthesis_cg_meta_assessment_2026-07-06.md` (the pre-registration
  source this drill executes against).
- `notes/research_capability_self_margin_frontier_map_2026-07-06.md` (taxonomy inventory, cross-referenced).
- `python tools/orchestrator/research_field_advisor.py` run this cycle (context only: confirms `dynamics` field
  is already closed/0%-yield, consistent with — not the basis for — this drill's mechanistic diagnosis).
- Recompute performed live this drill: `.venv/Scripts/python.exe` (numpy, scipy.stats.norm), all numbers in
  section (b) freshly computed, not carried over from any prior note.

**Total: 8 verified internal sources + 1 live recompute. No external citations (mechanism derivation from
own code, not a literature claim; no generic-math external query was needed for this off-disk numeric test).**

## P_deflated (calibration penalty applied)

This is a negative (HARD-FAIL) result on a falsifiable pre-registered prediction, not a novel-synthesis claim
requiring a P estimate of "is this true" — the finding itself (both families fail, by a converging 3.4x-7.1x
margin across 4 independent model attempts) is measured directly, not estimated. Confidence that this HARD-FAIL
finding is itself correct (i.e., that I have not mis-specified the order-statistic or product-law-chain models
in a way that is unfairly disadvantaging the taxonomy): **P=0.85** (the flat order-statistic derivation is
exact and z=90.5 leaves no fitting-choice ambiguity; the three product-law-chain variants span the natural
hop-count conventions and all converge on the same qualitative miss, which is the strongest evidence the
mismatch is not a parametrization artifact). Per calibration discipline, deflated to **P_deflated=0.65** to
account for the residual possibility that a hop-count convention outside the three tried (or a two-parameter
fit) could close the gap — but note that finding such a fit AFTER seeing K3/K4 would itself independently
trigger the "classification revised after seeing the fit" HARD-FAIL clause, so this residual uncertainty does
not change today's verdict.
