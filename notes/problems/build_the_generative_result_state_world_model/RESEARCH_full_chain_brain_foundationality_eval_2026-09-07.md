# Deep brain-foundationality evaluation of the FULL Option-A chain (owner: "evaluate deeply all up the line, make sure it's 100% brain-foundational, research liberally")

**problem:** build_the_generative_result_state_world_model | **date:** 2026-09-07 | **status:** IN PROGRESS
(3 deep neuroscience probes dispatched; probe 1 landed, probes 2-3 pending). This is a pre-build gate: NO
component is built until every stage below is 100%-brain-foundational or the deviation is named + justified.

The chain under evaluation (Option A):
`prose -> EXTRACTION -> COREF/participant-binding -> MEANING CHANNEL -> GENERATIVE DIRECTED EDGE-GENERATOR ->
REACHABILITY ENGINE -> ACHIEVEMENT CHECK -> DECISION LAYER`, all inside a RECURRENT TOP-DOWN loop.

Per stage: the brain's ACTUAL computation (PINNED vs contested, cited) -> our fidelity -> verdict + the
faithful fix.

---

## Stage 5 (evaluated first — it drove the whole re-plan) — REACHABILITY ENGINE
**CORRECTED by probe 1: SR/PPR is the WRONG PRIMITIVE. Use model-based generative forward simulation with an
explicit goal-state test.**
- Brain (PINNED): goal-directed multi-step inference = model-based FORWARD SIMULATION / rollout with a goal
  test (hippocampal forward replay/preplay, Pfeiffer-Foster 2013; utility-ordered simulation, Mattar-Daw
  2018), over a LEARNED generative transition model (Tolman-Eichenbaum Machine, Whittington 2020: structural
  code g reused across environments); at the comprehension level = Baker-Saxe-Tenenbaum 2009 inverse planning
  (run the rational forward planner, invert by Bayes); the discourse product = Trabasso causal network.
- SR (Dayan 1993; Stachenfeld 2017) is PINNED but for PREDICTION/VALUATION under a FIXED policy = discounted
  OCCUPANCY. It supports reward-revaluation but FAILS TRANSITION-revaluation (Momennejad 2017; Russek 2017) --
  and narrative means-end is a transition-structure question over NOVEL plans, exactly SR's failure regime. On
  a dense graph SR concentrates on hubs, washing out the goal signal (why our D7 degraded with scale).
- DISK: D7 (`hdlab/successor_representation.py`) is the genuine closed form, RUN AND LOST (0/24, degrades with
  scale); ORGAN_MAP carries an explicit PROHIBITION against building/scaling it on the pinned equation.
  Goal/means-end comprehension has NO pinned neural equation (audit 2b) -- so SR is not "faithful to" anything
  here.
- VERDICT: **NOT faithful as the engine.** Faithful = model-based generative rollout + goal-state test. REUSE
  our landed `causal_reasoner` traversal (forward reachability `descendants` + cut-and-re-propagate `is_necessary`
  = Pearl intervention -- this already IS a model-based rollout with a goal test) as the engine; DEMOTE SR to
  an optional prior/prioritizer (the NEED term for which plans to simulate first, Mattar-Daw). The learned
  transition model = an offline FOUNDATION asset (TEM-style), glass-box rollout at runtime (no LLM, no
  train-at-inference).

## Stage 1 — EXTRACTION (prose -> events + participants)
- Brain (PINNED): incremental, PREDICTIVE parsing (left-corner; LIFG/pMTG), roles by the extended Argument
  Dependency Model (actor-first prominence; Bornkessel-Schlesewsky) -- top-down expectation constrains the
  parse online.
- Ours: spaCy arc-eager (greedy, HARD-COMMIT, feed-forward). NOT faithful in mechanism (wall-map Wall 2). BUT
  measured event-extraction recall 0.98 on this gold -> NOT the binding loss point here.
- VERDICT: not 100% faithful (hard-commit vs predictive/graded), but not the binding gap for THIS task. The
  faithful version already exists in part (the globally-normalized graded parser SOLVED) and is completed only
  by receiving TOP-DOWN expectation from the situation model (the recurrent loop, Stage 7). FLAG: fidelity here
  is realized by closing the loop, not by a new parser.

## Stage 2 — COREF / PARTICIPANT BINDING
- Brain (PINNED): discourse referents maintained in the situation model (Heim/Kamp file-change semantics);
  ATL/hippocampal binding keeps "who wanted X" identical to "who did Y".
- Ours: E3 coref (NEEDS_ADAPTER, not on the live path) + a lenient surface-head, pronoun-permissive binding in
  the rollout. Partial.
- VERDICT: the generative rollout MUST bind result-states to COREF-RESOLVED participants (the brief's "over the
  resolved participants"); surface-head binding is a stand-in. FAITHFUL fix: wire E3 live as the participant
  source. FLAG: upstream to wire; small on single-protagonist TellMeWhy, load-bearing on multi-character prose.

## Stage 3 (this is the KNOWLEDGE dependency) — MEANING CHANNEL
- Brain (PINNED): ATL amodal conceptual hub (Controlled Semantic Cognition; Lambon-Ralph/Patterson/Rogers) --
  the source of the result-state predicates and the resolved-concept identities the rollout reads over.
- Ours: `meaning_foundation` is LATENT (no live read()-time consumer). The result-state predicate knowledge the
  DEEP-multistep rollout needs (verb->result-state, plan/script chains) rides on this + the consolidation gate.
- VERDICT: LATENT -> must be wired live first; this is the named knowledge-foundation dependency (per
  KNOWLEDGE_LEVER note: curated foundation through the consolidation gate FIRST, then online propose-and-verify).
  FAITHFUL and admissible as an OFFLINE static asset (invariant = no LLM at inference, not no offline asset).

## Stage 4 — GENERATIVE EDGE-GENERATOR
**CORRECTED by probe 2: compose-and-late-fuse is faithful at the PRIORS level but a patchwork at the MECHANISM
level. Faithful = ONE unified generative event-model with the engines as structured priors, not five scorers.**
- Brain (PINNED): comprehension runs ONE unified generative event/situation model -- Franklin 2020 Structured
  Event Memory (SEM); Kuperberg 2021 hierarchical generative framework; Rabovsky 2018 (the N400 is the update
  of a SINGLE event representation, reproducing 16 effects). Domain engines ARE modular at the neural level
  (intuitive physics parietal/premotor, Fischer 2016; intuitive psychology/ToM TPJ/mPFC -- dissociable), so
  separable engines are correct -- BUT they are invoked as generative PRIORS INSIDE one loop (Wong-Tenenbaum
  2023/2025 on-demand model synthesis; Hassabis-Maguire constructive binding), not run alongside and summed.
- The 3 missing pieces vs a compose-and-score design: (1) a single shared event-state every engine reads AND
  writes; (2) the generate-top-down -> precision-weighted-ERROR -> update control loop; (3) the recurrent
  forward ROLLOUT.
- DISK (the decisive corroboration): the shared event-state is ALREADY a landed organ -- `bound_event_backbone`
  (Franklin 2020 SEM; Zwaan-Radvansky), default-OFF. The prediction-error control loop is BUILT at 4 levels
  (`predictive_reader` forward / `n400_coherence_monitor` backward / `slot_attention_wm` / `gap_detector`) and
  wires NONE into the live reader = "the single biggest fidelity-vs-wiring gap." CAVEATS: `world_state_register`
  is a STATE organ, NOT a sequencing/causal-chainer (needs a separate ordering mechanism); event segmentation
  is a fixed 5-sentence window = OUR-INVENTION placeholder (faithful = EST error-peak boundaries, Zacks 2007);
  `occ_appraisal` + `goal_register` are in the UN-AUDITED Tier 6 (brain-fidelity UNESTABLISHED -> fidelity-score
  before leaning on them).
- VERDICT: keep the engines (faithful priors); KILL the late-fusion; wrap them in ONE generative
  predict -> error -> update -> roll-forward loop over the shared `bound_event_backbone` state.

## Stage 6 — ACHIEVEMENT CHECK (does the reached state achieve the goal-state?)
- Brain (PINNED): the goal-test of inverse planning (Baker-Saxe-Tenenbaum) -- would a rational agent pursuing G
  reach this state; mPFC value/goal-status tracking; hierarchical subgoal prediction errors (Ribas-Fernandes
  2011, ACC/mPFC).
- Ours: type-matched achievement + DEFEAT-suppression (built). Faithful IN KIND if it is the TERMINAL goal-test
  of the rollout (Stage 5), not a separate lexical heuristic.
- VERDICT: faithful as the rollout's goal-test; keep it coupled to the rollout, not bolted on.

## Stage 7 — DECISION LAYER + the RECURRENT TOP-DOWN LOOP
**CORRECTED by probe 3: additive+softmax is faithful ONLY for the local independent-cue readout; "pick the
cause" needs a THREE-stage decision; and the whole chain MUST be a recurrent top-down loop (eager-but-revisable).**
- DECISION: additive log-linear + softmax = the exact Bayesian posterior ONLY under conditional cue
  independence (McClelland 2013; Massaro FLMP). Our cues are CORRELATED (reachability + achievement are both
  downstream of the same predicted result-state) -> a naive sum DOUBLE-COUNTS. And softmax settling is MONOTONE
  (= argmax) so it can never produce a COALITION winner (mutually-supporting cues outvoting a lone strong cue).
  Faithful "pick-the-cause" = 3 coupled stages: (a) log-linear combine with DECORRELATED Competition-Model
  validities (Bates-MacWhinney); (b) a signed-PAIRWISE constraint-satisfaction settle -- **Thagard ECHO
  1989/1998 "explanatory coherence as constraint satisfaction" is literally the cause-selection mechanism, the
  missing citation** (Kintsch signed matrix; Hopfield) -- where uniform inhibition is a proven no-op and a
  coalition beats raw argmax; (c) a DDM/LCA collapse for the task-triggered commit (Gold-Shadlen; Bogacz;
  Usher-McClelland). REUSE `graded_competition` for (a) ONLY; (b) is a genuinely NEW organ (the monotone
  `normalized_recurrence` is not it).
- ARCHITECTURE (PINNED): the chain MUST BE one recurrent top-down predictive loop (Rao-Ballard 1999; Friston
  2010; Kuperberg-Jaeger 2016) -- the situation/goal model feeds expectations DOWN into sense-selection,
  role-assignment, parsing, coref as it reads, and prediction error (N400/P600) flows UP to revise. The
  feed-forward pipeline of hard-committing silos is the dominant deviation (wall-map). NUANCE (Christiansen-
  Chater Now-or-Never): "recurrent" != global attractor relaxation and != indefinitely-open distributions --
  it is an EAGER per-token feedforward sweep whose commits are REVISABLE by top-down error (predict-and-revise),
  predicting MEANING features not word-forms (Nieuwland 2018 killed form-prediction). So the eager parser is not
  wrong to commit -- it is wrong to commit IRREVERSIBLY and PRE-SEMANTICALLY.
- THE UNIFICATION: the decision layer is the TOP of the same loop -- the chosen cause is the top-level
  hypothesis whose top-down predictions (result-state -> reachability -> achievement) are checked through the
  loop; local readouts use monotone softmax (a), global cause-selection uses signed-pairwise coherence (b), the
  commit is DDM (c). One computation, three scales.

---

## FINAL VERDICT — Option A as written is NOT 100% brain-foundational; the evaluation caught 3 substitutions
The deep pass replaced three convenient primitives with the brain's actual computations, and the three
corrections turn out to be the SAME correction at three scales: **stop building feed-forward scorers; build one
recurrent generative predict->error->update->roll-forward loop over a shared event-state.**
1. **Reachability**: SR/PPR (occupancy under a fixed policy; already lost as D7) -> model-based generative
   forward simulation with a goal-state TEST (Baker-Saxe-Tenenbaum inverse planning; hippocampal rollout;
   reuse the landed `causal_reasoner` traversal). SR demoted to an optional NEED prioritizer only.
2. **Generation**: compose-and-late-fuse engines -> ONE unified generative event-model (SEM/Kuperberg) with the
   engines as structured priors parameterizing a top-down prediction over the shared `bound_event_backbone`.
3. **Decision**: additive+softmax alone -> 3 stages (decorrelated log-linear + signed-pairwise ECHO/Kintsch
   coherence + DDM commit), and the WHOLE chain must be the recurrent top-down loop, eager-but-revisable.

## THE 100%-BRAIN-FOUNDATIONAL CHAIN (corrected)
```
ONE RECURRENT TOP-DOWN PREDICTIVE LOOP  (Rao-Ballard/Friston/Kuperberg; eager-per-token + predict-and-revise,
Christiansen-Chater; predict MEANING not form, Nieuwland):
  shared latent EVENT-STATE .......... bound_event_backbone (Franklin 2020 SEM)         [LANDED, default-off -> ON]
  structured generative PRIORS (parameterize the top-down next-state prediction):
     physics ......................... force_dynamics_typer (Talmy/Wolff)                [PINNED, landed]
     psychology (goal + belief) ...... goal_register + _tom_chain (Baker-Saxe-Tenenbaum) [landed; FIDELITY-SCORE goal_register]
     affect .......................... occ_appraisal (OCC)                               [landed; FIDELITY-SCORE (Tier-6 un-vetted)]
     change-of-state ................. world_state_register (STRIPS/Zwaan-Radvansky)     [landed; STATE only -> add sequencing]
  prediction ERROR (drives update + EST segmentation + revision of lower stages):
     forward ......................... predictive_reader (surprisal, meaning-not-form)   [BUILT, unwired -> WIRE]
     backward ........................ n400_coherence_monitor                            [BUILT, unwired -> WIRE]
  forward ROLLOUT (chain predicted states to the goal-STATE test) .. causal_reasoner traversal (reachability +
     cut-&-re-propagate = Pearl intervention); SR as optional NEED prioritizer only      [LANDED engine, reuse]
  DECISION = top of the loop, 3 stages:
     (a) log-linear combine, decorrelated Competition-Model validities .. graded_competition            [reuse (a) only]
     (b) signed-pairwise coherence settle (Thagard ECHO / Kintsch) ...... NEW ORGAN                     [BUILD]
     (c) DDM/LCA commit ................................................ new                            [BUILD]
  event segmentation ................. EST error-peak boundaries (replace fixed 5-sentence window)       [FIX]
  upstream (extraction/coref/meaning) receive top-down expectations FROM the loop (that IS their fidelity fix);
     meaning_foundation wired live + curated result-state/plan foundation via the consolidation gate    [WIRE/BUILD]
```

## Build/fix inventory (what is already faithful+landed vs what this evaluation says must be built/fixed)
- **Already faithful + landed (REUSE):** causal_reasoner traversal (the rollout engine), force_dynamics_typer,
  _tom_chain, graded_competition stage (a), bound_event_backbone (turn on), predictive_reader + n400 (wire).
- **BUILD (genuinely new, brain-foundational):** the signed-pairwise ECHO/Kintsch coherence settle (decision b)
  + DDM commit (c); the unified generative event-model wiring (engines as priors -> top-down prediction over
  bound_event_backbone -> precision-weighted error -> update -> roll forward); a sequencing/causal-chaining
  mechanism on top of world_state_register.
- **FIX (OUR-INVENTION placeholders):** EST error-peak segmentation (replace the 5-sentence window);
  fidelity-SCORE occ_appraisal + goal_register (Tier-6 un-vetted) before leaning on them; wire E3 coref live as
  the participant source; wire the LATENT meaning channel + the offline curated foundation.
- **DO NOT:** SR/PPR as the reachability engine (wrong primitive + lost); late-fuse engine scores; use
  `normalized_recurrence`/uniform-inhibition settling for accuracy (monotone no-op); predict word-forms; a
  feed-forward one-pass cascade; external LLM at inference.

**Scope note:** this is no longer a single solver cell -- it is the project's named MAIN EVENT (the recurrent
generative world-model), and ~60% of the pieces are already built default-off. It needs owner-level SEQUENCING:
close the loop over the shared event-state FIRST (turn on bound_event_backbone + wire predictive_reader/n400 +
EST segmentation), then the model-based rollout over it, then the 3-stage coherence decision -- each a
measurable step, each reusing a proven brain-foundational organ.
