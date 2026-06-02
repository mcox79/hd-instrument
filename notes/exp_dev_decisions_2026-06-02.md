# exp_dev Decisions 2026-06-02

## Batch: Overnight Cycle 1 completion (post-compaction)

**Context:** Context compaction occurred mid-cycle. Resuming from the 9-script pre-smoke stage.
Verified smoke on all 10 candidates. 7 shipped, 3 dropped.

---

## SHIPPED (7/10)

1. **spectral_zstat_v2** (HARD_PASS smoke 26s) -- remote_cpu_queue timeout=900s
   - Fix from v1: sequential O(k*N^2) outer product loop replaced with vectorized dups.T @ dups / N
   - Spectral Z-stat is now the correct architecture

2. **kappa3_hutchinson_v1** (HARD_PASS smoke <5s) -- remote_cpu_queue timeout=1800s
   - Q-C3: kappa_3 free-cumulant fingerprint for Hopfield vs GOE discrimination
   - min_sigma_sep=12.5 at smoke scale; theory_ratio=12.59 (calibration probe, HP_MATCH=20x)

3. **implicit_gram_solve_v1** (HARD_PASS smoke <5s) -- remote_cpu_queue timeout=1800s
   - Q-A4: Gram-solve retrieval equivalent to Hopfield, memory ratio 0.00015 vs 1.0

4. **frobenius_symdiff_verify_v1** (HARD_PASS smoke <5s) -- remote_cpu_queue timeout=600s
   - Corrected formula: ||W_A-W_B||^2 ~ |symdiff| (not /N); empirical rel_err=0.001

5. **effective_rank_sweep_v1** (HARD_PASS smoke <5s) -- remote_cpu_queue timeout=600s
   - r_eff = exp(H(sigma)) monotone in M: frac_monotone=1.00, mean_r_eff/M=0.966

6. **conformal_reject_option_v1** (HARD_PASS smoke <5s) -- remote_cpu_queue timeout=600s
   - Q24: split CP coverage guarantee. Fixed upper->lower quantile direction. frac_pass=1.00

7. **heteroassoc_chain_depth3_v1** (HARD_PASS smoke 102s) -- remote_cpu_queue timeout=3600s
   - Q-B1: depth-3 heteroassociative chain + cert deletion. d3=0.997, d2_after=-0.008

---

## DROPPED (3/10) -- routed to Strategy for redesign

### pp31c_knee_v3_widegrid -- INSTRUMENTATION_SUSPECT
- Root cause: precision-vs-coverage curve is CONSTANT (all precisions identical) because
  system is far below capacity (M=50, N=8192). No precision-coverage tradeoff exists here.
  Score distribution tightly clustered at 0.70 (1-2*0.15), and ALL queries retrieve
  correctly regardless of tau threshold.
- Signal: PP-31c requires a near-capacity operating regime to create a detectable knee.
  At M=50/N=8192 = 0.006 load, Hopfield is perfect at all tau values.
- Strategy routing: redesign needs near-capacity M or heterogeneous noise levels.

### tau_mem_decay_sweep_v1 -- HARD_FAIL at smoke
- Root cause: tau_emp / tau_theory = 30x (30x off from prediction).
  Formula tau_mem = N/(2*lambda) assumed single-pattern isolation, but our simulation
  has M_eff = lambda/gamma = 10 concurrent background patterns creating interference.
  The SDE model does not match the simulation setup.
- Signal: theory is wrong for the simulated regime.
- Strategy routing: need proper multi-pattern SDE theory or isolate single-pattern decay.

### signed_am_b_pattern_full_v1 -- HARD_FAIL at smoke
- Root cause: repulsion_rate=0.000 at M_A=20, M_B=5, N=4096.
  B-patterns converge TO xi_B (cos_sim > 0.5 in all trials) rather than diverging.
  W_A (20 patterns) creates interference that prevents effective B-pattern repulsion.
  The W_A random field at xi_B location is larger than the W_B penalty.
- Signal: signed-AM repulsion requires M_A << N for B-patterns to be actual energy maxima.
- Strategy routing: test with M_A=1-3, M_B=1 (clean case) to confirm theory, then scale.

---

## PROT-021 NOTE
Stale local partials from earlier wrong-tau-grid runs contaminated pp31c smoke results.
PROT-021 checks N/M/run_mode but not custom fields like tau_min. Cleared manually.
Recommendation: add tau_min (and other config-discriminating fields) to PROT-021 check keys
in _seed_checkpoint.py, or add a per-experiment config_hash field.

---

Generated: 2026-06-02
exp_dev cycle 3: shipped 11 anchors (1 kappa3 fix + 10 new) to remote_cpu_queue. Root cause of kappa3_hutchinson_v1 timeout: Python for-loop over n_probes=5000 x 3 O(N^2) sequential ops at N=4096; fixed by vectorized batch DGEMM in v2 (100x speedup, 6.3s smoke vs 1800s timeout). Walk-back gate on lru_decay_kendall_v1 (tau=0.882 at smoke, within 20% of HP=0.90, FULL uses 5 seeds). All 11 remote-verified via queue_add.sh exit-0 + VERIFIED log lines.## Cycle 4 overnight batch (2026-06-02)

Shipped 8/10 anchors to remote_cpu_queue. Dropped 2 from original plan plus replaced q19 redesign needed:

DROPPED:
- graph_link_prediction_v1: AUC~0.5 at smoke -- fundamental mechanism failure. Asymmetric W cosine probe non-discriminative for link prediction when nodes have multi-outgoing edges (superposition destroys discrimination). AUROC formula was verified correct; the physics does not support this use case.
- timeseries_xor_fullscale_v2: SUSPICIOUS_RESULT gate -- all-zero metrics (in_acc=0.000, contam=0.000) at smoke N=4096.
- q19_aging_mu_high_res_v1: Smoke HARD_FAIL -- Phi(t_w) increases with t_w (mu=-0.40 negative). The plateau measurement at fixed T_MAX=200 captures time-lag artifact (states closer in time when t_w approaches T_MAX) not genuine aging signature. Redesign required (full-aging C(t,t_w) as function of t/t_w).

SHIPPED (all 8 REMOTE VERIFIED in queue.json):
- substrate_metric_norm_axioms_v1 (120s timeout) -- Frobenius axioms PP-41; smoke HARD_PASS
- write_back_dirty_bits_v1 (120s) -- dirty-bit write-back; smoke HARD_PASS
- write_around_routing_v1 (120s) -- cosine-probe routing; smoke HARD_PASS
- per_key_ttl_external_required_v1 (120s) -- Tier2-NEGATIVE TTL constraint; smoke HARD_PASS
- eviction_id_external_codebook_v1 (300s) -- Tier2-NEGATIVE eviction codebook; smoke HARD_PASS
- q22_batched_deletion_correlated_v1 (3600s) -- ghost-attractor at c=0.3-0.5; walk-back seeds 5->10
- multiagent_coord_competing_v1 (900s) -- write-count priority at 71% capacity; smoke HARD_PASS
- program_exec_audit_chain_v1 (600s) -- 3-cell audit chain; smoke HARD_PASS

Status at ship time: substrate_metric_norm_axioms_v1 and write_back_dirty_bits_v1 already completed (ran during shipping window).
Cycle 5 Batch 10: shipped 10 anchors to remote_cpu_queue. Q19 rescue (CK scaling collapse, smoke HARD_PASS). Q9 rescue (state-vector SDE, 10-seed walk-back). Caching: write_allocate HARD_PASS, capacity_aware_eviction MIDDLE_BAND, multi_substrate_hierarchy HARD_PASS. SWR replay HARD_PASS. Multiagent adversary HARD_PASS. Graph community 10-seed walk-back. Branching audit 10-seed walk-back. Q21 R-envelope FULL 4 targets. Remote verify: all 10 exit-0 + VERIFIED.Q-F1 dynamical_um_ck_class_v1 SHIPPED remote_cpu_queue: smoke HARD_PASS M_dyn=0.9246 wall=371.8s timeout=4800s; Q-F2 two_time_correlator_fdt_v1 SHIPPED remote_cpu_queue: smoke HARD_PASS collapse_mse=0.0048 piecewise_r2=0.9826 wall=0.2s timeout=1800s; Q-F3 cophenetic_um_rescue_v1 BLOCKED smoke HARD_FAIL mean_cophenetic=0.4787 routed to Strategy (P=20 too small, alpha=0.019 noise-dominated); Q-F4 q_f4_saddle_um_v1 BLOCKED INSTRUMENTATION_SUSPECT minima_ratio=1.0095 outside [0,1] routed to Strategy (N=512 noise-dominated); 9 smoke-only parked anchors from v330 confirmed already in queue from 04:39 cycle
## 2026-06-02 SHIP CYCLE: 8 Rescue Anchors (5 shipped, 2 genuine HF, 1 in-flight skip)

### Shipped 5/8 to remote_cpu_queue

**HARD_PASS smokes:**
- timeseries_xor_prot021_fix_v1: in_acc=1.000 contam=0.000 elapsed=7.8s. Root fix: v2 bundle-for-in-window architecture reverted to v1 individual tau_t queries. PROT-021 run_config updated.
- signed_am_b_pattern_m_sweep_v1: repulsion_rate=1.000 mean_cos_step1=-1.000 at ALL M_A=[1,5,20]. Root fix: KeyError mean_cos_final->mean_cos_step1; one-step dynamics confirmed. elapsed=4.3s.
- chi_sg_replica_arch_v1: gamma=0.757 > HP=0.5. Block Glauber (stochastic half-spin updates) replaces old sequential (240s/seed) and fully-parallel (oscillates). elapsed=24.1s. PROT-021 updated with T_THERM/T_MEAS/R/Q.

**MIDDLE_BAND smokes (justified ship):**
- graph_link_prediction_per_edge_keying_v1: AUC=0.970 >> HP=0.75 at 2 seeds; HP needs 3. FULL expected HARD_PASS. elapsed=41s.
- pp31c_knee_near_capacity_v1: delta_ratio=1.2 borderline < HP=2.0, tau_knee=0.39 below HP_TAU_LOW=0.50. Walk-back gate: doubled FULL N_QUERIES_PER_NOISE 50->100. Mixed-noise function added to create heterogeneous score distribution.

### Genuine HARD_FAILs dropped (2):
- q_f3_cophenetic_um_high_p_v1: cophenetic=0.143 << HF=0.55. Random BSC patterns have no hierarchical structure regardless of P. Feature requires correlated patterns.
- q_f4_saddle_um_n_filter_v1: denom>0.10 filter removes ALL 500 triples. Saddle proxies have pairwise overlap ~0.022-0.05 < filter=0.10. Filter is too aggressive; lowering it reintroduces noise contamination. Feature needs different saddle detection approach.

### Skipped (1):
- q9_tau_mem_corrected_sde_v1: already in-flight from prior cycle.

### Key bugs fixed this cycle:
1. signed_am KeyError: result['mean_cos_final'] -> result['mean_cos_step1']
2. pp31c: old compute_precision_coverage removed, replaced with compute_precision_coverage_mixed (heterogeneous noise fracs)
3. pp31c: stale checkpoint (no run_config key) deleted manually
4. chi_sg: sequential O(N^3) Glauber replaced with block Glauber O(N^2) per step
5. chi_sg: PROT-021 run_config updated to include T_THERM, T_MEAS, R_DISORDER, Q_REPLICAS

### Remote verify: 5/5 pass (confirmed in data/remote_cpu_queue/queue.json pending list)
exp_dev cycle 6: shipped 8/10 to remote_cpu_queue. q_f5 MIDDLE_BAND smoke (dft_snr=2.32, frac_osc=0.065); q_f6 shipped as calibration probe despite smoke BI noise; f4_free_cumulants COMPLETED HARD_FAIL N=1024 (m1~0 due to diagonal removal formula mismatch, redesign needed); caching_lru_lfu_hybrid COMPLETED MIDDLE_BAND (rho=0.732, recency-only signal, B=0/5); caching_admission_control shipped for N=1024 cliff; caching_eviction_cost_amortized HARD_PASS smoke (3/3, speedup=10.7x); hippocampal_place_field HARD_PASS smoke (3/3, cosine=0.879); dropped: substrate_spectral_health_check (Z-score formula mismatch), tau_mem_m_sweep (T_MAX<<tau_theory), multiagent_emergence (HARD_FAIL smoke 2/3, LAMBDA_SHARED redesign needed); self-test early-exit bug fixed across all 8 scriptsWave1+Wave2 batch: shipped 5/10 anchors (kappa3_hutchinson_n8192_smoke_v1[cpu], q_c5_cosine_gate_tau_recal_v1[cpu], combo3_unified_api_v1_n4096[gpu], q_b1_heteroassoc_chain_cert_v1_n4096[gpu], q_b1_heteroassoc_chain_cert_v1_n8192[gpu]); blocked 4 at smoke (q_f3_cophenetic genuine HF c=0.14, combo1_p3 HP2 kappa_3 Gram identity fails, q_c2_mp_hc empirical null needed, streaming_aging measurement design flaw); all 5 ships REMOTE VERIFIED; strategy upstream push filed at notes/exp_dev_to_strategy_smoke_fails_wave1_wave2_2026-06-02.md
## Batch ship: 9-cell overnight queue refill (context resumed 2026-06-02)

### Shipped anchors
OVERNIGHT_QUEUE (GPU, 4 anchors):
- combo4_dynamical_bundle_v1_n1024 (1200s): CK dynamical ultrametricity + aging collapse. SMOKE MIDDLE_BAND (M_dyn=1.19, mse=0.005). PROT-018 OK N=1024.
- q_c2_mp_hc_v2_corrected_n4096 (14400s): Empirical Wishart null for finite-N MP edge. SMOKE HARD_PASS (Z=-0.78). PROT-019: 14400s floor.
- combo1_p3_dam_implicit_gram_v2_identity_fix_v1 (14400s): p=3 Gram with CV-based HP2 stability check. SMOKE 3/4 HP. No _nN suffix; production N=4096.
- q_a3_l2_cross_layer_composition_v1_n4096 (14400s): L=2 Hadamard binding composition. SMOKE HARD_PASS (all fidelities=1.0). PROT-018 OK N=4096.

REMOTE_CPU_QUEUE (5 anchors):
- streaming_brand_gram_refresh_v1 (120s): Incremental Gram refresh algebraic identity. SMOKE HARD_PASS (min_acc=1.0).
- kappa3_monitor_detection_latency_v1 (600s): kappa_3 Hutchinson monitor detection. SMOKE HARD_PASS (W=1.8).
- drift_kernel_kappa3_detection_v1 (600s): Gradual drift detection via kappa_3. SMOKE HARD_PASS (W=1.5).
- hippocampal_place_field_full_v1_n4096 (14400s): Place-field FULL N=4096. SMOKE HARD_PASS.
- q_f4_saddle_overlap_correlated_v1 (1200s): Saddle ultrametric with correlated patterns. SMOKE MIDDLE_BAND (ratio=0.736).

### Blocked
- caching_admission_control_v2: SMOKE HARD_FAIL. At N=512, alpha_eff proxy never reaches threshold; all patterns admitted. No capacity cliff visible. Routed to strategy.

### Root causes fixed this cycle
1. GATE TIMEOUT root cause: scripts lacked self-test early exit. Gate timeout=180s; production sweeps run at full N when --self-test passed. Fix: added sys.exit(0) after _instrumentation_selftest() in all 7 scripts (combo4, q_c2, combo1_p3, kappa3_monitor, drift_kernel, hippocampal, q_a3_l2, q_f4).
2. PROT-019: q_c2 _n4096 timeout was 2700s (below 14400s floor). Fix: raised to 14400s.
3. combo4 wall-time: Glauber dynamics at N=4096 requires ~28800s. Fix: renamed to _n1024 production.
