# WALL MAP — every below-peak wall drilled to its NON-BRAIN-FOUNDATIONAL DECISION (2026-09-06)

**Owner directive (2026-09-06):** "research any wall until we understand it. the brain does it and excels, so where we aren't excelling, we've made a non-brain-foundational decision somewhere." This map drills the biggest below-peak walls (from the capability scoreboard in `INTEGRATION_LEDGER.md`) to the exact deviation. Method: 3 read-only research drills, each LEADING WITH BIOLOGY, reading the drilled SOLVEDs + audit + a literature check. A "ceiling" is only real after a fair test of the EXACT brain mechanism; otherwise it is a fidelity gap to BUILD across.

---

## THE DOMINANT FINDING — it is ONE decision, seen three times

**We built a FEED-FORWARD PIPELINE OF HARD-COMMITTING SILOS (tag → parse → assign-role → mean, each committing a single best hypothesis before the next), instead of the brain's SINGLE RECURRENT, TOP-DOWN-PREDICTIVE, GRADED loop where the situation model constrains every lower stage as it reads.** The audit already names it: *"the assembled reader is N parallel silos, not one integrated situation model"* (§2b 2026-08-31). All three drills land on the same place:

- **Parser drill:** the load-bearing deviation is the **greedy, bottom-up, hard-1-best arc-eager parser with a distribution-free score, computed BEFORE and INDEPENDENT of the situation model.** Proof (modern-board §6c): the role assigner is preverbal-dominated → picks the same as position 84% of the time → on position's failures recovers gold only **0.137, BELOW random (0.155)** — because "only a PARSE tells you which regime a clause is in," and the greedy hard-commit throws that graded parse away. A/B: the AGENT (read by `graded_competition`, keeps alternatives) has reliability margin **AUC 0.76**; the PATIENT (read off the greedy arc) has **AUC 0.50** — same precision-weight move, the only difference is the hard-commit.
- **Meaning drill:** each context word is a **frozen, sense-conflated type-vector re-resolved by NOTHING** — the readout scores a bag of frozen vectors (`diagnostic_context_wsd.py`), with **no recurrent meaning→context loop**. The substrate's own top-down organ `predictive_reader` (Altmann-Kamide forward prediction) is BUILT but *"a pure inert island"* (never on a live path). Disk localizes the loss to exactly this: KEY-unwinnable 0.000, QUERY-loss 100%, and a perfect sense-discriminative W fed to the *same* readout → **a_s 0.995**.
- **World-knowledge drill:** the brain's glass-box KB organs — `grounded_semantic_graph` (Collins-Loftus PPR spreading activation), `event_type` (Schank event schema), `entity_world_model_resolver`, `meaning_foundation` — are **BUILT but LATENT / default-off**, not wired into the read()-time loop.

**So the pieces of the brain's loop are already built as islands; the LOOP that integrates them — top-down prediction constraining parse + sense + knowledge-gap-filling — is the missing organ.** The single highest-leverage brain-foundational build is to CLOSE THAT LOOP (wire `predictive_reader` + `n400_coherence_monitor` + the structured situation model into the parse and the meaning stage), not more silos.

---

## THE WALLS — non-brain decision → buildable fix → falsification test

### 1. Meaning / word-sense (a_s ~0.33 fine)
THREE layered decisions; the biggest two are cheap + proven, NOT a ceiling:
- **A — we score at the FINE WordNet grain the brain does NOT use.** Human fine IAA ~0.72; coarse/shared-core ~0.90; in neutral context humans default to the dominant sense (Duffy-Morris-Rayner subordinate-bias). Our SAME picks score **0.2697 fine vs 0.5412 coarse** — a real context-driven win (coarse beats coarse-MFS **+0.1377 CI-sep**, context-shuffle twin **+0.1104 CI-sep**). **Build gap, 100% inside the invariant.**
- **B — the entire meaning channel is LATENT** (no live sense-selection consumer; everything proven is default-off/unwired → scores ZERO on the board). Wiring-debt decision.
- **C (the deep one) — frozen context, no recurrent re-resolution loop** (the dominant finding above).
- **Fix:** wire the meaning channel live + emit the COARSE (shared-core) sense (A+B, proven, buildable NOW — the word-sense p7 integration); then close the recurrent loop over the structured situation model (C).
- **Falsification:** on a MODERN COARSE WSD/WiC set (Raganato/SemEval-2015, the acquisition gap), does recurrent re-resolution beat the one-shot bag CI-sep, settle-over-shuffled-structure twin losing? **Honest prediction: crosses at COARSE, not FINE.** The FINE-grain residual is likely a genuine within-invariant limit — **and the brain doesn't excel there either** (it doesn't make that distinction), so it is NOT a counterexample to the principle. §2 no-encoder HOLD is empirically confirmed for the right reason.

### 2. Who-did-what / parser front-end
- **Non-brain decision:** the greedy hard-1-best distribution-free parse computed before the situation model (the dominant finding). NOT the POS tagger (3% of failures) and NOT candidate coverage (78% are *discrimination*, not coverage). UAS is the WRONG target (a better-UAS parser moves who-did-what ~+0.00).
- **Fix (glass-box, NOT "train a better parser" — trained loses OOD):** an intrinsically-graded, small-beam (top-2/3, P600-bounded), top-down-conditioned incremental parser as ONE organ — reuse `graded_competition` + `incremental_parser` + the calibrated per-arc confidence (AUC 0.858 prototyped) + WIRE `predictive_reader`'s top-down expectation into the attachment competition, so the PATIENT arc gets the AGENT organ's graded margin and the role competition gets a *decorrelated* "which regime" signal.
- **Falsification:** on position's canonical FAILURES (the 78% bucket), does the maintained-distribution parse cue recover gold CI-sep above the scrambled-structure twin (0.169) + random (0.155), no canonical regress? YES → build gap crossed. The residual **two-valid-agents** slice (89% of tie errors are character-vs-character) routes to grounded event-knowledge — invariant-bounded, NOT impossible, and a real ceiling only after that channel is fairly built.

### 3. World-knowledge ("barred by no-LLM" — a PARTIAL MISFRAME)
- **The misframe:** the invariant bars a trained LLM at inference but ALLOWS a static offline glass-box KB. The brain's world knowledge IS such a KB (Collins-Loftus network + Schank scripts + Kintsch C-I). "needs world knowledge → barred" conflates "needs a KB" (admissible, brain-foundational) with "needs an LLM" (barred). **But the solvers largely did NOT stop at "barred"** — they built the glass-box route and crossed most of both walls (entity-world-model chain 0.255→0.540 = 63% of the gap; mental-causal 70%-majority UNIFIED 1.000 vs 0.500).
- **The named decision that IS load-bearing:** (b) non-cued temporal ordering was deferred "Phase-1-gated" though the glass-box **event-schema** route (already built as `event_type.py` for causal) crosses it — a real unwired win.
- **The encyclopedic is-a slice — the RIGHT way to add it (corrected TWICE 2026-09-06: over-corrected to "withdrawn," then owner pointed to the ingest pipeline).** The distinction is INFERENCE-TIME RAW LOOKUP of a dump (a shortcut / external-tool-at-inference — reject) vs **OFFLINE INGEST THROUGH THE CONSOLIDATION/PRUNE GATE into the clean typed frozen store (brain-foundational = systems consolidation; ADMISSIBLE; PROVEN).** We already have the standalone module: `hdlab/consolidation_gate.py` (ingest→filter[recurrence+multi-seed+PPMI+schema-margin]→admit; raw-ungated twin LOSES −0.033, consolidated +0.067) + `hdlab/cls_growth` (reversibility) + `hdlab/learner/` — this is literally how the current `meaning_foundation` was built from WordNet+SyntagNet+ConceptNet. So ingesting a curated encyclopedic is-a/type KB through the SAME gate is the "clean foundation expanded to all knowledge" program (owner-posted: `build_and_freeze_the_clean_curated_knowledge_foundation`, `turn_on_the_learner...`, the 2026-09-04 import factory), NOT a shortcut. LEVERAGE is BROAD (it feeds the whole semantic store the meaning channel / bridging / coref / temporal-event-schema read — not the 8%-coref slice I first scoped it to). SEQUENCING: it pays off only once the meaning channel is wired LIVE (the store is latent today) → wire the channel first, then expand the foundation; and route a STRUCTURED KB (already clean/typed) through the import-factory admission path, not the reading-co-occurrence filters.
- **Fix:** wire `event_type.py` as the non-cued temporal-ordering prior (pure reuse); and, after the meaning channel is live, expand the frozen foundation with a curated encyclopedic is-a/type KB via the consolidation-gate ingest pipeline.
- **Honest genuinely-open-web residual:** a fraction of **~8%** of anaphoric common nouns (novel/FICTIONAL named entities with no encyclopedic entry — genuinely irreducible) + the above-0.540-ceiling multi-person cases. **NOT the "81%" the current headline implies.** → CORRECT THE SHORTHAND in the audit: "needs world knowledge → barred" should read "needs a static glass-box KB (admissible) vs needs a trained LLM (barred)."

### 4. Cross-cutting — FROZEN PHASE-DIAGRAM PARAMETERS (owner 2026-09-06)
- **Non-brain decision:** solvers treat the substrate's operating point (sparse↔dense, dimension, binding regime, capacity, decay/gain, indexed-vs-superposed) as FIXED, when it is FREE to move at any time, per organ. A wall "at this config" = MOVE the operating point, not a ceiling. The brain re-tunes these continuously (attention→precision/gain; sparsity→load). Fold into the brief standard so every solver checks "did I freeze a movable parameter?" See `dimensional_phase_diagram_audit_of_the_current_organs`.
- **Twin failure mode (from the coref wire):** solvers also measure against an ISOLATED/DEFAULT config, not the LIVE (already-tuned) substrate — the entity-unification +0.106 was vs a weakened baseline; the live incumbent's stronger pool config already subsumed it. Measure against the LIVE config AND consider moving it.

---

## THE GENUINE WITHIN-INVARIANT RESIDUALS (honest ceilings — and the brain doesn't excel there either)
1. **Fine-grain WSD** (below the shared-core): humans ~0.72 IAA; the brain uses coarse. Not a violation of "the brain excels."
2. **~8% of common-noun name_bridge = novel/fictional entities** with no encyclopedic entry: genuinely irreducible without in-text statement.
3. **Two-valid-agents genuine ambiguity:** needs grounded event-knowledge; invariant-bounded, a real ceiling only AFTER the grounded event-knowledge channel is fairly built.

Everything else below peak is a BUILD GAP, not a ceiling — and overwhelmingly ONE build: **close the recurrent top-down loop + wire the already-built glass-box organs into it.**

---

## FORWARD PLAN reshaped by this map (highest-leverage first)
1. **Wire the meaning channel live + emit COARSE** (word-sense p7, queued) — realizes the proven +0.14–0.20 latent gain; the meaning channel's first sense-selection consumer.
2. **Close the recurrent top-down loop** — wire `predictive_reader` (+ `n400`) into (a) the parse attachment competition and (b) the meaning re-resolution. This is THE dominant non-brain fix; it lifts parser, meaning, temporal, causal at once. A multi-step build (rubric: `PARSER_JOINT_INTEGRATION_RUBRIC.md`).
3. **Wire the latent glass-box KB organs** (`event_type` → temporal; `entity_world_model` → coref; `meaning_foundation` → the live consumer) so the world-knowledge gains reach a live board dim.
4. **Correct the "barred" shorthand** in `BRAIN_FOUNDATIONAL_AUDIT.md` ("needs a static glass-box KB = admissible, ingested offline through the consolidation gate" vs "needs a trained LLM at inference = barred").
5. **After the meaning channel is live (step 1):** expand the frozen foundation with a curated encyclopedic is-a/type KB via the `consolidation_gate` ingest→prune pipeline (the proven +0.067 machinery that already ingested WordNet/ConceptNet/SyntagNet) — brain-foundational offline consolidation, NOT inference-time lookup. Broad leverage (whole semantic store), latent until step 1.
