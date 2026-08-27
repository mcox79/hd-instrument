# CONSOLIDATION PHASE -- EXECUTION PLAN (the debt-drawdown + end-to-end measurement)

**created: 2026-08-27 by the strategy session** · **STATUS: ARMED, NOT STARTED** · living skeleton.
**Trigger:** the three in-flight problems integrate (`discrete_where_the_brain_is_graded_in_parsing_and_role_assignment` p1,
`wire_entity_tracking_end_to_end_on_running_narrative` p2, `the_reader_has_no_conceptual_meaning_channel` p3). Greenlit by
the owner ("we need the consolidation phase for sure"); WHEN + policy recorded in `STATUS.md` (2026-08-27 LATEST POSITION).
**PROGRESS: p2 (entity-end-to-end) INTEGRATED 2026-08-27 (EXCELLENT) -> its entity-line landing spec is now FINAL (rows
E/F below). Awaiting p1 + p3 owner_verdict: DONE (both SUBMITTED, not yet owner-finalized).**

> **WHY THIS DOC EXISTS:** a multi-organ consolidation improvised across 30-min heartbeats is how landings get mis-ordered
> or double-done, and how a queued fix gets forgotten. This is the ordered plan to execute against when the trigger fires --
> NOT a frozen commitment. **The three in-flight problems REFINE the exact organs the consolidation composes (parser+role
> assigner / entity / meaning), so the specifics below are re-derived from each SOLVED at landing time. The SKELETON
> (ordered sequence + composition topology + measurement design) is stable; the per-organ details are not.**
> **Do NOT duplicate what `tools/substrate_map.py` or `STATUS.md` already derives -- this file is the sequence + topology +
> measurement design only.**

---

## 0. DISCIPLINE FOR EVERY LANDING (non-negotiable, per Q111 + WIRE-DON'T-ISLAND)

1. Re-read the source problem's FULL `SOLVED.md` FRESH (owner often added work); re-verify scaffold-free FIRST-HAND.
2. Confirm the hdlab target file + integration point ON DISK before writing (the disk outranks this plan's file names).
3. Land DEFAULT-OFF behind a flag if behaviour changes; byte-exact no-op when the flag is off.
4. Witness REQUIRED (`verification/test_*_organ.py`): a self-contained construction proof, info-free twin LOSING.
5. Register in `data/capability_registry.jsonl` (utf-8, `newline=''`); commit after each landing (NO push).
6. NO number crosses scorers/populations; recompute every floor on the item's own population.

---

## 1. THE ORDERED LANDING SEQUENCE (dependency-sequenced, not cost-sequenced)

Each proven fix is currently a default-off ISLAND. Order is by WHAT each interacts with -- land a fix only after the
in-flight problem that refines it has integrated, so we land FINAL form once (no double-landing).

| # | proven fix (source SOLVED) | hdlab target (verify on disk) | gated behind | status |
|---|---|---|---|---|
| A | forward-prediction organ (`the_reader_is_feed_forward...`) | `hdlab/predictive_reader.py` | -- | ✅ **LANDED** `predictive_reader_v1` |
| B | semantic-control gate (`context_override...`) | `hdlab/semantic_control.py` | -- | ✅ **LANDED** `semantic_control_v1` |
| C | incremental left-corner builder (`the_argument_parser_is_batch...`) | new organ, candidate source; role assigner unchanged; prediction ON / revision OFF; route to relcl | **p1 discrete-graded** | QUEUED |
| D | front-end role-assignment fix (`the_live_front_end_mislabels...`) | `situation_reader`/`thematic_role_labeler`: quote-exclusion in mention-pick + speech-verb graded cue + perceptron over selected core mentions; **NO thematic-fit** | **p1 discrete-graded** | QUEUED |
| E | ACT-R salience binder + **GRADED write** (`entity_binding...` + `wire_entity_tracking...`) | drop-in ACT-R base-level activation for the pronoun-branch `salience()`; **write the pronoun's event into the register by softmax(activation/temp), temp swept ~2.0 -- NOT hard argmax (divisive-normalization interior optimum, +0.0268 CI-sep; uniform hedging HURTS)**; no settling for the pick | **p2 ✅ INTEGRATED 08-27 (spec final)** | QUEUED |
| F | entity-augment of the situation model (`the_situation_model_tracks_words_not_entities`) | augment the forward predictor's top-down context w/ the active entity's role-conditioned state; **AUGMENT not replace**; bind by salience not content. **NB (p2 measured): wire the composed entity readout for RETRIEVAL ("what did X do"), NOT as a predictive prior on running narrative (entity-augment of the next-object predictor HURTS -0.219, even under oracle linking)** | **p2 ✅ INTEGRATED 08-27 (spec final)** | QUEUED |
| E2 | **sparse per-entity trace store** (`wire_entity_tracking...`, fan effect MEASURED 0.695->0.608) | DG-style k-WTA (~1-5%) conjunctive encode at each event + CA3 attractor completion -- **NOT a pointer** (a pointer fixes cross-entity lookup, not within-register superposition crosstalk); keep the bundle as a gist. Shared lever with the dense->sparse consolidation deviation | **p2 (store-design/consolidation target)** | BUILD PROPOSAL (not a landed fix) |
| G | reordered-access meaning read (`context_override...`) | default-off per-sense read = frequency prior + structured-context log-likelihood; routed by organ B; **NO settling / grounding-for-selection / diagnosticity** | **p3 conceptual-meaning** | QUEUED |
| H | relcl filler-gap resolver + route-conflict (`the_relcl_parser...`) | specialised resolver + two always-on competing scorers + a conflict term (NOT if/else) | folds into C/D front-end | QUEUED (gated on a live number) |

**Retrieval-first memory read (folds under the composition, from `content_addressable_retrieval...` +
`resolve_retrieval_interference...`):** `AdditiveCueRetrieval` is already feature-agnostic -- content-addressable additive
(Lewis-Vasishth) read over the live register + CONTEXT REINSTATEMENT (one added context feature, GRADED not `sign()`) +
the recollection gate. A USAGE, not a new organ; wire as the reader's partial-cue memory read.

---

## 2. THE COMPOSITION TOPOLOGY (the end-to-end brain-faithful reader)

The wire-and-measure DECISIVE result: organs work on CLEAN inputs, fail through the LIVE front-end. So the composition is
front-end-first, then the validated downstream organs, as a late algebraic MERGE (Norris "Merge"), not a feedforward
cascade:

```
text
  -> FRONT-END: incremental left-corner builder (C) --candidates--> role assigner (D: word-order + quote-excl + speech-verb)
                 |__ relcl filler-gap (H) on reversible/underdetermined cases (route-conflict, not if/else)
  -> ENTITY: ACT-R salience binder (E) -> coref threads -> entity-augmented situation model (F, AUGMENT the gist)
  -> PREDICT: forward-prediction reader (A) -> -log P surprisal as shared difficulty signal
  -> MEMORY READ: content-addressable additive retrieval + context reinstatement (partial-cue; the retrieval convergence)
  -> MEANING: reordered-access per-sense read (G) <-ROUTED BY-> semantic-control gate (B: suppress the prior on conflict)
  -> MERGE: N400 coherence monitor -> comprehension answer
```

**One shared surprisal signal** (from A) feeds the relcl route-conflict, write-gating, and N400 confidence -- do not
recompute it three ways. **Front-end is the binding constraint** (proven) -- if the composed number does not move, the
attribution test says it is still the front-end, not the downstream organs.

---

## 3. THE MEASUREMENT DESIGN (the payoff number the McGuffey gold cannot give)

**The instrument gap:** the McGuffey entity-role gold is AGENT-SATURATED (majority-role floor ~0.78 = "always say agent"),
so a real role/comprehension win is invisible on plain accuracy -- every clean win this program found showed up only on a
ROLE-BALANCED metric or on modern QA-SRL. **So the consolidation must BUILD a role-balanced comprehension gold first**
(the one measurement task that is genuinely blocked-on-nothing but DEFERRED here because the 3 in-flight define what it
must score -- entity-linking columns from p2, graded role targets from p1, meaning-identity items from p3).

- **Protocol:** organs OFF vs ON, IDENTICAL inputs (reuse the `test_wire_organs_endtoend.py` harness pattern).
- **Floors, recomputed on the gold's OWN population:** majority-role; string-identity entity linking; exact-key retrieval;
  MFS meaning default; positional role baseline. The BAR = CI-separated over the strongest floor's UPPER bound.
- **Info-free twins that MUST LOSE:** shuffled salience (E), wrong-entity history (F), shuffled-context (retrieval),
  shuffled conflict-trigger (B). Any twin that does not lose = the gain is not the real mechanism.
- **Report CI half-width + null p95 beside every margin.** A width is not an effect. NO number crosses populations.
- **Attribution:** ablate each organ back to its floor to localise where the end-to-end gain (or non-gain) comes from.

**DECISIVE EITHER WAY:** the composed reader beats the floors CI-separated -> the accumulated brain-faithful modifications
earn a live comprehension capability (the program's payoff). It does NOT -> a rigorous, well-attributed negative that
localises the residual binding constraint (front-end again? representation-quality/grounded-space coupling? the meaning
content-supply?) -- which is itself a full PASS and names the next lever.

---

## 4. WHAT THIS PLAN DELIBERATELY DOES NOT DO

- Does NOT package new organ-problems (the queue drains INTO this phase -- STATUS consolidation policy).
- Does NOT land C-H before their gating in-flight problem integrates (avoids landing against a moving target).
- Does NOT wire settling (== argmax, a tautology), grounding-for-selection, or diagnosticity-weighting (all refuted).
- Does NOT raise `GROUNDED_CAP` (the meaning channel is MISSING, not mis-tuned) or chase FHRR replacement (FHRR CONFIRMED
  faithful -- SEM/Franklin 2020; the lever is STORE ORGANIZATION, not the binding algebra).
