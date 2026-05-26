# Visibility decisions 2026-05-26

## 17:00 -- v212: MoE SHIFT HARD-PASS + HiPPO-init CLOSED + Bet B 2-tier CELL-LEVEL

Source files: data/exp_wave14_moe_shift_partition_v3/metrics.json (remote, 3639s GPU); data/exp_wave14f_hippo_init_w_v1/metrics.json (remote, 1629s GPU); data/exp_wave14_betB_2tier_coarse_analysis_v1/metrics.json (local re-analysis, 0.015s).

Key: (1) MoE SHIFT mechanism confirmed at K>=4 (lift 20-31%); PARTITION arm negligible; MoE rebuild direction locked as SHIFT routing. (2) HiPPO-init W closed-negative (no depth benefit); but substrate naturally learns HiPPO-like eigenspace (spectral_corr=0.993) -- positive characterization. (3) Bet B binary taxonomy confirmed at cell CI level (silhouette=0.788, non-overlapping CIs).

Label-honest override: algorithm labeled MoE SHIFT as MIDDLE; pre-reg bands authorize HARD-PASS at K=4 lift=0.205 and K=8 lift=0.312 (both > 0.15 threshold). PROT-004: 1 HiPPO-init closure, 5 rescues filed.

v213 verdict batch (2026-05-26 ~18:30): 4 verdicts processed. (1) MoE K-scaling MIDDLE: diverging arms -- Arm_A/B degrade, Arm_C improves with K; K=4 design point confirmed. (2) Bet B 5-plateau HARD_FAIL: 4-tier taxonomy is the hard scope; Saad-Solla 4-corpus not retracted. (3) MoE top-edge v2: CLOSED-NEGATIVE formula error (N-independent normalization missing; DMPK sole discriminator). (4) Bet I polylog v2: D_SWEEP ceiling at 60; v3 needed with D_SWEEP=[100-200]. Queue-visibility gap flagged: overnight_queue.json stale (2026-05-19); runner reads unknown source. 0 Tier-1 advances; 14+7 portfolio UNCHANGED. Status_log entries written. v213 local commit complete; push deferred to main thread.
