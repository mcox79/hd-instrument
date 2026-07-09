# Research (brain-first, cross-domain, gates master-map BUILD #2): the biology of internal-channel
# differentiation, and whether a SHARED-WEIGHT Speaker/Listener that differs only in information
# access gets genuinely uncorrelated failure modes -- or is a mirror that shares its blind spots

**Date:** 2026-07-09. **Trigger:** direct USER drill on the single sharpest open question of the whole
language-acquisition program, explicitly gating master-map BUILD #2 (internal self-play grounding loop).
**Framing correction applied mid-drill per USER:** the POSSIBILITY question is CLOSED -- it is proven that a
system can be its own independent partner; every brain does it, every day, via genuinely differentiated
internal subsystems (hippocampus vs. neocortex, cerebellum vs. cortex, the two hemispheres, forward-model vs.
sensory feedback). None of this drill argues about whether internal self-partnering CAN work. **The entire
drill targets the mechanism: what makes internal parts genuinely independent (independent FAILURE MODES, not
just independent architecture), and how much differentiation is the minimum sufficient condition** -- sharpened
into the decision-relevant design question: is a SHARED-WEIGHT Speaker/Listener that differs ONLY in
information access (a mirror sharing its blind spots -- the exact stacked-corrections failure signature,
`corr(failure_mask_A, failure_mask_B) ~ 0.49` on the landed `pfc_gate_waypoint_rescue_kb_grounded_check_v1`
cell) sufficient, or is genuine differentiation (weights / objective / representation / architecture /
initialization / training data) required, and how much of it. This is the natural next-drill named at the end
of `notes/research_social_interactive_language_acquisition_5x_2026-07-09.md` (same day, this session), and
directly extends `notes/research_brain_independent_channels_resolve_compounding_error_tension_2026-07-09.md`
and `notes/research_stacked_independent_corrections_push_compounding_frontier_2026-07-09.md`. 4 parallel Sonnet
lit-scan sub-agents were dispatched on angles not yet covered by those 3 prior same-day notes: (1) brain
internal-channel mechanisms (inner speech, split-brain, efference copy) reinterpreted below as differentiation
calibration data, not as a possibility test; (2) self-supervised-learning collapse-prevention theory
(SimSiam/BYOL/DINO) as the precise mathematical analog of "shared-weight, information-asymmetric" branches;
(3) emergent-communication literature on tied/shared-weight self-play vs. separately-parameterized agents; (4)
the formal core -- ensemble-diversity, Kalman/common-mode-failure, and self-distillation theory on when two
views of one estimator decorrelate. Generic math/science terms only, no substrate framing exposed off-platform
per `[[feedback-query-privacy-decomposition]]`.

---

## HEADLINE

**The brain's answer to "how much differentiation is enough" is unambiguous and quantifiable: its genuinely
independent internal channels are never two copies of one estimator differing only in input -- they are
different COMPUTATIONAL DEVICES (different neurotransmitter, different plasticity rule, often a different
learning-algorithm CLASS entirely). Machine-learning theory across three independent literatures then answers
the substrate's exact design question with unusual unanimity: a SHARED-WEIGHT mirror that differs only in
information access is NOT enough -- it reliably produces the shared-blind-spot failure signature (collapse in
SSL, no validated success case in emergent comm, provably non-zero failure correlation in formal ensemble
theory) unless one further, specific, and now well-characterized differentiation is added on top.**

**(S1) The biology -- what differentiates the brain's genuine internal channels, ranked by how much
difference is load-bearing (reusing and sharpening the Tier-1/Tier-2 taxonomy from
`research_brain_independent_channels_resolve_compounding_error_tension_2026-07-09.md`, now with today's added
mechanism depth):**

1. **Cerebellum vs. cortex -- maximal differentiation, cleanest biological instance.** Per Doya (2000) and the
   Marr/Ito/Albus lineage, the cerebellum runs a DIFFERENT anatomical loop, a DIFFERENT neurotransmitter/
   plasticity mechanism (complex-spike-driven LTD at climbing-fiber synapses vs. cortex's Hebbian/dopaminergic
   plasticity), and -- the single most load-bearing fact -- a DIFFERENT LEARNING-ALGORITHM CLASS (supervised
   delta-rule vs. cortex's more Hebbian/RL-like process). Differentiation here spans architecture, plasticity
   rule, AND objective simultaneously. This is why its error signal (climbing-fiber complex spikes, "graded
   error signals," Frontiers 2019/PMC6749063) can catch errors cortex's own forward pass cannot see.
2. **Basal ganglia arbitration -- different CRITERION, not just a different estimate.** Redgrave, Prescott &
   Gurney (1999): a separate structure applies dopaminergic reward-history as a VETO criterion over
   cortex-proposed plans -- differentiation here is in the OBJECTIVE/criterion the arbiter uses, not primarily
   in architecture. This is a distinct differentiation AXIS from cerebellum's (algorithm-class) worth keeping
   separate in the substrate design space.
3. **Complementary Learning Systems (hippocampus vs. neocortex) -- differentiated in architecture/learning-
   rule/timescale, but with a documented DIFFERENTIATION GAP.** Fast, sparse, one-shot Hebbian (hippocampus) vs.
   slow, distributed, interleaved (neocortex) is real, substantial differentiation, and it demonstrably rescues
   catastrophic forgetting neither system alone achieves. But both are downstream of the SAME upstream sensory
   encoding stream -- false-memory/source-monitoring literature (PNAS 2023, *Nat. Commun.* 2023) shows corrupted
   input contaminates the hippocampal trace itself BEFORE any cross-check could occur. **This is the biological
   demonstration that differentiation of the CHANNEL is necessary but not sufficient if the UPSTREAM feed is
   shared** -- directly confirming, from pure neuroscience, the formal ensemble-theory finding below (common-mode
   failure survives architectural differentiation if the data-generating source is not also split).
4. **Efference copy / corollary discharge -- anatomically real differentiation that still fails under shared
   upstream corruption (new finding this drill, sharpens point 3's principle with a mechanistic depth case).**
   Von Holst & Mittelstaedt's reafference principle and Sperry's corollary discharge describe a genuinely
   separate predictive circuit compared against real sensory consequence -- a real, evolved comparator. But the
   schizophrenia self-monitoring literature (Ford et al. 2012, *World Psychiatry*, N1/P2 ERP suppression
   deficits) shows this comparator's failure mode is not random: efference copy and reafference are BOTH
   miscalibrated by the same corrupted upstream signal, producing systematic self/non-self misattribution
   (auditory hallucination, passivity experiences) rather than graceful degradation. **The lesson: even
   anatomically distinct circuits inherit correlated failure if they are fed from a common corrupted source --
   differentiation of computation does not automatically buy differentiation of DATA.**
5. **Split-brain hemispheres -- the clearest NEGATIVE calibration case: what "no real channel" looks like, not
   what "insufficiently differentiated channel" looks like.** Volz & Gazzaniga (2017, *Brain*) show the
   left-hemisphere "interpreter," when it lacks the right hemisphere's information, does not register a gap or
   flag uncertainty -- it fabricates a plausible-but-false story. This is not a differentiation failure (the
   hemispheres ARE genuinely differentiated, connected by a real information channel, the corpus callosum) --
   it is a case where the SPECIFIC piece of information one side needs simply never crossed the channel at all.
   Useful as a calibration signature for the substrate's failure-mask screen: confident-fabrication-without-
   flagged-uncertainty is the "missing/severed channel" signature, distinguishable from the "channels present but
   correlated" signature (points 3-4) by whether confidence tracks channel-disagreement rate at all.
6. **Inner speech / private speech (Vygotsky) -- the weakest claimant to genuine internal independence, now
   correctly read as calibration, not as a possibility test.** Alderson-Day & Fernyhough (2015) and the
   developmental private-speech literature (Winsler et al.) show inner speech is the internalization of an
   originally EXTERNAL dialogue -- it organizes/scaffolds already-partially-correct behavior rather than
   supplying a differentiated second estimator. Not evidence against internal self-partnering in general
   (settled, per the cerebellum/CLS/basal-ganglia cases above) -- evidence that THIS SPECIFIC mechanism is low
   on the differentiation spectrum and correspondingly weak as an error-catcher.

**Ranking of differentiation axes found in the biology, cheapest-to-costliest to replicate:** (a) split the
upstream DATA/input source (CLS's missing ingredient, cheapest to add); (b) split the OBJECTIVE/criterion
(basal ganglia's axis); (c) split the LEARNING RULE/algorithm class (cerebellum's axis, most expensive,
strongest track record).

**(S2) The ML/formal answer to "is shared-weight-info-access-only differentiation enough" -- convergent NO,
with the specific fix identified in each of 3 independent literatures:**

- **Self-supervised learning (closest engineering analog, hardest ablation evidence).** SimSiam's own ablations
  (Chen & He 2021) show removing stop-gradient collapses to chance accuracy even with the predictor MLP
  intact; Zhang et al. (ICLR 2022) show a SYMMETRIC predictor applied identically to both branches still
  collapses regardless of input/view differences. Wang et al. (CVPR 2022) name the general principle:
  "asymmetry" (in weights, gradients, or architecture) is the operative ingredient, not the input-view
  difference. The counterexample (Barlow Twins/VICReg: fully tied weights, live gradients, no stop-gradient) does
  NOT rescue information-asymmetry-alone -- it substitutes a different engineered asymmetry (batch-level
  anti-collapse loss term) for the parameter/gradient asymmetry it lacks.
- **Emergent communication.** Galke, Ram & Raviv (EmeCom @ ICLR 2022) state directly that essentially all
  published referential-game work (Lazaridou, Havrylov-Titov, Kottur, Chaabouni-style) uses separately-
  parameterized Speaker/Listener networks; a literally shared-weight, role-symmetric single estimator has no
  validated success case in this literature -- it is flagged as an open gap, not a demonstrated result. Lowe et
  al. (2020) directly test something close to pure self-play and find it underperforms without population
  diversity or supervised pretraining. The strongest DIRECT necessity ablation (Rita et al. 2022): population
  heterogeneity + sender/receiver TRAINING-SPEED asymmetry is what flips homogeneous-population's negative
  size-compositionality correlation (r ~ -0.5) positive -- differentiation of TRAINING DYNAMICS, not information
  access, is the causal lever isolated by ablation.
- **Formal ensemble/Kalman/self-distillation theory (the precise mathematical statement).** Failure-mode
  correlation ρ between two branches of a shared estimator shrinks with the DEGREE of pipeline differentiation
  (seed < architecture < data-subset, Fort/Hu/Lakshminarayanan 2019; Unified Theory of Diversity, JMLR 2023,
  r^2~0.99 diversity-performance correlation) but architectural/informational variation alone never provably
  reaches ρ=0 -- common-mode-failure theory (TMR/avionics literature) treats this as a KNOWN, structurally-
  unfixable-by-replication problem. Self-distillation (Mobahi, Farajtabar & Bartlett 2020) is the clean, PROVABLE
  extreme case: ρ->1 (zero new information enters the loop), and any apparent gain is a regularization artifact
  (Hilbert-space kernel sparsification), not error-decorrelation -- the exact "mirror sharing its blind spots"
  case named in this drill's retargeted framing, now with a rigorous mathematical account of why it happens. The
  ONE construction proven to give ρ=0 by CONSTRUCTION (not just empirically small) is Neyman-orthogonal
  cross-fitting (disjoint data folds, Chernozhukov et al. 2017): independence requires a disjoint or
  provably-orthogonal source of RANDOMNESS, not merely a different seed/architecture/loss on the same upstream
  data.

**(S3) The minimal-differentiation condition, stated as precisely as both literatures allow:**

**Two views/branches of a shared estimator get genuinely uncorrelated failure modes if AND ONLY IF at least
one of the following holds, ranked from formally-proven to empirically-strong to biologically-necessary-but-
expensive:**
1. **Disjoint data/randomness split (proven ρ=0 by construction)** -- the substrate's DIRECT analog of CLS's
   missing ingredient (point 3 above) and the formal literature's cross-fitting result. Cheapest to build.
2. **Parameter/gradient-flow asymmetry (lag, stop-gradient, or differential update speed)** -- the SSL
   literature's and Rita et al.'s empirically best-validated fix. Moderate build cost.
3. **Differentiated objective/criterion** -- the basal ganglia's axis; different LOSS FUNCTION or SUCCESS
   CRITERION for the two roles, not just different information. Moderate-to-high cost, no direct ML ablation
   found isolating this axis alone in an emergent-comm setting (a gap, flagged below).
4. **Differentiated learning-algorithm class / architecture family entirely** -- the cerebellum's axis, the
   strongest biological track record, the highest build cost (effectively building two structurally different
   estimators, not variations on one).

**Information-access asymmetry ALONE (the crux's literally-specified mirror design), with none of 1-4 present,
satisfies NONE of these conditions and is therefore predicted, with high convergent confidence, to reproduce
the stacked-corrections `corr(failure_mask) ~ 0.49` shared-blind-spot signature rather than genuine
independence.**

---

## Cheap decisive test (S2 continued: the concrete substrate design + measurable screen)

**Build/compare FOUR variants of the Speaker/Listener cell, all reusing the existing relational encoder + the
already-proposed externally-fed numeric-attribute seed/referent set (no new representational machinery):**

- **Arm B0 (naive mirror, as literally specified in the original crux):** fully shared/tied weights, live
  (non-stopped) gradients on both Speaker and Listener passes, differing ONLY in information access
  (full-neighborhood view vs. bandwidth-capped message + distractors). Satisfies NONE of the 4 minimal-
  differentiation conditions. **Predicted to reproduce the stacked-corrections shared-blind-spot signature.**
- **Arm B1 (differentiation axis 2, parameter-lag, BYOL/DINO analog):** Listener's weights are an EMA/
  stop-gradient-lagged copy of Speaker's, not live-tied.
- **Arm B2 (differentiation axis 1, disjoint-data/cross-fit analog):** Speaker and Listener trained/evaluated
  on disjoint folds of the referent set -- the one construction with a PROVEN ρ=0 guarantee.
- **Arm B3 (differentiation axis 2+biological-axis-1 combined, population/speed-asymmetry, Rita et al. 2022
  analog):** a small population of differently-initialized Listener variants; Speaker updated at a different
  training speed than Listener.

**The measurable screen (reusing the stacked-corrections screen verbatim, now with the biological/formal
grounding for WHY it is the right screen):**
```
corr(failure_mask_speaker, failure_mask_listener)   # per-referent binary correct/incorrect masks
```
computed on all four arms, alongside novel-referent generalization accuracy and cross-role representational
alignment (the social/interactive note's original metric). **This screen must run and clear BEFORE any
accuracy/alignment result from a self-play cell is trusted as genuine grounding** -- per finding (S2)'s
self-distillation warning, an un-screened accuracy gain can be a regularization artifact (ρ->1 case) dressed as
grounding.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE_BAND)

**HARD-PASS (minimal-differentiation condition confirmed on substrate data -- the biology's and ML theory's
convergent prediction transfers):**
- B0 shows `corr(failure_mask_speaker, failure_mask_listener) >= 0.40` (reproduces the mirror/shared-blind-spot
  signature, matching the stacked-corrections `~0.49` precedent) **AND**
- at least one of B1/B2/B3 shows `corr(failure_mask_speaker, failure_mask_listener) <= 0.20` **AND**
- that same arm beats B0 on novel-referent generalization accuracy by a paired-significant margin
  (`sign_p < 0.05`).
=> Confirms: differentiation (not information access alone) is the operative ingredient on this substrate too,
exactly as biology and ML theory predict. Build B2 (cross-fit) first -- cheapest, only PROVEN-by-construction
guarantee -- then layer B1/B3 if B2's communicative convergence proves too weak (see residual question below).

**HARD-FAIL, variant (a) -- surprising positive, worth independent replication before trusting:**
- B0 (naive mirror) already shows `corr(failure_mask_speaker, failure_mask_listener) <= 0.20` on its own.
=> Would mean this substrate's relational-encoder geometry escapes the SSL/emergent-comm/formal-theory
pattern -- an interesting anomaly, not to be generalized back into the literature without a second independent
cell confirming it.

**HARD-FAIL, variant (b) -- the load-bearing negative to state plainly if the data says so:**
- NONE of B1/B2/B3 achieves `corr(failure_mask_speaker, failure_mask_listener) <= 0.35`.
=> Would mean even PROVEN differentiation axes (disjoint data, parameter lag, population/speed asymmetry) fail
to decorrelate on this substrate's specific architecture -- pointing at a deeper common-mode cause (e.g. the
relational encoder itself, upstream of both roles, per the CLS/efference-copy lesson that channel
differentiation doesn't help if the FEED is shared). Actionable fallback: differentiate the UPSTREAM
representation itself (axis 1, applied one level deeper than the referent-set data split), or fall back to the
cerebellum-style axis-4 fix (a genuinely different architecture/algorithm-class Listener, highest cost, but the
biology's strongest track record).

**MIDDLE_BAND:** one or two of B1/B2/B3 show partial decorrelation (`0.20 < corr <= 0.40`) with a modest
generalization gain -- sweep differentiation STRENGTH (EMA decay rate for B1, fold count for B2, population
size/speed-ratio for B3) before concluding.

**P_deflated (capped 0.50 for novel-synthesis claims per calibration discipline):**
- P(the minimal-differentiation condition itself -- info-access-only symmetry is insufficient, at least one of
  the 4 named differentiation axes is required -- across biology, SSL, emergent-comm, and formal theory): raw
  ~0.85 (four independently-drilled literatures, several with direct controlled ablations: SimSiam's
  stop-gradient/predictor ablation, Zhang et al.'s symmetric-predictor-still-collapses result, Neyman-
  orthogonality's formal proof, Rita et al.'s population/speed-asymmetry necessity ablation) -> **P_deflated
  ~0.60-0.65** (kept below near-certain because each domain's underlying reason for the pattern differs --
  optimization-landscape argument in SSL, randomness-source argument in the formal theory, anatomical-substrate
  argument in biology -- "these are the same underlying law" is this drill's own unifying claim).
- P(novel-synthesis: B2 cross-fit specifically transfers cleanly to the substrate's relational encoder AND
  preserves enough shared structure for Speaker/Listener to still converge on a usable communicative code,
  despite training on disjoint referent folds): raw ~0.35 (genuinely uncertain -- flagged explicitly as the
  sharpest residual question below, since cross-fitting's ρ=0 guarantee was proven for a different problem
  shape, nuisance-parameter debiasing, not two-party communicative convergence) -> **P_deflated ~0.25-0.30**,
  held under the mandatory 0.50 novel-synthesis cap.
- P(HARD-FAIL variant (b) -- even proven differentiation axes fail to decorrelate on this substrate, common
  cause lives upstream of the split): raw ~0.20 -> **P_deflated ~0.12-0.15**.

---

## Cross-thread synthesis

- **Directly answers the "sharpest open question" left by
  `research_social_interactive_language_acquisition_5x_2026-07-09.md`**, now correctly scoped per the USER's
  mid-drill correction: not "is internal self-play possible" (closed, yes) but "how much differentiation does
  it need." Answer: a great deal more than information-access asymmetry alone, quantified via 4 concrete,
  buildable axes.
- **Directly extends and sharpens the biological Tier-1/Tier-2 taxonomy from
  `research_brain_independent_channels_resolve_compounding_error_tension_2026-07-09.md`**: that note ranked
  cerebellum/basal-ganglia Tier-1 and CLS/predictive-coding Tier-2 based on architectural distinctness; this
  drill adds the missing DIFFERENTIATION-AXIS vocabulary (data-split / objective-split / algorithm-class-split)
  that explains WHY cerebellum is stronger than CLS (spans all 3 axes vs. CLS's 2, still missing axis 1) and
  gives the substrate a concrete ranked menu instead of a qualitative tier label.
- **Directly extends and imports the stacked-corrections screen**
  (`research_stacked_independent_corrections_push_compounding_frontier_2026-07-09.md`, `kb_fresh_rate`
  failure-mask correlation, empirically observed `~0.49` on the KB-gate cell): this drill supplies the formal
  grounding (Neyman-orthogonality / common-mode-failure theory) for why that exact screen, not the naive
  `corr(signal, M_error)` screen, is the right one, and predicts the SAME signature will appear in the naive
  Speaker/Listener mirror (B0) for the same underlying reason.
- **Refines the social/interactive drill's bottleneck claim** (it read Chaabouni et al. as "bottleneck, not
  population size, drives compositionality"): today's emergent-comm scan finds Chaabouni et al. (ACL 2020)
  actually show bottleneck capacity beyond a threshold does not harm generalization; the strongest DIRECT
  necessity ablation is population heterogeneity + training-speed asymmetry (Rita et al. 2022) -- recommend B3
  get equal build-priority with B2, not treat bottleneck-alone as sufficient.
- Does not reopen unrelated closures (algebraic-topo, quantum-info, dynamics, option-critic/BlocksWorld) per
  `[[feedback-prior-work-informs-not-constrains]]`.

---

## Substrate-product implications

The self-contained-substrate mandate (no external LLM/model) is fully compatible with every differentiation
axis found, because all four (data-split, objective-split, parameter-lag, algorithm-class-split) are internal
structural/training-loop changes -- none requires an external AI model or a live human partner.

**Three buildable designs, ranked by cost and by strength of proof:**

1. **Cross-fit Speaker/Listener (B2, differentiation axis 1) -- cheapest, ONLY proven-by-construction
   guarantee, build FIRST.** Split the existing referent seed set into disjoint folds; train Speaker on fold 1,
   Listener on fold 2 (or k-fold rotate). Data-split change only, no new training dynamics.
2. **Parameter-lag Listener (B1, differentiation axis 2, BYOL/DINO analog) -- moderate cost, strongest
   empirical track record.** EMA-decayed Listener weights + stop-gradient. Directly reuses SSL's most-validated
   anti-collapse mechanism.
3. **Population + speed-asymmetry (B3, axes 1+2 combined, Rita et al. 2022 analog) -- highest cost, addresses
   the refined bottleneck understanding directly.** 2-4 differently-initialized Listener variants, Speaker at a
   different update cadence.

**Standing discipline, generalizing beyond this one cell:** per the self-distillation/mirror warning, no
self-play or channel-stacking cell should be trusted on accuracy/alignment metrics alone -- the
`corr(failure_mask_A, failure_mask_B)` screen (empirically validated on the KB-gate cell, now grounded in both
biology's differentiation-axis taxonomy and Neyman-orthogonality theory) must run and clear first.

**If HARD-FAIL variant (b) occurs:** per the CLS/efference-copy lesson (differentiation of the channel is
necessary but not sufficient if the upstream feed is shared), the fallback is to differentiate the UPSTREAM
representation, not to abandon self-play or reach for an external partner -- the biological precedent
(cerebellum) shows the fix that always works is a genuinely different computational device, which stays fully
inside the self-contained-substrate mandate.

---

## Sharpest residual open question

**Does the proven ρ=0 guarantee of disjoint-data cross-fitting (B2) survive contact with a COMMUNICATIVE
convergence requirement?** Neyman-orthogonal cross-fitting was proven for nuisance-parameter debiasing (each
fold's estimate is scored, never required to "agree" with the other fold's estimate on a shared code). A
Speaker and Listener trained on strictly disjoint referents have, by construction, never seen the same training
instance -- it is unverified whether they can still converge on a SHARED communicative code at all, or whether
the formal independence guarantee and referential-game convergence are in direct tension (maximal
differentiation might buy zero failure-correlation at the cost of zero successful communication). No paper
found in any of the 4 lit-scans tests disjoint-DATA (as opposed to disjoint random seeds, which is standard)
per-agent in a communication-game setting. Natural next drill: search specifically for multi-agent-RL /
referential-game work with disjoint per-agent training data, to locate where on the differentiation-vs-
convergence tradeoff curve the substrate should sit.

---

## Citations (verified count: 47 across 4 parallel Sonnet lit-scans, all live-URL or arXiv-ID confirmed;
generic neuroscience/ML/statistics terms only, no substrate-novel mechanism names, cell names, configs, or
numerical parameters exposed off-platform per `[[feedback-query-privacy-decomposition]]`)

**Brain internal-mechanism scan (7):** Alderson-Day & Fernyhough (2015) Psychol Bull; Vygotsky (1934/1962)
*Thought and Language*; Winsler et al., private-speech/task-performance (ScienceDirect); Volz & Gazzaniga
(2017) *Brain* 140(7):2051; corpus-callosum interhemispheric-transfer review (Springer, Neuropsychol Rev);
Wessel (2012) *Front Hum Neurosci* (ERN review); Ford et al. (2012) *World Psychiatry* (corollary-discharge
ERP deficits in schizophrenia). Plus, carried forward from
`research_brain_independent_channels_resolve_compounding_error_tension_2026-07-09.md` for the cerebellum/basal-
ganglia/CLS differentiation-axis analysis (not re-fetched this session, cited by reference): Wolpert, Miall &
Kawato (1998); Doya (2000); Redgrave, Prescott & Gurney (1999); McClelland, McNaughton & O'Reilly (1995);
Kumaran, Hassabis & McClelland (2016).

**SSL collapse-prevention scan (14):** Chen & He (2021) CVPR, SimSiam, arXiv:2011.10566; Grill et al. (2020)
NeurIPS, BYOL, arXiv:2006.07733; Richemond et al., "BYOL works even without batch statistics,"
arXiv:2010.10241; Caron et al. (2021) ICCV, DINO, arXiv:2104.14294; Tian, Chen & Ganguli (2021) ICML,
arXiv:2102.06810; Zhang et al. (2022) ICLR, arXiv:2203.16262; Tao et al. (2022) ECCV, "Understanding Collapse
in Non-Contrastive Siamese Representation Learning"; Wang et al. (2022) CVPR, arXiv:2204.00613; Zbontar et al.
(2021) ICML, Barlow Twins, arXiv:2103.03230; Bardes, Ponce & LeCun (2022) ICLR, VICReg, arXiv:2105.04906; Jha
et al., arXiv:2402.14957; Bowman et al. (2016) CoNLL (KL annealing); Kingma et al. (2016) NeurIPS (free bits);
Fu et al. (2019) NAACL (cyclical annealing); He et al. (2019) ICLR (lagging inference/posterior collapse).

**Emergent-communication scan (12):** Kottur, Moura, Lee & Batra (2017) EMNLP Best Short Paper; Batali (1998),
*Approaches to the Evolution of Language*; Choi, Lazaridou & de Freitas (2018) ICLR; Lowe et al. (2020),
arXiv:2002.01093; Galke, Ram & Raviv (2022) EmeCom@ICLR, arXiv:2204.10590; Chaabouni et al. (2020) ACL,
arXiv:2004.09124; Chaabouni et al. (2022) ICLR, "Emergent Communication at Scale"; Rita et al. (2022),
arXiv:2204.12982; Cogswell et al. (2019), arXiv:1904.09067; Li & Bowling (2019), arXiv:1906.02403; Ren et al.
(2020) ICLR, arXiv:2002.01365; Galke & Raviv (2024), *Language Development Research* 5(1), arXiv:2403.14427.

**Formal ensemble/Kalman/self-distillation scan (14):** Krogh & Vedelsby (1995) ambiguity decomposition;
generalized ambiguity decomposition, JMLR 24 (2023), arxiv/jmlr 20-843; Liu & Yao (1999) *Neural Networks*,
Negative Correlation Learning; Scholarpedia, "Negatively Correlated Ensemble Learning"; Fort, Hu &
Lakshminarayanan (2019), arXiv:1912.02757; "A Unified Theory of Diversity in Ensemble Learning," JMLR 24
(2023), arXiv/jmlr 23-0041; Kalman/sensor-fusion observability review, PMC9502392; NSF-SHREC common-cause-
failure TMR modeling report; TMR survey, arXiv:2603.14411 (note: forward-dated arXiv ID as returned by
search); fault-tolerant avionics survey (UNC); Mobahi, Farajtabar & Bartlett (2020) NeurIPS, arXiv:2002.05715;
Furlanello et al. (2018), Born-Again Networks, arXiv:1805.04770; Chernozhukov et al. (2017/2018), Double/
Debiased ML, arXiv:1701.08687; DML introduction survey, arXiv:2504.08324.

All 4 sub-agents used generic terms only ("inner speech private speech Vygotsky development," "split brain
interpreter confabulation corpus callosum," "efference copy corollary discharge schizophrenia self-
monitoring," "SimSiam BYOL DINO representation collapse siamese network," "posterior collapse VAE KL
annealing," "emergent communication referential game weight sharing self-play," "population heterogeneity
compositional language emergence," "ensemble diversity ambiguity decomposition negative correlation learning,"
"Kalman filter sensor fusion common cause failure redundancy," "self-distillation Born-Again Networks
regularization," "Neyman orthogonal cross-fitting double machine learning") -- no substrate-novel mechanism
names, cell names, configs, or numerical parameters were exposed off-platform, per
`[[feedback-query-privacy-decomposition]]`.
