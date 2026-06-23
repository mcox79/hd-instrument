# exp_dev hand-off — research: 2x revival CA3 LM HARD_FAIL

**Filed by:** Research (Opus 4.7 / 1M)
**Date:** 2026-06-23
**Trigger:** `notes/research_2x_revival_ca3_lm_HF_2026-06-23.md` — root-cause diagnosis of CA3 LM smoke HF + 2 pre-registered revival angles.
**Pause state:** check `data/orchestrator_paused.flag` at pickup; defer if paused.

**Per [[feedback-no-experiment-design-in-prompts]]:** the cell is fully specified in the research note's "Cell-design implications" section + falsifiable bands; exp_dev applies its own envelope-fail-bands check + smoke gate per its role contract. Pre-reg below is the proposed scaffold only.

---

## Anchor candidates (rank-ordered)

### #1 (PRIMARY) — `ca3_revival_no_cleanup_no_position_v1`
- **Anchor pointer:** `notes/research_2x_revival_ca3_lm_HF_2026-06-23.md` Revival #1 section
- **Substrate-product reading:** first substrate-LM mechanism to beat UNIGRAM floor at smoke; recurrent autoassoc step over Path A's W matrix (Hebbian); no position carriers; no cleanup against vocab encoder. Biology-faithful per de Camargo PeerJ 2018.
- **Tier hint:** T2 (measured-mechanism candidate); chain-grade-eligible if HARD_PASSes at smoke + full + cv<=0.10 across 3 seeds.
- **Why-now:** CA3 family is at 5th attempt against substrate-LM; predecessor research `research_5x_deeper_substrate_LM_gap_2026-06-23.md` pre-registered PC2 as higher-risk; this revival removes the three failure points (position bind, cleanup-vs-vocab, elementwise-on-non-bipolar) in one cheap cell. Cost: ~1min laptop CPU. Decisively falsifies the CA3 family OR opens substrate-LM-via-recurrent-step.

### #2 (CONDITIONAL on #1 not-HARD_FAIL) — `ca3_revival_dedicated_per_position_W_v1`
- **Anchor pointer:** `notes/research_2x_revival_ca3_lm_HF_2026-06-23.md` Revival #2 section
- **Substrate-product reading:** K_POS dedicated W matrices (one per position class) instead of shared-W + position-tag-binding. No iterative cleanup. No elementwise bind.
- **Tier hint:** T3 (conjecture; structurally weaker than #1 per parameter-budget analysis in research note).
- **Why-now:** queue only if revival #1 HARD_PASSes (would test additive composition) or revival #1 MIDDLE_BANDs (would test orthogonal contribution). If revival #1 HARD_FAILs, SKIP this one — substrate-as-LM CA3-family is closed and the next pivot per research note is PC1 (Eugenio hierarchical-bigram), NOT another CA3 variant.

---

## Context pointers (file paths; no summaries)

- `notes/research_2x_revival_ca3_lm_HF_2026-06-23.md` — the deliverable; intuitive diagnosis + cell spec + pre-reg bands
- `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md` — predecessor research; predicted PC2 (CA3) risk
- `notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md` — alternative cleanup angles (OMP, multi-bump CAN) for follow-up
- `experiments/exp_ca3_sequence_prediction_lm_smoke_v1.py` — parent cell source (revival #1 reuses harness)
- `data/exp_ca3_sequence_prediction_lm_smoke_v1_localsmoke/metrics.json` — parent HF metrics; baseline for sanity
- `hdlab/iterative_attractor.py` — DO NOT use in revival #1 (root cause of failure)
- `hdlab/sequence_memory.py` — c3 HARD_PASS primitive; reference for working substrate sequence binding
- `hdlab/char_trigram_encoder.py` — encoder used in parent CA3 cell; element-wise bind on these is destructive
- `notes/exp_dev_att1_iterative_attractor_pre_reg_2026-06-22.md` — att1 primitive pre-reg; the in-HF cleanup family

---

## Contract section

- **Substrate-only-decode:** zero LLM calls at inference (assert on exit, per parent cell convention).
- **CAN-FAIL discriminator:** UNIGRAM_BASELINE + PATH_A_RAW must reproduce parent cell values within 0.01 BPC (else implementation bug, NOT mechanism rejection).
- **HARD_PASS:** best ARM_CA3_RECURRENT BPC <= 10.253 (beats UNIGRAM) AND cv <= 0.10 AND lift over PATH_A_RAW >= +0.50 bits.
- **HARD_FAIL:** best ARM_CA3_RECURRENT BPC >= 11.145 (no benefit over PATH_A_RAW).
- **MIDDLE_BAND:** 10.253 < BPC < 11.145 → partial; queue follow-up with calibrated-T sweep at finer granularity + larger N_DIM.
- **Self-test (selftest first; selftest fail = no run):** (a) recurrent-step preserves Path A behavior at T=0 (zero iteration → identical to PATH_A_RAW); (b) recurrent-step at T=1 with beta=infinity → argmax-Pull (equivalent to single-step cleanup, sanity); (c) UNIGRAM/PATH_A re-baselines match parent.
- **Smoke gate:** ~1min laptop CPU; numpy only; same scale as parent (V=4000 N_DIM=4096 N_TRAIN=10000 seeds=[7,17,23]).
- **Post-ship REMOTE VERIFY:** N/A (laptop CPU; no remote dispatch needed for smoke scale).
- **Cert-class eligibility:** smoke is informative for HF/HP routing only; full N_TRAIN=100k GPU queue only if smoke not-HARD_FAIL (matches parent cell's queue gating).

## Autonomy declaration

exp_dev owns:
- Final cell name and file path (suggested `experiments/exp_ca3_revival_no_cleanup_no_position_v1.py`)
- Exact beta and T grid choice (research suggests beta in {2.0, 8.0, 32.0}, T_ITER in {2, 4}; exp_dev refines per envelope-fail-bands)
- Self-test set (research suggests 3 minimum; exp_dev adds as needed for formula-selftests discipline)
- Whether to also ARM_PATH_A_TEMP-only as a stand-alone calibration control or merge into the CA3_RECURRENT family
- All standard exp_dev disciplines (checkpoint-per-seed, atexit synthesizer, --self-test gate, SIGTERM handler, queue routing)

Research declares no interest in re-arbitrating cell-design choices once handed off. Per [[feedback-no-experiment-design-in-prompts]] research stops at "Cell-design implications" + falsifiable bands + cost envelope.
