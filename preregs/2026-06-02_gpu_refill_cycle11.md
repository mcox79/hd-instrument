# GPU Refill Cycle 11 -- Pre-registrations (2026-06-02)

## Summary
10 GPU anchors to overnight_queue. All smoke=SKIP (no local CUDA; CUDA guard confirmed in all scripts).

---

## 1. wave5_cell5_combo1_n65536_LOCAL_stretch_v1

**Queue:** overnight_queue | **N:** 65536 | **Seeds:** 5 | **Script:** experiments/exp_wave5_cell5_combo1_n65536_LOCAL_stretch_v1.py

**Hypothesis:** COMBO-1 p=3 DAM implicit Gram-solve scales to N=65536 LOCAL GPU with matrix-free operations (alpha=0.05, M=3277, no N x N materialization).

**HP:** MMD < 0.02 AND kappa3_resc within 5% of 1.0 AND write_slope <= 1.3 AND mean_cos >= 0.95.
**HF:** MMD >= 0.10 OR |kappa3_resc - 1.0| > 0.20 OR cosine < 0.70 OR OOM.
**MIDDLE:** HP1+HP2+one of HP3/HP4.

**OOM handling:** Script has VRAM guard at 6.5 GB; if OOM, HARD_FAIL with N_max routing to Strategy.
**Multi-scale smoke:** N_smoke=4096 AND N_smoke*4=16384 both run in smoke mode.

## Timeout estimate
Prior: wave5_cell5_combo1_n32768_local_v1 elapsed (unknown). Similar matrix-free p=3 at n32768: ~100s estimated.
N-scaling from 32768->65536 at scaling_exp=1.5: 1.5 * 100 * (65536/32768)^1.5 * (5/5) = 1.5 * 100 * 2.83 = 424s.
Round up to 600s. Adding 50% OOM margin = **900s timeout**.

---

## 2. combo2_p4_l3_signed_am_v1_n32768_5seed_verification_v1

**Queue:** overnight_queue | **N:** 32768 | **Seeds:** 5

**Hypothesis:** COMBO-2 p=4 DAM L3 signed-AM at N=32768 produces confirmed HARD_PASS in production-lock 5-seed verification.

**HP:** l3_fidelity_A >= 0.85 AND b_repulsion_rate >= 0.95 AND parity_contamination <= 0.05.
**HF:** l3_fidelity_A < 0.50 OR b_repulsion_rate < 0.50.
**MIDDLE:** 2/3 conditions.
**Prior:** combo2_p4_l3_signed_am_v1_n32768 HARD_PASS (completed). This is band-LIFT eligibility verification.

## Timeout estimate
Prior n32768 elapsed: ~1-3s (algebraic closed-form). Estimated: 5s * 5/5 * 1.0 = 5s.
With padding = **300s timeout** (minimum).

---

## 3. combo3_unified_api_v1_n32768_5seed_verification_v1

**Queue:** overnight_queue | **N:** 32768 | **Seeds:** 5

**Hypothesis:** COMBO-3 5-method unified audit API matches closed-form at N=32768 in explicit 5-seed production-lock.

**HP:** all 3 trace metrics within rel 1e-6. **HF:** any > 1e-2. **MIDDLE:** all within 1e-4.
**Prior:** combo3_unified_api_v1_n32768_local HARD_PASS.

## Timeout estimate
Prior n32768 local elapsed ~30-60s. Formula: 1.5 * 60 * 1.0 * 1.0 = 90s. Round to **300s timeout**.

---

## 4. q_b1_chain_depth_20_v1_n8192

**Queue:** overnight_queue | **N:** 8192 | **Seeds:** 5

**Hypothesis:** Heteroassoc chain depth-20 at N=8192 maintains fidelity >= 0.70 at depth-20.

**HP:** d5 >= 0.95 AND d10 >= 0.88 AND d15 >= 0.80 AND d20 >= 0.70.
**HF:** d5 < 0.80 OR d10 < 0.65 OR d15 < 0.50 OR d20 < 0.40.
**MIDDLE:** d20 in [0.55, 0.70) while others meet HP.

## Timeout estimate
Prior q_b1_chain_depth_15_v1_n8192 elapsed ~unknown; estimate depth-15 at N=8192 ~120s for FULL.
Depth-20: 1.5 * 120 * 1.0 * 1.0 = 180s. Round to **600s timeout**.

---

## 5. pp48_nkt_depth_7_v1_n4096

**Queue:** overnight_queue | **N:** 4096 | **Seeds:** 5

**Hypothesis:** PP-48 NKT at depth-7 (127 forbidden patterns) maintains pos_retrieval >= 0.85, nkt_repulsion >= 0.80, tree_structure >= 0.80.

**HP:** all 3 conditions. **HF:** pos < 0.50 OR nkt_rep < 0.50. **MIDDLE:** 2/3.

## Timeout estimate
Prior depth-5 at N=4096 ~30s. Depth-7 adds more patterns: 1.5 * 30 * 1.0 * 1.0 = 45s. Round to **300s timeout**.

---

## 6. pp49_hrc_counterfactual_depth_5_v1_n4096

**Queue:** overnight_queue | **N:** 4096 | **Seeds:** 5

**Hypothesis:** PP-49 counterfactual abduction at depth-5 (backed off from depth-10 FAST_FAIL) maintains hp1_cert_rate >= 0.85 AND cf_cos >= 0.60.

**HP:** hp1_cert_rate >= 0.85 AND cf_cos >= 0.60 AND hp3_audit >= 0.85 AND ds_cos >= 0.70.
**HF:** hp1_cert_rate < 0.85 OR cf_cos < 0.40.
**MIDDLE:** 3/4 conditions.
**Calibration:** no prior depth anchor; wider bands +-50% of predicted cosine >= 0.60.

## Timeout estimate
Prior depth-10 FAILED at 12.6s (FAST_FAIL). Depth-5: lighter. Estimate 60s for FULL. Round to **300s timeout**.

---

## 7. q_a3_l6_cross_layer_composition_v1_n4096

**Queue:** overnight_queue | **N:** 4096 | **Seeds:** 5

**Hypothesis:** L=6 cross-layer Hadamard composition at N=4096 maintains all level fidelities >= 0.90 AND l6_acc >= 0.60.

**HP:** 6/6 fidelities >= 0.90 AND l6_acc >= 0.60. **HF:** any fidelity < 0.55 OR l6_acc < 0.30.
**MIDDLE:** 5/6 or l6_acc in [0.30, 0.60).
**Prior:** L=5 HARD_PASS at N=4096. Bands relaxed vs L=5 (HP_L5=0.70 -> HP_L6=0.60).

## Timeout estimate
Prior L=5 at N=4096 ~30-60s. L=6 adds one more layer: 1.5 * 60 * 1.0 * 1.0 = 90s. Round to **300s timeout**.

---

## 8. combo1_pp48_audit_on_nkt_v1_n4096

**Queue:** overnight_queue | **N:** 4096 | **Seeds:** 5

**Hypothesis:** COMBO-1 implicit Gram audit produces valid certificates when applied to PP-48 NKT-structured signed-AM W_signed = W_A - W_B: cert_A ~ -1.0 for positive patterns AND cert_B_leaf > 0 for forbidden patterns.

**HP:** cert_A within 0.20 of -1.0 AND cert_B_positive_rate >= 0.80 AND kappa3_A > 0.001 AND cndc_disc >= 0.05 in >= 4/5 seeds.
**HF:** cert_A > -0.50 OR cert_B_positive_rate < 0 in >50% seeds.
**MIDDLE:** 3/4 conditions.
**P_deflated:** 0.60 (signed-AM application is novel; algebra proven but NKT cert sign is new test).

## Timeout estimate
Estimate similar to pp48_nkt at N=4096 ~30s per seed. Formula: 1.5 * 30 * 1.0 * 1.0 = 45s. Round to **300s timeout**.

---

## 9. combo3_pp51_5method_on_implicit_gram_v1_n4096

**Queue:** overnight_queue | **N:** 4096 | **Seeds:** 5

**Hypothesis:** COMBO-3 5-method audit API is self-consistent between N-side Krylov and M-side Gram eigenvalue pathways (PP-51 architecture) with relative error < 1e-4 on all trace metrics.

**HP:** all 5 HP (trace HP1-3, cert HP4, matvec HP5) in >= 4/5 seeds.
**HF:** any trace diverges by > 1e-2 OR deletion cert off by > 0.10.
**MIDDLE:** 4/5 conditions.
**P_deflated:** 0.65 (PP-51 M-side equivalence proven; first substrate-level confirmation).
**Composition classification:** PIPELINE.

## Timeout estimate
COMBO-3 n4096 prior elapsed ~5-10s. With 5 seeds: 1.5 * 10 * 1.0 * 1.0 = 15s. Round to **300s timeout**.

---

## 10. wave4_full_streaming_battery_n8192_v1

**Queue:** overnight_queue | **N:** 8192 (no _n suffix per PROT-018 rule 3) | **Seeds:** 5

**Hypothesis:** Wave 4 streaming battery at production N=8192 with GPU maintains mean_fidelity >= 0.70 and streaming primitives compose without interference.

**HP:** HP1 mean_fid >= 0.70 AND HP2 min_fid >= 0.40 AND HP3 min_reff > 0.20*W_WIN AND HP4 cert=-1.0 in >= 4/5 seeds.
**HF:** mean_fid < 0.40 (streaming collapsed).
**MIDDLE:** 3/4 conditions.
**GPU check:** VRAM > 100 MB at peak (assert in script).
**P_deflated:** 0.55 (first N=8192 streaming composition).

## Timeout estimate
Wave4 battery at N=1024 T=300: ~30-60s per seed. At N=8192 T=200 (reduced): matrix ops scale as N^2 -> 1.5 * 60 * (8192/1024)^2 * (5/5) * (200/300) = 1.5 * 60 * 64 * 0.67 = 3840s > 14400? No: 3840s < 4 hours.
More carefully: each step at N=8192 does 1 matvec (268MB). 200 steps * 5 seeds = 1000 matvecs. At GPU throughput this should be ~30-60s per seed. Estimate 1.5 * 60 * 5 = 450s total. Round to **900s timeout**.

Note: If wall > 7200s, flag visible to user.
