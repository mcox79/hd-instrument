---
priority: 3
review:
review_text:
---

# PROBLEM: the reader has a landed but default-OFF copular is-a/attribute capability (`bind_entity_states` → `sm.entity_states` + `sm.state_register`) with NO live consumer and NO board metric, so it scores a live 0/376 on predicate complements and cannot be turned on under the no-default-off rule. WIRE the consumer: add a "state" dimension to the situation-model QA harness that ASKS "what/who is X" / "is X a Y" and ANSWERS off `sm.state_register`, flip `bind_entity_states=True` in that reader, and prove a CI-separated `qa_state` row (+ a lift on `qa_aggregate`) on the baseline board vs the copular problem's validated most-recent-noun floor + shuffle twin — then the flag is net-positive on a real consumed metric and turns ON.

**slug:** `wire_the_copular_state_qa_consumer_and_turn_on_bind_entity_states` — **opened:** 2026-09-03 by the strategy session (a researched consumer-wire for the owner-DONE `the_reader_has_no_copular_is_a_binding_schema`). **status:** OPEN. Glass-box, NO external LLM. This is an EXPERIMENTS + BOARD wire (no hdlab change — the producer `bind_entity_states` already landed); strategy owns the board, so this is a scoped integration a solver executes end-to-end + measures.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** 🧠 OPENING MOVE: how does the BRAIN do THIS? Name the structure + computation, replicate it. Mark PINNED vs OUR-INVENTION. A rigorous located NEGATIVE is a PASS if the brain's actual mechanism, faithfully built, is what failed. 📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the copular entry + its OWED follow-ons).

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
The reader can now read "Ahab is the captain" / "the room is cold" and record that as a fact about the entity (a landed, tested capability), but it's switched OFF — because nothing in the live system ever ASKS "what is Ahab?", so turning it on would cost a little compute for zero measured benefit. The fix is to make the reading test actually ask those questions and grade the answers, so the capability has something to be good AT. Then turning it on demonstrably helps and we turn it on. The brain does exactly this: a copular predication updates the entity's attribute record, and comprehension can later query that record ("what was he?") without re-reading — a discourse-model read-out, not a text re-scan.

## 2. WHY THIS ONE — the capability is landed + validated but consumer-less (measured)
`bind_entity_states` (default-off, `hdlab/situation_reader.py::_read_entity_states`) produces `sm.entity_states` (typed `EntityState(holder, property, htype∈{pred_adj, pred_nom, ident})`) + `sm.state_register` (`state_at(holder)` / `is_in_state(holder,val,semantic=True)` read-back; `state_at('ahab')=['captain']` round-trips — witnessed). But grep confirms NO live consumer reads it (only its own witness), and the QA harness `DIMENSIONS` (`experiments/exp_situation_model_qa_v1.py:135`) has coref/events/salience/temporal/causal/location/belief but NO "state" — so "What is Ahab?" misroutes to `events` and the base reader scores **0/376** on predicate complements (`exp_copular_is_a_binding_readout_v1.py:4-6`; `BRAIN_FOUNDATIONAL_AUDIT.md:74`). Per no-default-off, a flag with no consumed metric stays off; this wire GIVES it one. Turn-on cost is only +5ms/read (measured, post the DG-projection cache speedup).

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: predicate-nominal / predicate-adjective copular predication updates the referent's ATTRIBUTE binding (Higgins 1979 predicational vs identificational; ATL amodal hub for is-a category — Lambon Ralph 2017), queried later from the discourse/situation model (a mental-model read-out, Glenberg 1987; not a re-parse). OUR-INVENTION: the discrete state register + the exact question templates (sweep). Mark PINNED vs OUR-INVENTION.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** the copular producer is landed + witnessed (read-back recall 0.672 CI-sep over the most-recent-noun floor 0.503, shuffle twin loses; `state_at('ahab')=['captain']` round-trips); the base reader scores **0/376** on predicate complements live; `bind_entity_states` turn-on cost **+5ms/read** (measured, post the DG-projection cache). (Sources: the copular SOLVED.md; `exp_copular_is_a_binding_readout_v1`.)
- **INFERRED (you must measure):** whether the state QA dimension scores a live `qa_state` CI-separated over the 0.503 floor with the shuffle twin LOSING, lifts `qa_aggregate` non-negatively, with NO other-dimension regression → `bind_entity_states` net-positive on a consumed metric → turned ON. The residual (surface-token keying cap) + its named cause.

## THE WIRE (researched spec — a clean, experiments-only change; auto board pickup)
All in `experiments/exp_situation_model_qa_v1.py` + auto-visible on `tools/baseline_board.py` (Instrument A iterates `res["per_dimension"]`, `baseline_board.py:99-110`):
1. **`build_state_questions(sm)`** (mirror `build_coref_questions` `:517` / `build_temporal_questions` `:576`): for each `EntityState` in `sm.entity_states`, emit "What is `{holder}` ?" (gold=`property`) + yes/no "Is `{holder}` a `{property}` ?". Transparent-derivation gold (the copular predication itself), same honesty bar as the temporal/causal dims.
2. **`SituationQA._answer_state(q)`**: answer OFF THE MODEL — `sm.state_register.state_at(holder)` (`state_register.py:399`) / `is_in_state(holder,val,semantic=True)` (`:363`, ATL WordNet synonymy/entailment via `state_match`). NEVER re-read text (same discipline as the other readouts).
3. **Router + dim:** add "state" to `DIMENSIONS` (`:135`), a copular "what/who is `<entity>`" / "is X a Y" frame → the state dim (wh-ontology `:292` + a cue in `CUE_DIM` `:139`).
4. **Flip `bind_entity_states=True`** in `build_reader` (`:490`) so the instrument's reader populates the register.

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a live `qa_state` per-dimension row on the baseline board (Instrument A) that scores CI-separated over the copular problem's validated **most-recent-noun floor (0.503)** with a **shuffle twin LOSING** (reuse the copular SOLVED's floor/twin so the row carries a CI — do NOT invent a degenerate gold), AND a non-negative move on `qa_aggregate` (today 0.36), AND `bind_entity_states` turned ON (default-on) since it is now net-positive on a consumed metric. Report CI half-width + null p95. Expected `qa_state` ≈ 0.67 within-clause vs floor 0.50. A rigorous located NEGATIVE — the register read-out does NOT beat the floor live (e.g. surface-token holder keying breaks it) — is a FULL PASS with the named cause. Also run the reader-QA before/after to confirm no other-dimension regression.

## ALREADY TRIED / DO NOT REDO / HONEST BOUNDS
- The producer `bind_entity_states` + `state_register` are LANDED + witnessed — do NOT re-derive; you CONSUME them.
- ⚠️ **Landed-wire limitation (decisive): holders/properties are SURFACE tokens at the sentence level, not canonical coref entities** (`situation_reader.py:1558`), so CROSS-sentence "what is Ahab (later 'he')" does NOT round-trip — lead with the WITHIN-clause metric; cross-sentence canonical-entity binding is a SEPARATE filed follow-on.
- ⚠️ The `ident` (identity/equative) htype is recorded but routed NOWHERE — this problem uses `pred_nom`/`pred_adj` (predicational) for the state read-out; identity→coref merge is a SEPARATE filed follow-on.
- Do NOT wire coref-identity-merge or fact-store is-a inheritance here (separate, bigger, filed).

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: `python tools/substrate_map.py`; read `hdlab/copular_binding.py`, `hdlab/state_register.py` (`state_at`/`is_in_state`/`state_match`), `hdlab/situation_reader.py::_read_entity_states` (`:1525-1563`), `experiments/exp_situation_model_qa_v1.py` (`:135,:224-228,:354-463,:490-505,:517,:576`), `tools/baseline_board.py:89-111`; read the copular problem's SOLVED.md for the validated most-recent-noun floor (0.503) + shuffle twin.
- Reproduce first-hand: the base reader's 0/376 on copular predicate complements (the can-fail live zero the wire must beat).

## FILES AND ENTRY POINTS
Build in `experiments/` (`exp_situation_model_qa_v1.py` + a witness under `verification/`); the board auto-picks up the new `per_dimension` row. REUSE the landed copular producer (`bind_entity_states`, `hdlab/state_register.py`) + the copular SOLVED's floor/twin. NO `hdlab/` change (the producer already landed). Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote the cross-sentence "what is X" number as the live capability — the landed wire keys on surface tokens (within-clause only).
- Do NOT use a degenerate/circular gold — reuse the validated most-recent-noun floor + shuffle twin so the row carries a real CI.
