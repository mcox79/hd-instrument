# PRIOR-ART DRILL: picturing sentences as scenes — brain + ML landscape (complements, does not re-derive, the SCV drill)

**Date:** 2026-07-19. **Filed by:** research (4 parallel Sonnet lit-scans + director synthesis). **Trigger:** USER's
core thread (humans build a mental picture/scene of a sentence to comprehend it) plus the live Scene-Coherence
Verifier (SCV) build in flight. This drill is explicitly SCOPED BROADER than, and does not re-derive, the
same-day companion note `research_mental_simulation_scene_verifier_error_signal_2026-07-19.md` — that note
already owns: Zwaan/Barsalou perceptual simulation, the WordNet-supersense+VerbNet attribute-scene design, the
scene-coherence verifier itself, and the contrast-is-the-active-ingredient training-signal diagnosis. This note
covers what that one did not: the wider psycholinguistic landscape beyond Zwaan/Johnson-Laird, and the full
ML/computational landscape (text-to-scene-graph, imagination/world-models, VLM render-and-check).

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature-agreement; novel-synthesis
capped at P<=0.50 per [[feedback-lit-scan-calibration-penalty]]). Established-lit findings are confidence-flagged
per source (established / contested / speculative-inference-by-scan), not blanket-deflated.

---

## HEADLINE

**The "build a scene, then check it" idea is well-trodden in psycholinguistics (situation models, event
segmentation, mental spaces, embodied construction grammar all converge on it — not novel) and has a genuine,
CREDITABLE, glass-box computational lineage in ML (WordsEye's rule-based depiction/constraint pipeline, SPICE's
rule-based sentence-to-scene-graph parser, and the Tenenbaum-lab "probabilistic-language-of-thought" line) — but
NO source found, in either literature, combines "picture a sentence as a checkable scene" with "use the check as
a self-supervised training signal for a comprehension system," fully glass-box, for TEXT specifically. That exact
combination remains the SCV's own open contribution (consistent with the companion note's own finding). The
single most important NEW result from this drill is a genuine, informative NEGATIVE: where the linguistic-
disambiguation version of "render and check" has actually been tested with a real generative/pixel renderer
(WinoVis, pronoun disambiguation via Stable Diffusion — near chance, 56.7%; LaViSA, structural-ambiguity via
text-to-image — soft/partial gains only) it does NOT work well. This is direct, credited evidence AGAINST going
pixel/generative and FOR the SCV's existing choice of discrete symbolic attribute-lookup — the pixel route has
been tried by others, for exactly this task class, and under-performs. Deflated P for "discrete/symbolic
scene-checking is the right level of representation for this task class" = 0.55 (raised, not capped, because this
is now supported by a DIRECT negative result on the alternative, not just an absence of positive evidence for it).</br>

---

## Ranked adoptable prior art for the glass-box substrate (item 5 — synthesis + verdict)

1. **WordsEye (Coyne & Sproat, SIGGRAPH 2001) — cheapest, most complete glass-box template. RANK 1.**
   Dependency parse -> semantic frame (WordNet-hypernym-driven "depiction rules") -> rule-based "transduction
   rules" that resolve spatial/attachment conflicts and add unstated-but-implied spatial constraints -> 3D scene.
   Zero neural components. This is the closest existing engineering precedent to "build a discrete scene from
   text and use spatial/world-knowledge constraints to pick the composition that makes sense" — i.e., almost
   exactly the SCV's own mechanism, one level more general (WordsEye resolves whole-scene, multi-entity spatial
   consistency; the SCV currently checks one verb-argument slot at a time). **GLASS-BOX-ADOPTABLE.** Credit:
   Coyne & Sproat. Honest gap: the literature surfaced does not report a quantitative disambiguation-accuracy
   number (PP-attachment or otherwise) for WordsEye's constraint resolution — its disambiguation-relevance is a
   reasonable **inference from mechanism**, not a demonstrated benchmark result.

2. **SPICE / Stanford rule-based scene-graph parser (Schuster et al. 2015 ACL-WS; Anderson et al. 2016 ECCV) —
   cheapest adoptable FRONT-END extractor. RANK 2.** 9 hand-written Semgrex dependency-pattern rules turn a
   sentence into an object/attribute/relation graph. **GLASS-BOX-ADOPTABLE**, and directly portable as a
   generalization of the SCV from "one verb-argument slot" to "a full small scene graph" per sentence. Honest,
   quantified cost of staying glass-box: re-scored on the newer FACTUAL benchmark, the rule-based parser scores
   SPICE-metric 64.77 vs a fine-tuned neural parser's 93.27 (Li et al. 2023, ACL Findings) — a real, ~20-30-point
   accuracy gap versus the neural alternative, which is the honest price of the glass-box choice, not zero-cost.
   Credit: Schuster, Krishna, Chang, Fei-Fei, Manning; Anderson, Fernando, Johnson, Gould; Li et al. (FACTUAL).

3. **AbstractScenes (Zitnick & Parikh, CVPR 2013) — validates the underlying PREMISE, not directly adoptable as
   a mechanism.** Human-composed clip-art scenes from sentences, with ground-truth object/pose/attribute known
   by construction; secondary-source-reported finding (not independently primary-verified) that subtle sentence
   wording changes produce different scene compositions — i.e., a constructed scene representation IS sensitive
   to and diagnostic of the semantic distinctions a disambiguator needs. This is the best available existence
   proof that "compose a scene from a sentence" carries disambiguating signal at all, independent of how the
   scene gets built. Credit: Zitnick, Parikh, Vanderwende.

4. **Larkin & Simon (1987, Cognitive Science), "Why a Diagram is (Sometimes) Worth Ten Thousand Words" —
   foundational theoretical support, non-ML, verified classic.** Argues a diagram's advantage over an equivalent
   propositional list is COMPUTATIONAL (grouping information used together avoids costly search/matching,
   enabling direct "perceptual inference" instead of derivation) — independent of any neural implementation.
   This is the strongest available theoretical justification for why a discrete STRUCTURED scene representation
   (not pixels) could do real computational work for the SCV, orthogonal to and reinforcing the SCV's own
   Johnson-Laird citation. Credit: Larkin & Simon.

5. **"From Word Models to World Models" (Wong, Grand, Lew, Goodman, Mansinghka, Andreas, Tenenbaum, arXiv:2306.12672,
   2023) + its ancestry (Kulkarni et al.'s "Picture" probabilistic-programming-for-scene-perception, CVPR 2015) —
   the single closest ML analog to "picture a sentence, glass-box, for language reasoning specifically."**
   Mechanism: an LLM translates an utterance into an executable probabilistic program (a "probabilistic language
   of thought"); the program is a glass-box simulate-and-infer step (not a neural net) producing a coherent
   world-state/judgment. Fully glass-box AT the simulation layer (the translation-to-program layer still needs a
   model, LLM or otherwise, to author the program — flag this honestly: NOT end-to-end glass-box as published,
   only the simulation/inference core is). Does not appear (from what could be verified) to close the loop as a
   self-supervised training signal — it is inference-time grounding, borrowed from a different tradition. Not
   needed for the SCV's current build; worth crediting as a MORE EXPRESSIVE representational target (probabilistic
   program vs. flat attribute-lookup) for a later iteration if the WordNet/VerbNet attribute set proves too
   coarse (Mechura's granularity-mismatch risk, already flagged in the companion note).

6. **Dreamer / World Models (Ha & Schmidhuber 2018; Hafner et al., Dreamer/V2/V3) — the strongest INDEPENDENT
   precedent for the SCV's OWN "double duty" design, from a completely different lineage (deep RL, not
   predictive coding).** The imagined rollout is simultaneously the simulation substrate AND, via backprop through
   imagined trajectories, the training signal for the policy — genuinely double-duty, well-established, heavily
   replicated. **REQUIRES-OPAQUE-MODEL-AT-RUNTIME** (VAE/RNN or RSSM latent world models are opaque neural nets) —
   NOT adoptable as an implementation. **ADOPTABLE AS STRUCTURAL PATTERN ONLY**: this is a second, independent
   convergent justification (beyond Rao & Ballard / Friston predictive coding, already cited in the companion
   note) that "the same simulate-and-check signal can drive both inference and learning" is a mainstream,
   cross-paradigm architectural pattern, not a fringe idea specific to neuroscience. Worth citing in the SCV's
   own design rationale as independent corroboration. Credit: Ha & Schmidhuber; Hafner et al.

7. **Spatial Role Labeling / SemEval 2012-2013 (Kordjamshidi, Bethard, Moens) — a SECOND source of discrete
   location/spatial typing, if WordNet supersenses prove too coarse for the location-vs-artifact residual.**
   Small symbolic trajector/landmark/spatial-indicator schema; early systems (feature-based CRFs) are still
   glass-box-adoptable at moderate accuracy cost versus later neural SOTA (Guo et al. 2021 report F1=0.95 on
   CLEF-2017 mSpRL with a deep model, not independently primary-verified). Relevant directly to the build/huts-
   vs-build/stream residual class the companion note already targeted. Credit: Kordjamshidi et al.

8. **NEGATIVE RESULT, cited as validation of the SCV's existing design choice: WinoVis (Park, Janecek,
   Ezzati-Jivan, Li, Emami, ACL 2024, arXiv:2405.16277) and LaViSA (Lee, Inadumi, Yoshino, arXiv:2606.19552).**
   WinoVis: rendering a sentence via Stable Diffusion 2.0 and checking which image matches the correct pronoun
   referent scores 56.7% precision, "only marginally surpassing random guessing" on Winograd-schema disambiguation
   — a genuine, established negative result for the PIXEL/generative version of "picture the sentence to
   disambiguate." LaViSA (a 1,503-sample, 7-category structural-ambiguity benchmark pairing ambiguous sentences
   with generated scenes) finds VLMs "can leverage visual scenes to resolve structural ambiguity to some extent"
   but "still struggle with certain ambiguity types and visually subtle semantic distinctions" — a soft partial
   positive at best. **Together these are the most decision-relevant finding of this whole drill**: when
   OTHERS have directly tested "render an actual image and check it" for exactly this task class (pronoun/
   attachment disambiguation), the result ranges from near-chance to weak-partial. This is real, credited,
   negative-to-mixed evidence AGAINST investing in a pixel-based or generative-image-based scene check, and FOR
   staying with the SCV's existing discrete WordNet/VerbNet attribute-lookup approach.

9. **NOT ADOPTABLE AT RUNTIME (flag clearly, credit as inspiration only): Whiteboard-of-Thought (Menon, Zemel,
   Vondrick, arXiv:2406.14562), Visual Sketchpad (Hu, Shi et al., arXiv:2406.09403), Visualization-of-Thought
   (Microsoft Research, arXiv:2404.03622), Mind's Eye (Liu et al., Google, arXiv:2210.05359).** All show large,
   real, repeated accuracy gains (up to +90pp in some settings) from a "render an intermediate representation,
   then read it back in" loop — but EVERY one of these needs a real, large VLM/LLM to perform the "read the
   rendered thing back and reason about it" half of the loop; some (WoT, Sketchpad) use a cheap deterministic
   renderer (matplotlib/turtle/graphics-engine code) for the DRAW half, but none avoid an opaque model for the
   INSPECT half. Also: all of the strong positive results are on spatial/geometric/navigational/math tasks, NOT
   linguistic disambiguation — the one place this pattern was tested on linguistic disambiguation specifically
   is item 8 above, and there it was weak-to-negative. **Verdict: credit the general "build an intermediate
   representation, then use it to check/ground a subsequent step" structural pattern as inspiration; none of
   these specific systems are implementable at runtime under the glass-box invariant.**

### Answering the SYNTHESIS question directly (item 5 of the task)

**Does anyone do exactly "picture a sentence into a simplified scene + check it makes sense to disambiguate
who-did-what, glass-box"?** No. The closest single system is WordsEye (glass-box, scene-from-text, spatial-
constraint resolution) but it was built for graphics generation, not evaluated as a disambiguation mechanism.
The closest ML-for-language-reasoning system is the Tenenbaum-lab probabilistic-language-of-thought line (glass-
box at the simulation core, evaluated on reasoning/QA, not disambiguation-training). The SCV (this session's own
design: WordNet-supersense + VerbNet-selectional-restriction type-consistency check, scored contrastively across
rival parses, reused as both selector and training signal) remains the most direct existing candidate for the
full combination — this drill did not find a closer prior system, which is itself the honest, deflated (P<=0.50)
answer to "has this been done already."

**Cheapest glass-box adoptable method beyond the SCV's WordNet/VerbNet attribute-scene:** the SPICE/Stanford
rule-based scene-graph parser (rank 2 above), used as a front-end to generalize the SCV from a single verb-
argument-slot check to a small multi-entity/multi-relation scene graph, when a case's ambiguity spans more than
one attachment site. Second-cheapest: WordsEye's transduction-rule spatial-constraint layer, if/when the SCV
needs to reason about more than one spatial relation simultaneously (e.g., two candidate PPs attaching to
different sites in the same clause).

---

## Angle-by-angle findings (credited, confidence-flagged)

### Angle 1 — Brain: picturing the sentence as a scene, beyond Zwaan/Johnson-Laird
Van Dijk & Kintsch's (1983) classic tripartite representation (surface code / textbase / situation model) is the
direct ancestor of both Kintsch's Construction-Integration model and Zwaan's event-indexing model — established.
Event Segmentation Theory (Zacks & Tversky 2001; Zacks & Swallow 2007; Kurby & Zacks 2008) shows people
spontaneously parse experience/narrative into discrete events at boundaries defined by changes along dimensions
that closely mirror Zwaan's 5 (characters, goals, objects, space, causality); the Event Horizon Model (Radvansky
& Zacks, *Event Cognition*, 2014) ties large prediction-error spikes at continuity breaks to a "global update"
reset of the situation model — established for the segmentation-memory link, but **no direct study bridges
event-boundary mechanisms to intra-sentence thematic-role/who-did-what ambiguity resolution** — a real, flagged
gap (moderate-confidence negative). Spatial mental models: Franklin & Tversky's spatial-framework work (1990,
*JEP:General*) is strong, established evidence that a genuinely spatial (not just propositional) egocentric
layout is constructed and used during narrative comprehension. Individual-differences literature is nuanced, not
a clean story: Irrazabal (2016) finds spatial inferencing during narrative comprehension relies mainly on
VERBAL working memory, with spatial WM recruited only when imagery is specifically required — a genuine
dissociation, not "spatial ability = disambiguation ability." **No study found directly correlates spatial-
ability psychometrics (e.g., mental rotation) with garden-path/thematic-role disambiguation performance** — a
second flagged gap. Developmental angle: Boerma, Mol & Jolles (2016, *Frontiers in Psychology*) show children
with stronger mental-imagery skills use illustrations more effectively for story comprehension (established,
single study); the general claim that younger readers rely more on illustrations, fading toward text-internal
cues with age, is real but the parallel to math-education's well-established "concreteness fading" framework
does NOT appear to have been explicitly drawn anywhere in the literature scanned — this specific synthesis is
**speculative-inference-by-scan**, not an established finding. Aphantasia: two studies go deeper than general
visual-memory testing (a 2023 bioRxiv preprint on reduced motor engagement during action-language reading, not
independently confirmed from primary text; Speed, Eekhof & Mak 2024, *Consciousness and Cognition*, finding no
recall/comprehension difference but reduced appreciation of scenery/action description) — but **no study was
found that specifically tests garden-path reanalysis, thematic-role assignment, or plausibility judgments in
aphantasics vs. controls** — a genuine, high-confidence-in-the-negative gap given multiple targeted searches came
up empty. Additional named "build-a-scene-then-check" accounts beyond the companion note: Mental Spaces Theory
(Fauconnier 1985/1994 — partial cognitive models linked by mappings, coherence via space-connections, a more
abstract cousin of Johnson-Laird's models) and Embodied Construction Grammar (Bergen & Chang; Bergen, Narayan &
Feldman — comprehension activates embodied schemas and runs a mental simulation, with an implicit fit-check via
which simulation coherently "runs") — both established theoretical frameworks. **Overall novelty verdict for
Angle 1: the core idea is well-trodden; the underexplored seams are the cross-literature bridges (event-boundary
mechanisms to intra-sentence ambiguity; spatial-ability psychometrics to disambiguation; aphantasia to structural
sentence-processing tasks specifically) — three real, useful, flagged absences, not three positive findings.**

### Angle 2 — ML: text-to-scene-graph / text-to-image / text-to-3D for disambiguation
Covered in ranked list items 1-3, 7. Summary finding not otherwise stated above: no paper found in this scan
reports a disambiguation-accuracy metric (e.g., "% of PP-attachment cases correctly resolved by picking the
physically-plausible generated scene") as a first-class evaluation for any text-to-scene/text-to-image system —
the closest is Nasr et al. (Neural Processing Letters 2020 / IWANN 2019), which uses REAL (not generated) images
to correct a text-only parser's PP-attachment errors, gaining up to +17 points accuracy for locative prepositions
on a Flickr-caption corpus (established) — but this is image-grounding on real photos, not scene-generation, and
the visual-feature side is a trained CNN (REQUIRES-OPAQUE-MODEL-AT-RUNTIME).

### Angle 3 — ML: imagination/world-models for language, "simulate then check"
Covered in ranked list items 5-6. The precise conjunction asked about — simulate a scenario from language, check
plausibility, use the check as BOTH the comprehension mechanism AND a self-supervised training signal, glass-box
— does not appear to exist as a shipped system anywhere found. The pattern's two halves exist separately and
robustly in different domains: simulate-as-training-signal (Dreamer/World Models) is extremely well established
but confined to control/robotics/games and is opaque-neural; simulate-a-sentence-into-a-checkable-world (Mind's
Eye, "Word Models to World Models"/Picture) is established for language specifically and is glass-box at its
core, but functions as one-shot inference-time grounding, not a training-signal loop. Porting "simulate-then-
check-as-training-signal" from control (Dreamer) into glass-box text comprehension would be a genuine
cross-domain synthesis, crediting both lineages explicitly — not a re-implementation of an existing system.

### Angle 4 — ML: VLM / visual-chain-of-thought / "draw to reason"
Covered in ranked list items 8-9. The single most decision-relevant sub-finding: where this pattern has actually
been tested on linguistic disambiguation specifically (as opposed to its usual spatial/geometric/math domain),
the evidence is thin and weak-to-negative (WinoVis near-chance; LaViSA soft-partial) — a genuine, credited
negative result that should be read as validating, not merely permitting, the SCV's discrete/symbolic design
choice over a pixel/generative one.

---

## Cheap decisive test

Not itself a new experiment — this is prior-art reconnaissance feeding the SCV build. The decisive test this
drill recommends layering ONTO the SCV's own already-registered Prediction 1/2/3 (see companion note): before
extending the SCV's coverage beyond the build/huts-class pilot, smoke-test whether SPICE-style rule-based
sentence-to-scene-graph extraction (rank 2 above) recovers the SAME candidate-parse structures the SCV's LCCP
rival-generation step already produces, on a held-out slice of the McGuffey corpus, with zero additional
annotation cost (pure structural cross-check, no gold needed for this specific test).

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction A (front-end generalization value). P=0.35 (deflated).** **HARD-PASS:** a SPICE-style rule-based
scene-graph extraction layer, applied to the SCV's existing rival-candidate slate, recovers additional
disambiguating multi-entity/multi-relation structure (beyond the single verb-argument slot the SCV currently
checks) on a non-trivial fraction (>15%) of cases the current single-slot SCV design abstains on. **HARD-FAIL:**
the SPICE-style extraction adds no new information beyond what the single-slot check already captures on this
corpus (i.e., the corpus's ambiguity classes are dominantly single-slot), OR the ~20-30-point rule-based-vs-neural
accuracy gap (Li et al. 2023) proves too costly on THIS corpus's specific verb/noun distribution (elevated false
scene-graph-edge rate) — either outcome is informative, not a wasted test.

**Prediction B (pixel/generative route, explicit can-fail on an established negative). P=0.15 (deflated, set
deliberately low — this prediction is registered ONLY to make explicit that we are NOT pursuing this route, given
existing evidence).** **HARD-PASS would require:** a pixel/generative scene-check (Stable-Diffusion-style
rendering + image-text alignment) outperforming the SCV's discrete attribute-lookup check on this project's own
ambiguity classes — given WinoVis's near-chance result on a closely analogous task (pronoun disambiguation via
diffusion rendering) and LaViSA's soft-partial result, this HARD-PASS is not expected to be sought; it is recorded
here only as the honest falsifiable alternative this project is explicitly declining to build, on credited
external evidence, not by assumption. **HARD-FAIL (the expected, default outcome, matching prior art):** no
pixel/generative route is attempted; this prediction remains untested by design, and the decision to skip it is
itself the deliverable of this section — recorded so a future session does not need to re-litigate "should we try
rendering pixels" without first checking this note.

---

## Cross-thread synthesis

Directly complements, without re-deriving, `research_mental_simulation_scene_verifier_error_signal_2026-07-19.md`:
that note established the SCV's core design (WordNet/VerbNet attribute-scene, contrastive scoring, double-duty
selector+trainer) and flagged its central claim (Angle B, scene-coherence as self-supervised signal) as
genuinely untested in the exact combination needed. This drill (a) independently confirms that gap is real by
scanning the FULL ML landscape (not just the psycholinguistics/weakly-supervised-parsing angle the companion note
covered) and finding no closer system, (b) supplies a second, independent architectural justification for the
double-duty design (Dreamer/World-Models, a completely different lineage from predictive coding), and (c)
supplies a genuine, credited NEGATIVE result (WinoVis, LaViSA) that the companion note did not have, which
directly supports the companion note's own choice of discrete symbolic attribute-lookup over any
perceptual/pixel alternative — this is new evidence, not a restatement. Also connects to the prior-art scour
synthesis (`prior_art_scour_synthesis_focus_chaingrade_2026-07-18.md`): the NVSA/NS-CL "learned front-end + fixed
glass-box reasoning core" pattern that synthesis identified as the porting template is structurally the SAME
shape as WordsEye's own pipeline (structured extraction -> fixed rule-based constraint resolution) — this drill
adds WordsEye and SPICE as ADDITIONAL, older, directly-credited precedents for that same architectural shape,
specifically in the text-to-scene sub-domain rather than the general neurosymbolic-vision domain the 07-18
synthesis drew from.

---

## Substrate-product implications

If the SCV's Prediction 1/2 (companion note) pass: this drill's ranked prior art gives a concrete, cheap,
credited path to GENERALIZE the SCV beyond the build/huts pilot — SPICE-style scene-graph extraction (rank 2)
for multi-relation cases, WordsEye-style spatial-constraint resolution (rank 1) if/when a case needs reasoning
about more than one spatial relation at once, and the Tenenbaum-lab probabilistic-program representation (rank 5)
as a later, more expressive fallback if WordNet/VerbNet coverage proves too coarse (matching the companion note's
own Mechura granularity-mismatch risk register). Independent of the SCV's own pass/fail outcome, this drill's
single most useful, immediately actionable finding is the NEGATIVE result (WinoVis/LaViSA): it is now
CREDITED EXTERNAL EVIDENCE, not just an internal design preference, that a pixel/generative scene-check is the
WRONG direction for this specific task class (linguistic disambiguation) — this closes off a speculative
direction (image-generation-based comprehension checking) that might otherwise have looked attractive given the
strong positive results the same "render and check" pattern shows on spatial/math/navigation tasks. That
divergence (strong on geometry/navigation, weak-to-negative on linguistic disambiguation specifically) is itself
a substrate-relevant finding: it suggests the "picture the sentence" mechanism's VALUE for THIS project is
specifically in the discrete/relational/typed structure a scene forces you to commit to (who has what type,
what relation holds), not in anything perceptual/spatial-metric about the scene — directly consistent with, and
now doubly supported by, both this project's own structural-beats-semantic pattern and the companion note's
Johnson-Laird-over-Barsalou framing.

---

## Citations (verified count)

Distinct sources cited across the 4 lit-scans + synthesis, credited by name: Van Dijk & Kintsch (1983); Kintsch
(1988); Zacks & Tversky (2001); Zacks & Swallow (2007); Kurby & Zacks (2008); Radvansky & Zacks (*Event
Cognition*, 2014; 2017); Radvansky (2012); Franklin & Tversky (1990); Irrazabal (2016); Just & Carpenter (1992);
Boerma, Mol & Jolles (2016); Pike et al. (2010, moderate-confidence bibliographic detail); Speed, Eekhof & Mak
(2024); aphantasia/action-language bioRxiv preprint (2023, unverified from primary text); Christianson et al.
(2001, lingering-misinterpretation, already known from companion note, re-cited here for garden-path framing);
Fauconnier (1985/1994, Mental Spaces); Bergen & Chang; Bergen, Narayan & Feldman (Embodied Construction Grammar);
Schuster, Krishna, Chang, Fei-Fei, Manning (2015); Anderson, Fernando, Johnson, Gould (SPICE, 2016); Li et al.
(FACTUAL, ACL Findings 2023); Coyne & Sproat (WordsEye, SIGGRAPH 2001); Zitnick & Parikh (AbstractScenes, CVPR
2013); Zitnick, Parikh & Vanderwende (ICCV 2013); Tan, Feng & Ordonez (Text2Scene, CVPR 2019); Johnson, Gu & Fei-
Fei (sg2im, CVPR 2018); Nasr et al. (2019/2020, PP-attachment via real images); Kordjamshidi, Bethard & Moens
(SemEval spatial role labeling, 2012/2013); Guo et al. (2021, CLEF-2017 mSpRL, not independently primary-
verified); Weber et al. (I2A, 2017); Ha & Schmidhuber (World Models, 2018); Hafner et al. (Dreamer/V2/V3); Liu et
al. (Mind's Eye, Google, 2022); Wong, Grand, Lew, Goodman, Mansinghka, Andreas, Tenenbaum ("Word Models to World
Models," 2023); Kulkarni et al. (Picture, CVPR 2015); Larkin & Simon (1987, verified classic); Menon, Zemel &
Vondrick (Whiteboard-of-Thought, 2024); Hu, Shi et al. (Visual Sketchpad, 2024); Microsoft Research
(Visualization-of-Thought, 2024); Park, Janecek, Ezzati-Jivan, Li & Emami (WinoVis, ACL 2024); Lee, Inadumi &
Yoshino (LaViSA, 2026, flagged as a very-recent/unusual-dated arXiv ID, treat with slightly extra caution pending
independent re-verification); Mehrabi et al. (LAVA/TAB/TIED, ACL 2023). **Approximate distinct-source count: 45.**
Several items are explicitly flagged above as unverified-from-primary-text or moderate-confidence bibliographic
detail and should not be treated as independently confirmed beyond this scan; the LaViSA arXiv ID in particular
carries an unusual (very-recent, 2026) date stamp and should be re-verified independently before being treated as
load-bearing for any downstream decision.
