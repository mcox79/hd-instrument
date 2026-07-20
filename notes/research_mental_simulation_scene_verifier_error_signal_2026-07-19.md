# BRAIN-DRILL (5x, scope-elevated mid-drill): mental-simulation SCENE as VERIFIER/ERROR-SIGNAL for reading comprehension

**Date:** 2026-07-19. **Filed by:** research (5 parallel Sonnet lit-scans + director synthesis). **Trigger:**
USER's original insight (humans build a simplified mental picture that carries plausibility for who-did-what)
elevated mid-drill by a USER scope-sharpen: **the picture is not just a representation, it is a VERIFIER — "if
I imagine something and it's ridiculous, obviously I read it wrong... the image has to make sense and then I
basically have the sentence and move on."** This makes the CENTRAL question of this note: does scene-level
coherence-checking function as (1) a parse-SELECTOR and (2) a genuine SELF-SUPERVISED TRAINING SIGNAL — the
missing learning signal this whole session's world-knowledge residual has been circling — with no gold labels?

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature-agreement;
novel-synthesis capped at P<=0.50 per [[feedback-lit-scan-calibration-penalty]]). Established-lit findings are
confidence-flagged per source (established / contested / this-is-inference), not blanket-deflated — deflation
applies to this note's OWN synthesis claims, not to replicated primary literature.

**Composes with, does not re-derive:** `research_animacy_vs_worldknowledge_residual_brain_drill_2026-07-19.md`
(atom 29357 — discrete animacy filter escaped the cosine wall for SELECTION but gave ZERO training signal,
capped net-neutral); `research_argument_adjunct_subcat_hard_residual_brain_drill_2026-07-19.md` (atom 29350 —
build/huts vs build/stream residual diagnosed as needing PER-INSTANCE structural parse, not per-verb aggregate
frequency); `research_situation_model_guided_comprehension_loop_compress_and_carry_2026-07-19.md` (Working
Situation Model, Zwaan's 5-dimension event-indexing tiers); `research_fork_c_compounding_end_to_end_substrate_loop_2026-07-19.md`
(fixed-operator/learned-policy loop, event-segmentation/consolidation); the two structured-carry HARD_FAILs
(atoms 29339 CCL topical, 29353 structured-FHRR patient-prior) that carried the WRONG thing ACROSS sentences.
**This note's mechanism is deliberately WITHIN-sentence (candidate-parse-vs-candidate-parse), not a carry across
sentences/documents — it is not a third attempt at the same failed cross-sentence mechanism.**

---

## HEADLINE

**Two separable claims, honestly graded differently. (I) The "simplified scene" itself is buildable from
LEARNED CONCEPTUAL ATTRIBUTES — WordNet noun-supersenses + VerbNet-style discrete selectional-restriction
features — with NO perceptual/pixel input; this is well-supported by convergent literatures (grounded-cognition,
psycholinguistics, computational-linguistics) and is not a novel proposal, it is assembling two mature
off-the-shelf symbolic resources. Deflated P=0.45. (II) THE CENTRAL, NEW CLAIM — that a scene-coherence check
can do DOUBLE DUTY as both parse-selector AND self-supervised training signal — is THEORETICALLY well-grounded
(predictive coding's inference/learning double-duty is a mainstream, textbook claim, not a fringe extension)
and has ONE strong direct brain-level analog (a graded meaning-level prediction-error signal, the N400,
demonstrably functions as an implicit-learning signal, Hodapp & Rabovsky 2021) — but the EXACT combination this
project needs (semantic/scene-plausibility computed over rival PARSES of the same sentence, used as a
CONTRASTIVE training signal for a symbolic parser's cue-weights) is NOT directly demonstrated anywhere in the
literature scanned. This is a genuinely open, unprecedented, well-motivated hypothesis, not an established
fact. Deflated P=0.35, capped below the general novel-synthesis ceiling because it composes two literatures
(implicit-memory-from-N400 and structural-syntactic-adaptation-from-surprisal) that have never been shown to
be the same mechanism.**

**The crucial DESIGN finding, from the machine-learning half of the scan, is not about gradedness vs
discreteness at all — it is about CONTRAST.** ML self-training/energy-based/weakly-supervised-parsing
literature converges on: a judgment (graded OR discrete) becomes a usable training signal only when applied
DIFFERENTIALLY across >=2 competing candidate outputs for the same input, routed through a margin/
cross-entropy/expected-reward mechanism. This directly diagnoses why this session's two prior signals landed
where they did: the cosine score was graded but was never shown to be embedded in a candidate-vs-candidate
contrast (it was applied as a single blended score, not a comparison); the animacy filter was discrete AND
applied per-candidate, but only as a PRE-FILTER (removing a candidate before scoring) rather than a
differential judgment that varies a downstream score across surviving candidates — which is exactly why it
filtered but never trained anything (fixed_ON=0, atom 29357). **The design implication: the missing ingredient
in both prior attempts was not the signal's graded/discrete nature, it was the absence of a same-sentence,
candidate-vs-candidate CONTRAST.** A scene-coherence check that scores BOTH rival parses of one ambiguous
sentence and uses the GAP between them is architecturally different from both prior attempts, not a
retry of either.

---

## Ranked verdict (viability ladder)

1. **Attribute-scene buildability (Part I): STRONG, established, not novel.** WordNet noun-supersenses
   (~26 categories: `noun.artifact`, `noun.location`, `noun.person`, `noun.animal`, `noun.substance`, etc.)
   plus VerbNet's existing binary selectional-restriction features per verb-argument slot (`+animate`,
   `+concrete`, `+location`, `-region`, `+organization`) already ENCODE almost exactly the place/object/
   animate/container/typical-location attribute set the task asked about. This is off-the-shelf, mature,
   symbolic, glass-box, zero-pixel. Confidence: high that this is buildable; medium-high (Mechura 2010,
   Erk 2007) that it will have real coverage/granularity gaps that need honest triage, not silent
   assumption of full coverage.
2. **Is the scene perceptual or conceptual (the acquisition crux): CONCEPTUAL, moderate-strong convergent
   support.** Riordan & Jones (2011) show distributional/text-only models are substantially REDUNDANT with
   perceptual/feature-norm models for category-level semantic structure. Louwerse's Symbol Interdependency
   Hypothesis and its "linguistic processes precede perceptual simulation" finding show statistical/symbolic
   processing operates FIRST, with perceptual simulation reserved for slower/deeper tasks — real-time
   lexical/referential disambiguation of the kind this project needs is closer to the "shallow/fast" end.
   Dual-coding theory's 50-year-old finding that abstract/categorical content is verbal-channel-only (not
   imagistic) supports the same conclusion for exactly the KIND of fact this scene needs (is-a-place,
   is-a-container — categorical/relational facts, not concrete perceptual images). Congenitally-blind
   comprehension of visual-metaphor language (equal to sighted controls) is a genuine natural experiment
   showing modality-specific perceptual grounding is NOT required for this class of comprehension.
   Confidence: medium-high — no study ran the exact head-to-head test needed, so this is convergent
   indirect evidence, not a single decisive study.
3. **Scene-level coherence-checking as a real brain mechanism (Angle A): STRONG for the checking itself,
   UNRESOLVED for how it unifies across grain-sizes.** Kuperberg's account of the semantic-P600 (conflict
   between thematic-role/event-structure assignment and the syntactic parse, amplitude scaling with
   reassignment difficulty) is the best existing bridge from "word-level ERP" to "does the constructed EVENT
   make sense" — established as a specific, credentialed theory (rival accounts exist). Separately, the
   comprehension-monitoring/memory-resonance literature (van den Broek, O'Brien, Rapp — "standards of
   coherence") shows genuinely SCENE/SITUATION-level inconsistency detection (relative to the situation model
   built from prior discourse, not local syntax) with real reading-time signatures. **Neither literature has
   been unified with the other, nor with garden-path P600 reanalysis, into one mechanism** — this is a real,
   flagged literature gap, not a search failure.
4. **Commit-vs-reanalyze decision (Angle C): a genuine open question, well-populated with partial pieces,
   no formalized threshold.** Ferreira's good-enough/satisficing processing is the best-developed account:
   comprehenders stop when a representation is sufficient for the task, NOT when fully verified — and,
   importantly, REVISION IS PARTIAL not total (lingering-misinterpretation effects: people retain traces of
   the discarded reading even after "correctly" reanalyzing). Constraint-based competition models (Trueswell/
   Tanenhaus/MacDonald) give a natural graded-race-to-threshold substrate. **No paper found gives an explicit
   quantitative "coherence score must clear X to commit" rule** — this maps directly onto the project's own
   existing margin-gated-abstain discipline (already used for coref) as the SAME kind of open engineering
   choice the literature hasn't resolved either, which is at least reassuring: the project isn't missing a
   known answer, it's in the same genuinely-unsolved space as the primary literature.
5. **THE CENTRAL CLAIM — scene-coherence as self-supervised training signal (Angle B): well-grounded
   theoretically, ONE strong direct analog, NOT directly demonstrated in combination. Deflated P=0.35 (capped
   below the general 0.50 ceiling — see HEADLINE).** Predictive coding (Rao & Ballard 1999; Friston's
   free-energy principle) makes inference (fast, settles the current interpretive state) and learning (slow,
   updates the generative model's parameters) literally the SAME error-minimization process at different
   timescales — established, mainstream, not an extension (though the precise gating of "how big an error
   also updates weights" is contested). Hodapp & Rabovsky (2021) is the single sharpest brain-level analog: a
   GRADED meaning-level prediction-error signal (N400 amplitude) computed for real-time comprehension ALSO
   functions as an implicit-learning signal (bigger N400 predicts better later implicit memory, gradedly) —
   direct evidence that an online semantic-plausibility-mismatch signal does double duty. Syntactic priming/
   error-driven adaptation (Chang, Dell & Bock 2006; Jaeger & Snider 2013) is real, replicated evidence that
   parsing PREFERENCES adapt within-session from a processing-outcome error signal — but that signal is
   SURPRISAL/distributional-frequency-based, not semantic-scene-plausibility-based; this is the extrapolation
   gap the project's hypothesis needs to cross, and no paper directly crosses it. On the ML side, weakly-
   supervised semantic parsing (Liang et al.; Neural Symbolic Machines; MAPO) is direct existence-proof that a
   DISCRETE correctness signal (did the parse's execution produce the right denotation?) CAN train a symbolic
   parser via policy-gradient/REINFORCE, with no gold parse trees — provided it compares across multiple
   candidate parses per input. **Overall: the hypothesis is coherent, brain-consistent, and has real partial
   precedent on both the neuroscience and ML sides — but the specific combination has never been tested. This
   is the honest, most valuable finding of this drill: a real, non-trivial, testable NEW hypothesis, not a
   confirmed mechanism.**

---

## Angle-by-angle findings (credited, confidence-flagged)

### Angle 1 — Perceptual simulation in comprehension
Zwaan's Immersed Experiencer Framework (Zwaan 2004; Zwaan & Madden 2005; Stanfield & Zwaan 2001, *Psych.
Science*; Yaxley & Zwaan 2007, *Cognition*) shows comprehenders simulate perceptual detail (orientation,
shape, distance, visibility) SELECTIVELY — only when relevant to the discourse goal, not exhaustively — which
is itself supportive of the "simplified, not full-imagery" framing this project wants. Barsalou's Perceptual
Symbol Systems (1999, *BBS*; 2008, *Annu. Rev. Psychol.*) is the strongest theoretical claim for perceptual
grounding but remains contested (Mahon & Caramazza 2008 argue the same evidence is equally consistent with an
amodal system with downstream spreading activation to sensorimotor cortex — i.e., perceptual activity as
EPIPHENOMENON, not cause). Johnson-Laird's mental models (1983) is notably closer to this project's "discrete
structured scene" framing than Barsalou's rich perceptual simulation — his models are built from propositional
input via semantic procedures and represent entities/types/relations, reasoning by manipulating/enumerating the
model, not necessarily perceptual content. **Necessity vs. accompaniment: genuinely contested.** Aphantasia
data are mixed: no gross comprehension deficit is reported generally, but at least one study line found
aphantasics selectively impaired on DEEP/inferential contextual word selection (not surface comprehension) —
suggestive that imagery contributes something beyond floor-level parsing, but does not show necessity, since
aphantasics remain far above floor. Visual-interference (dynamic visual noise) studies on the classic
shape-match paradigm are directly contradictory across studies found (some show disruption, some don't) —
flagged as needing primary-source verification, not resolved in this scan.

### Angle 2 — Spatial/event structure
The vision "what/where" (Ungerleider & Mishkin 1982) and its "what/how" reframing (Goodale & Milner 1992) do
NOT have a clean, established analog in language comprehension — the language dual-stream literature that
exists (Hickok & Poeppel 2004/2007; Saur et al. 2008) maps onto comprehension-vs-articulation or syntax-vs-
semantics, not place-content-vs-object-content. Treating the vision what/where split as licensing a discrete
place-vs-object channel in sentence semantics would be an OVER-EXTENSION — flagged as a fairly confident
negative finding. Lakoff & Johnson's image schemas (CONTAINER, PATH, SOURCE-PATH-GOAL, SUPPORT) give a
principled small inventory of discrete spatial primitives, but the empirical support (Gibbs & Colston 1995) is
mostly linguistic-analytic (corpus/introspective), not tightly-controlled online-processing evidence for
argument-structure disambiguation specifically. **The single most useful, underexploited finding in this
angle:** Ferretti, McRae & Hatherell (2001) found verbs prime typical agents/patients/instruments via fast
single-word priming but NOT typical locations (a null result); Hare, Jones, Thomson, Kelly & McRae (2009)
found the REVERSE direction works — location nouns prime the entities typically found there (hospital→doctor).
This asymmetry suggests LOCATION knowledge may be organized more like a discrete frame/scene lookup than like
smoothly-graded verb-argument thematic fit — directly relevant to the build/huts-vs-build/stream residual,
since that residual IS a location-vs-artifact typing question. Flagged clearly: this specific synthesis is
this scan's own inference, not a claim the primary authors make. The dominant McRae/Ferretti/Elman event-
knowledge program is otherwise established and GRADED (continuous typicality, graded N400 modulation) as its
default framing — a purely discrete system would likely under-fit that well-established graded data, but the
location-specific asymmetry is a genuine, targeted exception worth exploiting for exactly this residual class.
SemEval Spatial Role Labeling (Kordjamshidi et al. 2012/2013) and Region Connection Calculus (Randell, Cui &
Cohn 1992) give a working discrete category inventory (Trajector/Landmark/topological relation) as an
NLP-engineering existence-proof, not psycholinguistic evidence of human processing.

### Angle 3 — Acquisition/grounding crux
Covered in ranked-verdict item 2 above. Key added citations: Paivio (1971, dual-coding, concrete words get
both verbal+imagery channels, abstract words verbal-only); Louwerse (2011, *Topics in Cog. Sci.*; 2012,
*Frontiers in Psych.*, "linguistic processes precede perceptual simulation"); Riordan & Jones (2011, *Topics
in Cog. Sci.*, redundancy of distributional and perceptual/feature-norm models); congenitally-blind
visual-metaphor comprehension study (*Frontiers in Psychology*, 2018). No study directly ran the
attribute-lookup-vs-perceptual-simulation head-to-head test on this exact ambiguity class — this remains
a real, honestly-flagged gap, not a settled fact.

### Angle 4 — Computational implementations, cheapest buildable scene
Schank & Abelson's scripts (1977, implemented as SAM) are the direct historical precedent for exactly this
idea — a hand-built discrete scene from text, used for disambiguation; documented failure mode is
COVERAGE/AUTHORING COST (script brittleness), NOT insufficient perception — an important, reassuring
precedent (the known failure mode of this approach is a corpus/engineering-scale problem, matching this
session's dominant meta-finding, not a fundamental representational gap). Gupta et al. (2017, ACL, "Ontology-
Aware Token Embeddings for PP-Attachment") is the closest quantified positive case: injecting discrete WordNet
synset structure gave +5.4% absolute (34.4% relative error reduction) on PP-attachment — but this is a HYBRID
(discrete ontology signal + distributional model), not proof discrete-alone beats graded-alone. Erk (2007)
and Agirre & Martinez found distributional similarity models actually beat Resnik's WordNet-class model on
raw accuracy for selectional-preference acquisition (coverage advantage) — a real, honest counter-data-point
against assuming discrete-always-wins. Mechura (2010, Euralex) documents a real, citable granularity-mismatch
failure: WordNet categories often don't align with attested selectional preferences (no clean category for
"cancelable event nouns"). VerbNet ALREADY implements almost exactly the requested attribute scheme (`+animate`,
`+concrete`, `+location`, `-region`, per verb-class argument slot) — this is a mature existing resource, not a
build-from-scratch task. **Cheapest buildable scene: WordNet noun-supersense lookup (~26 categories) +
VerbNet's existing selectional-restriction features, as a hard set-membership check per verb-argument slot —
architecturally identical to how the animacy filter already works, extended to place/object/container/
location categories.** Honest bound: coverage/granularity mismatch (Mechura, Erk), not a documented
perceptual-grounding requirement — no source found proves attribute-lookup provably fails where perceptual
grounding provably succeeds for this task class; that risk is a theoretical caution (from the broader
embodied-cognition critique of amodal symbol systems), not a demonstrated empirical bound.

### Angle A — Scene-level coherence detection mechanism (the verifier's "how")
Covered in ranked-verdict item 3. Additional detail: purely semantic violations with NO syntactic ambiguity
can elicit a P600 with no N400 (the contested "semantic P600"/"semantic illusion" literature) — Kuperberg's
account treats this as conflict between parallel syntactic/semantic/thematic streams, with P600 amplitude
tracking reassignment difficulty; this is the best existing theoretical bridge between "word doesn't fit"
(N400) and "the whole EVENT doesn't hold together" (semantic P600), though rival accounts of the semantic-P600
exist and it remains an actively contested phenomenon, not settled. Johnson-Laird's account of reasoning
errors (failure to search for alternative models/counterexamples) is established for DEDUCTIVE reasoning; this
scan could NOT verify from primary text (a scanned/uncooperative PDF) whether he gives an explicit
comprehension-specific (not just syllogism-specific) account of "first model fails, build a second" — flagged
as unverified, not claimed.

### Angle B — THE CENTRAL CLAIM: self-supervised training signal (the verifier's "does it teach")
Covered in ranked-verdict item 5, the HEADLINE, and the design table below. Additional detail on the
discreteness-vs-gradedness resolution: hinge/margin loss, noise-contrastive estimation, and REINFORCE-over-
binary-reward all show that a DISCRETE judgment can drive learning, provided it is applied differentially
across >=2 candidates for the same input and routed through a contrast-sensitive update rule. This directly
explains, post-hoc, why this session's animacy filter (discrete, but a PRE-filter with no per-candidate
differential score) gave zero training signal (fixed_ON=0, atom 29357) while still being a genuinely different
kind of signal from the graded cosine that also failed (which was graded but not shown to be embedded in a
candidate-vs-candidate contrast either). **Neither prior failure is explained by "wrong on the graded/discrete
axis" — both are explained by "no candidate-vs-candidate contrastive structure."** This reframes the entire
session's structural-beats-semantic pattern one level deeper: the operative variable for TRAINABILITY is
contrast-structure, not discreteness; discreteness was merely what made the SELECTION half of animacy work.

### Angle C — Commit-vs-reanalyze decision
Covered in ranked-verdict item 4.

### Angle 5 — Structural verdict, synthesis (this drill's own contribution, capped P=0.35-0.45 per component)
See HEADLINE and ranked-verdict items 1-5.

---

## Design: human cue -> HD/substrate operation mapping

| Human cue (angle evidence) | HD-substrate operation |
|---|---|
| WordNet supersense + VerbNet selectional features already encode place/object/animate/container/location as discrete categories (Angle 3/4) | Per-NP-head discrete attribute lookup table (glass-box, zero-pixel), same architectural slot the animacy filter already occupies |
| Location information behaves as a discrete frame/scene lookup, distinct from graded verb-argument thematic fit (Ferretti/Hatherell null vs. Hare et al. positive, Angle 2) | Prioritize the LOCATION-vs-ARTIFACT typing (noun.location vs noun.artifact/noun.substance supersense) as the FIRST scene-attribute check — directly targets the build/huts vs build/stream residual, which atom 29350 already diagnosed as needing PER-INSTANCE structural typing |
| Semantic-P600 = conflict between thematic-role assignment and syntax, graded with reassignment difficulty (Kuperberg, Angle A) | Per-candidate-parse discrete coherence bit = does the candidate filler's attribute TYPE match the verb's VerbNet-class selectional-restriction slot? Computed per rival candidate, not blended into one score |
| Predictive coding: same error signal drives fast state-inference (selection) and slow parameter-learning (Rao & Ballard; Friston, Angle B) | The SAME per-candidate coherence bit is read twice: (1) at commit-time, pick the coherent candidate (selector); (2) logged as a training example for the LCCP's cue-weights (learner) |
| ML: a judgment (graded or discrete) trains only when applied differentially across >=2 candidates + routed through a contrast-sensitive update (hinge/margin, NCE, REINFORCE; Angle B) | Score BOTH rival parses of the same ambiguous sentence for scene-coherence; use the GAP (exactly-one-coherent cases) as a margin-style perceptron update to the LCCP's cue weights — self-supervised, no gold labels |
| Good-enough processing: commit when sufficient, not when fully verified; revision is partial, not total (Ferreira, Angle C) | Reuse the existing margin-gated-abstain discipline (already built for coref): commit only when exactly one candidate clears the coherence check; abstain (no selection, no weight update) when both or neither do — avoids training on uninformative ties |
| Script/frame brittleness (Schank & Abelson SAM, Angle 4) is a coverage/authoring-cost failure, not a perceptual-grounding failure | Honest risk register: expect silent gaps (missing WordNet/VerbNet coverage for this corpus's specific nouns/verbs) — triage as a corpus-coverage issue, not grounds to abandon the attribute-lookup approach |

---

## First buildable component

**Scene-Coherence Verifier (SCV): a per-sentence, per-candidate-parse discrete TYPE-CONSISTENCY check between
a verb's VerbNet-class selectional-restriction slot and a candidate filler's WordNet-supersense/VerbNet-feature
type, computed CONTRASTIVELY across the LCCP's existing rival-candidate generation step for hard-attachment
cases — used BOTH as a margin-gated selector (mirrors the coref design's existing commit/abstain discipline)
AND as a self-supervised training signal for the LCCP's own cue-weights (margin/perceptron-style update, no
gold labels).**

Concretely, scoped first to the build/huts vs build/stream class (chosen because it is the exact residual
atom 29350 already diagnosed as needing PER-INSTANCE structural typing rather than per-verb aggregate
frequency, and because Angle 2's location-priming asymmetry independently supports treating location-typing
as a discrete/frame-like lookup rather than a graded score):

1. For each hard-attachment case, the LCCP already proposes >=2 rival structures (e.g., candidate A: filler is
   the direct-object PATIENT/THEME; candidate B: filler heads a locative PP ADJUNCT). No new candidate
   generation is required — this reuses existing machinery.
2. Look up the verb's VerbNet class selectional-restriction for the PATIENT/THEME slot (e.g., `build`-class:
   THEME[+concrete, +artifact, -location]) and the ADJUNCT/locative slot's implicit restriction
   ([+location] or [-region] for a directional/locative reading).
3. Look up each candidate filler's own WordNet noun-supersense (e.g., "hut" -> `noun.artifact`; "stream" ->
   `noun.location`, plausibly `noun.object`/`noun.substance` depending on synset).
4. Score each candidate a discrete coherence bit: TYPE-MATCH (slot restriction satisfied) = 1, MISMATCH = 0.
5. **Selector use:** if exactly one candidate scores 1 and the other 0, commit to the coherent one (mirrors
   the coref design's margin-gated commit). If both or neither score 1, ABSTAIN (no selection made) — do not
   force a choice on an uninformative case.
6. **Training-signal use:** on the SAME exactly-one-coherent cases, log which of the LCCP's existing cue
   weights (word-order, animacy, preposition-cue, etc.) FAVORED the coherent candidate vs. the incoherent
   one, and apply a small margin/perceptron-style update: increase weights that favored the coherent
   candidate, decrease weights that favored the incoherent one. This runs over RAW, UNLABELED text (the
   already-staged ~99k-word McGuffey corpus, per the cron-tick discovery noted in the compaction backup) — no
   gold parses needed, since the "label" is internally generated by the coherence check itself.

This is architecturally NEW relative to both prior carry attempts (CCL topical, structured-FHRR patient-prior)
— it operates WITHIN one sentence's rival candidate parses, not across sentences/documents, and it is
explicitly contrastive (scores >=2 rivals differentially) rather than a single blended or filtered score.

---

## Cheap decisive test / design-gated can-fail

Real baseline = current LCCP reader (~0.557 precision, no scene-coherence check). One variable changes per
prediction (per [[feedback-experiment-design-gate-can-fail-real-baseline-difficulty-on]]). Three predictions,
triaged separately so a failure on one does not contaminate interpretation of the others (mirrors the parser
and animacy drills' own triage discipline).

**Prediction 1 (selector, on the location-vs-artifact residual sub-slice — the best-precedented claim).**
P=0.45 (deflated). **HARD-PASS:** on the triaged subset of the parser's coherent-but-wrong residual that is
specifically a location-vs-artifact typing case (reusing the parser drill's own Step-1 triage to isolate this
subset from the argument-structure-frequency-driven subset already identified as needing a different fix),
the SCV's exactly-one-coherent commit rule resolves a majority of these cases correctly, with a break-budget
no worse than broken<=fixed (help-not-hurt), measured against independent gold. **HARD-FAIL:** net breakage
exceeds net fixes on this subset, or the subset is near-empty after triage (which would CONFIRM, not
contradict, atom 29350's own diagnosis that this residual is dominated by argument-structure/frequency
factors, not entity-type factors) — an informative, expected-possible negative either way.

**Prediction 2 (self-supervised training signal — THE CENTRAL, NOVEL claim). P=0.35 (deflated, capped below
the general 0.50 ceiling given this is an untested combination of two literatures never shown to be the same
mechanism).** **HARD-PASS:** running the margin-style cue-weight update over the exactly-one-coherent cases
mined from the ~99k-word raw McGuffey corpus (no gold used in the update) measurably moves the LCCP's learned
cue-weights in a direction that INCREASES held-out precision relative to a frozen-weight control, on an
independent gold slice never touched by the update. **HARD-FAIL:** weight movement is null, noisy, or
net-negative on held-out precision. If HARD-FAIL: run the corpus-size ablation (99k words vs. the original
163-sentence gold slice) before concluding the mechanism itself is null — per this session's own recently-fired
decisive test (cron-tick 20:34Z), sparsity-masquerading-as-mechanism-failure is a live, real risk pattern this
exact arc has already caught once (per-verb stats, animacy classifier) and must be ruled out before treating
Prediction 2's failure as final.

**Prediction 3 (parser-residual scope check — pre-registered low-cost sanity check).** P=0.30 (deflated,
explicitly low). **HARD-PASS:** after Prediction 1's triage, the location-vs-artifact sub-bucket is
non-trivial in size (not near-empty) — confirming this residual slice is real and worth the build.
**HARD-FAIL:** the sub-bucket is near-empty — this would not contradict Prediction 2's training-signal test
in principle (which can still be validated on other ambiguous-attachment classes covered by VerbNet/WordNet
type-mismatches), but would mean the FIRST target (build/huts class specifically) was too narrow a pilot;
broaden to any VerbNet-class selectional-restriction mismatch, not just the build-class locative/artifact
split.

**Cross-check (both-ways can-fail, explicit).** If 1 passes and 2 passes: this is the strongest possible
outcome this session has produced — a discrete, glass-box, contrastive scene-coherence check that BOTH
resolves a chunk of the world-knowledge residual AND supplies the missing self-supervised training signal, with
no gold labels and no perceptual grounding. If 1 passes but 2 fails: the SCV is a genuine, real, bounded
SELECTOR win (like animacy) — bank it as that, and treat "coherence-as-training-signal" as still open,
distinguishing corpus-sparsity from mechanism-failure per Prediction 2's own fallback. If 1 fails but 2
somehow shows signal on a broader ambiguity class: re-scope the selector claim narrower, keep the
training-signal result. If both fail (and the corpus-size ablation rules out sparsity): the honest bound is
that discrete VerbNet/WordNet typing is too coarse for this corpus's specific verbs (Mechura's granularity-
mismatch risk materializing) and/or that the predictive-coding double-duty claim does not transfer, as-is,
from a continuous-neural-network gradient setting to this discrete/symbolic setting — a real, informative,
structural negative, distinguishing "the idea was wrong" from "the resources were too coarse."

---

## Cross-thread synthesis

Directly extends the animacy drill (atom 29357): that drill's own honest limitation — a discrete filter that
worked for selection but gave literally zero training signal (fixed_ON=0) because it never varied a score
across surviving candidates — is EXACTLY the gap this note's contrastive design closes; this is not
independent new territory, it is the animacy drill's own unresolved edge, now addressed. Directly extends the
parser drill (atom 29350): that drill's own conclusion — the residual needs a PER-INSTANCE structural parse,
not per-verb aggregate frequency, and named this as "the deeper-parser fork" — is precisely what the SCV's
per-instance, per-candidate type-check supplies; this note is the concrete design for that named-but-undesigned
fork. Deliberately distinct from both failed carry attempts (CCL topical, atom 29339; structured-FHRR
patient-prior, atom 29353): those carried information ACROSS sentences and got the direction of the cue wrong
(rewarding topical/patient continuity that narrative actively violates); this note's mechanism never crosses a
sentence boundary — it compares rival readings of the SAME sentence, sidestepping the cross-sentence carry
problem entirely. Composes with, without re-deriving, the Working Situation Model note's Zwaan 5-dimension
tiers and the FORK-C note's fixed-operator/learned-policy framing: this note's SCV is best understood as a
LOCAL, sentence-internal instance of the "learned-policy" layer FORK-C already recommends keeping all learning
in (never the binding operator, always the selection/scoring policy) — it is a new, concrete instantiation of
that policy layer, not a competing architecture.

---

## Substrate-product implications

If Prediction 1 and 2 both pass: this becomes the first component in this entire arc where a WORLD-KNOWLEDGE
signal is simultaneously a product feature (disambiguation) and a training mechanism (self-improvement from
raw text, no annotation cost) — directly serving the PIVOT's "runtime autonomous grounding" thrust and the
"learned, self-improving reader, not frozen hand-rules" directive, using only existing symbolic resources
(WordNet, VerbNet) with no external LLM at runtime and no pixels. If only Prediction 1 passes: still a real,
bounded, glass-box disambiguation win, cheap to ship, in the same family as the animacy filter (extends the
project's inventory of discrete pre-filters). If only Prediction 2 shows signal on a broader class: the
finding generalizes past this specific residual and should redirect design effort toward whichever ambiguity
class the discrete type-mismatch signal is richest for (VerbNet coverage permitting) rather than this specific
build-class pilot. If both fail even after the sparsity ablation: this is a genuine, hard-won structural
result — it would mean this project's residual needs either a richer non-lookup-based world-knowledge source
(the previously-flagged commonsense-KB investment) or that self-supervised learning from an internal coherence
check genuinely does not transfer from the neuroscience/ML precedents at this scale — either way, worth
knowing before further investment in this specific mechanism-class.

---

## Citations (verified count)

Distinct sources cited across the 5 lit-scans, credited by name: Zwaan (2004; & Madden 2005); Stanfield & Zwaan
(2001); Zwaan, Stanfield & Yaxley (2002); Yaxley & Zwaan (2007); Barsalou (1999; 2008); Mahon & Caramazza
(2008); Johnson-Laird (1983; & Byrne 1991); Paivio (1971); Louwerse (2011; 2012; 2018); Riordan & Jones (2011);
congenitally-blind visual-metaphor study (Frontiers in Psychology, 2018); Ungerleider & Mishkin (1982); Goodale
& Milner (1992); Hickok & Poeppel (2004; 2007); Saur et al. (2008); Lakoff (1987); Johnson (1987); Gibbs &
Colston (1995); Hampe ed. (2005); McRae, Spivey-Knowlton & Tanenhaus (1998); Ferretti, McRae & Hatherell
(2001); Hare, Jones, Thomson, Kelly & McRae (2009); McRae & Matsuki (2009); Elman (2009); Kuperberg (semantic
P600 program, various); Paczynski & Kuperberg (2012); Kordjamshidi et al. (SemEval 2012/2013/2015); Randell, Cui
& Cohn (1992); Kintsch (1988/1998); van den Broek (Landscape Model; standards-of-coherence program); Schank &
Abelson (1977); Erk (2007); Agirre & Martinez; Gupta et al. (2017); Shi & Mihalcea (2005); Mechura (2010);
VerbNet resource; "Scene Abstraction for Lexical Semantics" (2026 preprint, arXiv 2605.22542); Rao & Ballard
(1999); Friston (free-energy principle, various); Ransom & Fazelpour (precision-weighting critique); Chang,
Dell & Bock (2006); Jaeger & Snider (2013); Goldwasser, Reichart, Clarke & Roth (2011); LeCun et al.
(energy-based learning tutorial); Liang et al. (learning from denotations; Neural Symbolic Machines; MAPO);
Hodapp & Rabovsky (2021); Rabovsky, Hansen & McClelland (2018); Brouwer et al. (2016); O'Brien & Myers
(memory-based text processing); Ferreira & Patson (2007); Ferreira et al. (good-enough processing, 20-years-
later review); Trueswell, Tanenhaus & MacDonald (constraint-based competition); Pickering & Garrod (2013).
**Approximate distinct-source count: 52.** Several ERP/interference-study specifics (visual-noise-interference
direction; Johnson-Laird's comprehension-specific counterexample-search claim) were explicitly flagged as
unverified from primary text and should not be treated as independently confirmed beyond this scan.
