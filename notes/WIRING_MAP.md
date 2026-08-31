# WIRING MAP — the single living "what we built vs what is actually WIRED" burn-down

> **Why this exists (owner, 2026-08-30):** *"Are you actually wiring these in, or just farming out
> problems, getting solutions, and putting them on a shelf? … since you compact context periodically,
> there is a real risk that things get forgotten over time."* This is the compaction-proof answer +
> the focused-address plan. It supersedes the ARC-era `capability_integration_ledger.md` (2026-07-28)
> for the current reasoning-organ wave; that older ledger recorded the SAME concern
> (*"we develop stuff and forget about it"*) — the fact that it keeps being re-discovered IS the risk.
>
> **ROT-PROOF:** regenerate the numbers any time with **`python tools/wiring_debt.py`** (`--full` for
> every item). It derives from `notes/problems/*/SOLVED.md`, `data/capability_registry.jsonl`, and the
> live reader's imports — so this map cannot silently go stale. The registry is the machine source of
> truth for per-organ status.

---

## THE HONEST STATUS (derived 2026-08-30 — `python tools/wiring_debt.py`)

- `hdlab/` holds **182 modules**; the **live reader + substrate import only 19** of them (re-derived
  2026-08-31: arc_parser, context_grounded_valence, coref, corpus_registry, definitional_extraction,
  event_bundle, event_centrality_coref, frame_induction, gap_detector, hd_fact_store, hippocampal_encoder,
  information_foraging, pos_tagger, predicate_argument_frontend, reading_grounding_loop, scene_segment,
  situation_focus, substrate, thematic_role_labeler).
- **90 integrated submissions:** 24 landed, **27 QUEUED** (earned a landing, not confirmed live),
  18 correct-no-landing (rigorous negatives), 21 unclear.
- **Registry: 241 capabilities.** 190 tagged `WIRED` — but that tag means *promoted+registered*, not
  *called at inference*. Strict test: **10 reach the live reader/substrate; 116 are island-only**
  (used only by their own experiments/witnesses). Plus 24 explicit `ISLAND`, 25 `TRAPPED_SHARED`, 2 shelved.
- **2026-08-31 note:** the recent conceptual→`meaning_fusion` landing (DEBT 3, island-to-island) and the
  `tense_agnostic_events` detector (uses the already-imported `pos_tagger`) correctly did NOT change the
  live-reader import count — honest bookkeeping (a within-organ composition / a flagged behavior addition,
  not a new live import). The live-reader count moves only when a dimension is wired into `situation_reader`
  itself (the assembly, DEBT 2) — still the real completion.

**Plain reading:** the *bookkeeping* is durable — organs are promoted, witnessed, registered, and NOT
lost. But "integrate" has been stopping short of "wire into the live reader," so the live substrate is
thin (~19 organs) while ~100 validated organs sit as default-off islands. **That is the debt this map
burns down.**

---

## THE THREE DEBTS (this is the real structure, reconciled against `hdlab/` on disk)

### DEBT 1 — PROMOTION debt (code still only in `experiments/`, never promoted to `hdlab/`)
Cleanest to clear: promote the spaCy-free core `experiments/X.py` → `hdlab/X.py`, default-off, add an
organ witness, register. Each is a self-contained strategy landing (Q111).

| Organ | Source | Wire-step | Note |
|---|---|---|---|
| ~~belief_timeline~~ ✅ **PROMOTED 2026-08-30** | `hdlab/belief_timeline.py` | DONE (default-off organ; witness `test_belief_timeline_organ.py` 11/11; exp file now a re-export shim). **Live-reader wiring still pending** (moves to DEBT 2 / the assembly) | first burn-down |
| ~~state_register~~ ✅ **PROMOTED 2026-08-30** | `hdlab/state_register.py` | DONE (surgical core-only split; witness `test_state_register_organ.py` 14/14; 61/61 unregressed; extraction stays exp-side). **Live-reader wiring pending** (DEBT 2, ENTITIES coref re-rank) | second burn-down |
| **temporal_order_register** ⚠️ DEDICATED EFFORT | `experiments/_temporal_order_register.py` | NOT a single-file promotion (verified 2026-08-30): a 4-module chain — `_temporal_order_register` → `_temporal_ordering` (+ an ORC `pos_tag_sentence` tagger) + `_temporal_ordering_multiframe` → which pulls `_tagger` from **another cell** (`exp_oracle_mention_upperbound_reader_v1`). Untangle the tagger first — but NOT by swapping in `hdlab/pos_tagger.py` (verified 2026-08-30: it emits UPOS via our-own perceptron and is deliberately nltk-free, whereas the temporal extraction rules are written against NLTK Penn-treebank tags — different tag sets, not a drop-in). **Clean path = DEPENDENCY-INJECTION:** give the register + shared modules a `tagger` parameter (default supplied by the caller), keep the NLTK PerceptronTagger experiment-side so hdlab stays nltk-free; then promote the 3 modules + shims. | TIME dimension; ~25 importers — **do NOT rush in a heartbeat** |
| ~~perceptual_access_ledger~~ ✅ **PROMOTED 2026-08-30** | `hdlab/perceptual_access_ledger.py` | DONE (wholesale; spaCy lazy = no hard hdlab dep; organ witness 5/5; 6/6 unregressed). **Live-reader wiring pending** (DEBT 2, GOALS/ToM — closes the belief-timeline 0.098 gap) | third burn-down |
| **CLS keep-both-stores growth** — ✅ **SAFETY PRIMITIVE PROMOTED 2026-08-31; the loop is the live-canary problem** | `hdlab/cls_growth.py` | The reversibility HEART is landed: `make_ensemble_sim` (keep-both fusion — never discards a defined channel) + `rollback_gate` (regression-checked, random-control-fails), VERBATIM ports, witness `test_cls_growth_safe_primitive_organ.py` PASS. Registered `cls_growth_safe_primitive_v1` (default-off ISLAND). ⚠️ NOT yet landed (deliberately, "land faithfully not improvise"): the reliability-WEIGHTED operating point + the continual anchor-preserving GROWTH LOOP + the live read-path wiring — those land WITH the packaged `run_the_learner_on_live_and_evaluate_the_full_safety_and_benefit_suite` problem, which drives the loop end-to-end and picks the operating point on LIVE evidence. STORE hazards apply to the loop. **Flipping growth ON live is a separate OWNER-gated step.** | learner-on roadmap step-2 |

**Status (2026-08-30):** the three CLEAN single-file promotions are DONE (belief_timeline, state_register, perceptual_access_ledger). The two remaining are DEDICATED efforts (above) — a future focused block, not a heartbeat cram.

### DEBT 2 — WIRING debt / THE ASSEMBLY (promoted to `hdlab/` default-off, but the live reader never calls them)
The **biggest lever and the hard part**: these all edit `situation_reader`'s role/read path, so they
must be wired as ONE coordinated, measured effort (dimension by dimension) — NOT piecemeal. The
who-did-what slice already landed (quotative inversion, Change 1) and PROVED the pattern (0.551→0.798).

🔑 **KEYSTONE — ✅ LANDED 2026-08-31 (p1 integrated, EXCELLENT): the tense-agnostic event detector is now wired into
the live reader behind a DEFAULT-OFF `tense_agnostic_events` flag** (event recall 0.33→0.95 end-to-end when on;
byte-identical off; witness `test_tense_agnostic_events_organ.py`). Every per-dimension wiring reads off the event
set — CAUSATION, SPACE, ROLE/ENTITIES all improve when detection is complete — so **the assembly should now be
sequenced with this flag ON, re-measuring each dimension at real recall.** ⚠️ Flag boundary: placeholder tense (the
TIME dimension needs a tense-preserving variant first). NEXT assembly step candidate: turn the flag on + re-measure the
already-landed dimensions (who-did-what Change 1) at real recall, then wire the next dimension. ⚠️ **Scope caveat on the queued causation landing:** promoting `_literalness_gate`
drags `frame_sense_disambiguator` + `idiom_gate` + **spaCy** — the landing must decouple these (the reader's native
roles are spaCy-free, per the p2 OWNER_NOTES) or gate them lazily; do NOT introduce a hard spaCy dep into the canonical
reader. This makes the causation landing a careful multi-file effort, not a one-round drop.

📌 **QUEUED EXTRACTION-FRONT-END EXTENSIONS (integrated 2026-08-31, Q111 — extend the keystone in `_tense_agnostic_extract`,
each additive default-off with its own equivalence witness; land p5 first [clean], then p3 [heavier]):**
- **p5 tense-preserving (STRONG) — CLEAN, land first.** Add a default-off `preserve_tense` sub-flag: when on, assign a
  COMPOSED Reichenbach tense/is_pp (`assign_sentence`+`_stock_tense`, `experiments/exp_tense_preserving_live_reader_and_timeline_v1.py`)
  instead of the placeholder `TENSE_SIMPLE_PAST`. `situation_reader` ALREADY imports `experiments._temporal_ordering as T` (the tense
  constants), so this is a small lazy-import landing. Recall preserved EXACTLY (byte-identical event set). UNBLOCKS the landed TIME
  dimension (`timeline_register`) consuming ONE is_pp-faithful event set. Do NOT change the existing `tense_agnostic_events` semantics
  (the keystone witnesses compare against its placeholder path) — a NEW sub-flag.
- **p3 copular/nominal (EXCELLENT) — HEAVIER, focused follow-on.** Add a default-off `copular_nominal_events` sub-flag firing a
  `state`-sort node on each `cop` predicate (needs a labeled parse → lazy front-end, like causation) + an `event`-sort node on
  CONFIDENT event-denoting nouns (bake the WordNet event lexicon to a STATIC JSON asset → no nltk at runtime) + a new
  `SituationModel.entity_states` field routed from the state nodes. Ref `experiments/_copular_nominal_events.py`.
- ~~**verb_subcat (from p2, EXCELLENT) — the who-did-what PRESENCE lever.**~~ ✅ **LANDED 2026-08-31 (ARCHITECT HEARTBEAT).**
  Promoted `experiments/ref_verb_subcat_organ_v1.py` → `hdlab/verb_subcat.py` (re-export shim left) + a default-off
  `verb_subcat_gate` on `SituationReader` (post-read pass: suppress a bound patient on low-transitivity verbs). VERIFIED:
  witness `test_verb_subcat_gate_landing_organ.py` PASS — default-off byte-identical (organ not imported), through read()
  events 219 held + patients 147→112 (35 spurious suppressed), and == the validated SubcatGateReader byte-for-byte. Static
  glass-box WordNet+corpus assets, NO LLM. Registered `verb_subcat_gate_live_reader_v1`. ⚠️ This wired the SIMPLE
  transitivity gate (the through-read()-validated version). **QUEUED REFINEMENT (DEBT 2): the stronger GRADED
  Competition-Model gate (`hdlab.verb_subcat.patient_present`, QA-SRL who-did-what 0.30→0.49, AUC 0.777) — the brain-faithful
  version — needs the reader to expose POS + the patient token index at role-assignment time (a mid-`_read_events` plumbing
  change); a focused follow-on, not a post-read pass. The organ already ships `patient_present` so the upgrade is reader-side
  plumbing, not a re-derivation.**

| Organ (in hdlab, default-off) | Wire target in the reader | Dimension |
|---|---|---|
| ~~`force_dynamics_typer` + `_foreground_eventhood`~~ ✅ **LANDED 2026-08-31 — THE FIRST ASSEMBLY DIMENSION WIRED INTO THE CANONICAL READER** | the reader now has a default-off `causation_typed` flag → `sm.typed_causal_links` (CAUSE/ENABLE/PREVENT + endstate) via `hdlab/causation_typing.py`. Promoted `force_dynamics_lexicon` + `patient_tendency` → hdlab; created `hdlab/causation_typing.py` (ports the validated typer + p3 graded event-hood gate). Default OFF = byte-identical (no spaCy/experiment import). VERIFIED byte-for-byte equivalent to the validated `WiredCausationReader` across 11 configs + witness `test_causation_typed_landing_organ.py` PASS → inherits p2's within-clause AUTO 0.833 and p3's open-text precision gate (`causation_foreground_gate=True` opt-in). The WSD/literalness chain (`frame_sense_disambiguator`/`idiom_gate`/`_literalness_gate`) stays in experiments/ (lazy, default-off) — its own separate queued promotion. Registered `causation_typed_live_reader_v1`. | CAUSATION ✅ |
| `graded_coref_pick` / graded retrieval + entropy-abstain | the coref resolution stream | ENTITIES(coref) |
| `location_register` ✅ **LANDED 2026-08-31 (the 4th assembly dimension wired into the live reader)** — default-off `track_space` flag → `sm.locations` (a LocationRegister; `where_is`/`present_in_scene`) via `experiments/_space_reader.read_locations_in_substrate(prior_ext)`, lazily imported, driven by the reader's OWN in-substrate parse (NO spaCy). Witness `test_track_space_landing_organ.py` PASS: default-off byte-identical (adapter not imported), flag-on `sm.locations.where_is` == the validated register byte-for-byte over all 1040 (entity,t) cells. Registered `track_space_live_reader_v1`. Ceiling = parser recall (→ prediction-error p2). | SPACE ✅ |
| ~~`temporal_order_register`~~ ✅ **LANDED 2026-08-31 (2nd assembly dimension)** | the reader now has a default-off `timeline_register` flag → `sm.timeline_order` (whole-passage chronological event order incl. flashbacks) via the register, lazily imported (not promoted — the ~25-importer promotion stays a separate nicety). Default-off byte-identical (register not imported; narrow `_read_timeline` untouched). Witness `test_timeline_register_landing_organ.py` PASS (flag-on == register's own output byte-for-byte; flashback reordered). Registered `timeline_register_live_reader_v1`. | TIME ✅ |
| `state_register` (once promoted) | ENTITIES(state) re-rank of the coref pool | ENTITIES(state) |
| `belief_partition` + `perceptual_access_ledger` | per-agent belief + observation gate | GOALS/ToM |
| the register readout lines (`decode_serial`/`decode_gated`/`divnorm`) | the who-did-what event-set decode | ENTITIES |
| `incremental_parser` | replace the batch arc-parse candidate source behind a flag | PARSE |
| the who-did-what mislabel fix (quote-exclusion + speech-verb + core-mention) | `situation_reader`/`thematic_role_labeler` | ROLE |

**These are the coupled reader-wiring items behind ~10 of the 25 QUEUED landings.** They are the
substance of "an ever more complete substrate": each one measurably grows what the live reader can do.

🔧 **ASSEMBLY SEQUENCE (2026-08-31, owner: keep landing dimensions) — after CAUSATION (done ✅), by readiness/dependency:**
Each dimension = a careful default-off landing on the causation PATTERN (promoted organ + lazy experiment-side extraction
adapter + a delegating call in `read()` + equivalence/byte-identical witness). Next-up, best-first:
1. ✅ **TIME dimension — LANDED 2026-08-31** (additive `sm.timeline_order` via the register, default-off, lazy import — did
   NOT require the risky ~25-importer promotion; the promotion stays a separate nicety). The 2nd assembly dimension live.
2. (superseded — TIME landed above via the lazy-import pattern, not the promote-first plan.)
3. **GOALS/ToM (belief timeline)** — ADDITIVE (`sm.belief_timeline`); promoted (belief_timeline/belief_partition/
   perceptual_access_ledger all in hdlab), live end-to-end validated (0.902 vs floor 0.463 CI-sep). Needs a WorldEvent +
   observation-cue extraction adapter (perceptual_access_ledger, spaCy-lazy) + the temporal register (1). Additive, low-risk.
4. **SPACE (location)** — ADDITIVE (`sm.locations`); `location_register` promoted; needs the motion-event parse adapter.
5. **ENTITIES(state)** — `state_register` promoted; wiring MODIFIES the coref path (state-consistency re-rank) → higher-risk,
   land AFTER the additive dimensions + with a coref no-regression witness. Also the ROLE precise_voice wire (from p1, queued).
The parser (p2, PARSE dimension) is SOLVED-awaiting-owner-review; it improves the adapters' quality when it lands.

### DEBT 3 — STANDALONE meaning/memory islands (promoted; the reader *could* consult them but doesn't)
Wire into the reader's meaning / entity read-out (some gated on the assembly landing first).

`scalar_adjective_operation` + `fractional_power_encoding` (the p1 magnitude channel; the scalar op is now an
optional inject into the routed read-out) · `convergent_cue_reader` (log-Bayes cue product) · `factorized_entity_store`
+ `graded_temporal_context` (the two-system store) · `n400_coherence_monitor` · `transitive_ordering`.

✅ **2026-08-30 (owner-directed): `conceptual_meaning` + `meaning_operation_router` are now COMPOSED INTO `meaning_fusion`**
(the designated general meaning read-out) as an OPT-IN, demand-routed identity channel, default-off — the reader's meaning
read-out now holds BOTH dissociable systems (associative/relatedness + ATL identity/similarity). Witness
`test_meaning_fusion_conceptual_routing.py` (identity win +0.2761 CI-sep on SimLex; routing not pooling). ⚠️ This advances
DEBT 3 (island→island composition) but NOT the assembly (DEBT 2): `meaning_fusion` itself is still not imported by
`situation_reader`/`substrate` — the live reader has NO word-meaning read-out yet; wiring the composed read-out into the
live reader is the remaining step.

### NON-DEBT — correct no-landing (rigorous negatives + capability-without-a-reader-home; DO NOT re-attempt)
Recorded so they are never re-packaged. Newest: `wire_the_incremental_parser_as_the_reader_extraction_front_end`
(p2, EXCELLENT — reverified 16/16; wiring the incremental parser as the reader's ROLE candidate source is a FIDELITY
ERROR: precision reproduces [+0.145 CI-sep] but role F1 does NOT improve, and restricting the binder to the parser's
bounded buffer LOWERS patient acc 0.726→0.696 [role-binding is a SEPARATE cue-based stream — Frankland & Greene 2015 /
Lewis & Vasishth 2005]; powered voice-sliced QA-SRL confirms; → keep `incremental_parser_v1` DEFAULT-OFF precision-only,
NO dead role-flag, registry note corrected. The submission's POSITIVE — `verb_subcat` — is QUEUED, not no-landing).
`retrieval_interference_is_similar_competitor_cue_overload_not_event_count`
(p6, STRONG — reframe CONFIRMED [interference is content×context, not event-count], but the right-axis organ
`graded_antecedent_pick` ALREADY EXISTS and BOTH candidate new cues are CI-separated NEGATIVES [multi-timescale TCM −0.001;
gender/number +0.003/+0.004 over the person cleanup] → NO landing; the residual is STRUCTURAL [72% of errors gold-present-
but-not-most-accessible; ~0.10 below the oracle-of-cues], a Centering/accessibility problem, NOT cue-overload). `narrative_causal_graph_missing_implicit_inference_organ` (p5, STRONG —
covariation causal typing works on held-out MAVEN-ERE with power + generalizes to unseen type-pairs, but needs OBSERVED
CONTINGENCY so it is a rigorous NEGATIVE on single-document narrative → **NO reader landing**; the organ's home is
CORPUS-level causal knowledge, the knowledge-store p4 / the learner, NOT the reader). `causation_is_typed_per_clause_not_across_the_causal_network`
(discourse causal-network typing = a dead real-text lever); `the_discourse_fact_reasoner…` (world
knowledge net-zero on competitive coref); `teach_the_self_built_space…` (teaching does not rescue
retrieval). Full list: `python tools/wiring_debt.py --full`.

---

## THE FOCUSED-ADDRESS PLAN (sequenced by leverage × risk)

1. **Verify what we have still WORKS** (the owner's "make sure all the work is incorporated and working
   properly"). Run the organ-witness sweep (`verification/test_*_organ.py`); any FAIL = bit-rot to fix
   first (precedent: the `floor_battery` filename collision silently broke ~7 cells). Do this before
   building on top.
2. **Clear DEBT 1 (promotion) — cheap, safe, high-count.** Promote the ~5 experiments-only cores to
   `hdlab/` default-off + witness + register. Shrinks the debt fast and makes the code durable. Start
   with belief_timeline (fresh, clean, standalone).
3. **Land DEBT 2 (the assembly) — the real completion.** Wire the promoted role/dimension organs into
   the live reader, ONE dimension at a time, each measured end-to-end vs the positional/counting floor
   (the who-did-what slice is the template). This is a coordinated build = the natural next big PROBLEM,
   not a piecemeal strategy edit. **Highest leverage for "a more complete substrate."**
4. **Wire DEBT 3 (standalone meaning/memory)** into the meaning/entity read-out as the assembly opens
   the read points.
5. **Learner-on step-2** (DEBT 1's CLS growth) lands default-off in parallel (verdict-independent).

**Standing rule going forward (anti-forget):** every integration's `INTEGRATED_BY_STRATEGY` block must
say the landing STATE in these terms (promoted? live-wired? or QUEUED-with-target), and any QUEUED item
lands in this map. Re-derive with `tools/wiring_debt.py` on the maintenance cadence; a new island is a
tracked burn-down item, not a silent park.

---

## BURN-DOWN LOG (newest first)
- **2026-08-31** — **🧠 INTEGRATED (EXCELLENT) the BELIEF dimension `the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose`; `track_belief` WIRE QUEUED (DEBT 2, precise target below).** Reverified 19/19. A refute-and-rebuild validated on FANToM (external, n=3572; reader 0.893 vs floor 0.665 +0.228 CI-sep, beats two twins, false-belief 0.939). 🔧 **QUEUED LANDING (the next assembly dimension, the lazy-adapter track_space pattern — NOT a clean single-file promotion because `experiments/_belief_reader.py` imports `experiments._space_reader` + `experiments.state_register`):** add a default-off `track_belief` flag on `SituationReader` → additive fields `sm.belief_timeline` + `believes(A,F,t)` + `knows(A,F,t)`; `read()` (only when on) lazily imports `experiments._belief_reader.drive()` and composes the reader's OWN 4-channel extraction (narrator-epistemic + testimony + perception + inference) → the promoted `hdlab.belief_timeline`, reality separate, ignorance=None, source-tagged; value equivalence via the WordNet synonym+entailment path. WITNESS (required): default-off byte-identical + flag-on `sm.belief_timeline`/`believes` == `_belief_reader.drive` output + the FANToM organ check (`exp_belief_fantom_infoaccess_v1`). Register `belief_dimension_live_reader_v1`. Full diff spec in `notes/problems/the_belief_dimension…/PROPOSED_HDLAB_LANDING.md`. ⚠️ A substantial multi-channel effort = a dedicated focused heartbeat, not an end-of-round cram. Flip-on default-off/owner-gated. Ceiling = the shared parser-recall (p2, converges with SPACE).
- **2026-08-31** — **🎯 INTEGRATED (STRONG) the learner LIVE-CANARY `run_the_learner_on_live…`; the continual-growth
  ANTI-DRIFT ANCHOR primitive LANDED into `hdlab/cls_growth.py`.** The reversibility heart (`make_ensemble_sim`+`rollback_gate`)
  was landed 08-31 with the capstone; this adds the anti-drift half: `align_and_fuse` (Procrustes-aligned keep-both EMA slow
  anchor; `alpha`=consolidation-rate `eta`) + `procrustes_rotation`/`_l2norm_rows`, promoted VERBATIM (byte-identical) from
  `experiments/exp_learner_growth_aligned_continual_v1.py`, DEFAULT-OFF ISLAND. Witness `test_cls_growth_anchor_primitive_organ.py`
  5/5 incl. **byte-equality to the experiment** (faithful promotion, no drift). Registered `cls_growth_anchor_primitive_v1`.
  ⚠️ **BLOCKED (documented, not faked): the reader-side `learner_growth` read-out flag depends on `reader_meaning_channel`** —
  `situation_reader.read()` consults NO meaning store, so there is nowhere live to attach the fused read-out. **This is now the
  IMMEDIATE unblocker for a truly in-`read()` learner + the flip-on** (candidate next wire/problem). 🧾 **OWED (tracked, not
  silent): a re-export shim in `exp_learner_growth_aligned_continual_v1.py`** so the 3 promoted functions have ONE source of truth
  (the experiment keeps its copy for now; the witness proves no drift). Flipping growth ON by default = a separate owner call.
- **2026-08-31 (heartbeat)** — **INSTRUMENT FIX (owed Q111 "QA-instrument fix" CLEARED — the correct baseline
  every solver needs).** The QA capstone `experiments/exp_situation_model_qa_v1.py` was INSTRUMENT-COUPLED: it ran
  the DEFAULT (weak) reader and read temporal answers off `sm.events` tense, which `tense_agnostic_events` rewrites
  to a placeholder → temporal questions **collapse 86→0** (measured; probe A/B/C). **FIX:** `run()` now defaults to
  the CAPABLE reader (`build_reader`: tense_agnostic_events+preserve_tense+timeline_register) and `_answer_temporal`
  reads the whole-passage **`sm.timeline_order`** (a tense-INDEPENDENT constraint-graph toposort) FIRST. Additive /
  back-compat: `capable=False` reproduces the old default-reader run, and the timeline_order branch is skipped when
  empty (default reader byte-identical — the existing temporal test still passes 0.904>0.394). Witness
  `verification/test_situation_model_qa.py` **10/10** (+2 new: fast unit — readout consults timeline_order not tense;
  end-to-end — capable temporal_Qs=64>0, keystone-only=0 collapse asserted, model 0.719 > text-order 0.312). **NOT an
  hdlab wiring (instrument only)** → no registry row (registry is keyed on hdlab organ paths). Causal already
  tense-independent (connective gold + `sm.causal_links`); spaCy-free (remote-safe). Remaining owed reader-wirings
  unchanged: graded verb_subcat, p3 copular/nominal (+entity_states), meaning_fusion→reader, the p4 gate on hd_fact_store.
- **2026-08-31 (heartbeat)** — **ASSEMBLY (DEBT 2) +1: the SPACE dimension (WHERE) LANDED into the live reader**
  (default-off `track_space` → `sm.locations`; the 4th assembly dimension after causation/time; lazy `_space_reader`
  prior_ext arm; witness byte-for-byte equivalent over 1040 (entity,t) cells; regressions green). Clears an owed
  WIRE-DON'T-ISLAND landing. Registered `track_space_live_reader_v1`. Remaining owed reader-wirings: graded verb_subcat
  (POS/index plumbing), p3 copular/nominal (+entity_states), meaning_fusion→reader, the p4 gate on hd_fact_store.
- **2026-08-31** — **🎯 THE NORTH-STAR CAPSTONE INTEGRATED (EXCELLENT):** `turn_on_the_learner…` — learn-by-reading
  turns ON safe + beneficial, proven ~9 ways first-hand (5/6 core + 8/8 full; the 1 core fail is the schema-gated arm
  bar-5 refutes). **The default-off CLS SAFE-GROWTH SWITCH landing is now CONFIRMED-OWED + QUEUED** (DEBT 1, CLS row) —
  store-touching, careful, its own focused effort (NOT a heartbeat cram; STORE hazards apply). SEPARATELY: the p4
  schema-congruence gate lands on `hd_fact_store` (the capstone PROVED it belongs on the KB, not the learner). Flipping
  growth ON live is a separate owner-gated step. Reasoning (situation-model) is the North Star's remaining frontier.
- **2026-08-31 (heartbeat)** — **WIRING debt −1: `verb_subcat` LANDED into the live reader.** Promoted the reference
  organ → `hdlab/verb_subcat.py` (+ shim) + a default-off `verb_subcat_gate` (post-read transitivity suppression, the
  through-read()-validated simple gate; == SubcatGateReader byte-for-byte, patients 147→112). Also promoted p5
  (`preserve_tense`) earlier this session. **The live-reader import set grows: `hdlab.verb_subcat` (lazy, flag-on).**
  Queued refinement: the GRADED gate (needs POS/patient-index plumbing in `_read_events`).
- **2026-08-31** — **INTEGRATED 3 owner-DONE submissions (extraction front-end + parser):** p3 copular/nominal (EXCELLENT,
  14/14), p5 tense-preserving (STRONG, 12/12), p2 incremental-parser (EXCELLENT, 16/16). p2 = a route-closing NEGATIVE
  (parser-as-role-lever is a fidelity error → NON-DEBT) + a landing-ready POSITIVE (verb_subcat, who-did-what 0.30→0.49).
  **QUEUED landings (Q111):** p5 tense-preserving (clean, unblocks TIME), p3 copular/nominal (heavier, +entity_states),
  verb_subcat (who-did-what presence gate). All extend the keystone extraction front-end; the learner grows over this.
- **2026-08-30** — **PROMOTION debt −1 (#3):** perceptual_access_ledger promoted `experiments/` → `hdlab/perceptual_access_ledger.py`
  (wholesale; spaCy lazy → no hard hdlab dep; organ witness 5/5; 6/6 unregressed). The observation-cue front-end;
  closes the belief-timeline 0.098 gap once reader-wired. **PROMOTION debt remaining: temporal_order_register (multi-module),
  CLS learner-growth (design-heavy, has a proposed diff to land faithfully).**
- **2026-08-30** — **ASSEMBLY (DEBT 2) started:** packaged p2 `wire_the_causation_typer_into_the_live_reader` — the first
  "wire a promoted organ into the live reader" problem (CAUSATION), scoped to the typer's within-clause domain and respecting
  the integrated cross-sentence negative. Follows the who-did-what assembly template.
- **2026-08-30** — **PROMOTION debt −1 (#2):** state_register CORE promoted `experiments/` → `hdlab/state_register.py`
  (surgical core-only split matching hdlab/location_register.py; organ witness 14/14; 61/61 unregressed;
  spaCy extraction stays exp-side as a shim). Live-reader wiring pending (ENTITIES coref re-rank).
- **2026-08-30** — **verification sweep** of all 35 organ witnesses: **34 PASS, 0 FAIL, 1 TIMEOUT**
  (the parse-frontend witness needs >90s; not a failure). No bit-rot — the incorporated work runs.
- **2026-08-30** — **PROMOTION debt −1:** belief_timeline promoted `experiments/` → `hdlab/belief_timeline.py`
  (default-off, organ witness 11/11, exp file → re-export shim, registered). Live-reader wiring still pending.

## POINTERS (so this is never lost)
- **Refresh:** `python tools/wiring_debt.py [--full]`
- **Machine truth:** `data/capability_registry.jsonl` (per-organ `integration_status` + `gate_decision_target`)
- **Live path:** `hdlab/situation_reader.py` imports (the ~19 live organs)
- **Learner chain:** `notes/LEARNER_ON_ROADMAP.md` · **Brain fidelity:** `notes/BRAIN_FOUNDATIONAL_AUDIT.md`
- STATUS `POSITION` links here; MEMORY `[[wiring-map-burn-down]]` links here.
