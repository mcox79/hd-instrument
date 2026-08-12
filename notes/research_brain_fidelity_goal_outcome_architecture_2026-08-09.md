# Brain-fidelity audit: TOP-DOWN vs BOTTOM-UP goal-outcome architecture

**Filed by:** research sub-agent, 2026-08-09. Director-requested, load-bearing (decides direction).
Method: 4 parallel Sonnet lit-scan sub-agents (WebSearch/WebFetch, live-verified, primary sources
preferred, modern (post-2000, mostly post-2010) citations), each covering a different mechanism
angle, one explicitly tasked as adversarial devil's-advocate. This note is the Director-level
synthesis across all four, cross-checked against our own disk (`hdlab/goal_achievement.py`,
`hdlab/situation_model_accumulate.py`, `hdlab/state_of_mind.py`, `hdlab/goal_typing.py`) and against
9 prior project brain-fidelity audits (cited inline). Calibration penalty per
[[feedback-lit-scan-calibration-penalty]] applied throughout — deflate 0.15-0.25, cap
novel-synthesis P at 0.50.

## HEADLINE

**The brain does NOT compute "did I get what I wanted" bottom-up (extract outcome, then compare to
goal). Across four independent mechanism literatures — reward-prediction-error (RPE), PFC
guided-activation/biased-competition, predictive coding, and situation-model/discourse
comprehension — the converging, well-cited, mostly-established answer is TOP-DOWN: the goal is held
as an actively-maintained expectation that is constitutively involved in interpreting the incoming
outcome, not consulted only after an independent extraction step.** This is not univocal — there IS
a genuine, well-established bottom-up-first stage in the brain (a goal-agnostic perceptual-salience
"circuit breaker," Corbetta & Shulman 2002), but it operates on raw unexpectedness/salience for
*orienting*, not on semantic goal-outcome comparison, so it does not rescue our current
architecture's specific failure mode. **Our current bottom-up extract-then-compare pipeline
(`hdlab/goal_achievement.py`'s `valence_channel`, and more broadly the "extract outcome event
independently, then bind/compare" pattern across the goal-owner-attribution chain) is a genuine
FIDELITY DIVERGENCE for the ~half of the observed DesireDB shortfall population that has affect
words present but unbound to the goal (49% of items per the standing project measurement) — this
sub-problem is exactly what a goal-cued/biased-competition reframe fixes. It is NOT a fix for the
other half of the wall (outcome events with no goal-adjacent vocabulary present at all — the
OOV/grounding-vocabulary problem), which remains a separate, already-correctly-identified gap.**
Confidence in the TOP-DOWN verdict itself: high (multiple independent, well-established literatures
converge, deflated below). Confidence that the specific proposed architectural fix resolves the
DesireDB residual: moderate, capped per novel-synthesis discipline (see Falsifiable predictions).

---

## Per-mechanism findings (SHAPE + POSITION + METRIC + match/divergence)

### 1. Reward-Prediction-Error (RPE) — OFC / vmPFC / ventral striatum / VTA dopamine

**SHAPE:** RPE = signed difference between an *actively maintained* expected value/state and the
received outcome (Schultz, Dayan & Montague 1997, *Science* 275:1593, PMID 9054347; Schultz 2016
*Dialogues Clin Neurosci*, 2020 *Curr Opin Neurobiol* PMC8116345). Critically, the modern literature
splits this into two separable steps that must not be conflated: (a) the value-comparison arithmetic
itself (genuinely close to agnostic on top-down vs bottom-up in the base TD-error formalism), and
(b) **outcome IDENTIFICATION/INTERPRETATION** — classifying *what actually happened* before it can
be valued. For (b) the evidence is decisive and modern: **Takahashi et al. 2011** (*Nat Neurosci*
14:1590, PMID 22037501) — OFC-lesioned rats' dopamine RPE neurons *lose the ability* to correctly
interpret "externally similar" ambiguous outcome states without OFC's top-down inferred-state
signal. **Babayan, Uchida & Gershman 2018** (*Nat Commun* 9:1891, PMC5951832) — the single cleanest
result in the whole scan: an *identical physical reward magnitude* is classified as a positive vs.
negative prediction error by the dopamine system purely depending on which belief-state/expectation
was pending beforehand. **Howard & Kahnt 2018** (*Nat Commun* 9:1611, PMID 29686225) — midbrain
dopamine PE signals track violations of expected outcome *identity* (not just value), updating OFC's
identity-expectation model. **Sharpe et al. 2020** (*Nat Commun* 11:106, PMID 31913274) —
optogenetic dopamine transients drive associative/model-based learning, not model-free value
caching, directly undercutting the "pure scalar post-hoc subtraction" reading of RPE.

**POSITION:** VTA/SNc (phasic dopamine, ~100ms latency) + OFC (abstract, goal-relevant "economic"
value maintained across the choice-outcome delay — Padoa-Schioppa & Assad 2006 *Nature* 441:223,
PMID 16633341; offer-value/chosen-value cell classes) + credit-assignment/causal-model machinery in
lateral OFC (Walton et al. 2010 *Neuron* 65:927, PMID 20346766 — lesions cause credit to spread to
non-causal choices, i.e. OFC uses a maintained task-structure model that new outcome evidence is
read *against*).

**METRIC:** Single-unit recording, fiber photometry, optogenetics, lesion, human fMRI — converging
across rodent and primate.

**MATCH/DIVERGENCE for our architecture:** DIVERGENT. Our `goal_achievement.py::valence_channel`
computes outcome valence as a bottom-up bag-of-words vote over the WHOLE outcome sentence,
independent of what the specific goal was — structurally exactly the "outcome identified
independently, then compared" pattern the RPE literature above empirically rules out for ambiguous
cases. `relation_channel` is closer to brain-faithful (it actively searches for goal-verb recurrence
in the outcome, i.e. the goal *is* used as a cue during search) but only fires when the exact
lemma/synonym recurs; when it abstains, the fallback (`valence_channel`) reverts to the divergent
bottom-up pattern.

**Confidence: raw ~0.75 (convergent across 5 independent studies/methods spanning 3 species-classes
+ human fMRI); deflated to 0.55-0.60 per calibration discipline (some full texts inaccessible to the
lit-scan agent this session — Padoa-Schioppa & Conen 2017 review, Rushworth et al. 2011 full text —
flagged by the sub-agent as resting on secondary sourcing).**

### 2. Top-down goal-maintenance as active bias — PFC guided-activation, biased competition, predictive coding

**SHAPE:** Miller & Cohen 2001 (*Annu Rev Neurosci* 24:167) guided-activation theory: sustained PFC
activity representing a goal provides **bias signals** to posterior/sensory processing such that the
*same physical input* is processed differently depending on the active goal — this is the field's
dominant PFC theory, established. Desimone & Duncan 1995/Desimone 1998 biased competition: a
top-down target/goal template pre-activates matching candidate representations, biasing which one
"wins" a competition for representation — originally vision-specific (V4/IT), but a modern
lexical-semantic extension exists and is directly relevant: **Musz & Thompson-Schill 2016** (*Brain
Lang*, PMC5359984) shows left VLPFC activity actively *suppresses* the contextually-inappropriate
meaning of an ambiguous word via the same competitive-bias mechanism, structurally identical to
Desimone/Duncan just relocated to lexical content. Predictive coding (Rao & Ballard 1999 *Nat
Neurosci* 2:79; Clark 2013 *BBS* 36:181, PMID 23663408; Kuperberg & Jaeger 2016 *Lang Cogn Neurosci*
31:32, PMC4850025) is the most mechanistically explicit: **feedback connections carry the prediction
itself; feedforward connections carry only the residual error** — the "percept"/interpretation at
any level IS the top-down prediction as corrected by bottom-up error, not an independently-formed
bottom-up representation checked afterward. Kuperberg & Jaeger state this explicitly for language:
higher-level (message/situation-model) representations are passed DOWN to pre-activate lower-level
representations BEFORE bottom-up input arrives.

**POSITION:** Hierarchical cortical processing (all levels, phonology through discourse/message
level for language); PFC (dlPFC/VLPFC) as the source of the top-down bias signal, feeding back to
posterior/associative cortex.

**METRIC:** Single-unit competitive-suppression recordings (V4/IT); MVPA pattern-similarity + VLPFC
BOLD (lexical-semantic); simulation demonstrating predictive-coding networks spontaneously reproduce
known extra-classical receptive-field effects (Rao & Ballard); N400 amplitude as the most robust
behavioral/ERP marker of prediction-error-driven language processing.

**MATCH/DIVERGENCE:** DIVERGENT, and this is the sharpest one. Our pipeline's general SHAPE across
multiple components (not just goal-outcome) is "extract stage N independently and completely, THEN
consult higher-level structure" — this is the opposite of biased competition / predictive coding's
"top-down signal participates IN the competition/settling that produces the stage-N representation."
This same divergence pattern was independently flagged by the goal-owner-attribution component audit
(`notes/goal_owner_attribution_pipeline_brain_fidelity_audit.md`, 2026-08-09) for thematic-role
labeling: the brain's mechanism there (MacWhinney competition-model, verb-frame + multi-cue
integration) is ALSO a competitive-integration process, not a positional post-hoc heuristic — same
divergence class, different pipeline stage. This is not a one-off finding specific to goal-outcome;
it is a recurring architectural pattern across the whole comprehension pipeline.

**Confidence: raw ~0.75 for the general theory (guided-activation and predictive coding are
mainstream, heavily-cited, largely uncontested at the theory level); the specific claim that this
generalizes cleanly to discourse-level goal-outcome bias (as opposed to word-sense/attention) is
weaker — the lit-scan found NO paper using "biased competition" explicitly at discourse/narrative
goal level (a genuine literature gap, not a refutation). Deflated to 0.50-0.55 for the
discourse-level extension specifically; 0.65 for the general PFC-bias/predictive-coding claim.**

### 3. Situation-model / discourse comprehension — how readers actually track goal-outcome

**SHAPE:** Zwaan & Radvansky 1998 event-indexing model: intentionality/goal is one of five
continuously-tracked situational dimensions; the model's own reading-time methodology (RT
slowdown *at* a dimensional discontinuity) presupposes the prior goal-state is being held and
compared against each new clause AS IT ARRIVES, not retrieved only at a terminal resolution point —
directly modern-replicated by **Kopatich, Feller, Kurby & Magliano 2019** (*Cogn Res Princ Implic*
4:22, DOI 10.1186/s41235-019-0176-1): goal-shift panels are segmented as new events 3.5x more often
than goal-consistent panels, with ~370-500ms viewing-time costs AT the shift. Zacks event
segmentation theory (Zacks, Speer, Swallow, Braver, Reynolds 2007, *Psychol Bull* 133:273, PMID
17338600) states explicitly: "the perception of events depends on both sensory cues... and on the
top-down processing of conceptual features such as actors' goals" — segmentation is a CONTINUOUS
forward-prediction-then-error-detection process, not extract-then-compare, and goal/plan content is
explicitly one of the predictive dimensions, fused with bottom-up cues from the start (not staged
sequentially). Direct behavioral evidence of ONLINE (during-reading) goal-expectation effects:
**Albrecht & O'Brien 1993** (*JEP:LMC* 19:1061) — multiple active character goals compete for
working-memory availability in real time; **Lutz & Radvansky 1997** (*J Mem Lang* 36:293) — even
*completed* goal information stays MORE available than neutral info (argues directly against a
check-then-discard post-hoc model); **Haigh & Bonnefon 2015** (*Exp Psychol* 62:206, DOI
10.1027/1618-3169/a000290) — first-pass eye-tracking disruption when a subsequent action
contradicts a goal-based inference the reader had already formed, i.e. a genuine online reading-time
signature of top-down goal-bias on outcome-clause processing; **Amoruso et al. 2013** (*Front Hum
Neurosci* 7:57, DOI 10.3389/fnhum.2013.00057) N400 review — reduced N400 when an outcome matches a
context-generated (including goal-based) expectation.

Kintsch's construction-integration model: a SINGLE constraint-satisfaction settling computation
(construction = loose overgeneration of candidate propositions; integration = spreading-activation
settling to one coherent representation) used generically for ALL of comprehension, not a two-stage
extract-then-verify pipeline. No source accessed this session found a separate "verify against goal"
module described anywhere in the CI literature — combined with the independently-established finding
that goal-nodes persist as active constraints in exactly this kind of working buffer (Albrecht &
O'Brien; Lutz & Radvansky), the most defensible reading is: **expectation-satisfaction is the SAME
constraint-satisfaction operation as general coherence-settling, with the goal simply being one more
persistently-active, competitively-weighted node in the network** — flagged explicitly by the
lit-scan agent as a reasoned synthesis (primary Kintsch text was inaccessible this session), not a
directly-quoted primary claim; carry the corresponding confidence discount.

**POSITION:** Propositional/situation-model layer (mid-level, downstream of lexical access, upstream
of long-term-memory consolidation); goal-tracking specifically implicates working-memory
availability dynamics (Albrecht & O'Brien) more than any single localized region in the behavioral
literature (no fMRI/ERP study found that neurally localizes THIS SPECIFIC "goal biases outcome-clause
interpretation" effect to dlPFC/vmPFC — a genuine bridging gap between the neural PFC-bias literature
(finding 2) and the behavioral situation-model literature (finding 3), flagged honestly by the
lit-scan agent rather than papered over).

**METRIC:** Self-paced reading time, eye-tracking first-pass measures, probe-recognition latency,
recall accuracy, N400 amplitude, panel-segmentation judgments.

**MATCH/DIVERGENCE:** DIVERGENT. `situation_model_accumulate.py`'s `AccumulateRegister`/
`CausalLinkRegister` machinery (bind role x filler into an addressable, incrementally-updatable
per-entity representation) is actually reasonably FAITHFUL in mechanism SHAPE (bind+bundle+cleanup,
already flagged FAITHFUL in the prior goal-owner-attribution Component-4 audit) — the divergence is
in HOW it's fed: goal content currently participates only as a post-hoc comparison target
(`goal_achievement.py`'s channels run AFTER outcome text is already tokenized/scanned), not as an
active constraint that shapes which candidate outcome-interpretation the situation model settles on
in the first place.

**Confidence: raw ~0.70 (well-established foundational theories + solid modern behavioral
replications); deflated to 0.50-0.55 (several primary PDFs were inaccessible this session — original
Zwaan & Radvansky, Kintsch's own writing, Reynolds/Zacks/Braver computational model — resting on
secondary/abstract sourcing for some claims, explicitly flagged by the lit-scan agent).**

### 4. ACC expectancy-violation — adjudicating the existing internal claim + adversarial search

An existing project note (`notes/formalize_narrative_part2_goal_achievement_inference_2026-08-08.md`)
already claimed goal-achievement monitoring = "ACC expectancy-violation, fires on match/mismatch."
This drill independently verified/refined that claim rather than accepting it at face value.

**SHAPE:** The ORIGINAL 1999/2001 ACC conflict-monitoring theory (Botvinick, Nystrom, Fissell,
Carter, Cohen 1999 *Nature* 402:179, PMID 10647008; Botvinick et al. 2001 *Psychol Rev* 108:624) is
narrower than the internal note assumed: it is specifically about **response conflict** between
simultaneously co-active competing MOTOR programs — mapping "goal not met" onto that theory directly
would be a category error (no native representation of a temporally-extended goal-vs-later-outcome
comparison). BUT the field's theory evolved: **Alexander & Brown 2011** (*Nat Neurosci* 14:1338, DOI
10.1038/nn.2921) PRO model — mPFC/ACC **actively holds a time-resolved prediction of the upcoming
outcome BEFORE it occurs** (via a tapped-delay-line TD-learning representation) and fires a
"negative surprise" signal when the predicted event fails to occur; this model is explicitly built
to SUBSUME conflict-monitoring as a special case, and extends (Alexander & Brown 2014/2015, *Front
Comput Neurosci*, PMC4093652) to stimulus-level (not just action-level) prediction. This is the
single piece of literature closest to the internal note's original claim — and it is more precise
about WHY it counts as top-down: the prediction is generated and held BEFORE the outcome, so outcome
evaluation is inherently comparison-against-an-already-held-expectation, not independent
post-hoc lookup.

**Important complication (this is the adjudication, not just confirmation):** the field is NOT
unanimous that ACC = one clean expectancy-violation computation. Rushworth, Kolling, Behrens et al.
(Kolling et al. 2016, *Curr Opin Neurobiol*, PMC4863523) explicitly argue ACC carries MULTIPLE
dissociable signals (search-value/switch-value, model-updating, effort) that only partially overlap
with a match/mismatch story, and frame much of ACC through a foraging/explore-exploit lens.
Methodological critiques (Grinband et al. 2011 *NeuroImage* 57:303; a 2018 *Psychon Bull Rev* review
"Evidence against conflict monitoring and adaptation") show the underlying empirical base for
"conflict" signals is itself confounded/contested in places (time-on-task confounds, failed
conflict-adaptation replications). A direct follow-up to Somerville, Heatherton & Kelley 2006's
"dACC = generic expectancy-violation detector" finding (PMC3406317) found dACC activated to
expectancy-violating EXCLUSION but not to expectancy-violating OVERINCLUSION — a negativity/threat
asymmetry, not a symmetric match/mismatch computation (small-n caveat, but a real published
complication).

**ADVERSARIAL FINDING (the honest counter-evidence, actively searched for):** **Corbetta & Shulman
2002** (*Nat Rev Neurosci* 3:201) — a real, well-established, extremely-highly-cited dual-network
model: a DORSAL frontoparietal network implements top-down goal-directed attention, but a separate
VENTRAL frontoparietal network (TPJ, IFG) is genuinely NOT top-down — it is a "circuit breaker" that
detects behaviorally-relevant/salient/unexpected stimuli in a goal-INDEPENDENT, bottom-up way and can
interrupt the top-down system. This IS a legitimate bottom-up-first, goal-agnostic stage in the real
architecture. Zacks' event-segmentation theory reinforces that even basic event-individuation fuses
bottom-up sensory cues (motion, location-change) WITH top-down goal/intention cues from the start —
not a clean staged handoff, but not pure top-down override either.

**MATCH/DIVERGENCE:** the ACC/PRO-model finding STRENGTHENS the case for top-down architecture (more
precisely than the internal note's original framing: not "fires on match/mismatch" but "actively
holds the prediction before the outcome, and the held prediction is what the incoming outcome gets
read against"). The adversarial finding (Corbetta & Shulman) is genuine and must be incorporated
honestly: it supports a HYBRID recommendation (below), not pure top-down override — but it does NOT
rescue our current architecture, because Corbetta & Shulman's bottom-up stage operates on raw
perceptual salience for ORIENTING attention, not on semantic goal-outcome content comparison, which
is what `valence_channel`'s bag-of-words voting actually does (a goal-blind SEMANTIC judgment, not a
goal-blind SALIENCE/orienting judgment) — these are different computational categories, and only the
latter has bottom-up-first warrant in this literature.

**Confidence: raw ~0.65 (PRO model is a single, though influential, research program — not yet at
1999-conflict-monitoring-level independent replication; the pluralism/contested findings are
themselves well-established); deflated to 0.45-0.50.**

---

## THE VERDICT

**Our bottom-up extract-then-compare architecture is a genuine brain-fidelity divergence, not a
brain-faithful bottom-up-first design.** All four independent literatures (RPE, PFC guided-activation
+ biased competition + predictive coding, situation-model/discourse comprehension, and the
adjudicated ACC/PRO-model literature) converge on: the goal/expectation is held ACTIVE and
participates in constructing the interpretation of the incoming outcome, rather than being consulted
only after an independently-formed outcome representation already exists. This is not merely a
plausible-sounding metaphor — it rests on direct empirical demonstrations that IDENTICAL outcome
evidence gets classified oppositely depending on the pending expectation (Babayan/Uchida/Gershman
2018's belief-state dopamine result is the cleanest single existence-proof in the whole scan), that a
maintained top-down state signal is REQUIRED to correctly interpret ambiguous outcome states at all
(Takahashi et al. 2011's OFC-lesion result), and that online reading-time/ERP measures show
goal-based expectation effects operating DURING outcome-clause processing, not only afterward
(Haigh & Bonnefon 2015; Amoruso et al. 2013).

**The one legitimate bottom-up-first mechanism found (Corbetta & Shulman's ventral
salience/circuit-breaker network) operates on a different computational category (perceptual
unexpectedness for spatial/attentional orienting) than what our failing channel does (semantic
valence classification of outcome content) — so it does not license "our bottom-up valence-voting
approach is brain-faithful after all."**

**Scope discipline (do not oversell):** this verdict targets specifically the OUTCOME-INTERPRETATION
/ AFFECT-BINDING sub-problem — the ~49% of DesireDB items where affect words ARE present but not
bound to what the goal-owner cares about (whole-passage affect accuracy ~0.615, below the trivial
rule). It does NOT address the other half of the observed wall: outcome events with NO
goal-adjacent/affect vocabulary present at all (the OOV-of-event-ontology / grounding-vocabulary
problem, already correctly identified as the separate B-grounding pivot). A top-down reframe cannot
manufacture vocabulary that isn't there; it can only fix which of the words that ARE there get
weighted toward the fulfillment decision. Both gaps are real; this drill resolves the direction
question for the BINDING gap specifically, and confirms (does not newly discover) that the
VOCABULARY gap needs the separately-identified grounding lever.

### Concrete brain-faithful architecture recommendation

**Reuse, don't rebuild — the needed organs already exist:**

1. **Held goal-expectation vector** ("state of mind" analog): `hdlab/state_of_mind.py` already
   implements exactly the SHAPE needed generically (a maintained, salience-weighted, symbolic
   working-memory overlay of active discourse threads) — extend it (or use the same discipline
   inline) so the ACTIVE GOAL (from `hdlab.goal_typing.find_desired_state`) is one of the maintained
   threads, held active while the outcome sentence is being processed, not just retrieved
   afterward for a one-shot post-hoc comparison.
2. **Biased-competition-style selection among candidate outcome interpretations**:
   `hdlab/self_improving_loop.py::decode_coherence_margins` (cosine-cleanup top1-vs-runnerup
   readout) and `hdlab/situation_model_accumulate.py`'s `cleanup_argmax`/`AccumulateRegister` are
   exactly the superposition-collapse/query-cued-retrieval primitives biased competition and
   predictive coding call for — a goal-cue-weighted competition among candidate outcome-relevant
   spans/tokens, not a uniform bag-of-words scan.
3. **Concretely for `goal_achievement.py`**: replace (or add as a channel ahead of the current
   uniform `valence_channel`) a GOAL-CUED valence channel that weights each candidate valence-bearing
   token/predicate in the outcome by its relevance to the active goal cue (dependency-arc proximity
   via `candidate_generator.py`'s existing UD-parse machinery, or shared-feature similarity via
   `hdlab.lexical_similarity`/`hdlab.verb_lexical_similarity`, both already owned) BEFORE voting,
   rather than counting all valence words in the sentence equally regardless of which clause/referent
   they attach to. This is the direct glass-box analog of biased competition's "top-down template
   pre-activates matching candidates before/during the competition," and of Kintsch's "goal-node
   participates in the SAME settling process as everything else," and of the PRO model's "prediction
   held BEFORE outcome, comparison constitutive of interpretation."

**This is a hybrid, not pure top-down override** — per the Corbetta & Shulman and Zacks findings,
bottom-up content (the actual words present) still constrains/corrects the goal-biased weighting; the
recommendation is that the goal actively PARTICIPATES in scoring which outcome content matters, not
that it fabricates an outcome independent of the text.

---

## Cross-thread synthesis (prior project notes, not re-derived, extended)

- `notes/formalize_narrative_part2_goal_achievement_inference_2026-08-08.md` — its ACC-analog framing
  is CONFIRMED as directionally right and SHARPENED here: the accurate modern citation is the PRO
  model (Alexander & Brown 2011), not classical 1999/2001 conflict-monitoring, and the mechanism is
  more precisely "actively-held prediction before the outcome" rather than "fires on match/mismatch"
  (the latter phrasing under-specifies WHEN the expectation is formed/held, which is the whole crux
  of this drill's top-down-vs-bottom-up question).
- `notes/research_brain_event_segmentation_2026-08-05.md` — independently arrived at a compatible
  conclusion from the event-extraction angle: the brain's event unit is
  "prediction-error-gated... over ~5 tracked dimensions (time/space/causation/**goal**/protagonist)"
  and flagged that our extractor's "every predicate is an event" is unconditional where the brain's
  is SELECTIVE/relevance-gated. This drill's finding directly reinforces and specifies that gate: the
  relevance signal should be GOAL-cued (biased-competition-style), not merely a generic Zwaan-5
  discontinuity flag — a goal-specific instantiation of the same recommendation.
- `notes/research_synthesis_brain_fidelity_gap_event_prediction_relation_inference_2026-08-03.md` —
  independently converged on Kintsch construction-integration (overgenerate candidates, unscored,
  then filter via the already-validated `CausalLinkRegister` coherence organ) for the EVENT-PREDICTION
  frontier. This drill's finding is the natural extension to goal-outcome specifically: the active
  goal should be one of the constraints INSIDE that same integration/coherence settling, not a
  separate post-hoc gate applied after construction completes — consistent framing, different
  pipeline stage.
- `notes/goal_owner_attribution_pipeline_brain_fidelity_audit.md` (2026-08-09, same day) — its
  Component-3 finding (thematic-role labeling is MISSING-ENTIRELY as a general labeler; the one
  real-text attempt is a positional heuristic at 0.231 acc) is the SAME divergence class this drill
  finds for outcome-valence: a brain mechanism that's fundamentally a competitive, multi-cue,
  partially top-down integration (MacWhinney competition model for roles; biased
  competition/predictive coding for goal-outcome) is being approximated by a bottom-up positional or
  bag-of-words heuristic. This is now a THIRD independent pipeline stage (event segmentation,
  thematic roles, goal-outcome valence) showing the identical fidelity-divergence pattern —
  worth naming explicitly as a whole-pipeline architectural lesson, not three unrelated bugs.

---

## Cheap decisive test

Build `goal_cued_valence_channel(desire, outcome)` in `hdlab/goal_achievement.py`: form a goal cue
from `hdlab.goal_typing.find_desired_state` (desired-class + referent + key content lemmas, with
WordNet-neighbor expansion matching the existing `_verb_synonyms` pattern already in the file); score
each candidate valence-bearing token in the outcome by its dependency-arc proximity/attachment to
that cue (reuse `candidate_generator.py`'s existing unlabeled UD-parse arcs — no new parser) rather
than counting all valence words in the sentence with equal weight; compare against the CURRENT
uniform `valence_channel` on the held-out subset of DesireDB items where (a) `relation_channel`
currently abstains (`reason == "abstain"` or `"no_goal"`) AND (b) the outcome sentence contains >= 2
valence-bearing tokens (opinion_lexicon or `wordnet_polarity_propagation` hits) with mixed polarity —
exactly the population where uniform bag-of-words voting is structurally most likely to be
goal-blind-wrong (multi-clause outcomes describing several things, only one of which is the
character's actual goal-relevant content). This reuses every organ named in the recommendation above,
adds no new primitive, and is a same-day CPU-only smoke against data already used to produce the
0.686/0.620 macro-F1 numbers cited in `goal_achievement.py`'s own docstring.

## Falsifiable predictions

**HARD-PASS:** on the held-out mixed-polarity/relation-abstain DesireDB subset, goal-cued weighted
valence beats the current uniform bag-of-words valence by >= 10 points accuracy (or macro-F1, matched
to whatever metric the existing 0.686/0.620 comparison used) AND does not regress accuracy on the
single-clause/unambiguous subset (outcomes with 0-1 valence tokens, where goal-blind voting was never
structurally confused) by more than 2 points. This would mean the top-down/biased-competition reframe
is the correct fix for the BINDING half of the wall specifically.

**HARD-FAIL:** goal-cued weighting produces < 3 points change (either direction) on the mixed-polarity
subset — this would mean goal-relevance weighting was not the active lever even where affect words
ARE present, and the residual is dominated by something else even within the "affect words present"
population (e.g. the dependency-arc proximity signal itself is too noisy on real DesireDB prose to
serve as a goal-relevance proxy, or the CLASS_REGISTRY-style goal-cue extraction itself is too narrow
— NOT evidence the top-down mechanism is wrong in principle, since the literature convergence above
is independent of any one implementation choice; it would motivate a richer goal-cue representation,
not abandonment of the top-down direction). OR the single-clause subset regresses by > 5 points
(the weighting scheme is net-harmful — over-filtering valid signal), which would indicate the
weighting needs to be soft/graded (precision-weighted combination, per the predictive-coding
literature's own emphasis on graded prior-vs-input weighting) rather than a hard gate.

**Out of scope / will not be resolved by this test:** the OOV-vocabulary half of the wall (outcomes
with zero goal-adjacent/affect-bearing surface content) — a HARD-PASS here does not mean the whole
DesireDB wall is closed; a HARD-FAIL here does not mean the vocabulary-grounding lever (already
correctly identified) is wrong either. These are separable, both real, per the memory-log framing
this drill was dispatched to check.

---

## Substrate-product implications

1. **Direction confirmed, not overturned:** the current DesireDB program should NOT pivot away from
   fixing the affect-binding gap toward some other frontier — the brain-fidelity check requested by
   the Director comes back affirming that a goal-cued/top-down reframe of the existing bottom-up
   valence channel IS the brain-faithful next build, using organs already owned
   (`state_of_mind.py`, `decode_coherence_margins`/`cleanup_argmax`, `candidate_generator.py`'s
   UD-arcs, `lexical_similarity`) — this is a cheap, reuse-heavy fix, not a new subsystem.
2. **Whole-pipeline pattern named, not just a one-off fix:** three independent components across the
   comprehension pipeline (event segmentation, thematic-role labeling, goal-outcome valence) now
   share the identical fidelity-divergence diagnosis — "extract independently via a bottom-up/
   positional/bag-of-words heuristic, THEN consult higher-level structure" where the brain instead
   runs a competitive, multi-cue, partly-top-down integration AT that stage. This should inform how
   future components are FIRST-DRAFTED, not just how existing ones get audited after the fact —
   worth carrying into any new comprehension-pipeline stage design as a standing check ("does this
   stage extract independently-then-compare, or does it let the relevant higher-level context
   participate in the extraction itself?").
3. **Honest scope limit:** this reframe is a real, well-evidenced architectural fix for roughly HALF
   of the measured DesireDB shortfall population (the with-affect-words-but-unbound half); it is not
   a substitute for the separately-tracked grounding/vocabulary-coverage program, which remains
   necessary for the other half. Do not let a HARD-PASS on the cheap decisive test above be read as
   "the wall is closed" — it would close one well-defined sub-wall.
4. **No new lock exposure:** every organ named is already owned (own FHRR bind/bundle/cleanup, own
   UD-arc extraction, own lexicon-based similarity) — no external embeddings, no LLM-at-inference, no
   new borrowed component. Fully lock-compatible with existing invariants.

---

## Citations (verified count)

**26 distinct primary/secondary sources independently live-verified this session** across the 4
parallel lit-scan sub-agents (WebSearch/WebFetch against PubMed/Nature/ScienceDirect/PMC/journal
sites; author/year/venue/PMID or DOI recorded for each, not drawn from training memory):
Schultz, Dayan & Montague 1997 (PMID 9054347); Schultz 2016/2020 reviews (PMC8116345);
Padoa-Schioppa & Assad 2006 (PMID 16633341); Padoa-Schioppa & Conen 2017 (PMID 29144973, abstract
only — full text inaccessible); Walton et al. 2010 (PMID 20346766); Boorman, Behrens, Woolrich &
Rushworth 2009 (PMID 19524531); Takahashi et al. 2011 (PMID 22037501); Babayan, Uchida & Gershman
2018 (PMC5951832); Howard & Kahnt 2018 (PMC5913228); Gardner, Schoenbaum & Gershman 2018 (PMID
30464063); Sharpe et al. 2020 (PMC6949299); Miller & Cohen 2001 (Annu Rev Neurosci 24:167); Desimone
1998 (Phil Trans R Soc B 353:1245); Beck & Kastner 2009 (PMC2740806); Musz & Thompson-Schill 2016
(PMC5359984); Rao & Ballard 1999 (Nat Neurosci 2:79); Clark 2013 (PMID 23663408); Kuperberg & Jaeger
2016 (PMC4850025); Zwaan & Radvansky 1998 (abstract/secondary — primary PDF corrupted on fetch);
Kopatich, Feller, Kurby & Magliano 2019 (DOI 10.1186/s41235-019-0176-1); Zacks, Speer, Swallow,
Braver, Reynolds 2007 (PMID 17338600); Albrecht & O'Brien 1993 (JEP:LMC 19:1061); Lutz & Radvansky
1997 (J Mem Lang 36:293); Haigh & Bonnefon 2015 (DOI 10.1027/1618-3169/a000290); Amoruso et al. 2013
(DOI 10.3389/fnhum.2013.00057); McKoon & Ratcliff 1992 (PMID 1502273, abstract/secondary); Botvinick,
Nystrom, Fissell, Carter, Cohen 1999 (PMID 10647008); Alexander & Brown 2011 (DOI 10.1038/nn.2921);
Alexander & Brown 2014/2015 (PMC4093652); Kennerley, Walton, Behrens, Buckley, Rushworth 2006
(secondary sourcing, full text paywalled); Rushworth, Noonan, Boorman, Walton, Behrens 2011 (PMID
21689594); Kolling et al. 2016 (PMC4863523); Heilbronner & Hayden 2016 (PMID 27090954, abstract
only); Grinband et al. 2011 (ScienceDirect, secondary sourcing); Somerville, Heatherton & Kelley
2006 (PMID 16819523) + follow-up (PMC3406317); Corbetta & Shulman 2002 (Nat Rev Neurosci 3:201).
A subset of primary PDFs were inaccessible this session (corrupted fetch or paywall) and are
explicitly flagged inline above as resting on secondary/abstract-level sourcing rather than direct
primary-text quotation — carried forward honestly rather than silently upgraded to full confidence,
per the standing verify-on-disk / caveat-interpretation discipline.
