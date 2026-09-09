---
priority:
status: INTEGRATED
review: EXCELLENT
review_text: "Owner-DONE, reverified 35/35 (MULTISTEP_GOAL_SUBSET_WIN_FULL_POP_LOCATED_NEGATIVE). Located-negative + banked goal-slice organ (MeansEnd ATL-hub, +0.239 CI-sep, coverage 8.7->88%) SHELVED (no live home: needs the multi-engine competition + resolved coref; do-not-wire full-pop, all tie). Upstream brain-foundational scour recorded (3/9 BF; predictive-generative input chain non-live). Dedup: loop-closure INTEGRATED, meaning-channel/eval owner-DONE, crossing=pri-1. New critical gap POSTED (live causal pipeline discards the forward-predictive signal). priority 8 dropped. See INTEGRATION_LEDGER + BRAIN_FOUNDATIONAL_AUDIT S2b (CONT-29)."
---

# PROBLEM: The just-built generative result-state world-model wins its goal-subset but ties the base engine on the full population because 95.2% of the misses are genuine MULTI-STEP PLANS ("wanted milk" -> "went to the store" -> "bought milk"), so build the brain's hierarchical means-ends plan/script chaining to let the forward rollout compose intermediate steps and carry the win from the goal-subset to the full population.

**slug:** `chain_multi_step_plans_and_scripts_for_the_generative_world_model` — **opened:** 2026-09-08 by the strategy session as the direct continuation of the generative result-state world-model (its single biggest quantified lever) — **status:** OPEN. Strategy lands any hdlab wire (Q111). Glass-box, NO external LLM at inference (an offline-built static asset is admissible).

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do.
>
> **YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **"CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) -- RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one -- and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps -- AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) -- that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill -- do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across -- never a ceiling.
> Each fire: implement -> test (can-fail, strongest real floor, info-free twin LOSING) -> iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

> ## BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar -- work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN -- how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure -- do not build the tractable thing and cite neuroscience after.
> 2. **REUSE -- does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE -- does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly -- copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components -- that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.
>
> **(PHASE DIAGRAM -- the substrate is not locked to one regime.)** The substrate's operating point -- store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization -- is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **(FULL-STACK UPSTREAM -- prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED -- make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream capabilities; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT -- YOU AND UPSTREAM -- TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too -- and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
A good reader explains why a character does something by imagining the plan behind it: "she wanted milk, so she went to the store, so she could buy the milk." We just built an engine that imagines ONE step forward — "she did X, so now the world is like Y" — and checks whether Y is what the character wanted. On the stretch of stories where the answer really is one step away, it beats the plain baselines cleanly, and a scrambled version falls apart, so the imagined structure is doing the work. But across ALL stories it only ties the baseline, and we measured exactly why: about 95 out of 100 of the hard cases need a MULTI-STEP PLAN — "went to the store" serves "wanted milk" only if you fill in the whole shopping errand in between, and no single "did X so now Y" fact bridges that gap. This problem is to give the engine the missing ability people use every time they read: chain several imagined steps together — mentally run the plan — so the reader can connect a first action to the goal it ultimately serves.

## 2. WHY THIS ONE
This is the direct continuation of the just-built generative world-model — the project's named MAIN EVENT — and the fidelity scan puts a number on it: multi-step forward-model DEPTH is the single biggest recoverable signal loss (+0.148 on the oracle ladder, ~10x our current +0.016 contribution), and 95.2% of the goal-subset misses are multi-step plans no single-step schema can reach. The parent PROVED the rollout mechanism is correct and brain-faithful on its home turf but stalls at full population purely for lack of depth; closing that turns a located negative into a full-population win. The same generated multi-step expectation was independently named by four downstream consumers (causal edge-correctness, discourse coherence, who-did-what patient pick, implicit-event temporal order), so the lift compounds. Nothing above it in the plan is a bigger or better-quantified lever.

## 3. HOW THE BRAIN DOES THIS (the opening move)
**PINNED (copy the computation):** the meaning of an action is its RESULT-STATE (Schank & Abelson 1977 scripts/RESULT; Trabasso & van den Broek 1985 causal network of goals), and whether an action serves a goal is judged by INVERSE PLANNING — run the rational forward planner, check goal achievement (Baker, Saxe & Tenenbaum 2009; Csibra-Gergely teleology). To DEPTH>1: humans comprehend goal-directed action by instantiating SCRIPTS and PLANS and chaining SUBGOALS hierarchically via means-ends analysis (Schank-Abelson; Radvansky-Zacks event models; hippocampal forward rollout with a goal test, Mattar-Daw 2018). The faithful engine is a model-based generative forward rollout WITH an explicit goal-state test — REUSE the landed `causal_reasoner` traversal as that rollout. (SR/PPR is the WRONG primitive here — occupancy under a fixed policy, already lost as D7 — demote to an optional NEED prioritizer only.)
**OUR-INVENTION-UNDER-TEST (sweep, never adopt — phase-diagram parameters):** rollout DEPTH/beam K, the plan-step transition model, the script-slot representation, how intermediate states are scored, the stopping criterion, and the DENSITY of the plan/script store the rollout traverses.

## MEASURED vs INFERRED
**MEASURED (on disk; do NOT re-derive — see the parent SOLVED + its RESEARCH notes):**
- Single-step rollout, TellMeWhy non-adjacent (Lal 2021), item-level paired bootstrap: GOAL-subset n=92 rollout **0.3804** vs base 0.2935 **+0.0870 CI[0.0217,0.1522]** AND vs topical 0.2391 **+0.1413 CI[0.0652,0.2174]**, BOTH CI-sep; info-free NULL loses (obs 0.3804 > p95 0.3261, p=0).
- FULL population n=256: rollout **TIES** base **+0.0156 CI[-0.0156,0.0469]** (NOT CI-sep); reproduces gen_union 0.3086.
- THE WALL: single-step result-state schema covers **8.7%** of goal->action means-ends (8/92); **95.2%** of GOAL-subset misses are genuine MULTI-STEP PLANS; VerbNet DIRECTED broadening ties base (type-matched coverage 6.5%); GEK forward co-occurrence ties base (directionless — scores 'spilled the milk' 3.96 >= 'bought the milk' 3.64 for a milk goal).
- Coverage by hop-distance (GOAL subset): DIRECT 27% / SINGLE_STEP 4% / TWO_HOP 15% / **DEEP_MULTISTEP (>2 hops) 51%**; our mechanisms reach 46%.
- Fidelity scan (oracle ladder, n=256): base 0.277 -> +our surface means-end 0.293 (+0.016) -> +PERFECT goal simulator 0.441 (**+0.148 forward-model DEPTH, the dominant loss**) -> +PERFECT all-type means-end 0.773 -> gold 1.000. Extraction is NOT the bottleneck (0.98 recall); selection/integration loses ~25%.
- TOP-DOWN STACK prototype (C1 additive constraint-satisfaction integration + C2 directed MULTI-STEP forward model, made interdependent): GOAL-subset **0.467 +0.174 CI[0.098,0.261]** CI-sep, twin loses — ABOVE the single-step 0.380; full-pop 0.316 (+0.039, borderline). Evidence multi-step is the direction.

**INFERRED (the solver must MEASURE; fair game to overturn):**
- That chaining directed result-states to DEPTH K bridges the DEEP_MULTISTEP 51% and lifts the FULL population to CI-sep (not just the goal-subset).
- That the plan/script knowledge (VerbNet result predicates for single steps + plan/script chains) admitted offline through the consolidation gate covers the multi-step transitions — the exact coverage M% is unmeasured.
- The right rollout DEPTH/beam, plan-step transition model, intermediate-state scoring, and stopping criterion (sweepable phase-diagram parameters).
- Whether extending the directed forward model to the non-goal 64% (physics/mental/affect result-states, the +0.332 "other engines" gap) is needed for the full-population win.

## ALREADY TRIED
Two located negatives close the shallow routes; do not re-run them.
- **Single-step COVERAGE broadening (VerbNet directed result-states)** — TIES base (type-matched coverage fell 8.7%->6.5%); 95.2% of misses are multi-step, so a bigger single-step lexicon cannot cross the wall. LOCATED NEGATIVE, closed.
- **GEK forward CO-OCCURRENCE as the plan-step model** — TIES base (+0.0195 CI[-0.0039,0.043]); DIRECTIONLESS — scores a goal-DEFEATING action >= a goal-SERVING one. Wrong axis, closed.
- Also closed this lineage: CSKG typed-edge RETRIEVAL (coverage-bound 34% single-hop; a static-KB traversal reaches only TWO_HOP 15%, not the DEEP 51% — retrieval, not generation); surface goal-object overlap alone (ties base on full-pop); signed-pairwise ECHO coherence decision (mechanism proven, real-data flat — sparse candidate edges link_density 0.11); generate-don't-retrieve edges (generate>retrieve at a precise operating point, still not CI-sep); surface participant-binding (false negative — needs resolved coref, not surface overlap); optimized ACT-R coref (real organ win, flat on TellMeWhy single-cause-ID). Run `python tools/before_you_start.py "<what you are about to do>"`.

## VERIFY BEFORE YOU START
1. Understand the existing organs first: `python tools/substrate_map.py` and `python tools/reader_capabilities.py`; skim `hdlab/`.
2. Read the parent SOLVED IN FULL — `notes/problems/build_the_generative_result_state_world_model/SOLVED.md` plus its three `RESEARCH_*.md` notes — and the adjacent landed organ you REUSE, `notes/problems/build_the_goal_subgoal_hierarchy_graph_for_plot_structure_comprehension/SOLVED.md`.
3. Reproduce the parent's witness (does NOT rewrite landed metrics): `.venv/Scripts/python.exe verification/test_genworldmodel_resultstate.py` (8/8) — confirms the GOAL-subset CI-sep win, the full-pop located negative, and the coverage/multi-step wall on disk before you build.
4. The disk outranks this brief: if any number here disagrees with what those witnesses print, the DISK wins and you say so in SOLVED.md.

## THE BAR
PASS = a brain-faithful MULTI-STEP plan/script-chaining rollout (glass-box, NO external LLM at inference; an offline-built static plan/script asset IS admissible) that turns the GOAL-subset win into a **FULL-POPULATION CI-separated win on TellMeWhy non-adjacent** (Lal 2021), over the strongest floor recomputed PER population — base plausibility 0.2773, topical 0.2500 — with the **info-free twin** (permute the chained result-state across candidates) **LOSING** and **no live reasoner regressing**. Report the CI half-width and the null p95; gate on the floor's UPPER bound. A rigorous LOCATED NEGATIVE is a FULL PASS if it names the exact depth/plan-knowledge ceiling WITH a number — e.g. "multi-step chaining lifts full-pop to +N but stalls because the plan-step knowledge covers only M% of the means-ends transitions, enumerated with counts." Exhausting engineering variations is NOT a negative; it counts only if the brain's ACTUAL mechanism (a directed model-based multi-step rollout with a goal-state test), faithfully built, is what stalled.

## FILES AND ENTRY POINTS
**REUSE (do NOT rebuild):** the landed generative-rollout organs the parent composed — `hdlab/world_state_register.py`, `hdlab/possession_operators.py`, `hdlab/goal_register.py`, `hdlab/force_dynamics_typer.py`; the landed GOAL->SUBGOAL hierarchy graph `hdlab/goal_hierarchy_graph.py` (default-on) + its PPMI+SVD means-end bridge; the landed `causal_reasoner` traversal as the model-based rollout ENGINE; and the parent's cells `experiments/exp_genworldmodel_*.py` — especially `exp_genworldmodel_topdown_stack_v1.py`, whose C2 already prototyped the directed MULTI-STEP forward model (K-hop; the 2-hop bridge fires ~89 vs single-hop ~25). The plan/script knowledge frontier is the LATENT `meaning_foundation` channel (no live read()-time consumer today) plus a curated result-state + plan-schema store admitted offline through the consolidation gate.
**BUILD** in `experiments/` + `verification/` (write freely there); do NOT touch `hdlab/`, the plan, STATUS.md, or another problem's folder. Heavy/long runs -> REMOTE (README "REMOTE RUNS": drop a `REMOTE_RUN_REQUEST_<cell>.md`; the watcher auto-dispatches). Strategy lands any hdlab wire (Q111): state in SOLVED.md exactly what changes in `hdlab/` and why (default-off unless net-positive-and-measured, witnessed, impact-analysed). Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` for the systems you touch and fold an `AUDIT UPDATE` into its §2b.

## DO NOT QUOTE
- Do NOT re-run single-step result-state COVERAGE broadening (VerbNet directed — ties base, type-matched coverage 6.5%; a located negative already).
- Do NOT use GEK forward co-occurrence as the plan-step model (directionless — ties base; scores defeating >= serving actions).
- Do NOT quote the GOAL-subset **0.3804** as a full-population number — it TIES base on full-pop (+0.0156 CI[-0.0156,0.0469]); that tie is the whole point.
- Do NOT use SR/PPR as the reachability engine (wrong primitive, already lost as D7 0/24), a static-KB retrieval traversal as "generation", or Kintsch uniform-inhibition / normalized_recurrence settling for accuracy (monotone no-op).
- Do NOT use an external LLM as the planner/scorer at inference (THE invariant).
