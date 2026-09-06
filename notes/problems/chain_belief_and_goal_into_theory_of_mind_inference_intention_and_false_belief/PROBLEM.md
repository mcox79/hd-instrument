---
slug: chain_belief_and_goal_into_theory_of_mind_inference_intention_and_false_belief
status: INTEGRATED
review: EXCELLENT
review_text: "EXCELLENT, INTEGRATED_BY_STRATEGY 2026-09-06 -- the reasoning phase's first mentalizing system. Glass-box forward chain believes(A,F,t) x wants(A) -> action (acting off the BELIEVED state, so false belief falls out). NEW hdlab/theory_of_mind.py (reuses belief_timeline + goal_register), wired default-on as sm.predict_action/will_act_on/attribute_belief (lazy, additive). BigToM (modern): belief-pred CHAIN 0.849, false-belief +0.871 CI-sep over a 0% floor, twins lose, oracle 1.000. Byte-identical off-vs-on. Reverify test_tom_chain.py 9/9 + landing test_tom_chain_landing.py 12/12. BRAIN_FOUNDATIONAL_AUDIT.md 2b. Follow-ons: board_tom_action arm; goal->fact value binding via the meaning channel."
---

# PROBLEM: the reader stores what each character BELIEVES (per-agent, over time) and what each character WANTS (per-agent goals with status), but it never CHAINS them into a mental-state inference -- so it cannot answer "given what X believes and wants, what will X DO?" (intention attribution) or its false-belief special case (X believes P but P is false, so X acts on the false P, not on reality). Build the glass-box forward inference belief x goal -> predicted intention/action (and its Sally-Anne special case), prove it beats a reality-only floor CI-separated on a MODERN gold with the false-belief items load-bearing and an info-free twin LOSING, or a rigorous located negative naming the exact cause.

**slug:** `chain_belief_and_goal_into_theory_of_mind_inference_intention_and_false_belief` -- **opened:** 2026-09-06 by the strategy session (the substrate is turning the corner from BUILDING the situation-model representation -- who/what/when/where/why + goal/affect/belief/state, all now live and default-on -- to running INFERENCE over it; this is one of the first true "reason over the situation model" problems: Theory of Mind). **status:** CANDIDATE -- a CHAIN + VALIDATION problem: the belief and goal REGISTERS are built, PINNED-faithful, promoted, and default-ON; this composes them into a mental-state inference, it does NOT rebuild either register. You build + validate in `experiments/`; strategy lands any `hdlab/` wire (Q111, witnessed). Glass-box, NO external LLM at inference (THE invariant): the inference rule is a transparent, hand-auditable composition of the two registers, not a learned black box.

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
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch (Theory of Mind / mentalizing; belief;
> goal/intention); inherit its PINNED/INVENTED verdicts; put a short **AUDIT UPDATE** in your submission for any
> verdict you find wrong/stale or any new deviation.

> ## BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar -- work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN -- how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure -- do not build the tractable thing and cite neuroscience after.
> 2. **REUSE -- does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE -- does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly -- copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components -- that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.

## 1. THE PROBLEM IN PLAIN LANGUAGE

When you read a story you don't just track what each character KNOWS and what each character WANTS -- you put the two together to work out what they will DO. If a boy wants his ball and thinks it is in the cupboard, you predict he goes to the cupboard -- even when you, the reader, know his sister secretly moved it under the bed. He acts on what HE believes, not on the truth, so he opens the empty cupboard. That single move -- "given what she thinks is true and what she is trying to get, here is what she'll do next" -- is the heart of understanding a story: it is how we predict characters, understand their mistakes, and see through deception.

Our reader already keeps both halves: a private record of what each character thinks is true at each point in the story, and a record of what each character is trying to achieve. But it never joins them. Nothing in the reader answers "so what will this character do?" from those two records, and nothing captures the classic case where a character will act on something FALSE because they never saw the change. Build the joining step -- the reasoning that turns "believes X" plus "wants Y" into "will do Z" -- and prove, on modern test stories, that it predicts the false-belief action (open the empty cupboard) where a reader who ignored belief and just looked at the truth would get it wrong.

## 2. WHY THIS ONE

The situation-model REPRESENTATION is now largely built: the reader tracks who/what/when/where/why plus per-agent belief, goals, affect, and state, all live and default-on. The next frontier is INFERENCE over that representation, and mentalizing is the sharpest, most load-bearing case: predicting a character's action, understanding a mistake, and reading deception are all the SAME forward computation (belief x desire -> intended action), and it is what narrative comprehension is FOR. It is high-leverage because it reuses two already-proven registers rather than building new representation -- the value is in the CHAIN, which does not exist anywhere on disk. It is also a clean brain-system story (a distinct mentalizing network the substrate does not yet exercise as an inference), so a win moves the reader from "stores mental states" to "reasons with mental states." A rigorous negative is equally valuable: it would localize whether the ceiling is the registers' extraction quality or the inference rule itself, which tells the assembly what to fix next.

## 3. HOW THE BRAIN DOES THIS (the opening move -- PINNED vs OUR-INVENTION)

- **PINNED -- Theory of Mind is a DISTINCT brain system.** Belief representation is right TPJ (Saxe & Kanwisher 2003 -- selective for others' mental-state contents, kept SEPARATE from reality); intention/mentalizing is dmPFC (Frith & Frith 2006; Spunt & Lieberman Why>How). The substrate already honors the belief/intention split (belief_timeline = TPJ-analog, goal_register = dmPFC-analog) -- this problem exercises the dmPFC-analog computation that CONSUMES the belief representation.
- **PINNED -- action = rational planning over (belief, desire); the observer INVERTS and FORWARDS it (Bayesian Theory of Mind / inverse planning; Baker, Saxe & Tenenbaum 2009; Jara-Ettinger, Tenenbaum et al. naive utility calculus).** An agent chooses the action that best achieves its DESIRE given its BELIEF about the world. Observers attribute mental states by INVERTING this (action -> belief/desire) and predict behavior by running it FORWARD (belief x desire -> action). This problem needs the FORWARD direction (predict the action) plus the meta-representational special case below.
- **PINNED -- BDI folk psychology / the intentional stance (Malle 2004; Dennett 1987).** An INTENTION is the plan an agent forms given its beliefs and desires. "Why did X do A / what will X do?" is answered by attributing a belief and a desire and reading off the plan that connects them -- the belief-desire-intention triad.
- **PINNED -- false belief is a META-REPRESENTATION: the agent's belief is held SEPARATE from reality (Leslie 1987; Wimmer & Perner 1983; the Sally-Anne / unexpected-transfer task).** When the believed state differs from the true state (the agent missed a change), the predicted action targets the BELIEVED state, not reality. The belief_timeline already stores per-agent beliefs decoupled from reality (`timeline_belief` vs `reality_at`), so the meta-representation the false-belief inference needs is ALREADY on the substrate -- the missing piece is the forward step that reads the action off the BELIEVED value.
- **THE MECHANISM TO BUILD (the composition):** a transparent forward rule. For an agent A at story-time t with an active goal G (`wants(A)`) that references a fact/object F, the predicted intention/action is the goal-directed action toward G computed over A's BELIEVED state of F (`believes(A, F, t)`), NOT the true state (`reality_at(F, t)`). The FALSE-BELIEF case falls out for free: it is exactly the subset where `believes(A, F, t) != reality_at(F, t)` (A missed the change), and there the belief-driven prediction DIVERGES from the reality-driven one -- which is what makes the false-belief items the load-bearing discriminator in the bar. Keep the rule glass-box and hand-auditable (a named composition over the two registers), NOT a learned model.
- **OUR-INVENTION-UNDER-TEST (sweep, do NOT adopt as truth):** the exact action read-out format (does "act on the believed location" mean predicting the destination, the search location, or the next event predicate?), how a goal G is matched to a fact F it references, the tie-breaking when an agent holds multiple active goals, whether desire is a hard argmax or a soft utility, and second-order belief (X's belief about Y's belief) if the gold demands it. These are parameters/architecture choices -- sweep them, name each PINNED-vs-INVENTED.

## MEASURED vs INFERRED

- **MEASURED (on disk; do NOT re-derive -- these are the REGISTERS this problem chains, not results to reproduce):**
  - The per-agent BELIEF register is built, PINNED-faithful, promoted (`hdlab/belief_timeline.py`), and default-ON in the reader (`track_belief=True`), exposed as `sm.believes(agent, fact, t)` / `sm.knows(agent, fact, t)`. Its belief READ-OUT was validated: driven from the reader's own extraction it scores FANToM info-access ToM (Kim 2023, n=3572) 0.893 vs strongest floor 0.665 (+0.228 CI-sep), false-belief says-ignorant 0.939; a live-e2e belief-at-T on constructed passages 0.902. **These are BELIEF read-out numbers -- knows/ignorant/stale -- NOT action or intention predictions.**
  - The per-agent GOAL register is built, PINNED-faithful, promoted (`hdlab/goal_register.py` + `hdlab/goal_hierarchy_graph.py`), and default-ON (`track_goals=True`), exposed as `sm.wants(agent)` / `sm.why(action, agent)` / `sm.achieved(agent, goal)`, with a per-goal status (active/satisfied/failed) and a goal->subgoal hierarchy. **These answer what an agent WANTS and the goal-why of an action -- NOT what the agent will DO given a (possibly false) belief.**
  - **NOTHING composes belief x goal into an action/intention inference.** There is no `predict_action` / `will_act_on` / intention read-out anywhere in `hdlab/` or the reader (verify by enumeration -- see VERIFY BEFORE YOU START). The two registers sit side by side, never chained. THAT ABSENCE is the defect this problem targets.
- **INFERRED (you must measure):** whether a glass-box forward rule -- predicted action from `believes(A, F, t)` (the believed state) rather than `reality_at(F, t)` (the true state), toward the agent's active goal -- answers intention-attribution AND false-belief-prediction questions on a MODERN gold, CI-separated over the reality-only floor (which MUST lose on the false-belief subset, proving the belief representation is load-bearing) with an info-free twin (shuffled belief/goal bindings) LOSING. UNPROVEN -- it may be null (a valid PASS): the registers' extraction on the gold may be too weak to drive the chain, or the inference may need a world-model the substrate lacks. Everything under INFERRED is fair game to overturn, and overturning it (a rigorous located negative) is a result.

## ALREADY TRIED / DO NOT REDO

- `the_reader_has_no_belief_timeline_what_an_agent_knew_when` (integrated, SOLVED/EXCELLENT) -- BUILT `belief_timeline` (per-agent sample-and-hold belief over story-time). INHERIT it; do NOT rebuild the belief mechanism.
- `theory_of_mind_residual_is_the_observation_cue_front_end` (integrated, SOLVED/EXCELLENT) -- BUILT the perceptual-access registration ledger (the "did A witness E?" front-end feeding belief, 0.992). INHERIT it; do NOT rebuild the observation cue.
- `the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose` (integrated, SOLVED/EXCELLENT) -- drove belief_timeline from the reader's OWN extraction (FANToM 0.893). That work proved the belief READ-OUT (who knows/believes what, when). It did NOT chain belief to goals or predict any action. Read it IN FULL so you don't re-derive the belief read-out -- your job starts where it stops.
- The goal_register + goal_hierarchy_graph problems (integrated, owner-DONE) -- BUILT the goal/intention register and its hierarchy. INHERIT them; do NOT rebuild goal extraction.
- **A CAUTION, not a dead end:** the earlier belief work empirically REFUTED the object-MOVE Sally-Anne paradigm as a source you can MINE from literary prose (0 objects with >=2 extracted moves across 8 LitBank books) -- natural narrative feeds belief through language-about-minds, not object-move chains. This does NOT bar the Sally-Anne STRUCTURE: a CONSTRUCTED modern gold (ToMi-style, BigToM) contains the unexpected-transfer structure by design, which is exactly what you need to make the reality-only floor discriminating. Use constructed/annotated modern gold; do NOT try to mine false-belief action items from raw 19c prose.
- No prior problem has attempted the CHAIN (belief x goal -> action). Run `python tools/before_you_start.py "chain belief and goal into a predicted action / intention inference"` and `python tools/experiment_index.py query intention` / `query "false belief"` / `query "inverse planning"` before building, to confirm.

## VERIFY BEFORE YOU START (the disk outranks this brief)

- **FIRST STEPS (do these before proposing anything):**
  1. Understand ALL the live organs: `python tools/substrate_map.py`, `python tools/reader_capabilities.py` (confirm `track_belief` and `track_goals` are ON by default and see what `sm.believes/sm.knows/sm.wants/sm.why/sm.achieved` expose).
  2. Read IN FULL the two register organs you will CHAIN (do not skim): `hdlab/belief_timeline.py` (`timeline_belief`, `reality_at`, `current_belief_floor`, `WorldEvent`, `divergence`, `knowledge_advantage`, the twin helpers) and `hdlab/goal_register.py` (`GoalRegister.wants/why/achieved/goals_of`, `Goal`, `track_status`), plus `hdlab/goal_hierarchy_graph.py` (`GoalGraph`, `open_superordinate`).
  3. Read how the reader wires them: `hdlab/situation_reader.py` `_read_belief` (binds `sm.believes/sm.knows`) and `_read_goals` (binds `sm.wants/why/achieved`) -- your chain consumes THESE callables off the live `SituationReader.read()`, it does not re-extract.
  4. Read the previous SOLVED solutions named in ALREADY TRIED in their entirety (at minimum the belief-dimension SOLVED.md + `experiments/_belief_reader.py`, and the goal-register SOLVED.md + `experiments/exp_goal_register_qa_v1.py`).
  5. Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- the belief/ToM entries (2026-08-30 belief_timeline; 2026-08-31 belief-dimension) and the goal/intention entries (2026-09-04/05) -- so you inherit the PINNED verdicts and know the ToM system's current fidelity + named deviations.
- **ENUMERATE the absence (an absence claim requires an enumeration, not a search):** `grep -rin "predict_action\|will_act\|intention_of\|act_on_belief\|forward_plan" hdlab/ experiments/` and confirm nothing chains `believes` to `wants`. State how you enumerated in your submission.
- **Reproduce a register FIRST-HAND (positive control) before chaining:** run the belief organ's self-test (`.venv/Scripts/python.exe hdlab/belief_timeline.py`) and the goal register smoke (`.venv/Scripts/python.exe hdlab/goal_register.py`) so you know both halves work before you compose them.
- **Confirm the modern gold on disk:** `data/corpora/fantom/fantom_v1.json` (FANToM, Kim 2023) is present and is an info-access ToM population; `experiments/exp_belief_fantom_infoaccess_v1.py` shows how it was consumed. FANToM is BELIEF-only (who knows) -- good as a corroborating false-belief population, NOT sufficient for intention/action. For the intention x false-belief-ACTION headline you likely need a gold with belief-desire-ACTION items (see THE BAR).

## THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)

PASS = a glass-box mentalizing inference -- a transparent, hand-auditable forward composition of the LIVE belief and goal registers (`believes(A,F,t)` x `wants(A)` -> predicted intention/action, reading the action off the BELIEVED state), NO external LLM at inference -- that answers BOTH intention-attribution ("what will/does A do, and why?") AND false-belief-prediction ("A missed the change, so A acts on the stale state") on a MODERN gold, with ALL of:
1. **CI-separated over a REALITY-ONLY floor** -- the identical action-prediction computed from the TRUE state (`reality_at`), IGNORING belief. This floor MUST LOSE on the false-belief subset (that is the proof the belief representation is load-bearing: where belief and reality diverge, only the belief-driven chain is right). Recompute the floor on the same population; gate on its upper CI bound.
2. **An info-free twin LOSES CI-separated** -- shuffle the belief/goal bindings (random per-agent belief value and/or random goal->agent assignment, same shapes/counts) so the chain's structure is destroyed while the class balance is matched. Report CI half-width + null p95 beside every margin.
3. **Brain-faithful mechanism, stated as an operation** -- the forward inverse-planning composition named above (PINNED to Baker/Saxe/Tenenbaum inverse planning + Leslie meta-representation), reading the action off `believes` not `reality`. COPY the computation, SWEEP the parameters (action read-out format, goal-fact matching, desire hardness). No learned black box.
4. **A MODERN gold, verified** -- a modern ToM/false-belief-with-action dataset (e.g. BigToM (Gandhi et al. 2023) forward belief->action items with matched true-belief/false-belief conditions; ToMi (Le et al. 2019) unexpected-transfer belief-location items; Social IQa (Sap et al. 2019) "what will X do next"), OR a carefully-constructed modern gold with a documented info-free twin. FANToM (on disk) is a valid CORROBORATING info-access population but is belief-only. 19c text is BANNED as a load-bearing gold (owner 2026-09-06); report how the gold was obtained/verified + n. Foundation-building (offline import/annotation of an external dataset) is free and admissible; the RUNTIME inference must use only the substrate (no LLM).

A rigorous LOCATED NEGATIVE is a FULL PASS: the faithful inverse-planning chain, built, does NOT beat the reality-only floor -- with the EXACT cause named and enumerated (e.g. the goal register's extraction does not recover the goal that references the moved fact on this gold; the belief register does not fire on the gold's construction type; the action read-out cannot be scored against the gold's answer format; the gold's false-belief subset is too small to CI-separate). Ask whether the experiment COULD have succeeded before asking why it did not.

## FILES AND ENTRY POINTS

- **REUSE (do NOT rebuild; do NOT write `hdlab/`):** `hdlab/belief_timeline.py`, `hdlab/goal_register.py`, `hdlab/goal_hierarchy_graph.py`, and the live callables on `SituationReader.read()` (`sm.believes/sm.knows/sm.wants/sm.why/sm.achieved`, wired in `hdlab/situation_reader.py` `_read_belief` / `_read_goals`). Read the drivers `experiments/_belief_reader.py`, `experiments/exp_goal_register_qa_v1.py`, `experiments/exp_belief_fantom_infoaccess_v1.py`.
- **BUILD in `experiments/` + `verification/` (you may write freely there):** the chain cell that composes the two registers into a predicted action + the false-belief discriminator, its arms (belief-driven chain / reality-only floor / info-free twin), a scaffold-free witness that recomputes the headline + floors + twin from source, and the modern-gold loader/adjudicator. Heavy corpus-scale runs go REMOTE (drop a `REMOTE_RUN_REQUEST_<cell>.md`; the watcher dispatches -- see the standing rules).
- **DO NOT TOUCH (non-conflict -- these are in-flight or just-integrated; stay in the belief x goal -> action lane):** the who-did-what / agent-patient readout, parse confidence, the coref pick, and the space/ground work. This problem adds an inference on top of the existing registers; it does not modify who/what/where extraction.
- **Q111:** you prototype in `experiments/`, you NEVER write `hdlab/`. If it clears the bar, state in `SOLVED.md` exactly the diff you propose (most likely: a default-off `predict_intention` / `will_act_on(agent, fact, t)` read-out on `SituationReader` composing the two live registers, following the additive `_read_belief`/`_read_goals` pattern) and strategy lands + witnesses it.
- **Audit:** fold an **AUDIT UPDATE** into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (the ToM/mentalizing entries) -- e.g. "belief and goal registers are built but the mentalizing INFERENCE that chains them was absent / is now demonstrated / is a located negative because X."

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote the belief register's read-out numbers (FANToM 0.893; live-e2e belief-at-T 0.902; observation cue 0.992) as an intention or action-prediction result -- they measure who KNOWS/BELIEVES what, a different scorer and population from action prediction. No number crosses scorers/populations; recompute every floor on the item's own population.
- Do NOT quote the goal register's / goal-hierarchy's numbers (WANT-explicit, goal-hierarchy plot-structure gains) as an action-prediction result -- they measure what an agent WANTS and plot structure, not what the agent will DO given a belief.
- Do NOT re-mine false-belief object-move items from raw literary prose -- that was refuted (~absent in real prose). Use a CONSTRUCTED/annotated MODERN gold where the unexpected-transfer / belief-desire-action structure is present by design.
- Do NOT use an external LLM as the inference engine at runtime (THE invariant). Offline import/annotation of an external dataset for the gold is fine; the chain that produces the answer must be the glass-box composition over the substrate's own registers.
- Do NOT rebuild the belief mechanism, the observation front-end, the goal extractor, or the goal hierarchy -- all are built, promoted, and default-ON. This problem is the CHAIN, and only the chain.

---

**TLDR (plain English):** Our reader keeps a private note of what each character thinks is true and what each character wants, but it never puts the two together to guess what a character will do next -- especially the classic case where someone acts on a mistaken belief (opening the cupboard where the ball used to be). Build that joining step and prove, on modern test stories, that it predicts the mistaken action where a reader who only looked at the truth would get it wrong.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm both registers are live and that nothing chains them), picks/constructs a modern belief-desire-action gold with an info-free twin, builds the glass-box forward composition (act on the believed state, not reality), and reports the false-belief margin over the reality-only floor with CI half-width + null p95 -- or a located negative naming the exact cause.
