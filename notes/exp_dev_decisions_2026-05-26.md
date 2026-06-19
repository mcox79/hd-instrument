# exp_dev decisions 2026-05-26

2026-05-26 exp_dev: VERIFY 6 pre-block anchors: (1) wave14_1rsb_hysteresis_v2=TIMEOUT/failed (wall=3600s no metrics); (2) wave14_betB_pac_bayes_kl_predictor_v2=completed/ALT3_LAPLACE_ASSUMPTION_VIOLATED (r2_fisher=0.0 21/25 suspect cells; suspicious but real instrumentation result per honest-reread); (3) wave14_saddle_cascade_plateau_v1=CASCADE_INSTRUMENTATION_FAIL (corpus_a too short 49105<200000 all 21 cells errored); (4) wave14_ib_plateau_test_v1=still-running (started 2026-05-25T00:08:14 after cpu_runner_0 revived); (5) wave14_moe_alpha_c_prestep_v2=ALPHA_C_HARD_FAIL (alpha_c_measured=0.390625 outside [0.4,0.7]); (6) wave14_moe_shift_partition_v1=OOM-fail (torch.OutOfMemoryError at M_total=25600 K=8). GPU runner revived via schtasks /run /tn hd_gpu_runner_0.

2026-05-26 exp_dev: FLUSH 7 handoffs -- (1) wave14_moe_shift_partition_v2 shipped overnight_queue REMOTE_VERIFIED (now running); (2) wave14_betB_replay_hB_collateral_v1 shipped overnight_queue REMOTE_VERIFIED; (3) wave14_betB_replay_hC_scaling_v1 shipped overnight_queue REMOTE_VERIFIED; (4) wave14f_hippo_init_w_v1 shipped overnight_queue REMOTE_VERIFIED; (5) wave14g_recurrent_cleanup_k6_v1 NEW built+smoked (lift=-1.0 mechanistic HARD_FAIL expected -- formula drives toward key space) + shipped overnight_queue REMOTE_VERIFIED; prereg: preregs/2026-05-26_wave14g_recurrent_cleanup_k6_v1.md; (6) wave14e_bet_n_wta_v1 NEW built+smoked (P1=HARD_PASS util=0.886 P2=MIDDLE ratio=1.061 P3=HARD_FAIL@smoke cos=0.000 documented artifact) + shipped overnight_queue REMOTE_VERIFIED; corpus fix: bytes_to_input_vecs replaces self-referential Phi lookup; prereg: preregs/2026-05-26_wave14e_bet_n_wta_v1.md; (7) wave14_betB_4corpus_equalspacing_v1 result already complete locally HARD_PASS (BIC_delta=-121.3 spacing_err=0.0035 4 plateaus statistically distinct -- reanalysis of existing betB data per handoff AUTONOMY: spot-check first); no new ship needed. MCT handoff still DEFERRED (awaiting saddle-cascade verdict).

2026-05-26 exp_dev: wave14_saddle_cascade_plateau_v2 NEW built (corpus tiling fix vs v1 RuntimeError) + smoked (CASCADE_HARD_PASS R2=0.750 max_dev=0.087; 4/4 self-tests passed; 6.5s smoke) + shipped remote_cpu_queue REMOTE_VERIFIED; prereg: preregs/2026-05-26_wave14_saddle_cascade_plateau_v2.md; self-test passed on remote (2.6s).
- 2026-05-26 exp_dev: Shipped wave14_1rsb_hysteresis_v3 to remote_cpu_queue (timeout=7200s, ETA 20-40 min). Pred-4 1-RSB hysteresis probe v3 after v1 INSTRUMENTATION_FAIL + v2 TIMEOUT+DESIGN_BUG. Key fixes: (1) N=2048->1024 for 4x CPU speedup; (2) STATEFUL trajectories (v2 had zero statefulness): forward=fresh W per M, reverse=W_max re-tuned at decreasing M values; (3) single-corpus single-phase (eliminates 4-stage complexity); (4) checkpoint writes after each M cell; (5) M_SWEEP_FULL=[2k,5k,10k,20k,35k,48k]. Smoke PASS at N=256 (77s, gap=1.12 at M=2k) and N=512 (124s, gap=0.83). Remote --self-test gate PASS 2.7s. VERIFIED in remote queue.json (queue_pending=2).2026-05-26 exp_dev: (1) Pre-flight PASS: v2 mean_cosines[1600]=0.8482 in [0.83,0.87] -- grid-quantization confirmed. Built wave14_moe_alpha_c_prestep_v3 (dense M-grid=[1024,1536,1792,2048,2304,2560,2816,3072,3584], alpha-spacing=0.0625 in band, 7/7 self-tests, smoke PASS N=512 alpha_c=0.5625 N=2048 alpha_c=0.5000) shipped overnight_queue REMOTE_VERIFIED. (2) Built wave14_moe_top_edge_v1 (free-additive-conv top-edge ratio, standalone K-sweep N=4096 5seeds, 4/4 self-tests, smoke PASS valid metrics) shipped overnight_queue REMOTE_VERIFIED. MoE v2 still running; top-edge script independent of v2 result.2026-05-26 exp_dev: WF handoff Test 1 = INSTRUMENTATION-FAIL (no multi-N BetB data; existing runs log N=4096 only). Test 3 = INSTRUMENTATION-FAIL (no per-expert retention in MoE smoke data; moe_shift_partition_v2 just failed on remote, so Test 3 deferred to next MoE v3 design). Shipped 3 experiments: (1) wave14e_bet_n_wta_v2 overnight_queue REMOTE_VERIFIED (P3 instrumentation fix: PCA top-1 replaces degenerate mean-centroid, cross-corpus eval replaces single-corpus gap; smoke pca_cos_dist=0.63 vs 0.00 in v1; 7/7 selftests); (2) wave14_betB_replay_hB_collateral_v2 overnight_queue REMOTE_VERIFIED (H-B v2: N_FULL 4096->8192, gate 0.15->0.10; v1 showed all-5-seeds negative collateral = H-A-only pattern; new HB_SIGN_CONSISTENT_NEGATIVE verdict for all-negative case; 5b/5 selftests); (3) wave14_research_wf_taup_reship_v1 overnight_queue REMOTE_VERIFIED (WF Test 2: BetB N={1024,2048,4096} 5seeds per-epoch tau_p logging; sigma(tau_p) slope target [-0.7,-0.3] for N^{-1/2}; 4/4 selftests including WF prediction self-test cells). NOTE: moe_shift_partition_v2 = FAILED on remote - orchestrator should process verdict.
## Batch ship (resumed session after compaction)

**wave14_moe_shift_partition_v3** SHIPPED overnight_queue
- Root cause of v1/v2 failures: K=8 M_mult=2.0 -> M_total=25600 -> 1.11GiB OOM
- Fix: get_m_mult(K, smoke) returns [0.5, 1.0] when K>=8, [0.5, 1.0, 2.0] when K<=4
- Max M_total at K=8: 12800 (within 8GB budget); explicit torch.cuda.empty_cache() per cell
- Smoke PASS (9 cells, 0 OOM, valid metrics, MOE_SHIFT_MIDDLE verdict)
- Self-tests: 7/7 PASS; remote VERIFIED

**wave14_1rsb_pq_retained_v2** SHIPPED overnight_queue
- Envelope expansion of v1 (binder=-0.164, INCONCLUSIVE at N=2048 10-seeds)
- N_FULL=4096, SEEDS_FULL=20, KDE_BW=0.02 (tighter for UV-problem)
- HARD-PASS: binder>0.30 AND n_peaks>=2 AND mean_q_sig>5
- Smoke PASS (PQ_RETAINED_MIDDLE at N=512); self-tests: 5/5 PASS
- Remote VERIFIED

**wave14_betB_nscaling_v1** SHIPPED overnight_queue
- Envelope expansion of v206 HARD_PASS (BIC_delta=-121.3 at N=4096)
- N_FULL=8192, 5 seeds; 4-class taxonomy equal-spacing + REPLAY Cohen's d test
- Root bug fixed: evaluate_bpc called with wrong signature (missing pool_v/pool_l/pool_u; batch_size/device swapped)
- Correct call: base.evaluate_bpc(W, pool_v, pool_l, pool_u, byte_atoms, pos_atoms, val_idx, val_tgt, batch_size, device)
- Smoke PASS (NSCALING_HARD_FAIL at N=512/1epoch expected -- instrumentation confirmed working)
- Walk-back gate: N=1024 non-null (ret_A=0.992, ret_B=0.924); multi-scale confirmed
- Self-tests: 4/4 PASS; remote VERIFIED

**wave14_betB_replay_hA_direct_v1** SHIPPED overnight_queue
- H-A consolidation direct test: inter-phase vs intra-phase replay timing
- 3 arms x 5 seeds x N=4096; HARD-PASS: ret(Arm1)-ret(Arm2) >= 0.05
- Same evaluate_bpc signature bug fixed in all 3 arm functions
- Additional fix: f-string formatting error in final print (lift formatting)
- Smoke PASS (HA_MIDDLE at N=512/1epoch; lift=0.028 positive but below HP)
- Self-tests: 5/5 PASS; remote VERIFIED

Verdict sweep: SSH to marsh@home for new verdicts -- remote runner shows 6 pending in overnight_queue.
No terminal verdicts observed since v210 (wave14_moe_shift_partition_v2 was already noted as FAILED in prior decision log entry).

## 2026-05-26 pre-build session: 4 tasks (5-corpus + Bet I 3rd envelope + MoE SHIFT K-sweep + PROT-013)

**wave14_betB_5corpus_equalspacing_v1** QUEUED local_cpu_queue
- 5-corpus equal-spacing extension of v206 HARD_PASS (adds NO_REPLAY as 5th level)
- Smoke PASS; result: MIDDLE_BAND (spacing_error=0.0284 PASSES < 0.05; BIC_delta=-8.64 misses -10 by 1.36)
- Calls for full-scale GPU 5-corpus experiment; G4 n=5 is boundary of statistical power
- Prereq: prereqs/2026-05-26_wave14_betB_5corpus_equalspacing_v1.md

**wave14_beti_depth_polylog_v1** SHIPPED overnight_queue (REMOTE VERIFIED; queue depth 6)
- Bet I 3rd envelope: d_c = sqrt(N * log(N) / K) polylog correction probe
- N-sweep {256,512,1024,2048,4096} x d_sweep {5,10,15,20,25,30,40} x 5 seeds
- Smoke PASS (MIDDLE_BAND expected at smoke d-sweep; full run tests the cliff region)
- Prereq: prereqs/2026-05-26_wave14_beti_depth_polylog_v1.md
- Cap_map implication if HARD_PASS: Bet I upgrades from 2/3 to 3/3 envelopes

**wave14_moe_shift_K_scaling_v1** PRE-BUILT (gated on SHIFT verdict from wave14_moe_shift_partition_v2)
- K sweep {2,4,8,16,32} at N=4096; Arm A SHIFT vs Arm C SINGLE vs Arm B PARTITION
- Smoke PASS; selftests pass; ready for immediate dispatch on SHIFT verdict
- Prereq: prereqs/2026-05-26_wave14_moe_shift_K_scaling_v1.md
- DO NOT ship until shift_partition_v2 returns SHIFT (Arm A > Arm C by > 0.15)

**PROT-013** FILED to active_protocols.md
- evaluate_bpc signature self-test mandate (callable check in _instrumentation_selftest)
- Addresses systematic TypeError class: v1 Pred-4, v1 PAC-Bayes, hA_direct defensive fix
- One-line PROT: assert base.evaluate_bpc(W_tiny, ..., 10 args) callable without TypeError
wave14e_bet_n_wta_v3 shipped overnight_queue: P3 corpus-encoded-retrieval fix (root cause: v2 matched_gap=0 because cleanup_acc uses random Phi pairs not corpus-specific n-gram pairs); K=256, n_epochs=8, M-sweep extended to M=8000; smoke PASS; REMOTE VERIFIED
## 2026-05-26 exp_dev dispatch session: 4 experiments shipped

**wave14_moe_shift_K_scaling_v1** SHIPPED overnight_queue (REMOTE VERIFIED)
- SHIFT confirmed at v212 (K=4 lift=0.205, K=8 lift=0.312); K-scaling sweep unblocked
- K sweep {2,4,8,16,32} x N=4096 x 5 seeds; Arms: SHIFT / PARTITION / SINGLE
- Smoke: MIDDLE_BAND (expected; N=512 sub-optimal regime); 5/5 selftests PASS
- Prereq: prereqs/2026-05-26_wave14_moe_shift_K_scaling_v1.md (pre-existed)
- Queue: overnight_queue; ~2-3 GPU-hours

**wave14_betB_5corpus_fullscale_v1** SHIPPED overnight_queue (REMOTE VERIFIED)
- 5-corpus equalspacing full-scale: generates 15 new NO_REPLAY_SAME_CORPUS cells (seeds 100-114)
- Augments existing n_G4=5 to n_G4=20; re-runs 5-state BIC on combined data
- Protocol: Phase_A(corpus_A) -> Phase_B(corpus_B, NO replay) -> measure retention_A
- Dependency: data/exp_wave14_betB_shift_class_predictor_v1/metrics.json SCPed to remote
- Smoke: SMOKE_PASS (regime-mismatch at N=512; BIC bypassed in smoke mode; G4_new values valid)
- Prereq: prereqs/2026-05-26_wave14_betB_5corpus_fullscale_v1.md
- Queue: overnight_queue; ~2-3 GPU-hours; 15 seeds x 2-stage

**wave14_moe_top_edge_v2** SHIPPED overnight_queue (REMOTE VERIFIED)
- N=16384 retry of free-additive top-edge (v1 FREE_ADDITIVE_MIDDLE; systematic 0.5x offset)
- Finite-N hypothesis: offset should improve from 0.50 toward 0.75+ at N=16384
- K_sweep=[2,4] only; M_mult=[1.0] only (2x excluded for memory at N=16384)
- New metric: offset_ratio_emp_over_pred; new verdict: FREE_ADDITIVE_FORMULA_ERROR if offset<0.65
- Smoke: offset_ratio=0.61 at N=1024 (improvement trend consistent with finite-N)
- Prereq: prereqs/2026-05-26_wave14_moe_top_edge_v2.md
- Queue: overnight_queue; ~2-3 GPU-hours

**wave14f_hippo_warmstart_v1** SHIPPED remote_cpu_queue (REMOTE VERIFIED)
- HiPPO rescue #2: does HiPPO-init reach task-performance threshold FASTER than zero-init?
- Metric: epochs_to_reach(cos@d=5 >= 0.40) for each init; speedup_ratio = hippo/zero
- Design: N=2048, 3 seeds, 15 epochs, checkpoints [1,2,3,5,8,12,15]; n_patterns=30
- Smoke: SMOKE_PASS (regime-ceiling at N=512; both saturate at epoch=1; known artifact)
- REDESIGN NOTE: v1 script used spectral_corr approach (meaningless metric); rewritten to
  direct task-performance cosine convergence curve (matches hypothesis correctly)
- Prereq: prereqs/2026-05-26_wave14f_hippo_warmstart_v1.md
- Queue: remote_cpu_queue; ~20-40 min CPUSHIP_BATCH [23:21]: 10 experiments shipped. overnight_queue (7 GPU): wave14_moe_shift_K_scaling_v2 [now running], wave14_moe_top_edge_v3, wave14_betB_replay_hA_direct_v2, wave14_1rsb_pq_retained_v3, wave14e_bet_n_wta_v4, wave14_betB_5corpus_noreplay_fix_v1, wave14_betB_nscaling_v2. remote_cpu_queue (3 CPU): wave14_moe_intraexpert_overlap_v1, wave14f_hippo_eigenspace_v1, wave14_betB_rd_perturbation_recovery_v2. All 10 passed selftest+smoke. Fix: betB_5corpus_noreplay_fix_v1 rewrote run_one_4class_cell using base.train_w_with_replay (bigram-shape bug fixed). Removed sklearn dep. overnight_pending=6 cpu_pending=5.2026-05-26: Pre-built 7 anticipatory follow-on scripts for 10 in-flight anchors. K_scaling_v3 (v2 HARD_PASS trigger), K_perarm_v1 (v2 DIVERGENCE trigger), top_edge_v4 (v3 FREE_ADDITIVE_HARD_PASS trigger), bet_n_wta_v5 (v4 TIER1_PROMOTION trigger), pq_retained_v4 (v3 HARD_PASS trigger), 6corpus_extension_v1 (5corpus HARD_PASS trigger), replay_hA_direct_v3 (v2 HARD_PASS trigger). All smoke-tested PASS. Index: notes/exp_dev_prebuilds_2026-05-26.md. NO queue_add calls made.wave14_unified_svd_cascade_falsifier_v1 shipped to remote_cpu_queue. Re-trains delta-rule W on real corpus at N=256 (5 W instances: 1rsb-regime, over-capacity, 4-phase cascade, 2 corpus variants). SVD cascade equal-spacing test for UNIFIED framework (Bachtis-Biroli 2024). Smoke: UNIFIED_HARD_FAIL direction (mean spacing_error=2.38, all 5 HARD_FAIL; pre-reg HARD-FAIL threshold = spacing_error > 0.15 on >= 3/5). Pre-reg: preregs/2026-05-26_wave14_unified_svd_cascade_falsifier_v1.md. KEY findings: W not saved in original v206/v211/v212 runs; re-training uses delta-rule on same text corpus; singular structure shows spike (one dominant mode, non-equal spacing) not a cascade ladder.2026-05-26 allnight_refill: Shipped 14 anchors (GPU=6, CPU=8). GPU: replay_hA_direct_v3, 1rsb_pq_retained_v4, betB_6corpus_extension_v1, bet_n_wta_v5, beti_depth_polylog_v3, ortho_OT_retention_v1. CPU: moe_shift_K_perarm_v1, saddle_cascade_v5_n4096, betB_rd_perturbation_recovery_v3, unified_svd_cascade_v2, ortho_reservoir_lyapunov_v1, betB_replay_hB_collateral_v1, betB_replay_hC_scaling_v1, betB_replay_hB_collateral_v2. Orthogonal: GPU=Wasserstein-2 OT retention, CPU=Reservoir Lyapunov. All 14 bridge-verified. Queue depth: GPU=9, CPU=14.## urgent_refill_v2_ship [2026-05-26]

Shipped 10 anchors (GPU=4, CPU=6). All 10 gate-passed and verified in remote queue.json.

CPU (remote_cpu_queue): renyi_dp_retention_v1, spectral_graph_lambda2_v1, moe_top_edge_dmpk_v1, tcft_substrate_falsifier_v1, ortho_blahut_arimoto_v1, ortho_pme_ising_capacity_v1
GPU (overnight_queue): hippo_k8_depth_v1, ortho_score_diffusion_v1, betB_cosine_geometry_n8192_v1, hippo_spectral_reg_v1

Orthogonal probes: Renyi-DP (CPU, field drill 0), score-based diffusion (GPU, field drill 0).
Top-edge diagnosis: N-invariant ~0.50x offset R2=0.0 across v1-v4 = formula error. DMPK sqrt(K) structural alternative shipped.
Research upstream-push filed: notes/exp_dev_to_research_top_edge_formula_error_2026-05-26.md
HiPPO PROT-004: rescue #4 (K8_depth) + #5 (spectral_reg) both shipped GPU.
Queue depth post-ship: CPU=19 pending, GPU=10 pending.2026-05-26 exp_dev night_rescue_batch: Shipped 2 rescue probes. (1) wave14_1rsb_rate_dep_hysteresis_v1 remote_cpu_queue REMOTE_VERIFIED: rate-dependence sweep epochs=[1,2,4,8,16,32] at M=[2000,10000] N=1024; discriminates thermodynamic-1RSB vs kinetic-glass; smoke r=-0.9996/-0.9987 (strong rate dependence signal); ETA 1-2h CPU. (2) wave14_1rsb_cluster_cond_pq_v1 remote_cpu_queue REMOTE_VERIFIED: cluster-conditional P(q) trains W under 4 shift-class conditions (CLASS_A/B/C/D), 5 seeds each N=1024; tests Krzakala+2007 cluster-glass framework; smoke shows inverted within/across structure (within_q=0.03 < across_q=0.24); ETA 2h CPU. Priority 3 TCFT already in queue as wave14_tcft_substrate_falsifier_v1 (CONFIRMED present). Night-depth already covered: GPU=10 pending, CPU=21 pending. 4-corpus Saad-Solla falsifier ALREADY DONE (betB_4corpus_equalspacing_v1 HARD_PASS BIC_delta=-121.28 spacing_error=0.0035). Total bridge-verified: 2/2 new ships + TCFT pre-existing = 3/3 rescue probes.exp_dev 2026-05-26: AGS basin-class handoff -- Test 1 (cluster-conditional P(q|k) peak positions) SKIPPED: queue depth 22 CPU / 10 GPU, v1 already in flight; v2 deferred until v1 verdict returns. Test 2 (Kerdock 4-distance-class audit) SHIPPED: wave14_kerdock_distance_class_audit_v1 -> remote_cpu_queue; smoke PASS, verdict HARD_FAIL (3 classes found, not 4; empirically correct Welch-bound structure); VERIFIED present in remote queue. Additional anchors SKIPPED: conservative given depth healthy + user asleep.2026-05-27 night_conservative_refill: failure_pattern=INDEPENDENT. (1) saddle_cascade_v4=TIMEOUT (running OK superseded by v5_n4096 in remote_cpu_queue). (2) pq_retained_v4=OOM+trigger-not-met (v3 HARD_FAIL binder=-0.2547 unimodal; v4 dead hypothesis; NO RETRY). (3) 6corpus_v1=ImportError+trigger-not-met (5corpus MIDDLE_BAND spacing_err=0.077; expansion premature). 0 ships. GPU=7 CPU=20 pending. All priorities covered.