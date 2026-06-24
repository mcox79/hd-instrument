# exp_dev hand-off — research: substrate-as-LM test methodology audit (2x)

**Filed-by:** Research (Opus 4.7-1M)
**Date:** 2026-06-23
**Trigger:** USER 2026-06-23 methodology-audit drill — `notes/research_drill_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md`
**Pause state:** check `data/orchestrator_paused.flag` before any dispatch (per [[feedback-orchestrator-pause-experiments]])

Per [[feedback-no-experiment-design-in-prompts]] — this hand-off provides anchor candidates + substrate-product reading + context pointers; exp_dev authors the cell and pre-reg.

---

## Anchor candidates (rank-ordered)

### 1. PRIMARY: `substrate_as_lm_revised_harness_v1` (tier-1; cheap decisive)

**Anchor pointer:** `notes/research_drill_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md` sections L3.1, L4, and "Cheap decisive test (full pre-reg, restated)"

**Substrate-product reading:** **THE cheap decisive test for the methodology audit.** Reuses entire `fresh_W_bpc_per_encoder_v2` infrastructure (V=4000, N_DIM=8192, N_TRAIN=100000, 3 seeds, 4 encoder arms); changes ONLY the measurement layer. Adds per-position logit saving + 6 measurement modes M1-M6:
- M1: top-1 accuracy per arm
- M2: top-5 accuracy per arm
- M3: top-20 accuracy per arm
- M4: per-query selection-mixer BPC (replaces log-linear mixer)
- M5: bits-per-substrate-Poisson-shuffle (neuroscience-standard baseline)
- M6: log-linear lambda profile (CONTROL — must reproduce lambda=0 collapse from fresh_W_v2)

**Tier hint:** tier-1 chain-grade-eligible IF M1+M2+M4 pass with cv <= 0.10 across 3 seeds. New `hdlab/` primitive: `substrate_lm_topk_ranker(V, N_DIM, encoder)` if HARD_PASS.

**Why-now:** USER explicitly directed methodology audit; 7+ prior substrate-as-LM cells all collapse to lambda=0 = unigram floor; diagnosis says 70% of the gap is wrong-metric (BPC penalizes top-1-correct miss-mass exponentially). Cheap (~100 min GPU) AND high-leverage (unblocks 3+ prior HARD_FAILs if HARD_PASS).

**Pre-reg HARD_PASS:** ANY semantic encoder arm clears M1 (top-1 >= unigram top-1 + 0.05) AND M2 (top-5 >= unigram top-5 + 0.10) AND M4 (selection_bpc <= unigram_bpc - 0.05) with cv <= 0.10
**Pre-reg HARD_FAIL:** NO encoder arm clears M1 AND M5 (Poisson-shuffle gain) < 0.05 bits/token
**P_deflated:** 0.65 (asymmetric per USER brain-existence-proof directive; novel-synthesis cap relaxed to 0.65)

### 2. SECONDARY: cross-cell reclassification — apply revised harness to existing saved data

**Anchor pointer:** same drill, section L5 (table of 7 prior HARD_FAILs)

**Substrate-product reading:** if the primary cell's per-position logits can be saved AND the same measurement code can be applied to 3 strong reclassification candidates' saved data:
- `data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json` (sub_top1=0.445 >> unigram 0.276; M1 likely already HARD_PASS)
- `data/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1/metrics.json` (bpc_best=7.864; M1+M2 reanalyzable if logits saved)
- `data/exp_fresh_W_bpc_per_encoder_v2/metrics.json` (12/12 lambda=0; strongest reclassification candidate)

**Tier hint:** tier-2 measured-mechanism; not chain-grade by itself but lifts prior cell's classifications from HARD_FAIL → HARD_PASS/MIDDLE_BAND under bias-removed metrics.

**Why-now:** doubles the leverage of primary cell — if logits weren't saved in those cells, re-dispatch with logit-save flag (~30 min wall per cell). Per Fix #21 (poll for filesystem landings) + Fix #26 (pre-dispatch verify-the-referent gate), check `recent_landings.jsonl` and `atoms.jsonl` first to avoid re-dispatching cells whose data is already sufficient.

### 3. TERTIARY: composition with PC1 mechanism fix (deferred to primary HARD_PASS)

**Anchor pointer:** `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md` (PC1 hierarchical-bigram) + this drill's revised harness composition

**Substrate-product reading:** if revised harness HARD_PASSes on existing Path A v3 substrate, queue PC1 (hierarchical rank-stacking from prior drill) + revised harness (correct measurement). Composition tests whether mechanism fix + correct measurement together break the unigram bar AND approach bigram.

**Tier hint:** tier-1 chain-grade-eligible if M1+M2+M4 pass at BPC <= 7.500 (the prior drill's HARD_PASS bar with revised harness)

**Why-now:** DEFERRED — only dispatch after primary cell verdict. If primary HARD_FAILs (P=0.20), PC1 mechanism fix is moot under wrong-metric. If primary HARD_PASSes, PC1 composition becomes top-priority next cycle.

---

## Context pointers (file paths only; no summaries per [[feedback-overhead-reduction]])

- `notes/research_drill_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md` (parent research note this drill; full diagnosis + L3 spec + L4 cell-design)
- `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md` (prior PC1/PC2 mechanism-side drill; complement to this measurement-side drill)
- `notes/research_2x_revival_ca3_lm_HF_2026-06-23.md` (ca3 genuine mechanism failure; not harness-rescuable)
- `notes/orchestrator_to_skunkworks_N1v3_FAIR_BPC_real_top1_unigram_level_perplexity_2026-06-21.md` (PRIOR USER-FACING framing already identified the top-1-vs-distribution distinction)
- `notes/skunkworks_to_research_cc_all_LANDED_VET_path_c_armA_projected_HARD_FAIL_and_path_b_mkn_MIDDLE_BAND_MM_2026-06-22.md` (MKN smoothing-class lever exhausted at 6.1% gap closure; confirms decode-side BPC ceiling under current harness)
- `data/exp_fresh_W_bpc_per_encoder_v2/metrics.json` (SMOKING GUN: 12/12 lambda=0 across 4 encoders x 3 seeds; bpc_per_lambda_test monotonic)
- `data/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1/metrics.json` (parent baseline)
- `data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json` (strongest reclassification candidate; sub_top1=0.445)
- `experiments/exp_fresh_W_bpc_per_encoder_v2.py` (source code to fork for revised harness; only measurement layer changes)
- `hdlab/whitening.py`, `hdlab/sequence_memory.py`, `hdlab/char_trigram_encoder.py` (existing primitives; unchanged)

---

## Contract section

**Per exp_dev contract:**
- run `python tools/predispatch_check.py substrate_as_lm_revised_harness_v1` per Fix #26 before any spawn
- pre-flight smoke gate (must reproduce M6 lambda=0 collapse from fresh_W_v2 as sanity-check)
- Fix #28 verify-per-arm metrics (NOT verdict_msg) — read per-arm M1-M6 individually from per_unit before any cross-cell reclassification claim
- Fix #14 spawn budget <= 3 in-flight; if at ceiling, defer per Fix #27
- substrate_only_decode_gate = TRUE (zero LLM forward calls; same as fresh_W_v2)
- run_mode = 'full' (not smoke) for primary HARD_PASS / HARD_FAIL bands
- 3 seeds [7, 17, 23] (consistency with fresh_W_v2 lineage)
- cite this hand-off + parent research note in cell prereg notes
- post-ship REMOTE VERIFY (per Fix #21 filesystem-poll)
- commit prereg to origin/main BEFORE remote dispatch (per `[[feedback-commit-prereg-notes-before-remote-dispatch]]`)

**Pause state:** check `data/orchestrator_paused.flag` first. If paused, queue this hand-off for resume; do NOT dispatch.

**Routing:**
- Primary cell route: GPU (overnight_queue) per Fix #22 (matmul + per-position logits at V=4000 x n_test=7886 x 4 arms = matmul-bound, GPU-appropriate); ~100 min wall
- Secondary (reclassification): local_cpu_queue or laptop CPU; pure measurement reanalysis if logits available (~30 min per cell)

---

## Autonomy declaration

exp_dev decides:
- Exact cell name (`substrate_as_lm_revised_harness_v1` is suggested but not load-bearing)
- Whether to fork `experiments/exp_fresh_W_bpc_per_encoder_v2.py` or author from scratch
- Smoke gate config (smaller V or N_TRAIN per [[feedback-long-cells-must-checkpoint-resume-restartable]])
- Whether to bundle primary + secondary into one cell or two
- Pre-reg final HARD_PASS / HARD_FAIL precise numerical bands (this hand-off provides starting bands; exp_dev tightens based on dev-set calibration)
- tau hyperparameter sweep for selection-mixer (this hand-off suggests {0.05, 0.1, 0.2, 0.3, 0.5}; exp_dev finalizes)

Research does NOT decide:
- Implementation language (Python is project default)
- Specific torch.cuda + batched ops (per Fix #24 GPU dispatch must actually use GPU)
- Schema-VET checklist items (Skunkworks owns)

---

## What this hand-off does NOT include

- The full implementation code (exp_dev authors)
- Decision on whether to also re-run substrate_as_lm_composed_primitives_GPU_v1 with logit saving (the 3/4 load-failed cell; deferred to exp_dev judgment)
- Cell timing budget per seed (exp_dev measures via smoke-VET per Fix #17)
- Decision on whether HARD_PASS triggers product-positioning pivot (USER's call after verdict lands)
