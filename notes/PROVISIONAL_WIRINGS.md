# PROVISIONAL WIRINGS — everything in the live reader that is TEMPORARY / non-final, and what its final state is

Companion to `notes/INTEGRATION_LEDGER.md` (claimed-vs-realized gains). This is the "held together with tape" view: every component wired as a **scoped workaround**, **default-off hold**, **latent landing**, **provisional gold**, or **lossy coupling** — with why it's provisional, what FINAL looks like, and what it waits on. Disk-verified 2026-09-05. Many of these are exactly what the top-down pass RESOLVES (marked ⟶PASS).

Legend: `SCOPED` live-but-restricted · `OFF` landed default-off with a measured reason · `LATENT` in hdlab, no live consumer · `GOLD` measurement-not-final · `COUPLING` lossy/partial live wire.

---

## 1. SCOPED WORKAROUNDS (live, deliberately restricted to avoid a known regression)

- **`_read_causation` SCOPES `predicate_recall` OFF for causal** (`situation_reader.py:1843-1851`). `predicate_recall` is default-ON everywhere else, but `_read_causation` disables it over its own event extraction because the extra recovered events add distractor causes that mis-pick the connective/bridge selection → causal regresses **−0.0594 CI-sep** if unscoped. The comment states it plainly: *"scoping is the measured interim; the faithful fix (force-dynamic attribution) is the filed meaning-hub successor."* **FINAL:** the connective causal path is density-robust so it doesn't need to scope recall off. **Waits on:** the force-dynamic/meaning-hub causal scorer. **Partly addressed:** the causal mental-bridge landed 2026-09-05 (the mental half), but the connective-path scoping still stands. ⟶ a filed successor.
- **The connective causal QA gold IS the positional rule (circular for plausibility).** The board's causal arm is scored against a gold built from the connective-adjacent rule, so no plausibility mechanism can beat it (proven: a perfect-parse oracle loses). **FINAL:** a non-circular causal gold (the bridging dissociation / RC.GOLD). **Waits on:** a mined non-circular causal instrument. `GOLD`

## 2. DEFAULT-OFF HOLDS (landed, kept off with a measured reason)

- **`structural_do_recover=False`** (`:702`). Recovers who-did-what patients the front-end drops, but held off: recovery precision **0.385** on the ~76%-oblique-CONFOUNDED 19c gold + unmeasured downstream harm (feeding low-confidence patients asserts false facts). **FINAL:** on, once a clean 19c gold + an info-free random-recovery twin + a downstream-consumer regression check exist. **Waits on:** a clean 19c gold + the CRF/predicate precision gate (Step 1). ⟶PASS-adjacent.
- **`causation_typed=False`** (`:679`) + **`causation_foreground_gate=False`** (`:683`). Opt-in TYPED within-clause causation (Talmy/Wolff force dynamics) — additive, never replaces `causal_links`; kept off (a spaCy-lineage/opt-in path). **FINAL:** the event-TYPE organ (landed `hdlab/event_type.py`) + the force-dynamic scorer supersede this. **Waits on:** the causal successor problem.
- **`sense_prior`/`prior_weight` (Bayesian rare-sense readout) in `diagnostic_context_wsd`** — landed default byte-identical (`prior_weight=0`), KEPT off because its only consumer (`consolidation_gate`) is itself off. **FINAL:** on, when a live meaning stage consumes it. **Waits on:** the meaning tier (Step 4). ⟶PASS.

## 3. LATENT LANDINGS (promoted to hdlab, ZERO live read()-time consumer) — the biggest block

Disk-verified importer counts (reader = refs in `situation_reader.py`):

| organ | hdlab importers | reader? | note |
|---|---|---|---|
| `meaning_foundation` | 0 | no | the curated foundation loader (+0.0755) |
| `composed_hub_predictor` | 0 | no | the who-did-what hub (AvgSim→MaxSim +0.065) |
| `grounded_semantic_graph` (`select_sense`) | 0 | no | **the meaning-wire's target** — the sense picker the curated-foundation beats +0.0633 on WiC |
| `crf_tagger` | 0 | no | the calibrated CRF POS posterior (+0.041 19c event recall); its consumer `predicate_detector` doesn't import it |
| `diagnostic_context_wsd` | 2 (both off/latent) | no | the WSD readout (gamma/topk + sense_prior stacked) |
| `consolidation_gate` | 2 (latent) | no | the offline admission guard (+0.067 clean-foundation lift latent) |
| `cls_growth` | 1 (consolidation_gate) | no | the reversible growth wrapper |
| `semantic_control` | 2 (conceptual_meaning/scalar_adjective) | no | the additive reordered read |

**This is one connected LATENT MEANING CLUSTER.** The reader has NO read()-time meaning stage, so every gain in it (foundation +0.0755, hub +0.065, precision +0.023, clean-foundation +0.067, rare-sense +0.065, the WiC +0.0633) is on the shelf. **FINAL:** a `reader_meaning_channel` read()-time stage (within-invariant half now) + the 0c WiC board arm to score it. **Waits on:** the meaning tier (Step 4) + the §2 owner decision for the deep-contextualization half. ⟶PASS (the single highest-leverage block).

Plus **opt-in publishers with no consumer:**
- **`arc_labeler.label_graded`** (landed 2026-09-05, default-off, **0 consumers**) — the graded label posterior + entropy (AUC 0.930). **FINAL:** consumed by the entity_states/who-did-what readout (graded, not hard 1-best). **Waits on:** `consume_the_graded_pos_posterior` (row 7). ⟶PASS.
- **`diagnostic_context_wsd` gamma/topk** — the P9 precision-weighting, default byte-identical, opt-in (but the organ is latent). Same fate as the cluster.

## 4. PROVISIONAL BOARD GOLDS (measurement in a non-final state — the ruler, not the reader)

- **Patient who-did-what: the LitBank object/patient gold is ~76%-oblique CONFOUNDED/INVALID.** The live +0.086 patient reads −0.006 against it. **FINAL:** the clean-UD patient arm (Step 0a, BUILT). ⟶PASS.
- **State (copular is-a): the LitBank gold is READER-DERIVED → COVERAGE-only** (`:701-704`); the non-circular capability number is on modern UD-EWT. **FINAL:** a ~200-clause hand-annotated 19c copular gold (filed). `GOLD`
- **Causal: connective-reducible** (`:725`) — a high score means it recovers the text's connective structure, not force-dynamic reasoning. See §1. `GOLD`
- **Temporal: the model timeline + the gold share the tense signal** (`:676-678`) — tests the QA CLAIM (route a before/after question), NOT independent temporal reasoning. `GOLD`
- **Goal-hierarchy: only ~4% of the live goal-why arm is multi-hop** → the graph organ scores 0.68→1.00 on the authored battery but registers nothing on the board. **FINAL:** the goal-hierarchy arm (Step 0b, BUILT). ⟶PASS.
- **Meaning: there is NO meaning/word-sense board dimension at all.** **FINAL:** the WiC/sense arm (Step 0c, BUILT). ⟶PASS.
- **Standing: the reader-EVAL corpus is 19c (McGuffey/LitBank) — a corpus-age confound** flagged ~10×. Modern annotated (UD-EWT/QA-SRL) is the fair test.

## 5. LOSSY / PARTIAL LIVE COUPLINGS

- **`referent_per_np` opens BLANK feature cards** (`_mk_referent`: gender=None, lowercased). Live + default-on, but the referents it creates lack the features a downstream consumer would use. **FINAL:** restore feature typing IF a feature-consuming downstream needs it. **Waits on:** measured need.
- **The +0.043 above-baseline coref bonus (overlay-by-discourse-entity) is NOT landed** — the `wire_the_referent_to_coref_linking_pass` submission left coref byte-identical at baseline; the bonus uses the coref column's provided clustering (an owner decision). **FINAL:** land it or record the reason. **Waits on:** an owner call (near-term). ⟶PASS-adjacent (coref tier).
- **The reader parses every sentence TWICE** (base arc-factored for the front-end + arc-eager for roles). Live, redundant. **FINAL:** one arc-eager parse for all consumers. **Waits on:** the in-flight `consolidate_the_arceager_and_arc_double_parse` (board-neutral, ~5% faster). ⟶PASS (parser tier).

## 6. FLIPPED-ON WITH A CAVEAT

- **`parser_arceager=True`** — flipped on 2026-09-04; the residual caveat was the per-register question (arc-eager is +modern/−19c). The double-parse consolidation peek shows the full board is ZERO-regression with arc-eager serving all consumers, so the caveat is effectively resolved (pending that submission landing). ⟶PASS.
- **`predicate_recall=True`** — flipped on scoped (see §1). The unscoped-causal regression is the caveat; scoping contains it.

---

## How the pass burns this down (the resolution map)
- **Step 0 (ruler)** resolves the patient/goal-hierarchy/meaning GOLD gaps (all 3 arms BUILT).
- **Parser tier** resolves the double-parse + the arc-eager per-register caveat (the consolidation submission).
- **Coref tier** resolves the entity-KB latent + surfaces the +0.043 coref-bonus decision.
- **Meaning tier (Step 4)** resolves the entire LATENT MEANING CLUSTER + `sense_prior`/gamma/`label_graded` opt-ins (via the read()-time stage + the 0c arm).
- **Causal successor** resolves the `_read_causation` scoping + the circular causal gold + `causation_typed`.
- **Structural-DO** resolves once the clean 19c gold + CRF precision gate exist (Step 1-adjacent).

**Not resolved by the pass (need their own work / owner call):** the 19c corpus-age confound (use modern golds), the non-circular causal/temporal golds, the 19c copular gold, the §2 deep-contextualization half of the meaning channel.
