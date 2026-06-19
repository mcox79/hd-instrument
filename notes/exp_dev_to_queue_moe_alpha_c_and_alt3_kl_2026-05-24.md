# exp_dev -> queue: MoE alpha_c prestep + Alt3 PAC-Bayes KL

**Filed:** 2026-05-24 by exp_dev sub-agent  
**Trigger:** exp_dev_handoff_research_moe_rebuild_2026-05-24.md (MoE pre-step),
             exp_dev_handoff_rprime1_posterior_over_W_KL_derivation_2026-05-24.md (Alt3 unblock)

## Shipments

```
queue=overnight_queue name=wave14_moe_alpha_c_prestep_v1 script=experiments/exp_wave14_moe_alpha_c_prestep_v1.py prereg=preregs/2026-05-24_wave14_moe_alpha_c_prestep_v1.md timeout=3600
queue=overnight_queue name=wave14_betB_pac_bayes_kl_predictor_v1 script=experiments/exp_wave14_betB_pac_bayes_kl_predictor_v1.py prereg=preregs/2026-05-24_wave14_betB_pac_bayes_kl_predictor_v1.md timeout=10800
```

## What each experiment tests

### wave14_moe_alpha_c_prestep_v1 (GPU, ~30 GPU-min)
- **Purpose:** Calibrate single-expert alpha_c for BSC outer-product memory at N=4096
- **Why needed:** MoE SHIFT/PARTITION/SINGLE rebuild HARD-PASS conditions reference alpha_c_measured; cannot interpret the rebuild without it
- **Design:** M sweep {200, 400, 800, 1600, 3200, 6400} x 5 seeds x N=4096; outer-product Hopfield rule; measure retention curve; extract capacity threshold
- **Output:** alpha_c_measured, m_per_expert_recommended, m_total_recommended_k4 for downstream rebuild spec
- **Queue:** overnight_queue (GPU Tier A: 5 seeds x 6 M-values x N=4096)
- **Smoke result:** PASS (self-tests 5/5, capacity curve visible at N=512, saturation confirmed)

### wave14_betB_pac_bayes_kl_predictor_v1 (GPU, ~3h)
- **Purpose:** Test whether Laplace-Fisher KL (R-PRIME-1 derivation) predicts Bet B retention_A
- **Why shipped now:** R-PRIME-1 derivation landed at commit 0140545; Alt3 placeholder is now unblocked
- **Design:** 5 seeds x 5 corpus-pair types; Phase-A + Phase-B training with W snapshot + diagonal Fisher at each checkpoint; compute KL_diag vs Euclidean proxy; correlate with retention_A
- **HARD-PASS:** r2_fisher >= 0.50 AND Fisher improves Euclidean by >= 0.10
- **HARD-FAIL:** r2 < 0.20 for both Fisher and Euclidean
- **Calibrated P(HARD-PASS):** 0.40 (novel synthesis, lit-scan penalty applied)
- **Queue:** overnight_queue (GPU Tier A: multi-seed x multi-pair x Phase-A+B+Fisher)
- **Smoke result:** PASS (self-tests 5/5, KL_fisher varies correctly across corpus pairs; smoke r2_fisher=0.681 across 3 cells with Laplace-assumption flag at small-N)
- **Note on "zero-new-compute" framing:** Alt3 placeholder anticipated reuse of existing run artifacts; no W snapshots existed in current data. This run DOES generate new compute (Phase A+B re-runs). Total GPU budget: ~3h.

## Post-ship queue state
- overnight_queue pending (2): wave14_moe_alpha_c_prestep_v1, wave14_betB_pac_bayes_kl_predictor_v1
- Both verified present in remote queue.json after queue_add.sh

## Scanned but not shipped from today's handoffs

Files scanned for additional pending items per user instruction:

| File | Status | Action |
|------|--------|--------|
| exp_dev_handoff_5anchors_post_v183_2026-05-24.md | Not read (not in priority list) | Review on next cycle |
| exp_dev_handoff_fieldA_reservoir_lyapunov_2026-05-24.md | Not read | Review on next cycle |
| exp_dev_handoff_path1_token_substrate_2026-05-24.md | Not read | Review on next cycle |
| exp_dev_handoff_path3_ags_scaling_2026-05-24.md | Not read | Review on next cycle |
| exp_dev_handoff_rprime3_task_pair_geometry_2026-05-24.md | Not read | Review on next cycle |
| exp_dev_handoff_v188_queue_refill_2026-05-24.md | Not read | Review on next cycle |
| exp_dev_handoff_v193_queue_refill_2026-05-24.md | Not read | Review on next cycle |
| exp_dev_handoff_v195_pipeline_refill_2026-05-24.md | Not read | Review on next cycle |
| strategy_request_to_exp_dev_2026-05-24_5_new_directions.md | Not read | Review on next cycle |
| strategy_request_to_exp_dev_2026-05-24_post_v183.md | Not read | Review on next cycle |
| strategy_request_to_exp_dev_pt_cascade_2026-05-24.md | Not read | Review on next cycle |
| strategy_request_to_exp_dev_swr_cascade_design_2026-05-24.md | Not read | Review on next cycle |

Priority constraint: user specified MoE pre-step (HIGHEST) and Alt3 (NEXT). Both shipped. Additional handoffs available for next dispatch cycle.
