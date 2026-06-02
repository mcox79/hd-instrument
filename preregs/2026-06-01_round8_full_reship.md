# Pre-registration: Round 8 Full Re-ship (I-1 fix)

**Date:** 2026-06-01
**Reason:** I-1 infra fix -- remote runner_v2_prod.py lacked HDLAB_RUN_MODE=full in child_env.
**Fix applied:** SSH patch to C:/dev/hd-instrument/experiments/runner_v2_prod.py line 343.
**Self-test:** PASS -- child_env line confirmed present post-patch.
**Re-ship suffix:** _full_v2 appended to allow-duplicate bypass for completed entries.

## Timeout estimate method

`timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))`

All are CPU experiments (remote_cpu_queue). Minimum timeout_s = 300.

---

## ct2_outlier_count_full_v2

**Tests:** CT-2 free-Poisson framework: eigenvalue rank and edge convergence.
**Smoke elapsed:** 22.4s at N=4096, 2 seeds, 2 alphas.
**Full config:** 5 seeds, 5 alphas, N_scaling_grid [256,512,1024,2048,4096].
**Timeout:** ceil(1.5 * 22.4 * (5/2) * (5/2)) = ceil(1.5*22.4*6.25) = ceil(210) = **300s**

**HARD-PASS:** rank_test_pass=True (all M nonzero eigenvalues, all (N,alpha) combos) AND mean_edge_error < 0.05 at N=4096, 5/5 seeds. Convergence direction True.
**MIDDLE-BAND:** rank_test_pass=True but mean_edge_error in [0.05, 0.15] OR 3-4/5 seeds.
**HARD-FAIL:** rank_test_pass=False OR mean_edge_error > 0.20 at N=4096, or convergence direction False in majority.

No prior empirical anchor at full 5-seed grid; bands reflect calibration-probe policy (smoke passed narrow criteria).

---

## c_infty_seb_detection_full_v2

**Tests:** C_infty SEB detection via spectral gap analysis at N=2048.
**Smoke elapsed:** 0.78s at 2 seeds.
**Full config:** 5 seeds, N=2048 (GPU-capable but runs CPU).
**Timeout:** ceil(1.5 * 0.78 * (5/2)) = ceil(2.9) = **300s**

**HARD-PASS:** SEB detection rate >= 0.80 at alpha=0.05, 4/5 seeds confirm.
**MIDDLE-BAND:** detection rate [0.60, 0.80] or 3/5 seeds.
**HARD-FAIL:** detection rate < 0.40 or 0/5 seeds confirm.

---

## matrix_trace_primitives_full_v2

**Tests:** Matrix trace primitive accuracy (tr(W^k) correlates with computed trace).
**Smoke elapsed:** 4.12s at 2 seeds.
**Full config:** 5 seeds.
**Timeout:** ceil(1.5 * 4.12 * (5/2)) = ceil(15.5) = **300s**

**HARD-PASS:** trace_r2 > 0.90 at 4/5 seeds across K_GRID.
**MIDDLE-BAND:** trace_r2 in [0.70, 0.90] or 3/5 seeds.
**HARD-FAIL:** trace_r2 < 0.50 or 0/5 seeds.

---

## spectral_mp_primitives_full_v2

**Tests:** Marchenko-Pastur spectral primitive: lambda_plus formula at N_MAIN=4096.
**Smoke elapsed:** 3.1s at N=1024, 2 seeds.
**Full config:** N=4096, 5 seeds.
**Timeout:** ceil(1.5 * 3.1 * (4096/1024)^1.5 * (5/2)) = ceil(1.5*3.1*8*2.5) = ceil(93) = **300s**

**HARD-PASS:** Z_clean >= 10 at 4/5 seeds; lambda_plus error < 0.02.
**MIDDLE-BAND:** Z_clean [3,10] or 3/5 seeds.
**HARD-FAIL:** Z_clean < 3 or lambda_plus error > 0.10.

---

## r_alpha_throughput_full_v2

**Tests:** Retrieval retention R(alpha) throughput sweep at N=4096, full alpha grid.
**Smoke elapsed:** 0.06s at N=512, 2 seeds, 4 alphas.
**Full config:** N=4096, 5 seeds, 12 alphas.
**Timeout:** ceil(1.5 * 0.06 * (4096/512)^1.5 * (5/2) * (12/4)) = ceil(1.5*0.06*22.6*7.5) = ceil(15.2) = **300s**

**HARD-PASS:** mean_R_low_alpha > 0.97 at 4/5 seeds; monotone decay confirmed.
**MIDDLE-BAND:** mean_R_low_alpha in [0.90, 0.97] or 3/5 seeds.
**HARD-FAIL:** mean_R_low_alpha < 0.80 or majority non-monotone.

---

## capacity_cliff_graceful_full_v2

**Tests:** Graceful capacity cliff: monotone R(alpha) decay with cliff at alpha_c.
**Smoke elapsed:** 0.099s at N=512, 2 seeds.
**Full config:** N=512 (N_SMOKE=512 in both modes), 5 seeds, fine alpha grid.
**Timeout:** ceil(1.5 * 0.099 * (5/2) * (12/5)) = ceil(0.89) = **300s**

**HARD-PASS:** n_monotone=5/5 seeds; cliff_found=True at alpha >= 0.10.
**MIDDLE-BAND:** n_monotone=3-4/5 seeds; cliff_found partial.
**HARD-FAIL:** n_monotone < 3/5 or no cliff found in majority.

---

## csp_memory_warm_start_full_v2

**Tests:** CSP warm-start from memory: convergence speedup with stored initialization.
**Smoke elapsed:** 0.65s at 2 seeds, 5 instances.
**Full config:** 5 seeds, 10 instances.
**Timeout:** ceil(1.5 * 0.65 * (5/2) * (10/5)) = ceil(4.9) = **300s**

**HARD-PASS:** warm-start convergence >= 20% faster than random init, 4/5 seeds.
**MIDDLE-BAND:** 10-20% speedup or 3/5 seeds.
**HARD-FAIL:** no speedup or degradation in majority seeds.

---

## planted_csp_viability_full_v2

**Tests:** Planted CSP viability: substrate correctly stores/retrieves planted satisfying assignment.
**Smoke elapsed:** 0.095s at 2 seeds.
**Full config:** 5 seeds.
**Timeout:** ceil(1.5 * 0.095 * (5/2)) = ceil(0.36) = **300s**

**HARD-PASS:** retrieval_acc > 0.90 at 4/5 seeds, planted assignment recovered.
**MIDDLE-BAND:** retrieval_acc [0.70, 0.90] or 3/5 seeds.
**HARD-FAIL:** retrieval_acc < 0.50 or 0/5 seeds successful.
