# Research: the exact end-to-end neural circuit for context-specific word-sense selection — stage-by-stage, vs our pipeline

Filed by: research sub-agent, 2026-09-03. Direct WebSearch/WebFetch drill (no sub-agents), for
`break_the_contextual_input_encoding_ceiling_for_specific_sense_selection`. Our pipeline: word2vec
context-word vectors -> biased-competition (variance-diagnosticity) weighting -> cosine to WordNet-gloss
sense vectors -> argmax. Caps at a_s~0.31 on subordinate senses; readout saturated (iterative settling
collapsed to one-shot); ~85% of the disambiguating info is present in context (oracle-extractable) but
gold-blind extraction gets only ~0.31. Builds on and does NOT duplicate two prior notes already on disk:
`notes/research_wsd_context_conditioned_sense_selection_2026-08-23.md` (prior x likelihood decomposition,
CSC control network, already recommends an additive frequency-prior arm, P_deflated=0.40, NOT YET TESTED)
and `notes/research_channel_combination_reliability_weighting_2026-08-23.md` (distributional vs
sensorimotor/experiential channel fusion, concreteness-gating). This note's job: pin the CIRCUIT, stage
by stage, and locate the one stage most responsible for the *subordinate-sense-specific* ceiling — a
different, sharper diagnostic question than either prior note asked.

`research_field_advisor.py` run at cycle start: not applicable (its 22 fields are substrate-physics/
stat-mech, no adjacency to this cognitive-neuroscience question) — same finding as both prior notes.

---

## HEADLINE

**The stage most responsible for the reported symptom (ceiling specifically on subordinate senses,
despite ~85% of the answer being present in context) is Stage 3 — dynamic semantic control (LIFG/pMTG)
— and this substrate already tried the brain's most literal implementation of it and HARD-FAILED for a
diagnosed, non-mechanism reason.** `exp_task_local_normalisation_pool_v1` (ORGAN_MAP C3) built exactly
the Chiou/Lambon-Ralph 2018 operation — a context-driven multiplicative gain boost on the
task-relevant representation dimensions — and it HARD-FAILED (d=-0.0220) because on this substrate's
256-dim / ~70-observations-per-concept representation, the dimensions most worth boosting are also the
worst-estimated ones (estimation noise, not wrong mechanism, blocked behind B4). This is exactly
consistent with "readout saturated": the brain-correct control operation needs a sharper representation
before it can work, so a fresh coherence-only cosine-argmax cannot recover the extra 54 points (0.85
minus 0.31) no matter how it re-weights the existing noisy dimensions in one shot.

Stage 1's missing frequency/dominance PRIOR (already flagged in the 08-23 note) is real and cheap to
add, but — a sharper point this note adds — **it targets the wrong error pattern for this specific
symptom.** The reordered-access literature (Duffy/Morris/Rayner 1988) predicts a frequency prior helps
DOMINANT-congruent items and *costs* a little on SUBORDINATE-congruent items (the human RT data: 13-46ms
slower even under strong disambiguating context). A pipeline capped specifically on subordinate items
needs a STRONGER, sharper *likelihood* signal when context favors the rare sense — not a prior that by
construction pulls the other way. Build the prior anyway (it fixes a different, real defect and is
free), but do not expect it to move the a_s~0.31 subordinate number.

The most promising buildable, glass-box, transformer-free fix is **Stage 4: an explicit discourse/
situation-level prior term**, additive alongside Stage 1's frequency prior and the existing coherence
score — `score(sense_i) = log_prior_freq(sense_i) + log_prior_discourse(sense_i | discourse-so-far) +
coherence(local_context, sense_i)`. This gets the FUNCTIONAL benefit of top-down control (use more of
what's already known to sharpen the choice) via an INDEPENDENT evidence source that doesn't require
estimating which of the existing noisy context/gloss dimensions to boost — sidestepping the exact wall
that blocked the literal Stage-3 rebuild. **Caveat, stated plainly per calibration discipline: no
source anywhere — including the only implemented computational model of the N400 (Nour Eddine &
Kuperberg 2024) — actually builds or tests a discourse-level prior for word-SENSE selection. The
authors' own model explicitly has no discourse/situation level and "cannot represent competing word
senses." This is genuine novel synthesis, capped at P<=0.50.**

P_deflated: Stage-1 prior-term "real but wrong-symptom-target" — 0.55 (well-pinned mechanism, high
confidence in the *qualitative* mismatch argument). Stage-3-is-the-blocked-mechanism diagnosis — 0.45
(strong within-substrate evidence via C3, deflated for extrapolating the *reason* onto this specific
sense-selection symptom rather than C3's original task). Stage-4 discourse-prior fix — 0.35 (novel
synthesis, capped, no direct precedent for sense selection specifically).

---

## Stage 1 — Lexical access / form -> meaning (VWFA -> posterior temporal): sense-UNSELECTED then resolved

**PINNED.** Swinney (1979, *J Verbal Learning & Verbal Behavior* 18:645-659), cross-modal priming:
at word offset, BOTH senses of an ambiguous word are primed *regardless of prior disambiguating
context* — context does not pre-select before any sense activates. Several syllables later, only the
contextually-appropriate sense remains primed. This is **exhaustive access, then rapid context-driven
suppression**, not selective access. Simpson (1981/1994)'s diagnostic three-way interaction test for
pure selective/context-only access was non-significant — ruled out.

**PINNED, homonymy vs polysemy dissociate.** Klepousniotou, Pike, Steinhauer & Gracco (2012, *Brain and
Language* 123:1) EEG/N400: for **homonyms** (unrelated meanings, e.g. "pen"), only the **dominant**
meaning shows a reduced N400 — real winner-take-most, competing/separate lexical entries (also
Klepousniotou 2002: homonym meanings *inhibit* one another in priming). For **polysemes** (related
senses, e.g. "lip"/metaphorical, "rabbit"/metonymic), **both dominant and subordinate senses** show
reduced N400 — one shared, underspecified core representation, senses *facilitate* each other in
priming rather than compete. **This is a genuine architectural fork our pipeline does not encode at
all**: it treats every WordNet multi-sense entry uniformly (cosine to k discrete gloss vectors,
argmax), when the brain runs two different regimes depending on whether the senses are a homonym split
or a polysemy cluster.

**PINNED, reordered access (best-supported model).** Duffy, Morris & Rayner (1988, *J Mem Lang*
27:429-446), replicated Binder & Rayner (1998, *Psychon Bull Rev* 5:271-276): resting activation is set
by frequency (dominant sense has a head start); context adds an activation boost to the contextually
relevant sense; a measurable reading-time cost (~13-46ms) occurs specifically when frequency and context
disagree, and the cost survives even under strong disambiguating context. No literal equation published;
qualitative rule only.

**NEW this pass — timing is earlier and less cleanly staged than textbook serial access implies.** Mollo,
Jefferies, Cornelissen & Gennari (2018, *Brain and Language* 177-178:23-36), MEG, verified fetch: LIFG
shows a context-by-ambiguity interaction (controlled-retrieval signature) starting **within ~100ms** of
stimulus onset, persisting through 150ms and 300-400ms; posterior MTG shows interactions at ~100ms/20Hz
and again at 500-600ms. Both regions show effects *earlier than the classic ERP literature's ~100ms/
N400 window*, meaning control-network involvement overlaps the earliest stages of access itself rather
than switching on only after a clean initial-access phase completes. No formal equation; oscillatory
power changes only.

**Verdict for our pipeline:** Stage 1's core missing computational content is the **frequency/dominance
prior** (already identified, 08-23 note, P_deflated=0.40, not yet built/tested) — but per the HEADLINE
argument above, this term's predicted benefit pattern (help dominant-congruent, small cost on
subordinate-congruent) is the wrong shape to explain a ceiling specifically ON subordinate items.

---

## Stage 2 — ATL hub + sensorimotor/affective spokes: what grounded features add beyond distributional vectors

**PINNED, hub function (qualitative, no closed-form equation found anywhere in primary sources —
confirmed again this pass, same finding as the 08-23 companion note).** Lambon Ralph, Jefferies,
Patterson & Rogers (2017, *Nat Rev Neurosci* 18:42-55): bilateral ATL is a transmodal, amodal hub that
integrates modality-specific "spoke" inputs (visual-form, auditory, motor/praxis, affective, verbal/
distributional) into a single graded conceptual similarity space, and mediates transmodal interactions
between spokes (patterns not derivable from any one spoke alone — this is the empirical signature of
semantic-dementia patients losing category-general, cross-modal concept structure, not just one input
channel).

**PINNED, complementarity is MEASURED, not assumed** (re-confirmed from the companion note, directly
relevant to Stage 2 of this drill): Bruni, Tran & Baroni (2014, *JAIR*) directly measure that a
text+image (grounded) model beats text-only on semantic tasks — the visual channel "provides
complementary semantic information," not redundant with distributional statistics. Andrews, Vigliocco &
Vinson (2009, *Psychol Rev*) and Roller & Schulte im Walde (2013, EMNLP): joint
experiential+distributional models fit human similarity/relatedness judgments better than either source
alone. Contested counter-view (Louwerse, symbol-interdependency hypothesis): perceptual structure is
already redundantly encoded in language statistics — genuinely unresolved, flagged honest.

**What this means concretely for our pipeline:** word2vec context vectors and WordNet-gloss vectors are
**both pure distributional/associative channels** — structurally missing the grounded (sensorimotor,
affective, praxis) spoke information the ATL hub integrates and that is independently measured to carry
real, non-redundant sense-discriminating signal. For subordinate senses specifically, this may matter
disproportionately: subordinate/rare senses often have short, underspecified WordNet glosses (little
distributional signal to extract a sharp cosine target from) where a grounded feature (e.g.
concreteness, a McRae/Cree feature-norm cluster) could disambiguate where pure co-occurrence text
cannot. **This is a real, measured gap, but it is a general representation-quality issue, not shown
anywhere in the literature to be *specifically* a subordinate-sense-selection mechanism** — flag as
PLAUSIBLE-BY-SYNTHESIS, not pinned for this exact application.

---

## Stage 3 — Semantic control (LIFG + pMTG): the exact operation

**PINNED, control = dynamic connectivity boost to the task-relevant spoke, not (necessarily) gain on an
already-fixed vector.** Chiou, Humphreys, Jung & Lambon Ralph (2018, *Cortex* 103:100-116), 5-node DCM:
effortful/task-relevant retrieval selectively **strengthens IFG's effective connectivity TO the
spoke/region holding the task-relevant feature dimension** — control changes what information flows
INTO the hub computation, not (only) a post-hoc reweighting of an already-computed similarity vector.
Hoffman, McClelland & Lambon Ralph (2018, *Psychol Rev* 125:293-328) give the closest thing to a
literal equation in this whole area: hub input = a weighted combination of candidate response options,
weights set by a **context buffer** ("prediction units" carried from the previous timestep), continuously
reweighted as the network **settles**.

**Unresolved tension, PINNED as an open question within the same research program.** Jackson, Rogers &
Lambon Ralph (2020, *Nat Hum Behav*) found their own best-fitting computational architectures place
control on the SPOKES (peripheral, feature-level), not on hub-input weights as in Hoffman et al 2018 —
the same lab has two live computational accounts of WHERE control physically acts, unresolved as of
this pass.

**PINNED, control is dissociable into two separable operations, not one.** Badre & Wagner (2002, 2005
Neuron): **controlled retrieval** (getting task-relevant knowledge active at all — anterior LIFG) is
dissociable from **selection** (choosing among already-competing active alternatives — more posterior
LIFG/parietal). Noonan, Jefferies et al. (2010/2013, *Cerebral Cortex*; TMS): confirms a **distributed**
network (LIFG + pMTG both causally necessary, not LIFG alone) with graded, modality-specific
specialisation (pMTG more verbal-weighted, anterior IFG stronger for verbal associations specifically).

**PINNED, the physiological mechanism at the neuron-population level is genuinely time-extended
competition, not a single feedforward score.** Desimone & Duncan (1995) biased-competition model:
multiple simultaneously-active stimulus/candidate representations mutually SUPPRESS each other in a
shared processing pool; top-down attention/control biases this competition toward the task-relevant
representation. Reynolds, Chelazzi & Desimone (1999, *J Neurosci* 19:1736-1753) and Chelazzi, Miller,
Duncan & Desimone (1993, *Nature* 363:345-347; 1998, *J Neurophysiol* 80:2918-2940): single-unit
recordings in macaque IT/V4 show the population response to a cued target **sharpens gradually over
~150-300ms** within a trial as competing (distractor) representations are progressively suppressed —
a genuine settling process, not an instantaneous computation.

**Directly relevant counter-finding, semantic domain, fetched full text this pass.** Shahdloo, Çelik &
Çukur (bioRxiv 658096, "Biased competition in semantic representation during natural visual search"):
at the level of semantic *tuning profiles* (fMRI, divided attention between two known target
categories), the converged/asymptotic outcome of biased competition is well predicted by a **static,
one-shot weighted linear combination** (ordinary-least-squares fit across single- vs divided-attention
conditions) — no iterative dynamics needed to fit the aggregate result at this (slow, fMRI) timescale.
**Reconciliation: the underlying microcircuit process (mutual suppression + gain, Reynolds/Chelazzi/
Desimone) is iterative/time-extended; its converged OUTCOME can be well-approximated by a one-shot
weighted score IF the weights are properly calibrated** — exactly the McClelland (2013) equivalence
condition already pinned in the 08-23 note (bias=log-prior, weight=log-likelihood, conditional
independence, additive in log-space). **This means "iterative settling collapsed to one-shot" is, on
its own, probably NOT the fundamental gap** — a well-calibrated one-shot score can reach the same
fixed point. The real gap is that our cosine-similarity score is not a calibrated log-likelihood and
our "biased-competition weighting" is not the brain's actual operation (a connectivity-style boost to
task-relevant *representation dimensions*, which requires a sharp enough representation to boost in the
first place).

**Cross-thread, this substrate's own evidence (the single most load-bearing fact in this note):**
`exp_task_local_normalisation_pool_v1` (ORGAN_MAP C3) already built the LITERAL Chiou/Lambon-Ralph
2018 mechanism — multiplicative per-dimension gain, i.e. exactly "boost the task/context-relevant
feature dimensions" — on this substrate's 256-dim representation, and it **HARD-FAILED**
(HARD_FAIL_GAIN_HURTS, d=-0.0220, CI[-0.034,-0.0097]). Per the 08-23 note's own diagnosis: this failed
for an **estimation-noise reason**, not a wrong-mechanism reason — the dimensions with the largest
anchor-difference (the ones most worth boosting) are also the worst-estimated at ~70 observations per
concept, so boosting them amplifies noise faster than signal. Blocked behind B4 (representation
capacity). **This is exactly consistent with the reported symptom**: the brain-correct control
operation cannot yet do its job on this substrate's current representation, so any one-shot re-weighting
of the existing noisy dimensions — however it's computed — is capped by the same wall, independent of
whether it's done via literal per-dimension gain (already tried, failed) or via the variance-diagnosticity
weighting the current pipeline uses (a different but related reweighting, same underlying representation).

---

## Stage 4 — Predictive coding hierarchy: does a higher (situation/discourse) level set the sense?

**PINNED, canonical microcircuit + equations, general predictive coding (not language-specific).** Rao
& Ballard (1999, *Nat Neurosci* 2:79-87): `O = f(U^(0) X^(0)) + N^(0)` at the lowest level; each higher
level of "causes" X^(l) predicts the level below it, `X^(l) = f(U^(l+1) X^(l+1)) + N^(l+1)`; feedback
(higher->lower) carries predictions, feedforward (lower->higher) carries residual prediction error.
Bastos, Usrey, Adams, Mangun, Fries & Friston (2012, *Neuron* 76:695-711): the canonical cortical
microcircuit maps onto this algebra — prediction errors are computed in **superficial pyramidal cells
(L2/3)**, whose **postsynaptic gain/sensitivity to presynaptic input IS the precision term** (the
formal weight on how much a given error updates belief); predictions are carried top-down from **deep
pyramidal cells (L5/6)** of the higher area into distinct layers of the lower area. This is the most
mechanistic, circuit-level-explicit stage in the whole drill.

**PINNED qualitatively, language-specific, no full equations for word sense.** Kuperberg (2016,
*Cognition*; Kuperberg & Jaeger 2016, *Lang Cogn Neurosci* 31:32-59): a hierarchical generative
architecture in which the comprehender continuously predicts a *message*, generating top-down
probabilistic predictions cascading down through event/situation-model, then lexical, then
orthographic/phonological levels, tested against bottom-up input; N400 amplitude (left ATL, ~300-500ms)
reflects prediction error at the semantic-feature level specifically. Corroborated by graded, cloze-
probability-scaled N400 amplitude (DeLong, Urbach & Kutas 2005, *Nat Neurosci*; 9-lab replication,
Nieuwland et al. 2018, *eLife* — the coarser article/phoneme-level pre-activation claim did NOT
replicate, flagged contested).

**Critical negative finding, fetched full text this pass — the ONLY implemented computational version of
this framework does NOT include a discourse level or sense selection.** Nour Eddine, Brothers, Wang,
Spratling & Kuperberg (2024, *Cognition*), "A Predictive Coding Model of the N400": the actual
implemented model has **four levels only** (orthographic -> lexical -> semantic-feature -> conceptual),
prediction error computed as element-wise `PE = ST oslash tdR` (state divided by top-down
reconstruction), **no explicit variable precision parameter** (fixed connection-strength V-matrix
encodes frequency instead), and **no discourse/situation-model level above the conceptual layer**. Each
lexical item maps to ONE fixed semantic-feature pattern — **there is no mechanism in this model for
representing or selecting among multiple senses of a word.** The authors themselves state this
architecture is "unrealistically shallow." **This means the specific claim "the higher discourse/
situation level sets which sense is selected" has never been formally implemented or tested anywhere in
the literature for word sense** — it is a natural, well-motivated extrapolation from the qualitative
hierarchical-prediction framework, not a demonstrated result. Same conclusion the 08-23 note already
reached from the other direction (Rabovsky/McClelland 2018's model also has no separate precision term
and no sense-selection mechanism); this pass confirms it against the newer, more relevant 2024 model too.

**Verdict for our pipeline:** completely absent (no discourse/situation-model layer exists at all) and
genuinely novel to build for sense selection specifically — but the underlying algebra (Rao-Ballard) is
fully specified and glass-box-implementable without a transformer: a discourse-prior term computable
from entities/events already mentioned (already-built organs: narrative/event-schema machinery per
MEMORY's `verb_role_exemplar_selector`, ATOMIC/ConceptNet-style commonsense edges) could serve as
`log_prior_discourse(sense_i | discourse-so-far)`, added alongside Stage 1's frequency prior.

---

## Stage 5 — Hippocampal/episodic + PFC contributions from prior discourse and world knowledge

**PINNED, but the evidence argues AGAINST hippocampus as the sense-selection bottleneck specifically.**
Schmolck, Stefanacci & Squire (2000, *Hippocampus* 10:759-770), fetched via search-index (title/venue/
authors/pages confirmed): amnesic patients with damage **limited to the hippocampal formation**
performed like controls on both DETECTING sentence ambiguity and EXPLAINING it; patients with **larger
temporal-lobe lesions extending beyond the hippocampus** were impaired to the same degree as classic
patient H.M. **This is a clean dissociation: hippocampus per se is not necessary for lexical/sentence
ambiguity resolution; broader (likely ATL/semantic) temporal cortex is what's doing the work** —
consistent with Stage 2's ATL-hub framing, not a separate hippocampal mechanism.

**PINNED, hippocampus DOES matter for a related but distinct computation: online referential/relational
binding.** Duff & Brown-Schmidt (2012, *Front Hum Neurosci*, review, fetched full text): amnesic
patients show deficits specifically in **flexible referential binding** (e.g., marking a referent as
definite vs. indefinite based on whether it was already established in discourse — controls did this
90% of the time, amnesics near chance at 56%) — a "relational binding" account, not a sense-selection
account. **No experiment anywhere in this review (or found elsewhere this pass) manipulates word-SENSE
ambiguity resolved via prior discourse in amnesic patients** — the gap is honest and real: this specific
question (does hippocampus contribute to *sense* choice, as opposed to *referent* choice, using prior
discourse) has not been directly tested.

**PINNED, mPFC supplies schema-level predictions that are the more plausible upstream source of a
Stage-4 discourse prior.** mPFC encodes schema-congruent expected information and signals event-level
predictions/prediction errors (event-prediction literature, general finding, multiple converging
sources); hippocampus preferentially encodes schema-INCONSISTENT (unexpected) information. This is
consistent with mPFC — not hippocampus — being the better candidate source for the top-down
"situation-model expectation" that Stage 4's predictive-coding hierarchy would need to feed down toward
lexical-semantic processing.

**Verdict for our pipeline:** de-prioritize hippocampal-specific mechanisms; if a Stage-4 discourse
prior is built, frame it as approximating mPFC-style schema/event expectation, not episodic/hippocampal
recall — and flag honestly that no study has tested this for sense selection specifically, matching
Stage 4's own caveat.

---

## Cheap decisive test

Two independent, orthogonal, cheaply-runnable tests, in priority order (both reuse only data already on
disk — no new corpus read):

1. **Discourse-prior arm (Stage 4, the primary novel-synthesis recommendation).** Build
   `log_prior_discourse(sense_i | discourse-so-far)` from entity/event mentions already extracted
   upstream in the pipeline (already-wired narrative/event organs), add it as a third additive term
   beside the existing coherence score and (once built) Stage 1's frequency prior. Bucket the held-out
   sense-selection set by SUBORDINATE vs DOMINANT gold sense (the same split the 08-23 note already
   defines) and separately by whether the discourse-so-far actually contains a diagnostic
   entity/event cue for that item (print this reachability count before reading the verdict, per
   standing discipline — if few items have a usable discourse cue, a flat result is a reachability
   failure, not a refutation).
2. **Representation-sharpening precondition check (Stage 3, confirms or refutes the C3-generalization
   claim in this note's HEADLINE).** Before re-attempting any form of context-driven dimension
   reweighting, measure per-dimension estimation variance specifically on the SUBSET of dimensions that
   differ between the top-2 competing gloss vectors for subordinate-sense items — if those dimensions
   sit in the same high-estimation-noise band C3 already identified, that is direct confirmation this
   note's Stage-3 diagnosis generalizes from C3's original task to sense selection; if not, the C3
   generalization is refuted and the ceiling has a different cause.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Discourse-prior arm (Stage 4):**
- HARD-PASS: subordinate-sense accuracy (a_s) improves over the coherence(+frequency-prior) baseline by
  a CI-separated margin of >=10 percentage points specifically on items WITH a usable discourse cue
  (per the reachability count above), with no more than a 3pp regression on items without one.
- HARD-FAIL: no CI-separated gain on cue-bearing items, OR gain is uniform regardless of cue presence
  (meaning the term is adding noise/generic lift, not the hypothesized discourse-conditioned signal).
  On HARD-FAIL: this specifically refutes the Stage-4 discourse-prior hypothesis as this note frames
  it — redirect to Stage 2 (grounded-feature gap) as the next candidate, not to abandoning the
  hierarchical-prediction idea altogether.

**Representation-sharpening precondition check (Stage 3 generalization):**
- HARD-PASS: the discriminating dimensions for subordinate-sense pairs show estimation variance in the
  same high band C3 flagged (a directly comparable per-dimension variance statistic, not just "noisy").
- HARD-FAIL: discriminating dimensions are well-estimated (low variance) — in that case the C3 finding
  does NOT generalize to this task, and the a_s~0.31 ceiling has a cause independent of representation
  capacity (e.g. genuinely wrong Stage-3 operation, not a noise-blocked correct one) — re-open the
  question of whether the current variance-diagnosticity weighting is even attempting the right
  computation.

---

## Cross-thread synthesis (this substrate's own prior work)

- `notes/research_wsd_context_conditioned_sense_selection_2026-08-23.md` — origin of the frequency-prior
  recommendation (Stage 1 here); this note's contribution is showing that recommendation targets a
  different error pattern than the subordinate-sense-specific ceiling this problem reports, and should
  be built as a SEPARATE, independently-evaluated fix, not treated as the solution to this ceiling.
- `notes/research_channel_combination_reliability_weighting_2026-08-23.md` — origin of the grounded-
  spoke/concreteness-gating findings (Stage 2 here); confirmed, not re-litigated, in this pass.
- `notes/problems/no_glass_box_verb_sense_disambiguation/research_brain_foundational_verb_sense_2026-08-28.md`
  — adjacent problem (verb-noun joint scoring, construction mappings); shares the CSC/control-network
  background but is architecturally distinct (joint two-word scoring vs. single-word discourse-prior).
- `exp_task_local_normalisation_pool_v1` / ORGAN_MAP C3 — **the single most load-bearing fact in this
  note**: literal brain mechanism already tried, failed for a diagnosed representational-capacity
  reason, blocked behind B4. This note's contribution is arguing this same wall plausibly explains the
  subordinate-sense ceiling here too (test 2 above checks this directly) and that Stage 4's discourse
  prior is a way to get control's functional benefit WITHOUT re-hitting B4.
- ORGAN_MAP C4 (attractor settling not recommended) and the McClelland (2013) equivalence proof — this
  note adds the Shahdloo/Çelik/Çukur semantic-domain fMRI confirmation that a well-calibrated one-shot
  weighted score CAN match settled biased-competition output, reinforcing that "iterative settling
  collapsed to one-shot" is likely not, by itself, the fundamental gap.

## Substrate-product implications

Two concrete, ranked, buildable next steps, both glass-box and transformer-free: (1) build and
separately evaluate Stage 1's frequency-prior term (cheap, well-pinned, but expect it to help
dominant-congruent items, not fix the subordinate-sense ceiling — report this expectation explicitly so
a small/negative subordinate-item result there is not mis-read as refuting the whole prior-x-likelihood
framework); (2) run the representation-sharpening precondition check before investing further in any
context-driven reweighting mechanism — if confirmed, the honest message to the owner is "the control
operation is right, the representation underneath it is not sharp enough yet, this is a B4 problem
wearing a Stage-3 costume"; if refuted, build the Stage-4 discourse-prior term instead, understanding
it as genuine novel synthesis (P<=0.50) with no direct precedent, using organs already on the
substrate (narrative/event-schema extraction) rather than any new external model.

## Citations (verified count)

**19 distinct primary sources**, all checked live this pass via WebSearch/WebFetch (not from memory),
several with full-text fetch (marked FT): Swinney 1979; Klepousniotou 2002; Klepousniotou, Pike,
Steinhauer & Gracco 2012; Duffy, Morris & Rayner 1988; Binder & Rayner 1998; Mollo, Jefferies,
Cornelissen & Gennari 2018 (FT, PMC5840520); Lambon Ralph, Jefferies, Patterson & Rogers 2017; Bruni,
Tran & Baroni 2014; Andrews, Vigliocco & Vinson 2009; Chiou, Humphreys, Jung & Lambon Ralph 2018;
Hoffman, McClelland & Lambon Ralph 2018; Jackson, Rogers & Lambon Ralph 2020; Badre & Wagner 2002/2005;
Noonan, Jefferies et al. 2010/2013; Desimone & Duncan 1995; Reynolds, Chelazzi & Desimone 1999; Chelazzi,
Miller, Duncan & Desimone 1993/1998; Shahdloo, Çelik & Çukur (bioRxiv 658096, FT); Rao & Ballard 1999;
Bastos, Usrey, Adams, Mangun, Fries & Friston 2012; Kuperberg 2016 / Kuperberg & Jaeger 2016; DeLong,
Urbach & Kutas 2005; Nieuwland et al. 2018; Nour Eddine, Brothers, Wang, Spratling & Kuperberg 2024 (FT,
PMC10984641); Schmolck, Stefanacci & Squire 2000; Duff & Brown-Schmidt 2012 (FT, PMC3319917). Bibliographic
identity (author/year/venue/pages) confirmed via multi-index convergence for all; mechanism/equation
detail confirmed against actual fetched full text (not snippet-only) for the seven marked FT above —
those are the highest-confidence claims in this note, especially the two negative findings (Nour Eddine
2024's shallow 4-level model with no sense mechanism; Shahdloo's one-shot-suffices semantic fMRI result)
since negative/limiting findings are the ones most likely to be over-claimed from a snippet alone.

Per lit-scan calibration discipline: all P estimates above deflated 0.15-0.25 from raw synthesis
confidence; the Stage-4 discourse-prior recommendation, being pure novel synthesis with zero direct
precedent for sense selection, is capped at P<=0.50 and stated as such throughout.
