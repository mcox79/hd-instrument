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

## CYCLE-6 UPDATE (2026-09-08) -- GLUCOSE (the RIGHT gold): coalition REFUTED on real narrative; topical/Trabasso is the signal
Owner: do the RIGHT gold (GLUCOSE narrative causal-chain, not the easy on-disk MAVEN-ERE), brain-foundationally
(no leak). Acquired GLUCOSE (pinned fetch_glucose_v1.py; train 65522). Built the corrected chain on GLUCOSE
>=3-candidate cause-selection (reasoner sees ONLY story+selected; dim-1..5 antecedents = offline gold).
`exp_genworldmodel_glucose_chain_v1.py` (witness 4/4). RESULT = rigorous LOCATED NEGATIVE: on the non-adjacent
coalition subset (n=735) TOPICAL connectivity 0.450 >> additive 0.376 > coherence 0.336 ~ coref 0.325;
coherence-additive -0.040 CI[-0.064,-0.016] (BELOW); coherence <= shuffled-edge twin 0.355 -> generated causal
edges NOT load-bearing. Coalition mechanism intact on the constructed control (W4) but REFUTED as the lever on
real narrative (across BOTH TellMeWhy + GLUCOSE) because generating CORRECT causal edges from text is the wall
(edge-correctness c, now confirmed on a CHAIN gold). KEY: the dominant BRAIN-FOUNDATIONAL signal for real
narrative cause-ID is ASSOCIATIVE/TOPICAL connectivity (Trabasso & van den Broek; Collins-Loftus) -- the
generative means-end + coalition ADD NOISE relative to it. Live win-mechanisms that carry: (a) topical/participant
connectivity; (b) result-state achievement check on marked-goal causes (TellMeWhy GOAL-subset +0.087 CI-sep).
Wall = edge-correctness = meaning-channel/knowledge-foundation (Q111). 12 cells + 12 witnesses (all green).

## CYCLE-7 UPDATE (2026-09-08) -- the edge-correctness FIX + the SOT question (owner)
`exp_genworldmodel_edge_correctness_fix_v1.py` (witness 4/4). SOT: no literal 'SOT' organ on disk -> read as
STRUCTURE-OF-TIME (causes-precede-effects; `temporal_reasoner` + iconicity position order); STATE-OF-THINGS
(`world_state_register`) already inside rs_fire. Built a DIRECTED causal-connectivity edge = topical *
directed-force/psych, SOT-gated, + state. On GLUCOSE coalition subset (n=735): (1) SOT IS LOAD-BEARING (SOT-gated
beats SOT-shuffled twin +0.060 CI[0.035,0.086]); (2) BUT does NOT beat raw TOPICAL connectivity (topical 0.450 >
sot_pos 0.419, sot_state 0.433, not CI-sep); (3) directed force/psych typing HURTS (-0.079 CI-sep below); the
TemporalReasoner ORGAN gives no lift (0.371) while the iconicity PRINCIPLE carries. ANSWER: yes incorporates SOT,
SOT is real, but neither SOT nor the landed typing organs CLOSE the edge-correctness wall -> the fix needs CORRECT
CAUSAL KNOWLEDGE (meaning-channel/foundation, Q111), not more typing/temporal organs.

## META-CONCLUSION (across all 13 cycles -- the durable finding)
On REAL narrative cause-ID (TellMeWhy + GLUCOSE), EVERY generated/typed causal signal (force/psych, CSKG, ECHO
coalition, directed typing, SOT-organ, coref-coalition) is net-flat-or-NEGATIVE vs simple ASSOCIATIVE/TOPICAL
connectivity, because generating CORRECT causal structure from text (edge-correctness c) is the unsolved wall.
The TWO things that DO carry, brain-foundationally: (a) topical/participant connectivity (Trabasso & van den
Broek causal-network connectivity; Collins-Loftus spreading activation); (b) the result-state achievement check
on MARKED-goal causes (TellMeWhy GOAL-subset rollout +0.087 CI-sep). SOT (temporal order) is load-bearing but
subordinate. The decision-layer coalition + generative typing are proven on CONSTRUCTED controls but refuted as
levers on real data. The single remaining lever = correct causal KNOWLEDGE = the meaning-channel/knowledge
foundation (Q111, strategy). 13 cells + 13 witnesses (all green). Reverify any via
`.venv/Scripts/python.exe verification/test_genworldmodel_<name>.py`.

## FULL FILE LIST (13 cells / 13 witnesses, all green; + 5 research/handoff notes + GLUCOSE fetch)
cells: exp_genworldmodel_{resultstate, upstream_verbnet, signal_loss_ladder, signal_loss_precise, topdown_stack,
coherence_decision, generative_edges, participant_bound_edges, resolved_referent_binding, goal_detection_fidelity,
optimized_coref, glucose_chain, edge_correctness_fix}_v1.py + fetch_glucose_v1.py.
witnesses: test_genworldmodel_{same 13 names}.py.
notes: SOLVED.md, RESEARCH_brain_fidelity_scan_2026-09-07.md, RESEARCH_multistep_priors_and_options_2026-09-07.md,
RESEARCH_full_chain_brain_foundationality_eval_2026-09-07.md, THIS backup.
gold acquired: data/corpora/glucose/ (train 65522; pinned fetch_glucose_v1.py; CC-BY-NC).

================================================================================
## >>> RESUME HERE (2026-09-08, pre-compaction) -- READ THIS BLOCK FIRST <<<
================================================================================
HEADLINE POSITIVE (the session's biggest win): SOT = the SITUATION MODEL (state-of-mind, tracks story state
across sentences) IS the missing piece. `exp_genworldmodel_sot_situation_model_v1.py` (witness
`test_genworldmodel_sot_situation_model.py` 3/3): conditioning cause-selection on the ACCUMULATED situation
model BEATS the pairwise topical baseline on GLUCOSE, LOAD-BEARING.
  * sot_accum 0.610 vs topical 0.450 = +0.1592 CI[0.117,0.200] CI-SEP (coalition subset n=735).
  * sot_accum vs PROPER info-free twin (marginal values permuted across candidates) 0.424 = +0.1850
    CI[0.146,0.225] CI-SEP -> LOAD-BEARING (the candidate->contribution mapping carries real signal).
  * sot_salience +0.034 CI-sep, sot_focal +0.027 CI-sep (secondary).
  MECHANISM: sot_accum = the candidate whose ADDITION to the running accumulated gist contributes the most NEW
  effect-relevant content = the event that INTRODUCES the effect's preconditions into the situation state
  (Gernsbacher structure-building; Zwaan-Radvansky situation model; Kintsch C-I). Organs: hdlab.state_of_mind
  WorkingOverlay (entity salience across sentences) + situation_model_accumulate.AccumulateRegister.
  CAVEAT to chase: the ORDER-shuffle "twin" scored HIGHER (0.758) than real order -> real narrative order is
  SUBOPTIMAL for this marginal (curiosity; the PROPER info-free value-permutation twin at 0.424 is the valid
  load-bearing control and sot_accum beats it). NEXT: (a) strengthen sot_accum with the REAL AccumulateRegister
  (FHRR event-history) not just content-stem accumulation; (b) re-run the SOT-conditioned decision on TellMeWhy
  (does situation-model conditioning also lift the single-antecedent gold?); (c) combine sot_accum with the
  result-state rollout; (d) propose sot_accum as the brain-foundational cause-selection wire (Q111).

STRATEGY NOTE (2026-09-08) relevant to us: the reader's reuse of GOLD coref labels ("gold-coref inheritance" in
the entity gate) is a LEAK -> report coref/name-bridge/experiencer on the HONEST de-leaked floor. OUR coref/SOT
work is ALREADY honest-floor (used the reader's own coref + spaCy + WorkingOverlay, NEVER gold coref). Two NEW
posted problems our located-negatives feed: replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_
clustering (the de-leaked binder -- our resolved-referent-binding finding feeds it) and
world_knowledge_common_noun_to_name_bridge_the_81_percent_residual (our edge-correctness/knowledge wall aligns).
Do NOT reuse the occupation-KB axis (located negative).

WHERE THINGS STAND (honest): the corrected chain's DECISION-layer coalition + generative-typing were REFUTED as
levers on real narrative (TellMeWhy + GLUCOSE) -- they add noise vs topical. The THINGS THAT WIN on real gold:
(1) SOT situation-model accumulation conditioning (sot_accum, GLUCOSE +0.159 CI-sep, load-bearing) <- NEW, the
lever; (2) result-state achievement check on marked-goal causes (TellMeWhy GOAL-subset +0.087 CI-sep);
(3) topical/Trabasso connectivity (the strong baseline SOT beats). The edge-correctness wall (correct causal
KNOWLEDGE) remains for the coalition, but SOT does NOT need it -- SOT is a live win NOW.

FILES NOW: 14 cells + 14 witnesses (all green). New since the cycle-7 list:
  exp_genworldmodel_sot_situation_model_v1.py + test_genworldmodel_sot_situation_model.py (3/3, the SOT WIN).
Also: exp_genworldmodel_edge_correctness_fix_v1.py + witness (4/4, SOT-temporal located negative),
exp_genworldmodel_glucose_chain_v1.py + witness (4/4), fetch_glucose_v1.py, data/corpora/glucose/.
REVERIFY THE WIN: .venv/Scripts/python.exe verification/test_genworldmodel_sot_situation_model.py  (3/3, ~2min).
Ledger: `python tools/problem_ledger.py --check` -> malformed/incomplete: 0.
CWD RESET each Bash call -> prefix `cd /c/AI/hd-instrument &&`; `export PYTHONIOENCODING=utf-8`.
================================================================================

================================================================================
## >>> CYCLE-9 CORRECTION (2026-09-08, post-compaction adversarial audit) -- READ AFTER THE RESUME BLOCK <<<
================================================================================
Owner: "dig deeper into the solution to identify if you missed anything." I did, and it OVERTURNS the GLUCOSE SOT
headline while STRENGTHENING the TellMeWhy result-state win. 4 new cells + witnesses (all green): sot_accum_
diagnosis (4/4), distinct_confound_audit (3/3), position_floor (4/4), tellmewhy_position_floor (4/4). 18 cells /
18 witnesses total now.
  * MISSED FLOOR: a pure POSITION baseline (`earliest` = pick the first story sentence; brain-foundational =
    causes-precede-effects iconicity + narrative primacy) was NEVER run in cycles 6/7/8. On GLUCOSE it scores
    0.694, ABOVE the whole semantic stack (sot_accum 0.610, overlap_count 0.603, topical 0.450). Adding semantic
    on top of position DEGRADES it (best combo -0.029 CI-sep below earliest). => GLUCOSE non-adj cause-selection
    is POSITION-DEGENERATE. Per the measurement bar (CI-sep over the strongest floor ACTUALLY RUN), the SOT
    +0.159-over-topical does NOT clear it -- topical was a WEAK baseline (max word-relatedness saturates, ties
    broken by earliest, tie-rate ~1.8). **GLUCOSE SOT win WITHDRAWN as a headline.**
  * MECHANISM MISLABEL x2: the 0.758 order-shuffle "twin" was a SINGLE-SEED artifact (40-order avg = 0.593 <
    real 0.610, so ORDER is not the lever); and the 1/k_s "cue-distinctiveness" weighting is inert-to-harmful
    (raw overlap_count 0.603 CI-beats distinct 0.580). The honest GLUCOSE signal is raw content-overlap count,
    which itself loses to position.
  * TELLMEWHY SURVIVES + STRENGTHENED: TellMeWhy non-adj is POSITION-USELESS (earliest/nearest/before_nearest =
    0.000; latest 0.076 << base 0.293). So the result-state rollout GOAL-subset win rs_refine 0.380 CI-beats the
    strongest POSITION floor by +0.3043 CI[0.196,0.424] (and base by +0.087). The PRIMARY positive is now
    controlled against BOTH topical and position floors. SOLVED status intact (it was always anchored on the
    TellMeWhy located-negative + subset positive, not the GLUCOSE SOT bonus).
  * DURABLE: the dominant SIMPLE signal for real-narrative cause-ID is DATASET-DEPENDENT -- POSITION on GLUCOSE,
    SEMANTIC/result-state on TellMeWhy. ALWAYS run a position floor AND a topical floor; the stronger is the bar.
  * REVERIFY: test_genworldmodel_{tellmewhy_position_floor, position_floor, distinct_confound_audit,
    sot_accum_diagnosis}.py.
================================================================================

================================================================================
## >>> CYCLE-10 (2026-09-08) -- the two optimizations PROTOTYPED brain-foundationally + the PHASE-DIAGRAM move <<<
================================================================================
Owner: "prototype these solutions brain foundationally... look in existing capabilities, but always check for
brain foundationality" + "remember the phase diagram". 3 new cells + witnesses (all green); 21 cells / 21
witnesses total.
  * OPT#1 competition_model_integrator (4/4): the position-vs-semantic combination the brain's way = the
    COMPETITION MODEL (Bates-MacWhinney; PINNED), NOT a hand gate. Reuses the LANDED hdlab.graded_competition
    (net_activation/map_pick; additive activation = Bayesian posterior). Cue weights = learned validities via an
    error-driven delta rule on a train split (no leak). ONE integrator, robust best-of-both: GLUCOSE learns
    position (matches the 0.71 floor, no dilution -> cycle-9 blend-hurts fixed), TellMeWhy learns result-state and
    CI-BEATS the best single cue +0.130 CI[0.044,0.239] (synergy). Verdict ROBUST_BEST_OF_BOTH_WITH_SYNERGY.
  * OPT#2 deep_rollout (4/4): deepen the result-state rollout (multi-step chaining; Schank-Abelson/Mattar-Daw;
    reuse multistep_fire/_reach past K=2). Monotone lever (coverage 12->38%, acc 0.326->0.380, beats base +0.087)
    but COVERAGE-bound on the sparse CSKG. Verdict DEPTH_COVERAGE_BOUND_ON_EXISTING_STORE.
  * PHASE-DIAGRAM rollout_phase_diagram (4/4): treated the coverage bound as a movable DENSITY knob, not a
    ceiling. Augment the causal graph with associative edges at swept density; op-point selected on train, scored
    on test. Moving density LIFTS the rollout over base +0.152 / topical +0.196 / sparse (0.348 vs 0.304) CI-sep
    -> NOT a ceiling. BUT raw-density not structure: an info-free SAME-DENSITY RANDOM-edge twin MATCHES it (0.391)
    -> a load-bearing/structure win needs a denser CORRECT store (edge-correctness / meaning foundation, Q111).
    Verdict DENSITY_MOVE_LIFTS_BUT_JUST_ASSOCIATIVE_DENSITY. (Fixed a set-iteration nondeterminism in _reach ->
    sorted; smoke had over-claimed load-bearing, train/test+twin corrected it.)
  * NET: the brain-foundational, reusable, no-regress deliverable is the COMPETITION-MODEL cue-validity
    integrator (robust cause-selector, additive channel). Both depth and density are real but bounded by
    edge-CORRECTNESS = the Q111 knowledge foundation. Reverify:
    test_genworldmodel_{competition_model_integrator, deep_rollout, rollout_phase_diagram}.py.
================================================================================

================================================================================
## >>> CYCLE-11 (2026-09-08) -- SWEEP existing organs for the correct-STRUCTURE lever + wire the ENTROPY organ <<<
================================================================================
Owner: "prototype those solutions now; sweep the organs/capabilities we have for the shortcomings." Explore-swept
all directed causal-knowledge assets, prototyped the 3 most promising WITH the load-bearing twin. 3 new cells +
witnesses (all green); 24 cells / 24 witnesses total.
  * directed_kb_rollout (4/4): swapped associative edges for the LANDED directed causal-precedence store
    (CausalKnowledgeStore, 65k CSKG Causes/HasPrerequisite). NOT load-bearing (0.283 vs random-directed twin
    0.304). Beats topical (+0.130 = coverage) but not base, not its twin. Generic verb-pair KB lacks
    item-specific structure.
  * entropy_gated_integrator (4/4): wired hdlab.graded_competition entropy as the per-item availability gate. NO
    accuracy lift (as the organ's MAP theorem predicts; net_activation already zeroes absent cues) BUT entropy is
    a VALID gold-free confidence signal (CI-sep higher on errors: GLUCOSE +0.109, TellMeWhy +0.252). Use =
    uncertainty, not accuracy.
  * script_order_cue (4/4): strategy's broad order store (temporal_script_schema/chains_broad.json, 454k p_before
    pairs) as a 5th cue. No CI-sep load-bearing lift: GLUCOSE flat; TellMeWhy 0.391->0.500 point-est but NOT
    CI-sep (n=46 underpowered) + not load-bearing vs shuffle. Coverage high (0.87-0.91) -> limit is per-pair
    correctness / story CONTEXT, exactly strategy's scope. (FOLLOW-UP: the TMW +0.109 point-estimate is worth a
    larger-n GOAL sample to power.)
  * CONSOLIDATED: every existing directed/order STORE adds coverage but is NOT load-bearing (twin matches) --
    context-free stores can't supply the ITEM-SPECIFIC correct structure real cause-ID needs. The load-bearing
    correct-structure we have stays the RESULT-STATE check (rs_fire); the entropy organ gives confidence not
    accuracy; the frontier lever is reading the specific story's CONTEXT (Q111), not another static store.
  * Reverify: test_genworldmodel_{directed_kb_rollout, entropy_gated_integrator, script_order_cue}.py.
================================================================================

================================================================================
## >>> CYCLE-14 (2026-09-08) -- FULLY UNDERSTOOD the LOO failure: world-state TOO PHYSICAL <<<
================================================================================
2 cells + witnesses (loo_resolved 3/3, causal_type_census 4/4); 28 cells/witnesses. Owner: "keep researching,
we need to fully understand" + "we have psychology databases historically -- how does this need to be represented".
  * STRONGER LOO (loo_resolved): resolving cross-sentence object identity via LANDED ACT-R object-anaphora coref
    + a semantic-relatedness bridging arm does NOT unblock LOO (obj_match 0.073->0.086; no CI-sep lift) ->
    pronoun-coref RULED OUT as the blocker.
  * CENSUS (causal_type_census, the decisive why): gold cause->effect causal TYPES -- GLUCOSE GOAL 41%/OTHER
    36%/PHYSICAL 12%/MENTAL 6%/AFFECTIVE 5%; TellMeWhy GOAL 37%/OTHER 40%/PHYSICAL 9%/MENTAL 9%/AFFECTIVE 5%.
    Psychological (GOAL+MENTAL+AFFECTIVE) ~52% vs PHYSICAL ~9-12%. world_state_register models ONLY physical
    possession/toggle -> represents only 5.6%/2.5% of gold pairs = the exact LOO ~5% coverage ceiling.
  * UNDERSTANDING: LOO counterfactual-necessity is the RIGHT mechanism but folds the WRONG ontology (physical,
    not psychological). Right substrate = a MUTABLE PSYCHOLOGICAL STATE (goals/beliefs/desires/emotions; inverse
    planning Baker-Saxe-Tenenbaum + ToM + OCC appraisal), folded + LOO-tested identically.
  * NEXT (dispatched research cycle-15): sweep the landed PSYCHOLOGY DATABASES (goal_register, occ_appraisal,
    affect_lexicon, _tom_chain/BigToM, emotion/appraisal KBs) + design the psychological-state register LOO must
    fold. SAME mechanism, RIGHT ontology (52% coverage). Reverify:
    test_genworldmodel_{loo_resolved, causal_type_census}.py.
================================================================================

================================================================================
## >>> CYCLE-12/13 (2026-09-08) -- script-order CONFIRMED at power + the CONTEXT-CONDITIONED structure <<<
================================================================================
CYCLE-12: the cycle-11 script-order TellMeWhy lead, POWERED on pooled TellMeWhy train+val+test GOAL (n=935,
test 467), is CONFIRMED: adding strategy's broad script-order cue (temporal_script_schema p_before) to the
Competition-Model integrator lifts 4cue 0.499 -> 5cue 0.559 (+0.060 CI[0.024,0.096] CI-sep) AND beats a
shuffled-script twin (+0.062 CI[0.019,0.105] = load-bearing). SECOND live load-bearing win from existing organs.
Cell exp_genworldmodel_script_order_power_v1.py + witness (3/3).

CYCLE-13: RESEARCHED (note research_context_conditioned_cause_selection_2026-09-08.md, 46 sources) + PROTOTYPED
the context-conditioned structure. The research is DECISIVE: 3 independent literatures (Trabasso&van den Broek
1985; Mackie INUS; Batusov-Soutchanski STRIPS actual-causality) converge on LEAVE-ONE-OUT COUNTERFACTUAL
NECESSITY -- remove candidate, does E's precondition flip met->unmet, conditioned on the whole story's folded
world-state. Ranked shortlist in the note: #1 LOO world-state necessity (P=0.40), #2 Kintsch coherence-settling
(P=0.35), #3 LOO surprisal-reduction (P=0.25). predictive_reader is already-fitted on disk (no fit needed).
Prototyped #1 (exp_genworldmodel_loo_necessity_v1.py + witness 4/4) reusing hdlab.world_state_register fold +
precondition state. RESULT = LOCATED NEGATIVE, blocker QUANTIFIED: HARD-FAIL on real narrative (no CI-sep lift;
~4% firing; doesn't beat null/order-shuffle twins) because CROSS-SENTENCE OBJECT IDENTITY is only ~10%
(E_has_goalobj ~0.63, op_reach ~0.6, but object-match ~0.10) -- the object E needs is named differently than the
candidate that establishes it -> needs RESOLVED DISCOURSE REFERENTS (coref/meaning-foundation, Q111). Same wall,
9th angle, now quantified; mirrors cycle-3 (ORACLE binding EXCELs +0.035). NEXT arms if a resolved-referent
front-end lands: mechanism #2 (Kintsch settling over CausalLinkRegister typed bindings) + #3 (LOO
surprisal-reduction over n400_coherence_monitor running gist). 26 cells/witnesses.
================================================================================
