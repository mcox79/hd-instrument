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
- **2026-09-02 (WIRE — DEBT-2 (a) first piece LANDED: the arc-eager parser route into the live reader)** — **⚡ WIRED a default-off `parser_arceager` flag on `SituationReader`.** When on, `_router_roles` (the role_route='wired' who-did-what path) sources its parse heads from the promoted `hdlab.arceager_parser` (UAS 0.775→0.842) instead of the richfeat `arc_parser`, feeding `predicate_argument_frontend` (both return `Dict[int,int]` 1-based heads — a drop-in swap). Witness `test_parser_arceager_route_landing_organ.py` **4/4** first-hand: default-off byte-identical (219 events == the no-flag wired reader), flag-on LIVE (changed who-did-what on 10/219 events — only the head source differs), flag-on VALID (patient-fill 0.489→0.489, no collapse), organ sanity. Registered `parser_arceager_route_live_reader_v1`. REMAINING DEBT-2 (a) hooks (scoped): `attach_conf`→`graded_competition` (N7 currency), calibrated-abstain→`predict_revise` drop-trigger, deeper predarg PP-role routing. Flip default-ON is a separate owner decision — measure the QA who-did-what lift vs the 0.205 baseline first.
- **2026-09-02 (INTEGRATION — three owner-DONE; 1 promotion landed, 3 reader-wires scoped DEBT-2)** — **🧠 FOLDED IN the improved parser + the coref-densifier EntityBinder + the grow-the-graph located-negative (all EXCELLENT; reverified 8/8, 18/18, 4/4 first-hand).** PROMOTED the arc-eager parser operator → `hdlab/arceager_parser.py` (self-contained, VERIFIED byte-faithful 6/6 first-hand, DEBT-1 burned; registered `arceager_parser_operator_v1`; asset `data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz`). ⚠️ **SCOPED DEBT-2 WIRING ROUND (3 reader-wires, precise targets):** (a) **PARSER** — a default-off `parser='arceager'` route on the reader front-end (needs a POS source; UAS drops gold→pred-POS, measure on target corpus) + `attach_conf`→`graded_competition` (the N7 difficulty currency) + calibrated-abstain→`predict_revise` drop-trigger + route `predicate_argument_frontend` through the improved parser (this is where the parser gain LANDS: matrix-verb F1 +0.015, PP/oblique-role F1 +0.027, feeds `world_state` ARG2). NOTE: `parse_with_conf(tokens, pos, W)` needs POS as input (does not tag); head 0 = ROOT and conf=0.0 means "defaulted-to-root, not scored". (b) **COREF-DENSIFY** — promote `experiments/world_state_entity_binding.py` → `hdlab/world_state_entity_binding.py` (self-contained, imports only stdlib) + a default-off `densify_world_state` flag on `_read_world_state` (indexical I/me→NARRATOR + object-anaphora it→recency routes are self-contained in the binder; the he/she route needs the reader's mention-level coref stream — `event_centrality_coref.resolve_stream` midx→cluster — plumbed in). (c) **MEANING READ-OUT** — the grow-the-graph TIER-1 read organ (reordered-access → competitive settling → `semantic_control`), which IS the grounded-semantic-graph organ's own DEBT-2 completion (emit the graded SETTLED activation vector, not an argmax synset). Do NOT wire the grow-the-graph discrete-edge GROWTH (confirmed non-improvement). **THEN BENCHMARK** after wiring (fast QA ~2-5 min + a targeted meaning-channel run) vs the 0.352 / 0.205 baseline. Follow-ons FILED as the fresh queue: `wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector` (1), `register_native_parse_and_pos_training_data…` (2), `incremental_entity_maintenance_pronoun_chaining…` (3).
- **2026-09-01 (PROMOTION — DEBT 1 burned for the north-star meaning organ)** — **🧠🥇 PROMOTED the grounded semantic GRAPH organ to `hdlab/grounded_semantic_graph.py` (self-contained, byte-faithful). DEBT 1 (promotion) burned; the reader/consolidation REFRAME is DEBT 2, a MEASURED re-architecture, sequenced next.** Inlined the ~14 primitives the experiment organ imported (from the ladder-WSD + PPR-spreading-activation + sense-wall cells) so the hdlab file has NO experiments imports; VERIFIED FIRST-HAND (witness `verification/test_grounded_semantic_graph_organ.py` **3/3** — builds 117,659 synset nodes / 1,025,488 edges in ~67s, differentiates 'bank' river `bank.n.03` ≠ money `depository_financial_institution.n.01`, and BYTE-EXACT to the experiment organ's `select_sense` on 6 ambiguous probes bank/plant/crane/bass across contexts). Mechanical inline by a directed subagent, re-verified first-hand (rebuilt both graphs). Registered `grounded_semantic_graph_organ_v1`. ⚠️ **DEBT 2 (DEFERRED as a MEASURED unit, NOT rushed): reframe `reading_grounding_loop.canonicalize` FLAT cosine → GRAPH DIFFUSION.** KEY FINDING (why it is deferred, not islanded-by-neglect): `canonicalize` is **NOT** in the live `situation_reader.read()` path — it is the OFFLINE grounding/CONSOLIDATION write-path (foundation building), and it does CONCEPT-ANCHOR merging by cosine (not WordNet WSD), so the reframe is a delicate change to a LOAD-BEARING function that must be **MEASURED** (does graph-diffusion grounding beat flat-cosine grounding on a held-out grounding task?), and it **COMPOSES with the in-flight pri-1 grow-the-graph-from-reading learner** (pri-1 = the WRITE/GROW half; the reframe = the READ half). The brain-foundational COMPLETION (emit the graded SETTLED PPR activation vector, not an argmax synset — +0.067 AUC richer) rides WITH the reframe. Do it after pri-1 lands (same path) OR as its own measured unit with the box available. This follows the established belief_timeline/state_register pattern (promote → DEBT 1 burned → reader-wiring = DEBT 2 pending).
- **2026-09-01 (INTEGRATION + WIRE — the STATE dimension)** — **🧩 INTEGRATED + LANDED the mutable WORLD-STATE register (`situation_model_has_no_mutable_world_state_register`, owner-DONE, EXCELLENT) — the situation model's STATE dimension (WHO-HAS-WHAT / OPEN-CLOSED at story-time t), the aligner's #1 named adjacent gap, is now WIRED.** Reverified **36/36** first-hand (register 1.000 vs the strongest stateless floor `last_obj_mention` 0.750, +0.250 CI-sep; three info-free twins lose; precondition-read 1.000 vs ever-had 0.512; FrameNet 105-verb operator lexicon WITH recipient; learn-and-adapt recovers gold 1.000 vs shuffle 0.417 + abstains on non-transfer). **LANDED:** promoted `experiments/world_state_register.py`→`hdlab/world_state_register.py` + `experiments/possession_operators.py`→`hdlab/possession_operators.py` VERBATIM + a default-off `track_world_state` flag on `SituationReader` → read() (LAST over the final event set) folds the reader's OWN events into `sm.world_state` = a `WorldState` (possession have(holder,obj) + open/closed toggles as STRIPS operators; PRED/AGENT/PATIENT from the reader's extraction, recipient/source from `wired_extra_roles`, operator class from the cached FrameNet lexicon — no nltk at inference) exposing has/holder_of/is_open/unmet_preconditions. Witness `test_world_state_register_landing_organ.py` **4/4** — default-off byte-identical (219 events / 136 entities on 1023_bleak_house) + flag-on register == a recompute through BOTH the hdlab core AND the experiments core BYTE-EXACT (4 objects × 222 story-times) + promoted-core mechanism + the wire builds correct mutable possession on a known transfer (anna GETs→GIVEs to ben; FrameNet recipient consumed; final holder ben). Registered `world_state_dimension_live_reader_v1`; `reader_capabilities` manifest updated. ✅ **The live-reader import set grows: `hdlab.world_state_register` + `hdlab.possession_operators` (lazy, flag-on).** ⚠️ **HONEST BOUND:** the wire lands the CAPABILITY (mechanism-proven, byte-faithful); LIVE who-has-what on real prose is COREF/parser-recall-bound (81% pronoun agents — the register faithfully folds whatever the reader extracts, so 19c extraction noise flows through). The register-through-coref open-text re-measure + frame-SENSE selection are the located follow-ons. REUSES the existing `location_register` (SPACE) + `state_register` (ENTITIES) — builds only the genuinely-missing possession + mutable-forward-application + precondition-READ. CONFIRMS order is conventional (the register does NOT break the ~0.59 before/after order wall). Flip-on default-off/owner-gated.
- **2026-09-01 (INTEGRATION + WIRE QUEUED)** — **🧠🥇 INTEGRATED the NORTH-STAR MEANING ORGAN (grounded semantic graph read by spreading activation, owner-DONE, EXCELLENT, 5/5). WIRE QUEUED with a precise target.** ⚠️ **QUEUED WIRE (Q111, DEBT 2 + DEBT 3 — the meaning-channel unblock):** promote `experiments/grounded_semantic_graph_organ.py` (~verbatim — build / select_sense / add_edges / learn_from_text) to `hdlab/` + reframe `reading_grounding_loop.canonicalize` from a FLAT cosine lookup → GRAPH DIFFUSION (personalized-PageRank spreading activation over WordNet + disambiguated gloss + ConceptNet thematic edges). Default-off, byte-identical when off. Acceptance gate = `verification/test_grounded_semantic_graph_ladder.py` (5/5). Register `grounded_semantic_graph_organ_v1`. ⚠️ **THE BRAIN-FOUNDATIONAL COMPLETION (item 1, do WITH the wire):** the organ must EMIT the graded SETTLED activation vector (the brain's contextual meaning), NOT argmax a synset — the settled vector ranks meaning +0.067 AUC richer than the label (held-out CI-sep); route it into `situation_reader` / `meaning_fusion` (this ALSO clears the "meaning organs are unwired islands" audit debt). ⚠️ Wire `semantic_control` onto the walk (the landed PINNED per-item gate) as the reliability-weighted control the SemCor boundary located as missing. NEW owner-authorized data assets on disk: `data/syntagnet/SyntagNet-1.0/` (CC BY-NC-SA), `data/wsdeval/WSD_Evaluation_Framework/`. FOLLOW-ONS not yet issued: the LEARNED graph (grow/retune/own-granularity — the north-star program, specced; heavy → REMOTE) + the settled-vector downstream demo (graded/compositional task, REMOTE).
- **2026-09-01 (INTEGRATION + WIRE QUEUED)** — **🧩 INTEGRATED the verb-role EXEMPLAR selector (p5, owner-DONE, EXCELLENT, 10/10). WIRE QUEUED with a precise target (a substantial landing: new organ + a 14.7MB offline asset + a construction-conditional integrator — flagged the asset-size decision to the owner).** ⚠️ **QUEUED WIRE (Q111, DEBT 2):** add `hdlab/verb_role_exemplar_selector.py` — load `data/selectional_preferences_v1/selectional_slots_v1.pkl` (14.7MB glass-box UD verb-role exemplar store) + `select_patient(verb, candidates) -> head` scoring candidates by nearest-exemplar (k-NN) GROUNDED similarity to the verb's OBJ fillers, with a `precision`/coherence (peakedness) trust weight. Wire it (default-off, byte-identical when off) as (a) the drop-fill TARGET selector in the LANDED `predict_revise` path (replacing the nearest-nominal position fallback with the exemplar selector when the store covers the verb), and (b) a role-assignment TIE-BREAKER at non-canonical order, INTEGRATED with position via construction-conditional cue weighting (down-weight word-order at non-canonical structure — the deployment win +0.027 over the live wired reader). Acceptance gate = `verification/test_verbrole_exemplar_which_arg.py` (10/10). Register `verb_role_exemplar_selector_v1`. ⚠️ Do NOT wire it as a 19c/OOD selector (it ties its twin there — register-native store missing); ship the `semantic_control` shrinkage as the OOD safety layer (graceful degradation). ⚠️ **ASSET DECISION for the owner:** the store is 14.7MB — force-add to git (like the 1.9MB POS-tagger/predict_surprisal assets, but ~8×), OR trim/lfs. The FHRR-bound variant (`exp_fhrr_event_role_assignment_v1.py`, reuses the wired `hdlab.binding` + `bound_event_backbone`) is the brain-foundational form + an optional ship. The register-native corpus (the #1 lever, +0.149) is ISSUED as its own problem (`the_selectional_event_store…register_native_corpus`, pri 2).

- **2026-09-01 (INTEGRATION + WIRE — the ASSEMBLY completion)** — **🧩 INTEGRATED + LANDED the TIERED BOUND-EVENT-TOKEN BACKBONE (p4, owner-DONE, EXCELLENT) — DEBT 2, THE ASSEMBLY, is now REAL, not just composed.** The assembled reader was N PARALLEL SILOS: each dimension stored the MARGINALS (the set of agents / actions / times), nothing stored the JOINT (which agent did which action). That is the BINDING PROBLEM. Reverified **10/10** first-hand (JOINT coref 1.000 CI-ABOVE late-fusion-of-marginals 0.600, sep +0.400, on LitBank old fiction AND UD-EWT modern web; binding-shuffle collapses it; twin null; MUST-CHUNK fires @ M=256; cued retrieval 1.00 vs silo 0.01; NECESSITY grounded 0.379 > symbol 0.217 under paraphrase). **LANDED** a default-off `bind_event_tokens` flag on `SituationReader` → read() (only when on, LAST over the final event set) builds `sm.event_tokens` (ONE FHRR bound token per event over {AGENT,PATIENT,PRED,TENSE} — the JOINT the silos can't store) + `sm.episodic_store` (a `BoundEpisodicStore`: N400 CHUNK segments + a DG/CA3 STORE tier + a `resolve`/`corefer` readout via the DIRECT bound-token route — the validated route that completes at 1.00; the DG-at-retrieval CA3 path is a known low-fidelity follow-on). The wire is a **NEW thin assembler `hdlab/bound_event_backbone.py`** that COMPOSES existing organs ONLY (`binding` + `n400_coherence_monitor` + `hippocampal_encoder`), promoted VERBATIM from the validated cell so a wired token is **torch-EQUAL** to the cell's. Witness `test_bound_event_backbone_landing_organ.py` **5/5** — default-off byte-identical (219 events on 1023_bleak_house_brat; event_tokens/episodic_store None + event set/entities/timeline/causal unchanged) + all 219 tokens byte-exact vs `E.event_token()` + `resolve`==`joint_decide` 30/30 (accept a real event, reject a RECOMBINATION) + the tiered store genuinely assembled (N400 12 segments + DG/CA3 (219,4096)). Registered `bound_event_token_backbone_live_reader_v1`; `reader_capabilities` manifest updated. ⚠️ PLACE-binding is a mapped follow-on (`locations` accepted but not bound — would diverge from the validated 4-role result); a faithful EC→CA3-direct completer + the **front-end ROLE-assignment lever** (agent-role 0.271 while event recall 0.953 = the real ecological bottleneck) are the sharply-scoped follow-ons. ✅ **The live-reader import set grows: `hdlab.bound_event_backbone` (lazy, flag-on) → binding + situation_model_accumulate + n400_coherence_monitor + hippocampal_encoder.** This is the step from the reader HAVING features to the reader UNDERSTANDING which goes with which — **the prerequisite for reasoning (p6)**. Flip-on default-off/owner-gated (this problem is the evidence).
- **2026-09-01 (WIRING ROUND)** — **🧠 LANDED `track_belief` into the live reader — the BELIEF/ToM dimension (the 5th situation-model dimension, WHO-BELIEVES-WHAT-WHEN). BOTH queued reader-wires are now BURNED DOWN (predict_surprisal + track_belief).** Default-off `track_belief` flag on `SituationReader` → binds two QUERY callables to the passage's own sentences: `sm.believes(agent_aliases, fact, t)` (the agent's registered belief VALUE; may diverge from reality = false belief) + `sm.knows(...)` (Butterfill & Apperly current/stale/ignorant). Each drives the promoted `hdlab.belief_timeline` via the lazily-imported `experiments._belief_reader.drive` adapter (4 channels: narrator-epistemic + testimony [substrate-native] + perception [`hdlab.perceptual_access_ledger` gate, lazy spaCy] + inference), reality separate, ignorance=None. The lazy-adapter track_space pattern (the adapter composes `_space_reader`/`state_register`, so NOT a clean single-file promotion). Witness `test_track_belief_landing_organ.py` **3/3** — default-off byte-identical (104 events, believes/knows None) + `sm.believes/sm.knows` == an independent `drive()+timeline_belief` BYTE-EXACT (t=1,3,5) + the read-out mechanism recovers a correct FALSE BELIEF on a two-agent gold scenario (belief 'drawer' != reality 'shelf' → 'stale'). Registered `belief_dimension_live_reader_v1`. ⚠️ PERCEPTION track lazily loads spaCy (opt-in, local-only, like causation_typed); DOMINANT channels are substrate-native. Live change-of-state extraction on hand-built prose is separately parser-recall-bound (p5's ceiling; FANToM is the powered live population — which is exactly what the just-packaged predictive-parser problem targets). ✅ **The live-reader import set grows: `experiments._belief_reader` + `hdlab.belief_timeline` + `hdlab.perceptual_access_ledger` (lazy, flag-on).**
- **2026-08-31 (WIRING ROUND)** — **⚡ LANDED `predict_surprisal` into the live reader — the FIRST live node of the prediction-error hierarchy (one of the two queued wires, BURNED DOWN).** Default-off `predict_surprisal` flag on `SituationReader` → a POST-READ pass (after verb_subcat_gate) computes per-event N400 SURPRISAL of the reader's OWN bound PATIENT among its sentence's candidate nominals via the promoted `hdlab.predictive_reader` (loaded from a persisted QA-SRL-fitted asset), exposing additive `EventRecord.patient_surprisal` + `.pred_precision` + (with `surprisal_abstain_tau`) `.low_confidence`. Added `PredictiveReader.save/load` (pickle). Asset: `data/frontend_assets/predict_surprisal_predictor_v1.pkl` (1.9MB, force-committed like the POS-tagger asset; roundtrip byte-faithful). Witness `test_predict_surprisal_landing_organ.py` **4/4** — default-off byte-identical (104 events, metadata None) + flag-on `patient_surprisal` == an independent recompute BYTE-EXACT on 55 scored events (`verb=lemma_word(predicate)`, role `PATIENT`, `nominal_heads` VERBATIM from the driver) + abstain flag + asset integrity. Registered `predict_surprisal_live_reader_v1`. Do NOT wire auto-revision (proven NEGATIVE). ✅ **The live-reader import set grows: `hdlab.predictive_reader` (lazy, flag-on).** **Remaining queued reader-wire: `track_belief` (the belief dimension — the other of the two; a focused multi-channel effort).**
- **2026-08-31** — **⚡ INTEGRATED (EXCELLENT) the FORWARD-PREDICTION organ `the_forward_prediction_organ_is_inert…`; one hdlab BUG FIXED; `predict_surprisal` WIRE QUEUED (the first live prediction-error node).** Reverified 8/8. `predictive_reader` validated LIVE as an error-risk flag (AUC 0.651 CI-sep) + abstain decision (+0.035 CI-sep), generalizes to 19c narrative; auto-revise is a decomposed NEGATIVE (structural errors → parser-recall-bound). 🐛 **LANDED (hdlab): `frame_induction.is_passive_real` bounded `range(lo, min(v_idx, len(tokens)))`** — was IndexError on ~1/1300 sentences (verified no-crash on out-of-range v_idx; normal case unchanged). 🔧 **QUEUED LANDING (WIRING_MAP DEBT 2 / prediction-error Phase C — a focused build, NOT a heartbeat cram):** default-off `predict_surprisal` flag on `SituationReader` → additive `EventRecord.patient_surprisal` + `.precision` metadata + an optional `surprisal_abstain_tau` marking the highest-surprisal bindings `low_confidence` (the validated decision). read() (only when on) computes per-argument surprisal via the promoted `hdlab.predictive_reader.PredictiveReader` over the sentence's candidate nominals, exactly as `experiments/_forward_prediction_live.py` proves (imports ONLY promoted hdlab organs — clean). ⚠️ **NEEDS AN OFFLINE ASSET: a PredictiveReader fitted on QA-SRL selectional preferences, persisted + committed** (no existing asset on disk; the 5-dict model pickles cleanly; the fit is ~minutes/120k items). WITNESS: default-off byte-identical + flag-on `patient_surprisal` == the driver's `surprisal_of` on real sentences + the 8/8 organ check. Register `predict_surprisal_live_reader_v1`. Do NOT wire auto-revision (proven NEGATIVE). Flip-on default-off. ⚠️ **TWO reader wires now queued (belief + surprisal) — the reader-integration debt is accruing; a DEDICATED wiring round is the right next move (see STATUS).**
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
