# Deep brain drill: how the brain achieves genuinely-learned compositional generalization, given what failed for us this session (5x / multi-angle)

**Filed by:** research (Opus synthesis over 4 parallel Sonnet lit-scan sub-agents). **Trigger:** direct USER
deep-brain-drill request, accounting explicitly for three session failures: (a) hand-denoised role/filler
vectors = free-by-construction, not learned; (b) hand-rule reader/extractor bounded at 0.557, emits symbols
not native maps, no grounding; (c) picture-verifier / thematic-fit oracle failed to train even gold-perfect.
Builds on, and does not relitigate, `notes/research_structural_residual_and_learned_in_substrate_reader_pivot_2026-07-19.md`
(factorization core = shared binding formalism, not literal shared circuit), `notes/research_integrated_graded_experiential_reader_viability_corpus_precondition_2026-07-19.md`
(CONTRAST across rivals, not gradedness, is what trains), `notes/research_mental_simulation_scene_verifier_error_signal_2026-07-19.md`
(SCV null result), and `notes/research_prediction_error_native_learning_signal_grounding_link_2026-07-09.md`
(predictive coding already partially built on this substrate: `hdlab/predictive_coding.py`, Spoke1 cell
family, P_deflated=0.46, MIDDLE_BAND not yet HARD_PASS).

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature agreement;
novel-synthesis capped at P<=0.50), per [[feedback-lit-scan-calibration-penalty]].

---

## HEADLINE

**1. Is the brain's key difference LEARNING-THE-GEOMETRY-FROM-GROUNDED-EXPERIENCE? PARTIALLY — corrected.**
The geometry is a genuine **hybrid**, not fully learned and not fully innate: the low-dimensional attractor
manifold (grid-cell population geometry) is substantially **pre-configured/scaffolded before experience**
(toroidal topology present ~P10, before eye-opening), while its **metric alignment/binding to specific
environments** is genuinely learned via a predictive (TD/successor-representation) objective over
experienced transitions (Stachenfeld et al. 2017; Tolman-Eichenbaum Machine, Whittington et al. 2020). And
"grounded" is the wrong qualifier for the general case: the strongest evidence for a **trainable** error
signal (N400-as-prediction-error models, Rabovsky & McRae 2014; Rabovsky/Hansen/McClelland 2018; Kuperberg
2024 PC-N400 model) is built on **amodal, distributional** feature spaces, not embodied/sensorimotor ones.
Grounding is **sufficient, not necessary**, for a dense continuous residual — the substrate's own real
ingested corpus stream is an equally valid, cheaper exogenous target (already independently found viable,
07-09 note).

**2. Is the missing element a grounded predictive-coding LEARNING LOOP? YES for "predictive-coding learning
loop," NO for "grounded" as the load-bearing qualifier.** The correct, sharper diagnosis: the missing
element is a **predictive, precision-weighted, error-driven loop that scores multiple explicit RIVAL
generative hypotheses against real subsequent (exogenous) data**, using the resulting **contrastive**
residual — not a grounded-per-se or merely-graded scalar coherence score — to drive both use-time selection
and weight update. This directly explains why our gold-perfect oracle (graded but non-contrastive, single
score against one curated table) still failed to train: gradedness without rivalry is exactly the
non-contrastive-collapse failure mode independently documented in BYOL/DINO (self-distillation architectures
avoid collapse only via an architectural trick substituting for negatives) and is exactly why active
inference's model-comparison layer (expected free energy compared ACROSS candidate policies/hypotheses) is
where contrast lives in the free-energy framework, not in the base per-site prediction-error signal.

**3. Single mechanism whose absence best explains all three failures:** **Contrastive Predictive Coding
over rival generative hypotheses, scored against real exogenous continuation data** (CPC/InfoNCE + active-
inference policy-comparison + Rao-Ballard precision-weighted residual, fused). Its absence explains: (a)
handed vectors — no predictive objective over experienced transitions to derive eigen-structure, so
structure was stipulated, not induced (TEM/SR shows the derivation mechanism); (b) hand-rule parser — no
generative forward model at all, so no error signal exists to extend rule coverage from experience, and no
mechanism for graceful degradation on novel phrasing (only ad hoc rule authoring); (c) oracle/verifier — had
gradedness, still failed, because it scored ONE hypothesis against a fixed table instead of comparing
MULTIPLE rival candidate parses' prediction errors against what the text actually says next. P_deflated=0.42
(single-unifying-mechanism claim; each component ingredient individually sits higher, 0.55-0.85, per angle
below — capped by novel-synthesis ceiling since no cited source combines all three ingredients in one
biologically-faithful package).

---

## Angle 1 — Is the geometry learned, not given? (grid cells / entorhinal structural code)

**Established:** Grid cells are the slowest-maturing spatial cell type — head-direction and border cells are
adult-like near eye-opening (~P14 in rat), grid cells reach adult hexagonal firing only over the following
1-2 weeks (Langston et al./Wills et al. 2010, *Science*; review: Tan et al. 2017, *WIREs Cog Sci*). But a
2026 bioRxiv finding shows the **toroidal population-level geometry** in MEC emerges even earlier, ~P10,
*before* active exploration — the attractor manifold itself is scaffolded early and largely
experience-independent, while behavioral read-out (metric hexagonal firing) matures later with locomotor
experience. A direct deprivation study (Wernle et al. lineage, PNAS 2023/PMC10576132) raised rats in
geometrically impoverished spherical enclosures for 2-3 months: grid cells still formed but were initially
disorganized on first exposure to a novel square arena (~6.5% qualified as grid cells vs. ~15% in
normally-reared controls), normalizing after only 5-7 days of exploration. Authors' own interpretation: **"a
preconfigured, experience-independent basis for the grid pattern"** whose alignment is fine-tuned by
experience, not built from scratch.

**The learning-rule account:** Stachenfeld, Botvinick & Gershman (2017, *Nat. Neurosci.*) — hippocampus
encodes a Successor Representation (expected discounted future occupancy) learned via TD-learning; grid
cells emerge as low-dimensional eigenvectors of the SR matrix (a spectral decomposition). Biologically
plausible spiking/STDP implementations now closely approximate TD-learned SR weights (George et al. 2023,
*eLife* 80680, 80663). The Tolman-Eichenbaum Machine (Whittington et al. 2020, *Cell*) is the closest full
computational demonstration: it factorizes a content-agnostic structural code (grid/border/object-vector-
cell-like) from environment-specific sensory content, trained on a purely predictive objective over
transition sequences across MANY structurally-similar environments — a genuinely learned low-conjunctivity
reusable code, not a hand-orthogonalized one, because its eigenstructure is DERIVED from the statistics of
experienced transitions.

**Load-bearing caveat (do not oversell):** "Disentangling Fact from Grid Cell Fiction in Trained Deep Path
Integrators" (PMC10723537) and the *Current Biology* NeuroAI piece show generic RNNs trained ONLY on
path-integration essentially never spontaneously produce hexagonal grid tuning without hand-crafted
supervised targets or specific architectural/regularization scaffolding inserted — much of the earlier
"grids emerge from training alone" literature (Cueva & Wei 2018; Banino et al. 2018) required substantial
scaffolding to get the hexagonal geometry specifically. The SR/TEM lineage derives grid-like periodicity
more directly from the objective's structure (spectral decomposition of predictable transition statistics)
with less hand-tuning, but "fully free, zero scaffold" is not an accurate summary of the field.

**Tolerance Principle (Yang):** A separate, well-validated (PMC10643500; Schuler & Yang) quantitative
account of WHEN a rule becomes productive over exemplars (exceptions e <= N/ln(N)) — a computational-level
efficiency argument for the tipping point from item-memorization to rule-extraction, not itself a synaptic
learning rule, but empirically matches child-acquisition timing for specific morphological rules.

**Timescale:** Grid maturation ~2-4 weeks postnatal (manifold scaffolded by ~P10, metric fine-tuning ~5-7
days once the attractor exists). Schema learning (Tse et al. 2007, *Science*): ~15 trials over ~1 month to
build a hippocampus-independent neocortical schema, after which NEW consistent associations are learned in
a single trial.

**Verdict, Angle 1 (deflated P=0.50):** Genuine hybrid — not fully learned, not fully innate. The strongest,
least-contested LEARNED component is TD-error/predictive-objective-driven weight learning (SR/TEM lineage)
producing low-conjunctivity bases as a side effect of learning to predict transition statistics — this is
mechanistically distinct from hand-orthogonalized vectors because dimensionality/eigenstructure is derived
from data, not stipulated. But some scaffold (recurrent architecture class, spectral/predictive objective
design, an early-forming attractor manifold) is doing real, non-optional work. Honest framing: "partially
learned, partially structurally scaffolded," not "fully free given the right geometry" and not "fully
learned from nothing."

## Angle 2 — Is grounding the source of structure AND the source of the error signal? (embodied cognition, N400)

**Established, structure claim:** Barsalou's Perceptual Symbol Systems (1999) and follow-ons (Barsalou et
al. 2003; Pecher et al., *Psychonomic Bull. & Rev.*) show concept representations recruit modality-specific
sensorimotor cortex, with simulations componential/context-dependent rather than fixed amodal feature lists.
Zwaan's Immersed Experiencer Framework and situation-model work (Zwaan 2009; Zwaan & Radvansky 1998) extend
this to sentence comprehension (readers simulate perceiver-relative distance/orientation). This is good
evidence grounded representations carry richer, denser, more graded relational STRUCTURE than an amodal
category lookup.

**Separable, and more contested, learning-signal claim:** Rabovsky & McRae (2014, *Cognition*) trained a
feature-based connectionist attractor network and showed settling-error tracks N400 amplitude across seven
classic effects, explicitly interpreting N400 as implicit prediction error. Rabovsky, Hansen & McClelland
(2018, *Nat. Human Behaviour*, Sentence Gestalt model) extended this: N400 = magnitude of change in an
implicit probabilistic sentence-meaning representation, unifying N400/P600 as one continuous update measure.
A 2024 hierarchical predictive-coding N400 model (PMC10984641) formalizes this as literal lexico-semantic
prediction error, continuous and graded (not threshold/binary). **Load-bearing finding: all three of these
models are explicitly AMODAL/distributional** (abstract feature vectors like <round>, <bouncy>; no embodied
simulation invoked) — the strongest N400-as-trainable-error-signal literature does NOT require grounding to
get gradedness and trainability.

**Verdict, Angle 2 (deflated P=0.50):** Grounding is **sufficient but not necessary**. It's one reliable way
brains obtain a high-density, continuous, contrastive feature space, but the mundane, better-evidenced
diagnosis for why our hand-curated oracle failed is that any coarse discrete/binary compatibility table
collapses the continuous residual needed for a nonzero, informative gradient — this would happen WITH or
WITHOUT sensorimotor content. The real requirement is graded, high-dimensional, RESIDUAL-based contrast, not
grounding per se. This is a genuine correction to the drill's own premise: "grounding is the source of the
error signal" over-specifies; "dense/continuous representational contrast is the source of the error
signal, and grounding is one route to obtaining it" is the better-supported claim.

## Angle 3 — Is comprehension prediction, not parsing? (surprisal, active inference, Sentence Gestalt)

**Established:** Surprisal theory (Hale 2001; Levy 2008) — word-by-word difficulty as negative log-
probability from an incremental probabilistic (generative) parser — robustly predicts garden-path
slowdowns and reading-time effects across ~6 orders of magnitude, a unifying result classical rule-based
accounts don't achieve alone. Caveat: neural-LM-derived surprisal underestimates garden-path magnitude in
some studies; Futrell's lossy-context-surprisal argues memory constraints on the context representation are
ALSO needed (prediction alone is incomplete). Anticipatory eye movements (Altmann & Kamide 1999; Kamide et
al. 2003) are solid, replicated evidence of real-time GENERATIVE anticipation (not retrospective
structure-building) combining multiple cues (subject+verb) before the target word arrives.

**Concrete computational template — the Sentence Gestalt model** (McClelland/St. John/Taraban 1989; revived
Rabovsky/Hansen/McClelland 2018): an update network incrementally folds each word into a distributed
"Gestalt" hidden layer representing current best estimate of full event meaning; a separate query network
reads out role-fillers on demand. Information flow: predict (implicit event-role expectation) -> compare
against actual input -> error/update hidden state -> carry forward. **This is, independently, almost exactly
our own "compress-and-carry" framing** (Kintsch-CI/van Dijk, per the standing anchor) — converging evidence
this loop shape is the right target, not a novel invention.

**Robustness argument (mixed, not airtight):** Noisy-channel comprehension models (Levy, Gibson) and
connectionist parsers show graceful (not catastrophic) degradation on noisy/ungrammatical input, a real,
citable advantage. But symbolic systems' typical failure mode when engineers add robustness is
OVERGENERATION (too many candidate parses), not brittleness per se — and "good-enough processing" (Ferreira
et al.) shows HUMANS themselves often use shallow heuristics rather than full generative analysis, so some of
prediction's apparent robustness advantage may be heuristic shallow-processing, not deep generative modeling.

**Verdict, Angle 3 (deflated P=0.45):** Predictive/generative comprehension is the better-evidenced account
and IS a genuinely different architecture class from rule-based parsing (concrete template exists:
Sentence Gestalt). But "our 0.557 ceiling is BECAUSE we used rules not prediction" is the LEADING hypothesis,
not an established diagnosis — rule-coverage gaps and good-enough shallow-processing remain live,
distinguishable alternatives that need to be ruled out (does the ceiling correlate with coverage gaps on
held-out constructions, vs. with genuinely novel/OOD phrasing specifically where predictive graceful
degradation would help)?

## Angle 4 — What is the learning signal we lack, and can it be replicated without an external LLM?

**Established:** Predictive coding / free-energy principle (Rao & Ballard 1999; Friston) — hierarchical
generative model, top-down predictions, bottom-up precision-weighted residual, minimizing variational free
energy (accuracy + complexity). Self-supervised by construction: the "label" at every instant is just the
next sensory sample. Dopaminergic reward-prediction-error (Schultz) is a special case of the same
compare-predict-update algorithm, generalized to novelty/curiosity-driven learning even absent reward.

**Are prediction-error-minimization and contrastive-rival-comparison the same mechanism?** Leans
complementary-but-nested, not identical: base predictive coding gives a scalar error per site — not
intrinsically contrastive. But active inference's POLICY/MODEL SELECTION layer is explicitly comparative:
expected free energy is compared ACROSS candidate policies/hypotheses, with posterior-over-policies
proportional to model evidence (Parr & Friston 2019). **This is the mechanistic bridge that explains our
own sibling finding (CONTRAST across rivals, not gradedness, is what trains):** contrast lives in the
higher-order hypothesis-comparison layer of the free-energy framework, not in the base per-site residual.
Flag: framing PC+contrast as literally "one mechanism" is speculative/emerging synthesis, not settled
consensus — most sources treat perception (PC) and policy-comparison (active inference) as related but
formally distinct layers.

**ML precedents, ranked by match to "grounded/exogenous + rival-scored + local-contrastive":**
- **CPC** (van den Oord et al. 2018): predicts future latents, InfoNCE scores the true future against
  SAMPLED NEGATIVES — genuinely rival-based, closest ML match to (a)+(b) of the target shape.
- **BYOL/DINO** (self-distillation, explicitly NON-contrastive): avoid collapse only via architectural
  asymmetry (stop-gradient, momentum teacher) substituting for negatives — a direct cautionary parallel: a
  non-contrastive graded score is collapse-prone/untrainable without either negatives or an architectural
  trick, exactly what happened to our gold-perfect single-score oracle.
- **World models** (Ha & Schmidhuber 2018; Dreamer lineage): forward-model prediction error used AS its own
  intrinsic curiosity reward — matches (a)+(b).
- **Equilibrium propagation**: biologically-plausible LOCAL, contrastive-by-construction learning rule
  (free phase vs. weakly-clamped phase) — best precedent for (c), no backprop needed.

**No single cited architecture combines all three** (grounded/exogenous forward prediction + explicit
rival-hypothesis scoring + local contrastive update) in one biologically-faithful package — this composite
is itself flagged in the literature as an open research direction. Each ingredient has independent,
well-established precedent; the combination is genuine novel synthesis (justifying the P<=0.50 cap).

**Verdict, Angle 4 (deflated P=0.50, capped):** The missing-learning-signal diagnosis is real and plausible
as ONE necessary ingredient common to all three failures, but resist calling it a single proven unification:
(i) handed vectors lacked a representation-LEARNING signal (CPC/EP-style local contrastive loss) to shape
structure from data; (ii) the hand-rule parser lacked an error signal FROM PREDICTION AGAINST OUTCOME to
revise/extend rule coverage; (iii) the oracle specifically lacked RIVAL comparison — exactly the gap active
inference's policy-comparison layer fills by scoring competing hypotheses against each other rather than
each hypothesis against one fixed gold table. A shared underlying gap (no self-supervised, contrastive,
error-driven update rule) plausibly explains all three, but each failure also has a distinguishable proximate
cause.

## Angle 5 — Envelope-push: the single mechanism, and what it changes

**Name:** a **precision-weighted predictive-coding loop that maintains multiple explicit rival generative
hypotheses and scores their prediction error against real subsequent exogenous data, using the CONTRASTIVE
(relative) residual — not a single scalar coherence score — to drive both use-time selection and local
weight update.** This is CPC's rival-scoring + active inference's cross-hypothesis model comparison +
Rao-Ballard's precision-weighted residual + the substrate's own already-partially-built
`predictive_coding.py` primitive, fused into one loop. Grounding (Angle 2) is demoted from "the" ingredient
to "one valid instance of" the more general requirement (dense, continuous, exogenous target content) — the
substrate's real ingested corpus stream already qualifies (07-09 note: satisfies the disjoint-exogenous-data
axis AND the differentiated-plasticity-rule axis, "for free," without needing literal embodiment).

**How it would change the substrate, concretely (buildable largely from existing primitives, genuinely
novel combination — hence P<=0.50):**
1. At each clause/token boundary, maintain the ALREADY-SCOPED rival LCCP candidate parses (the SCV design's
   rival set, per the 07-19 note) rather than committing to one hand-rule-selected structure.
2. Each rival's lightweight generative/predictive sub-model predicts upcoming ACTUAL text/structure (reusing
   `predictive_coding.py`'s `residual_magnitude`/`proportional_gate` machinery, already half-built per the
   07-09 note).
3. Score each rival's prediction error against the real, exogenous continuation (the next actual words in
   the corpus — not a self-generated or oracle-curated target). The gain over the failed oracle design: the
   comparison target is now REAL FUTURE DATA, continuous, and there are multiple rivals to contrast against,
   not one fixed table.
4. Use the RELATIVE (contrastive) error across rivals — not any single rival's absolute score — to (i)
   select the winning parse at use-time, and (ii) drive a local, precision-weighted update into a dedicated
   weight matrix (kept structurally separate from the existing contrastive-Hebbian W, mirroring the CLS
   lesson already flagged in the 07-09 note) that refines both the small LCCP cue-integration weights
   (per the 07-19 corpus-precondition note's narrower, buildable-now scope) AND, cumulatively over many
   instances, the reusable structural code itself (the TEM/SR-style generalizing geometry from Angle 1) —
   rather than a hand-denoised one.
5. This directly resolves the diagnosed cause of the SCV's null result: the SCV scored ONE candidate against
   a coherence table (no rivalry, no real-data target); this design scores MULTIPLE rivals against REAL
   subsequent text (rivalry + exogenous target), which is exactly the two changes the literature says are
   necessary for a graded signal to actually train (Angle 4's BYOL/DINO cautionary parallel + Angle 2's
   dense-continuous-target requirement).

---

## Cheap decisive test

**Step 1 (free, reuse existing instrumentation):** Read the actual `v2` Spoke1 cell source
(`exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v2`) to confirm HOW its
already-landed `ARM_PREDICTIVE_ONLY` (gap=0.566, per the 07-09 note's disk-verify table) computes its write
strength — if it already writes through a dedicated, precision-weighted matrix rather than the shared
competitive-allocation machinery, this drill's core mechanism (steps 2-4 above) may already be PARTIALLY
running and testable by re-reading existing metrics, not by building anything new.

**Step 2 (build, small, reuses the already-scoped SCV rival-candidate set):** Wire the existing rival-LCCP
candidate generation (already designed per the 07-19 SCV note) to `predictive_coding.py`'s residual machinery,
scoring each rival's forward prediction against the REAL next clause/sentence in held-out corpus text
(not the coherence-table oracle). This is a re-target of an already-built component (rival candidates +
predictive-coding primitive), not new representational math.

**Step 3 (falsification-critical, must-fail control):** Compare three arms on the SAME held-out set: (A)
single-hypothesis absolute residual (replicates the failed SCV's non-contrastive shape — expected to
reproduce the null/near-zero training signal), (B) multi-rival CONTRASTIVE residual against real exogenous
continuation (this drill's proposed mechanism), (C) multi-rival contrastive residual against a SHUFFLED/
scrambled continuation (must-fail control — if (C) trains as well as (B), the signal is not actually using
real predictive structure and the result is vacuous).

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1 — Contrast (arm B) produces a measurable, nonzero training signal where absolute single-
hypothesis scoring (arm A) does not.** P=0.45 (deflated; strong theoretical convergence across CPC,
active-inference model-comparison, and the BYOL/DINO cautionary parallel, but genuinely untested in this
exact combination). **HARD-PASS:** arm B's measured weight-update magnitude (or downstream metric delta) is
statistically distinguishable from zero AND from arm A's (near-zero, per the SCV precedent). **HARD-FAIL:**
arm B shows no more training signal than arm A — would mean rivalry-without-grounding-content is still
insufficient, and the missing ingredient is something Angle 2 under-weighted (grounding may matter more than
this drill concludes) or something not yet identified.

**Prediction 2 — Must-fail control: arm C (contrastive-against-shuffled) collapses toward arm A's near-zero
signal, NOT toward arm B's.** P=0.55 (deflated; this is the more standard, better-precedented claim — a
predictive signal against scrambled targets should be uninformative by construction). **HARD-PASS:** arm C's
signal is statistically indistinguishable from arm A and clearly below arm B. **HARD-FAIL:** arm C trains as
well as arm B — the "signal" is coming from something other than genuine predictive structure against real
data (e.g., a leakage/confound in the rival-scoring setup); do not trust Prediction 1 even if it nominally
HARD-PASSes.

**Prediction 3 — the learned weight update, over enough instances, measurably shifts the LCCP cue-
integration weights in the direction the 07-19 corpus-precondition note already scoped as buildable-now
(small cue-trust reweighting on the existing WordNet/VerbNet scaffold), rather than needing new distributional
word-meaning statistics.** P=0.40 (deflated; this is the corpus-scope constraint already established
07-19, carried forward as a prediction about THIS specific mechanism). **HARD-PASS:** cue-weight shifts are
measurable and improve held-out disambiguation accuracy without requiring new corpus-scale distributional
statistics. **HARD-FAIL:** no measurable cue-weight shift occurs even with clear contrastive signal present
(Prediction 1 HARD-PASS) — would mean the signal exists but doesn't propagate to the intended parameters,
an implementation/wiring bug to fix before drawing further conclusions.

---

## Cross-thread synthesis

This drill directly reconciles three same-day findings that looked, on the surface, disconnected: (1) the
SCV's null result (`research_mental_simulation_scene_verifier_error_signal_2026-07-19.md`) is now explained
mechanistically, not just empirically — it lacked BOTH rivalry (Angle 4) and a real-data target (Angle 2),
the two ingredients this drill's literature converges on as jointly necessary; (2) the corpus-precondition
note's scope-split (`research_integrated_graded_experiential_reader_viability_corpus_precondition_2026-07-19.md`)
is corroborated and narrowed further — the buildable-now target is cue-INTEGRATION weight learning on the
existing symbolic scaffold, which Prediction 3 above operationalizes as a specific, falsifiable claim; (3)
the standing prediction-error/grounding thread from `research_prediction_error_native_learning_signal_grounding_link_2026-07-09.md`
is directly extended — that note found predictive coding viable as an additional learning axis (P=0.46,
already partially built, MIDDLE_BAND) and found predicting real ingested data satisfies the exogenous-
anchor requirement "for free"; THIS drill adds the missing piece that note flagged as untested: the
CONTRASTIVE (multi-rival) framing, which that note did not yet have (it proposed a single PRED arm, not a
rival-scored one).

It also corrects, not just confirms, the drill's own opening premise: "grounding is the source of structure
AND the error signal" over-claims — the literature draws a real, load-bearing distinction between grounding
providing STRUCTURE (established) and grounding being NECESSARY for a trainable error signal (not
established; the strongest N400-training models are amodal). Per
[[feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts_2026-07-17]], this
correction is reported as a finding, not smoothed over to fit the prompt's framing.

The factorization-core framing (07-19 note, Angle 3 there) is reinforced from a new angle: Angle 1 here
shows the brain's OWN structural code is similarly a hybrid of scaffolded-attractor-geometry + learned-
binding-to-content, which is architecturally analogous (not identical) to keeping the factorization core
(reusable binding substrate) and the content/data-specific learned weights as distinct layers — the brain's
grid-cell/hippocampal split (structural-scaffold cells vs. content-bound place cells) is itself a real
biological precedent for exactly that architectural separation, strengthening (not merely repeating) the
07-19 verdict.

## Substrate-product implications

Not a publication angle — a build-priority and honesty angle. This drill's practical payoff is a SPECIFIC,
falsifiable redesign of the failed SCV: swap "one hypothesis vs. a curated coherence table" for "multiple
rival hypotheses vs. real subsequent corpus text, scored contrastively." This reuses THREE already-existing
or already-scoped components (the SCV's rival-LCCP candidate generation; `hdlab/predictive_coding.py`'s
residual/precision-weighting machinery; the corpus-precondition note's narrow cue-integration-weight
learning target) rather than requiring new representational math or a new corpus investment — the single
biggest practical finding of this drill is that the fix is a RE-WIRING of existing parts into the rivalry +
real-data-target shape, not a new architecture. If Prediction 1 HARD-FAILs, the honest fallback is that
Angle 2's "grounding demoted to sufficient-not-necessary" call was wrong for THIS substrate's specific
content (its amodal WordNet/VerbNet scaffold may be too coarse to serve as adequate generative content even
with rivalry added), reopening the grounding question rather than the rivalry question. If Prediction 2
HARD-FAILs (shuffled control trains as well as real), STOP — this indicates a leakage/confound bug, not a
positive result, and no downstream claim should be built on Prediction 1 until Prediction 2 is independently
re-verified clean.

For the standing learned-in-substrate-reader program (USER 07-18 authorization): this drill provides the
first mechanistically-motivated, falsifiable design for the "compress-and-carry" loop's actual LEARNING
signal — previously the compress-and-carry framing had the right shape (Sentence-Gestalt-like, per Angle 3)
but no validated training signal; this drill closes that gap with a specific, cheap, largely-already-built
proposal, at the cost of an honest P<=0.50 novel-synthesis cap since no cited source has combined these three
ingredients before.

---

## Citations (verified count)

**~40 distinct primary/named sources** across 4 parallel live lit-scans, synthesized here (each sub-agent's
report independently listed sources; flagged inline above where a specific claim rests on a single
contested/unreplicated finding): Langston et al. 2010 *Science*; Wills et al. 2010 *Science*; Tan et al.
2017 *WIREs Cog Sci*; 2026 bioRxiv toroidal-geometry-precedes-navigation preprint; Wernle et al.-lineage
PNAS 2023 (PMC10576132) geometric-deprivation study; Stachenfeld, Botvinick & Gershman 2017 *Nat.
Neurosci.* (predictive map / successor representation); Whittington et al. 2020 *Cell* (Tolman-Eichenbaum
Machine); George et al. 2023 *eLife* 80680 and 80663 (STDP/spiking SR implementations); Widloski & Fiete
(grid cell development via STDP); Cueva & Wei 2018, Banino et al. 2018 (trained deep path integrators);
PMC10723537 and *Current Biology* NeuroAI critique (grid-cell-fiction caveat); Yang (Tolerance Principle,
multiple papers, PMC10643500, Schuler & Yang); Tse et al. 2007 *Science* (schema consolidation); Barsalou
1999 *BBS*, Barsalou et al. 2003 (perceptual symbol systems); Pecher et al. *Psychonomic Bull. & Rev.*;
Zwaan 2009, Zwaan & Radvansky 1998 (situation models, event-indexing); Rabovsky & McRae 2014 *Cognition*;
Rabovsky, Hansen & McClelland 2018 *Nat. Human Behaviour* (Sentence Gestalt / N400); PMC10984641 (2024 PC
model of N400); Kuperberg lineage (N400-in-silico, hierarchical PC for language); Hale 2001, Levy 2008
(surprisal theory); Futrell (lossy-context surprisal); Altmann & Kamide 1999, Kamide et al. 2003
(anticipatory eye movements); Christiansen & Chater (Now-or-Never bottleneck); Tabor & Tanenhaus (dynamical
parsing); Levy & Gibson (noisy-channel comprehension); Ferreira, Bailey & Ferraro (good-enough processing);
Rohde & Plaut (connectionist language processing); Rao & Ballard 1999 *Nat. Neurosci.*; Friston (free-energy
principle, multiple); Parr & Friston 2019 (generalised free energy / active inference policy comparison);
van den Oord et al. 2018 (Contrastive Predictive Coding, InfoNCE); BYOL/DINO self-distillation lineage;
Ha & Schmidhuber 2018 (world models); Dreamer/DreamerV2/V3 lineage; Equilibrium Propagation lineage; Schultz
(dopaminergic reward-prediction-error). All cross-referenced against, and consistent with, this session's
own prior notes: `research_structural_residual_and_learned_in_substrate_reader_pivot_2026-07-19.md`,
`research_integrated_graded_experiential_reader_viability_corpus_precondition_2026-07-19.md`,
`research_mental_simulation_scene_verifier_error_signal_2026-07-19.md`,
`research_prediction_error_native_learning_signal_grounding_link_2026-07-09.md`.

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: novel-synthesis capped at P<=0.50 throughout. The unified
Angle 5 mechanism (contrastive predictive coding over rival hypotheses, scored against real exogenous data)
is this drill's own cross-literature synthesis, held at P=0.42 — no single cited source addresses this exact
combination. Each component literature individually sits at the P levels reported per-angle (0.40 to 0.85
depending on how directly-evidenced vs. inferred). The correction to the drill's own premise (grounding
demoted from necessary to sufficient-for-one-instance) is itself flagged as an interpretation running ahead
of a head-to-head empirical test — no source directly compares a grounded vs. amodal version of the SAME
oracle/verifier on the SAME task; this is an inference from convergent indirect evidence (the N400 models
being amodal AND trainable), not a controlled comparison.

---

## VERDICT (one line)

**The brain's structural code is a genuine hybrid (scaffolded attractor geometry + learned predictive
binding, per TEM/SR), NOT simply "learned from grounded experience" — grounding is demoted from necessary to
one-sufficient-instance of a more general requirement (dense, continuous, exogenous content); the true
single mechanism whose absence best explains all three session failures is a precision-weighted predictive-
coding loop that scores MULTIPLE RIVAL generative hypotheses against REAL subsequent exogenous data using
their CONTRASTIVE (not absolute/scalar) residual to drive both selection and learning — this is buildable
now largely from already-existing substrate primitives (predictive_coding.py, the SCV's rival-LCCP
candidates, the corpus-precondition note's cue-integration scope) via a specific re-wiring, not a new
architecture, at P_deflated=0.42 (novel-synthesis-capped) pending the 3-arm must-fail-controlled test
above.**
