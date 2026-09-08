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

## PROTOTYPE RESULTS -- the "do all" pass (each a proof/refutation of the upstream principle; verified on disk)
All measured with the fair-test controls (density floor + shuffled twin + the honest metrics). NO hdlab written.

| upgrade prototyped | result | brain-foundational reading |
|---|---|---|
| **Detection ceiling: turn eventive-NOMINAL on** (`exp_joint_event_detection_ceiling_v1`) | **WIN** | causal-edge BOTH-detectable 0.607 -> **0.850** (+0.243); trigger recall 0.753 -> 0.921. Nominalizations ARE events (neo-Davidsonian); the category gate was the upstream cap on causal recall. |
| **Causal CSKG broadening** (`exp_joint_causal_cskg_v1`) | **REFUTED** | CSKG covers 2.16% of MAVEN causal edges (63.4% have both lemmas in vocab, not the edge = EDGE gap). Retrieval is coverage-bounded BY CONSTRUCTION; a bigger generic KG is the wrong upstream fix -- the brain SIMULATES, it does not retrieve. |
| **Causal content-sensitive SIMULATOR** (`exp_joint_causal_simulate_v1`) | **RIGHT MECHANISM, HARD-FAIL strict gate, coref-capped** | `compute_causal_link` (world_state + possession + VerbNet endstate[62 cls/1189 verbs, 0 tuning] + goal + affect + patient_tendency/force-dynamics). Precision-on-fired (fair, between-gold-events): connective 0.758 > contiguity 0.568 > **simulate 0.465** > generative 0.363 > twin 0.232. Beats twin CI-sep + class-generative on point estimate (content-sensitivity helps), but simulate-generative +0.102 CI[-0.013,0.207] NOT CI-sep, loses to the recency/contiguity prior. Fires only 86 edges/710 docs -- **coref-capped: only 6.5% of literal gold pairs surface-match**; 93.5% need coref ("the fort"<->"it") to bind A's patient to B's participant. |
| **Spatial marginal-attachment** (`exp_joint_spatial_frontend_upstream_v1`, Proto A) | **REFUTED** | the exact-MAP parse is already ~99.9% confident on these attachments (median reliability 0.999); the 22.8% "both-extracted-not-linked" misses are NOT attachment-uncertainty, so consuming the marginal is a no-op on held-out. |
| **Spatial learned construction inventory** (`exp_spatial_construction_mining_v1`, Proto B) | **WIN** | offline-mined WordNet-hypernym-conditioned containment-affinity table (UD-EWT, pure counting, no training run); statistically EQUAL to the hand-lists on the binding precision axis (CI incl 0) + slightly better held-out recall + GENERALIZES (coerces unseen containers cathedral/province, rejects unseen surfaces shelf/ledge). Usage-based construction grammar replaces enumeration -- the acquisition-fidelity upgrade. |

## METRIC RECONCILIATION (two agents, two denominators -- settled)
`precision-on-fired` = |fired  INT  gold| / |fired|. The FAIR denominator is **edges between two ANNOTATED (gold) events** (you cannot grade a pair where one event is unannotated -- MAVEN's annotation is incomplete). Under it: connective 0.758, contiguity 0.568, generative 0.363, simulate 0.465, twin 0.232. The earlier 0.104/0.186/0.235 used the all-fired denominator (counts edges touching unannotated events as wrong) -- superseded. The balanced hard-negative QA (witness C2, contig 0.139) is a THIRD lens (precision-sensitive but abstention-dominated for low-fire arms). All three agree qualitatively: contiguity/recency is a STRONG brain-foundational baseline; class-generative is coverage-bound; the simulator improves precision over class-level but is coref-capped on recall.

## THE CONVERGENCE (the principle held to the root)
Every brain-foundational mechanism prototyped this pass under-performs for the SAME upstream reason, now QUANTIFIED:
- **Causal simulator** (sound mechanism, beats twin + class-generative on point estimate) fires on only **6.5%** of gold pairs because it needs the shared participant named identically -- **participant COREFERENCE** is the cap.
- **Spatial typer** "both-extracted-not-linked" misses (65.6% wrong-ground + 34.4% unbound) trace to binding locatives to the SYNTACTIC head not the THEMATIC event, and to the absence of a NESTED situation model -- the same entity/situation-tracking gap.

Both -> the **participant/entity COREFERENCE + GROUNDING channel (the meaning/entity model)**, exactly the root the full-chain scan named (meaning channel latent + entity-maintenance loop unwired). The reasoners and typers are brain-foundational; the one non-brain-foundational dependency the whole chain rests on is entity/coref/meaning -- and it is out of solver write-scope (strategy/coref+meaning-channel problems own it). No further extraction prototypes are worthwhile until it is wired; they all hit this wall.
