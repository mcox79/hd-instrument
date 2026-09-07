---
problem: build_the_generative_result_state_world_model
status: SOLVED
bar: "A FULL-POPULATION CI-separated win on at least ONE consumer's MODERN gold -- the rollout turns a named SUBSET win into a full-population win ... the info-free twin LOSES CI-separated ... no live reasoner regressing. A rigorous NEGATIVE is a FULL PASS (e.g. 'the participant-bound rollout beats retrieval + topical + twin CI-sep on the GOAL subset AND lifts the full non-adjacent population toward CI-sep but stops at +N because generating the result-state needs a verb->effect-state schema the meaning foundation covers only M% of, enumerated with counts -- the knowledge-foundation coverage wall, quantified, filed as the next problem')."
result: "LOCATED NEGATIVE (the bar's explicitly-blessed full pass), with the SUBSET positive delivered. Built the participant-bound GENERATIVE result-state rollout (compose world_state_register + possession_operators + goal_register: simulate the effect action forward to a result-STATE, CHECK type-matched achievement against the goal-STATE, suppress goal-DEFEATING actions). On modern TellMeWhy non-adjacent (Lal 2021, item-level paired bootstrap): GOAL-subset POSITIVE n=92 -- rollout 0.3804 vs base 0.2935 +0.0870 CI[0.0217,0.1522] AND vs topical 0.2391 +0.1413 CI[0.0652,0.2174], BOTH CI-sep; the many-shuffle info-free NULL loses (observed 0.3804 > null p95 0.3261, p=0.0). FULL population n=256: ties base (rollout-base +0.0156 CI[-0.0156,0.0469], NOT CI-sep) -- reproduces the prior gen_union 0.3086. THE WALL, QUANTIFIED: the single-step result-state schema covers only 8.7% of goal->action means-ends (8/92) and 91.2% of the GOAL-subset misses are COVERAGE-misses; VerbNet directed broadening raises nothing (type-matched coverage 6.5%) because 95.2% of the misses are genuine MULTI-STEP PLANS ('wanted milk'->'went to the store') with NO single-step result-state achieving the goal -- the wall is rollout DEPTH (plan/script chaining), NOT verb->result-state coverage. TOP-DOWN into extraction (bar item 4): a can-fail positive control -- the generated goal-state expectation discriminates achieve-vs-defeat 10/12 where the feed-forward surface silo (goal-object overlap) TIES 0/12."
floor: "base plausibility engine (content+physics+psych, goal OFF) 0.2773 = the STRONGEST floor, recomputed on each population (GOAL subset 0.2935, OTHER 0.2475); topical (content-only argmax) 0.2500; CSKG typed-edge retrieval (coverage-bound 34%); GEK forward co-occurrence reachability (broad but directionless) 0.2969 (+0.0195 CI[-0.0039,0.043], ties base); info-free NULL by permuting the generated result-state across candidates (400 draws), GOAL null p95 0.3261 / full null p95 0.3047."
controls: "(1) INFO-FREE NULL (permute the result-state signal across candidates, 400 draws -> null mean/p95/p-value): on the GOAL subset the rollout BEATS null p95 (obs 0.3804 > 0.3261, p=0.0 -> the generated state's placement is load-bearing); on the FULL population it does NOT (obs 0.293 < p95 0.305 -> the state fires on too few items, the located negative). (2) BASE ABLATION (goal OFF) -- rollout beats base CI-sep on the GOAL subset (+0.087), isolating the achievement check. (3) TOPICAL floor -- CI-sep on the GOAL subset (+0.141). (4) GEK-DIRECTIONLESS diagnostic -- learned forward co-occurrence scores a goal-DEFEATING action >= a goal-SERVING one ('wanted milk'->'spilled milk' 3.96 >= '->bought milk' 3.64); the broad GEK arm ties base -> co-occurrence is the WRONG axis. (5) UPSTREAM broadening (VerbNet directed result-states) ties base; the miss decomposition isolates the residual as MULTI-STEP plans (95.2%), NOT single-step coverage. (6) TOP-DOWN can-fail positive control -- surface silo ties 0/12, rollout 10/12. (7) NO-REGRESS -- the rollout is inert without an explicit goal marker (byte-identical to the goal-OFF base) and modifies no live reasoner (additive channel)."
files_changed: "experiments/exp_genworldmodel_resultstate_v1.py (THE rollout: participant-bound result-state achievement check composing world_state_register + possession_operators + goal_register + force_dynamics; arms base/topical/objmatch/typed/gen_union/rs_refine/rs_strict/rs_bound/rs_union/gek_broad; null-p95 twin; GEK-directionless diagnostic; coverage enumeration; topdown_control(); no_regress()); experiments/exp_genworldmodel_upstream_verbnet_v1.py (the UPSTREAM VerbNet directed-result-state broadening + the single-step-vs-multi-step-plan miss decomposition; writes a VerbNet result-state cache); verification/test_genworldmodel_resultstate.py (8/8 witness); verification/test_genworldmodel_upstream_verbnet.py (3/3 witness); data/exp_genworldmodel_resultstate_v1/metrics.json; data/exp_genworldmodel_upstream_verbnet_v1/{metrics.json,verbnet_resultstates.json}. Gold reused: data/corpora/tellmewhy/. NO hdlab write (Q111 -- proposed landing stated below)."
reverify: ".venv/Scripts/python.exe verification/test_genworldmodel_resultstate.py   # 8/8 (~10s): W1 reproduces disk baseline; W2 GOAL-subset CI-sep over base+topical; W3 info-free NULL loses (obs>p95,p=0); W4 full-pop located negative + coverage wall; W5 GEK co-occurrence ties base; W6 top-down can-fail control (silo ties, rollout discriminates); W7 no-regress/additive; W8 selectivity coverage-capped.  THEN .venv/Scripts/python.exe verification/test_genworldmodel_upstream_verbnet.py   # 3/3: VerbNet directed result-states, broadening ties base, 95% multi-step residual"
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
- **P2 -- wire the LATENT meaning channel live FIRST** (`meaning_foundation` has no read()-time consumer today);
  the multi-step rollout reads the resolved participants + result-state predicates over it.
- **P3 -- once the multi-step rollout lands, REVISIT the four consumers** (causal edge-correctness c, coherence
  full-population unmarked-causal, who-did-what two-valid patient, implicit-event temporal order) to receive the
  generated top-down expectation -- each named it independently.
- **DO NOT re-file (tested + closed this round):** a bigger SINGLE-STEP verb->result-state lexicon (VerbNet
  directed broadening ties base; 95% of misses are multi-step); GEK / co-occurrence as the means-end
  (directionless -- scores defeat >= achieve); CSKG retrieval (coverage-bound 34%); the surface goal-object
  overlap alone as the full-population fix (ties base). Do NOT use an external LLM at inference (THE invariant).
