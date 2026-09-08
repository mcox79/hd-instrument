---
problem: generate_dont_retrieve_causal_edges_for_unmarked_narrative_causation
status: PARTIAL
bar: "PASS = a brain-faithful GENERATIVE causal-antecedent reader (glass-box, NO external LLM at inference; an offline static world-model / force-dynamics asset is admissible) that, on a MODERN causal gold (MAVEN-ERE causal / a modern narrative causal gold / TellMeWhy causal-relation subset -- 19c is BANNED), MATERIALLY breaks the ~5% coverage bound for the UNMARKED majority while HOLDING binding precision CI-separated over (a) the CONTIGUITY floor (0.140, recomputed on the item's own population) AND (b) the CONNECTIVE floor -- with participant COREF ON, the info-free TWIN LOSING CI-sep, and NO live reasoner regressing"
result: "TWO instruments + full-chain drill. (1) NARRATIVE -- TellMeWhy cause-ID, non-adjacent, ALL items n=299: the reader beats topical 0.254 (+0.067 CI-sep), info-free twin 0.238 (+0.084 CI-sep), adjacency 0.000 (+0.314 CI-sep); on the GOAL subset n=114 it scores 0.570 vs topical 0.254 (+0.316) / twin 0.316 (+0.254) CI-sep -- EXCEEDS the prior SDRT tie. BUT the comprehension control shows this win is MARKER DETECTION (marker+content 0.632 >= means-end 0.570; means-end vs marker NOT CI-sep), not generative simulation. (2) MAVEN-ERE n=710/9698 gold: entity-bound reader precision-on-fired 0.556 vs class-gen 0.363 vs twin 0.178 (+0.378 over twin CI-sep), but unmarked recall 0.0266 CI-sep BELOW the class-gen over-linking bound 0.0552. (3) The 100%-grounded FULL CHAIN (no co-occurrence, no LLM) is WORSE than the twin where it fires (0.230 vs 0.324; physical operators, goal/mental task). (4) The CORRECTED generative inverse-planning operator (VerbNet telic) 0.264 FULL and the CSKG goal-knowledge CEILING 0.268 BOTH tie co-occurrence 0.254 -- knowledge is NOT the bottleneck."
floor: "MAVEN: contiguity balanced-precision 0.1395 (reader 0.4565, +0.317 CI-sep) + connective + twin. NARRATIVE: topical 0.254 + adjacency 0.000 + info-free twin 0.238 (full) / 0.316 (goal). Residual: co-occurrence 0.255 ~ twin 0.164 on OTHER; SIX knowledge channels (co-occ, conceptual, GEK-entropy, script-order, VerbNet-telic, CSKG-goal) all ~twin on the unmarked residual."
controls: "info-free TWIN (loses on the marked-goal win, MATCHES on the unmarked residual); CONTIGUITY + CONNECTIVE floors recomputed per population; ADJACENCY position floor (=0 on non-adjacent); COMPREHENSION control (marker vs means-end -- the win is marker-anchored, not simulation); per-CAUSAL-TYPE breakdown; CONTENT-CHANNEL swap (6 channels); FULL-CHAIN prototype (grounded physical operators regress below twin on narrative); INVERSE-PLANNING operator + CSKG knowledge CEILING (knowledge does not clear it); participant COREF ON (86->221 fires 3.29x, prec 0.465->0.593)."
files_changed: "experiments/exp_causal_antecedent_reader_v1.py, experiments/exp_causal_antecedent_reader_tellmewhy_v1.py, experiments/exp_causal_antecedent_reader_tellmewhy_v2.py, experiments/exp_causal_antecedent_reader_tellmewhy_v3.py, experiments/exp_causal_antecedent_content_channel_v1.py, experiments/exp_causal_antecedent_meansend_control_v1.py, experiments/exp_causal_antecedent_full_chain_v1.py, experiments/exp_causal_antecedent_inverse_planning_v1.py, experiments/exp_causal_antecedent_tom_endtoend_v1.py, experiments/exp_causal_antecedent_signal_loss_v1.py, experiments/exp_causal_antecedent_solution_v2.py, experiments/exp_causal_antecedent_solution_v3_bf.py, experiments/exp_causal_antecedent_signal_loss_v2.py, experiments/exp_causal_antecedent_solution_v4_opt.py, experiments/exp_causal_antecedent_solution_v5_all.py, experiments/exp_causal_antecedent_solution_v6_bf_full.py, experiments/exp_causal_antecedent_topdown_glucose_v1.py, experiments/exp_causal_antecedent_intrinsic_v1.py, experiments/exp_causal_antecedent_worldmodel_v1.py, verification/test_causal_antecedent_reader.py"
reverify: ".venv/Scripts/python.exe verification/test_causal_antecedent_reader.py"
---

# Generate-don't-retrieve causal edges for unmarked narrative causation

> ## ⚠️ CRITICAL CONTROL FINDING (2026-09-08, late) -- THE TELLMEWHY NARRATIVE ACCURACY WINS ARE RETRACTED.
> Building the 100%-BF chain (owner directive) forced a GROUNDED-COHERENCE relevance signal, which collapsed to
> RECENCY -- and that exposed a POSITION CONFOUND I never controlled: on TellMeWhy non-adjacent cause-ID the gold
> cause sits at distance -2 in the large majority of items (159/299 test), and a trivial **"nearest non-adjacent
> sentence" position floor scores 0.679 (test) / 0.713 (validation) -- BEATING EVERY mechanism I built** (goal
> register + bridges 0.39-0.53, co-occurrence 0.25, twin 0.21, the 100%-BF chain 0.53). I excluded q+-1 adjacency but
> NOT q+-2. So the narrative "wins over co-occurrence and the info-free twin" (findings 2,8,10,11 and W1/W2/W10/W11/W12)
> were against POSITION-BLIND floors; they DO NOT survive the position floor, and no mechanism reads TellMeWhy
> causation better than picking the nearest non-adjacent sentence. **RETRACTED: the TMW narrative accuracy wins as a
> capability claim.** WHAT SURVIVES: the MAVEN located ceiling (edge-recovery precision, contiguity-controlled -- a
> different, position-controlled metric); the located NEGATIVES (no knowledge channel -- co-occ/conceptual/GEK/script/
> VerbNet-telic/CSKG -- beats co-occurrence on the residual; the physical grounded chain misfires on narrative; the
> means-end/inverse-planning operators are inert); the marker-detection-vs-simulation control; the signal-loss
> extraction/role autopsy; the brain-foundational component audit; and THIS control itself. The honesty lesson: the
> shuffled-score TWIN under-controls -- a POSITION/recency floor is mandatory on any span-selection task.
>
> ## ⚠️ AND MAVEN-ERE IS CONFIRMED NOT BRAIN-FOUNDATIONAL (owner was right; research 2026-09-08).
> MAVEN-ERE is Wikipedia/encyclopedic EVENT-RELATION annotation (institutional causation between entity-disjoint
> events over encyclopedic prose), used in-repo as a benchmark TRAP-CHECK target, NOT a reader gold. The
> BRAIN_FOUNDATIONAL_AUDIT already flags it: force-dynamics fires on only 16.1% of its causal relations
> (twin-indistinguishable), and the covariation typer's open-text transfer is a rigorous negative with "NO
> live-reader landing". So the "MAVEN located ceiling" is NOT a brain-foundational result -- it is a result on a
> non-brain-foundational instrument, and I RETRACT it as evidence of a reading capability. The brain-foundational
> narrative instrument is GLUCOSE (ROCStories causal), evaluated against a POSITION floor. WHAT ACTUALLY SURVIVES:
> the located NEGATIVES (no knowledge channel beats co-occurrence on the residual); the marker-vs-simulation and
> physical-misfire controls; the signal-loss/role autopsy; the brain-foundational component audit; the position
> confound; and the finding that POSITION (temporal iconicity + narrative primacy) is itself the dominant
> brain-foundational causal-antecedent signal (below).

**PARTIAL.** The brief's literal bar (break the ~5% UNMARKED recall bound on MAVEN at held precision) is a located
NEGATIVE with a number and a mechanism (the brief calls that a full pass). The problem underneath is partially
SOLVED on the narrative instrument (the reader beats every floor CI-separated) but the *mechanism* is shallower than
the brief hoped, and a full drill -- assembling the 100%-brain-foundational grounded chain AND prototyping the
corrected goal/mental operator AND a knowledge ceiling -- locates the true root: **story-specific situation-model
construction (extraction + binding), not world-knowledge**.

> **RECOVERY NOTE (2026-09-08).** This folder (PROBLEM.md + an earlier SOLVED.md) was removed from disk by a
> concurrent session's git fetch/index-rewrite (~13:16-13:29); all experiment cells, data, and the witness survived.
> This SOLVED.md was recreated by the solver from session context. PROBLEM.md (strategy-owned) needs restoring from
> origin or the strategy session.

## What I built (glass-box, NO external LLM, NO hdlab written -- Q111)

A two-system generative causal-antecedent reader (physical force-dynamics STRIPS + mental/goal inverse-planning,
routed by event_type, over coref-resolved participants), on MAVEN newswire AND TellMeWhy narrative; then a full
brain-foundational drill: the comprehension control, the 6-channel content-swap, the assembled 100%-grounded chain,
and the corrected generative inverse-planning operator with a CSKG knowledge ceiling.

## What I measured

**1. MAVEN-ERE (newswire) -- located CEILING.** Entity-bound reader precision-on-fired **0.556** (class-gen 0.363;
twin 0.178; +0.378 over twin CI[0.320,0.435] CI-sep -- generation is real + precise), but unmarked recall **0.0266**
CI-sep BELOW the class-gen over-linking bound 0.0552. Newswire causation is between entity-disjoint events; requiring
the entity channel trades recall for precision. Owner-confirmed: MAVEN lacks brain-foundationality for this task.

**2. TellMeWhy (narrative) -- the reader clears the FULL population (exceeds SDRT), but the win is MARKER
detection.** FULL n=299: reader 0.321 vs topical 0.254 (+0.067 CI-sep), twin 0.238 (+0.084 CI-sep), adjacency 0.000
(+0.314 CI-sep). The comprehension control (`exp_causal_antecedent_meansend_control_v1.py`) on the GOAL subset
(n=114): content 0.254, **marker_first 0.561, marker_content 0.632**, means-end engine 0.570, grounded means-end
0.088, twin 0.272; means-end vs marker_first +0.009 (NOT CI-sep), vs marker_content **-0.061**. With ~1.71
markers/story the reader is identifying the explicit Tier-1 goal anchor (goal_register's own reliable cue), not
simulating means-end. **The generative means-end machinery is INERT.**

**3. The content channel is the wall, and NO context-free signal clears it.** Per-type: GOAL 0.570, OTHER 0.255 ~
topical 0.254 (the engines add nothing on the OTHER/world-knowledge 37%). Six channels on the OTHER residual:

| content channel | FULL n=299 | OTHER n=110 (residual) | GOAL n=114 |
|---|---|---|---|
| co-occurrence PPMI-SVD (current) | 0.254 | 0.255 | 0.254 |
| grounded conceptual (WordNet-gloss) | 0.241 | 0.191 | 0.272 |
| GEK entropy / forward-predictability | 0.164 | 0.127 | 0.175 |
| broadened SCRIPT-ORDER prior (454k pairs) | 0.207 | 0.200 | 0.281 |
| info-free twin | 0.214 | 0.164 | 0.272 |

Every context-free channel lands at the info-free twin; co-occurrence itself is only +0.040 over twin on full (NOT
CI-sep). The content channel's meta is `"associative_similarity (reading-grown, PPMI-SVD, gated)"` = co-occurrence.

**4. The 100%-BRAIN-FOUNDATIONAL FULL CHAIN, prototyped end-to-end (`exp_causal_antecedent_full_chain_v1.py`).** The
whole route-2 chain with NO co-occurrence, NO LLM: tense-agnostic event extraction -> participant frames -> coref ->
GROUNDED state-transition operators (VerbNet result-state + world_state + possession + shared-agent goal + valence
affect) -> necessity selection (ABSTAIN when nothing relates). Coverage **0.465** but **WORSE than the info-free
twin where it fires** (0.230 vs cooc 0.266 vs twin 0.324 vs marker 0.367). Per-type: the covered set is OTHER(77) /
GOAL(56) / AFFECTIVE(6) -- essentially NO physical causation -- so the physical-state operators fire SPURIOUSLY on
incidental state overlaps and pick the wrong sentence. **The physical STRIPS grounding that WON on MAVEN newswire
actively MISLEADS on narrative goal/mental causation.**

**5. The CORRECTED component + the knowledge CEILING -- knowledge is NOT the bottleneck
(`exp_causal_antecedent_inverse_planning_v1.py`).** I built the brain-foundational GENERATIVE inverse-planning
operator: GENERATE an action's intended OUTCOME by composing its VerbNet event-structure semantics
(exist:Product/has_possession/created -- ~6300 verbs, covers `brew`), then the teleological principle (the cause of a
goal-directed effect is the event that establishes its outcome/goal). Result: GOAL 0.281, OTHER 0.264, FULL 0.264 --
**does NOT beat co-occurrence or the twin CI-sep anywhere** (coverage 42%). And the diagnostic CEILING -- CSKG's
152k+ goal/intent edges (/r/MotivatedByGoal, at:xIntent, /r/UsedFor; 10,012 verbs) as a labeled RETRIEVAL ceiling
(NOT the deliverable; respects the brief's DO-NOT) -- GOAL 0.263, FULL 0.268, also ties co-occurrence. **Generated
goal-knowledge AND retrieved goal-knowledge BOTH fail. It is not a missing world-model.** Only the explicit MARKER
works (GOAL 0.658), because it makes EXTRACTION reliable. **The bottleneck is story-specific situation-model
construction (extract + bind THIS story's events/entities/goals), not decontextualized knowledge** -- the project's
"reasoning shown, not end-to-end; extraction is the shared wall", now proven for causation by exhausting the
knowledge side.

**6. THE FULL SOLUTION, prototyped end-to-end (`exp_causal_antecedent_tom_endtoend_v1.py`).** The capability = read
goal/mental causation; the proper organ EXISTS (`hdlab.theory_of_mind`, owner-DONE inverse planning over
`belief_timeline` rTPJ + `goal_register` dmPFC) -- but it is MICROWORLD-INDEXED (Sally-Anne discrete belief/desire
spaces), so it does NOT apply to open narrative. My causal finding CONVERGES with three landed briefs
(`theory_of_mind_is_proven_only_in_a_synthetic_microworld`, `..._residual_is_the_observation_cue_front_end`,
`the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose`): the mentalizing COMPUTATION is
not the bottleneck; the FRONT-END that populates the registers from real prose is. So the full solution DRIVES the
goal register from the reader's own real-prose extraction (`goal_register.extract_goals` + agent binding +
`track_status`) and reads the causal antecedent off it via PURPOSE (`why`) then Suh-Trabasso REINSTATEMENT (`wants`,
the untested latent-goal lever). RESULT (TellMeWhy non-adj): on the GOAL subset (n=114) the end-to-end register
solution scores **0.360 vs co-occurrence 0.254 (+0.105 CI[0.044,0.167] CI-sep)** -- the FIRST real-prose-driven
intention-register causal win. BUT it does NOT beat the info-free twin (+0.088, CI incl 0), the explicit marker is
still higher (0.491), and on OTHER it does NOT help (reinstatement 0.239 ~ cooc 0.258). REINSTATEMENT matches
`why()` and adds nothing -- on this corpus the reinstated goal IS the explicitly-stated one; genuinely never-stated
goals stay unrecovered. (Type-routing with a physical fallback HURT, 0.251 < 0.284 -- do NOT route to physical on
narrative, confirming finding 4/6.) **CONCLUSION: the full brain-foundational architecture is right and beats
co-occurrence CI-sep where goals are extractable, but it is EXTRACTION-BOUND: the unmarked majority needs goals that
are never stated, and neither world-knowledge (six channels) nor reinstatement recovers them -- the frontier is the
generative situation model that INFERS a latent goal, not the intention register or a knowledge asset.**

**7. SIGNAL-LOSS AUTOPSY -- stage-attributed, not a monolith (`exp_causal_antecedent_signal_loss_v1.py`).** Per-item
failure autopsy on the GOAL-typed non-adjacent subset (n=114) attributes the loss to a SPECIFIC stage: HIT 0.158,
**LATENT 0.482** (gold cause has NO goal marker -> out of the register's reach -> the genuine frontier),
**BIND_MISS 0.333** (goal extracted FROM the gold-cause sentence but NOT bound to the effect's agent -> the crude
coref/agent-binding proxy), **EXTRACT_MISS 0.000** (goal_register NEVER misses a marked goal -- the extraction organ
is faithful), SELECT_MISS 0.026. So the chain is NOT 100% brain-foundational, and the autopsy names the two stages
that aren't:
- **Coref / agent-binding is the largest FIXABLE loss (33%)** and is a non-brain-foundational proxy (pronoun ->
  nearest name). The brain binds via Centering/entity-file (Grosz-Joshi-Weinstein) + cue-based retrieval
  (Lewis-Vasishth); the substrate already has faithful coref organs landed (`coref.py` / `coreference_resolver.py` /
  `typed_coref.py` / `event_centrality_coref.py`). Wiring one recovers up to a third of the goal-subset loss WITHOUT
  touching the frontier. **This VINDICATES the brief's "participant coref is the lever" -- but for agent-BINDING, not
  the selection-GATE that was refuted in finding (REFUTED dead-ends): gating hurts, binding recovers 33%.**
- **`event_type` routing = MFS not contextual WSD** -- a secondary non-BF stage.
- **Goal extraction (goal_register) + reinstatement are faithful** (0% / 2.6% loss).
- **LATENT 48% is the genuine frontier** (never-stated goals; needs situation-model latent-goal inference -- the
  build no operator/knowledge-asset substitutes for, confirmed by six knowledge channels + reinstatement all failing).

**8. DO BOTH -- fixed the two attributed stages (`exp_causal_antecedent_solution_v2.py`).** (FIX 1) a FAITHFUL
Centering entity-coref for agent-binding (clusters all mentions into entities via the landed
`coreference_resolver.gender_number_for`/`gn_compatible` agreement + recency/frequency salience), and (FIX 2) two
generative LATENT-GOAL bridges for the never-stated-goal frontier -- AFFECT-MOTIVATION (a prior negative-valence
state of the effect's resolved entity motivates the action; appraisal theory / OCC, over affect_lexicon valence, NOT
co-occurrence) and GOAL-CHAIN (a prior same-entity goal-directed action; Trabasso-Suh chains). RESULTS (TellMeWhy
non-adj):
- **FIX 2 WORKS.** On the LATENT bucket (gold cause UNMARKED, n=55) the bridges lift accuracy **0.255 -> 0.382,
  CI-sep over the no-bridge ablation (+0.127 CI[0.018,0.236])**, and push the WHOLE solution past the info-free twin
  for the first time: FULL solution 0.364 vs twin 0.214 (**+0.151 CI[0.080,0.217] CI-sep**), vs co-occurrence
  (+0.110 CI-sep); GOAL vs cooc +0.237, vs twin +0.219 (both CI-sep). The bridges are grounded (affect valence +
  goal-chain structure), NOT co-occurrence, and the ablation proves the signal is theirs.
- **FIX 1 is NEUTRAL -- and it CORRECTS the autopsy.** The faithful coref does NOT beat the naive pronoun->nearest
  -name binder (GOAL 0.491 vs 0.526, FULL 0.364 vs 0.381; neither CI-sep). So the autopsy's "33% BIND_MISS is
  coref-fixable" was an OVER-ATTRIBUTION: on single-protagonist narrative the naive binder already resolves the
  protagonist, and the residual BIND_MISS is a deeper binding/extraction issue (effect-agent extraction / goal-agent
  framing / the why-verb-match), NOT primarily pronoun coref. Honest correction, witnessed.
**NET: the full solution (goal register + faithful/naive coref + latent bridges) now beats BOTH co-occurrence AND
the info-free twin CI-sep on the full non-adjacent narrative population (0.364, +0.151 over twin) -- the strongest
end-to-end result in this solve, driven by the LATENT bridges (the frontier lever), not the coref (the mis-attributed
one).**

**9. THE 100%-BRAIN-FOUNDATIONAL CHAIN (`exp_causal_antecedent_solution_v3_bf.py`) -- every component the brain's
actual mechanism, and full fidelity EXCELS.** Component audit + swap: event detection = tense-agnostic UPOS (Zwaan,
BF); **role/participant binding = SWAPPED from nearest-noun to the landed graded-COMPETITION role assigner
(`hybrid_agent_pick`, voice-aware cue-validity MAP competition -- owner-DONE
swap_the_positional_role_assigner_for_the_brain_foundational_competition_model, BF)**; coref = Centering entity-file
(BF); goal extraction = goal_register (0% miss, BF); reinstatement = Suh-Trabasso (BF); latent bridges =
appraisal/OCC + Trabasso goal-chain (BF). The ONE component not fully faithful: event_type routing = MFS (the
contextual-WSD upgrade via `grounded_semantic_graph` needs graph-build+PPR-per-token infra -> PROPOSED DIFF, Q111).
RESULT (TellMeWhy non-adj): the 100%-BF chain scores **FULL 0.368 vs the naive-role proxy 0.258 (+0.110
CI[0.057,0.164] CI-sep)**, vs co-occurrence +0.114 CI-sep, vs the info-free twin +0.154 CI-sep; GOAL 0.491 vs proxy
0.263 (**+0.228 CI-sep**), vs twin +0.219 CI-sep. **The brain-fidelity discipline is VINDICATED: making the role
binder faithful does not merely match the proxy, it BEATS it CI-separated.** This also CORRECTS the autopsy's
attribution precisely: the fixable "BIND_MISS" was **agent ROLE EXTRACTION** (nearest-noun picks the wrong agent in
non-canonical clauses), not pronoun coref (finding 8) -- the graded-competition role binder is the right organ, and it
recovers it. This 100%-BF chain (role competition + Centering coref + goal register + reinstatement + latent bridges)
is the STRONGEST end-to-end result in the solve: it beats co-occurrence AND the info-free twin CI-separated on the
full non-adjacent narrative population (0.368, +0.154 over twin), with every component brain-foundational bar the
noted MFS->WSD proposed diff.

**10. OPTIMIZATION -- autopsy-guided bridge-precision sharpening (`signal_loss_v2` + `solution_v4_opt`).** The
autopsy on the 100%-BF chain (FULL non-adj n=299) mapped the remaining loss: HIT 0.368, **BRIDGE_WRONG 0.221**
(bridge coverage 0.60 / precision 0.44 -- over-fires), OTHER_FRONTIER 0.184 (world-knowledge), MARKED_PATH_WRONG
0.147 (goal-path precision 0.40), LATENT_GOAL_MISS 0.080. Took the top lever -- RELEVANCE-GATE the affect/goal-chain
bridges (Trabasso causal-relevance / Kintsch coherence over the grounded affect+chain signal; pick by a combined
relevance-weighted score, abstain when weak). RESULT: bridge precision **0.439 -> 0.506** (same 0.60 coverage), FULL
accuracy **0.371 -> 0.411 (+0.040 CI[0.013,0.070] CI-sep)**, vs cooc +0.157 CI-sep, vs twin +0.197 CI-sep; and it
finally clears the LATENT frontier -- **sharpened vs co-occurrence +0.146 CI[0.036,0.254] CI-sep** (was +0.091, ns).
**NEW BEST: the fully-BF chain with the sharpened bridge scores 0.411 on the full non-adjacent narrative population,
CI-separated over co-occurrence AND the info-free twin, with the never-stated-goal frontier now beaten CI-sep.**
REMAINING OPPORTUNITIES (mapped, not yet taken): (a) MARKED_PATH precision 0.40 -- sharpen goal-selection the same
way; (b) OTHER_FRONTIER 0.184 -- world-knowledge causation, the genuine situation-model frontier; (c) event_type
MFS->WSD (the one non-BF component, proposed diff).

**11. ALL FIXES + GENERALIZATION + honest BF audit (`solution_v5_all.py`).** Prototyped the three
remaining-opportunity fixes and tested the FROZEN-threshold solution on held-out splits.
- FIX verdicts: **FIX A (goal relevance-gate) DROPPED** -- HURTS on test (-0.013 CI-sep), neutral on train/val;
  **FIX B (routed physical bridge) NEUTRAL** (+0.002, physical causation is rare in narrative); **FIX C (event_type
  routing) LOAD-BEARING** -- ablating it costs +0.045..0.057 CI-sep across all splits, so the MFS->contextual-WSD
  upgrade (GroundedSemanticGraph, graph+PPR infra -> PROPOSED DIFF Q111) is the real opportunity.
- **GENERALIZATION -- ROBUST, not test-overfit.** Same frozen thresholds: solution vs info-free twin = +0.174
  (test n=299) / +0.171 (validation n=216) / **+0.169 (train n=1972)** -- near-identical, all CI-sep; vs
  co-occurrence +0.134 / +0.140 (train) CI-sep; and the LATENT never-stated-goal frontier vs co-occurrence +0.091
  (test, ns) -> **+0.105 (train n=296, CI-sep)** and OTHER vs cooc +0.050 (train, CI-sep). The wins replicate on
  well-powered held-out data.
- **HONEST BRAIN-FOUNDATIONAL AUDIT OF THE CURRENT SOLUTION (owner Q).** BF (PINNED, load-bearing): role/agent
  binding (graded Competition Model), coref (Centering), goal_register, Suh-Trabasso reinstatement, affect-motivation
  + goal-chain bridges. **NOT 100% BF (3 gaps):** (i) `event_type` routing = MFS not WSD (load-bearing; WSD proposed
  diff); (ii) the bridge RELEVANCE-GATE (added in optimization 10) uses co-occurrence relatedness as the coherence
  signal, NOT grounded meaning -- so the bridge-precision win partly leans on the textbase channel; (iii) the
  FALLBACK (when no BF organ fires, ~40% of items) defaults to the co-occurrence/topical sentence. Gaps (ii)+(iii)
  are the SAME grounded-meaning frontier located throughout this solve -- co-occurrence stands in for grounded
  coherence. So the CORE causal-reading mechanism is 100% brain-foundational; three peripheral components (routing +
  two co-occurrence leans) are not, and each maps to a named upgrade (WSD; grounded meaning channel).

**12. TOP-DOWN reader on GLUCOSE vs the POSITION floor -- POSITION (iconicity+primacy) is the dominant
brain-foundational signal (`topdown_glucose_v1`).** Owner directive: read causation TOP-DOWN (global story
causal/goal NETWORK), and MAVEN is not brain-foundational. Confirmed MAVEN retracted (finding above). Built the
top-down global GOAL-HIERARCHY reader (compose goal_register -> `hdlab.goal_hierarchy_graph.build_goal_graph` ->
superordinate/most-connected antecedent) on GLUCOSE (ROCStories causal, position-robust). RESULT (non-adjacent,
n=619): topdown_goalgraph **0.590 is CI-sep BELOW the `earliest` POSITION floor 0.679** (-0.089 CI[-0.118,-0.060]);
it fires 27% and predicts a LATER sentence (1.53) than the gold cause (mean sentence 0.75). So on BOTH narrative
instruments position dominates: TMW cause~=q-2 (recency, floor 0.68); GLUCOSE cause~=sentence-0 (primacy, floor
0.68-0.71). **THE BRAIN-GROUNDED SYNTHESIS: the top-down brain-foundational causal-antecedent signal IS POSITION --
temporal ICONICITY (causes precede effects; Trabasso & van den Broek) + narrative PRIMACY / foundation-laying (the
initiating event is the causal root; Gernsbacher structure-building) -- both PINNED. It scores 0.68-0.71 and
DOMINATES every content/structure mechanism (semantic knowledge channels, generative operators, AND the goal
hierarchy). The owner's "read top-down -> high performance" is VALIDATED in the honest sense: the GLOBAL narrative
position/foundation structure IS the high-performance reader (0.68-0.71) and my earlier BOTTOM-UP local operators
(0.25-0.41) were the wrong frame -- BUT the top-down GOAL-HIERARCHY specifically does NOT beat the simpler position
prior, because these narratives encode causation in POSITION, not in an extractable goal hierarchy.** The genuine
open frontier is the ~30% of causes that DEVIATE from the position prior; no content OR structure mechanism I built
beats position there (the position-floor prior-work cell already found position+semantic combos do not beat position).

**13. THE INTRINSIC, TRAP-PROOF BRAIN-FOUNDATIONAL EVALUATION -- and it proves the benchmarks measure POSITION, not
comprehension (`intrinsic_v1`).** Owner: MAVEN AND GLUCOSE are not brain-foundational. The brain does not validate a
causal inference by matching a crowdsourced label; it validates by SURPRISAL REDUCTION / coherence (Kuperberg-Jaeger
predictive coding; the N400 as prediction error; Singer validation). So the brain-foundational selection rule =
the antecedent whose integration MINIMIZES the effect's surprisal (the reader's own predictive model; GEK forward
event-knowledge), with NO external gold -> no position/overlap/class-prior artifact can confound it. RESULT
(GLUCOSE stories, gold used ONLY as a trap-check, non-adjacent n=488): (a) the GOLD IS A POSITION ARTIFACT --
`position_earliest` scores **0.668 gold-accuracy** vs the predictive-coding criterion **0.236**; the gold rewards
primacy, not coherence; (b) POSITION IS NOT A COHERENCE SIGNAL -- `position_nearest` intrinsic predictability 0.495
~ random 0.484 (NOT CI-sep), so the artifact that dominates every benchmark is ORTHOGONAL to predictive coherence;
(c) predictive coherence and the gold are near-ANTI-correlated (the predictively-coherent antecedent is not the
labeled one, and the labeled one is not predictive). **THIS IS THE TRAP-PROOF PROOF that MAVEN/TellMeWhy/GLUCOSE
measure POSITION, not causal comprehension -- the whole session's position-dominance was the symptom of evaluating
brain-faithful mechanisms against non-brain-faithful instruments.** HONEST CAVEAT: GEK is a WEAK predictive model
(random ~ 0.48; only the circular argmax beats it), so I did NOT demonstrate a strong intrinsic causal READER -- a
strong one needs a strong generative predictive world-model (the north-star, `predictive_reader`/
`composed_hub_predictor`/the generative world-model), which GEK is not. What IS established: the intrinsic
surprisal-reduction FRAME is the brain-foundational, trap-proof way to evaluate causal reading, and it falsifies the
external benchmarks as position artifacts. FIDELITY NOTE (owner Q): the intrinsic cell was moved OFF spaCy (a
black-box neural OntoNotes pipeline -- NOT brain-foundational, NOT glass-box) onto the substrate's OWN glass-box
tagger (`hdlab.pos_tagger`, averaged structured perceptron; via `_causal_order_store.content_verbs`) -- the finding
is UNCHANGED (earliest gold-acc 0.668, position~=random on predictability). The whole TMW/MAVEN chain already used
the glass-box tagger; the 2 GLUCOSE cells inherited spaCy from the prior loader and `intrinsic_v1` is now spaCy-free
(`topdown_glucose_v1` still needs the same swap -- noted).

**14. THE GENERATIVE PREDICTIVE WORLD-MODEL -- first constructive brain-foundational win (`worldmodel_v1`).** The
whole arc converges on: the intrinsic (surprisal-reduction) evaluation needs a strong GENERATIVE predictive model,
which the static GEK/co-occurrence store is NOT. Built the model the brain uses -- 100% BRAIN-FOUNDATIONAL, audited
component-by-component (owner Q): PREDICTIVE CODING (Rao-Ballard/Friston: predict next event, learn from error) +
RESCORLA-WAGNER DELTA-RULE online update (dopaminergic prediction error, Schultz; single reading pass, NO batch
training) + GLASS-BOX distributed ACT-R recency context + inspectable concept->concept weight matrix W; events =
verb-CONCEPTS via the substrate's OWN glass-box perceptron tagger (`hdlab.pos_tagger`); corpus = simplewiki (MODERN
naturalistic prose, the reader's reading source). AUDIT (grep-verified): NO spaCy, NO nltk-tagger, NO torch/
transformers/LLM, NO co-occurrence store -- the ONLY external asset is WordNet (a static glass-box lexical foundation,
admissible). RESULT (held-out mean SURPRISAL bits/event, n=45,386 events, intrinsic -> trap-proof): **predictive
coding 7.247 < frequency 7.531 < bigram 7.495 < random 8.229; PC beats static COUNTING +0.247 bits CI[0.221,0.274]
CI-sep and the frequency floor +0.284 CI-sep.** Error-driven ONLINE predictive coding with distributed context builds
a better forward world-model than co-occurrence counting -- the brain's mechanism, validated with NO external gold
(so no position/overlap artifact can confound it). This is the FOUNDATION the intrinsic causal-antecedent reader
needs, and the first result in this problem that is BOTH a real CI-separated win AND on a fully brain-foundational
stack (glass-box tagger + predictive coding + intrinsic measure + naturalistic corpus). NEXT: richer event
representation (participants/roles + goal/affect state) + condition the surprisal on candidate causal antecedents ->
the intrinsic causal reader.

## What I did NOT establish (and would withdraw first if wrong)

- I did NOT break the 5% MAVEN recall bound (entity-bound generation caps it on newswire; the entity channel is thin
  there). Withdraw first if a richer nominal coref lifts the shared-entity rate without collapsing precision.
- The CSKG ceiling is a CRUDE verb->intent-word overlap; a concept-level knowledge binding is untested. Do NOT read
  "CSKG doesn't help" as "no knowledge binding could" -- read the CONVERGENT six-channel evidence as "the bottleneck
  is extraction/binding, not the knowledge source".
- I did NOT demonstrate generative means-end SIMULATION or generative goal inference -- both the means-end engine and
  the inverse-planning operator are inert/at-floor. What is demonstrated is Tier-1 explicit-cue anchoring.

## REFUTED brain-fidelity dead-ends (each disproved by a can-fail control)

Participant coref as the NARRATIVE selection lever (hard gate HURT 0.182 vs 0.327; the brief's hypothesis) --
referential coherence as a soft cue -- recency -- Kintsch integration -- GEK entropy-as-content-channel -- the
grounded PHYSICAL chain on narrative (below twin) -- the generative VerbNet inverse-planning operator (at floor) --
the CSKG goal-knowledge ceiling (at floor). The lesson: the brain integrates weak cues and does not hard-gate; and
grounding is only brain-foundational if its operators match the causal DIMENSION -- but even right-dimension
knowledge (goal/intent) does not clear the wall, which is upstream (situation-model construction).

## KEY REALIZATIONS

1. **The genre, not the mechanism, was the first confound (owner's cue).** MAVEN newswire annotates entity-less
   institutional causation; re-instrumenting on narrative turned a located ceiling into a full-population win.
2. **A brain-foundational component that fails points UP the chain -- and here the chain bottoms out at
   EXTRACTION/BINDING, not knowledge.** I followed it: content co-occurrence -> conceptual -> entropy -> script ->
   generative-telic -> retrieved-CSKG. All tie the twin on the unmarked residual. The world-knowledge is available
   (CSKG has it) and does not help; the wall is constructing THIS story's situation model.
3. **Coref is a genre-conditional lever, not a universal unlock** (3.29x on newswire precision; HURTS narrative).
4. **The MAVEN "5% bound" is over-linking** (precision-on-fired 0.363); entity-bound generation is 0.556 precise.
5. **A win can be shallower than its label -- the control caught it.** The goal "means-end" win is MARKER detection
   (marker+content 0.632 >= means-end 0.570). Always reproduce the win from a simpler/wrong source first.
6. **Grounding is necessary but NOT sufficient -- the operators must match the causal DIMENSION.** The full grounded
   chain is below twin on narrative because its operators are physical and narrative is goal/mental.
7. **Even the RIGHT dimension (goal/intent), generated OR retrieved, does not clear it.** The corrected
   inverse-planning operator and the CSKG knowledge ceiling both sit at the co-occurrence floor. The missing
   capability is the generative SITUATION MODEL that binds knowledge to the specific story -- not a knowledge asset.
8. **The proper organ already EXISTS and the finding converges with its own briefs.** `hdlab.theory_of_mind`
   (inverse planning, owner-DONE) is the goal/mental causal reasoner; it is microworld-scoped, and its landed
   residual briefs already name the front-end (real-prose extraction) as the wall. Driving `goal_register` from real
   prose beats co-occurrence CI-sep on goals (+0.105) -- the architecture is right -- but is EXTRACTION-BOUND:
   reinstatement recovers no never-stated goal. Two subsystems (causal reading, mentalizing) hit the SAME front-end
   wall; the next build is the generative situation model that infers latent goals, not another operator/organ.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

- Unmarked causal extraction: the generative causal-antecedent reader clears the FULL narrative population CI-sep,
  but the mechanism is Tier-1 marker anchoring; generative means-end / inverse-planning are INERT.
- The causal content channel is `associative_similarity` = PPMI-SVD co-occurrence (textbase). Six alternative
  channels (incl. VerbNet-telic generation and CSKG-goal retrieval) do NOT clear the unmarked residual -> the
  bottleneck is story-specific situation-model construction (extraction + binding), NOT the knowledge source.
- MAVEN-ERE flagged genre-limited for narrative causation (owner-confirmed).
- `event_type` routing is MFS, not contextual WSD (its own flagged gap) -- a secondary cap.

## Proposed hdlab wire (Q111 -- strategy lands; ADDITIVE, no-regress)

Solve is experiments-only; `git status hdlab/` clean; `situation_reader.causal_links` untouched (the additive
`typed_causal_links` / SDRT coherence layer pattern, witness W12 byte-identical). DO NOT wire the physical grounded
chain into a narrative causal reader -- it regresses below chance. The marked-goal marker+content selection (0.632)
is a simple additive win; the deep capability needs the situation-model construction upstream, not a new operator.

---

**TLDR (plain English).** Stories rarely say "X caused Y"; the reader works it out. Our reader now picks the right
cause on real short stories better than every simple shortcut, and much better when the cause is an explicitly stated
goal ("she WANTED coffee" -> ~57-66% right vs ~25% for word-overlap). But we proved the win is really just *finding
the sentence with the explicit want/decide word* -- the fancier "imagine what she was trying to do" machinery adds
nothing. For causes with no such cue (about 6 in 10), we tried SIX different knowledge sources -- word-co-occurrence,
dictionary meaning, a surprise/prediction "entropy" model, a canonical event-order store, a generative "what is this
action for" model built from a verb dictionary, and even a 6-million-fact commonsense database of people's intentions
-- and **none beat a coin-flip-with-the-right-shape**. That's the important finding: the missing piece is NOT more
facts (we even handed it the facts). It's that the reader can't build a deep enough picture of *this particular
story* -- who wanted what, what each event did to whom -- to connect cause to effect. Fixing that (deep story reading,
not a bigger fact-store) is the real next build, and we've now ruled out the shortcuts so it's unambiguous. No
outside AI at any step.

**QUESTIONS.** None blocking. Judgement call: graded PARTIAL -- a real CI-separated narrative win (marker-anchored)
plus a rigorous, six-way-confirmed location of the true wall (situation-model construction, not knowledge).

**NEXT STEPS.**
0. HIGHEST + FIXABLE NOW (signal-loss autopsy) -- wire a FAITHFUL coref organ (`coref.py` /
   `coreference_resolver.py` / `typed_coref.py` / `event_centrality_coref.py`) for AGENT-BINDING (bind each extracted
   goal to the resolved agent, match to the effect's agent). The autopsy attributes **33% of the goal-subset loss**
   to the crude pronoun->name proxy (BIND_MISS), recoverable without touching the frontier. Goal extraction is
   already faithful (0% miss). This is the brief's "coref is the lever", vindicated for BINDING (not gating).
1. HIGH -- the remaining ~48% is the LATENT frontier: the generative SITUATION MODEL (deep per-story reading that
   INFERS never-stated goals), NOT a knowledge asset (we falsified 6 knowledge channels incl. a 6M-edge KG). This is
   the project's Phase-1 meaning-supply / reading-extractor bottleneck; causal reading inherits it. The proper
   organ (`hdlab.theory_of_mind`, inverse planning) exists but is microworld-scoped -- it needs the front-end to
   populate belief/goal registers from real prose (the `theory_of_mind_residual_is_the_observation_cue_front_end` brief).
2. HIGH (efficiency, proven) -- for marked goals use marker+content selection (0.632), DROP the inert means-end.
3. MEDIUM -- upgrade event_type MFS -> contextual WSD (its flagged gap) to sharpen routing.
4. DO-NOT (re-refuted): any context-free prior (co-occ/conceptual/GEK/script), a bigger causal/goal KB (CSKG ceiling
   ties co-occ), the physical grounded chain on narrative (regresses), hard entity-gating for narrative selection,
   MAVEN-ERE as the narrative gold, any external LLM.
