---
problem: build_the_generative_result_state_world_model
status: SOLVED
bar: "A FULL-POPULATION CI-separated win on at least ONE consumer's MODERN gold -- the rollout turns a named SUBSET win into a full-population win ... the info-free twin LOSES CI-separated ... no live reasoner regressing. A rigorous NEGATIVE is a FULL PASS (e.g. 'the participant-bound rollout beats retrieval + topical + twin CI-sep on the GOAL subset AND lifts the full non-adjacent population toward CI-sep but stops at +N because generating the result-state needs a verb->effect-state schema the meaning foundation covers only M% of, enumerated with counts -- the knowledge-foundation coverage wall, quantified, filed as the next problem')."
result: "LOCATED NEGATIVE (the bar's explicitly-blessed full pass), with the SUBSET positive delivered. Built the participant-bound GENERATIVE result-state rollout (compose world_state_register + possession_operators + goal_register: simulate the effect action forward to a result-STATE, CHECK type-matched achievement against the goal-STATE, suppress goal-DEFEATING actions). On modern TellMeWhy non-adjacent (Lal 2021, item-level paired bootstrap): GOAL-subset POSITIVE n=92 -- rollout 0.3804 vs base 0.2935 +0.0870 CI[0.0217,0.1522] AND vs topical 0.2391 +0.1413 CI[0.0652,0.2174], BOTH CI-sep; the many-shuffle info-free NULL loses (observed 0.3804 > null p95 0.3261, p=0.0). FULL population n=256: ties base (rollout-base +0.0156 CI[-0.0156,0.0469], NOT CI-sep) -- reproduces the prior gen_union 0.3086. THE WALL, QUANTIFIED: the single-step result-state schema covers only 8.7% of goal->action means-ends (8/92) and 91.2% of the GOAL-subset misses are COVERAGE-misses; VerbNet directed broadening raises nothing (type-matched coverage 6.5%) because 95.2% of the misses are genuine MULTI-STEP PLANS ('wanted milk'->'went to the store') with NO single-step result-state achieving the goal -- the wall is rollout DEPTH (plan/script chaining), NOT verb->result-state coverage. TOP-DOWN into extraction (bar item 4): a can-fail positive control -- the generated goal-state expectation discriminates achieve-vs-defeat 10/12 where the feed-forward surface silo (goal-object overlap) TIES 0/12."
floor: "base plausibility engine (content+physics+psych, goal OFF) 0.2773 = the STRONGEST floor, recomputed on each population (GOAL subset 0.2935, OTHER 0.2475); topical (content-only argmax) 0.2500; CSKG typed-edge retrieval (coverage-bound 34%); GEK forward co-occurrence reachability (broad but directionless) 0.2969 (+0.0195 CI[-0.0039,0.043], ties base); info-free NULL by permuting the generated result-state across candidates (400 draws), GOAL null p95 0.3261 / full null p95 0.3047."
controls: "(1) INFO-FREE NULL (permute the result-state signal across candidates, 400 draws -> null mean/p95/p-value): on the GOAL subset the rollout BEATS null p95 (obs 0.3804 > 0.3261, p=0.0 -> the generated state's placement is load-bearing); on the FULL population it does NOT (obs 0.293 < p95 0.305 -> the state fires on too few items, the located negative). (2) BASE ABLATION (goal OFF) -- rollout beats base CI-sep on the GOAL subset (+0.087), isolating the achievement check. (3) TOPICAL floor -- CI-sep on the GOAL subset (+0.141). (4) GEK-DIRECTIONLESS diagnostic -- learned forward co-occurrence scores a goal-DEFEATING action >= a goal-SERVING one ('wanted milk'->'spilled milk' 3.96 >= '->bought milk' 3.64); the broad GEK arm ties base -> co-occurrence is the WRONG axis. (5) UPSTREAM broadening (VerbNet directed result-states) ties base; the miss decomposition isolates the residual as MULTI-STEP plans (95.2%), NOT single-step coverage. (6) TOP-DOWN can-fail positive control -- surface silo ties 0/12, rollout 10/12. (7) NO-REGRESS -- the rollout is inert without an explicit goal marker (byte-identical to the goal-OFF base) and modifies no live reasoner (additive channel)."
files_changed: "experiments/exp_genworldmodel_resultstate_v1.py (THE rollout: participant-bound result-state achievement check composing world_state_register + possession_operators + goal_register + force_dynamics; arms base/topical/objmatch/typed/gen_union/rs_refine/rs_strict/rs_bound/rs_union/gek_broad; null-p95 twin; GEK-directionless diagnostic; coverage enumeration; topdown_control(); no_regress()); experiments/exp_genworldmodel_upstream_verbnet_v1.py (the UPSTREAM VerbNet directed-result-state broadening + the single-step-vs-multi-step-plan miss decomposition; writes a VerbNet result-state cache); experiments/exp_genworldmodel_signal_loss_ladder_v1.py (the BRAIN-FIDELITY SCAN: oracle ladder + per-stage recall diagnostics -- where the chain loses signal); experiments/exp_genworldmodel_topdown_stack_v1.py (the TOP-DOWN brain-foundational STACK prototype: C1 additive constraint-satisfaction decision layer + C2 directed multi-step forward model, wired to depend on each other; the interdependence measurement + null twin; w_m/K swept as phase-diagram params); experiments/exp_genworldmodel_signal_loss_precise_v1.py (the PRECISE orthogonal trace: topical-confound audit, tightened extraction fidelity, means-end reachability tiers by hop-distance, + the ALL-COMPONENT brain-fidelity audit); verification/test_genworldmodel_resultstate.py (8/8 witness); verification/test_genworldmodel_upstream_verbnet.py (3/3 witness); verification/test_genworldmodel_signal_loss_ladder.py (4/4 witness); verification/test_genworldmodel_topdown_stack.py (5/5 witness); verification/test_genworldmodel_signal_loss_precise.py (5/5 witness); experiments/exp_genworldmodel_coherence_decision_v1.py (BUILD step-1 of the corrected chain: Thagard ECHO / Kintsch signed-pairwise coherence decision coupled to model-based rollout edges) + verification/test_genworldmodel_coherence_decision.py (5/5 witness); experiments/exp_genworldmodel_generative_edges_v1.py (deepening-cron cycle-1: GENERATE-don't-retrieve causal edges + phase-diagram density-precision sweep) + verification/test_genworldmodel_generative_edges.py (4/4 witness); experiments/exp_genworldmodel_participant_bound_edges_v1.py (cycle-2: participant-bound edges) + verification/test_genworldmodel_participant_bound_edges.py (4/4 witness); notes/problems/build_the_generative_result_state_world_model/RESEARCH_multistep_priors_and_options_2026-09-07.md (prior-drill + options) + RESEARCH_full_chain_brain_foundationality_eval_2026-09-07.md (the corrected 100%-brain-foundational chain, 3 neuroscience probes); notes/problems/build_the_generative_result_state_world_model/RESEARCH_brain_fidelity_scan_2026-09-07.md (the itemized brain-vs-us mechanism-diff, per stage); data/exp_genworldmodel_resultstate_v1/metrics.json; data/exp_genworldmodel_upstream_verbnet_v1/{metrics.json,verbnet_resultstates.json}; data/exp_genworldmodel_signal_loss_ladder_v1/metrics.json; data/exp_genworldmodel_topdown_stack_v1/metrics.json. Gold reused: data/corpora/tellmewhy/. NO hdlab write (Q111 -- proposed landing stated below)."
reverify: ".venv/Scripts/python.exe verification/test_genworldmodel_resultstate.py   # 8/8 (~10s): W1 reproduces disk baseline; W2 GOAL-subset CI-sep over base+topical; W3 info-free NULL loses (obs>p95,p=0); W4 full-pop located negative + coverage wall; W5 GEK co-occurrence ties base; W6 top-down can-fail control (silo ties, rollout discriminates); W7 no-regress/additive; W8 selectivity coverage-capped.  THEN .venv/Scripts/python.exe verification/test_genworldmodel_upstream_verbnet.py   # 3/3: VerbNet directed result-states, broadening ties base, 95% multi-step residual.  THEN .venv/Scripts/python.exe verification/test_genworldmodel_signal_loss_ladder.py   # 4/4: the fidelity scan -- forward-model depth is the dominant loss (+0.148), extraction is not the bottleneck (0.98), selection loses 25%.  THEN .venv/Scripts/python.exe verification/test_genworldmodel_topdown_stack.py   # 5/5: the TOP-DOWN stack -- C1 integration + C2 multi-step forward model compose (interdependence), GOAL subset 0.467 CI-sep (twin loses), above the single-step 0.380.  THEN .venv/Scripts/python.exe verification/test_genworldmodel_signal_loss_precise.py   # 5/5: the PRECISE trace -- topical is load-bearing but 91% of errors; extraction not the loss point; DEEP_MULTISTEP 51% is the exact residual; all-component fidelity audit.  THEN .venv/Scripts/python.exe verification/test_genworldmodel_coherence_decision.py   # 5/5: ECHO signed-pairwise coherence decision -- MECHANISM PROVEN on the constructed coalition control (coalition beats lone-topical; uniform-inhibition twin = no-op), real-data flat because candidate causal links are sparse (link_density 0.11) = the upstream edge-correctness wall"
---

# SOLVED (located negative + subset positive) -- the generative result-state world-model is BUILT and brain-faithful; the single-step rollout WINS its GOAL-subset domain but the full-population wall is NOT verb->result-state COVERAGE (the brief's guess) -- it is rollout DEPTH: 95% of the misses are MULTI-STEP PLANS that need script/plan chaining, and neither directed (VerbNet) nor learned (GEK) single-step broadening crosses it.

## The brain frame (how the brain does this; PINNED vs OUR-INVENTION)
PINNED (copied): the meaning of an action is its RESULT-STATE (Schank-Abelson 1977 scripts/RESULT; Trabasso &
van den Broek 1985), and whether an action serves a goal is judged by INVERSE PLANNING -- simulate the action
and check whether its predicted outcome achieves the goal-STATE (Baker, Saxe & Tenenbaum 2009; Csibra-Gergely
teleology). OUR-INVENTION-UNDER-TEST (swept): the state representation (which predicates a result-state carries),
the achievement CHECK scoring, the DEFEAT-suppression gate, the participant binding -- and, decisively, the
ROLLOUT DEPTH (single-step vs multi-step plan), which the brief listed as swept and which turns out to be the
binding parameter.

## What I built (compose the landed organs, do not rebuild)
A participant-bound GENERATIVE result-state means-end (`experiments/exp_genworldmodel_resultstate_v1.py`).
For each candidate cause C (a goal statement: agent WANTS goal-object/goal-action) and the effect action q:
1. GENERATE q's result-STATE over the resolved participants -- compose `hdlab.world_state_register`
   (STRIPS verb->effect: GET->POSSESS, LOSE->~POSSESS, TOGGLE_ON/OFF->OPEN/CLOSED, USE->precondition-have) +
   `hdlab.possession_operators` (FrameNet-derived, higher-coverage verb->op) + `hdlab.force_dynamics_typer`.
2. Represent C's goal-STATE from `hdlab.goal_register` (the PINNED desire/intention lexicon + goal-object span).
3. CHECK achievement, type-matched + participant-bound: the goal-head verb is PERFORMED (route 1), OR a
   POSSESS/USE/TOGGLE_ON op puts the goal object into the desired state (route 2); a LOSE/TOGGLE_OFF op or a
   negation on the goal object => DEFEAT => SUPPRESS the boost (the selectivity gain over surface overlap).
This is a strict, brain-faithful refinement of the prior best arm (`objmatch`, goal-object-as-patient surface
overlap): it can only REMOVE overlap fires that the simulated outcome shows do NOT serve the goal.

## What I measured (one screen; each floor recomputed on its own population; item-level paired bootstrap)
| slice | n | headline | verdict |
|---|---|---|---|
| baseline reproduction | 256 | base 0.2773 / topical 0.2500 / objmatch 0.2930 / gen_union 0.3086 -- matches the SDRT SOLVED disk exactly | DISK CONFIRMED |
| **GOAL subset POSITIVE** | 92 | **rollout 0.3804 vs base 0.2935 +0.0870 CI[0.0217,0.1522]; vs topical +0.1413 CI[0.0652,0.2174]; info-free NULL loses (obs 0.3804 > p95 0.3261, p=0.0)** | **REAL-PROSE WIN, twin LOSES** |
| FULL non-adjacent | 256 | rollout-base +0.0156 CI[-0.0156,0.0469] (ties); gen_union +0.0312 (ties); NULL not beaten (obs 0.293 < p95 0.305) | LOCATED NEGATIVE |
| coverage wall | 92 | single-step schema covers 8.7% of goal-actions; 91.2% of GOAL misses are COVERAGE-misses | WALL QUANTIFIED |
| UPSTREAM VerbNet (directed) | 256/92 | type-matched coverage 8.7%->6.5%; rollout ties base; **95.2% of GOAL misses are MULTI-STEP PLANS** | DEEPER WALL LOCATED |
| UPSTREAM GEK (co-occurrence) | 256 | broad (fires 76~79) but ties base +0.0195; DIRECTIONLESS ('spill' 3.96 >= 'buy' 3.64) | WRONG AXIS |
| TOP-DOWN into extraction | 12 | goal-state expectation discriminates achieve-vs-defeat 10/12; surface silo TIES 0/12 | can-fail control PASSES |
| NO-REGRESS | -- | inert without a goal marker (== goal-OFF base); modifies no live reasoner | ADDITIVE |

## The wall, located precisely (the deliverable the bar asked for)
The brief GUESSED the wall was "a verb->effect-state schema the meaning foundation covers only M% of." I built
that schema (8.7% coverage) AND its brain-foundational broadening (VerbNet directed result-states) AND the
learned alternative (GEK forward co-occurrence), and the disk says the wall is ONE LEVEL DEEPER:
- Broadening single-step verb->result-state coverage does NOT move the full population, because **95.2% of the
  GOAL-subset misses are genuine MULTI-STEP PLANS** -- "wanted milk" is served by "went to the store" only via
  a plan (go->at-store->store-has-milk->obtain), and NO single verb->result-state predicate bridges it. The
  achievement check fires correctly where the effect clause directly realizes the goal ("wanted milk"/"bought
  milk"), which is the 8.7% it covers.
- Learned co-occurrence (GEK) has broad coverage but is DIRECTIONLESS -- it scores a goal-DEFEATING action as
  high as a goal-SERVING one -- so it cannot supply the achievement check; it ties base. This confirms, from the
  causal/coherence side, the recurrent-loop SOLVED's finding that FORWARD-MODEL RICHNESS is the binding
  constraint, and the "generate don't retrieve" thesis: retrieval/co-occurrence is the wrong architecture.
- So the next lever is a DIRECTED, MULTI-STEP PLAN/SCRIPT rollout over a curated result-state + plan foundation
  (VerbNet result predicates for the single steps + script/plan chains), admitted offline through the
  consolidation gate -- the knowledge-foundation frontier, NOT a bigger single-step lexicon.

## Full-stack upstream + no-regress (bar items 4-5)
- UPSTREAM prototyped BOTH ways (VerbNet directed; GEK learned) to EXCEED, and MEASURED that neither crosses the
  full-population wall -- with the exact residual (multi-step plans, 95.2%) enumerated. The meaning channel the
  rollout reads over (`hdlab.meaning_foundation`) is LATENT/unwired today (confirmed: no live read()-time
  consumer); the plan/script knowledge the multi-step rollout needs is NOT in the substrate at coverage (the
  script organ `temporal_script_schema` fires ~4%, GEK is topical) -- so the meaning-channel + a plan-schema
  foundation must be wired/built LIVE FIRST before a multi-step rollout can be evaluated end-to-end.
- NO live reasoner regresses: the rollout is a SEPARATE goal-signal channel, inert without an explicit goal
  marker (byte-identical to the goal-OFF base) and it modifies no live reasoner. CONSUMERS to REVISIT once a
  multi-step rollout lands: `causal_reasoner` (edge-correctness c), `coherence_reader` (the full-population
  unmarked-causal residual), the who-did-what parser (two-valid patient pick), the temporal reasoner
  (implicit-event order) -- all four named the same generative expectation.

## Brain-foundational fidelity scan -- where EXACTLY we lose signal (checklist items 6 + 8; full note: RESEARCH_brain_fidelity_scan_2026-09-07.md)
An ORACLE LADDER (`exp_genworldmodel_signal_loss_ladder_v1.py`, witness 4/4) grants each stage its perfect
version so the GAP between rungs IS the signal lost there (TellMeWhy non-adj n=256):
```
base 0.277 -> +our surface means-end 0.293 -> +PERFECT goal simulator 0.441 -> +PERFECT all-type means-end 0.773 -> gold 1.000
              (+0.016 ours)           (+0.148 FORWARD-MODEL DEPTH)   (+0.332 other engines)    (+0.227 extraction/selection)
```
Itemized brain-vs-us, ranked by measured loss:
1. **Forward-model DEPTH (the dominant +0.148).** Brain: the meaning of an action is its result-state, simulated
   forward over intuitive-theory engines with infinite coverage because COMPUTED, chaining MULTI-STEP
   (Schank-Abelson scripts; Battaglia-Tenenbaum simulation). Us: SINGLE-STEP resource-coded lookup. Measured: the
   gold goal means-end is DIRECT 27% / single-step-VerbNet 4% / **MULTI-STEP plan 68%** -- we structurally cannot
   generate the 68%. THE gap; fix = directed multi-step plan/script rollout (not a bigger table, not co-occurrence).
2. **Cue INTEGRATION / selection (~25%).** Brain: weighted PARALLEL constraint satisfaction with learned
   validities (McClelland-Rumelhart; Kintsch; Competition Model). Us: multiplicative content-gate `content*(1+goal)`
   -- a low-content gold cause cannot be rescued by the boost. Measured: even a PERFECT boost wins only 75% on the
   GOAL subset (base overrides 25%). A tractable secondary fix.
3. **Goal INFERENCE (~11%).** Brain: mPFC/TPJ recovers implicit goals; us: Tier-1 lexical markers only
   (goal-detection recall 0.89). The 11% miss is unmarked goals needing ToM.
4. **The other causal ENGINES (+0.332).** The goal engine is only ~1/3 of the means-end signal; physics/mental/
   affect means-ends each need their own generative engine.
5. **Extraction is NOT the bottleneck here (0.98 event recall)** -- a genuine finding; the extraction wall lives on
   harder prose (SPACE's 25-35% motion recall), not clean modern TellMeWhy. So for THIS task the loss is
   downstream (the forward model + integration), not the upstream parse.

**PRECISE 2nd-pass trace + all-component fidelity audit (owner: "figure out EXACTLY where we're losing"; full
detail in RESEARCH_brain_fidelity_scan_2026-09-07.md; witness test_genworldmodel_signal_loss_precise.py 5/5).**
The generation residual, EXACT by hop-distance on the GOAL subset: DIRECT 27% / SINGLE_STEP 4% / TWO_HOP 15% /
**DEEP_MULTISTEP 51%** -- our mechanisms reach 46%; the 51% beyond a 2-hop reach is the plan/script residual. A
CORRECTED finding: the base's TOPICAL-content cue is NOT a removable confound (removing it crashes 0.277->0.102) --
it is load-bearing (spreading activation, brain-faithful) but the dominant ERROR source (**91% of base errors pick
a topically-related NON-cause**); the generative means-end must OVERRIDE topical and fails exactly on the DEEP 51%.
Extraction confirmed NOT the loss point (main-verb 0.98, goal-marker 0.89). The all-component audit flags TWO
non-brain-foundational leaks beyond the known-missing recurrent loop: (a) **CSKG is RETRIEVAL, not generation** --
the multi-step rollout rides a static KB (the anti-pattern the brief names), reaching only the TWO_HOP 15%; the DEEP
51% needs a GENERATIVE plan/script model, not a denser KB traversal; (b) **topical is the right cue in the wrong
ROLE** (dominant ranker vs weak prior) -- the fix is the generative signal OVERRIDING it via constraint
satisfaction, which is why the forward-model depth AND the integration fix must land TOGETHER (the interdependence).

## Top-down brain-foundational stack prototype (owner: prototype the components top-down; they rely on each other) + the PHASE-DIAGRAM lens
The fidelity scan surfaced two buildable brain-foundational components; I prototyped BOTH, wired to depend on
each other, and measured the interdependence (`exp_genworldmodel_topdown_stack_v1.py`, witness 5/5):
- **C1 (the TOP / decision layer) -- additive weighted CONSTRAINT SATISFACTION** replacing the multiplicative
  content-gate (McClelland-Rumelhart / Competition Model). It recovers the measured selection loss: a PERFECT
  forward model rises from oracle 0.441 (mult gate) to 0.461 (w_m=0.6) / 0.504 (w_m=0.8, +0.063 CI-sep).
- **C2 (forward-model depth) -- a DIRECTED MULTI-STEP rollout** (K-hop over the CSKG cause/enable graph;
  directed, unlike topical GEK). The 2-hop plan bridge fires ~89 vs the single-hop ~25 (broader coverage).
- **THE INTERDEPENDENCE (the owner's point, measured):** the composition ladder is monotone -- base 0.277 ->
  forward-model-alone 0.293 -> both-old-integration 0.309 -> **full stack 0.316**; on the GOAL subset base
  0.293 -> fwd-alone 0.370 -> integ-alone (single-step) 0.380 -> **full stack 0.467**. Each component adds;
  best TOGETHER. **GOAL subset: stack 0.467 vs base 0.293 = +0.174 CI[0.098,0.261] CI-sep, info-free NULL
  loses (obs 0.467 > p95 0.326, p=0)** -- well above the single-step rollout's 0.380. Full population 0.316
  (+0.039, borderline; twin p=0.08) -- improved over the prior 0.309 but not cleanly separated, because the
  signal is goal-gated and the 64% non-goal items get no lift.
- **PHASE-DIAGRAM lens (owner):** w_m (integration weight), K (rollout depth), and the hop-decay are SWEPT as
  phase-diagram parameters (the GOAL win is robust across w_m 0.4-0.8; the full-pop peaks at w_m~0.6). The
  remaining full-population wall is TWO movable operating points, NOT a ceiling: (1) the knowledge-store
  COVERAGE/DENSITY -- the multi-step rollout rides on the sparse CSKG graph (single-hop 34%); densifying/
  broadening that store (the curated result-state + plan foundation through the consolidation gate) is a
  sparse->dense phase-diagram move; (2) the causal-engine BREADTH -- goals are ~36% of causes; extending the
  directed forward model to physics/mental/affect result-states (the +0.332 "other engines" ladder gap) lifts
  the non-goal 64%. Both are parameters to move next, not fixed limits.

## Deep full-chain brain-foundationality evaluation + the corrected chain (owner: "evaluate deeply all up the line, 100% brain-foundational"; full detail in RESEARCH_full_chain_brain_foundationality_eval_2026-09-07.md, 3 cited neuroscience probes)
The pre-build evaluation caught THREE non-brain-foundational substitutions in the plan -- all the SAME
correction at three scales (stop building feed-forward scorers; build ONE recurrent generative
predict->error->update->roll-forward loop over a shared event-state):
1. **Reachability: SR/PPR is the WRONG primitive** (occupancy under a fixed policy; fails transition-revaluation;
   already lost as D7). Faithful = model-based generative forward simulation with a goal-state TEST
   (Baker-Saxe-Tenenbaum inverse planning) -- REUSE the landed causal_reasoner traversal; SR demoted to an
   optional NEED prioritizer.
2. **Generation: compose-and-late-fuse is a patchwork.** Faithful = ONE unified generative event-model
   (Franklin 2020 SEM; Kuperberg 2021; Rabovsky 2018 N400) with the engines as structured PRIORS over the
   shared `bound_event_backbone` state (LANDED default-off), driven by the built-but-unwired prediction-error
   loop (`predictive_reader`+`n400`) -- "the single biggest fidelity-vs-wiring gap."
3. **Decision: additive+softmax alone can't pick a cause** (monotone=argmax, correlated cues double-count).
   Faithful = signed-PAIRWISE coherence constraint satisfaction (Thagard ECHO 1989/1998; Kintsch) + DDM commit,
   inside the recurrent top-down loop (eager-but-revisable, Christiansen-Chater; predict MEANING not form,
   Nieuwland 2018). ~60% of the corrected chain is already built default-off.

**BUILD step-1 (this round): the ECHO signed-pairwise coherence decision, coupled to the model-based rollout
edges** (`exp_genworldmodel_coherence_decision_v1.py`, witness 5/5). MECHANISM PROVEN on a constructed coalition
control: a candidate embedded in a coherent causal chain beats a lone high-TOPICAL distractor (additive=0,
coherence=1), and the uniform-inhibition twin reproduces additive (=the proven no-op) -- the effect lives
entirely in the signed pairwise off-diagonal. On real TellMeWhy non-adjacent the decision is FLAT
(coherence 0.289 vs additive 0.312, not CI-sep; null not beaten) because candidate-candidate causal-chain links
are SPARSE + imperfect (link_density 0.11) -- the SAME U6 edge-correctness wall, now at the candidate-coherence
level. A brain-foundational component correct in mechanism, starved by an upstream (the generated causal edges)
that is not yet correct/dense -> re-confirms the binding lever is the generative directed-edge upstream over the
meaning channel. The signed-pairwise decision LANDS in the corrected chain; it pays off once the edges are dense.

**DEEPENING-CRON cycle-1: GENERATE-DON'T-RETRIEVE the causal edges** (`exp_genworldmodel_generative_edges_v1.py`,
witness 4/4). Attacked the edge-correctness wall with the faithful mechanism: generate the directed causal edge
by SIMULATION over the landed force-dynamics + event-type engines (no retrieval), swept on the phase diagram
(density-precision operating point + directed asymmetry). Findings: (1) flooding with high-density generated
edges HURTS (tau=0: density 0.512, acc 0.258 -- spurious coalitions); a PRECISE operating point RECOVERS
(tau=1.0: density 0.084, acc 0.328) -- +0.070, a MOVABLE operating point, not a ceiling. (2) At the optimum,
GENERATED edges beat CSKG-RETRIEVAL edges (coh_GEN 0.328 vs coh_CSKG 0.277) -- generate > retrieve, confirmed.
(3) But still NOT CI-sep over the additive decision (+0.019 CI[-0.020,0.059]) -- the class-level intuitive-theory
engines are PRECISION-COVERAGE-BOUND (sparse at high precision, wrong at high density). TRIANGULATED across 3
builds (decision, generative-edges, coverage-tiers): the binding residual is PARTICIPANT-BOUND, content-sensitive
edges over the (LATENT) meaning channel -- the class-level engines' presence-test is participant-blind; the
faithful fix is the content-sensitive rollout over coref-resolved participants + the wired meaning foundation.

**DEEPENING-CRON cycle-2: PARTICIPANT-BINDING the edges** (`exp_genworldmodel_participant_bound_edges_v1.py`,
witness 4/4). Bound each generative causal edge to a SHARED RESOLVED PARTICIPANT. LOCATED NEGATIVE: surface
content-noun binding does NOT help -- it makes edges SPARSER (0.038 vs 0.084) AND lower-accuracy (0.312 vs
0.324), because in real narrative the shared participant is usually COREF-RESOLVED/pronominal ("went to the
store"/"wanted milk" share the protagonist, not a surface noun), so surface-overlap gating KILLS real causal
edges. Faithful participant-binding needs REAL coref (E3, NEEDS_ADAPTER), not surface overlap.

**TRIANGULATION (5 independent builds converge on ONE wall):** coverage-tiers (DEEP_MULTISTEP 51%),
precise-trace (topical dominance; extraction not the issue), ECHO decision (mechanism proven, real-data flat),
generative edges (generate>retrieve + phase-diagram optimum, class-level engines precision-coverage-bound),
participant-binding (surface overlap too crude). ALL -> the binding wall is UPSTREAM causal-edge correctness c,
needing participant-bound content-sensitive result-state generation over COREF-RESOLVED participants (E3,
NEEDS_ADAPTER) reading the MEANING CHANNEL (meaning_foundation, LATENT) -- both hdlab/latent = strategy's (Q111).
The solver-side mechanisms (ECHO decision, model-based rollout, generative directed edges, phase-diagram
operating point) are BUILT + proven-in-mechanism; they deliver once fed correct/dense edges (causal_reasoner
1.000 on clean DAGs; U6 advantage=c -> +0.81 at c=1).

## What I did NOT establish (withdraw-first if wrong)
- I would withdraw first any claim of a FULL-POPULATION win: there is none; the full population ties base, a
  located negative. The clean CI-sep positive (twin loses) is on the GOAL subset (n=92, the engine's domain).
- The GOAL-subset win is essentially the prior objmatch score (0.3804): my result-state achievement check
  REPRODUCES it but does not EXCEED it on this gold, because the DEFEAT-suppression selectivity, though correct,
  bites on only 2 of 79 fires (covered defeat-verbs are rare in effect clauses). The NOVEL contribution is the
  mechanism + the precise, deeper wall decomposition + ruling out both upstream shortcuts -- not a higher score.
- The top-down control is a CONSTRUCTED minimal-pair positive control (like the SDRT mechanism control), not a
  full-population extraction win; it demonstrates the mechanism the silo lacks.

## KEY REALIZATIONS (the enabling moves)
1. **The brief's wall guess was one level too shallow -- test it, don't inherit it.** Building the verb->result-
   state schema AND its VerbNet broadening AND the GEK alternative, then decomposing the misses, showed the wall
   is not COVERAGE (8.7%) but rollout DEPTH: 95% of means-ends are MULTI-STEP PLANS a single verb->result-state
   cannot bridge. The located negative is more precise BECAUSE I broadened upstream instead of asserting coverage.
2. **The right axis is DIRECTED result-states, and learned co-occurrence cannot supply it.** GEK scores 'spilled
   the milk' >= 'bought the milk' as a continuation of 'wanted milk' -- co-occurrence has no achievement
   direction. VerbNet's semantic predicates do (has_possession vs destroyed). This is why "generate (a directed
   result-state), don't retrieve (a topical neighbour)" is the whole point, measured.
3. **A generated result-state is load-bearing only where it FIRES -- so coverage caps the twin control.** The
   info-free null loses on the GOAL subset (where the state fires) but not on the full population (where it
   rarely fires) -- the same 8.7% coverage that caps the score caps the control, and saying so is the finding.
4. **Compose the landed change-of-state organs -- the substrate already had the result-state schema.**
   `world_state_register` (a STRIPS GET/LOSE/TOGGLE engine) + `possession_operators` (FrameNet) were built and
   unused for means-end; reuse, not rebuild -- and their coverage IS the measured wall.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec.2b -- the generative result-state world-model entry, added 2026-09-07)
- The generative result-state world-model is BUILT (participant-bound, composes world_state_register +
  possession_operators + goal_register + force_dynamics) and is brain-faithful (Schank-Abelson RESULT +
  Baker-Saxe-Tenenbaum inverse planning). It WINS the GOAL subset of modern TellMeWhy non-adjacent CI-sep
  (twin loses) but TIES base on the full population.
- REVISE the anticipated wall: it is NOT "verb->effect schema coverage" (single-step). It is rollout DEPTH --
  95.2% of goal->action means-ends are MULTI-STEP PLANS; single-step directed (VerbNet) and learned (GEK)
  broadening both fail to cross it. Record the GEK-directionless deviation: learned forward co-occurrence
  cannot supply an achievement-DIRECTED result-state (the "generate don't retrieve" axis), converging the
  recurrent-loop SOLVED's forward-model-richness finding from the causal/coherence side.
- The completing lever is therefore a DIRECTED MULTI-STEP PLAN/SCRIPT rollout over a curated result-state +
  plan foundation admitted offline through the consolidation gate -- scoped INSIDE the knowledge-foundation
  north star, NOT a bigger single-step lexicon.

## Proposed hdlab landing (strategy lands; Q111 -- I do not write hdlab/)
1. Promote `experiments/exp_genworldmodel_resultstate_v1.py`'s result-state achievement means-end as a method
   on the coherence/causal means-end path (a NEW `sm.inferred_meansend_links` field; `sm.causal_links`
   untouched), DEFAULT-OFF / confidence-gated, impact-measured. It is additive (inert without a goal marker).
2. Do NOT land it as a full-population lift (there is none) and do NOT land the GEK-co-occurrence arm as the
   fix (directionless). The value banked now is the DECOMPOSITION: the next problem is a DIRECTED multi-step
   plan/script rollout, and wiring the LATENT `meaning_foundation` + a plan-schema foundation live is its
   prerequisite.
3. Fold the AUDIT UPDATE.

## TLDR (plain English)
A good reader imagines "she did this, so now the world is like that" and checks whether the imagined result is
what the character wanted. I built exactly that: a little engine that simulates an action forward to its result
and checks whether it achieves the stated goal, made only of parts we already had. On the stretch of real
stories where the cause IS a goal, it beats the plain baselines cleanly, and a scrambled version falls apart --
so the imagined structure is doing the work. But across ALL stories it only ties the baseline, and I found
exactly why -- and it is NOT what we assumed. We assumed we just needed a bigger table of "what each verb
results in." I built that table (and a much bigger, higher-quality one from a linguistics database), and it did
not help, because 95 out of 100 of the hard cases are MULTI-STEP PLANS: "she wanted milk" is explained by "she
went to the store" only if you know the whole shopping plan, and no single "verb -> result" fact bridges that.
I also proved the tempting shortcut -- using word-co-occurrence learned from stories -- cannot work, because it
scores "spilled the milk" as high as "bought the milk" for someone who wanted milk (it has no sense of achieving
vs ruining a goal). So the honest, precise result: the engine is right and works on its home turf; the real
missing piece is multi-step PLAN knowledge, which is a knowledge-building program, not a bigger lookup table.

## QUESTIONS
One labelling call for the owner (the science is identical either way):
- I filed **SOLVED** as the bar's explicitly-blessed "rigorous NEGATIVE is a FULL PASS" -- the mechanism is
  built + brain-faithful; the GOAL-subset positive passes bar items 1/2/3 on its population (twin loses); the
  top-down control (item 4) and no-regress (item 5) pass; and the full-population residual is located and
  quantified to the exact next lever, matching the SDRT/causal SOLVED precedent (subset positive + located
  negative).
- The HONEST BOUND: there is NO full-population CI-sep win (the bar's item-2 headline), and my GOAL-subset score
  does not exceed the prior objmatch arm. **If you tie the label to a full-population lift, this is a strong
  PARTIAL.** I lean SOLVED on the bar's negative provision + precedent; your call via owner_verdict.

## NEXT STEPS (priority-ordered)
- **P1 -- the completing lever, now precisely scoped: a DIRECTED MULTI-STEP PLAN/SCRIPT rollout.** Not a bigger
  single-step result-state lexicon (proven inert), not co-occurrence (directionless). Chain directed
  result-states over a curated plan/script foundation (VerbNet result predicates for single steps + a
  plan-schema store) admitted offline through the consolidation gate; check goal-state reachability within K
  steps. This is the knowledge-foundation frontier the recurrent-loop SOLVED and the knowledge-lever note both
  name; it serves all four consumers.
- **P1.5 -- DONE this round (the top-down stack prototype): cue INTEGRATION (additive constraint satisfaction) +
  the DIRECTED MULTI-STEP forward model.** Both built + witnessed (5/5); they compose (GOAL 0.467 CI-sep, twin
  loses). The integration fix recovers the selection loss (oracle 0.441->0.504); the multi-step 2-hop rollout
  broadens coverage. What remains to cross the FULL population are two PHASE-DIAGRAM moves (below), not a ceiling.
- **P1.6 -- PHASE-DIAGRAM move (store density): densify/broaden the multi-step rollout's knowledge store.** It
  currently rides on the sparse CSKG cause/enable graph (single-hop 34%). Move the operating point sparse->dense:
  a curated result-state + plan-schema foundation (VerbNet result predicates for single steps + plan/script chains)
  admitted offline through the consolidation gate. This is the knowledge-foundation frontier, now with the ROLLOUT
  ARCHITECTURE already built to consume it.
- **P1.7 -- PHASE-DIAGRAM move (engine breadth): extend the directed forward model to the OTHER causal engines**
  (physics/mental/affect result-states, the causal reasoner's U8 class-level seeds), so the means-end signal fires
  on the non-goal 64% (the +0.332 "other engines" ladder gap) -- the lever for the full-population win.
- **P2 -- wire the LATENT meaning channel live FIRST** (`meaning_foundation` has no read()-time consumer today);
  the multi-step rollout reads the resolved participants + result-state predicates over it.
- **P3 -- once the multi-step rollout lands, REVISIT the four consumers** (causal edge-correctness c, coherence
  full-population unmarked-causal, who-did-what two-valid patient, implicit-event temporal order) to receive the
  generated top-down expectation -- each named it independently.
- **DO NOT re-file (tested + closed this round):** a bigger SINGLE-STEP verb->result-state lexicon (VerbNet
  directed broadening ties base; 95% of misses are multi-step); GEK / co-occurrence as the means-end
  (directionless -- scores defeat >= achieve); CSKG retrieval (coverage-bound 34%); the surface goal-object
  overlap alone as the full-population fix (ties base). Do NOT use an external LLM at inference (THE invariant).
