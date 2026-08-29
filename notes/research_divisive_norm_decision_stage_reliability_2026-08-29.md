---
topic: divisive normalization at a decision/combine stage vs preserved per-source magnitude for reliability-weighted cross-channel evidence pooling
requested_by: solver problem `read_terminal_bundle_stores_normalize_per_component_not_pooled` (crux question on the typer's cross-role combine)
date: 2026-08-29
lit_scan_lanes: 3 (Sonnet, parallel) + Opus/Sonnet-5 synthesis
calibration: lit-scan calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis capped P<=0.50
---

# Research: divisive normalization at the decision stage vs raw-magnitude-encodes-reliability

## HEADLINE

**The brain does NOT independently rescale each evidence source to a common/equal magnitude before a
reliability-weighted combine — that operation does not appear anywhere in the divisive-normalization or
cue-integration literatures, and it structurally destroys the thing (magnitude/gain) that carries reliability.**
What the brain DOES do under the name "divisive normalization" (Carandini & Heeger 2012; Louie & Glimcher
2011/2013; Ohshiro/Angelaki/DeAngelis 2011/2017) is a **SHARED, POOLED divisor** — the identical denominator
(built from the *sum* of all sources' drive) applied to every source — which compresses the overall scale but
**algebraically preserves the ratio between sources**. That is a different operation from "normalize each source
to a common scale," and it is measured, independently, in LIP, OFC, and multisensory (MSTd) cortex. Separately,
Bayesian/optimal cue-combination theory (Ma/Beck/Latham/Pouget 2006 probabilistic population codes; Fetsch/
DeAngelis/Angelaki 2011-2013; Ernst & Banks 2002 MLE) treats each source's raw response gain/magnitude as the
literal carrier of its reliability — summing (or inverse-variance-weighting) the RAW magnitudes is the optimal
rule; there is no normalize-to-common-scale step in any of these models. **Verdict on the crux (#4): "weight-and-
pool the raw per-source magnitudes" is MORE brain-faithful than "divisively normalize each source to a common
scale, then weight-and-pool."** The measured harm in the typer (divnorm on the per-role sup_map hurts at low
n_train, -0.06/-0.05/-0.03 CI-separated, shrinking to neutral as n grows) is exactly the predicted signature of
inserting an extra, un-calibrated automatic-gain step in front of an already-explicit, separately-learned
precision weight (`shard_weights_`) — a "stacking two reliability mechanisms" failure mode that no reviewed
model uses, and that is worst exactly where the explicit weight is noisiest (low n) and washes out once the
weight is well-estimated (high n) — matching the measured n-dependence.

## (a) One-paragraph direct answer to the bottom-line question

Un-normalized per-source magnitude is the **correct, brain-faithful choice**, not a bug, when a downstream
combine already applies (or is meant to apply) reliability-based weighting — because in every literature this
scan touched (divisive normalization in decision/sensory cortex, probabilistic population codes, MLE cue
integration), magnitude/gain IS the reliability signal, and the combine step (sum, or inverse-variance-weighted
sum) is defined to operate on that raw magnitude. Divisively normalizing each source to a shared/common scale
BEFORE the combine either (i) erases the very information the weighting needs (if done per-source
independently), which no paper describes as correct, or (ii) is redundant with / miscalibrates an already-
explicit learned weight (if done as a shared pooled gain, the brain-faithful form), which is the literal
mechanism behind the measured typer harm. The single exception the literature supports is a SHARED pooled gain
term computed BEFORE any explicit weight is fit/learned (so the weight-learning process sees a consistently-
scaled input) — not inserted downstream of an already-fit weight.

## (b) Per-question findings with citations

**Q1 — per-channel-then-pool or pool-then-normalize?**
All three verified circuit families use the same architecture, and it is neither of the two poles as commonly
imagined — it is **"combine (sum) the sources into one drive term, then divide that combined/pooled drive
signal by a POOLED (population- or set-level) normalization term that is common to the whole pool being read
out."**
- Carandini & Heeger 2012 (*Nat Rev Neurosci* 13:51-62) canonical form: R_i = drive_i^n / (sigma^n +
  sum_j drive_j^n) — one shared denominator (built from ALL channels) divides every channel's OWN numerator.
  Ratios between channels are preserved exactly (R_i/R_k = drive_i/drive_k regardless of the shared divisor).
- Louie, Grattan & Glimcher 2011 (*J Neurosci* 31:10627-10639, PMC3285508) and Louie, Khaw & Glimcher 2013
  (*PNAS* 110:6139-6144, PMC3625302): value of option i is divided by (sigma + sum of ALL options' values) — the
  2013 paper states explicitly that "the presence of all option values in the denominator... mediates the
  relative nature of the value coding." Confirmed directly from primary text: relative differences between
  sources are PRESERVED; only overall scale compresses.
- Ohshiro, Angelaki & DeAngelis 2011 (*Nat Neurosci* 14:775-782, PMC3102778) and 2017 (*Neuron* 95:399-411,
  PMID 28728025): combined drive E = d1*I1 + d2*I2 is formed FIRST (a weighted linear sum across modalities),
  THEN raised to a power and divided by a population-pooled term (mean activity across N multisensory neurons).
  This is "sum, then normalize by a population pool" — not per-channel normalization followed by summation; the
  math is not equivalent because the nonlinearity sits between the sum and the division.
  Confidence: HIGH (verified via primary full text for all four papers).

**Q2 — does raw magnitude encode reliability, or should sources be normalized to a common scale first?**
- Ma, Beck, Latham & Pouget 2006 (*Nat Neurosci* 9:1432-1438, PMID 17057707): for Poisson-like probabilistic
  population codes, the Bayes-EXACT combination of two independent cues is literal SUMMATION of their raw
  activity vectors — no normalization step. Each population's overall response GAIN is what encodes reliability
  (higher gain -> higher precision -> automatically contributes more to the sum). Confidence: HIGH.
- Fetsch, Pouget, DeAngelis & Angelaki 2011/2012 (*Nat Neurosci* 15:146-154) and the review Fetsch, DeAngelis &
  Angelaki 2013 (*Nat Rev Neurosci* 14:429-442, PMID 23686172): decoding RAW MSTd firing-rate gain predicts
  behavioral reliability-weighting in vestibular-visual heading discrimination — gain literally tracks
  reliability. No study runs the direct counterfactual "artificially equalize the two cues' magnitude and show
  weighting breaks," but the mechanism (gain=reliability, sum raw) makes that outcome the model's direct logical
  entailment. Confidence: MEDIUM-HIGH (mechanism measured; the specific counterfactual is inferred, not run).
- Ernst & Banks 2002 (*Nature* 415:429-433, PMID 11807554), MLE framework: weights w_i = (1/sigma_i^2) /
  sum_j(1/sigma_j^2) are applied to each cue's RAW, natively-scaled estimate. The model's only "normalization"
  is that the weights sum to 1 — not that the cues' own magnitudes are pre-equalized. Pre-normalizing a cue to a
  fixed scale before applying w_i is not part of any MLE cue-integration model reviewed and would be redundant
  with (or corrupt calibration of) the explicit weight. Confidence: HIGH for the model form.
- No genuine literature dissent found: Drugowitsch et al. 2014 (*eLife* 3:e03005, robust averaging) and Rohde/
  van Dam/Ernst 2016 (*Multisensory Research* 29:279-317, tutorial) document real deviations from pure
  inverse-variance-weighted averaging, but these are attributed to causal inference (whether to fuse cues at
  all) or misestimated reliabilities — never to a "normalize-then-weight" architecture being correct.

**Q3 — Ohshiro/Angelaki/DeAngelis: where does divisive normalization sit, does it predict inverse effectiveness
and reliability-weighting as emergent?**
Verified: Ohshiro, Angelaki & DeAngelis, *Nat Neurosci* 14:775-782 (2011, THEORETICAL-MODEL, fit to pre-existing
superior-colliculus/MSTd data) and *Neuron* 95:399-411 (2017, closer to MEASURED-IN-BRAIN — new MSTd recordings
testing a specific diagnostic cross-modal suppression signature, confirmed, disfavoring a subtractive-inhibition
alternative). The 2011 paper states the model "accounts naturally" for **inverse effectiveness** (weak unimodal
inputs give proportionally larger multisensory boosts) as falling directly out of the interaction between the
expansive output nonlinearity and normalization saturation — not a hand-tuned add-on. It also argues the SAME
pool-normalization mechanism reproduces apparent **reliability-dependent reweighting** "without requiring
dynamic changes in synaptic weights" — i.e., emergent from the same computation, not a separate mechanism.
However, this is not unanimous: PPC theory (Ma et al. 2006; Beck, Latham & Pouget 2011, *J Neurosci*,
"Marginalization in neural circuits with divisive normalization" — titles found via search, not independently
fetched, MEDIUM confidence) locates reliability-weighting upstream, in each unisensory population's own gain,
with normalization/summation doing near-optimal combination "for free" downstream — a related but distinct locus
claim. A separate computational paper (PMC9393257) proposes LEARNED synaptic reweighting as a complementary,
SEPARATE mechanism (likely for slower experience-dependent recalibration, e.g. ventriloquism aftereffects) that
a purely static normalization circuit would not explain — meaning the field treats "automatic pool-normalization
gain control" and "explicit/learned precision weighting" as two coexisting, non-identical mechanisms, not one
substituting cleanly for the other.

**Q4 — bottom line, more or less brain-faithful, and where the literature is split.**
Answered in HEADLINE/(a) above. The one genuine gap: **no paper models what happens when a pool-normalization
gain-control step and an explicit/learned precision weight act on the SAME signal simultaneously** (Lane C
searched directly for this and found nothing — flagged as an honest absence, not a search failure, since the
adjacent loci for reliability-weighting — population gain, pool normalization, learned synaptic weight — are
each independently documented but never stacked in one model in the literature reviewed). The typer's measured
harm is therefore a **novel-synthesis prediction, not a directly-confirmed one**: extending the "gain=reliability,
don't duplicate it" principle to the specific case of "automatic normalization stacked on an explicit LOO-learned
weight." Capped at P<=0.50 per calibration discipline (see below).

## (c) PINNED vs OUR-INVENTION labeling

- **"Divisive normalization at a decision/combine population"** — **PINNED.** Directly measured (not just
  theorized) in LIP (Louie, Grattan & Glimcher 2011, single-unit recordings), OFC (Louie, Khaw & Glimcher 2013;
  Padoa-Schioppa & Conen 2017 review), and multisensory cortex MSTd (Ohshiro/Angelaki/DeAngelis 2017, Neuron,
  new recordings confirming the model's diagnostic suppression signature). Independently replicated across three
  circuit families with a consistent equation form (shared pooled denominator, numerator-preserving ratios).
  This is as solid as systems-neuroscience computational claims get.
- **"Divisive normalization at a hippocampal/WM memory register"** — **OUR-EXTENSION-UNDER-TEST** (unchanged
  from the parent problem's classification, reconfirmed by this scan). Carandini-Heeger's canonical computation
  is documented in sensory cortex (V1/MT), decision-association cortex (LIP/OFC), and multisensory cortex
  (MSTd/SC) — NOT specifically characterized in hippocampal CA3/CA1 pattern-completion/separation circuits or
  prefrontal working-memory maintenance circuits as the mechanism for an ITERATIVE SERIAL decode-and-suppress
  readout. It is a plausible, motivated extension by analogy (the computation is described as "canonical" and
  general enough to plausibly recur), and the register experiment's own measured result (0.367->0.988) is real
  evidence FOR the extension working here — but it is evidence from OUR substrate, not a citation of the brain
  doing this in a memory register. Keep the register/multibank divnorm switch (it is measured-good), but do not
  upgrade its brain-fidelity label past OUR-EXTENSION-UNDER-TEST without a citation specific to hippocampal/PFC
  working-memory readout normalization.

## (d) Adjacent-component flag: is anything in the reader pipeline not brain-foundational and optimizable?

Yes — **the typer's `shard_weights_` (LOO-fit explicit per-role scalar weight) is itself the less brain-faithful
piece, not the missing normalization.** The literature's actual reliability-weighting mechanisms are (i) an
automatic GAIN that scales with a population's own precision (Ma/Beck/Latham/Pouget: "gain = reliability," no
fitting required, the weighting falls out of a raw sum), or (ii) slow learned synaptic reweighting for
experience-dependent recalibration (PMC9393257). Our typer's LOO-fit scalar is architecturally closer to (ii)
(a trained weight) but is fit OFFLINE per role rather than continuously from evidence-population gain, so it
carries none of the "for free, self-calibrating" property that makes option (i) elegant and hard to miscalibrate.
**A more brain-foundational optimization worth a follow-on build/research probe:** could each role-shard's raw
stored-evidence magnitude be engineered to directly encode confidence/reliability (e.g., scaled by the number of
contributing exemplars, or by an inverse-variance-like statistic of that shard's training signal), so that the
weighted combine becomes a straight, un-learned SUM of raw magnitudes (matching the Ma-Beck-Latham-Pouget PPC
result) instead of requiring a separately-fit LOO weight at all? If the raw magnitude already carries the
reliability signal by construction, the "does normalization help" question dissolves — there would be nothing
left to inject a competing automatic gain against. This reframes the typer's whole design question from "how do
we combine two competing reliability mechanisms" to "can we build ONE mechanism (self-calibrating magnitude) and
retire the other (LOO-fit weight)" — a higher-fidelity direction than either arm of the original crux.

## Cheap decisive test

Reuse the existing, already-built harness (`experiments/exp_read_terminal_divnorm_typer_v1.py`, no rebuild
needed) and extend it with a THIRD arm alongside the existing per-component floor and the already-measured
sup_map-divnorm arm:

1. **Arm 1 (floor, already measured):** per-component `S_i/|S_i|` on the sup_map, existing explicit
   `shard_weights_` combine. mean_acc 0.8333 @ n_train=40 (byte-faithful, reused).
2. **Arm 2 (already measured, HURTS):** `norm="divnorm"` applied to the sup_map BEFORE cleanup/argmax, existing
   explicit weight combine. -0.0625/-0.0486/-0.0312 CI-separated at n=8/16/24.
3. **Arm 3 (NEW — this crux's candidate, the "decision-stage" reading):** leave the sup_map untouched
   (per-component, as in Arm 1); instead apply a SHARED pooled divisor to the per-role CLEANUP SCORE vector
   (one scalar computed from the combined/pooled score magnitude across ALL roles for that trial — the
   Carandini-Heeger/Louie-Glimcher form, ratio-preserving), THEN apply the existing `shard_weights_` and sum.
4. **Arm 4 (NEW — the literature's clearly-wrong case, included as a discriminating control):** normalize each
   role's score INDEPENDENTLY to its own unit scale (z-score or divide-by-own-norm per role — i.e., erase
   cross-role relative magnitude entirely) before applying `shard_weights_` and summing.

Run all four at n_train in {8, 16, 24, 40} with the existing 5-seed protocol and the existing scrambled-label
info-free twin.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **HARD-PASS for "insertion point matters, shared-pool-at-decision is salvageable":** Arm 3 matches or beats
  Arm 1 (per-component floor) CI-separated at n_train=8/16/24 (margin >= +0.02), AND Arm 3 clearly beats Arm 2
  (the already-measured harmed sup_map arm) CI-separated at the same n's, AND the info-free twin loses for Arm 3.
  This would mean the harm in Arm 2 was about WHERE the pooled norm sits in the pipeline (before vs after
  cleanup), not about stacking pooled-gain-control on an explicit weight per se.
- **HARD-FAIL for that same claim (predicted primary outcome per this scan's synthesis):** Arm 3 ALSO hurts
  CI-separated at low n_train, comparably to Arm 2 (within ~0.02 of Arm 2's harm at each n). This would confirm
  the mechanism is "any automatic pooled gain stacked on an already-explicit LOO-learned weight miscalibrates
  it," independent of exactly where in the pipeline the gain is inserted — the literature-predicted outcome.
- **HARD-PASS for "raw-magnitude-encodes-reliability is the correct read" (the Q4 crux):** Arm 4 (independent
  per-role equalization, the "erase relative magnitude" case) is CI-separated WORSE than both Arm 2 and Arm 3 at
  every n_train tested. This is the sharpest test of the headline claim — literature predicts Arm 4 is the worst
  arm because it is the only one that structurally destroys cross-role relative magnitude rather than just
  applying a shared/pooled rescale.
- **HARD-FAIL for that claim:** Arm 4 is statistically indistinguishable from or better than Arm 1/Arm 3 — would
  mean cross-role relative magnitude is NOT load-bearing for this organ's combine, contradicting the PPC/MLE
  reliability-encoding framework as applied here (a real, informative negative — would mean the typer's 2-way
  decision does not actually depend on relative magnitude fidelity the way vestibular-visual heading does, most
  likely because `shard_weights_` already fully absorbs whatever relative-magnitude information existed, making
  the input scale irrelevant once an explicit weight is present).

## Cross-thread synthesis

This directly extends the SOLVED.md finding for
`read_terminal_bundle_stores_normalize_per_component_not_pooled` (typer table row: divnorm on sup_map HURTS at
low load, "double-counts" the already-explicit `shard_weights_` gain). That result was empirical without a named
brain mechanism for WHY stacking hurts; this scan supplies the mechanism and a name for it: the brain's own
reliability-weighting literature treats "automatic pooled gain" (normalization) and "explicit/learned precision
weight" (synaptic reweighting) as two SEPARATE, non-stacking loci for the same computational job, and no
reviewed model combines them on one signal. It also sharpens the general §2b audit rule the SOLVED.md note
proposed ("overloaded store + iterative/direction-sensitive readout -> divnorm") with a THIRD gating condition
specific to weighted cross-source combines: **do not insert automatic normalization gain-control anywhere in a
pipeline that already carries an explicit, separately-calibrated precision/reliability weight for the same
sources** — independent of overload or readout class. This is a new, generalizable caution beyond the original
audit rule, applicable to any future organ (not just the typer) that combines multiple weighted evidence
sources.

## Substrate-product implications

- **Do not build** "normalize each source to a common scale, then weight-and-pool" as a general substrate
  default for multi-source weighted combines — it is measured-harmful in the one organ tested and is
  literature-discouraged in general (it either erases the reliability signal or double-counts an explicit
  weight).
- **Do run** the 4-arm decisive test above before concluding the crux is fully closed — it costs one more small
  experiment on already-built infra and would either close the "insertion point" question (HARD-PASS/FAIL 1) or
  confirm the sharper "relative magnitude is load-bearing" claim (HARD-PASS/FAIL 2), either of which strengthens
  the audit rule with a real citation-grounded mechanism instead of an empirical-only rule.
- **Higher-value follow-on** (flagged in (d)): investigate whether role-shard evidence magnitude can be
  engineered to directly encode reliability (contributing-exemplar count, inverse-variance-like statistic) so
  the LOO-fit `shard_weights_` can eventually be RETIRED in favor of a raw-magnitude sum — a more brain-
  foundational (PPC-style, self-calibrating) design than either arm of the original crux. This is a candidate
  next problem, not scoped or built here.

## Citations (verified count)

16 distinct sources identified across all three lanes. **11 verified via primary full text / DOI / PMID / PMC ID**
(pulled quotes or equations directly, not just recalled): Carandini & Heeger 2012 (Nat Rev Neurosci); Louie,
Grattan & Glimcher 2011 (J Neurosci, PMC3285508); Louie, Khaw & Glimcher 2013 (PNAS, PMC3625302); Ohshiro,
Angelaki & DeAngelis 2011 (Nat Neurosci, PMC3102778); Ohshiro, Angelaki & DeAngelis 2017 (Neuron, PMID 28728025);
Ma, Beck, Latham & Pouget 2006 (Nat Neurosci, PMID 17057707); Fetsch, DeAngelis & Angelaki 2013 (Nat Rev
Neurosci, PMID 23686172); Fetsch, Pouget, DeAngelis & Angelaki 2011/2012 (Nat Neurosci, DOI nn.2983); Ernst &
Banks 2002 (Nature, PMID 11807554); Drugowitsch et al. 2014 (eLife 3:e03005); PMC9393257 (crossmodal synaptic
plasticity / reliability recalibration model). **5 medium-confidence** (found via search snippets / secondary
sources, not independently fetched full text this pass): Louie et al. 2014 (J Neurosci, "Dynamic Divisive
Normalization Predicts Time-Varying Value Coding"); Padoa-Schioppa & Conen 2017 (Neuron review); Beck, Latham &
Pouget 2011 (J Neurosci, "Marginalization in neural circuits with divisive normalization"); Jacobs 1999 (Vision
Research, recalled from training only); Rohde, van Dam & Ernst 2016 (Multisensory Research, tutorial review).
**Calibration penalty applied:** the general architectural answer (Q1/Q2, "shared pooled divisor preserves
ratios; raw magnitude is the reliability code") is well-supported by convergent, independently-replicated,
primary-verified sources — held at P=0.75 (deflated from an intuitive ~0.90 for the fact that no paper runs the
direct "artificially equalize cue magnitude, show weighting breaks" counterfactual manipulation). The
substrate-specific extension (Q4's typer prediction, the "stacking two reliability mechanisms" generalization,
and the falsifiable-prediction table above) is genuine novel synthesis — **capped at P=0.50** per
[[feedback-lit-scan-calibration-penalty]].
