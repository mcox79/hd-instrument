---
review: EXCELLENT
review_text: Reverified first-hand verification/test_causal_selection_plausibility_and_scoping.py 19/19 + a new pure-hdlab landing witness test_causal_mental_bridge_landing.py 9/9 (connective causal QA + goal WANT/WHY QA + events + coref BYTE-IDENTICAL off-vs-on on 12 board docs; goal graph strict SUPERSET; +214 mental_bridge links; all_capabilities_off() sets the flag False). LANDED (Q111): (1) promoted the event-TYPE organ VERBATIM -> hdlab/event_type.py (WordNet verb supersense -> folk-psych ontology; consolidates the idiom_lexicon/causation_typing supersense pattern); (2) wired the MENTAL-BRIDGE PASS-2 into _read_causation behind causal_mental_bridge (DEFAULT-ON pure-add; connective links emitted FIRST so the goal-graph stays a superset -- the measured landing requirement). The brief's literal route (retire scoping via a plausibility selector) is a rigorous LOCATED NEGATIVE = the full pass the bar names (connective selection is STRUCTURAL, scoping is its optimum, the QA gold is circular; perfect-parse oracle LOSES -> mechanism-agnostic). The landable value crosses the DEEPER wall: mental causation (11/16 real cause verbs; force dynamics covers 3/16), a distinct brain system. Exemplary: refuted the brief's own measured premise + built the mechanism where it belongs (bridging, not connective) + an 11-stage brain-fidelity audit + a signal-loss ladder localizing the residual UPSTREAM (coref 0.500, WSD 0.875), not the selector. DEFERRED to the integration ledger / top-down pass (the FIELD-accuracy + downstream-signal work): GroundedSemanticGraph WSD wire (type_ok 0.688->0.750), the coref-experiencer wire, the mined mental-bridge gold instrument, and 3 consumers to receive the event-type signal (causation_typing mental typing 3/16->16/16, affect OCC channel, goal-graph motivational spine). §2b folded. INTEGRATED 2026-09-05.
---

# PROBLEM: the causal dimension's connective/bridge cause-SELECTION is a density-brittle OUR-INVENTION adjacency heuristic — it regresses −0.0594 CI-separated when the event set densifies, and we currently SCOPE `predicate_recall` out of the causal candidate set as an interim patch. The brain-faithful parse-structural fix is a LOCATED NEGATIVE (clausal-head selection fails 3 ways, −0.079 to −0.317, because the OOD 19c parse cannot identify the causal clausal head) AND cannot work IN PRINCIPLE (Koornneef & Van Berkum 2006; Sanders & Noordman — plausibility resolves the cause even given a perfect parse; cross-clausal connectives may have no governed structural argument). Proven by isolation (`exp_event_detection_causal_oracle_v1.py`): a PERFECT parse is WORSE for causal and oracle participants don't help → a SEMANTIC compatibility scorer is structurally necessary. Build a glass-box FORCE-DYNAMIC / situation-model PLAUSIBILITY causal scorer (Talmy/Wolff force dynamics; implicit-causality verb-class + a normality/compatibility scorer — DROP participant-overlap, empirically falsified) that picks the connective cause CI-separated over the current adjacency/connective heuristic AND over the scoped floor, info-free (shuffled-plausibility) twin LOSING, no-regress on the other dims — retiring the scoping workaround. Buildable as a coarse VerbNet/FrameNet + argument-compatibility first cut; full fidelity via the meaning hub. Glass-box, NO external LLM.

**slug:** `a_force_dynamic_meaning_hub_causal_scorer_retire_the_connective_scoping_workaround` — **opened:** 2026-09-05 by the strategy session, the explicit follow-on the event-detection SOLVED note named (§5/§6/§9: the parse-structural causal fix is a located negative that cannot work in principle; the isolation proof shows a semantic plausibility scorer is structurally necessary, and the current `predicate_recall`-scoping is an interim workaround to retire). **status:** OPEN. Strategy lands the Q111 wire; fold a §2b AUDIT UPDATE. Glass-box, NO external LLM.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the structure + computation; PINNED vs OUR-INVENTION. RESEARCH where unsure.
> 2. **REUSE — does an existing organ already do it?** Check `tools/substrate_map.py` / `hdlab/` FIRST.
> 3. **GENERALIZE — how does the brain generalize it?** Build for that.
> 4. **HIT A WALL? GO DEEPER.** A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, failed.
> 5. **OPTIMIZE BY EXACT REPLICATION.** Copy the computation, SWEEP the parameters.
> 6. **PERFORMANCE vs THE BRAIN.** Where do we lose signal? The mechanism-diff.
> 7. **ADJACENT COMPONENTS.** Map the neighbours — seeds the next problems.
> 8. **COMPLETION BAR.** COMPLETE + EXCELLENT + conveys the full benefit?

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a story says one thing happened "because" of another, the reader has to pick which earlier event is the cause. The current method just guesses the nearest preceding event — a crude proximity rule that breaks as soon as the reader notices more events, because the real cause is often not the closest one. We tried the textbook grammar-based fix (follow the sentence structure to the cause) and it failed three different ways, partly because the 200-year-old prose parses badly and partly because — as the reading-science literature shows — people pick the cause by what makes SENSE, not by grammar alone, even when the grammar is perfect. The job is to build a glass-box "does this cause plausibly produce this effect" scorer, grounded in how forces and intentions work, so the reader picks the right cause by meaning — and to retire the stop-gap that currently just hides the problem by excluding events from the causal search.

## 2. WHY THIS ONE — the parse-structural route is a proven dead-end and a scoping workaround is live
The brain-faithful grammar route is a located negative in three ways and cannot work in principle — the isolation experiment showed a PERFECT parse is actually WORSE for causal and oracle participants don't help, which pins the missing organ as a semantic plausibility scorer, not more parsing. Meanwhile the causal dimension currently limps along by SCOPING a whole event source out of the candidate set — a workaround, not a fix. This is the one causal lever with a diagnosis pointing straight at the correct brain mechanism (force dynamics / implicit causality) and a concrete first cut, and it retires standing debt.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — event-detection SOLVED §5/§6/§9):** the connective/bridge cause-selection is a density-brittle OUR-INVENTION adjacency heuristic (−0.0594 CI-sep on densification); parse-structural clausal-head selection fails 3 ways (−0.079 to −0.317); the perfect-parse isolation (`exp_event_detection_causal_oracle_v1.py`) shows a perfect parse is WORSE for causal and oracle participants don't help → participant-overlap is empirically falsified and a semantic scorer is structurally necessary.
- **INFERRED (you must measure):** whether a glass-box force-dynamic / implicit-causality plausibility scorer crosses CI-separated over the adjacency/connective heuristic AND the scoped floor, with the shuffled-plausibility twin losing and no-regress on the other dims.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: read `notes/problems/register_robust_event_detection_turn_on_and_expand_lifts_every_who_did_what_arm/SOLVED.md` §5, §6, §9 IN FULL; read `experiments/exp_event_detection_causal_oracle_v1.py` (the perfect-parse-is-worse isolation) and `exp_event_detection_structural_causal_v1.py` (the 3 clausal-head negatives) IN FULL.
- Check `tools/substrate_map.py` / `hdlab/` for the landed `causation_typed` path (Talmy/Wolff), `sm.causal_links`, and the event/role front end FIRST — REUSE, do not re-derive.
- Reproduce first-hand: the scoped-floor causal number + the connective-heuristic densification regression (the can-fail baseline the plausibility scorer must beat).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a glass-box force-dynamic / situation-model plausibility causal scorer (Talmy/Wolff force dynamics; implicit-causality verb-class + a normality/compatibility scorer; participant-overlap DROPPED as falsified) that picks the connective cause CI-separated over BOTH the current adjacency/connective heuristic AND the scoped floor, with a shuffled-plausibility info-free twin LOSING and no-regress on the other dimensions — and the `predicate_recall` scoping workaround retired. A coarse VerbNet/FrameNet + argument-compatibility first cut is admissible (full fidelity via the meaning hub). Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — a glass-box force-dynamic causal scorer cannot beat the connective heuristic within the invariant (with the named cause + number) — is a FULL PASS. Strategy lands the Q111 wire; fold a §2b AUDIT UPDATE.

## ALREADY TRIED / DO NOT REDO
- Parse-structural clausal-head selection — 3 located negatives (−0.079 to −0.317); cannot work in principle (Koornneef & Van Berkum 2006; Sanders & Noordman). Do NOT re-attempt a parse-only fix.
- Participant-overlap — empirically falsified by the oracle-participant isolation. DROP it.
- The connective adjacency/proximity heuristic — density-brittle (−0.0594). It is the floor to beat, not a component to extend.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE the landed `causation_typed` path (Talmy/Wolff, `hdlab`), `sm.causal_links`, the causal readout, and the event/role front end. Measure on the causal dimension of the who-did-what arms. Strategy lands the Q111 wire; fold a §2b AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md`.

## DO NOT QUOTE
- Do NOT quote a causal gain without the shuffled-plausibility info-free twin LOSING + no-regress on the other dims.
- Do NOT quote the parse-structural or participant-overlap routes as open — they are located negatives / falsified.
- Do NOT use an external LLM (the invariant).
