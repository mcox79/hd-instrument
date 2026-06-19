# Preregs: Cycle 12 GPU Refill -- 10-cell batch

Date: 2026-06-02
Queue: overnight_queue (GPU)
Context: Queue empty; 3 failure rescues + 7 new cells.

---

## 1. a4_audit_during_training_v2_longer_timeout_v1

**Hypothesis:** kappa_3 detects training-injected anomaly within W <= 50 writes at 3-sigma.

**HARD-PASS:** HP1 (detection <= 50 writes) AND HP2 (latency <= 50) AND HP3 (FPR < 5%) in >= 4/5 seeds.

**HARD-FAIL:** HF1 (never detected within 200 writes) OR HF2 (FPR > 20%).

**MIDDLE:** detection 51-100 writes OR FPR 5-20%.

**Rescue from v1:** v1 timed out at 120s. v2 uses 600s timeout + per-step progress + reduced N_HUTCHINSON=200.

**Timeout estimate:** smoke_wall=2.1s, FULL_N/smoke_N=2 (512->1024), FULL_seeds/smoke_seeds=2.5, scaling=1.5. `ceil(1.5 * 2.1 * 2^1.5 * 2.5) = ceil(22.2)` -> 300s. Add margin for N_BASELINE_RUNS=20 (4x smoke): 300*4 = **timeout_s=1800**.

---

## 2. combo1_p3_dam_implicit_gram_v3_n8192_vram_friendly_v1

**Hypothesis:** COMBO-1 p=3 DAM implicit Gram with M=N*2 (VRAM fix) passes same HP gates as v3_gpu_fix at N=4096.

**HARD-PASS:** HP1 (MMD < 0.02) AND HP2 (|kappa3_resc - 1| <= 0.05) AND HP3 (slope <= 1.3) AND HP4 (cos >= 0.95).

**HARD-FAIL:** MMD >= 0.10 OR |kappa3_resc - 1| > 0.20 OR cos < 0.70.

**MIDDLE:** HP1+HP2+1 of HP3/HP4.

**Rescue from production_envelope_v1:** OOM at M=N*4 (64MB Gram x 4 buffers). Fix: M=N*2 only (537 MB Xi, ~570 MB total).

**Timeout estimate:** smoke_wall ~30s est, FULL/smoke N ratio = 2 (N=2048->4096 active), seeds=2.5x. `ceil(1.5 * 30 * 2^1.5 * 2.5) = 318` -> **timeout_s=600**.

---

## 3. pp49_hrc_counterfactual_depth_8_v1_n4096

**Hypothesis:** Counterfactual abduction valid at depth-8 on heteroassoc chain; precision >= 0.95 for cf_cos.

**HARD-PASS:** HP1 (cert_rate >= 0.85) AND HP2 (cf_cos >= 0.95) AND HP3 (audit >= 0.85) AND HP4 (ds_cos >= 0.70).

**HARD-FAIL:** hp1_cert_rate < 0.85 OR cf_cos < 0.40.

**MIDDLE:** 3/4 conditions.

**Rescue from depth-10:** OS exit 3221226505 (FAST_FAIL). Depth-8 between depth-5 HP and depth-10 fail.

**Timeout estimate:** depth-5 smoke ~5s. depth-8 is same order; FULL seeds 2.5x. `ceil(1.5 * 5 * 1 * 2.5) = 19` -> **timeout_s=600** (generous, N=4096 each chain has N^2 H matrix).

---

## 4. kappa3_sensitivity_sweep_n16384_v2_seed_diversity_v1

**Hypothesis:** sigma_separation >= 4.0 at N=16384 (fingerprint clearly distinguishable); v1 failure was seed-diversity issue.

**HARD-PASS:** mean_min_sigma_sep >= 4.0.

**HARD-FAIL:** mean_min_sigma_sep < 2.0.

**MIDDLE:** 2.0 <= min_sigma_sep < 4.0.

**v2 fix:** 10 seeds (was 5), same M_LIST and HP.

**VRAM budget:** Xi(53 MB) + Krylov(262 MB) = 315 MB. Safe.

**Timeout estimate:** FULL N=16384, 10 seeds, n_probes=1000. Krylov is fast; est ~30s/seed. `ceil(1.5 * 30 * 10) = 450` -> **timeout_s=1200**.

---

## 5. caching_v3_well_stressed_above_capacity_n4096

**Hypothesis:** r_eff monitor + eviction prevents accuracy collapse at alpha=0.22 > alpha_c=0.138. Monitor-triggered eviction prevents accuracy collapse at alpha > alpha_c.

**HARD-PASS:** Cell A (fid_eviction >= 0.80 AND fid_no_eviction <= 0.50) AND Cell B (alarm fires <= alpha_c write) AND Cell C (retained_fid >= 0.85) in >= 4/5 seeds.

**HARD-FAIL:** fid_eviction < 0.50 OR fid_no_eviction > 0.80 at alpha_stress.

**MIDDLE:** 2/3 cells.

**v3 fix over v2:** explicit above-capacity stress at alpha=0.22 (v2 was at alpha=0.049 < alpha_c).

**Timeout estimate:** N=4096, W matrix ops, 5 seeds. `ceil(1.5 * 30 * 1 * 2.5) = 113` -> **timeout_s=600**.

---

## 6. pp52_hebbian_lora_speedup_n4096_v1

**Hypothesis:** Hebbian matches GD+Adam within +-2pp AND speedup >= 100x at N=4096, M=400.

**HARD-PASS:** HP1 (delta <= 2pp) AND HP2 (wall_speedup >= 100x) AND HP3 (flops >= 400x) in >= 4/5 seeds.

**HARD-FAIL:** HF1 (acc_heb < 90% of GD) OR HF2 (speedup < 10x).

**Timeout estimate:** GD runs up to 5000 iters at N=4096 per seed. ~60-120s/seed est. `ceil(1.5 * 120 * 1 * 2.5) = 450` -> **timeout_s=1800**. Flagged as potentially long.

---

## 7. pp52_one_shot_addition_n4096_v1

**Hypothesis:** One-shot write adds patterns with immediate retrieval (cos >= 0.90) AND existing accuracy retention >= 95% at N=4096.

**HARD-PASS:** HP1 AND HP2 AND HP3 in >= 4/5 seeds.

**HARD-FAIL:** cos < 0.70 OR drop > 10pp OR write > 10s.

**Timeout estimate:** Quick experiment (one W build + K=10 writes). `ceil(1.5 * 20 * 1 * 2.5) = 75` -> **timeout_s=600**.

---

## 8. pp52_exact_rollback_n4096_v1

**Hypothesis:** W_rollback == W_original within 1e-6 relative error (fp32 precision); retained accuracy >= 0.95 at N=4096.

**HARD-PASS:** HP1 (rel_err < 1e-6) AND HP2 (acc >= 0.95) AND HP3 (rollback < 0.5s) in >= 4/5 seeds.

**HARD-FAIL:** rel_err >= 1e-4 OR drop > 5pp.

**Timeout estimate:** Quick; K=20 writes + K rollbacks at N=4096. `ceil(1.5 * 15 * 1 * 2.5) = 57` -> **timeout_s=600**.

---

## 9. combo1_pp48_audit_on_nkt_v2_depth_5_v1

**Hypothesis:** COMBO-1 implicit Gram audit produces discriminative certificates for depth-5 NKT structure (31 forbidden patterns).

**HARD-PASS:** HP1-HP4 in >= 4/5 seeds.

**HARD-FAIL:** cert_A > -0.50.

**MIDDLE:** 3/4 HP.

**v2 extension:** NKT_DEPTH=5 (31 patterns vs 15 in v1).

**Timeout estimate:** `ceil(1.5 * 20 * 1 * 2.5) = 75` -> **timeout_s=600**.

---

## 10. q_b1_chain_depth_30_v1_n8192

**Hypothesis:** Heteroassoc chain at depth-30 meets degradation envelope: d5 >= 0.95, d10 >= 0.88, d20 >= 0.70, d30 >= 0.55.

**HARD-PASS:** All 4 depth thresholds met.

**HARD-FAIL:** d5 < 0.80 OR d10 < 0.65 OR d20 < 0.40 OR d30 < 0.30.

**MIDDLE:** d30 in [0.40, 0.55) while earlier depths meet HP.

**Timeout estimate:** H matrix 268 MB at N=8192; 15 chains x 30 hops x 5 seeds. est ~120s/seed. `ceil(1.5 * 120 * 1 * 2.5) = 450` -> **timeout_s=1800**.
