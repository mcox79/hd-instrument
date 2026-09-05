# TOP-DOWN INTEGRATION PASS — the pre-mapped execution plan

Companion to `notes/INTEGRATION_LEDGER.md` (the tracker/scoreboard). This is the **ordered, wiring-mapped execution plan** so the pass runs fast once the last in-flight problems land. Every file/function/gate below is disk-verified (2026-09-05). Q111: strategy owns all hdlab writes.

**Method (every step):** turn on / wire → measure the board off-vs-on → update the downstream consumer to RECEIVE the signal → measure again → lock. ORDERED top-down, NEVER a simultaneous flip (the `referent_per_np` lesson: a who-did-what win silently tanked coref). Attribute every delta. `no-default-off` + `flip-on-find-the-break`.

## Pre-pass checklist (do at kickoff, after the last 4 land)
1. **Gate scan** — `grep -rlE "^owner_verdict:[[:space:]]*DONE" notes/problems/*/OWNER_NOTES.md` with no `INTEGRATED_BY_STRATEGY`; reverify + grade + STAGE each new owner-DONE (cheap hygiene), batch the live-wiring into the pass.
2. **Fresh BASELINE board** — `experiments/exp_situation_model_qa_v1.py --run` (all current defaults, 100 docs, local capped-threads). This is the "before" reference the whole pass measures deltas against (the last committed agg 0.389/0.659 is stale — arceager/predicate_recall/goal-graph/causal-mental-bridge all changed since). Commit it as `baseline_pre_pass_2026-09-XX`. **Board harness smoke-tested clean on 8 docs (this session).**
3. Confirm the ledger scoreboard rows are current (add rows for the 4 just-landed).

---

## STEP 0 — BOARD-INSTRUMENT UPGRADE (do FIRST; verdict-independent measurement infra)
**Why first:** several LIVE gains are invisible because the board under-measures. Fix the ruler before turning knobs, else the pass can't attribute gains.

- **0a. Patient-slot who-did-what QA.** Disk-verified: `build_events_questions` (exp_situation_model_qa_v1.py:649) asks **agent-only** (`"slot":"agent"`), though `_answer_events` (:433) already handles `patient`. The LitBank patient/object gold is ~76%-oblique CONFOUNDED (multiple solvers flag it INVALID).
  - **Build:** a `patient` events sub-arm scored on **CLEAN UD-EWT gold** (patient := gold `obj` | `nsubj:pass`), reusing `experiments/exp_valency_labeled_patient_v1.py` (UD_TEST = `data/corpora/ud_english_ewt/en_ewt-ud-test.conllu`; `labeled_pick`; the clean-gold builder at ~:190). Score the live reader's `structural_patient_pick` path (`hdlab/predicate_argument_frontend.route_predicate_arguments`, default-on) against it.
  - **Realizes:** the already-live patient +0.0861 (clean UD) — currently invisible.
  - **Also:** re-base/annotate the events who-did-what board note that the LitBank patient arm is INVALID (agent arm stays on LitBank; patient arm on clean UD).
- **0b. Goal-hierarchy multi-hop arm.** Only 4% of board goal-why is multi-hop → the graph's 1.000 plot-structure result is invisible. Reuse `experiments/exp_goal_hierarchy_qa_v1.py` (30-item authored battery) as a `goal_hierarchy` sub-arm.
- **Non-conflict:** build as additive arms; don't alter existing scored dims' numbers until measured with owner visibility.

---

## STEP 1 — EVENT/PREDICATE TIER: wire the CRF posterior → predicate_detector
Disk-verified: `hdlab/crf_tagger.py` (`GlassBoxCRF.vpost`, pure-numpy, asset `data/frontend_assets/pos_crf_glassbox_ud_ewt.json`) has **ZERO importers = LATENT**. `predicate_detector` IS live via `situation_reader` (`predicate_recall` default-ON).
- **Wire:** swap `predicate_detector`'s category cue `verb_margin` → `logit(CRF vpost)` (lifts its 19c recall 0.582→0.806). **CRITICAL GATE:** a HIGH-PRECISION verb-recovery threshold — the recall-tuned threshold floods the parse (6576 forced VERBs collapse who-did-what reachability 0.698→0.497). Measure the precision/recall operating point on 19c before flipping.
- **Realizes:** +0.041 free-text 19c event recall / +0.31 who-did-what reachability (both currently on deployment instruments only).
- **Then:** re-validate the ~20 role-output organs (world_state/causation/hd_fact_store) — this is also the gate `structural_do_recover` was held on (feeding low-confidence recovered patients asserts false facts). Needs a clean 19c gold + info-free random-recovery twin LOSING.

---

## STEP 2 — COREF/ENTITY TIER: land the STAGED entity-KB resolver (owner-DONE pri 2)
Disk-verified: no `hdlab/entity_world_model_resolver.py` and no `role_kinship_scenario_kb.json` on disk yet. Reverified `test_entitykb_resolver_v2.py` **6/6**.
- **Promote → `hdlab/entity_world_model_resolver.py`:** `resolve()` (exp_entitykb_resolver_v2.py:234, ~250 lines) + the KB (`KB_GROUPS`/`_KB_ROLE2GROUP`/`_KB_ROLE2GENDER`, :91–113) + `kb_group`/`kb_gender`/`kb_role_compatible` + `Salience` + deps (`Entity`,`_actr` from exp_commonnoun_entity_world_model_v1; `LK`/`DIAG`/`DEC` helpers). Full-chain params: `salience="composite", kb=True, repair=True, sitmodel=True, attrs=True, pron_coref=True, reader_coref=<live sm.entities head-sets>`.
- **KB asset:** ship `KB_GROUPS` → `data/frontend_assets/role_kinship_scenario_kb.json` (small hardcoded dict; inline-in-organ is also acceptable — glass-box either way).
- **Live coupling:** the resolver's `reader_coref` param takes the reader's per-text `person_entity_heads` (built in exp_reader_sitmodel_cache_v1 from `sm.entities` head-sets) — wire the LIVE `sm.entities` head-coref at read() (NOT a cache). Integrate as the common-noun-coref path in `hdlab/commonnoun_binder.py`.
- **DO NOT** wire the reader AGENT head-match (regresses named coref −0.0064 CI-sep). Default-ON justified (aggregate +0.0809 CI-sep, downstream relational +0.1440, named no-regress).
- **Realizes:** the common-noun coref +0.43 headroom / 0.54 ceiling — which caps affect experiencers (87% of affect loss) + goal/relational binding.
- **Adjacent (owner call):** the `+0.043` above-baseline coref bonus (overlay-by-discourse-entity from `wire_the_referent_to_coref_linking_pass`) — decide land vs hold (it consumes the coref column's provided clustering).

---

## STEP 3 — WHO-DID-WHAT TIER: realize the patient gain + sweep optimizations
With Step 0's patient-slot arm live, the +0.086 patient becomes visible (structural_patient already default-on). Then sweep named-but-unbuilt levers: thetic/presentational/unaccusative construction detector (~20% new-agent ceiling), animacy_lexicon coverage misses, a register weight re-sweep for modern prose. Passive PATIENT via `precise_voice` is still default-off (adjacent gap).

---

## STEP 4 — MEANING TIER (the big latent cluster): build the ONE read()-time meaning stage
Disk-verified: `diagnostic_context_wsd`, `meaning_foundation`, `composed_hub_predictor` have **ZERO hdlab importers** — the reader never consults meaning. FOUR proven gains wait on this one stage: curated foundation +0.0755, rare-sense readout +0.065, precision-weighting +0.023, clean-foundation +0.067.
- **Build a `reader_meaning_channel` stage in `situation_reader.read()`** consuming `hdlab/meaning_foundation.py` (frozen curated KEYS) via `hdlab/diagnostic_context_wsd` — STACK the three landed opts: curated KEYS + gamma/topk precision-weighting + `sense_prior`/`prior_weight` Bayesian.
- **Within-invariant now (pri 4):** rebuild `composed_hub_predictor`'s verb-role exemplar store on the 80k C1b store + adopt MaxSim (over AvgSim, +0.065), wire into the live who-did-what/argument path, measure the live consumed metric (no-default-off). Also: swap the reader's default distributional store `hub_ppmi_svd_200d` → the 80k C1b store.
- **§2-GATED (the FINE rare-sense half):** the contextual-encoder route to break the ~0.35 subordinate-sense ceiling — HOLD pending the owner decision. The within-invariant KEYS/hub half proceeds regardless.
- **Realizes:** the whole latent meaning cluster at once (coarse), on a scored meaning/who-did-what consumer.

---

## STEP 5 — DOWNSTREAM SIGNAL-UPDATES: feed the new event-TYPE signal to its consumers
The causal landing (`hdlab/event_type.py`, live) added +214 mental causal links but 3 consumers don't yet RECEIVE the event-type signal:
- **`causation_typing`** → add a MENTAL/INTENTIONAL causal type routed by event-type (coverage 3/16 → 16/16 real edges).
- **`affect_register`** → its OCC-appraisal inferred-emotion channel (EMOTION/BODY outcome appraised against a preceding PERCEPTION/COGNITION trigger).
- **`goal_hierarchy_graph`** → the motivational spine (+47 enablement edges, already additive/superset-verified).
- **Instrument:** mine a real-corpus non-adjacent MENTAL-bridge gold (the missing scored instrument — no live mental-causal metric exists) so the mental bridge's field accuracy becomes measurable.
- **Also route through** the GroundedSemanticGraph WSD organ (event-typing 0.688→0.750, chain 0.875→0.938) + the reader's live coref for the experiencer gate (removes the out-of-reader 0.500 ceiling).

---

## LAND-READY NOW (verdict-permitting)
- **arc-labeler fast path** (`add_the_arc_labeler_fast_scoring_path`, currently OPEN): a byte-identical ~54% whole-read speedup. Land the moment it's owner-DONE — promote `_FastLabelPlan` + `ArcLabeler._ensure_fast` into `hdlab/arc_labeler.py`, route `label()` through it, keep `_predict_label`/`_score` as the training/reference path. Compounds with the landed parser + tagger speedups.

## CLOSE-OUT
Fresh FULL board with everything integrated = the **realized aggregate** (never measured end-to-end). Every scoreboard row must then have a board dim that moved by its claimed amount, or a named reason (invariant / instrument gap / located negative). Fold an `AUDIT UPDATE` into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b per step.

## GATING OWNER DECISION
**§2/P9 — HOLD the no-transformer invariant (strategy rec) vs relax for one offline contextual encoder.** Gates only the FINE rare-sense half of Step 4. Everything else (steps 0–3, 5, the within-invariant Step-4 half) proceeds regardless.
