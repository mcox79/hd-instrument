---
priority: 10
review:
review_text:
---

# PROBLEM: the situation model tracks WHO/WHAT/WHEN/WHERE, physical CAUSATION, who-KNOWS-what (belief), who-IS-what (state) and who-HAS-what (possession) — but it has NO INTENTIONAL/GOAL dimension: what each agent is TRYING to achieve. Narrative comprehension is overwhelmingly goal-driven (a story's causal spine is goal→plan→action→outcome; Trabasso & van den Broek 1985) and INTENTIONALITY is the 5th Zwaan-Radvansky event-indexing dimension, so the reader cannot answer goal-based "why" ("why did she go to the market?" → to buy bread [a GOAL], not a physical cause), "what does X want", or "did X achieve their goal". Build a glass-box GOAL/INTENTION dimension: extract agent goals from text (explicit desire/intention/purpose constructions + goal→plan→action inference), track them in the situation model as a per-agent goal register, and answer goal-QA on real narrative CI-separated over a trivial floor with an info-free twin losing — or a located negative naming why goals are not recoverable glass-box.

**slug:** `the_situation_model_has_no_goal_intention_dimension` — **opened:** 2026-09-04 by the strategy session (the one classic situation-model dimension not yet built — the reader has coref/events/temporal/causal/location/belief/state but no goal/intention). **status:** OPEN. Strategy lands any hdlab wire (Q111, default-off, witnessed). Glass-box, NO external LLM at inference (the invariant).

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** The mission is the most brain-faithful substrate. A rigorous located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar — work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure — do not build the tractable thing and cite neuroscience after.
> 2. **REUSE — does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE — does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly — copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components — that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When we read a story, most of what we understand is WHY people act — and "why" is usually a GOAL, not a physical push: she went to the market *in order to* buy bread; he lied *because he wanted* to protect her. Our reader records what happened, who did it, when, where, and what physically caused what — but it has no idea what any character is TRYING to do. So it can't answer the most natural story questions ("what does she want?", "why did he do that?", "did she get what she was after?"), and it can't use goals to make sense of a sequence of actions as one plan. The job: give the reader a goal-tracker — pull each agent's goals from the text (from purpose words like "to"/"in order to"/"so that" and want/intend/try verbs, plus the goal→plan→action pattern), keep a running per-character goal register, and answer goal questions on real narrative.

## 2. WHY THIS ONE — it is the missing 5th situation-model dimension, and the backbone of narrative
Zwaan & Radvansky (1998) index events on FIVE dimensions — time, space, causation, protagonist, and INTENTIONALITY (goals). The reader has the first four (temporal / location / causal / coref+entity) but NOT the fifth. And intentionality is not a peripheral add-on: goal→plan→action→outcome is the CAUSAL SPINE of story comprehension (Trabasso & van den Broek 1985; the events most central to a narrative are the goal-linked ones). Without it, the reader's "why" is limited to physical causation (the causal dimension), missing the goal-based "why" that dominates real text. This is a distinct, high-leverage capability: it unlocks a whole class of questions and gives the causal/coref dimensions a goal scaffold to attach to.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: goal/intention representation is the DESIRE+INTENTION component of the intentional stance (Dennett), computed by the mentalizing network (medial prefrontal cortex; Saxe/Frith) — DISTINCT from belief (what an agent KNOWS, the existing belief/ToM dimension) and from physical causation. Narrative goal structure is a goal→subgoal→plan→action hierarchy (Schank-Abelson scripts; Trabasso goal-plan causal network); comprehenders infer a goal when an action is otherwise unexplained (abductive goal inference) and track goal satisfaction/failure. OUR-INVENTION-under-test: the exact goal-extraction cues (purpose/desire/intention constructions + the abductive goal-inference rule) + the goal-register data structure + the satisfaction/failure update. Mark PINNED vs OUR-INVENTION. Explicit purpose/desire constructions are the reliable anchor (like the connective anchor for causation); unstated goals via script inference are the harder tail.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** the reader's current QA dimensions are coref/events/salience/temporal/causal/location/belief/state — a first-hand grep confirms NO goal/intention dimension (this problem builds it). The causal dimension recovers PHYSICAL connective causation (because/so), not goal-based purpose (to/in-order-to/so-that) — the two are disjoint constructions.
- **INFERRED (you must measure):** whether a glass-box goal extractor (explicit purpose/desire/intention constructions + an abductive goal-inference rule over the reader's own event stream) populates a per-agent goal register that answers goal-QA on real narrative CI-separated over a trivial floor (e.g. most-recent-action, or the physical-cause) with an info-free twin (shuffled goal-agent binding) LOSING; the recall/precision split between EXPLICIT goals (purpose constructions) and INFERRED goals (script/abductive); the residual + its named cause.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: `python tools/substrate_map.py`, `python tools/reader_capabilities.py`; read the sibling situation-model dimensions IN FULL to reuse their pattern — `situation_model_has_no_mutable_world_state_register` / `the_reader_has_no_copular_is_a_binding_schema` (state) + `the_reader_has_no_belief_timeline_what_an_agent_knew_when` (belief) SOLVED.md (the per-agent register + QA-arm pattern you mirror), and `causation_is_typed_per_clause...` (the causal dimension, to contrast physical-cause vs goal). Read `hdlab/situation_reader.py` (`_read_causation` / `_read_entity_states` / the belief timeline — the register+readout pattern) + `experiments/exp_situation_model_qa_v1.py` (`build_causal_questions` + the per_dimension readout — you add a `goal` dimension the SAME way, non-circular gold from purpose-construction grammar).
- Build a NON-CIRCULAR goal gold from the text's purpose/desire grammar (like the causal connective gold), NOT from the reader's own goal_net.

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a glass-box GOAL/INTENTION dimension (a per-agent goal register populated from explicit purpose/desire/intention constructions + an abductive goal-inference rule over the reader's event stream; NO external LLM) whose `goal` QA answers on real narrative (a `goal` per_dimension row) score CI-separated over the strongest trivial floor (most-recent-action / physical-cause), with a shuffled-goal-agent info-free twin LOSING CI-separated and NO regression on the other dimensions (additive). Report CI half-width + null p95; recompute the floor on the item's own population. A rigorous located NEGATIVE — goals are not recoverable glass-box on natural text beyond the explicit-purpose slice, with the named cause + number (e.g. abductive goal inference needs the meaning/world-knowledge channel) — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed) + adds the `goal` board arm.

## ALREADY TRIED / DO NOT REDO
- The CAUSAL dimension recovers PHYSICAL cause (because/so connectives) — do NOT re-derive it; goals are a DISJOINT construction class (to / in order to / so that / want / intend / try). This is the intentional dimension, not another causal tweak.
- The BELIEF/ToM dimension tracks what an agent KNOWS — goals are what an agent WANTS/INTENDS; do NOT conflate them (distinct mentalizing components).
- Do NOT build a goal gold from the reader's own goal_net (circular) — the gold comes from the purpose/desire GRAMMAR, read off the token stream.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE `hdlab/situation_reader.py` (mirror `_read_causation` / the belief-timeline register+readout), `experiments/exp_situation_model_qa_v1.py` (add a `goal` dimension: a `build_goal_questions` + `_answer_goal` + the per_dimension readout, non-circular purpose-grammar gold + a floor + a twin), the entity/coref stream (goals bind to resolved agents). Strategy lands the Q111 wire (default-off `track_goals` flag → `sm.goal_register`) + the `goal` board arm. Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote a goal-QA number without its floor + twin — a register that always names the most recent action is not goal comprehension.
- Do NOT quote the explicit-purpose slice as the full capability — report the explicit-vs-inferred split (inferred/abductive goals are the hard tail, likely gated on the meaning channel).
- Do NOT use an external LLM to extract or infer goals (the invariant).
