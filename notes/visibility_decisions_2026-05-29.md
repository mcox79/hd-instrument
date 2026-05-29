# Visibility decisions 2026-05-29

## v269 -> v270 @ first post-reset cycle (BATCHED 6-VERDICT)

- bet_b_4stage_phaseD_aweight_v2 FOURSTAGE_MIDDLE_BAND ret_A=0.751 ret_B=0.852 ret_C=0.801 — 3RD STAGE-A SUB-0.80 PERSISTENCE (Bet B 4-stage row UNCHANGED annotation-only)
- saad_solla_v16_n8192 SS_V16_HARD_PASS 2/2 seeds x 2 M_frac at N=8192 — 4TH-AXIS PRODUCTION-SCALE Saad-Solla LEADING ✅ UNCHANGED, framework-reliability specific 68-81%->70-83% +2% LIFT
- axis1_mb_chunk8_v1_n4096 C8_MIDDLE_BAND ret_low=0.16 ret_high=0.13 pass_collapse=0/9 M/N=25-32 DEEP-OVER-CAP TAIL continuation (AXIS-1 row UNCHANGED annotation-only)
- kf3_multisub_v3_n8192 + t1_beta_sweep_v2_n8192 + t2_codebook_boundary_v2_n8192 ALL Kerdock-even-log2 SCRIPT_PRECONDITION_VIOLATION at import time (N=8192 log2=13 odd; script requires even log2) — 3 LABEL-VS-HONEST catches NEW sub-flavor SCRIPT_PRECONDITION_VIOLATION 124th-126th
- 1 CONSOLIDATED Kerdock-vuln structural rescue routing filed covering 6 anchors at N=4096 or N=16384 + upstream chunk9/chunk10/pb3_v4/t3_susceptibility_v2/kf2_be1-family audit
- Portfolio 14+31 UNCHANGED; HONEST 150->156 (+6); LABEL-VS-HONEST 123->126 (+3); 181st PROT-009 paired commit

## v270 -> v271 @ post-v270 catchup BATCHED 5-VERDICT

- kf1_hallu_rescue_v2_n4096 KF1T1_HARD_PASS 5 seeds x 3 M_fracs N=4096 above_thresh_frac=0 all 15 cells mean ratio_to_uniform=4.72x — FIRST PRODUCTION-SCALE 5-SEED KF-1 CONFIRMATION; KF-1 row green-smoke 55-70% -> green 65-80% LIFT +10%; framework-reliability product-feature 87-97% -> 88-97% LIFT +1% lower bound; RELIABILITY-RECALC EVENT
- pb3_extended_v4_n8192 PB3V4_HARD_FAIL FLAT_TAU_N8192 tau_recovery=0.0 ALL 15 cells (3 seeds x 5 betas) — FIRST CONTRADICTING EVIDENCE for PB-3 critical-slowing N-extension; row UNCHANGED pending 3 cheapest-first rescue sketches (audit -> N-down -> dtype)
- t3_susceptibility_v2_n8192 T3_MIDDLE_BAND 0/5 seeds all-3-chi >= 0.5 (only chi_cb 0.1-0.65; chi_M ~ 0; chi_beta = 0) HONEST middle-band (NOT Kerdock as caller guessed; ran 378s 5 seeds 30 cells) — saddle-cascade multi-axis signature ABSENT; ALSO 129th LABEL-VS-HONEST catch sub-flavor ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH (anchor `_n8192` vs config.N=4096 = PROT-018 enforcement gap)
- axis1_mb_chunk9_v1_n8192 + axis1_mb_chunk10_v1_n8192_fine BOTH Kerdock-even-log2 SCRIPT_PRECONDITION_VIOLATION at import time (N=8192 odd log2) — 127th + 128th LABEL-VS-HONEST catches; ABSORBED into v270 consolidated rescue routing (no new routing per upstream guidance)
- Portfolio 14+31 UNCHANGED; HONEST 156->161 (+5); LABEL-VS-HONEST 126->129 (+3); 182nd PROT-009 paired commit
- Pipeline-pacing: overnight=12 pending+1 running, remote_cpu=4 pending+1 running HEALTHY — NO refill dispatch


## v271 -> v272 @ BATCHED 13-VERDICT GPU drain event

- kf2_be1_{fp32,fp16,int8,int4,int2,int1}_n8192 ALL KF2_BE1_*_HARD_PASS max_iso<0.05 5/5 seeds — PER-CELL HONEST BUT STRATEGIC OVER-CLAIM 130th LABEL-VS-HONEST NEW sub-flavor STRATEGIC_INTERPRETATION_OVER_CLAIM (identical iso 0-0.02 across all 6 precisions = quantization-INSENSITIVE in operative regime; INT1 binary BETTER iso than FP32 = physics-impossible if quantization mattered; cost-advantage 32x narrative NOT validated at probe level; W-magnitude-operative retrieval test required); KF-2 row UNCHANGED with precision-floor strategic-OVER-CLAIM annotation
- region_c_kf1_n4096_beta64_mfrac4 + region_c_kf2_n4096_beta64_mfrac4 BOTH REGION_C_*_HARD_PASS 5/5 ret=1.000 — HONEST ferromagnet phase trivial pass
- region_d_kf1_n4096_beta64_mfrac12 + region_d_kf2_n4096_beta64_mfrac12 BOTH REGION_D_*_MIDDLE_BAND 5/5 mean_ret=0.3325 — HONEST over-cap collapse phase
- REGION C+D AGGREGATE finding: substrate KF-behavior BETA-INVARIANT IDENTICAL to A/B at beta=8 = STEERABLE-KILLER-FEATURE hypothesis NOT SUPPORTED at probe level (operational simplicity over steerability); killer-feature phase-class profile UNCHANGED with NEW annotation
- axis4_hyst_ramp_v1_n4096 AXIS4_HARD_FAIL max_loop_area=0.0 all 9 ramps NO RETENTION HYSTERESIS substrate M-history-INDEPENDENT — HONEST closure-level finding; UNSURE-section hysteresis-killer direction CLOSED at probe level with 2 rescue arms (high-beta multi-basin + near-critical M)
- axis2_codebook_density_v2_n4096_collapse AXIS2V2_MIDDLE_BAND retention M_frac-INVARIANT 0.62-0.66 across M_frac 4-20 every codebook class — HONEST over-cap ceiling re-confirmation; AXIS-2 row UNCHANGED
- saad_solla_v19_n4096_beta_sweep FAILED wall_s=4559 (76min substantive-not-timeout) NO REMOTE METRICS 5th-axis BETA disambiguation BLOCKED — Saad-Solla LEADING UNCHANGED 5th-axis DEFERRED; 3 cheapest-first rescue sketches inline (v20-style narrower-beta-retry + dtype-instrumented rerun + N=2048 smoke parallel)
- Portfolio 14+31 UNCHANGED; framework reliability product-feature 88-97% UNCHANGED specific 70-83% UNCHANGED general 73-83% UNCHANGED non-eq-stat-mech 66-76% UNCHANGED
- HONEST observations 161->167 (+6: V2 axis4 + V3 axis2 + V4-V9 kf2_be1 + V10-V11 region C + V12-V13 region D)
- LABEL-VS-HONEST catches 129->130 (+1 STRATEGIC_INTERPRETATION_OVER_CLAIM NEW sub-flavor compound catch covering kf2_be1 6-anchor cost-narrative as ONE strategic-narrative over-claim)
- Pipeline-pacing: GPU drained (overnight_queue 0 pending+running); per dispatch context caller has structural deep-strategy plan for 16h overnight refill — verdict_handler DEFERS refill dispatch per [[feedback-no-padding-experiments]] + [[feedback-verdict-arrival-is-queue-depletion-signal]]
- 0 NEW routings filed (5 rescue sketches inline; saad_solla v20-rerun candidate to be operationalized at strategy cycle)
- 183rd PROT-009 paired commit
v272->v273 ANNOTATION-ONLY: user-delivered triage strategy commit; 3 at-risk claims (BE-1 cost-advantage/steerability/Bet-B-arch) documented in cap_map annotation; A1 soft-readout BE-1 designated RUN-FIRST; 5-cluster overnight refill plan with TIER 1/2/3/4 allocation routed to exp_dev; no state moves until verdicts land

v273->v274 BATCHED 4-VERDICT Section-4 branching trigger: saad_solla_v20 FAILED CPU-TIMEOUT 2nd-strike 5th-axis STRUCTURAL CONSTRAINT G9 v18_n16384 RECOMMEND TRIM + t1_v3 T1V3_HARD_FAIL FLAT_BETA_C Cluster B1 LAST-CHANCE BETA-STEERABILITY CLOSED HONESTLY + t2_v3 T2V3_HARD_PASS 3/4 op-points Cluster B3 CODEBOOK-AXIS STEERABILITY CONFIRMED FIRST POSITIVE STEERABILITY AXIS + kf1_v3_n8192 FAILED Kerdock-even-log2 SCRIPT_PRECONDITION_VIOLATION 131st LABEL-VS-HONEST 1 rescue routing filed BSC-sub-cheapest; KF-5 narrative REFRAMED beta->codebook; killer-feature phase-class profile yellow 45-60->50-65 +5%; codebook-order phase boundary 55-68->60-73 +5%; framework reliability all bands UNCHANGED; portfolio 14+31 UNCHANGED; HONEST 167->170 (+3); LABEL-VS-HONEST 130->131 (+1); 185th PROT-009 paired commit


## v274 -> v275 @ post-v274 GPU+CPU drain wave BATCHED 10-VERDICT

- pb3_extended_v5_n4096 PB3V5_HARD_FAIL FLAT_TAU_N4096 tau_recovery=0.0 ALL 15 cells GENUINE-NOT-KERDOCK = PB-3 critical-slowing 2ND-STRIKE (v4_n8192 + v5_n4096 both flat); row UNCHANGED, 3 fresh rescue arms filed (R2 v3-IDENTICAL re-reproduction PRIMARY); routing strategy_request_to_exp_dev_v275_pb3_v6_rescue_axes filed
- axis4_hyst_critical_v2_n4096 AXIS4V2_HARD_FAIL max_loop_area=0.0 ALL 12 ramps at beta_c=10 = AXIS-4 hysteresis-killer direction 2ND-STRIKE (v272 at beta=8 + v275 at beta_c=10 both flat); UNSURE-section direction UNCHANGED, 3 fresh rescue arms inline (high-beta + codebook-variation + faster-ramp)
- kf2_isolation_proof_v2_n4096_audit KF2V2AUDIT_HARD_PASS_STANDARD max_iso=0.0202 < 0.05 25/25 cells N=4096 BSC Kerdock-safe = FIRST production-scale 5-seed STANDARD-PATH isolation proof; PARTIALLY DEFUSES v272 STRATEGIC_INTERPRETATION_OVER_CLAIM by establishing baseline divergence (standard within 30% theory_bound vs BE-1 quantization-INSENSITIVE)
- bid_m_normalized_v5_n8192 OUTSIDE_BANDS 6/6 fracs N=8192 production-scale 3-seed mean_bid=201.6 = M-NORMALIZED 2ND-N=8192-AXIS substrate-outside-Hopfield CONFIRMATION post-v269 STRUCTURAL TIMEOUT WALL; non-eq-stat-mech band 66-76% -> 67-77% (+1% lower bound) RELIABILITY-RECALC capped per lit-scan-calibration M-normalization-not-novel
- ortho_noneq_corroborator_v1 HARD_FAIL hs_ratio violated |hs-1.0|>6.0 ALL 5 seeds = HS-orthogonal-decomposition non-eq class EXCLUDED at probe level; non-eq-stat-mech direction UNCHANGED (HS exclusion is class-constraint not closure); surviving Crooks/Sagawa-Ueda/drift-diffusion-BP/free-probability candidates
- axis3_triplepoint_v2_n4096 AXIS3V2_MIDDLE_BAND global_max|delta_ret|=0.37 sign_divergence=False at deep-over-cap M_frac=10 beta=8 = no triple-point signature at probed point; row UNCHANGED, 3 rescue arms filed (near-phase-boundary + sign-divergence-finer + codebook-variation)
- kf3_cross_codebook_v1_n4096 KF3_CROSS_MIDDLE_BAND best_family=kerdock leak=0.01409 contam=0.05631 n_hp=0/15 = PARTIAL_ISOLATION cross-codebook at probe level; row UNCHANGED, 3 rescue arms filed (tighter HP_cont + kerdock-restricted sub-family + under-cap M_frac)
- axis2_codebook_density_v2_n4096_collapse AXIS2V2_MIDDLE_BAND class_spread_12=0.007 ret_8=ret_16 across bsc/hadamard/kerdock = REPRO of v272 outcome confirming M_frac-INVARIANT over-cap ceiling 0.62-0.65 REPRODUCIBLE; AXIS-2 row UNCHANGED
- kf5_steerable_beta_v2 KF5_HARD_PASS LABEL-OVER-CLAIM 132ND LABEL-VS-HONEST NEW SUB-FLAVOR STEERABILITY_PARTIAL_DECOUPLING (entropy_mono=5/5 ✅ + bpc_mono=0/5 ❌ + bpc_interior_min=5/5 ⚠️); "IS steerable" label collapses metric-decoupling; v274 codebook-axis-CONFIRMED + beta-axis-CLOSED reframe UNCHANGED on operational metric
- tcft_erase_time_v1_n2048 HARD_FAIL variance_ratio=0.0 ALL 75 cells N=2048 small-N TCFT erase-time mechanism null; row UNCHANGED, 3 N-scaling/M-scaling/et-resolution rescue arms filed
- Portfolio 14+31 UNCHANGED; framework reliability product-feature 88-97% UNCHANGED specific 70-83% UNCHANGED general 73-83% UNCHANGED non-eq-stat-mech 66-76% -> 67-77% (+1% LIFT)
- HONEST 170 -> 179 (+9: V1-V8 + V10 honest; V9 OVER-CLAIM caught)
- LABEL-VS-HONEST 131 -> 132 (+1 NEW SUB-FLAVOR STEERABILITY_PARTIAL_DECOUPLING)
- 1 NEW routing filed (strategy_request_to_exp_dev_v275_pb3_v6_rescue_axes_2026-05-29.md)
- Pipeline-pacing: GPU=17+1 running HEALTHY (A1/A2/B1/C1/C2 + 12 others pending); CPU=0 IDLE-by-design (no genuine open CPU work; PB-3 v6 routing GPU-side); NO refill dispatch
- 186th PROT-009 paired commit; verdict_handler sub-agent inline strategy+visibility no Agent sub-dispatch
