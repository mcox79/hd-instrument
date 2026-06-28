# exp_dev hand-off — research: schema-driven inference primitive for Stage 3

**Filed-by:** research (Opus 4.7 1M)
**Filed:** 2026-06-27
**Trigger:** Drill `notes/research_drill_2x_schema_driven_inference_stage3_2026-06-27.md` produced 3 ranked dependency-free cells that pivot from the 4x extraction-side HARD_FAILs of today (BCM zero-init / Tonegawa K=100 / Tonegawa K=500 / Hopfield consolidation v2) to top-down schema instantiation.
**Pause state:** check `d:/AI/hd-instrument/data/orchestrator_paused.flag` before ship.
**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names anchors + tier hints + WHY-NOW; exp_dev decides cell-author code + smoke runs + dispatch routing.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (rank-1, ship-FIRST) — `cortex_schema_instantiation_context_prior_v1`

- **Source drill pointer:** `notes/research_drill_2x_schema_driven_inference_stage3_2026-06-27.md` § TOP-1
- **Substrate-product reading:** first schema-INFERENCE primitive (Stage 3 advances from "extraction-CHAIN_GRADE only" to "extraction + inference both CHAIN_GRADE"). Unlocks M3 milestone glass-box conversational reasoning ("what does this novel bird eat?") via Gilboa-Moscovitch vmPFC schema-instantiation mechanism.
- **Tier hint:** P_deflated = 0.50 (at novel-synthesis cap; brain-existence-proof bump applies; mechanism orthogonal to today's 4 HARD_FAILs). HARD_PASS would be MEASURED_MECHANISM tier minimum; chain-grade if discriminators clean.
- **Why-now:**
  - 4 schema-extraction cells HARD_FAILed today (BCM, Tonegawa v2, Tonegawa v4, Hopfield-consolidation v2); the extraction-side has 5+ negative cells — pattern is structural per substrate cone geometry. Inference-side is UN-TESTED.
  - Existing `schema_driven_proof_step_inference_v1` prereg is BLOCKED on `lean_mathlib_ingest_v1` (no data dir) + `sub_atom_token_stream_encoder_v2_real_mathlib` (RUNNING@375s). This cell is DEPENDENCY-FREE — uses synthetic concept-hierarchy task (8 schemas × 6 typed slots × 20 exemplars).
  - All required substrate primitives are CHAIN_GRADE (ultrametric clustering / HRR bind/unbind cert-atom-586 / refuse-gate V_REL=256 / partition routing).
  - ~20 lines new code total (slot-unbind + refuse-gate composition; rest is existing primitives).
- **Compute:** smoke 30 min CPU laptop (with full-N preview arm per [[feedback-discriminator-must-survive-scale]]); full 4-6 CPU-hr remote_cpu via hdi_orchestrator (HRR bind/cleanup is CPU-friendly per [[feedback-fix24]]).

### ANCHOR 2 (rank-2; complementary, parallel-ship if budget) — `cortex_schema_MACFAC_two_stage_retrieval_v1`

- **Source drill pointer:** `notes/research_drill_2x_schema_driven_inference_stage3_2026-06-27.md` § TOP-2
- **Substrate-product reading:** two-stage retrieval (MAC sparse-dotprod + FAC structural rerank) — provides SCALABLE schema-inference for large schema banks. 30-year-old Gentner-Forbus architecture; direct VSA mapping.
- **Tier hint:** P_deflated = 0.45. Mechanism ORTHOGONAL to ANCHOR 1 (retrieval architecture vs context-bound prior). If both HARD_PASS → independent dual evidence + compose-able for production.
- **Why-now:** if ANCHOR 1 fails, MAC/FAC is the next architectural rung; if ANCHOR 1 succeeds, MAC/FAC provides retrieval-front compose. Sparse-bipolar primitive already CHAIN_GRADE; ~40 lines new code (MAC sparse-index + FAC structural-match scoring).
- **Compute:** smoke 30 min; full 3-5 CPU-hr remote_cpu.

### ANCHOR 3 (rank-3; CHEAP upper-bound probe; ship-FIRST as fast falsifier) — `cortex_schema_exemplar_bayes_importance_sample_v1`

- **Source drill pointer:** `notes/research_drill_2x_schema_driven_inference_stage3_2026-06-27.md` § TOP-3
- **Substrate-product reading:** Bayesian posterior over slot-fillers via exemplar importance-sampling (Shi-Griffiths-Feldman 2010 mathematical equivalence proof). Tests whether substrate's cosine kernel is RICH ENOUGH to support posterior-style inference at all.
- **Tier hint:** P_deflated = 0.38 (LOWER but CHEAPEST). Acts as falsification probe: if K-nearest exemplar-Bayes HARD_FAIL, then ANCHOR 1+2 are unlikely to PASS (cone-geometry confound). If HARD_PASS, ANCHOR 1+2 with structural binding should pass at HIGHER accuracy.
- **Why-now:** cheap rapid probe (~15 lines new code; 20 min smoke; 2-3 CPU-hr full). Ship in parallel with ANCHOR 1 as falsifier. RUN-FIRST candidate if you must pick only one.

---

## Context pointers (file paths; not summaries)

- Source drill: `d:/AI/hd-instrument/notes/research_drill_2x_schema_driven_inference_stage3_2026-06-27.md`
- Prior extraction-side HARD_FAILs (4): 
  - `d:/AI/hd-instrument/data/exp_gap3_cls_two_tier_BCM_slow_replay_v1/metrics.json`
  - `d:/AI/hd-instrument/data/exp_cortex_schema_tonegawa_sparse_ensemble_v2/metrics.json`
  - `d:/AI/hd-instrument/data/exp_tonegawa_v4_permutation_bundled_smoke/metrics.json`
  - `d:/AI/hd-instrument/data/exp_gap3_cls_two_tier_HOPFIELD_consolidation_v2_regime_fix/metrics.json`
- BCM forensics + lit-anchored rescue recipe: `d:/AI/hd-instrument/notes/research_drill_bcm_slow_learning_at_chance_3x_2026-06-27.md`
- Tonegawa fairness-question hand-off: `d:/AI/hd-instrument/notes/exp_dev_to_research_tonegawa_v2_smoke_HARD_FAIL_fairness_design_question_2026-06-27.md`
- Cortex schema integration drill (complementary; this morning): `d:/AI/hd-instrument/notes/research_drill_2x_cortex_schema_integration_2026-06-27.md`
- Multihop schema-chunking drill (orthogonal; this morning): `d:/AI/hd-instrument/notes/research_drill_brain_multihop_M1_schema_chunking_cortex_3x_2026-06-27.md`
- Existing dependency-blocked prereg (COMPLEMENT, not duplicate): `d:/AI/hd-instrument/preregs/2026-06-27_schema_driven_proof_step_inference_v1.md`
- Substrate primitive references (CHAIN_GRADE for composition):
  - HRR bind/unbind (cert-atom-586): `d:/AI/hd-instrument/hdlab/` (sequence_binding module)
  - Refuse-gate V_REL=256: `d:/AI/hd-instrument/hdlab/refuse_gate.py`
  - Ultrametric clustering: `d:/AI/hd-instrument/hdlab/ultrametric.py`
  - Partition routing: `d:/AI/hd-instrument/hdlab/partition.py`

---

## Contract

exp_dev decides:
- Final cell anchor names (suggested prefixes above; OK to abbreviate)
- N_DIM (drill suggests N=4096 full; N=1024 smoke with full-N preview arm)
- Smoke regime (drill suggests between-schema cosine 0.35; slot-mask 50%; K=8 schemas; 20 exemplars/schema)
- Per-arm code (drill provides 5-arm spec for ANCHOR 1; 4-arm for ANCHOR 2 + ANCHOR 3)
- Ship-order: drill recommends ANCHOR 3 + ANCHOR 1 in parallel (ANCHOR 3 is cheap falsifier; ANCHOR 1 is rank-1 mechanism); ANCHOR 2 after results land if ANCHOR 1 doesn't HARD_PASS
- Queue routing per [[feedback-cell-author-smoke-and-dispatch-route-via-orchestrator-for-heavy-cells]]: smoke on laptop CPU; full via hdi_orchestrator → remote_cpu (HRR bind/cleanup is CPU-friendly per [[feedback-fix24]]).

Pre-registered HARD-PASS / HARD-FAIL / MIDDLE_BAND bands per cell are in the drill note § TOP-1 / TOP-2 / TOP-3.

Fairness floor (mandatory across all 3 cells):
1. between-schema cosine in [0.30, 0.45] regime (NOT the 0.076 ultrametric-smoke regime or the K=100 over-easy regime that fairness-saturated Tonegawa v2).
2. Separate W per arm (no shared bind-keys / cluster matrix); separate W_content from W_structural for ANCHOR 2.
3. Verify-the-referent: report slot-inference accuracy PER SLOT-TYPE (not aggregate); inflate-aware metric per [[feedback-experiment-bias-master-checklist]] N.
4. Smoke FIRES discriminator per [[feedback-three-smoke-disciplines]] (mechanism vs baseline > 5% spread at smoke OR halt).
5. CARDINALITY_OK pre-reg per cell (drill provides EXPECTED_N_UNITS).
6. ANY arm > 0.95 absolute → FAIRNESS_VIOLATION; ANY mechanism within +0.05 of best baseline → HARD_FAIL.

---

## Autonomy declaration

Research provides: hand-off pointers + tier hints + WHY-NOW + 3 ranked anchor candidates + pre-reg fairness floor + composition pointers.

Research does NOT specify:
- Cell-author code (exp_dev's call)
- Smoke runtime / shape (exp_dev's call within drill's smoke-budget hints)
- Queue choice (hdi_orchestrator's call per fix24/fix25)
- Final cell anchor names (exp_dev's call)
- Whether to bundle as one multi-arm cell or three cells (exp_dev's call; drill writes them as 3 separable cells but bundling is acceptable if smoke gates pass for all 3)

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off is the research → exp_dev contract surface; exp_dev owns the implementation.

---

## File reference list (for exp_dev pickup verification)

- This hand-off: `d:/AI/hd-instrument/notes/exp_dev_handoff_research_schema_driven_inference_stage3_2026-06-27.md`
- Source drill: `d:/AI/hd-instrument/notes/research_drill_2x_schema_driven_inference_stage3_2026-06-27.md`
