# Full-chain brain-fidelity scan: text -> reasoners (2026-09-07)

Owner directive: scan the whole relation-extraction->reasoning chain for 100% brain-foundational fidelity; find
updates/upgrades + efficiencies. Owner principle applied throughout: **a brain-foundational component that
under-performs is usually starved by a NON-brain-foundational dependency UPSTREAM -- trace the failure, don't polish
the component.** Method: 3 parallel read-only scans (fresh context each) over segments; runtime-verified wiring; a
real bug found + fixed. NO hdlab written (Q111). This is the SOLVER's proposal; strategy lands.

## THE CONVERGENT ROOT CAUSE (the principle, applied)
Every under-performing brain-foundational component traces to the SAME small set of non-brain-foundational upstream
dependencies:

| symptom (a brain-faithful component under-performing) | traced UPSTREAM to (the non-brain-foundational dependency) |
|---|---|
| causal generative typer covers only ~4.5% of edges | types on `event_type` MOST-FREQUENT-SENSE (meaning-BLIND) + a TOY 21-verb force lexicon; the brain disambiguates in context (ATL hub + control) and holds a VAST experiential causal store |
| spatial Figure-Ground typer leaves 22.8% attachment misses | the parse produces an exact brain-faithful per-arc confidence MARGINAL that NOTHING consumes for attachment (the OBL/spatial marginal consumer is dormant); construction inventory is HAND-CODED not learned |
| the 3 reasoners are at-fidelity but move no board dim | extraction-capped -> the front-end reads MEANING-BLIND -> and each reasoner is an ISLAND with no live consumer |
| event detection misses ~43% of causal triggers (57.3% detectable) | the eventive-NOM channel is OFF; no light-verb detection -- nominalized events are invisible |
| role binding path/location/source capped | PP-attachment ceiling = the BATCH greedy parse (not incremental/predictive), and it reads GREEDY heads where an exact-MAP decode is measured to help |

**The single dominant root: the MEANING CHANNEL is fully built + switched on but NEVER CONSUMED inside `read()`** (it
is a set of QA hooks). So the whole front-end reads meaning-blind -- which the brain never does. That one gap caps
causal typing, role tiebreak, and the edges feeding all three reasoners. Five separately-proven meaning gains
(curated +0.076, rare-sense +0.065, ATL-precision +0.023, clean-foundation +0.067, shared-core +0.169) all wait on
this one read()-time integration. Secondary roots: a TOY causal-knowledge lexicon; the unconsumed exact-parse
marginal; two duplicate parse front-ends (live GREEDY vs experiment EXACT-MAP).

## PER-SEGMENT FIDELITY (verified on disk)
- **Tokenizer** (spatial path): crude regex; abbreviation-blind + LOSSY (drops `$ % & / @`, currency, number-units). Fidelity LOW-but-cheap. Not filed.
- **POS tagger**: error-driven averaged perceptron = brain-COMPATIBLE (a generative "more brain-foundational" tagger was proven to REGRESS -- do not swap). Near its surface ceiling. Win = EFFICIENCY (vectorize emission + memoize). MEDIUM.
- **Arc/graded parser**: greedy arc-eager LIVE; exact-MAP + single-root Matrix-Tree marginals LANDED (owner-DONE) but `decode="exact"` default-OFF and the marginal has NO obl/spatial consumer. The marginal IS the brain-faithful ranked-parallel posterior. Incremental/predictive parser is the deeper fidelity target (left-corner owner-DONE, queued). MEDIUM (batch, not incremental).
- **Event detection** (`joint_event_ranks`): neo-Davidsonian, tense-agnostic + copular; brain-foundational. Gap: NOM channel off (57.3% detectable ceiling); no graded event-hood (a proven +0.08 gate exists uncomposed). HIGH mechanism.
- **Spatial typer**: Talmy/Herskovits semantic typing; brain-foundational MECHANISM, wins precision +0.386 over density. Gaps: LATENT (no live consumer -- the live SPACE dim is a different organ, `location_register`); construction inventory HAND-CODED not learned; uses greedy not exact-MAP. HIGH mech / MEDIUM acquisition + LATENT.
- **Causal typer**: generative world-model typing (recency prior + physics/psychology/affect) = the brain's Graesser-Singer-Trabasso mechanism; ISLAND. Recovers UNMARKED edges connectives can't (0.055) + beats connective on recall (+0.040 CI-sep). HIGH-precision/LOW-recall (~4.5%): coverage capped by CLASS-level engines. **BUG FOUND + FIXED** (below).
- **Role binding** (`predicate_argument_frontend`): Competition-Model cue integration + exact-marginal ranker; the MOST brain-faithful + LIVE. Cap = PP-attachment (the batch parse). HIGH.
- **Coref**: PINNED graded ACT-R softmax pick, LIVE (+0.133). The entity-maintenance LOOP is owner-DONE (+0.057 held-out) but NOT wired to hdlab; missing the Kehler-Rohde coherence prior (~19% residual). HIGH mechanism / wire pending.
- **Meaning channel**: hub-and-spoke assets present + callables return signal, but LATENT (see root cause). The keystone.
- **Reasoners** (spatial/causal/temporal): computations at-fidelity, byte-faithful, glass-box. Islands; extraction-capped. HIGH.

## BUG FOUND + FIXED (my own causal cell; verified at runtime)
`exp_joint_causal_survival_v1._val` double-centered valence: `_warriner`/`valence` already return [-1,+1] (0=neutral),
and I subtracted 5.0 again -> every word mapped ~[-6,-4] (always negative) -> the affect-congruence leg fired on ALL
pairs (a spurious constant 0.4 floor). FIXED (use `AffectLexicon.valence` directly). Corrected numbers: generative
recall 0.051 -> 0.045; balanced precision 0.496 -> 0.478. HONESTY CORRECTION (agent-caught): the balanced precision
~0.48 is ~CHANCE -- it reflects the generative typer ABSTAINING on negatives (not strong cause/non-cause
discrimination) vs the contiguity flood over-linking. The honest claim is HIGH-precision/LOW-recall (coverage ~4.5%),
recovering unmarked edges. Witness re-run 11/11 with corrected numbers.

## RANKED UPGRADE BACKLOG (leverage x buildability; F=fidelity, E=efficiency)
1. **[F, KEYSTONE] Wire the meaning channel into `read()`** -- call `select_sense` on ambiguous content heads, feed committed senses into causal typing (`event_type`), role tiebreak, and bridging. Cashes 5 proven gains; unblocks the causal content-sensitive rollout. In flight (word-sense problem). *The root fix.*
2. **[F+E] Consolidate on ONE exact-MAP parse shared across event/spatial/causal/role** + turn the eventive-NOM channel ON. Removes duplicate greedy/exact front-ends, upgrades the LIVE path to exact-MAP (+0.072 spatial, +0.027 role PP-roles measured), lifts the 57.3% detection ceiling. All pieces built; wiring + a flag.
3. **[F, my component] Broaden the causal typer's knowledge (CSKG static asset) + patient-tendency, over the recency prior** -- the upstream-fix for the ~4.5% coverage cap (toy lexicon -> broad experiential store; the brain-foundational answer per the principle). Depends partly on the meaning channel for content-sensitivity.
4. **[F, my component] Learned spatial construction inventory** -- replace ~6 hand-coded lists (`_PLACEISH`/`_REGION_PART`/`_DEICTIC_GROUND`/...) with ONE offline-mined, WordNet-hypernym-conditioned construction map (usage-based grammar, offline-counted = no training run, brain-admissible). Attacks the diminishing per-rule trap; promote+wire the latent spatial typer.
5. **[F] Wire the entity-maintenance loop + Kehler-Rohde coherence prior into live coref** (owner-DONE, +0.057).
6. **[F] Wire the N400 coherence monitor as the situation-model write/segment gate** + re-query the episodic store on partial cues (built organs, islands).
7. **[E] Vectorize + per-document-memoize the POS-tagger emission** (mirror the arc-parser scatter-gather); byte-identical.
8. **[F] Flip `decode="exact"` on** after the 8-consumer no-regress check (removes 7.2% invalid-tree parses).
9. **[F] Wire the reasoners to live consumers** (causal->goal-why/ToM; temporal->timeline) + board arms.

## WHAT I AM PROTOTYPING NEXT (both next-steps, threaded through the root cause)
- **CAUSAL upstream-fix (proof of the principle):** add the broad causal-knowledge asset (CSKG) to the generative typer and measure whether coverage rises from ~4.5% toward the ~17% CSKG bound -> proves the cap was the toy-lexicon dependency, not the typer.
- **SPATIAL upstream-fix (proof of the principle):** wire the exact-parse marginal into attachment (the dormant OBL consumer) and measure whether the 22.8% attachment misses shrink -> proves the cap was the unconsumed brain-faithful parse signal.
- **SPATIAL acquisition:** prototype the offline-mined learned construction inventory (item 4).
Each: implement -> can-fail test with the density floor + twin -> keep only if net-positive on the BINDING (precision) axis.
