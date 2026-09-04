---
priority: 7
review:
review_text:
---

# PROBLEM: the just-landed GOAL register is FLAT — it tracks each character's goals + a status field, but NOT the goal→subgoal→plan→action→outcome HIERARCHY that is the backbone of narrative ("she wanted to escape [superordinate], so she found a key [subgoal], to unlock the door [sub-subgoal]"). Plot comprehension IS building that goal/causal network and reinstating a superordinate goal after an intervening subgoal completes (Trabasso & van den Broek 1985 causal-network; Suh & Trabasso 1993 reinstatement over distance; salience from CONNECTIVITY in the network, not hierarchy depth). The flat register already MEASURES reinstatement (status-gated wants() = 1.000 vs a recency floor 0.000) but only over the flat list; an explicit goal→subgoal GRAPH with connectivity-based salience + reinstatement over a distance of intervening material is the richer capability the goal dimension earned. Build the glass-box goal-hierarchy graph (link a subgoal to its superordinate via purpose/enablement relations over the reader's OWN goal + causal extraction) and answer plot-structure questions (why-chain: "why did X find the key" → "to escape"; superordinate reinstatement across intervening subgoals) CI-separated over a flat-register floor with an info-free twin LOSING — or a located negative naming why the hierarchy cannot be built glass-box from explicit narrative.

**slug:** `build_the_goal_subgoal_hierarchy_graph_for_plot_structure_comprehension` — **opened:** 2026-09-04 by the strategy session, the explicit §7 follow-on the owner-DONE `the_situation_model_has_no_goal_intention_dimension` named (the flat register is OUR-INVENTION-flat on the graph; the richer follow-on is the connectivity-salience goal→subgoal GRAPH). **status:** OPEN. Strategy lands any hdlab wire (Q111). Glass-box, NO external LLM.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** The mission is the most brain-faithful substrate. A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

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
The reader now tracks what each character wants, but as a flat list. Stories aren't flat: a big goal ("escape") spawns smaller goals ("find a key") that spawn actions ("search the room"), and when a small goal is met the reader snaps attention back to the still-open big goal. That goal-and-plan structure is basically what "understanding the plot" means. The job: connect the goals the reader already finds into a tree (this small goal serves that bigger one), so it can answer plot questions — "why did she look for the key?" ("to escape") — and correctly return to the overarching goal after a sub-task is done.

## 2. WHY THIS ONE — it is the goal dimension's named richer capability, and it composes existing organs
The goal register (owner-DONE) landed the flat per-character goals + a status field, and MEASURED reinstatement over the flat list (status-gated wants 1.000 vs recency 0.000), but explicitly named the goal→subgoal GRAPH with connectivity salience as its §7 follow-on ("OUR-INVENTION-flat on the graph today"). It REUSES the landed goal register + the causal readout (the causal network the reader already builds) — the graph is the composition of what exists. It moves the reader from tracking goals to comprehending PLOT, the highest form of narrative understanding, and it diversifies the queue toward reasoning over the (now-complete) situation model.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: narrative comprehension builds a GOAL/CAUSAL NETWORK — nodes (goals, attempts, outcomes) linked by MOTIVATION (a goal motivates a subgoal) and ENABLEMENT/physical-cause relations; a node's importance to the reader is its CONNECTIVITY in the network (Trabasso & van den Broek 1985 — recall + judged-importance predicted by number of causal connections, NOT hierarchy depth or recency); reinstatement returns to the most-connected still-unsatisfied superordinate after a subgoal completes, over a distance of intervening material (Suh & Trabasso 1993). OUR-INVENTION-under-test: the exact subgoal→superordinate linking rule (purpose "to VP" / enablement / temporal-precedence cues), the connectivity-salience metric, the reinstatement-over-distance rule. Sweep, do not adopt. REUSE (do NOT re-derive): the landed `hdlab/goal_register.py` (the flat goals + status + reinstatement), the reader's causal readout / causal network (`_read_causation`, the connective/bridge links), the entity/coref binding.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — the goal SOLVED):** the flat goal register: WANT-explicit CI-sep, agent-bound, status field 1.000 vs 0.333, reinstatement 1.000 vs 0.000 over the FLAT list; the reader already builds a causal network (connective/bridge links, the causal readout at 0.905).
- **INFERRED (you must measure):** whether a glass-box goal→subgoal graph (linking subgoals to superordinates via purpose/enablement over the reader's own goal + causal extraction, with connectivity-based salience) answers plot-structure questions (goal-why-chain + superordinate reinstatement across intervening subgoals) CI-separated over a flat-register floor, info-free (shuffled-edges) twin LOSING; the residual + its named cause.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: `python tools/substrate_map.py`, `python tools/reader_capabilities.py`; read `notes/problems/the_situation_model_has_no_goal_intention_dimension/SOLVED.md` §7 (the flat-graph limitation + the reinstatement measurement) IN FULL; read `hdlab/goal_register.py` (the flat register + `track_status` + `wants()` reinstatement), `hdlab/situation_reader.py` (`_read_goals`, `_read_causation` — the causal network to compose with), `hdlab/causation_typing`/the causal organs.
- Check the prior narrative-causal-graph problems (`narrative_causal_graph_missing_implicit_inference_organ`, integrated) so you EXTEND/compose, not re-derive.

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a glass-box goal→subgoal hierarchy graph (subgoal→superordinate motivation/enablement links + connectivity salience + reinstatement-over-distance; NO external LLM) that answers plot-structure questions (goal-why-chain + superordinate reinstatement across intervening subgoals) CI-separated over a flat-register floor, with a shuffled-edges info-free twin LOSING and no-regress on the flat goal arm. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — the goal hierarchy cannot be built glass-box from explicit narrative (with the named cause + number, e.g. subgoal→superordinate linking needs world-knowledge inference) — is a FULL PASS. Strategy lands the Q111 wire.

## ALREADY TRIED / DO NOT REDO
- The FLAT goal register + status + flat-list reinstatement is LANDED (goal dimension, default-on) — this is the GRAPH (subgoal→superordinate links + connectivity salience), a new axis; do not re-derive the flat register.
- The causal network (connective/bridge links) is landed — COMPOSE with it (motivation vs physical-cause are disjoint but both are network edges), do not re-derive causal detection.
- Do NOT fold this into the flat register — it is an explicit relational GRAPH over the goals.
- Do NOT use an external LLM (the invariant).

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE `hdlab/goal_register.py`, `hdlab/situation_reader.py` (`_read_goals`/`_read_causation`), the causal organs. Add a `goal_hierarchy` board arm / plot-structure QA. Strategy lands the Q111 wire. Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote a gain without the shuffled-edges info-free twin losing (else it is the flat register, not the graph).
- Do NOT claim reinstatement without measuring OVER A DISTANCE of intervening subgoals (the flat register already does adjacent reinstatement).
- Do NOT use an external LLM (the invariant).
