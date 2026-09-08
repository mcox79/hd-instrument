# CONTEXT BACKUP / HANDOFF -- build_the_generative_result_state_world_model (2026-09-07)
**Purpose:** full recovery entry point if this SOLVER session compacts. Read this FIRST, then SOLVED.md + the
three RESEARCH_*.md notes below. Everything here is on disk and witnessed.

## Scope / rules (solver session, Opus 4.8)
Write ONLY `experiments/`, `verification/`, `notes/problems/build_the_generative_result_state_world_model/`.
NOT hdlab/ (strategy lands, Q111), NOT preregs/**, NOT arm_key*. data/foundation READ-ONLY. NO external LLM at
inference. Finish with SOLVED.md; validate `python tools/problem_ledger.py --check`. A rigorous located negative
is a FULL PASS. Bash cwd resets -> prefix `cd /c/AI/hd-instrument &&`; `export PYTHONIOENCODING=utf-8`.

## The problem
The reasoners (causal/temporal/coherence/who-did-what) are near-perfect on GOLD relations but slump end-to-end
because they RETRIEVE links (coverage-bound). Build the GENERATIVE result-state world-model: simulate an action
forward to a result-STATE, check vs the goal-STATE, feed top-down into extraction. Turn a subset win into a
full-population CI-sep win on a consumer's MODERN gold (recommended: SDRT non-adjacent TellMeWhy), twin losing,
no reasoner regressing. A located negative naming the exact missing knowledge is a full pass.

## HEADLINE STATE (as of this backup)
Filed **SOLVED** (located negative + subset positive; owner iterating). The generative result-state rollout is
BUILT + brain-faithful; GOAL-subset CI-sep win (0.380 vs base 0.293, twin loses); full-population LOCATED
NEGATIVE. Deep full-chain brain-foundationality evaluation (3 cited neuroscience probes) CORRECTED the plan and
found the binding wall. 5 build cycles triangulated the wall to ONE upstream dependency.

## THE CORRECTED 100%-BRAIN-FOUNDATIONAL CHAIN (from RESEARCH_full_chain_brain_foundationality_eval_2026-09-07.md)
The deep eval caught THREE non-brain-foundational substitutions (all the SAME correction: stop building
feed-forward scorers; build ONE recurrent generative predict->error->update->roll-forward loop):
1. **Reachability: SR/PPR is the WRONG primitive** (occupancy under fixed policy; fails transition-revaluation;
   already lost as D7 -- ORGAN_MAP prohibits rebuilding on the pinned equation). Faithful = model-based
   generative forward simulation + goal-state TEST (Baker-Saxe-Tenenbaum inverse planning; hippocampal rollout,
   Mattar-Daw) -- REUSE the landed `causal_reasoner` traversal (reachability + cut-&-re-propagate = Pearl). SR
   demoted to an optional NEED prioritizer only.
2. **Generation: compose-and-late-fuse is a patchwork.** Faithful = ONE unified generative event-model (Franklin
   2020 SEM; Kuperberg 2021; Rabovsky 2018 N400) with the engines (force_dynamics/goal/affect/ToM) as structured
   PRIORS over the shared `bound_event_backbone` state (LANDED default-off), driven by the built-but-unwired
   prediction-error loop (`predictive_reader` forward + `n400_coherence_monitor` backward) = "the single biggest
   fidelity-vs-wiring gap."
3. **Decision: additive+softmax alone can't pick a cause** (monotone=argmax; correlated cues double-count).
   Faithful = signed-PAIRWISE coherence constraint satisfaction (Thagard ECHO 1989/1998 -- the missing citation;
   Kintsch signed matrix) + DDM/LCA commit, INSIDE the recurrent top-down loop (eager-but-revisable,
   Christiansen-Chater; predict MEANING not word-form, Nieuwland 2018).
~60% of the corrected chain is already built default-off. hdlab wiring = strategy's (Q111).

## THE BINDING WALL (triangulated from 5 independent builds -- all converge here)
The causal reasoner's U6 phase diagram: on real narrative, multi-hop advantage EQUALS edge-correctness c and is
INDEPENDENT of density, rising to +0.81 at c=1. So the reasoning MECHANISM is not the bottleneck; UPSTREAM
edge-generation is. The 5 builds:
- coverage-tiers: DEEP_MULTISTEP 51% of goal means-ends are multi-step plans (beyond 2-hop).
- precise-trace: topical content is load-bearing (removing crashes 0.277->0.102) BUT 91% of errors; extraction
  NOT the loss point (0.98 recall).
- ECHO decision: mechanism PROVEN on constructed control (coalition beats lone-topical; uniform-inhibition twin
  = no-op), real-data FLAT (candidate causal links sparse 0.11).
- generative edges: generate>retrieve confirmed (0.328 vs cskg 0.277); phase-diagram optimum (tau=1.0: flood
  0.258 -> 0.328, +0.070) -- movable operating point NOT a ceiling; but class-level engines
  precision-coverage-bound (not CI-sep over additive).
- participant-binding: surface content-noun binding FAILS (sparser + lower acc) because the shared participant
  is coref-resolved/pronominal -> needs REAL coref.
**=> The wall is UPSTREAM causal-edge correctness c: participant-bound content-sensitive result-state generation
over COREF-RESOLVED participants (E3, NEEDS_ADAPTER) reading the MEANING CHANNEL (meaning_foundation, LATENT) --
both hdlab/latent = strategy's (Q111).** The solver-side mechanisms are BUILT + proven-in-mechanism; they
deliver once fed correct/dense edges (causal_reasoner 1.000 on clean DAGs; U6 advantage=c).

## KEY NUMBERS (TellMeWhy non-adjacent, n=256, GOAL 92; base 0.277, topical 0.250, string-id n/a)
- objmatch/gen_union (prior best) 0.309; rs_refine (result-state) GOAL 0.380 vs base 0.293 (+0.087 CI[0.022,0.152]).
- top-down stack (multi-step + additive integration) GOAL 0.467 (+0.174 CI-sep, twin loses), full 0.316.
- oracle ladder: base 0.277 -> surface 0.293 -> perfect-goal 0.441 (+0.148 forward-model) -> perfect-all 0.773
  (+0.332 other engines) -> gold 1.000 (+0.227 extraction/selection). Selection loss ~25% (oracle_goal 0.75).
- generative edges coh 0.328 vs cskg 0.277 vs additive 0.309-0.316; participant-bound 0.312 (no lift).

## FILES (all mine; reuse, don't rebuild)
Cells: exp_genworldmodel_{resultstate,upstream_verbnet,signal_loss_ladder,signal_loss_precise,topdown_stack,
coherence_decision,generative_edges,participant_bound_edges}_v1.py.
Witnesses (all green): test_genworldmodel_{resultstate 8/8, upstream_verbnet 3/3, signal_loss_ladder 4/4,
signal_loss_precise 5/5, topdown_stack 5/5, coherence_decision 5/5, generative_edges 4/4,
participant_bound_edges 4/4}.py.
Notes: SOLVED.md; RESEARCH_brain_fidelity_scan_2026-09-07.md (per-stage mechanism-diff + all-component audit);
RESEARCH_multistep_priors_and_options_2026-09-07.md (prior-drill + options); RESEARCH_full_chain_brain_
foundationality_eval_2026-09-07.md (the corrected chain, 3 neuroscience probes); THIS backup.
Data dirs: data/exp_genworldmodel_*_v1/metrics.json.

## LANDED ORGANS TO REUSE (from the drills)
causal_reasoner traversal (the rollout engine, reachability + Pearl counterfactual, 1.000 on DAGs);
force_dynamics_typer (Talmy/Wolff, 0.929 typing); goal_register (Levin, marked-goal recall 0.89);
world_state_register (STRIPS GET/LOSE/TOGGLE); possession_operators (FrameNet, 105 verbs); _tom_chain
(belief x goal -> action, BigToM); occ_appraisal (OCC affect check); graded_competition (additive
net_activation+softmax = decision stage a); bound_event_backbone (Franklin SEM shared event-state, default-off);
predictive_reader + n400_coherence_monitor (the prediction-error loop, built/unwired); goal_hierarchy_graph
(wired default-on). generalized_event_knowledge/GEK = DIRECTIONLESS (do NOT use for achievement).

## DO-NOT-REDO (measured; reopen ONLY with corrected upstream)
SR/PPR as the reachability engine (wrong primitive + lost as D7); GEK/co-occurrence as the achievement axis
(directionless -- scores spill>=buy); CSKG topical densification (dense != correct); bigger single-step VerbNet
lexicon (ties base -- wall is DEPTH); normalized_recurrence/uniform-inhibition settling for accuracy (monotone
no-op); surface content-noun participant-binding (too crude -- needs real coref); external LLM at inference.

## OPEN / NEXT (solver-side, not bottlenecked by the coref/meaning wall)
1. RESEARCH the participant-binding negative fully (dispatched 2026-09-07): the brain's entity-continuity /
   participant-binding mechanism for causal chains; why surface overlap is the wrong proxy; the faithful fix
   (real coref / discourse referents) -- confirm false-negative-from-upstream vs wrong-mechanism.
2. Real-coref participant binding = the faithful fix for cycle-2 (RESEARCH-CONFIRMED false-negative from the
   surface proxy). Mechanism is brain-foundational (DRT/Heim; Zwaan entity index; ACT-R/Centering; Kehler-Rohde)
   + already built (`world_state_entity_binding.EntityBinder` + `event_centrality_coref` + `bound_event_backbone`)
   + already MEASURED to WIN (resolved 0.1739 vs string-id 0.0589 CI-sep; who-has-what +0.148 CI-sep; oracle 0.62
   vs surface 0.17; surface-blind ACTIVELY HARMFUL 71.5%->0%). WIRING IT into the edge-generator requires the
   DOCUMENT-LEVEL reader: `SituationReader.read(conll_path)` -> `sm.events` with resolved agent/patient (the
   lightweight `_extract_events` used by my cells carries NO participants). That is the recurrent-loop/coref
   wiring = strategy's Q111. So: upstream excel/exceed is PROVEN on disk; the end-to-end wire is the hand-off.
3. FIDELITY-SCORE the Tier-6 organs occ_appraisal + goal_register (flagged "brain-fidelity unestablished") --
   independent of the edge wall; on the checklist (#5).
4. HAND-OFF to strategy (Q111): wire the recurrent loop -- turn on bound_event_backbone + wire
   predictive_reader/n400 + EST error-peak segmentation; wire E3 coref + meaning_foundation live. Then the
   model-based rollout over correct/dense edges + the ECHO decision deliver.

## CYCLE-3 UPDATE (2026-09-07) -- upstream prototyped end-to-end; EXCEL/EXCEED PROVEN at oracle
`exp_genworldmodel_resolved_referent_binding_v1.py` (witness 4/4) called the LANDED EntityBinder object-anaphora
resolver over spaCy participants to bind edges on resolved referents. ORACLE participant-binding (share the
gold-cause referent) + ECHO coherence BEATS additive CI-sep (oracle 0.324 vs 0.289, +0.0352 CI[0.004,0.070]) ->
the mechanism DELIVERS when binding is correct. Real recency object-anaphora is FLAT (0.293 == surface) -> the
residual sharpens to coref CORRECTNESS (recency too weak; full ACT-R/Centering document coref
`event_centrality_coref` closes it, needs document-level `read(conll)` -> sm.events wiring = Q111). No regress.
So: ALL solver-side components built + proven (8 cells + 8 witnesses, all green = the complete solver-side
prototype of the corrected chain); the hand-off is the document-level coref/meaning-channel wiring, and its
ceiling is quantified (+0.035 CI-sep at oracle).

## CYCLE-4 UPDATE (2026-09-07) -- goal-detection upstream AUDITED + CLEARED
`exp_genworldmodel_goal_detection_fidelity_v1.py` (witness 3/3): goal_register's Levin-class goal DETECTION is
LOAD-BEARING (twin->chance 0.496, Levin-twin +0.451 CI-sep) + HIGH-FIDELITY (balanced-acc 0.946, non-goal
rejection 1.000) but TIES a naive lexical floor -> 100% brain-foundational + load-bearing but NOT the
underperformance cause; CLEARED as an upstream suspect. Both upstream suspects now checked: goal-detection=clean;
coref/participant-binding QUALITY = the SOLE remaining lever (excel/exceed proven at oracle; needs the
document-level coref front-end, Q111). SOLVER-SIDE CONVERGED: 10 cells + 10 witnesses (all green); the only
remaining lever is out of solver scope (hdlab document-level coref/meaning-channel wiring). Last un-audited item =
occ_appraisal fidelity (not used in the rollout; needs emotion gold).

## CRON
Deepening cron `b258c5dd` (13,43 * * * *), prompt = "keep doing what you've been doing + consider the checklist".
Session-only, auto-expires 7 days. CANCEL + submit when the brain-mechanism bar is met AND the checklist yields
nothing more.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)
The generative result-state world-model: mechanism corrected to a recurrent generative loop (SEM shared state +
prediction-error loop + model-based rollout + ECHO decision); SR/PPR is the wrong reachability primitive; GEK is
directionless; the binding wall is upstream edge-correctness c (participant-bound generation over coref-resolved
participants + the latent meaning channel). Solver mechanisms built+proven; upstream wiring = strategy (Q111).

## CYCLE-5 UPDATE (2026-09-08) -- OPTIMIZED coref built; MECHANISM-TASK MISMATCH found
`exp_genworldmodel_optimized_coref_v1.py` (witness 4/4): ACT-R base-level-activation object-anaphora resolver
(Lewis-Vasishth, PINNED) resolves 181 anaphora vs recency 73 (2.5x = real organ-level win) but is FLAT on the
TellMeWhy causal-coherence decision (ACT-R 0.285 == recency == additive == twin), while the ORACLE excels
(+0.066 CI[0.027,0.106]). KEY: improving coref to fidelity did NOT move the decision because TellMeWhy cause-ID
is SINGLE-ANTECEDENT -- the multi-candidate object-CHAIN structure the ECHO coherence + participant-binding
machinery needs is rarely present. The earlier GOAL-subset win (0.380) was from the RESULT-STATE ROLLOUT, not the
coherence machinery. To show the coherence + coref chain EXCELS, use a MULTI-CANDIDATE causal-CHAIN gold (WIQA
multi-hop / who-did-what two-valid / narrative-chain), NOT TellMeWhy single-cause-ID. Coref upgrade is real +
no-regress; payoff is consumer-dependent. 11 cells + 11 witnesses (all green). The two live win-mechanisms on
TellMeWhy remain: result-state rollout (GOAL-subset +0.087 CI-sep) + the corrected chain at oracle binding
(+0.035-0.066 CI-sep); the coherence-chain machinery awaits a chain-structured consumer.
