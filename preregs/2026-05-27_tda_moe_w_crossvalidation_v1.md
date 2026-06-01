# Pre-registration: tda_moe_w_crossvalidation_v1

**Date:** 2026-05-27
**Script:** experiments/exp_tda_moe_w_crossvalidation_v1.py
**Queue:** remote_cpu_queue (CPU; ~15-30 min)
**Trigger:** exp_tda_reanalysis_5probe_v1 returns TDA_HARD_PASS

## Hypothesis

If TDA-C (b_0-plateau diagnostic) passes on purpose-generated W, does it also work
as an offline audit tool on W matrices from existing pipeline experiments?

## Design

Cross-validate TDA-C against 5 existing MoE experiment results (K_scaling_v1, K_perarm_v1,
cosine_router_v1). Re-generate W from same seeds + apply TDA-C. Tally agree rate.

## Pre-registered bands

- **HARD-PASS (reliable offline audit):** agree_rate >= 4/5 AND TDA-B vs top-edge Pearson r >= 0.40
- **HARD-FAIL:** agree_rate <= 2/5 OR r < 0.10
- **MIDDLE:** agree_rate 3/5
