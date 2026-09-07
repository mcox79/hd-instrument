# Research: the brain recipe for unmarked causal inference + a buildable content-sensitive generative-simulation architecture (2026-09-07)

## HEADLINE
The brain does not retrieve "A causes B" from a knowledge graph; it SIMULATES A's specific effect on its specific
patient forward to a result-STATE, then checks whether that state satisfies B's specific precondition (Schank-Abelson
RESULT + STRIPS precondition/effect, run as a forward physics/psychology simulation -- Battaglia/Hamrick/Tenenbaum
2013; Wolff 2007). Today's own on-disk refutation (`exp_joint_causal_cskg_v1`, `data/exp_joint_causal_cskg_v1/metrics.json`)
proves this is not a framing preference: broadening the causal typer with a 5.95M-edge commonsense KG (CSKG) lifted
coverage by only +0.0014 (NOT CI-separated) because 63.4% of MAVEN gold causal pairs already have BOTH lemmas in the
KG's vocabulary but NOT the specific edge -- an EDGE gap, not a vocabulary gap. Retrieval is coverage-bounded BY
CONSTRUCTION (a KG stores typical/frequent pairings, not this-sentence's specific object+context). The substrate
already has every load-bearing PIECE of the compute-don't-retrieve recipe built and SOLVED in isolation (force
dynamics, patient tendency, world-state STRIPS effects, FrameNet-derived possession operators, goal/inverse-planning
engine, grounded ConceptNet/CSKG affordance corroboration) -- what is missing is the COMPOSITION that turns "A's
verb is in the CAUSE class" (today's typer, ~4.5% recall, precision-on-fired 0.104, LOSES to both floors) into "A's
SPECIFIC patient, in this context, ends up in a state that SPECIFICALLY satisfies B's SPECIFIC precondition." I also
verified LIVE (not from memory) that `nltk.corpus.verbnet` frame semantics expose exactly this `cause(Agent,E)` +
`state(result(E), Endstate, Patient)` STRIPS structure for ~270 VerbNet classes, generalizing world_state_register's
hand-seeded GIVE/GET/LOSE/TOGGLE lexicon far beyond possession -- and it is CURRENTLY UNUSED anywhere in hdlab/
experiments (confirmed by grep + a live probe, printed below).

## Cheap decisive test
Build ONE new function, `derive_result_state(event) -> Effect`, that composes (in this order) `hdlab.world_state_register`
GET/LOSE/TOGGLE_ON/TOGGLE_OFF lexicon -> `hdlab.possession_operators` FrameNet GIVE/GET/LOSE -> a NEW `verbnet_result_state()`
helper that reads `nltk.corpus.verbnet.frames(classid)` for the verb's class, finds a `state(result(E), Endstate, Patient)`
predicate, and maps VerbNet's `Endstate` placeholder to a concrete state token via a small (~30-entry, auditable) per-class
endstate map (dry->DRY, break->BROKEN, open->OPEN...). Pair it with `derive_precondition(event) -> PreCheck` (existing
`world_state_register` USE-class check, extended to read a VerbNet `state(during(E),...)`/`has_possession` predicate as
the precondition where present, CSKG `HasPrerequisite`/`UsedFor` as final backoff). Re-run the EXISTING harness
`experiments/exp_joint_causal_cskg_v1.py` with ONE new arm, `content_sensitive` (recency window IDENTICAL to
`generative`/`generative_cskg`; only the per-candidate score changes to `satisfies(derive_result_state(A), derive_precondition(B))`),
against the SAME MAVEN-ERE gold, SAME detection, SAME bootstrap code (`boot_prec_diff`, `boot_margin` already written).
This is a ~1-day build (the compositions exist; only the two wrapper functions + the VerbNet endstate map are new) and
the harness/metrics/CI code needs ZERO changes.

## Falsifiable predictions
**HARD-PASS:** `content_sensitive` precision-on-fired beats the class-level `generative` arm's 0.1044 CI-separated
(doc-level paired bootstrap, `boot_prec_diff`, lo>0), AND beats `connective` (0.2347) and/or `contiguity_floor` (0.1864)
CI-separated on at least one of {all, unmarked}, AND the `shuffled_twin` of the new arm loses CI-separated. This would
be the first arm in this problem's history to win precision-on-fired over BOTH real floors, not just the density floor.

**HARD-FAIL (pre-registered, not to be explained away):** if `content_sensitive` ties or loses to `generative`'s 0.1044
(NOT CI-sep or negative), the honest conclusion is NOT "content-sensitive simulation doesn't work" -- it is that the
composition is still starved by the SAME upstream the `FULL_CHAIN_BRAIN_FIDELITY_SCAN_2026-09-07.md` already located:
`event_type`/`force_dynamics_typer`/`patient_tendency` all type on WordNet MOST-FREQUENT-SENSE (meaning-blind), so a
figurative/wrong-sense verb produces a wrong result-state/precondition with high confidence. Diagnostic to run in that
case: gate `content_sensitive` to fire ONLY on the subset where `patient_tendency`'s own sense/attachment residual is
absent (i.e., literal core-physics verbs the SOLVED already validated at 7/7 modern) -- if precision-on-fired clears
the HARD-PASS bar on THAT subset but not the full population, the finding is "mechanism correct, coverage capped by
the un-wired meaning channel" (confirms backlog item #1), not a mechanism failure.

**Secondary HARD-FAIL (asset-level):** if the VerbNet endstate map cannot be populated above ~30-40 auditable classes
without per-item gold-tuning (i.e., "Endstate" cannot be resolved from the verb lemma alone for most classes), VerbNet's
frame semantics is a narrower asset than this note claims and the result-state generation stays possession/FrameNet-only
-- report this honestly rather than force-fitting the map.

## The brain recipe -- step by step, cited, PINNED vs OUR-INVENTION-swept

**Step 0 -- candidate search is a RECENCY-biased backward search, not corpus retrieval. PINNED.**
Graesser, Singer & Trabasso 1994 (constructionist theory of comprehension, Psych. Review 101:371) -- readers run a
continuous "search after meaning," posing implicit why-questions and searching BACKWARD through a short window of the
situation model (not the whole discourse) for a causal antecedent, biased by recency/currency. The substrate already
implements exactly this window (`experiments/exp_joint_causal_survival_v1.bind_edges`, mode `generative`/`gen_prior`,
`WINDOW=4`) -- keep it; do not widen it into a full-document search.

**Step 1 -- route to a domain-general simulation engine (physical vs mental are dissociable systems). PINNED.**
Jack et al. 2013 (opposing physical/social domains); Fischer, Mikhael, Tenenbaum & Kanwisher 2016 (an intuitive-physics
network functionally distinct from Saxe & Kanwisher's 2003 rTPJ mentalizing network); Campanella et al. 2022 (triple
dissociation). The substrate's `hdlab.event_type.event_type(verb)` (WordNet supersense -> {PHYSICAL, PERCEPTION,
COGNITION, EMOTION, COMMUNICATION, BODY, SOCIAL, STATIVE, OTHER}) is the router. OUR-INVENTION: the WordNet-supersense
proxy for the domain split (a coarse but auditable stand-in for the neural dissociation, not itself neurally validated
at this granularity -- the module's own docstring flags this).

**Step 2a (PHYSICAL branch) -- simulate A's force-dynamic effect on the SPECIFIC patient. PINNED mechanism, OUR-INVENTION
lexicon.** Talmy 1988 (force dynamics: Agonist/Antagonist, tendency, steady-state vs onset); Wolff 2007 (JEP:General 136,
"force theory of causation" -- CAUSE/ENABLE/PREVENT fall out of a truth-table over patient-tendency x affector-patient
concordance x endstate-reached, forces combine as a VECTOR SUM); Wolff & Song 2003 (Cog. Psych. 47:276-332, verb choice
tracks force vectors); Battaglia, Hamrick & Tenenbaum 2013 (PNAS 110:18327, "Simulation as an engine of physical scene
understanding" -- people run approximate forward Newtonian simulations to predict/judge outcomes, not lookups). THE KEY
FIDELITY MOVE this note is built around: the type must be computed from THIS patient's tendency (the object's actual
disposition + the actual force magnitude + gravity/direction in THIS sentence), not from the verb's class alone --
exactly what `hdlab.patient_tendency.patient_tendency_signal`/`type_with_full_tendency` already do (a 4-term additive
force-sum: affector-magnitude + patient-affordance + directional/gravity + causing-vs-letting, PROVEN additive not
winner-take-all on a rotating-conflict control, `causation_typing_needs_a_patient_tendency_estimator/SOLVED.md`).

**Step 2b (MENTAL/GOAL branch, when A's agent = B's agent) -- inverse planning. PINNED.**
Baker, Saxe & Tenenbaum 2009 (Cognition 113:329, "Action understanding as inverse planning" -- an observer infers the
agent's goal by simulating candidate plans and comparing to the observed action; Csibra & Gergely 2007 teleological
stance). Malle 1999 (the "reason" engine for intentional action is a distinct causal system from physical cause).
Reuses `hdlab.goal_register` (PINNED desire/intention lexicon) composed with the result-state machinery below --
already built and measured as the DOMINANT narrative causal category (35.9% of TellMeWhy non-adjacent causes; SOLVED
`sdrt_discourse_coherence_reader.../SOLVED.md`).

**Step 2c (MENTAL/APPRAISAL branch) -- affect-congruent mental cascade. PINNED, thin implementation.**
Appraisal theory (Ortony/Clore/Collins; Scherer) -- an event's outcome is appraised by an experiencer and produces a
congruent-valence mental/emotional reaction that becomes the next event's antecedent state. Currently a coarse valence-
sign-congruence check (`hdlab.affect_lexicon.AffectLexicon.valence`); this is the WEAKEST-fidelity leg (see Step 2 of
`gen_causal_type` -- a bare `va*vb>0` test) and the one most in need of `hdlab.occ_appraisal`'s fuller appraisal
dimensions (desirability/praiseworthiness/expectedness), not just sign-congruent valence.

**Step 3 -- derive B's PRECONDITION. PINNED mechanism (STRIPS = the computational-level account of the brain's forward
model), OUR-INVENTION coverage.** Schank & Abelson 1977 (scripts: an ACT has ENABLING CONDITIONS and a RESULT);
Fikes & Nilsson 1971 (STRIPS precondition/effect as the computational-level formalization); Zwaan & Radvansky 1998
(event-indexing: the situation model tracks state dimensions updated by events and consulted by later events).
`hdlab.world_state_register.WorldState`/`PreCheck` implements exactly this shape (an event's precondition is
checked against the CURRENT register state, at story-time T) but its verb coverage is narrow (only the `USE` class:
"agent must HAVE the object used"). `hdlab.possession_operators` (FrameNet-derived GIVE/GET/LOSE + Donor/Recipient/
Theme roles) broadens the EFFECT side but not general non-possession preconditions.

**Step 4 -- SATISFACTION CHECK is the causal link. PINNED.**
van Dijk & Kintsch 1983 (situation-model updating); Haviland & Clark 1974 (an unmet precondition triggers a bridging
inference -- given-new contract). If A's derived Effect predicate type-and-value-matches B's PreCheck requirement, emit
a typed edge (CAUSE/ENABLE/PREVENT from Step 2a/2b's engine) with a confidence proportional to the match's specificity
(an exact predicate+value match > a class-level match > a CSKG-backoff hit). If A's Effect DEFEATS B's precondition or
goal (a LOSE/TOGGLE_OFF where B needs HAVE/OPEN), veto/suppress -- already built and validated as the selectivity gain
in `exp_genworldmodel_resultstate_v1.py` (the DEFEAT-suppression gate).

**Step 5 (deepening, not required for the cheap test) -- counterfactual necessity check. PINNED.**
Gerstenberg, Goodman, Lagnado & Tenenbaum (Counterfactual Simulation Model -- causal judgments compare the actual
outcome to simulated counterfactual outcomes with the candidate cause removed/altered; necessity + sufficiency both
enter human judgments, not just "did it happen after"). `hdlab.causal_reasoner.CausalGraph.graded_necessity` already
implements a graph-level approximation of this; extending it to re-run Step 2-4's SPECIFIC simulation with A ablated
(rather than a topological-graph necessity) is the CSM-faithful upgrade, named as a follow-on, not blocking.

**Step 6 -- abstain-to-recency-default. PINNED (a feature, not a gap).**
When no candidate A in the window produces a satisfying result-state for B, fall back to the plain recency prior
(`gen_prior`'s existing behavior) rather than inventing a link -- consistent with `patient_tendency`'s own
"abstain rather than hallucinate a type" discipline, validated as correct behavior (defers 6/6 on agentive
manipulation in the modern real-text serve).

**OUR-INVENTION-swept, explicitly (do not adopt as pinned):** the verb->force-class lexicon (FrameNet Causation-family
mapping, ~300 verbs); the patient-affordance property->lability map (labile half CSKG-corroborated, inert half
principled-but-unverified core physics); the GET/LOSE/TOGGLE and FrameNet-frame->operator mappings; the recency
WINDOW=4; the 4-cue tendency combination WEIGHTS (the additive rule itself is proven, the weights are swept); the
proposed VerbNet-Endstate-token map (new, untested); the CSKG-backoff precedence order.

## Asset survey -- verified on disk (paths are absolute-relative to `C:\AI\hd-instrument\`)

| Recipe step | Concrete asset (VERIFIED to exist) | Status / coverage caveat |
|---|---|---|
| Step 0 recency window | `experiments/exp_joint_causal_survival_v1.py::bind_edges(mode="generative"/"gen_prior")`, `WINDOW=4` | built, NOT yet in hdlab (experiments/ only) |
| Step 1 domain router | `hdlab/event_type.py::event_type(verb)` + `MENTAL_TRIGGER`/`MENTAL_OUTCOME` sets | LIVE in hdlab; MFS-only (no contextual WSD) -- mistypes homographs ("saw"), onomatopoeia |
| Step 2a verb force-class | `hdlab/force_dynamics_typer.py::force_dynamic_type()`; `hdlab/force_dynamics_lexicon.py::build_force_lexicon()` | LIVE in hdlab (behind `causation_typed` flag); ~300 verbs, FrameNet Causation family, PREDATES any test gold |
| Step 2a patient-specific tendency | `hdlab/patient_tendency.py::patient_tendency_signal()` / `type_with_full_tendency()` | LIVE in hdlab; SOLVED/EXCELLENT (held-out 1.000 vs magnitude-only 0.675 vs lexicon 0.500); modern real text 7/7 output-correct, defers 6/6 agentive; wiring into the live reader BLOCKED on the sense/attachment gate (every over-fire on unfiltered text is a WSD/attachment error) |
| Object dispositions/affordances (broad backoff) | `hdlab/grounded_semantic_graph.py::GroundedSemanticGraph` (WordNet++ nodes; ConceptNet edges kept: `RelatedTo,IsA,PartOf,HasA,UsedFor,CapableOf,AtLocation,Causes,HasProperty,MadeOf,HasSubevent,HasPrerequisite,MotivatedByGoal,ReceivesAction,...`; PPR spreading activation) | LIVE in hdlab; SOLVED (ladder + WiC twin control); reaches the 5.95M-edge CSKG substrate (`data/grounding_testbed/cskg.tsv.gz`, `data/cskg_foundation_v1/`) |
| Step 2a result-state (effect) generation | `hdlab/world_state_register.py::WorldState/Effect` (GET/LOSE/TOGGLE_ON/TOGGLE_OFF/USE lexicon, hand-seeded); `hdlab/possession_operators.py` (FrameNet-derived GIVE/GET/LOSE + Donor/Recipient/Theme roles, broader coverage) | Both LIVE in hdlab (behind `track_world_state`); composed+proven in `experiments/exp_genworldmodel_resultstate_v1.py` (GOAL-subset CI-sep win, n=92) |
| Step 2a result-state, BROADER (NEW asset found this cycle) | `nltk.corpus.verbnet.frames(classid)` -- `semantics` field carries `cause(Agent,E)` + `state(result(E), Endstate, Patient)` predicates for ~270 change-of-state/possession/motion classes | VERIFIED LIVE by direct probe this cycle (see below) -- NOT currently parsed anywhere in hdlab/experiments (only `classids`/`lemmas`/`themroles` are used, in `hdlab/predicate_argument_frontend.py`, `hdlab/director_kb.py`, `hdlab/patient_tendency.py`). Endstate is a class-level placeholder token, not auto-resolved to a concrete state string -- needs a small per-class map (new, ~1 day) |
| Step 2b goal/inverse-planning | `hdlab/goal_register.py` (PINNED desire/intention lexicon); `experiments/_sdrt_coherence.py` (goal-causation engine, SOLVED, CI-sep on GOAL subset) | goal_register LIVE in hdlab; the coherence reader's goal engine is SOLVED but NOT yet promoted to hdlab |
| Step 2c affect congruence | `hdlab/affect_lexicon.py::AffectLexicon.load().valence()`; `hdlab/affect_register.py`; `hdlab/occ_appraisal.py` (fuller appraisal dims, underused) | LIVE in hdlab; valence-sign-congruence is the current (thin) implementation; occ_appraisal is a named upgrade |
| Step 3 B's precondition | `hdlab/world_state_register.py::PreCheck` (USE-class only, narrow); VerbNet `state(during(E),...)`/`has_possession` predicates (same NEW asset as above); CSKG `HasPrerequisite`/`UsedFor` via `experiments/exp_causal_reasoner_cskg_v1.py::build_cskg_causal/cskg_causal` (final backoff) | PreCheck narrow; VerbNet-predicate route NEW/unbuilt; CSKG backoff MEASURED TODAY at only 2.16% coverage bound on MAVEN gold pairs (`cskg_coverage_bound_all_gold: 0.0216`) -- usable only as a sparse tie-breaker, not the primary mechanism |
| Step 4 satisfaction check | new, trivial (~20 lines): typed predicate-name+value match between `Effect` and `PreCheck` shapes already defined in `world_state_register.py` | NOT built yet; the dataclass shapes make it mechanical |
| Step 5 counterfactual necessity | `hdlab/causal_reasoner.py::CausalGraph.graded_necessity` | LIVE in hdlab; operates on the ABSTRACT graph today, not the Step 2-4 generated state -- named deepening, not blocking |
| Step 6 recency default | `experiments/exp_joint_causal_survival_v1.py::bind_edges(mode="gen_prior")` | built, not yet in hdlab |
| Live wiring point | `hdlab/causation_typing.py::TypedCausalLink`, `read_typed_causation()`, `is_foregrounded_event()` (Hopper-Thompson event-hood gate), `force_engagement_score()` | LIVE, default-off behind `causation_typed` in `situation_reader`; the composition point for everything above |

**Live VerbNet probe (run this cycle, not asserted from memory):**
```
>>> from nltk.corpus import verbnet as vn
>>> vn.frames('other_cos-45.4')[6]['semantics']   # "Tony broke the piggy bank open with a hammer."
[{'predicate_value': 'cause', 'arguments': [{'type':'ThemRole','value':'Agent'}, {'type':'Event','value':'E'}]},
 {'predicate_value': 'state', 'arguments': [{'type':'Event','value':'result(E)'}, {'type':'VerbSpecific','value':'Endstate'}, {'type':'ThemRole','value':'Patient'}]},
 {'predicate_value': 'Pred', ...}, {'predicate_value': 'use', ...}]
```
This is a real, generic `cause(Agent,E) -> state(result(E), Endstate, Patient)` STRIPS template straight from a
linguistic resource -- exactly the shape Step 3/4 needs, for classes far beyond possession (dry, break, fragment,
cook, wet, freeze, ...).

## Buildable architecture

```python
def compute_causal_link(A, B, window_events, force_lexicon, verbnet_endstate_map, cskg):
    """A, B: events with .verb, .agent, .patient, .clause_tokens, .outcome_tokens.
    Returns (score in [0,1], edge_type in {CAUSE,ENABLE,PREVENT,None}, mechanism_tag)."""
    typeA, typeB = event_type(A.verb), event_type(B.verb)
    score, edge_type, mechanism = 0.0, None, None

    if typeA == "PHYSICAL":
        endstate_A = detect_endstate_reached(A.outcome_tokens)                 # force_dynamics_lexicon
        force_type = type_with_full_tendency(A.agent, A.verb, A.patient,       # patient_tendency
                                              A.clause_tokens, endstate_A, force_lexicon)
        eff_A = derive_result_state(A, verbnet_endstate_map)                   # NEW: world_state_register
                                                                                #      + possession_operators
                                                                                #      + verbnet cause/state frame
        pre_B = derive_precondition(B, cskg)                                   # NEW: world_state_register.PreCheck
                                                                                #      + verbnet precondition frame
                                                                                #      + CSKG HasPrerequisite backoff
        if satisfies(eff_A, pre_B):                                            # NEW: ~20-line predicate match
            score, edge_type, mechanism = confidence(force_type, eff_A, pre_B), force_type, "force-dynamic-result-state"

    if typeA in MENTAL_TRIGGER and A.agent == B.agent:
        goal = goal_register.detect(A.clause_tokens, agent=A.agent)            # goal_register (existing)
        if goal and result_state_matches_goal(derive_result_state(B, verbnet_endstate_map), goal):
            score, edge_type, mechanism = max(score, GOAL_CONF), edge_type or "CAUSE", mechanism or "inverse-planning"

    if typeA in MENTAL_TRIGGER and typeB in MENTAL_OUTCOME:
        va, vb = AffectLexicon.load().valence(A.verb), AffectLexicon.load().valence(B.verb)   # affect_lexicon
        if va is not None and vb is not None and abs(va) > 0.1 and abs(vb) > 0.1 and va * vb > 0:
            score, mechanism = max(score, 0.4), mechanism or "affect-congruence"

    return score, edge_type, mechanism   # 0.0 -> caller falls back to recency-default (gen_prior)
```
`derive_result_state`/`derive_precondition`/`satisfies` are the only genuinely NEW code; everything they call
(`world_state_register`, `possession_operators`, `patient_tendency`, `force_dynamics_typer/lexicon`, `event_type`,
`affect_lexicon`, `goal_register`, `grounded_semantic_graph`/CSKG) is a validated, on-disk, glass-box asset. This is
composition, not invention -- consistent with the SOLVED result-state world-model's own recommendation
("compose the landed change-of-state organs -- the substrate already had the result-state schema").

## Measurement plan (MAVEN-ERE valid, honest metrics)
Reuse `experiments/exp_joint_causal_cskg_v1.py` verbatim (loader, detection, bootstrap) and add one arm:
- **precision-on-fired** = correct / fired-between-two-gold-events -- THE decisive metric per this problem's own
  methodology note (recall/survival is a density-confounded FREE axis; precision is the BINDING axis). Compare
  `content_sensitive` against `connective` (0.2347), `contiguity_floor` (0.1864), `generative` (0.1044),
  `generative_cskg` (0.1043) -- ALL FOUR, doc-level paired bootstrap (`boot_prec_diff`, already written).
- **edge recall (all/marked/unmarked)** -- informational only, report but do not gate on it (today's own scan proved
  a density flood matches recall for free).
- **shuffled_twin of `content_sensitive`** must lose CI-separated (rules out "any plausible-looking edge set scores
  this well" -- the same control every arm in this problem has already used).
- **mechanism diagnostic**: among `content_sensitive`'s correct fires, what fraction are cases where CSKG's blunt
  lemma-pair lookup (`cskg_score`) would have MISSED (no edge) but the STRIPS/VerbNet result-state/precondition
  match fired correctly? This is the direct proof that content-sensitivity (not "a bigger KB") is the source of any
  gain -- the point this whole investigation exists to test.
- **balanced hard-negative accuracy**: report but flag ABSTENTION-DOMINATED (already proven ~chance/uninformative
  for a high-precision/low-recall arm in this exact harness) -- do not headline it.

## Cross-thread synthesis
This composes THREE already-SOLVED problems that never wired to each other for pairwise (A,B) causal typing:
(1) `causation_typing_needs_a_patient_tendency_estimator` (the specific-object force computation), (2)
`build_the_generative_result_state_world_model` (the result-state rollout, whose own P1 next-step names "a
directed multi-step plan/script rollout ... over a curated result-state + plan foundation" -- this note's Step 2a/3/4
is the SINGLE-STEP version of exactly that lever, scoped to physical force-dynamic causation rather than goal
means-ends), and (3) `sdrt_discourse_coherence_reader_for_...causal_inference` (whose SOLVED explicitly names "the
causal reasoner's own content-sensitive generative rollout P1 (force_dynamics + goal_register + belief_partition +
affect_register)" as the one remaining lever shared by three consumers). Today's `exp_joint_causal_cskg_v1` refutation
is the fourth convergent data point (after CSKG 17.3% on TellMeWhy goal-means-ends, CSKG 34% on goal->action edges,
and now CSKG 2.16% on MAVEN causal pairs) that RETRIEVAL is coverage-bounded by construction on every axis this
substrate has tried it on -- reinforcing rather than merely repeating the prior finding, because this is the first
time the edge-gap-vs-vocab-gap DIAGNOSTIC (63.4% vocab-covered, 2.16% edge-covered) has been measured directly,
making the mechanism claim ("a KG cannot know THIS gate's disposition, only typical dispositions") an empirical
result rather than an inference.

## Substrate-product implications (plain terms, no jargon)
Right now the reader's best guess at "why did this happen" is checking whether the verb belongs to a small list of
"causing" words (about 300 of them) -- it recovers only about 1 in 20 of the causal links a human reader would find,
and even when it does fire, it is wrong more often than a much dumber "things mentioned near each other are probably
related" guess. We already separately built, and separately proved correct, several pieces of a much better approach:
a tool that reads whether a SPECIFIC object (a ball, a gate, a piece of cloth) tends to do something on its own; a
tool that tracks who currently has what and whether something is open or shut; and a tool that reads a person's want.
None of these three tools currently talk to each other for this specific job. This note is the plan to wire them
together into one pipeline that imagines "what does this specific action do to this specific thing" and then checks
"does that satisfy what the next action needs" -- the same way a person works out that a story detail matters. The
plan also found a genuinely new, free resource (a linguistics dictionary already installed on this machine) that
directly states, for hundreds of English verbs, "this verb causes a resulting state" in exactly the shape needed,
which nobody had read into the system yet. Risk: this could still fall short, for the same reason the object-tool
above sometimes gets confused -- the reader does not yet reliably know WHICH MEANING of an ambiguous word is meant in
context, and that gap caps every piece downstream of it, not just this one.

## Citations (verified count: 13 distinct primary sources, all previously used and cross-validated on this
substrate's own SOLVED files with matching journal/year details, plus 1 live on-disk API probe this cycle)
1. Battaglia, Hamrick & Tenenbaum 2013, PNAS 110:18327 -- intuitive physics engine / forward simulation.
2. Gerstenberg, Goodman, Lagnado & Tenenbaum -- Counterfactual Simulation Model of causal judgment.
3. Talmy 1988 -- force dynamics (Agonist/Antagonist, tendency, causing/enabling/preventing/letting).
4. Wolff 2007, JEP:General 136 -- force theory of causation (CAUSE/ENABLE/PREVENT truth-table).
5. Wolff & Song 2003, Cog. Psych. 47:276-332 -- verb choice tracks force vectors.
6. Wolff & Barbey 2015, Front. Hum. Neurosci. 9:1 -- force-vector-sum computational account.
7. Baker, Saxe & Tenenbaum 2009, Cognition 113:329 -- inverse planning for intentional action.
8. Csibra & Gergely 2007 -- teleological stance.
9. Malle 1999 -- reason vs. cause, dissociable folk-explanatory systems.
10. Graesser, Singer & Trabasso 1994, Psych. Review 101:371 -- constructionist causal-antecedent search.
11. Schank & Abelson 1977 -- scripts, ACT preconditions/results.
12. Fikes & Nilsson 1971 -- STRIPS precondition/effect formalism.
13. Zwaan & Radvansky 1998, Psych. Bull. 123:162 -- event-indexing model.
14. Haviland & Clark 1974 -- given-new bridging inference. / van Dijk & Kintsch 1983 -- situation-model updating.
15. Jack et al. 2013; Fischer, Mikhael, Tenenbaum & Kanwisher 2016; Saxe & Kanwisher 2003 -- physical/mental domain
    dissociation (network-level, not claimed at the class-label level).
Plus: Ilievski, Szekely & Zhang 2021 (CSKG, arXiv:2012.11490) for the refutation asset, and a live
`nltk.corpus.verbnet.frames()` probe run this cycle (not from memory) confirming the `cause`/`state(result(E),...)`
predicate structure exists and is unused in this codebase.

## TLDR (plain English)
We figured out, step by step, how a person works out that one thing caused another when the story never says
"because": they imagine the specific action's effect on the specific thing it acted on, then check whether that
outcome is exactly what the next action needed to happen. We already have working, separately-tested pieces of every
step of that (does this ball tend to roll, does this person now have the key, does this character want the same
thing) -- they've just never been chained together for this exact job, and today's test proved that grabbing a giant
ready-made fact-list instead (rather than reasoning it out) cannot substitute, because a fact-list only knows typical
pairings, not what happened in THIS sentence. We also found a free, already-installed dictionary resource that spells
out "this verb causes this kind of resulting state" for hundreds of verbs, unused until now.

## QUESTIONS
None blocking. One judgement call for whoever builds this: whether to scope the first build to the PHYSICAL/force-
dynamic branch only (Step 2a, the highest-confidence piece, already has a proven per-component estimator) or to
include the GOAL branch (Step 2b) in the same pass -- the GOAL engine is already SOLVED separately and reuse is cheap,
but composing both at once makes a HARD-FAIL harder to diagnose (two new failure surfaces at once). I'd build and
measure Step 2a alone first, since the measurement harness (`exp_joint_causal_cskg_v1.py`) already isolates arms
cleanly and a clean physical-only result is more diagnostic.

## NEXT STEPS (priority-ordered)
1. **Build `derive_result_state`/`derive_precondition`/`satisfies` + the VerbNet endstate map (~30-40 classes) and
   run the `content_sensitive` arm** against the pre-registered HARD-PASS/HARD-FAIL above. Cheapest, most direct test
   of this note's central claim. (~1 day; the harness needs zero changes.)
2. **If HARD-PASS: promote to hdlab behind `causation_typed`'s existing default-off gate**, wiring through
   `hdlab/causation_typing.py::read_typed_causation` (the composition point already exists).
3. **If HARD-FAIL: run the literal-subset diagnostic** (gate to patient_tendency's own validated-literal cases) before
   concluding anything -- per the pre-registered escape-hatch above, this converts an ambiguous null into either
   "confirms the meaning-channel is the blocker" (actionable: prioritize backlog item #1, wiring `meaning_foundation`
   into `read()`) or "the mechanism itself needs rework" (a genuinely new finding).
4. **Either way, extend `derive_precondition` with the VerbNet `during(E)` precondition predicates** (not just
   `state(result(E),...)` effects) -- this note only probed the effect side; the precondition side of the same
   resource needs its own 30-minute probe before Step 3 is considered fully scoped.
5. **Do NOT re-propose:** broadening the causal typer with more CSKG edges as the primary fix (REFUTED today, 2.16%
   coverage bound, edge gap not vocab gap); a bigger hand-curated force-verb or affordance lexicon as the primary fix
   (diminishing per-rule returns, named in the FULL_CHAIN scan); scoring this on recall/whole-subgraph-survival alone
   (density-confounded, proven repeatedly in this problem's own history).
