# Research drill: psychology of bridging/causal/counterfactual inference for the deep residual's chaining step (2026-08-09)

Filed by: Research (Sonnet), director+USER-requested drill. Trigger: the deep residual needs inferring
a goal-relevant RESULT from a literal outcome EVENT with no surface cue -- "wanted to knock out a guy" /
"I walked away" => preclusion => goal failed; "wanted to know why" / "I talked about it" => means-end =>
goal met. 4 parallel Sonnet lit-scans (automatic-vs-strategic inference generation; causal-network models
of comprehension; counterfactual/preclusion inference; situation-model updating + script expectation).

**Substrate state read before writing this (load-bearing, not re-derived):** `hdlab/goal_outcome_relation.py`
(built earlier THIS session, 2026-08-09, "Direction-B fork-A") already targets exactly this problem --
INSTANTIATES (means-end) and CONTRADICTS (preclusion) relations between a goal and an outcome. It is
currently **purely lexical**: `goal_atoms`/`outcome_atoms` are hand-authored pool-membership booleans
(`INFO_EXCHANGE_POOL`, `ERRAND_POOL`, `SKILL_TRAIN_POOL`, `COGNITION_GOAL_POOL`...) feeding a learned
construction-cue classifier for INSTANTIATES + a verb-agnostic regex for the self-reliance CONTRADICTS
sub-class, plus `mwe_disengage_scan` -- a WordNet verb-gloss dictionary lookup -- for the non-compositional
CONTRADICTS fraction. **It does not run over the situation-model bundle** (`hdlab/situation_model_accumulate.py`'s
`AccumulateRegister`/`CausalLinkRegister`, bind-role/bundle-event, decode via unbind+cleanup_argmax) or the
concept-relation organs (`hdlab/quality_relation.py` opposition, `hdlab/lexical_similarity.py`
`concept_similarity`) named in this drill's brief. The module's own docstring discloses the scaling problem
this drill is meant to address: hand-pool literal authorship was adopted only after WordNet hypernym expansion
was **measured noisier** (spurious bridges via generic hub synsets), and the CONTRADICTS dictionary-lookup
floor is 26/29 = 0.897 with 5 disclosed real gaps (bailed out / chickened out / shied away / washed her hands
of / turned the other cheek -- all genuinely absent or gloss-silent in WordNet). This is the precise gap this
drill's literature should speak to: is there a psych-validated, GRADED (not hand-pool, not exact-dictionary)
mechanism for the same two relations that generalizes further, and is it cheap enough to be a default
computation.

---

## 1. Which inferences are AUTOMATIC vs STRATEGIC (bounds what's cheap to model)

**Minimalist hypothesis** (McKoon & Ratcliff 1992, *Psychological Review* 99(3)) [ESTABLISHED as a historical
position, empirically superseded in its strong/narrow form]: only two inference classes are automatic --
locally-coherence-required bridging (connect current clause to the immediately preceding one) and
easily-available-knowledge inferences. Everything else (elaborative, predictive, most goal/global-coherence
inference) is strategic, generated only when task-driven.

**Constructionist theory** (Graesser, Singer & Trabasso 1994, *Psychological Review* 101(3)) [ESTABLISHED
taxonomy, "all-online" reading CONTESTED]: ~13 inference classes; distinctively claims **causal-antecedent
and superordinate-goal inferences ARE generated online** because comprehension is a default "search after
meaning" -- readers default to explaining *why* an event is mentioned, which requires activating the
character's motivating goal. Subordinate-goal/action, causal-*consequence* (forward), instantiation-of-noun,
and emotional-reaction inferences are conceded to be mostly offline/strategic even by GST.

**Empirical resolution since 1994** [CONTESTED overall framing, but two dividing lines are ESTABLISHED and
replicated]: the field reframed the binary into a resource/constraint-graded account (Cook 2017 review; Long
& Lea), but two asymmetries recur and are the load-bearing findings for this drill:
- **Backward causal-antecedent bridging is reliably automatic**; **forward causal-consequence/predictive
  inference is not** (Baggett, Johnson & Graesser 1993: causal-antecedent concepts reactivate within a
  ~400ms post-sentence window in RSVP+lexical-decision; predictive inferences require elaborative/task
  conditions or a highly constraining context, per Klin, Guzmán & Levine 1999 and Cook, Limber & O'Brien
  2001). Singer & Halldorson (1992/1996) show antecedent validation is a fast tentative-inference-then-check
  process, not exhaustive search.
- **Goal-outcome checking is automatic specifically when the goal is the CURRENT, ACTIVE, UNRESOLVED
  superordinate goal held in working memory** [ESTABLISHED, directly on-point]. Suh & Trabasso (1993, *Journal
  of Memory and Language* 32) and Trabasso & Suh (1993, *Discourse Processes* 16) used discourse-model
  analysis + think-aloud protocols + recognition priming to show goal-satisfaction inferences fire online
  specifically when an incoming action/event is causally/structurally tied to the most recently unsatisfied
  goal. Checking against a distant/backgrounded/already-resolved goal reverts to strategic processing --
  a CONTESTED boundary but the direction is consistent across sources.

**Bottom line (what to build now vs defer):** model as an UNCONDITIONAL DEFAULT computation, run on every
(active-goal, new-outcome-event) pair: (a) referential/entity resolution, (b) causal-antecedent bridging to
the immediately prior clause, (c) goal-satisfaction/preclusion checking against the current active unresolved
goal. Defer as STRATEGIC/optional (do not build into the always-on precedence chain): forward/predictive
consequence beyond the stated outcome, subordinate-goal/instrument inference, thematic/point-of-story
inference, emotional-reaction inference, and goal-checking against backgrounded/resolved goals.

## 2. Causal-network representation of the goal->attempt->outcome chain

Trabasso & van den Broek (1985, *JML* 24(5)) and Trabasso & Sperry (1985, *JML* 24(5)) [ESTABLISHED]: a story
is a directed graph of **typed nodes** (Setting, Event, Internal-Response, Goal, Attempt, Outcome) connected
by **4 typed causal edges**, established via a counterfactual-necessity test ("if A had not occurred, B would
not have"): Physical causation, Psychological causation (event/outcome -> internal state or goal),
Motivation (goal -> attempt/subgoal), Enablement (state creates a necessary condition without directly
causing). **GOAL is its own node type**, not an edge label -- it receives incoming psychological-causal edges
and emits outgoing motivational edges to Attempt. Stein & Glenn's (1979) story grammar
(Setting->Initiating-Event->Internal-Response->Plan->Attempt->Direct-Consequence->Reaction) is the ESTABLISHED
precursor structure the causal-network model absorbs.

**Recursive goal-subgoal-outcome unit** [ESTABLISHED]: Goal motivationally-causes Attempt, Attempt
physically-causes Outcome; if Outcome satisfies the goal, the chain closes; if it fails, the Outcome instead
**psychologically causes a NEW Goal node** (subgoal), recursively embedding another Attempt->Outcome cycle
("recursive transition network," Trabasso & van den Broek 1985's own term).

**Causal connectivity predicts recall/importance** [ESTABLISHED core empirical signature]: number of direct
causal connections + main-causal-chain membership (vs. causally-isolated "dead-end" nodes) independently
predict recall, summarization inclusion, and importance ratings (Trabasso & Sperry 1985) -- dead-end nodes are
essentially dropped from recall/summary.

**Goal "liveness" for inference = graded activation, not a binary flag** [ESTABLISHED mechanism, CONTESTED
whether a clean goal-specific decay function exists]: van den Broek's Landscape model (1996, 1999) reframes
goal persistence as ordinary cycle-by-cycle spreading-activation dynamics (node strength + reactivation from
causally-connected co-active nodes) -- a goal stays "hot" because many subsequent Attempt/Outcome nodes point
back to it, not because of a hand-coded resolved/unresolved timer. Resolution *starves* activation rather than
explicitly flagging it. Trabasso & Suh (1993) confirmed via think-aloud that readers spontaneously perform
**maintaining** (keep a causally-antecedent goal active), **retrieving** (reinstate it), **elaborating**, and
**explaining** (connect an incoming event back to the chain) -- genuinely online operations at the points the
causal graph predicts, not post-hoc rationalization.

**Minimal graph this literature licenses:** typed nodes {Setting, Event, Internal-Response, Goal, Attempt,
Outcome}; typed edges {Physical, Psychological, Motivation, Enablement}; a Goal->Attempt->Outcome triple as
the atomic unit, recursively chained on failure; importance/inference-priority = f(connectivity, main-chain
membership); goal availability for a NEW inference = graded activation that persists via connectivity, decays
by starvation, not an explicit timer.

## 3. Counterfactual/preclusion inference -- the "walked away precludes knockout" step

This is the thinnest, most honestly-open area of the four lanes -- report accordingly.

**Mental Models Theory** (Johnson-Laird; Byrne 2005, *The Rational Imagination*, MIT Press) [ESTABLISHED
general mechanism, SPECULATIVE at the specific goal-preclusion level]: under the "principle of truth,"
situation-model updating REPLACES an incompatible prior model rather than tagging it with negation --
consistent with "walked away" simply overwriting a "will land the blow" expectation. But no source found names
a specific "the model of an assertion also represents what it forecloses" mechanism for goal-preclusion
specifically; Byrne's mutability/immutability work is about generating counterfactual alternatives to a
*known* outcome, not *detecting* that a new action rules out a goal in the first place. This is a plausible
but genuinely undocumented extension.

**Talmy's Force Dynamics** (1988, *Cognitive Science*) [ESTABLISHED linguistic-descriptive theory; only
INDIRECT psycholinguistic uptake found]: Agonist/Antagonist framing gives blocking verbs a built-in entailment
("held back" -> NOT-advancing) independent of any negation morpheme. Glenberg & Kaschak's (2002) Action-sentence
Compatibility Effect and Matlock's fictive-motion work (2001, 2004) confirm readers simulate implied
motion/effort online with reading-time consequences -- real evidence force-dynamic content is computed during
comprehension -- but **no study directly tests whether readers use antagonist-wins structure to derive a
wordless goal-failure entailment.** Genuine gap, not just under-searched.

**Plan-failure/goal-obstacle recognition** (Wilensky 1983 *Planning and Understanding*; Schank & Abelson 1977;
Lehnert 1981 Plot Units) [SPECULATIVE/theoretical only, explicitly flagged per this drill's own discipline]:
symbolic-AI specifications of *what* a story-understander must detect (goal conflict, thwarted plans, chained
affect-state primitives for unfulfilled promises), never validated with human-subject experiments for the
specific wordless-incompatibility inference. Trabasso & van den Broek's causal-network model (section 2) IS
human-validated for goal-status *tracking* generally, but doesn't isolate this specific case.

**Negation-as-simulation** (Kaup, Lüdtke & Zwaan 2006; Kaup, Yaxley, Madden, Zwaan & Lüdtke 2007, *QJEP*)
[ESTABLISHED for EXPLICIT negation only]: readers simulate the affirmative state then suppress/background it,
evidenced via picture-recognition latency. **No extension to IMPLICIT (wordless) negation was found.**
"Mutual exclusivity" as a term is confined to word-learning (Markman & Wachtel 1988) and does not transfer to
narrative/goal comprehension in the literature searched.

**The one mature, validated mechanism is COMPUTATIONAL, not psychological** [ESTABLISHED as an implemented
AI technique, NOT claimed as a model of human processing]: GraphPlan's **mutex relations** (Blum & Furst 1997,
*Artificial Intelligence* 90) formally define when two actions/states cannot co-occur (inconsistent effects,
interference, competing preconditions) -- a direct computational analog requiring only a lookup against
action effect/delete-lists, no negation token needed. Even closer: partial-order causal-link planning's
**threat/clobbering detection** (Chapman 1987 TWEAK; McAllester & Rosenblitt 1991) checks whether an action's
effect negates a precondition PROTECTED by a causal link supporting a goal -- literally "does this action
delete the condition my goal depends on." Riedl & Young (2010, *JAIR*, "Narrative Planning: Balancing Plot and
Character") apply this machinery to character-goal story generation.

**Bottom line:** no validated general PSYCHOLOGICAL mechanism exists in the literature for "action X precludes
goal G" inference from wordless incompatibility -- this echoes the concept/script-knowledge gap the program
already diagnosed, not a new finding. What DOES exist and IS implementable is the computational mutex/threat
shape: maintain each active goal's supporting condition(s); for each new outcome-event, check its
effect/state against those conditions for negation/mutual-exclusion; fire "precluded" on a hit. This requires
a graded world-knowledge lookup of action-effects/state-incompatibilities -- exactly the concept-grounding
layer `hdlab/quality_relation.py` already builds (see section 5), just applied to event/state incompatibility
rather than adjective-quality opposition. **Flag honestly: this mechanism is licensed by computational
precedent, not by a validated account of human processing** -- treat the CONTRADICT/preclusion leg's psych
grounding as weaker than the ACHIEVE/means-end leg's (section 1's Suh & Trabasso finding is much stronger).

## 4. Situation-model updating + script expectation -- why the inference is CHEAP, not open search

**Zwaan's Event-Indexing Model** (Zwaan, Langston & Graesser 1995, *Psychological Science*; Zwaan & Radvansky
1998, *Psychological Bulletin* 123) [ESTABLISHED]: readers monitor 5 dimensions -- space, time, causation,
**intentionality** (protagonist goal/plan), entity/protagonist -- updating on discontinuity. Discontinuity
costs are reliably demonstrated for temporal and causal breaks (Zwaan, Magliano & Graesser 1995) and for
protagonist/temporal shifts (Rinck & Weber 2003); **intentionality is explicitly a "second-order" dimension
keyed to the entity dimension** -- goal-continuing sentences integrate faster, goal-related discontinuity
inflates reading time alongside causal/temporal breaks. ESTABLISHED that intentionality is a directly
monitored, trackable situation-model variable; CONTESTED whether it cleanly dissociates from causation
(the two are correlated in the data).

**Kintsch's Construction-Integration model** (1988, *Psychological Review* 95; 1998 book) [ESTABLISHED
canonical description]: two-stage process -- **construction** = weak, context-blind activation of a broad
proposition network including irrelevant/inconsistent elaborations; **integration** = spreading-activation
constraint-satisfaction that reinforces mutually-consistent nodes and suppresses inconsistent/irrelevant ones,
converging on a small coherent subset. This "activate-broad-then-settle" architecture is the field's standard
account of how relevant inferences get selected WITHOUT exhaustive symbolic search -- cheap parallel
constraint relaxation substitutes for serial search. Computational descendants: the Predication algorithm,
the Landscape model + LSA integrations (Yeari & van den Broek 2016). The specific claim that this is *the*
mechanism for GOAL-relevant selection (as opposed to general topical coherence) is a reasonable
extrapolation, not something Kintsch states in goal-specific terms -- CONTESTED/SPECULATIVE at that
specificity, but well-supported by convergence with section 1's findings.

**Scripts as pre-computed default slots** (Schank & Abelson 1977) [ESTABLISHED theory + ESTABLISHED strong
empirical support]: Bower, Black & Turner (1979, *Cognitive Psychology* 11) showed readers **falsely
recognize unmentioned-but-script-typical actions** as having been stated -- direct evidence script activation
supplies default content without new processing. Graesser, Gordon & Sawyer (1979, *JVLVB* 18) found near-zero
recognition-memory discrimination for typical/default actions (handled by a cheap "pointer") vs. reliably
better discrimination for atypical ones (require costlier tagging) -- the single strongest piece of direct
behavioral evidence that script defaults reduce processing cost relative to open search.

**Active goals function exactly like scripts for expectation-generation** [ESTABLISHED for the underlying
findings; CONTESTED/SPECULATIVE that this is a formally unified single mechanism -- no paper states it
explicitly, but the pieces jointly license it]: Klin, Guzmán & Levine (1999) and Cook, Limber & O'Brien
(2001) show predictive/outcome inferences are generated online specifically when context is **highly
constraining** (few plausible continuations) -- functionally the goal-literature analogue of script-slot
constraint. Combined with Suh & Trabasso (1993)'s goal->attempt->outcome causal-chain tracking and Kintsch's
construct-then-settle architecture: **an active goal pre-activates a small, bounded set of expected
resolution-types**, construction broadly and cheaply fires candidate propositions from the incoming outcome
text (including irrelevant ones), and integration runs a fast settling pass where candidates overlapping the
goal-primed set get reinforced and everything else decays. This is script-slot-filling generalized from
stereotyped event sequences to arbitrary goal-outcome pairs.

**Bottom line:** the mechanism that makes this inference cheap is NOT exhaustive lookup over all possible
outcome meanings -- it's a **goal-narrowed candidate set + activation-relaxation settling**, the same shape
Kintsch's CI already gives for general coherence, specialized to the goal dimension the way a script
specializes it to a stereotyped scene sequence.

---

## 5. Mapping to the owned substrate

**What already exists and maps directly (reuse, no new organ class):**

| Psych finding | Owned substrate primitive | Fit |
|---|---|---|
| Kintsch C-I / Zwaan multi-event-indexing (construct broad, settle via constraint) | `hdlab/situation_model_accumulate.py::AccumulateRegister` -- bind(role, event-slot) accumulated via bundle, decoded via unbind+cleanup_argmax | Exact -- the module's own docstring already cites this justification |
| Trabasso/van den Broek causal-network CAUSE/EFFECT edges | `hdlab/situation_model_accumulate.py::CausalLinkRegister(AccumulateRegister)` -- `add_cause_effect`, per-entity bind(CAUSE_vec/EFFECT_vec, linked idx) | Partial -- has ONE undifferentiated CAUSE/EFFECT edge, not the 4-way physical/psychological/motivation/enablement typing the lit found, and no GOAL/Attempt/Outcome node typing yet |
| Means-end/INSTANTIATES graded relation (script-slot-style "does this fill the expected resolution slot") | `hdlab/lexical_similarity.py::concept_similarity` (McRae-style shared-feature bundle cosine) | Graded SAME-pole check -- directly generalizes `goal_outcome_relation.py`'s hand pool-membership lists |
| Preclusion/CONTRADICTS graded relation (mutex/incompatibility check) | `hdlab/quality_relation.py` opposition composition (WordNet-antonym Channel A -> signed-FPE-axis Channel B -> concept_similarity fallback Channel C, cosine-thresholded OPPOSED/SAME/UNRELATED, zero confirmed false positives on its own adversarial probes) | Structurally right SHAPE (graded signed incompatibility, not boolean dictionary lookup) but currently scoped to adjective QUALITY axes (density/sheen/energy/tone, 23-word hand lexicon) -- needs the axis space extended to event/state incompatibility, not adjective opposition |
| Goal node as its own typed entity (not an edge label) | Not yet present -- `AccumulateRegister`'s `role_vocab` currently has only `CAUSE_ROLE`/`EFFECT_ROLE`; a `GOAL_ROLE` would extend the SAME class the same way `CausalLinkRegister` already extended `AccumulateRegister` | Direct, small, API-consistent extension |

**Proposed MINIMAL inference mechanism (goal-conditioned, reusing owned primitives, no new organ class):**

1. **Represent the goal as a bound filler** in the same entity's `AccumulateRegister`-style bundle already
   used for situation tracking: `bind(GOAL_ROLE, goal_concept_vec)`, where `goal_concept_vec` is the goal
   predicate's position in the grounded concept space (not a literal word-ID) -- extends `role_vocab` with a
   `GOAL_ROLE` alongside `CAUSE_ROLE`/`EFFECT_ROLE`, the identical pattern `CausalLinkRegister` already used
   to extend `AccumulateRegister`.
2. **Represent each candidate outcome event the same way**: `bind(OUTCOME_ROLE, outcome_concept_vec)`,
   accumulated into the SAME protagonist entity's register -- this is exactly Kintsch C-I / Zwaan multi-event
   indexing (section 4), already the module's own justification for `AccumulateRegister`'s existence.
3. **The chaining/inference step = two graded relation queries between the decoded goal-filler and the
   decoded outcome-filler, run through owned concept-relation organs unchanged:**
   - **ACHIEVE (means-end) query**: `concept_similarity(goal_concept, outcome_concept)` -- high graded
     similarity = outcome INSTANTIATES goal -> Fulfilled-supporting evidence. This is the literature-licensed
     (section 4, script/goal-slot-constraint) generalization of `goal_outcome_relation.py`'s hand-authored
     pool lists into a single graded query against a grounded concept space -- directly targets the module's
     own disclosed scaling caveat (literal-pool authorship was adopted only because hypernym expansion was
     measured noisier; a properly-grounded concept space is the thing that should fix that, not a bigger
     hand list).
   - **CONTRADICT (preclusion) query**: `quality_relation.py`'s opposition-channel SHAPE (graded signed axis,
     cosine-thresholded, zero-false-positive-calibrated) run over a goal/event-incompatibility axis --
     generalizes `mwe_disengage_scan`'s hand WordNet-gloss-keyword dictionary lookup (itself already a
     miniature instance of section 3's ESTABLISHED computational mutex/threat mechanism) into the graded-
     relation shape, aimed at recovering the 5 disclosed dictionary gaps (bailed out / chickened out / shied
     away / washed her hands of / turned the other cheek) that exact-lemma lookup cannot reach.
4. **Goal-conditioning gate** (directly implements Suh & Trabasso's "current active unresolved goal only"
   finding, section 1): the chaining step queries ONLY the most-recently-bound, still-unresolved `GOAL_ROLE`
   filler for that entity. Once a query returns a confident ACHIEVE or CONTRADICT verdict, that goal is
   resolved (stops being queried against new outcome events) -- a direct, cheap extension of the register,
   not a new mechanism.
5. **Automatic, not strategic**: per section 1, this whole step belongs in the AUTOMATIC/default tier -- it
   should be wired as an unconditional channel in `goal_achievement_verdict`'s existing precedence chain
   (same pattern as channels R/V/C), not gated behind extra strategic machinery. What stays deferred:
   forward/predictive inference beyond the stated outcome, subordinate-goal inference, and goal-checking
   against backgrounded/already-resolved goals (all matches the "defer" list in section 1).

**Honest asymmetry to carry forward**: the ACHIEVE/means-end leg (step 3, first bullet) has STRONG,
ESTABLISHED psych backing (Suh & Trabasso 1993, Klin et al. 1999, Cook et al. 2001, Kintsch C-I). The
CONTRADICT/preclusion leg (step 3, second bullet) is licensed only by COMPUTATIONAL precedent (GraphPlan
mutex / causal-link threat detection), not by a validated psychological mechanism -- section 3 found this is
a genuinely open area. Treat the CONTRADICT leg's calibration accordingly (deflated further, see P estimate).

---

## Cheap decisive test (can-fail, reuses the EXISTING harness, no new data)

`hdlab/goal_outcome_relation.py::self_test()` already has everything needed for a direct ablation: 14
TRAIN_EXAMPLES + 11 HELDOUT_EXAMPLES with disjoint tags, a memorization-baseline control, and a
scrambled-label control. The test: **swap ONLY the feature/relation computation** --

- Replace `goal_atoms`/`outcome_atoms`'s hand pool-membership booleans with a single graded
  `concept_similarity(goal_concept_vec, outcome_concept_vec)` score (bound into the `AccumulateRegister` shape
  per steps 1-2 above) for the INSTANTIATES side.
- Replace `mwe_disengage_scan`'s exact dictionary lookup with `quality_relation.py`'s graded opposition-channel
  shape (extended to an event/state-incompatibility axis) for the CONTRADICTS side.
- Keep the train/heldout split, `memorization_baseline_predict`, the scramble control, and every existing
  `self_test` assertion structurally UNCHANGED -- this isolates whether the situation-model+concept-relation
  route is a genuine improvement, not a different eval.

**HARD-PASS** (commit to the situation-model-grounded route as the go-forward mechanism): held-out accuracy
on the SAME 11-item heldout set >= the current construction-cue classifier's `held_acc` **AND** the scramble
control collapses to at/below the existing scramble baseline (goal-conditioning genuinely active, not
outcome-similarity-alone) **AND** it recovers >= 1 of the 5 disclosed WordNet-MWE dictionary gaps (bailed out
/ chickened out / shied away / washed her hands of / turned the other cheek) via graded relation where the
exact-lemma dictionary lookup structurally cannot -- this is the direct test of whether GRADED concept-
relation genuinely generalizes past the dictionary-coverage ceiling the current mechanism already disclosed,
not just reproduces it with more moving parts.

**MIDDLE_BAND** (real but not yet demonstrating the scaling advantage -- iterate concept-grounding quality
before committing further): matches current `held_acc` within noise, scramble control collapses, but
recovers 0/5 of the disclosed dictionary gaps.

**HARD-FAIL** (the grounded-relation route is not worth the added complexity yet -- keep the current
hand-pool/dictionary mechanism as the operating point): held-out accuracy drops below `memorization_baseline_predict`'s
accuracy, OR drops below the current classifier's `held_acc` by more than trivial noise, OR the scramble
control does NOT collapse (the relation is reading general outcome-similarity/valence, ignoring which
specific goal is paired -- the same wrong-goal-leakage failure class this arc has caught 4+ times already),
OR it recovers 0/5 dictionary gaps AND regresses accuracy (no signal, no scaling benefit).

---

## Cross-thread synthesis

- Sharpens `hdlab/goal_outcome_relation.py` (Direction-B fork-A, built earlier this session): that module
  already targets the correct TWO relation types (INSTANTIATES/CONTRADICTS) but implements them lexically
  (hand pools + exact-dictionary lookup). This drill supplies the literature-grounded argument for WHY the
  next iteration should route the same two relations through the situation-model bundle + concept-relation
  organs instead, and gives the specific psych citations (Suh & Trabasso 1993 for ACHIEVE; GraphPlan
  mutex/causal-link-threat for CONTRADICT, honestly flagged as computational-not-psychological precedent).
- Directly extends `notes/research_glassbox_utility_inverse_planning_leg_2026-08-09.md`'s utility-leg
  (attribute-weighted bind/bundle scoring against SATISFIED/VIOLATED/ABSENT): that drill supplied the
  WHAT-to-score representation (weighted attribute-predicate bundle); this drill supplies the HOW-the-
  relation-gets-computed mechanism (graded means-end/preclusion queries against the situation-model bundle)
  and the automaticity bound (build this as a default channel, not a strategic/deferred one).
- Corroborates `notes/research_brain_fidelity_goal_outcome_architecture_2026-08-09.md`'s top-down finding
  (goal actively biases interpretation of the outcome, not bottom-up extract-then-compare): section 1's Suh &
  Trabasso finding is the SAME literature that audit drew on, independently re-confirmed here with the added
  automaticity-boundary detail (active/unresolved goal only).
- Extends `notes/research_brain_fidelity_oov_schema_prediction_2026-08-09.md` (schema-competition/N400-as-
  prediction-error): that drill covered how novel OOV outcome PHRASING gets fit against an active schema;
  this drill covers the companion inference step once a candidate outcome IS extracted -- does it satisfy or
  preclude the goal. Complementary, not overlapping.
- `hdlab/quality_relation.py`'s own docstring already flags its 23-word 4-axis lexicon as "a small hand-
  supplied seed, not a general open-vocabulary solution" -- the CONTRADICT leg proposed here inherits that
  same disclosed coverage caveat unless the axis lexicon is scaled up before this test is run; flagged
  honestly rather than assumed away.

## Substrate-product implications

A working goal-conditioned chaining step over the situation-model bundle would let the product make an
auditable claim not just about WHICH lexical channel fired (the current `goal_achievement.py` trace) but
about the SPECIFIC RELATION TYPE it inferred (means-end instantiation vs. force-dynamic/mutex preclusion) and
which CONCEPT-SPACE evidence supported it -- a strictly richer, still fully inspectable trace than either the
current bag-of-words valence vote or the hand-pool construction-cue classifier. This is the same auditability
differentiator this arc has repeatedly identified as the defensible product edge (glass-box trace over
accuracy-parity); this drill's contribution is showing the trace can extend one more level (concept-relation
evidence, not just which-channel) while staying inside primitives already owned and reused, not a new
opaque component.

## Falsifiable predictions (HARD-PASS / HARD-FAIL, restated compactly)

- **HARD-PASS**: matches-or-beats current `held_acc` on the existing 11-item heldout set + scramble control
  collapses + recovers >=1/5 disclosed dictionary gaps via graded relation.
- **HARD-FAIL**: drops below memorization baseline OR below current `held_acc` (non-trivially) OR scramble
  control fails to collapse OR 0/5 dictionary-gap recovery combined with any accuracy regression.
- **MIDDLE_BAND**: matches current accuracy + scramble collapses, but 0/5 dictionary-gap recovery (real,
  not yet scaling).

## Citations (verified count: 0 primary-source-read this drill; all 4 lit-scan lanes report secondary/
WebFetch-sourced citations, cross-referenced across independently-searched lanes -- 31 distinct citations
named across the 4 lanes, several independently corroborated across lanes: McKoon & Ratcliff 1992; Graesser,
Singer & Trabasso 1994; Baggett, Johnson & Graesser 1993; Singer & Halldorson 1992/1996; Cook 2017; Long &
Lea 2005; Suh & Trabasso 1993 (x2 sources); Trabasso & Suh 1993; Klin, Guzmán & Levine 1999; Cook, Limber &
O'Brien 2001; Trabasso & van den Broek 1985; Trabasso & Sperry 1985; Stein & Glenn 1979; van den Broek,
Risden, Fletcher & Thurlow 1996; van den Broek, Young, Tzeng & Linderholm 1999; Yeari & van den Broek 2016;
Johnson-Laird & Byrne 2002; Byrne 2005; Talmy 1988; Glenberg & Kaschak 2002; Matlock 2001/2004; Wilensky
1983/1978; Schank & Abelson 1977; Lehnert 1981; Kaup, Lüdtke & Zwaan 2006; Kaup, Yaxley, Madden, Zwaan &
Lüdtke 2007; MacDonald & Just 1989; Markman & Wachtel 1988; Blum & Furst 1997 (GraphPlan); Chapman 1987
(TWEAK); McAllester & Rosenblitt 1991; Riedl & Young 2010; Zwaan, Langston & Graesser 1995; Zwaan & Radvansky
1998; Zwaan, Magliano & Graesser 1995; Rinck & Weber 2003; Therriault & Rinck (chapter); Kintsch 1988/1998;
Bower, Black & Turner 1979; Graesser, Gordon & Sawyer 1979.)

---

## HEADLINE

Four converging lit-scan lanes give a psych-grounded shape for the deep residual's chaining step. (1)
Goal-satisfaction/preclusion inference against the CURRENT ACTIVE unresolved goal is ESTABLISHED as automatic
(Suh & Trabasso 1993) -- build it as an unconditional default channel, not a gated/strategic one; forward-
predictive and backgrounded-goal inference stay deferred. (2) The representation this licenses is a typed
causal-network node/edge structure (Trabasso & van den Broek 1985) with goal "liveness" as graded activation
persisting via connectivity, not a binary flag -- maps directly onto the already-owned
`AccumulateRegister`/`CausalLinkRegister` bind/bundle/unbind shape, needing only a `GOAL_ROLE` extension
(same pattern `CausalLinkRegister` already used). (3) The ACHIEVE/means-end leg is well-supported
psychologically (script-slot-constraint literature, Kintsch C-I construct-then-settle) and maps onto
`lexical_similarity.concept_similarity` as a graded generalization of `goal_outcome_relation.py`'s current
hand-pool lists. (4) The CONTRADICT/preclusion leg is the field's genuinely thin spot -- no validated
psychological mechanism for wordless action-precludes-goal inference exists; the only real precedent is
COMPUTATIONAL (GraphPlan mutex / causal-link threat detection), which maps onto `quality_relation.py`'s
opposition-channel SHAPE (graded signed incompatibility) extended from adjective-quality axes to
event/state-incompatibility axes -- flagged as weaker-grounded than the ACHIEVE leg and calibrated
accordingly. The cheapest decisive test reuses `goal_outcome_relation.py`'s EXISTING train/heldout/
scramble-control harness unchanged, swapping only the underlying relation computation from hand-pool
lexical lists to situation-model+concept-relation grounded graded queries -- pre-registered HARD-PASS
requires matching-or-beating current held-out accuracy, a collapsing scramble control, AND recovering at
least one of the 5 already-disclosed WordNet-MWE dictionary gaps (the direct test of genuine generalization
past the current mechanism's own disclosed ceiling).

P_deflated=0.40 overall (blended: section 1's automaticity finding and section 2's causal-network
representation are ESTABLISHED/high-confidence secondary-sourced literature, 0.60-0.70; the ACHIEVE-leg
mapping to `concept_similarity` is well-licensed, ~0.50; the CONTRADICT-leg mapping to `quality_relation.py`
is genuinely novel synthesis with NO psychological precedent found, only computational -- capped at 0.35 per
calibration discipline given section 3's own honest "genuinely thin/open area" verdict; the mapping-to-
substrate architecture as a whole is this drill's own synthesis, not literature-stated, so deflated per
[[feedback-lit-scan-calibration-penalty]] even though the underlying psych claims are solid).
