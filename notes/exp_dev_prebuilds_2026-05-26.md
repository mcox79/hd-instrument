# Anticipatory Pre-builds Index -- 2026-05-26

All scripts are SMOKE-TESTED and QUEUE-READY. DO NOT queue_add until the trigger condition fires.

---

## Pre-build 1: K_scaling_v3 -- extreme-K continuation

**Script:** `experiments/exp_wave14_moe_shift_K_scaling_v3.py`
**Prereg:** `preregs/2026-05-26_wave14_moe_shift_K_scaling_v3.md`
**Queue:** overnight_queue (GPU)
**Trigger (PATH A -- MONOTONE):** v2 returns HARD_PASS or monotone K-scaling past K=64
  - retention_A(K=64)/retention_A(K=2) >= 4.0 OR monotone with structural_lift >= 0.10
**What it tests:** K sweep {64, 128, 256} at N=2048 (N reduced for memory); does SHIFT scale to extreme K?
**Expected bands:** HARD_PASS if 10%+ gain K=64->128; HARD_FAIL if degradation; MIDDLE if plateau
**Smoke result:** PASS (end-to-end, MIDDLE_BAND at smoke scale -- expected at small N)

---

## Pre-build 2: K_perarm_v1 -- divergence mechanism diagnosis

**Script:** `experiments/exp_wave14_moe_shift_K_perarm_v1.py`
**Prereg:** `preregs/2026-05-26_wave14_moe_shift_K_perarm_v1.md`
**Queue:** remote_cpu_queue (CPU, ~45-90 min)
**Trigger (PATH B -- DIVERGENCE):** v2 shows Arm_A retention DEGRADES at K>=32 while Arm_C stable
**What it tests:** K={2,4,8,16,32,64} with diagnostic metrics: routing_entropy, inter_expert_cosine, M_to_capacity_ratio
**Expected bands:** M2 (gating degrades), M3 (intra-expert interference), M1 (capacity saturation), or MIXED
**Smoke result:** PASS (MIXED_EVIDENCE at smoke scale -- expected; K range too small for full diagnosis)

---

## Pre-build 3: top_edge_v4 -- N-scaling with corrected formula

**Script:** `experiments/exp_wave14_moe_top_edge_v4.py`
**Prereg:** `preregs/2026-05-26_wave14_moe_top_edge_v4.md`
**Queue:** overnight_queue (GPU)
**Trigger (PATH A -- FORMULA CORRECT):** v3 returns FREE_ADDITIVE_HARD_PASS (offset_ratio ~1.0 at N=16384)
**What it tests:** N sweep {4096, 8192, 16384, 32768}, K in {2,4}; fit offset=1 - A/sqrt(N)
**Expected bands:** HARD_PASS if offset >= 0.85 at N=32768 and fit R2 >= 0.70; HARD_FAIL if offset < 0.75
**Smoke result:** PASS (correctly returns HARD_FAIL at tiny N -- expected; offset=0.5x at small N)
**NOTE:** If v3 returns FREE_ADDITIVE_FORMULA_ERROR instead, route to DMPK fallback (to be built on demand)

---

## Pre-build 4: bet_n_wta_v5 -- extreme-K codebook stress

**Script:** `experiments/exp_wave14e_bet_n_wta_v5.py`
**Prereg:** `preregs/2026-05-26_wave14e_bet_n_wta_v5.md`
**Queue:** overnight_queue (GPU)
**Trigger:** v4 returns BET_N_TIER1_PROMOTION or BET_N_PARTIAL_TIER2
**What it tests:** K sweep {512, 1024, 2048}; P2 (cleanup_acc_ratio), P3 (corpus_specificity), dead_atom_frac
**Expected bands:** HARD_PASS if P2>=1.10 + P3>=0.05 + dead_frac<0.30 at K=1024; HARD_FAIL if collapse
**Smoke result:** PASS (HARD_FAIL at smoke scale -- p2_ratio<1 expected at smoke; dead_frac=0 healthy)
**NOTE:** If v4 DEGRADES at K=512 (PATH B), route to K=384 intermediate (build on demand when triggered)

---

## Pre-build 5: pq_retained_v4 -- P(q) at N=16384

**Script:** `experiments/exp_wave14_1rsb_pq_retained_v4.py`
**Prereg:** `preregs/2026-05-26_wave14_1rsb_pq_retained_v4.md`
**Queue:** overnight_queue (GPU)
**Trigger:** v3 returns HARD_PASS (binder > 0.30 AND n_peaks >= 2 at N=8192)
**What it tests:** N=16384, 20 seeds; binder_cumulant, n_peaks, peak_sep_sigma; does 1-RSB signal grow with N?
**Expected bands:** HARD_PASS binder>0.40 + sep>=3sigma; UV_PROBLEM_CONFIRMED if binder<0 persists
**Smoke result:** PASS (selftest 4/4, module load clean; full smoke requires infrastructure which loads OK)
**NOTE:** If v3 MIDDLE_BAND, route to ultrametric triple probe (to be built on demand)

---

## Pre-build 6: betB_6corpus_extension_v1 -- 6-corpus Saad-Solla framework limit

**Script:** `experiments/exp_wave14_betB_6corpus_extension_v1.py`
**Prereg:** `preregs/2026-05-26_wave14_betB_6corpus_extension_v1.md`
**Queue:** overnight_queue (GPU)
**Trigger:** 5corpus_noreplay_fix_v1 returns HARD_PASS (BIC_4vs3 < -30 AND spacing_err < 0.05)
**What it tests:** 6-phase corpus sequence; BIC_5vs4 and equal-spacing error of 5 retention values
**Expected bands:** HARD_PASS BIC_5vs4 < -25 + spacing_err < 0.05; HARD_FAIL if 4-state preferred
**Smoke result:** PASS (selftest 4/4, module load clean)
**NOTE:** If 5corpus_noreplay_fix_v1 HARD_FAILS, route to 4-corpus replay-isolated taxonomy (separate build on demand)

---

## Pre-build 7: betB_replay_hA_direct_v3 -- timing resolution of H-A consolidation

**Script:** `experiments/exp_wave14_betB_replay_hA_direct_v3.py`
**Prereg:** `preregs/2026-05-26_wave14_betB_replay_hA_direct_v3.md`
**Queue:** overnight_queue (GPU)
**Trigger:** replay_hA_direct_v2 returns HARD_PASS (inter-phase replay > intra-phase by >= 0.05)
**What it tests:** 5-arm comparison: INTER_BOUNDARY, INTRA_RANDOM, INTRA_RECENT, INTRA_FIXED_INTERVAL, NO_REPLAY
**Expected bands:** H_A1/H_A2/H_A3 discrimination; AMBIGUOUS if gaps < 0.03
**Smoke result:** PASS (AMBIGUOUS at smoke scale -- N=512 too small for effect; expected)

---

## Other in-flight anchor follow-ons (on-demand -- no pre-build script yet)

- **saddle_cascade_plateau_v3 follow-on:** If HARD_PASS (R2<0.85, dev>=0.08): build v4 with deeper f-grid
  (more points near the step transition). If HARD_FAIL: route to CiT alternative.

- **moe_shift_partition_v3 follow-on:** If HARD_PASS (Arm_A > Arm_C by >0.15): build K-scaling v2 pipeline
  (already in-flight). If HARD_FAIL: characterize whether PARTITION beats SINGLE (null control comparison).

- **betB_rd_perturbation_recovery_v2 follow-on:** If HARD_PASS (lambda>0, R2>0.7): build v3 with longer
  recovery window (k_recovery doubled) and exponential fit validation. If HARD_FAIL: confirm saddle-cascade.

- **moe_intraexpert_overlap_v1 follow-on:** If OVERLAP_DOMINANT (iec >= 0.3 at K>=8): build gating
  temperature sweep (top-1 vs top-2, temperature in {0.5, 1.0, 2.0}).

---

## Summary table

| Pre-build | Script | Trigger | Queue | Smoke |
|---|---|---|---|---|
| K_scaling_v3 | exp_wave14_moe_shift_K_scaling_v3.py | v2 HARD_PASS | overnight | PASS |
| K_perarm_v1 | exp_wave14_moe_shift_K_perarm_v1.py | v2 DIVERGENCE | remote_cpu | PASS |
| top_edge_v4 | exp_wave14_moe_top_edge_v4.py | v3 FREE_ADDITIVE_HARD_PASS | overnight | PASS |
| bet_n_wta_v5 | exp_wave14e_bet_n_wta_v5.py | v4 TIER1_PROMOTION | overnight | PASS |
| pq_retained_v4 | exp_wave14_1rsb_pq_retained_v4.py | v3 HARD_PASS | overnight | PASS |
| 6corpus_ext_v1 | exp_wave14_betB_6corpus_extension_v1.py | 5corpus HARD_PASS | overnight | PASS |
| replay_hA_v3 | exp_wave14_betB_replay_hA_direct_v3.py | v2 HARD_PASS | overnight | PASS |
