# exp_dev hand-off -- research: baseline 7.22 vs 7.30 encoder-ablation rescue

Filed-by: research sub-agent (Opus 4.7 1M)
Trigger: d:/AI/hd-instrument/notes/research_surprise_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md
Date: 2026-06-24

Pause state block: check data/orchestrator_paused.flag before dispatching any anchor.
Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT + AUTONOMY.
exp_dev decides anchor names, sweep grids, threshold formulas, queue assignments, and pre-reg bands.

---

## Why this matters (1 paragraph)

The 3-cell-replicated "ARM_BASELINE_NO_CLEANUP=7.2268" finding is a METHODOLOGY confound, not a real lift over fair_harness baseline 7.3065. The two numbers measure DIFFERENT QUANTITIES on DIFFERENT TEST SUBSETS. Identifying which factor (encoder family vs ctx-unk-filter vs alpha-Laplace) dominates the gap is HIGH-VALUE because P1 (encoder dominance) implies relaxing f=0.05 sparsification could give fair_harness baseline a free +0.06-0.10 BPC lift. This would flip whether the canonical chain-grade rail sits at 7.30 or 7.22 and would re-tier the cf-RPE chain-grade-bonus decision. The cell is cheap (~5 min CPU) and DECISIVE.

---

## Anchor candidates (rank-ordered, cheapest decisive first)

### Rank 1: ENCODER-ABLATION-ON-FAIR-HARNESS-V1 (CPU ~5-10 min, fully decisive)

Anchor pointer: 5-arm cell, single seed=7, N_DIM=8192, N_TRAIN=100k, N_HELD=20k, V=4000, text8. Re-uses fair_harness scaffolding but ablates encoder + filter independently.

Arm structure (exp_dev to name + tune):
- A. fair_harness as-shipped (word2vec sparse-bipolar f=0.05, ctx≠unk filter, alpha-Laplace=0.1) -- expected 7.3065 (sanity rail)
- B. word2vec DENSE bipolar (no f=0.05 sparsification; sign-binarize only), ctx≠unk filter, alpha=0.1 -- predicted 7.15-7.25
- C. char-trigram dense (cleanup-cells encoder), ctx≠unk filter, alpha=0.1 -- predicted 7.18-7.25
- D. fair_harness encoder + NO ctx-unk filter, alpha=0.1 -- predicted 7.32-7.36
- E. char-trigram dense, NO filter, alpha=1.0 (cleanup-cells as-shipped) -- expected 7.2268 (sanity rail)

Substrate-product reading: tells us whether the canonical chain-grade rail can be moved from 7.30 to 7.20 by relaxing the f=0.05 sparsification of word2vec encoder. If yes, all cf-RPE / STDP / heterogeneous-plasticity deltas re-tier.

Tier hint: Tier 1 (cheap, fully decisive, gates interpretation of all downstream chain-grade tiering).

Pre-reg suggestion (exp_dev refines):
- HARD-PASS-METHODOLOGY-HYPOTHESIS: arm C lands within ±0.05 of either 7.22 OR 7.30 (resolves direction)
- HARD-FAIL: arm C lands outside [7.18, 7.35] (4th factor we haven't identified -- W normalization, batch precision, dtype)
- BONUS-CHAIN-GRADE-RAIL-FLIP: arm B BPC <= 7.25 (sparsification was hurting; canonical rail moves to ~7.20)

Why now: blocks the next round of chain-grade tier decisions on cf-RPE family; orchestrator should pause new fair_harness-baselined cells until this lands.

### Rank 2: CF-RPE-RE-BASELINE-ON-CHAR-TRIGRAM-V1 (CPU ~30 min, dependent on Rank 1)

Anchor pointer: if Rank 1 shows char-trigram dense is a viable encoder family, run a copy of cf-RPE N_STEPS curve (N=5000) on char-trigram dense encoder instead of word2vec sparse-bipolar.

Substrate-product reading: tests whether cf-RPE lift generalizes across encoder families. If cf-RPE bpc=7.06 on char-trigram dense (matching its 7.04 on word2vec sparse), the cf-RPE mechanism is encoder-independent and the substrate is more robust than current cert tier shows.

Tier hint: Tier 1 (encoder-independence is a major cert-grade strengthener).

Why now: only after Rank 1 confirms char-trigram dense is the correct family. If Rank 1 shows word2vec dense (arm B) is best, run Rank 2 on that instead.

### Rank 3: BASELINE-CALIBRATION-TABLE-V1 (CPU minimal, infrastructure)

Anchor pointer: ship `data/baseline_calibration_table.json` mapping (encoder_family, ctx_unk_filter, alpha_laplace, N_DIM) -> expected_baseline_bpc. Populated from Rank 1's 5 arms + any subsequent cells.

Substrate-product reading: prevents future cross-encoder lift framings. This is the META-atom enforcement layer.

Tier hint: Tier 2 (infrastructure; not a science cell; supports discipline).

Why now: same cycle as Rank 1 results land. Build the table from Rank 1's data.

---

## Context pointers (file paths)

- Research note (full L1-L4 analysis): d:/AI/hd-instrument/notes/research_surprise_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md
- Fair_harness cell (canonical encoder + filter): d:/AI/hd-instrument/experiments/exp_fair_harness_substrate_as_lm_v1.py
- Multi_iter cell (char-trigram baseline 7.2268): d:/AI/hd-instrument/experiments/exp_substrate_multi_iteration_cleanup_LM_v1.py
- Tanh cell (char-trigram baseline 7.2332 at N=4096): d:/AI/hd-instrument/experiments/exp_substrate_continuous_tanh_attractor_dynamics_v1.py
- Cue_clamped cell (char-trigram baseline 7.2268): d:/AI/hd-instrument/experiments/exp_substrate_iterative_cleanup_cue_clamped_production_v1.py
- cf-RPE N_STEPS curve (uses fair_harness baseline 7.3372): d:/AI/hd-instrument/data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json
- Heterogeneous plasticity (uses fair_harness baseline 7.306): d:/AI/hd-instrument/data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json
- CONFIG_VERSION delta signatures (compare these first before any cross-cell BPC framing):
  - fair_harness: "PRETRAIN_DIM=300 ... sparse_f=0.050 pc_layers=3 kwta_k=10"
  - cleanup-cells: "f=0.050 amplitude_scale=4.472" (NO pretrain_dim, NO kwta)

---

## Contract

exp_dev is autonomous on: anchor names, sweep grid, threshold bands, queue assignment, timeout formula,
smoke vs full sequencing, whether to batch or serial. exp_dev MUST commit the cell + pre-reg note
before remote dispatch (per [[feedback-commit-prereg-notes-before-remote-dispatch]]).

exp_dev is NOT autonomous on: pausing or resuming the runner, changing the substrate architecture beyond
what anchors above specify, committing cap_map changes (orchestrator/verdict_handler owns that),
re-baselining cf-RPE chain-grade tier in the cert ledger (Skunkworks owns by-construction-saturation tiering).

## Autonomy declaration

exp_dev has full autonomy to sequence, batch, skip, or reorder anchors above based on current queue state,
runner availability, and findings from Rank 1. The rank ordering above is research-advisory; exp_dev should
apply rung-ladder methodology (Rank 1 first since it gates all others). If laptop CPU is busy, Rank 1 can
go on local_cpu_queue at any seed budget; the 1-seed result is already decisive.

Per [[feedback-fix28-violation-count-internalize-harder]]: when Rank 1 lands, read per-arm metrics.json BEFORE
propagating any cross-arm narrative. Do NOT frame from verdict_msg summary text alone.
