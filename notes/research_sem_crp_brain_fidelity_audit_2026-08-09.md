# Research: adversarial brain-fidelity audit — sticky-CRP event-clustering vs DG/CA3 match-or-spawn

**Filed-by:** research sub-agent, 2026-08-09. **Trigger:** director-issued adversarial audit question —
is "sticky Chinese Restaurant Process (CRP) latent-cause clustering" (proposed today, in
`notes/exp_dev_handoff_research_brain_script_acquisition_consolidation_2026-08-09.md` anchor 3, as the
mechanism for `hdlab/grounding_acquisition_loop.py`'s Library reuse-existing-schema-vs-spawn-new decision)
the brain's actual event-clustering shape, or a convenient nonparametric-Bayes prior mislabeled as
brain-derived? 4 parallel Sonnet lit-scan lanes dispatched; all 4 returned high-density, largely
primary-source-verified findings (multiple full-text PDF fetches with direct quotes, not just abstracts).

## HEADLINE

**Sticky-CRP-as-event-clustering is a DEVIATION when treated as a brain mechanism, but a legitimately
disclosed COMPUTATIONAL-LEVEL (Marr level 1) rational model of the event-segmentation problem — its own
authors never claim otherwise, and no one (including Gershman's own follow-up work) has validated it as, or
even proposed a concrete neural implementation for, the brain's actual algorithm.** Separately: DG/CA3
pattern-separation/completion IS a materially more brain-foundational SHAPE for the match-or-spawn decision
— decades of causally-tested (NMDAR-KO), continuously-graded (sigmoidal similarity-response), competitive-
dynamics evidence — but no paper bridges the two frameworks, so the fix is a genuine novel-synthesis
proposal, not literature-supplied.

## 1. Is SEM's sticky-CRP presented as mechanistic or computational-level?

**COMPUTATIONAL-LEVEL, explicitly and repeatedly, by the authors' own words.** Franklin, Norman, Ranganath,
Zacks & Gershman (2020), "Structured Event Memory: A neuro-symbolic model of event cognition," *Psychological
Review* 127(3):327-361. VERIFIED via full-text PDF fetch + extraction (gershmanlab.com host), direct quotes:

- "we then lay out a general computational-level analysis, framing event cognition in terms of a common
  probabilistic generative model of events" (p.327, abstract-adjacent).
- "Our model is a computational-level analysis of event segmentation and memory that frames these tasks in
  terms of probabilistic reasoning" (p.331).
- On the scene-representation learning mechanism specifically: "we are agnostic to the specific details of
  how it is learned in the brain" (p.332).
- Discussion, explicit level-separation: "A related issue is how the computational-level model relates to a
  circuit-level implementation... our neural predictions are an open empirical question for future research"
  (p.356).

This is a self-aware, disciplined Marr-level disclosure — SEM's authors never claim the sticky-CRP is a
neural algorithm. Brain-region mappings (posteromedial network, hippocampus, vmPFC) are offered as untested
hypotheses, not fitted claims.

**Independent replication of the sticky-CRP mechanism specifically: NOT FOUND.** Semantic Scholar citation
sweep (~100 citing papers) plus 2 targeted fetches. No paper by authors fully outside
Franklin/Norman/Ranganath/Zacks/Gershman reuses or extends the sticky-CRP clustering step inside a new model.
Two adjacent, informative data points:
- Basgol, Ayhan & Ugur (2022/2023, *Cognitive Systems Research*, arXiv:2210.05710) — outside authors who
  benchmark against SEM directly ("the only model validated by ground-truth [human segmentation] data") and
  report a *non*-sticky-CRP self-supervised NN scoring higher on point-biserial correlation with human
  segmentation — i.e., a competing, better-performing alternative, not a sticky-CRP extension.
- Nguyen (2024, arXiv:2409.18992, solo-authored review of mechanistic event-comprehension models) argues the
  sticky-CRP is a fixed, *unlearned* hyperparameterized prior and explicitly proposes replacing it: "learning
  lateral dynamics across event types can be implemented by a learnable Markov transition matrix. This
  approach might provide a better prior than the sticky Chinese Restaurant Process." This is an ML-side
  critique (learnability), independent of and convergent with the brain-fidelity critique below.

**Empirical support base: purely BEHAVIORAL, zero neural data fit.** VERIFIED (full-text extraction).
Validated only against human video-segmentation judgments (Zacks et al. 2001/2006; point-biserial
correlation model r=0.168 vs human r=0.29 — a real residual gap even against noisy human agreement),
doorway/event-boundary recall paradigms (Radvansky & Copeland 2006; Pettijohn & Radvansky 2016), and
script-based false-recall (Bower, Black & Turner 1979). fMRI/hippocampus/vmPFC data appear only as post-hoc
qualitative discussion, explicitly labeled "an open empirical question for future research" — never fit or
tested against.

## 2. Latent-cause inference (Gershman, Blei & Niv 2010 and lineage): rational model or brain algorithm?

**Explicitly rational/Marr-level-1, arguably the most disciplined level-separation in this literature.**
Gershman, Blei & Niv (2010), "Context, Learning, and Extinction," *Psychological Review* 117:197-209.
VERIFIED (primary text read in full). The CRP mixture is presented as the *generative model* (the animal's
prior over environment/cause structure) — separate from the *inference algorithm* (a particle filter), about
which the authors explicitly decline to make an implementational claim: "it would be premature to commit to
the particle filter as an algorithmic-level description of the conditioning data that we model, because...
this algorithm will make behavioral predictions essentially identical to those made by any other algorithm
that adequately approximates the posterior." The hippocampal mechanism they float (pattern
separation/CA3 attractors) is offered only as a speculative sketch for how the algorithm *might* be realized
— not asserted as established.

**Neural evidence for latent-cause/latent-state inference exists — but discriminates NOTHING CRP-specific.**
Three flagship neural results were checked directly:
- Wilson, Takahashi, Schoenbaum & Niv (2014, *Neuron*) — OFC as a "cognitive map of task space." VERIFIED
  full text: uses small, hand-specified, experimenter-defined state sets (2-4 states), NOT CRP/DP-inferred.
  Tests generic hidden-state coding via lesion behavior + VTA dopamine RPE. No clustering, stickiness, or
  power-law growth prediction tested. Rating: MODERATE for generic latent-state coding, NONE for
  CRP-specificity.
- Schuck, Cai, Wilson & Niv (2016, *Neuron*) — same pattern: 16 deterministic, rule-defined states, not
  CRP-inferred. MODERATE/generic only.
- Starkweather, Babayan, Uchida & Gershman (2017, *Nat Neurosci*) — dopamine RPE under belief-state
  inference. Uses a standard HMM, not CRP/DP. Confirms generic belief-state updating; does not discriminate
  sticky-CRP from HMM/particle-filter/non-sticky-clustering alternatives.

No neural study anywhere in this lane actually deploys CRP/DP machinery — every flagship neural test uses
simpler finite-state or HMM formalisms. The CRP/DP layer is confined to Pavlovian *behavioral*-modeling
papers. No explicit authorial statement of "we chose CRP for mathematical convenience (exchangeability,
power-law growth) over biological fidelity" was found as a standalone quote, but the Marr-level disclosure
above functions as an implicit version of exactly that claim.

## 3. Algorithmic/implementational-level neural mechanism for familiar-reuse vs novel-spawn

**DG/CA3 pattern separation/completion is a well-established, CAUSALLY-TESTED, decades-deep circuit account
of exactly this functional decision — structurally very different in shape from a discrete CRP cluster
draw.**

- **DG pattern separation**: Leutgeb, Leutgeb, Moser & Moser (2007, *Science* 315:961-966), VERIFIED fetch.
  In parametrically-morphed environments, DG granule cells decorrelate overlapping inputs via a graded,
  continuous *rate*-code change (which cells fire, how much) — orthogonalization happens smoothly, before any
  discrete remap. CA3, downstream, only recruits a substantially different population once the change crosses
  a threshold ("global remapping" — more categorical, but still emergent from continuous underlying dynamics,
  not an explicit hyperparameter draw).
- **CA3 pattern completion**: Nakazawa et al. (2002, *Science* 297:211-218), VERIFIED fetch. CA3-NMDAR-knockout
  mice retain normal spatial reference memory but are SELECTIVELY impaired retrieving a stored map from a
  partial/degraded cue — direct causal (not just correlational) evidence that CA3 recurrent-collateral
  (autoassociative) plasticity implements "reuse existing trace from a partial match." Builds on Marr's (1971)
  original attractor-network theoretical proposal.
- **CA3 output is a continuous sigmoidal function of input similarity** (Knierim/Neunuebel review, VERIFIED
  fetch): small Δinput -> smaller Δoutput (completion dominates); large Δinput -> nonlinear flip to
  Δoutput > Δinput (separation dominates). This is graded competitive dynamics between two coupled
  subsystems (DG sparsity/inhibitory tone biasing separation; CA3 recurrent strength biasing completion) —
  NOT a discrete urn-scheme draw governed by one scalar concentration parameter.
- **Novelty-detection / gating**: Lisman & Grace (2005, *Neuron* 46:703-713), VERIFIED fetch — the
  hippocampal-VTA loop is a downstream *consequence*-gating signal (novelty -> VTA dopamine -> boosts LTP),
  sitting AFTER whatever computes the match/mismatch, not the comparator itself. Vinogradova (2001,
  *Hippocampus* 11:578-598), SECONDARY (not fetched this cycle) — proposes CA1 as the actual
  match-to-stored-context comparator whose mismatch output plausibly feeds the Lisman-Grace loop.

**No paper directly compares CRP-style discrete clustering against DG/CA3 as competing candidate mechanisms
for the same decision** — this specific comparison is a genuine gap in the field, not evidence either way.
The structural facts assembled above support a novel-synthesis (not literature-sourced) judgment: DG/CA3 is a
better-motivated brain SHAPE, because (a) it is causally tested via lesion/knockout, not just fit to
behavioral judgments; (b) its separation-vs-completion arbitration is continuous/similarity-graded, matching
the intuitive shape of "how similar is this new event to stored ones" better than a discrete draw; and (c)
recency effects in the hippocampal literature (the functional analog of CRP's "stickiness" term) are
conventionally attributed to slowly-drifting temporal-context representations (temporal-context-model
lineage), not an explicit recency-weighted prior over which cluster to reuse — flagged here as background
domain knowledge, NOT verified by a sub-agent fetch this cycle, so treat with appropriately lower confidence
than the fetch-verified claims above.

## 4. Bridge from CRP concentration/stickiness to a concrete neural quantity

**GENERAL-ANALOGY-ONLY, bordering on NONE FOUND at the literal parameter level — including in Gershman's own
flagship papers.** This is the most decisive negative finding of the drill:

- Hasselmo (2006, *Curr Opin Neurobiol* 16:710-715), VERIFIED (abstract + secondary corroboration): high ACh
  suppresses recurrent/feedback (pattern-completion) dynamics and biases toward encoding new afferent-driven
  representations; low ACh permits retrieval/consolidation. Directionally analogous to "high ACh -> spawn,
  low ACh -> reuse" — but this mapping is the sub-agent's own inference; Hasselmo's paper predates CRP-in-
  cogsci usage and never frames the claim in latent-cause/clustering terms.
- Yu & Dayan (2005, *Neuron* 46:681-692), VERIFIED: ACh = expected uncertainty, NE = unexpected
  uncertainty/context-switch signal — explicitly change-point-like, but pre-dates sticky-HDP-HMM (Fox et al.
  2011) and is never renamed or reformalized in CRP terms by later work.
- **Direct check of the papers that actually use CRP concentration parameters**: Sanders, Wilson & Gershman
  (2020, *eLife*, "Hippocampal remapping as hidden state inference") uses an explicit CRP concentration alpha
  for hidden-state/remapping inference and VERIFIED (fetched) explicitly declines to propose any
  neural/neuromodulatory correlate, calling their approach "an analytical heuristic rather than an algorithmic
  theory."
- **SEM itself, full-text grepped**: has a dedicated "Neural Correlates" section (pp.352-353) proposing vmPFC
  = posterior over event models, and dopamine (VTA/SNc) = within-event prediction-error signal — but ZERO
  occurrences of "acetylcholine," "norepinephrine," "noradrenaline," "locus coeruleus," or "pupil" anywhere in
  the full text. The sticky-CRP's own hyperparameters (concentration alpha, stickiness lambda) are left with
  NO proposed neural implementation, even in the flagship paper that introduces them. This is a checkable,
  verified gap, not an absence-of-search artifact.
- Two 2025 papers (McKenzie et al., eLife reviewed preprint 105183; Clewett, Huang & Davachi, *Neuron* 2025,
  PMC11343187) DO empirically tie LC-NE release to hippocampal "reset" at event boundaries — but both
  explicitly avoid Bayesian/CRP formalization, framed as "network reset," confirmed by direct quote-checking.

**Rating: GENERAL-ANALOGY-ONLY.** No paper names any neuromodulator as implementing a CRP concentration or
stickiness parameter. The closest legitimate bridges (Yu & Dayan's NE-as-change-point signal; the 2025
LC-NE/hippocampal-reset empirical work) are real but never formalized in CRP terms by anyone, including the
model's own authors.

## Marr-level adjudication table

| Level | Sticky-CRP (SEM / Gershman latent-cause lineage) | DG/CA3 pattern separation/completion |
|---|---|---|
| Computational (what problem, what's optimal) | Explicit, disciplined, author-disclosed. This is exactly what CRP is FOR. | Not typically framed this way in the primary lit (mechanism-first tradition), but implicitly solves the same problem. |
| Algorithmic (what representations/steps) | Undefined by the authors — "agnostic," "open empirical question." Only a particle-filter *sketch*, explicitly disclaimed as non-committal. | Well-characterized: sparse orthogonal DG code + CA3 recurrent-collateral autoassociative attractor, continuous sigmoidal separation-vs-completion arbitration. |
| Implementational (what neurons/circuits) | No verified bridge for the CRP-specific hyperparameters (alpha, lambda) to any neural quantity, even in the flagship paper. | Causally tested (Nakazawa 2002 NMDAR-KO), circuit-localized (DG vs CA3 double dissociation, Leutgeb 2007), decades of converging electrophysiology/lesion/imaging evidence per Yassa & Stark 2011 review. |

**Verdict: sticky-CRP is COMPATIBLE at the computational level (a legitimate, honestly-labeled rational model
of the event-clustering PROBLEM) but a DEVIATION if anyone treats it as validated at the algorithmic or
implementational level — which SEM's own authors never do, but which is exactly the risk flagged in today's
sister note** (`notes/exp_dev_handoff_research_brain_script_acquisition_consolidation_2026-08-09.md` anchor
3: "the CRP-style soft-match/spawn library-keying logic ... the genuinely novel, untested piece with no
owned precedent"). DG/CA3 pattern-separation/completion is the better-motivated brain SHAPE for the
match-or-spawn decision specifically — but no paper performs this comparison directly, so recommending it as
a replacement is this drill's own novel-synthesis judgment, capped and flagged accordingly below.

## Cheap decisive test

Ablate the discrete CRP draw against a continuous-similarity-graded rule on the SAME held-out episode set
already used for the `grounding_acquisition_loop.py` / `hdlab/learner` MDL-gate pipeline (anchor 1 of the
sister hand-off), before committing to anchor 3's full soft-match-or-spawn build:

1. Implement the CRP-style stickiness/concentration draw exactly as anchor 3 currently specifies (baseline).
2. Implement a DG/CA3-motivated alternative: compute a continuous similarity score between the incoming
   trace's situation-model register and each existing `LibraryItem`'s accumulated register (the CA3-style
   "how close is this to a stored attractor" measure), pass it through a graded threshold whose steepness is
   itself a function of local competition among candidate items (a DG-sparsity-style suppression term, not a
   free global concentration hyperparameter) — spawn a new item only when no candidate clears the graded
   threshold. No explicit recency/"stickiness" term (per the finding above that CRP's stickiness term has no
   clean neural analog; use last-N-episode context drift, if any, only if the researcher can point to it as
   temporal-context drift, not as a cluster-recency prior).
3. Compare cluster-purity / reuse-accuracy / false-consolidation-resistance on the identical corpus and
   `self_test` invariants already specified in the sister hand-off's anchor 3 design.

## Falsifiable predictions

**HARD-PASS**: the continuous-similarity/graded-threshold (DG/CA3-motivated) mechanism matches CRP's
cluster-purity and reuse-accuracy within 5% AND passes all of `self_test`'s existing coherent/scrambled/
adversarial invariants with zero regressions AND removes the unmotivated global stickiness hyperparameter —
adopt it as the brain-faithful replacement; this would be convergent evidence with Nguyen (2024)'s
independent ML-side "replace the fixed CRP prior" critique.

**MIDDLE_BAND**: the two mechanisms are statistically indistinguishable on the current (likely small/synthetic)
corpus — underpowered, not evidence of equivalence; proceed to a richer corpus (anchor 3's full multi-script
design) before concluding redundancy, same discipline the sister note already applies to its own anchor 1
vs anchor 3 sequencing.

**HARD-FAIL**: the continuous-similarity mechanism degrades cluster quality by more than 15% relative to CRP,
OR introduces a NEW false-consolidation path that CRP's discreteness happened to avoid (any one-off/
adversarial item promoted under the graded threshold that CRP correctly rejected) — in that case, CRP's
extra machinery is functionally load-bearing for this specific build's coverage even though it lacks brain
validation; the honest fix becomes RELABELING ONLY (document sticky-CRP explicitly as "a rational/
computational-level heuristic borrowed from Gershman's cognitive-modeling literature, not a claimed brain
mechanism" in the module docstring), not a mandatory rewrite, deferring the neural-shape replacement until it
stops costing accuracy.

## Cross-thread synthesis

This drill directly resolves the open risk flagged in today's earlier delivery
(`notes/research_brain_script_acquisition_consolidation_2026-08-09.md` / its companion hand-off, anchor 3):
"CRP-style soft-match/spawn logic = genuinely untested novel code" was correctly flagged as the
lowest-confidence piece of that design. This audit adds two sharpenings: (1) it was ALSO never validated as
brain-derived in the source literature — building it borrows an honestly-disclosed rational-model
abstraction, not a neuroscientific claim, so any internal documentation calling it "brain-faithful" would be
an overclaim regardless of how the ablation above turns out; (2) DG/CA3 supplies a concrete, causally-tested
alternative SHAPE (continuous similarity-graded competitive dynamics, no free stickiness hyperparameter) that
the cheap decisive test above can arbitrate cheaply, using infrastructure (`AccumulateRegister`,
`grounding_acquisition_loop.py::self_test`) the sister hand-off already scoped. This also converges with an
independent ML-literature critique (Nguyen 2024) that reaches "replace the fixed CRP prior" from a totally
different angle (learnability, not brain-fidelity) — two independent lines of critique landing on the same
fix is a meaningfully stronger signal than either alone.

## Substrate-product implications

- Do not let "sticky-CRP" pass as a brain-fidelity claim in module docstrings or hand-off files without the
  Marr-level caveat established here — per the standing brain-foundational discipline, an unvalidated
  computational-level convenience masquerading as mechanism is exactly the failure mode that discipline exists
  to catch.
- The cheap decisive test above is strictly cheaper than anchor 3's full build (anchor 1's infrastructure,
  already-scoped corpus) and produces a DIRECT answer to "does the brain-motivated shape cost anything" before
  committing to the harder full multi-script build — sequence it as anchor 3a, before the full anchor 3.
- If DG/CA3-shaped continuous competition wins (HARD-PASS above), it is also SIMPLER (one fewer free
  hyperparameter — no separate concentration + stickiness constants to tune) — a rare case where the
  brain-faithful fix and the parsimony-favoring fix coincide.

## Calibration

Per lit-scan calibration policy: this cycle is unusually well-verified (multiple full-text PDF fetches with
direct quotes across all 4 lanes, not snippet-only) — high confidence in the LITERATURE-CHARACTERIZATION
claims (Marr-level framing, replication status, neural-evidence specificity, absence of a neuromodulator
bridge). P for "the literature claims above are accurate as characterized" = 0.78 pre-deflation, deflated to
**0.60** (0.18 deflation — near the top of the 0.15-0.25 band, reflecting residual risk of missed citing
papers despite the multi-fetch verification density). The SEPARATE novel-synthesis claim ("DG/CA3 continuous
competitive dynamics is the right replacement mechanism, and the concrete cheap-test design above will
discriminate it correctly") is capped at **P=0.50** per the novel-synthesis rule — no paper performs this
comparison directly, so this is this drill's own construction, not literature-sourced.

## Citations (verified count)

Primary-source VERIFIED (full-text or abstract fetched and confirmed this cycle): 11 —
Franklin/Norman/Ranganath/Zacks/Gershman 2020 (Psych Review); Gershman/Blei/Niv 2010 (Psych Review); Wilson/
Takahashi/Schoenbaum/Niv 2014 (Neuron); Leutgeb/Leutgeb/Moser/Moser 2007 (Science); Nakazawa et al. 2002
(Science); Lisman & Grace 2005 (Neuron); Hasselmo 2006 (Curr Opin Neurobiol); Yu & Dayan 2005 (Neuron);
Sanders/Wilson/Gershman 2020 (eLife); Nguyen 2024 (arXiv:2409.18992); Basgol/Ayhan/Ugur 2022/2023 (Cognitive
Systems Research, arXiv:2210.05710).

SECONDARY (search-snippet or partial-fetch, not full-text quote-verified this cycle): 8 — Schuck/Cai/Wilson/
Niv 2016 (Neuron); Starkweather/Babayan/Uchida/Gershman 2017 (Nat Neurosci); Gershman & Niv 2010 (Curr Opin
Neurobiol); Yassa & Stark 2011 (Trends Neurosci); GoodSmith et al. 2017 (Neuron); Marr 1971 (Phil Trans R Soc
Lond B); Vinogradova 2001 (Hippocampus); McKenzie et al. 2025 (eLife reviewed preprint) / Clewett, Huang &
Davachi 2025 (Neuron).

Total distinct sources checked: 19.
