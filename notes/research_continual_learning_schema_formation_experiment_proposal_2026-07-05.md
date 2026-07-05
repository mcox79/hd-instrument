# exp_dev hand-off — research: continual learning schema formation

**Filed by:** Research (5x convergence drill), 2026-07-05.

**Trigger:** `notes/research_5x_drill_continual_learning_spec_and_brain_mechanism_2026-07-05.md` — 5x convergence drill closes on a decisive empirical fact already on disk: `exp_substrate_c3_segregated_dual_W_spectrum_replication_v1` (landed, MIDDLE_BAND) fixed forgetting almost perfectly (0.678 -> 0.011) using the brain-correct segregated-dual-store + one-way-replay architecture, but **transfer stayed at exactly 0.000**. All 5 independent literatures (CLS neuro, cognitive-science schema theory, VSA/HDC bundling math, modern ML continual-learning surveys, info-theory/stability-plasticity) converge on why: item-level replay is a retrieval-robustness operation, not an abstraction operation. No substrate cell (of ~80 landed CL-adjacent cells) has ever tested generalization to a novel, previously-unseen item sharing learned relational structure — that is the actual definition of "schema formation" and it is untouched.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time; this hand-off is a research-lane deliverable, not a queue-priority override.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHOR + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands (already drafted below as a STARTING proposal from the research drill, not binding), queue choice, smoke profile, FULL profile. exp_dev may revise the pre-reg numbers below; they are a research-lane draft, not a locked spec.

---

## Anchor candidates (rank-ordered)

### 1. `schema_bundle_structural_transfer_v1` (PRIMARY — new capability test, never built)

- **Anchor pointer:** `notes/research_5x_drill_continual_learning_spec_and_brain_mechanism_2026-07-05.md` Section E.3-E.4.
- **Substrate-product reading:** this is the FIRST cell that would test genuine schema-formation (train on relation-type R episodes, hold out novel entity pairs of the same relation-type, measure structural-transfer accuracy above random baseline) rather than forgetting-prevention/retrieval-robustness (which ~80 prior cells already cover and which the MVP no-forgetting bar has cleared 4x independently: a8, CRISPR, distshift v430, c3).
- **Proposed mechanism (research draft, exp_dev may revise):** bundle (Hebbian sum/superposition) M bound (role_subject⊗entity_A, role_object⊗entity_B) episode vectors for one relation-type into a schema vector, held in a SEPARATE, one-way-fed schema store (reuse the segregated dual-W harness from `exp_substrate_c3_segregated_dual_W_spectrum_replication_v1` — do not write the schema store back into the episodic store). Query: bind a NOVEL entity (never in the training M) to role_subject, read against the schema store, check if the correct (never-seen) entity_B-shaped answer is recovered above random baseline.
- **Draft pre-reg (research proposal, exp_dev owns final numbers):**
  - HARD-PASS: structural transfer accuracy - random_baseline >= 0.30, cv <= 0.30 across >= 3 seeds, AND a shuffled-relation control arm shows transfer accuracy - random_baseline <= 0.05 (discriminates genuine structure from codebook-collision artifact).
  - HARD-FAIL: transfer accuracy - random_baseline <= 0.05 on the real (unshuffled) arm.
  - MIDDLE_BAND: gain in (0.05, 0.30) — real but small; sweep M (episode count feeding the bundle).
- **Corpus:** reuse already-ingested FB15k-237 or ConceptNet relation-typed atoms (substrate already has these ingested — `n8_conceptnet_ingest_pre_reg`, FB15k-237 U1 cert 584 lineage) — no new ingest required, this is pure algebra on existing atoms.
- **Why now:** two landed MIDDLE_BAND results (`crispr_plasticity_slab_replay_v1`, `c3_segregated_dual_W_spectrum_replication_v1`) are sitting un-actioned; per USER-standing negative/partial-result routing discipline, this hand-off IS the 2x-revival — and the convergence synthesis says the right revival axis is NOT "tune R higher on the existing item-replay cells" but "build the bundling-based schema mechanism that neither existing cell tests."
- **P_deflated = 0.32** (novel-synthesis cap 0.50 binding, further deflated — VSA literature explicitly flags multi-schema/bundling interference as an open, unsolved problem; this is a first attempt at this exact composition on substrate's Hebbian-superposition arithmetic).

### 2. `schema_multi_relation_interference_v1` (CONDITIONAL on #1 HARD-PASS)

- **Anchor pointer:** same research note, Prediction 2 (Section E.4).
- **Substrate-product reading:** tests whether TWO different relation-types bundled into two separate schema vectors coexist without cross-contamination — the exact failure mode the VSA/HDC literature (LifeHD, Kleyko et al.) flags as unsolved and structurally avoided in published systems by keeping schemas in separate slots rather than one shared bundle space.
- **Draft pre-reg:** HARD-PASS: cross-contamination rate <= 0.05. HARD-FAIL: cross-contamination rate >= 0.20 (would mean per-relation separate schema slots are required, per the LifeHD engineering answer, rather than one shared bundle space).
- **P_deflated = 0.25** (literature leans toward interference being likely; this is the more uncertain prediction).
- **Only ship if #1 clears HARD-PASS** — no point stress-testing multi-schema coexistence if single-schema bundling doesn't work at all.

### 3. `crispr_long_horizon_J20_v1` (MVP-hardening, cheap, stretch/parallel candidate)

- **Anchor pointer:** `notes/research_drill_continual_learning_CRISPR_regime_map_2026-07-01.md` rank-3 cell (already fully speced there: J=20 phases, M=400, N=4096, 3 seeds, append-only arm only; HARD-PASS = forget_p1 <= 0.01 at J=20; HARD-FAIL = routing_acc < 0.80).
- **Substrate-product reading:** this is NOT part of the schema-formation gap — it is closing out the MVP's long-horizon coverage hole (only J=5 tested so far). Cheap (~2 CPU-hr), already fully pre-registered by a prior drill, just never dispatched. Low-risk queue-filler alongside #1.
- **P_deflated = 0.55** (per the 07-01 drill; append-only is structurally partition-clean, main risk is routing accuracy at 20 slabs, not forgetting itself).

---

## Context pointers (paths, not summaries)

- `notes/research_5x_drill_continual_learning_spec_and_brain_mechanism_2026-07-05.md` — this drill's full memo (headline, A-F spec, citations).
- `data/exp_crispr_plasticity_slab_replay_v1/metrics.json` — landed MIDDLE_BAND, item-level replay result (transfer_final=0.125 best case, cv=0.40) — the "wrong axis" result this hand-off routes past.
- `data/exp_substrate_c3_segregated_dual_W_spectrum_replication_v1/metrics.json` — landed MIDDLE_BAND, forgetting=0.011 vs FUSED=0.678, transfer=0.000 — the core empirical fact motivating anchor #1.
- `notes/research_drill_continual_learning_CRISPR_regime_map_2026-07-01.md` — prior regime map (anchor #3 is fully speced there already).
- `notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md`, `notes/research_continual_learning_architectural_revival_2x_drill_2026-06-24.md` — prior drill chain this converges against.
- U1 / FB15k-237 / ConceptNet ingest certs (CERT 584, M1_HYPERNYM CERT 573) — existing relation-typed corpus for anchor #1's episodes, no new ingest needed.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands before smoke (draft numbers above are a research-lane starting point; exp_dev owns the final pre-reg).
- Self-test per [[feedback-formula-selftests]].
- Multi-seed FULL on smoke clearance; paired-trials discipline for the shuffled-control arm (anchor #1).
- Substrate-only-decode gate: zero LLM calls (this is pure vector algebra on already-encoded atoms).
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`; POST-SHIP REMOTE VERIFY.
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: anchor name, N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), ETA, smoke profile, FULL profile, corpus specifics (which relation-type(s) from FB15k-237/ConceptNet). The research drill's pre-reg numbers above are a STARTING proposal grounded in the lit-scan calibration, not a locked spec — exp_dev may revise based on cell-authoring realities (e.g. codebook size available for the chosen relation-type, actual episode counts on disk). If exp_dev judges anchor #1's mechanism needs a different first-pass implementation (e.g., starting with a single hand-picked high-count relation-type before generalizing), that is exp_dev's call.

---

## Filed by

Research (Opus synthesis, 5x convergence drill: 5 parallel Sonnet lit-scan sub-agents + substrate-internal mining of ~6 prior CL drill notes + 2 landed MIDDLE_BAND metrics.json reads), 2026-07-05. Hand-off ready for exp_dev pickup.
