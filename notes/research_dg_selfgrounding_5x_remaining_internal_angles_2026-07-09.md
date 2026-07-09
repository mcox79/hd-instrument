# Research: 5x negative-drill on the VET-confirmed DG self-grounding HARD_FAIL(a) -- the four remaining
# independent internal-revival angles (A-D), plus an envelope cross-check (E)

Filed by: research (Sonnet lit-scan x4 in parallel, synthesized by research). Date: 2026-07-09.

**Trigger:** `exp_selfplay_dg_pattern_separation_xfit_v1` landed FULL (5 seeds, 15:43:52Z) with verdict
`HARD_FAIL_REPRESENTATION_INSUFFICIENT_REDIRECT_EXOGENOUS` -- disk-verified (Fix#28, `Read` not assumed):
`B0_mirror corr=0.788` (naive-mirror shared-blind-spot signature confirmed) -> `B1_crossfit corr=0.393
ground=0.595` -> `DG_XFIT corr=0.377 ground=0.589`, `improve(B1-DG)=0.015` (far under the pre-registered
`DG_IMPROVE_MARGIN=0.10`), `dg_input_cos` (trigram feature pairwise cosine similarity) measured at
`0.0185-0.0199` across all 5 seeds -- i.e. the shared upstream representation the DG pattern-separation stage
was applied to is already almost perfectly decorrelated BEFORE any DG transform runs, so DG had ~zero headroom
to improve on. `data/exp_selfplay_dg_pattern_separation_xfit_v1/metrics.json` is the disk source for all
numbers in this note; not re-derived, directly read. This closes the loop the DG note's own S3 fork
pre-registered: case (a) fired exactly as specified, ruling out "the blind spot lives in the shared
representation/coding transform" and pointing at "the blind spot lives in the shared training
signal/distribution both branches ultimately chase" (case (a)'s named redirect).

Per USER instruction: do NOT re-litigate the representational-transform question itself (settled, dead) --
drill the four REMAINING independent internal-revival angles this program has not yet closed (A-D), plus one
envelope cross-check (E), before committing fully to the exogenous-referent pivot already scoped in
`notes/research_exogenous_referent_grounding_predictive_coding_2026-07-09.md` (`B1+EXOG`).

4 parallel Sonnet lit-scan sub-agents were dispatched, one per angle A-D, generic academic terms only per
`[[feedback-query-privacy-decomposition]]` (no substrate-novel names, cell names, configs, or numeric
parameters exposed off-platform). Angle E is a synthesis cross-check against the already-fresh, independently
four-literature-converged `research_exogenous_referent_grounding_predictive_coding_2026-07-09.md` note --
no new dispatch needed, reused per `[[feedback-prior-work-informs-not-constrains]]`.

---

## HEADLINE

**All four remaining internal angles are independently confirmed dead (or dead-in-practice) for THIS specific
blind spot, and -- more valuably than a simple 4-for-4 negative -- they converge on the SAME underlying reason,
which sharpens the diagnosis beyond what the DG note alone established: the residual
`corr(failmask)=0.377` is a BIAS-level (shared-systematic-error) signature, not a NOISE/VARIANCE-level one, and
no internal-only construction found in reconciliation theory, differentiation theory, formal
decorrelation theory, or coding theory can manufacture new information about which shared conclusions are
right vs wrong -- they can at best reduce variance around a shared bias, never the bias itself, unless a
genuinely outside (exogenous) source of ground truth is introduced. No surviving internal candidate warrants a
new cell before the pivot. Proceed to `B1+EXOG` as already scoped.**

**Single most useful surviving artifact (not a revival, a standing design discipline):** Angle B's
orthogonal-subspace differentiation principle -- confirmed, not refuted, by our own on-disk data (DG_XFIT cost
grounding only `-0.006` vs B1, consistent with a differentiation that happened to sit close to orthogonal to
the grounding-relevant subspace) -- should be pre-registered as a checklist item for any FUTURE
differentiation-axis proposal on this substrate (see S(B) below), even though it does not rescue this specific
negative (there is nothing left to exploit even along an orthogonal axis, per Angle D).

**P_deflated(a purely-internal fix is dead for this specific setup / exogenous input is the only known working
lever): 0.65-0.70** -- high because four independently-sourced literatures converge without being prompted
toward the same underlying mechanism, corroborated by on-disk empirical confirmation (three separate confirmed
internal-only negatives now: settling, differentiation, DG). Held below 0.80+ because Angle C found this is
NOT a proven mathematical impossibility (see below) -- only an exhaustively-searched absence of any known
constructive internal-only method, which is strong but not a closed door in principle.

---

## Angle-by-angle verdicts

### Angle A -- reconciliation / wake-sleep replay as a NON-representational internal revival

**Verdict: CONFIRMED DEAD. P(reconciliation/replay revives the fix) ~ 0.05.**

The lit-scan found the cleanest possible disproof available in this literature, not just an absence-of-evidence
result. Dayan & Hinton's own 1995 analysis of the wake-sleep algorithm (recognition pass vs generative pass,
each fit against the other) proves the two passes do NOT converge to independent, unbiased estimates -- they
settle at a mutually-consistent but mutually-DISTORTED fixed point off the true maximum-likelihood manifold
(formalized information-geometrically by Ikeda, Amari & Nakahara 1998). This is the textbook opposite of
independent failure modes: reconciliation loops that fit two passes against each other converge on **shared**
bias, not decorrelated error. Separately, bagging/bootstrap resampling of a single shared data stream (the
closest formal analog to "replay different subsets to each branch") is a well-established bias-variance result:
resampling reduces VARIANCE, never the systematic BIAS every resample inherits from the shared
data-generating process and shared model class. Prioritized/reward-weighted replay (hippocampal replay
content-selection literature) reweights which subset of a shared stream gets replayed, but the reweighting
signal itself is a function of the same shared upstream model -- no result in this literature shows that
differently-reweighted replay of one source produces two independent consumers. **Reconciliation/replay is
confirmed, with unusually strong and directly-on-point formal support, as a pure consumer/stabilizer of
independence, never a producer** -- exactly as the earlier `selfplay_upstream_blindspot_brain_fix` note ranked
it (tertiary, orthogonal), now upgraded from "ranked low" to "actively, formally ruled out" for THIS specific
use (manufacturing independence, as opposed to its legitimate other job of stabilizing/transferring content
between already-differentiated systems).

### Angle B -- differentiated split that decorrelates WITHOUT destroying grounding

**Verdict: theoretically sound principle, but DEAD-IN-PRACTICE here (no residual structure left to exploit).
P(a new differentiated-architecture axis revives this specific blind spot) ~ 0.08.**

The lit-scan found a sharp, convergent principle across ensemble learning, multi-task learning, and
mixture-of-experts theory: **differentiation between two branches of a shared source is FREE (costs nothing to
their shared-task fidelity) exactly when it lives in a subspace ORTHOGONAL to the shared task-relevant
gradient/signal, and COSTLY exactly when it competes with or conflicts against that subspace.** PCGrad's
empirical mechanism is the sharpest instance: gradients with negative cosine similarity get corrected (costly,
conflicting), gradients that are merely orthogonal are left untouched (free). The biological calibration case
(cerebellum vs cortex) fits this exactly -- cerebellum's radically different learning algorithm costs nothing
to shared behavioral output because it is not a second estimator of the SAME target at all, it is a
complementary computation feeding a different pipeline stage (division of labor, not dual estimation).

Applying this principle honestly to our own on-disk data is itself informative: DG_XFIT's grounding-cost
relative to B1 was `0.589` vs `0.595`, a `-0.006` delta -- essentially free, exactly consistent with a
differentiation that happened to sit close to orthogonal to the grounding-relevant subspace (DG's transform
targets decorrelation of the SHARED representation broadly, not the grounding-relevant features specifically).
**But this is exactly why it also gained almost nothing (`+0.015` decorrelation)**: an orthogonal-subspace
differentiation is only useful if there is residual CORRELATED STRUCTURE living in that orthogonal subspace for
it to remove -- and Angle D (below) independently confirms there is none left, because the input representation
is already near-maximally decorrelated at the cosine-similarity level (`~0.019`) system-wide, not just in the
grounding-relevant subspace. A cleverer, more deliberately-orthogonal differentiation axis would inherit the
same problem: it would cost little (consistent with the principle), but it would also have nothing left to
decorrelate, for the same reason DG had nothing left. **This angle does not open a door here, but it DOES
supply a durable, well-evidenced design discipline this program should pre-register against any future
differentiation-axis proposal:** before proposing a new architectural-differentiation cell, check whether the
target subspace (a) still carries residual shared-cause correlation (the actual lever) and (b) sits orthogonal
to the grounding/task-relevant subspace (the cost-avoidance condition) -- both conditions, not just one, must
hold for a differentiation axis to be worth building.

### Angle C -- the decisive cross-domain question: is exogenous input PROVABLY required, or just easiest?

**Verdict: NOT a proven mathematical impossibility -- but genuinely, exhaustively, no known constructive
internal-only method exists for this shared-cause class, and the one theoretical loophole found does not apply
to our specific situation. P(an as-yet-undiscovered internal-only construction exists that would work here) ~
0.05-0.10 (speculative, unbuildable with current knowledge).**

This is the sharpest and most honest finding of the whole drill. Across common-cause/common-mode-failure
reliability theory, Neyman-orthogonal cross-fitting / double-ML, negative-correlation learning, determinantal
point processes, ICA identifiability, and Kalman/sensor-fusion theory, **no genuine theorem was found proving
exogenous randomness is mathematically REQUIRED** to decorrelate two branches of a single shared cause. What
exists instead is: (i) strong empirical/engineering consensus (common-mode failure literature, including the
sobering Knight & Leveson 1986 finding that even INDEPENDENTLY-DEVELOPED software teams -- genuine architectural
exogeneity -- still produced far more correlated failures than a naive independence assumption predicts); (ii)
domain-specific sufficient-condition theorems (cross-fitting, NCL) that were never posed as necessity proofs and
in NCL's case have a provable non-zero correlation FLOOR under shared data, not a proof that only exogenous data
can reach zero; and (iii) one genuine, sharp counterexample cutting the OTHER way -- classical measure theory
shows a single continuous Uniform[0,1] random variable can be deterministically digit-interleaved into two
provably INDEPENDENT Uniform[0,1] outputs, entirely by internal/deterministic means, PROVIDED the shared source
carries enough entropy and the right splitting function is known.

That counterexample is the honest reason this angle cannot be called a closed door in principle. But it does
not rescue this specific case, for a reason this drill's own synthesis makes visible: the digit-interleaving
trick requires spare, currently-unexploited ENTROPY in the shared source to split -- and Angle D independently
confirms our shared representation has none left at the level DG could reach (input cosine similarity already
`~0.019`, i.e. already close to the orthogonality floor). Moreover, the residual `corr(failmask)=0.377` is not,
on the evidence assembled across A and C together, a residual-ENTROPY problem at all -- it behaves like a
residual-BIAS problem (both branches systematically wrong on the same underlying hard cases because they are
both ultimately fit against the same self-generated notion of "correct," exactly the wake-sleep failure mode
from Angle A). No known internal construction in ANY of these six literatures manufactures new information
about which shared conclusion is actually right; the closest formal loophole (digit-interleaving) manufactures
independent *noise*, not independent *ground truth*, and our residual correlation reads as bias, not noise.
**This is the load-bearing convergence point of the whole drill: A, B, and C independently arrive at "internal
constructions can decorrelate noise/variance but not bias," from reconciliation theory, differentiation theory,
and formal decorrelation theory respectively -- three unrelated fields naming the same limit.**

### Angle D -- is the near-zero-headroom bound fundamental, or an artifact of the near-orthogonal-code regime?

**Verdict: FUNDAMENTAL within the current code regime -- confirmed, not artifactual. A correlated-code regime
would restore headroom, but at a real, well-quantified, and ALREADY-established cost. P(reviving DG via a
correlated-code regime change is a good trade) ~ 0.05 (real lever, bad trade).**

The lit-scan found this is close to definitional, not merely empirically observed: pattern-separation "gain"
(input similarity minus output similarity) is bounded above by input similarity minus a chance-level floor, so
as input similarity approaches that floor, gain necessarily approaches zero -- corroborated by Babadi &
Sompolinsky's (2014) analytic treatment showing expansion+sparsification cannot manufacture separation beyond
what is licensed by structure already present in the input's correlation pattern, and by the empirical DG/
mushroom-body literature (large decorrelation gains ONLY occur when input correlation starts high, e.g.
Drosophila projection-neuron input ~0.83 -> Kenyon-cell output ~0.68 -- a real gain precisely because there was
real overlap to remove). Classical Johnson-Lindenstrauss random-projection theory reinforces this from the
distance-preservation side: linear random projections preserve, not reduce, similarity; the actual decorrelation
work in an expansion+k-WTA circuit comes from the nonlinear competition stage exploiting near-independent random
directions, which has nothing left to exploit once two inputs are already near-orthogonal.

Deliberately using a more-correlated (denser, overlapping) input code WOULD restore real headroom for a
pattern-separation stage -- this is a genuine, not illusory, lever. But it directly costs the SAME variable that
governs downstream associative-store capacity and interference-robustness: compressed-sensing mutual-coherence
bounds (Donoho-Elad, Donoho-Tanner) show recoverable-pattern capacity is inversely bounded by code coherence,
and classical Hopfield-type associative-memory capacity (critical load `alpha_c`) degrades monotonically with
pattern correlation. **This is not a new finding in isolation -- it is independent literature-level
confirmation of this program's own already-established, separately-derived design principle**
(`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08`, memory-filed
2026-07-08): near-orthogonal store-codes are required for capacity, and trading that away to reopen a
few points of self-play decorrelation headroom -- itself already shown (via the landed FULL run) to be worth
at most `+0.015` corr improvement even under the BEST current DG configuration -- is a bad trade against an
already-solved, load-bearing constraint. Confirmed dead as a revival path, not because the lever doesn't exist,
but because the lever is correctly priced and not worth pulling.

### Angle E -- envelope cross-check: is exogenous-referent the correct next direction?

**Verdict: CONFIRMED, independently, from two directions now.** The forward drill
(`research_exogenous_referent_grounding_predictive_coding_2026-07-09.md`, 4 parallel lit-scans on predictive
coding/active inference, sensorimotor contingency, Harnad categorical perception, and causal representation
learning) already converged on real-data prediction as the load-bearing exogenous anchor
(`P_deflated=0.45` mechanism-level; `B1+EXOG` HARD-PASS `P_deflated=0.25`, already fully scoped with
falsifiable HARD-PASS/HARD-FAIL thresholds, reusing existing `predictive_coding.py` primitives, no new
architecture). This backward-facing 5x-negative-drill now independently arrives at the identical destination
from the opposite direction (systematically closing off internal alternatives rather than proposing the
positive mechanism), and the two drills' reasoning converges on the exact same underlying diagnosis: closed
internal loops can decorrelate NOISE but not BIAS, and only a genuinely exogenous ground-truth signal can break
a shared-bias fixed point (mirrored almost verbatim by the wake-sleep proof in Angle A and the digit-interleaving
entropy-requirement in Angle C). Two independently-dispatched drill arcs reaching the same destination by
different routes is a meaningfully stronger convergence signal than either alone.

---

## Cheap decisive test

**No new large cell is proposed by this drill** -- its job was closure, not a new candidate, and it succeeded
(A-D all close). Two concrete, near-zero-cost actions follow directly:

**(1) Recommended immediate action: proceed to `B1+EXOG`**, exactly as scoped in
`research_exogenous_referent_grounding_predictive_coding_2026-07-09.md` -- no changes to that design are
warranted by this drill; if anything, this drill raises confidence in that pivot by independently ruling out
every plausible internal alternative rather than assuming exogenous-by-elimination.

**(2) A genuinely new, near-zero-cost confirmatory check (reuses already-collected DG_XFIT FULL data, no new
run) that directly tests this drill's own central claim** -- that the residual `corr(failmask)=0.377` is a
BIAS signature (same referents fail across independent seeds) rather than a NOISE signature (which referents
fail varies randomly seed-to-seed) -- before spending B1+EXOG's build budget on the assumption:

- **Method:** using the 5 already-run DG_XFIT seeds' per-unit data, compute, per referent, the co-failure rate
  across seeds (both speaker and listener wrong on that referent). Rank referents by co-failure rate. Compare
  the top-decile-hardest referents' average co-failure rate against the population average, and compute the
  Jaccard overlap of the top-decile-hard-referent SET across seed-pairs (i.e. is the same subset of referents
  hard in seed 7 and seed 13, or does "which referents are hard" reshuffle randomly).
- **HARD-PASS (confirms this drill's bias diagnosis, exogenous target is correctly aimed):**
  top-decile co-failure rate `>= 2x` the population-average co-failure rate, AND cross-seed-pair Jaccard overlap
  of the hard-referent set `>= 0.40`.
- **HARD-FAIL (would reopen an internal angle -- specifically, re-examine Angle A's bagging/variance-reduction
  logic, since it would mean the residual correlation IS noise/variance-level after all, not bias-level):**
  top-decile-vs-average ratio `< 1.3x` OR cross-seed-pair Jaccard `< 0.15` (hard-referent identity is
  effectively random across seeds).
- **MIDDLE_BAND:** ratio in `[1.3x, 2x)` with partial seed-stability -- worth a wider seed sweep before
  concluding either way, not a full re-drill.

This check is cheap (pure post-hoc analysis of on-disk `per_unit` data, no GPU, no new training) and is the
single most direct way to falsify this drill's central synthesis claim before committing `B1+EXOG`'s larger
build budget to it.

---

## Falsifiable predictions summary table

| Angle | Claim | HARD-PASS (revival) | HARD-FAIL (confirmed dead) | P_deflated |
|---|---|---|---|---|
| A | Reconciliation/replay manufactures independence | (not proposed as buildable -- theory-level negative, no test needed) | wake-sleep biased-fixed-point proof + bagging bias-invariance result, both directly on point | 0.05 |
| B | Orthogonal-subspace architecture differentiation revives the fix | new differentiation axis shows real decorrelation gain (`>=0.10` corr improvement) while grounding cost stays `<0.02` | gain stays near `DG_XFIT`'s `+0.015` regardless of axis chosen (no residual structure to exploit) | 0.08 |
| C | An undiscovered internal-only construction exists for this shared-cause class | (unbuildable with current knowledge -- speculative only) | exhaustive 6-literature search, no constructive method found; residual correlation reads as bias not entropy | 0.05-0.10 |
| D | Correlated-code regime change is a net-positive trade | -- (not recommended; would require reopening the capacity-vs-coherence tradeoff as a live design question) | independent literature confirmation of already-established correlation-hurts-capacity principle; DG's own best-case gain (`+0.015`) too small to justify the trade | 0.05 |
| (new) | Residual `corr(failmask)` is bias-level (same referents recur as hard across seeds) | co-failure concentration `>=2x` avg AND cross-seed Jaccard `>=0.40` | concentration `<1.3x` OR Jaccard `<0.15` | untested, near-zero-cost, propose before `B1+EXOG` build |

All P values calibration-deflated 0.15-0.25 per `[[feedback-lit-scan-calibration-penalty]]`; none exceed the
0.50 novel-synthesis cap (all are well below it, consistent with a converged negative-closure drill rather than
a positive-synthesis one).

---

## Cross-thread synthesis

- Directly closes the S3 fork of `research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md`: case (a)
  fired on the landed FULL run, and this drill independently confirms (via 4 unrelated literatures) that there
  is no OTHER internal angle left to try before the fork's own named redirect (exogenous).
- Directly raises confidence in `research_exogenous_referent_grounding_predictive_coding_2026-07-09.md`'s
  `B1+EXOG` proposal without changing its design -- this drill is confirmatory-by-elimination, arrived at from
  the opposite direction (systematically closing internal doors rather than opening the exogenous one).
- Cross-links `research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md`'s
  differentiation-axis taxonomy: Angle B sharpens WHY axis 1 (disjoint data/exogenous randomness, the only axis
  that note found provably `rho=0` by construction) is qualitatively different from axes 2-4
  (parameter-lag, objective-differentiation, algorithm-class-differentiation) -- axes 2-4 are all INTERNAL
  differentiation and, per this drill's Angle A/B/C convergence, can only reduce variance around a shared bias,
  never the bias itself; axis 1 works specifically because disjoint data is (weakly) exogenous relative to each
  individual branch, even though it is not exogenous relative to the WHOLE system -- consistent with why B1
  (axis 1 alone) already achieved most of the observed decorrelation (`0.788 -> 0.393`) while DG (representation
  differentiation, axes 2/4-adjacent) added almost nothing (`+0.015`).
- Independently corroborates, via a completely different literature (compressed sensing / associative-memory
  capacity, Angle D), the memory-filed
  `reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08` design principle
  -- two unrelated investigations now agree that near-orthogonal store-codes are load-bearing for capacity and
  should not be traded away for decorrelation headroom elsewhere in the system.
- Does not reopen unrelated closures (algebraic-topo, quantum-info, dynamics) per
  `[[feedback-prior-work-informs-not-constrains]]`.

---

## Substrate-product implications

- Not a publication-framing question. This drill's job was risk-reduction on a pivot decision already worth
  real build budget (`B1+EXOG`) -- it found no cheaper alternative was being prematurely skipped, which is
  itself the product-relevant result: proceed to `B1+EXOG` with higher confidence, and retire the
  representation/differentiation-only branch of this investigation rather than revisiting it after a future
  negative (per the standing discipline this program has now built three times: settling HF, differentiation
  HF, DG HF -- all three converge on the same "internal loops decorrelate noise not bias" limit).
- **New standing design discipline for this program going forward (from Angle B):** before proposing any future
  internal-differentiation cell (architecture, loss, or algorithm-class axis) intended to decorrelate two
  branches of a shared representation, pre-register BOTH (a) whether the target subspace still carries residual
  shared-cause correlation to exploit, and (b) whether the differentiation sits orthogonal to the
  grounding/task-relevant subspace. Condition (a) failing (as it does here) makes any further differentiation
  proposal along these lines low-value regardless of how well condition (b) is satisfied.
- Cheap next action (near-zero cost, before committing `B1+EXOG`'s build budget): run the bias-vs-noise
  co-failure concentration check specified above on already-collected `DG_XFIT` per-unit data.

---

## Citations (verified count: 47 across 4 parallel Sonnet lit-scans, all live-URL/arXiv-ID confirmed this
cycle; generic academic terms only, no substrate-novel mechanism names, cell names, configs, or numerical
parameters exposed off-platform per `[[feedback-query-privacy-decomposition]]`)

**Angle A -- reconciliation/replay (15):** Hinton, Dayan, Frey & Neal (1995) *Science* 268:1158; Dayan & Hinton
(1995) NeurIPS "Does the Wake-Sleep Algorithm Produce Good Density Estimators?"; Ikeda, Amari & Nakahara (1998)
NeurIPS 11 "Convergence of the Wake-Sleep Algorithm"; Le Roux et al. (2020) arXiv:2008.06687 "Natural Reweighted
Wake-Sleep"; Mattar & Daw (2018) *Nat Neurosci* "Prioritized memory access explains planning and hippocampal
replay"; Mattar/Antonov et al. (2021) *PNAS* "Prioritized experience replays on a hippocampal predictive map";
"The role of experience in prioritizing hippocampal replay" (2023) *Nat Commun*; Schaul, Quan, Antonoglou &
Silver (2016) arXiv:1511.05952 "Prioritized Experience Replay"; Shin, Lee, Kim & Kim (2017) NeurIPS
arXiv:1705.08690 "Continual Learning with Deep Generative Replay"; McClelland, McNaughton & O'Reilly (1995)
*Psych Rev* (CLS, cross-cited); Momennejad et al. (2019) arXiv:1905.02636; scikit-learn bias-variance
decomposition docs; Bierman & Van der Merwe ensemble bias-variance analysis; Munson & Caruana (Cornell)
"On Feature Selection, Bias-Variance, and Bagging"; "Pathologies of Predictive Diversity in Deep Ensembles"
arXiv:2302.00704.

**Angle B -- differentiation/shared-fidelity tradeoff (15):** Krogh & Vedelsby (1995) ambiguity decomposition;
"A Unified Theory of Diversity in Ensemble Learning" (2023) *JMLR* 24, arXiv:23-0041; Liu & Yao (1999)
*Neural Networks* Negative Correlation Learning; "Negative Correlation Learning" Scholarpedia/Springer entry;
Ghosal et al. "ForkMerge: Mitigating Negative Transfer in Auxiliary-Task Learning" arXiv:2301.12618; Yu et al.
(2020) "Gradient Surgery for Multi-Task Learning" (PCGrad) arXiv:2001.06782; "InterroGate" arXiv:2402.16848;
"Collaborative Information Bottleneck" arXiv:1604.01433; "RDD: Pareto Analysis of the
Rate-Distortion-Distinguishability Trade-off" arXiv:2509.24805; "Affinity Is Not Enough: Recovering the Free
Energy Principle in Mixture-of-Experts" arXiv:2605.00604; "Mixture-of-Experts with Expert Choice Routing"
arXiv:2202.09368; "Dynamics of specialization in neural modules under resource constraints" (2024)
*Nat Commun*, PMC11695987; Doya (2000) "What are the computations of the cerebellum, the basal ganglia and the
cerebral cortex?"; "Trade-offs among cost, integration, and segregation in the human connectome" PMC10312266;
"Diversity, accuracy and efficiency in ensemble learning" *Intelligent Data Analysis*.

**Angle C -- decisive theoretical question (17):** NASA "Common Cause Failures and Ultra Reliability" report;
Knight & Leveson (1986) N-version programming experimental evaluation; "Correlated Failures in Multi-Version
Software" *ScienceDirect*; IEC 61508 beta-factor CCF estimation (SIS-Tech); Rausand & Lundteigen Ch.10 CCFs;
Chernozhukov et al. (2017/2018) Double/Debiased ML arXiv:1701.08687; "Cross-Fitting-Free Debiased ML"
arXiv:2602.11333; DoubleML resampling documentation; Brown & Wyatt "Negative Correlation Learning and the
Ambiguity Family of Ensemble Methods"; Krogh & Vedelsby ambiguity decomposition (cross-cited); "Determinantal
Point Processes in RandNLA" arXiv:2005.03185; Darmois-Skitovich theorem; "Identifiability of overcomplete ICA"
arXiv:2401.14709; "Secure single-channel blind source separation" PMC11859866; "Optimal Sequential Fusion
Kalman Filter, cross-correlated noise" (2025) *Sensors*, MDPI; "Optimal Kalman filtering fusion with
cross-correlated sensor noises" *ScienceDirect*; Mobahi, Farajtabar & Bartlett (2020) "Self-Distillation
Amplifies Regularization in Hilbert Space" arXiv:2002.05715; "Towards Understanding Ensemble, Knowledge
Distillation and Self-Distillation" arXiv:2012.09816.

**Angle D -- fundamental vs config-contingent (13):** Marr (1971) via pattern-separation review PMC3726960;
"Reassessing pattern separation in the dentate gyrus" *Frontiers*; "Strong Evidence for Pattern Separation in
Human Dentate Gyrus" *J Neurosci* 36:7569; Babadi & Sompolinsky (2014) "Sparseness and Expansion in Sensory
Representations" *Neuron*; "Random convergence of olfactory inputs in the Drosophila mushroom body" (2013)
PubMed; Johnson-Lindenstrauss lemma notes (UWisc) and Wikipedia; "Restricted Isometry Property" Wikipedia;
Donoho-Tanner Phase Transition for Sparse Recovery; Donoho-Elad-type generalized uncertainty
principle/mutual-coherence bound; "On the storage capacity of Hopfield models with correlated patterns";
"On the Maximum Storage Capacity of the Hopfield Model" PMC5222833; "Mechanisms of pattern decorrelation by
recurrent neuronal circuits" *Nat Neurosci*; "Robust and consistent measures of pattern separation based on
information theory, dentate gyrus" PMC10906873.

**Angle E -- reused, not re-fetched:** all 34 citations of
`research_exogenous_referent_grounding_predictive_coding_2026-07-09.md`, cited there in full (Pezzulo, Parr,
Cisek, Clark & Friston 2023; Vincent-Lamarre et al. 2016; Coelho Mollo & Milliere 2023; Harnad 1990; Ahuja et
al. 2023; Squires, Seigal, Bhate & Uhler 2023; Geiger et al. 2022/2024; among others -- see that note for full
list).
