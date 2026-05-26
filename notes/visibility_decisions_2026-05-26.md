# Visibility decisions 2026-05-26

## 17:00 -- v212: MoE SHIFT HARD-PASS + HiPPO-init CLOSED + Bet B 2-tier CELL-LEVEL

Source files: data/exp_wave14_moe_shift_partition_v3/metrics.json (remote, 3639s GPU); data/exp_wave14f_hippo_init_w_v1/metrics.json (remote, 1629s GPU); data/exp_wave14_betB_2tier_coarse_analysis_v1/metrics.json (local re-analysis, 0.015s).

Key: (1) MoE SHIFT mechanism confirmed at K>=4 (lift 20-31%); PARTITION arm negligible; MoE rebuild direction locked as SHIFT routing. (2) HiPPO-init W closed-negative (no depth benefit); but substrate naturally learns HiPPO-like eigenspace (spectral_corr=0.993) -- positive characterization. (3) Bet B binary taxonomy confirmed at cell CI level (silhouette=0.788, non-overlapping CIs).

Label-honest override: algorithm labeled MoE SHIFT as MIDDLE; pre-reg bands authorize HARD-PASS at K=4 lift=0.205 and K=8 lift=0.312 (both > 0.15 threshold). PROT-004: 1 HiPPO-init closure, 5 rescues filed.
