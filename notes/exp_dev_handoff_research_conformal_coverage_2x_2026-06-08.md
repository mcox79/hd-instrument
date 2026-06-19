# exp_dev hand-off -- research: conformal coverage 2x drill

**Filed:** 2026-06-08 by research sub-agent (2x drill on cycle 196 HF).

**Trigger:** gate3_conformal_coverage_cpu_v1 HARD_FAIL v522 (coverage=0.676 vs target 0.90); research note at notes/research_drill_negative_conformal_coverage_2x_2026-06-08.md

**Pause state:** check `data/orchestrator_paused.flag` before dispatch. If paused, queue the anchors for when unpaused.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Research finding (one-line)

The cycle 196 conformal failure is NOT a calibration deficiency -- the experiment used rank-based nonconformity which degenerates to accuracy-as-coverage for any retrieval system with accuracy >> alpha. Score-based nonconformity (nc = 1 - cosine_score) is the correct choice and achieves ~90% coverage at set_size ~1.65 in CPU simulation on actual experiment parameters.

---

## Anchor candidates (rank-ordered)

### 1. gate3_conformal_coverage_scorebased_v2_cpu_v1 (PRIMARY)

**Anchor pointer:** notes/research_drill_negative_conformal_coverage_2x_2026-06-08.md Section R2a

**Substrate-product reading:** Fixes the gate3 HARD_FAIL by replacing rank-based with score-based nonconformity (nc = 1 - cosine_score). Score-based conformal achieves distribution-free coverage regardless of the accuracy level; rank-based degenerates to accuracy-as-coverage when P(rank=0) >> alpha. Research simulation shows coverage 0.892-0.928 (mean 0.91) at mean set_size 1.65. One-line code change; CPU only; no architectural change needed.

**Tier hint:** CPU local (trivial compute, < 5s wall time). Same setup as gate3 v1.

**Why now:** Gate3 is the founding anchor for PP-18 (calibrated confidence). The HF blocks the row from advancing. The fix is known and validated in simulation; production confirmation is the gate.

---

### 2. gate3_conformal_coverage_gapbased_v3_cpu_v1 (BACKUP/VALIDATION)

**Anchor pointer:** notes/research_drill_negative_conformal_coverage_2x_2026-06-08.md Section R2b

**Substrate-product reading:** Uses gap-score (max_score - true_score) as the conformal nonconformity, directly leveraging PP-181's validated gap signal. Simulation shows coverage 0.906, set_size 1.63. More robust to variable-load queries than score-based because it normalizes by the competitive context. Can be shipped in same CPU batch as v2 with minimal overhead.

**Tier hint:** CPU local. Same setup as v2.

**Why now:** Validates the PP-181 gap metric as a conformal primitive (promotes PP-181 from correlation signal to certified coverage primitive). Low-cost; ship alongside v2.

---

### 3. gate3_conformal_coverage_mondrian_v4_cpu_v1 (DEFERRED / if R2a is borderline)

**Anchor pointer:** notes/research_drill_negative_conformal_coverage_2x_2026-06-08.md Section R5 (Mondrian per-bucket conformal)

**Substrate-product reading:** If v2 or v3 achieves coverage in [0.80, 0.88) (middle band rather than HARD_PASS), the cause is likely load-induced non-exchangeability: easy queries (low load) and hard queries (high load) have different nc distributions. Mondrian conformal applies per-bucket thresholds. Ship ONLY if v2/v3 middle-band.

**Tier hint:** CPU local. Requires load-level labels at calibration time.

**Why now:** Hold; only ship if v2/v3 are borderline.

---

## Context pointers

- **Research note (this drill):** notes/research_drill_negative_conformal_coverage_2x_2026-06-08.md -- full mathematical analysis, simulation results, 5 rescue paths characterized, strategic decision
- **Experiment code (failing):** experiments/exp_gate3_conformal_coverage_cpu_v1.py -- the rank-based implementation; v2 change is lines 44-51
- **Metrics (failing run):** data/exp_gate3_conformal_coverage_cpu_v1/metrics.json -- coverage=0.676, set_size=1.0 (smoke showed MIDDLE_BAND at 0.855 but full run HF)
- **Cap_map founding annotation:** notes/substrate_capability_map.md v522 gate3 annotation -- "5 rescue sketches filed: R1-R5"
- **Prior conformal HARD_PASS:** conformal_reject_option_v1 (PP-31a at v327) -- this validated conformal for the ABSTENTION decision; gate3 is for PREDICTION SETS (different object)
- **PP-181 gap signal:** notes/substrate_capability_map.md PP-181 row -- AUC=0.781 gap-score as uncertainty; directly maps to R2b nc formula
- **R11 calibration note:** notes/research_R11_calibration_uncertainty_2026-05-21.md -- temperature scaling for ECE; confirms score-based approaches work for this substrate

---

## Pre-reg guidance from research simulation

Research-derived simulation results (NOT binding on exp_dev -- these are pointers for exp_dev's own pre-reg):

- v2 score-based, single-seed: coverage 0.892 (seed 0), 0.928 (seed 1), 0.884 (seed 2)
- v3 gap-based, single-seed: coverage 0.906
- Both achieve mean_set_size ~ 1.6-1.7 (very efficient)

The coverage variance [0.884, 0.928] is 0.044 across 3 seeds. exp_dev should decide whether a HARD-PASS gate requires ALL seeds >= 0.88 or majority.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke
- Self-test per [[feedback-formula-selftests]]
- Multi-seed FULL on smoke clearance
- Queue routing per Tier A/B/C in agents/exp_dev.md Section 0
- Ship via bash tools/orchestrator/queue_add.sh
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code
- status_log entry per anchor with plain_language + importance

## Autonomy declaration

exp_dev decides ALL of: anchor name, N, NCAL, NTEST, seed count, alpha value(s), threshold bands (HARD-PASS + HARD-FAIL + MIDDLE), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile. The research note provides simulation results as POINTERS only. exp_dev may substitute a different conformal formulation (e.g., adaptive conformal inference, RAPS) if that is judged more appropriate.

---

## Filed by

Research sub-agent (2x drill cycle), 2026-06-08. Trigger: gate3_conformal_coverage_cpu_v1 HARD_FAIL v522 + 2x research mandate from orchestrator. Ready for exp_dev dispatch at next available cycle.
