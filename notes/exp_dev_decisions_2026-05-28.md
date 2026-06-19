# exp_dev decisions 2026-05-28

Shipped 5 GPU anchors to overnight_queue: saad_solla_v13_n4096_5seed (saad-solla 5-seed N=4096 rescue from v12 timeout), pb3_extended_v3_n4096 (CUDA gen bug fix, 5-seed 7-beta), axis1_mb_chunk5_n4096 (M-x-beta softmax confidence surface, HARD_PASS smoke), axis3_triplepoint_v1_n4096 (triple-point perturbation direction, walk-back to 5 seeds), kf3_multisub_v2_n4096 (first TRUE N=4096 multi-substrate isolation; v1 smoke-only). Blocked axis4_hyst_ramp_v1_n4096 (DESIGN FLAW: linear W reversible, loop_area always 0). All 5 remote-verified exit 0.exp_dev 2026-05-28 batch2: Shipped 5 anchors. GPU: saad_solla_v14_n8192_3seed (t=12600s option-c 3-seed; 3rd reship), axis1_mb_chunk6_n4096 (t=3600s FULL 270-cell surface), axis1_mb_chunk7_n4096 (t=3600s high-M tail M/N={16,20} bug-fixed). CPU: kf2_isolation_proof_v2_n8192 (t=600s N=8192 envelope), moe_fixed_total_capacity_K_sweep_v1_n4096 (t=4500s fixed-cap K-ceiling). TCFT v3 already in queue; bet_b batch128+rehab_epochs already completed; skipped both. chunk7 design bug (random probe != stored keys) caught by multi-scale smoke and fixed. All 5 anchors REMOTE VERIFIED via queue_add.sh exit-0 + presence check.## 2026-05-28 post-restart batch

Shipped 3 anchors:
1. saad_solla_v15_n8192_5seed -> overnight_queue (21600s). Root cause fix: v14 used 3 f-points, v15 uses 5 (same as v11 that HARD_PASSed). Gate OR-clause aligned to v252 convention. Smoke PASS (r2=0.803 < 0.85).
2. bid_n_stability_v4_n12288 -> remote_cpu_queue (10800s). N=12288 intermediate rescue for v3 timeout (N=16384 too slow). Smoke PASS (BID non-null, in_known_class=False).
3. axis3_triplepoint_v2_n4096 -> overnight_queue (3600s). Alternate operating points (M_frac=10/8/4). Smoke HARD_PASS: sign_divergence=True at M_frac=10, max|delta|=0.35.

Local completion (not queued):
- wave14_moe_hebbian_anchor_router_v2_n4096: ran locally to HARD_FAIL at N=4096 FULL (entropy=4.0b at K=16, all 3 variants). Definitive result: K-scaling entropy collapse fundamental in BSC space for static anchors. Clarifies v1 suspicious smoke-only run (2.7s wall).
## 2026-05-28 24h overnight batch ship

Shipped 4-anchor overnight GPU batch to overnight_queue in priority order:
- t3_susceptibility_v1_n4096 (PRIO-1: 3-axis susceptibility probe, ~0.5 GPU-day)
- c1_kf_battery_phase_v1_n4096 (PRIO-2: killer-feature battery across phase boundary, ~2-3 GPU-days)
- m1_boundary_fine_v1_n4096 (PRIO-3: boundary fine-sweep M_c localization, ~1 GPU-day)
- c3_tcft_phase_v1_n4096 (PRIO-4: TCFT deletion cert N-scaling at N=4096, ~1-2 GPU-days)

Decisions:
- C3 redesigned from large-M {20K,45K,80K,200K} to feasible {128,512,2048,4096} due to O(M*N^2) infeasibility
- Added missing --self-test argparse arg to all 4 scripts (gate requires it)
- PROT-018: all N_FULL=4096 verified pre-ship
- Remote verified: 4/4 PASS via SSH poll of overnight_queue/queue.json
- wave14_moe_hebbian_anchor_router_v2_n4096 HARD_FAIL surfaced for verdict_handler dispatch
## AGGRESSIVE REFILL 8-ANCHOR SHIP (2026-05-28 cycle 2)

Shipped 8 anchors for 24h+ offline window.

GPU (overnight_queue):
- saad_solla_v16_n8192: M-axis expansion of v15 HARD_PASS_STRONG, M_fracs=[0.25,0.50], N=8192, 2-seed, timeout=21600; smoke r2=0.803 HARD_PASS
- t1_beta_sweep_v1_n4096: first beta_c localization at phase boundary M_frac=8.0, softmax confidence metric (argmax is beta-invariant - fixed), smoke conf_low=0.00017->conf_high=0.641 MIDDLE_BAND, timeout=14400
- t2_codebook_boundary_v1_n4096: codebook-order boundary search c-fraction sweep M_frac=2.0, smoke slope=0.138 MIDDLE_BAND (calibration probe, HP_SLOPE_MIN widened to 0.10 per calibration policy), timeout=14400
- saad_solla_v17_cross_cb_v1_n4096: cross-codebook generality BSC+Antipodal non-Kerdock, smoke r2=0.668/0.693 both PASS MIDDLE_BAND, timeout=10800

CPU (remote_cpu_queue):
- bid_m_normalized_v2_n4096: extended M-range [0.025-15.0] BID sweep, bug fixes (key='bid_estimate', band=BAND_MAX_INSIDE not 50.0), smoke HARD_PASS all>>0.55, timeout=3600
- moe_capacity_aware_router_v1_n4096: capacity-aware routing 5th rescue arm (fill_frac min-load), meta-learning lock: routing MUST be capacity-aware not identity-aware, smoke K=16 ret=0.911 MIDDLE_BAND, timeout=3600
- pb2_corr_len_v2_n1024: edit-propagation correlation length vs M_frac, smoke xi=0.395 monotone HARD_PASS, timeout=1800
- kf2_cross_codebook_v1_n4096: KF-2 isolation across kerdock/bsc/gaussian, smoke all max_iso<0.05 HARD_PASS, timeout=1800

ABANDONED: tcft_erase_time_v1_n2048 -- _run_direct anti-Hebbian cancels Hebbian leaving W~0, var_ratio~0 all cells; interface signature (N,M,seed) does not accept erase_steps; design error not instrumentation-bug.

All scripts updated with --self-test argparse gate (was missing, blocked queue_add gate).
REMOTE VERIFY: 8/8 PASS (queue_add.sh built-in SSH verify)
PROT-018: all pass (N suffix binding confirmed pre-ship)
PROT-019: all pass (timeouts >= tier minimums)
2026-05-29: BE-1 precision sweep (6 _n8192 GPU anchors fp32/fp16/int8/int4/int2/int1) + phase region C/D (4 _n4096 GPU anchors kf1/kf2 x region_c/d beta=64) scripted, smoked, preregs filed; SSH offline so queue_add staged in exp_dev_to_queue note; TCFT/SS phase variants blocked Tier-22026-05-29 Shipped kf3_cross_codebook_v1_n4096 to remote_cpu_queue (timeout=14400s; smoke=SMOKE_PARTIAL leakage=0.018 at 4x-smoke trending HP). Blocked KF-4 v4 (structural acc_drop=0 across 3 mechanisms; Kerdock error-correction absorbs drift) and BID v6 (BAND_MAX_INSIDE=0.55 not applicable to raw BSC pattern BID). Routing notes filed to Strategy.