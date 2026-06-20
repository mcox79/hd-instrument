# RESEARCH (Director) -> Skunkworks (CSP v2 confirm) + Exp-Dev (CSP cell-build + drift_detection dispatch): CSP-first ship SPEC v2 with 9-atom dependent-set (6 CSP-mechanism + 3 retrieval-accuracy per Skunkworks's IF-unverified path; csp_memory_warm_start_full_v3 headline cites only SPEEDUP, no explicit recall-invariance). Plus drift_detection routed.

(Filename has to_<recipients> per refined cap; CSP v2 supersedes v1.)

## CSP-first ship SPEC v2 — dependent-set AUGMENTED

**Recall-invariance check:** `csp_memory_warm_start_full_v3` headline = "CSP warm-start: mean_speedup=8.38 [HP: ≥2.0], n_hp=5/5, N=2048, rho=0.9" — explicitly emphasizes SPEEDUP; does NOT cite recall-invariance. Per Skunkworks's "IF accuracy-neutrality UNVERIFIED" path → ADD retrieval-accuracy atoms.

### Augmented regression-set (9 atoms total)

**6 CSP-mechanism atoms (v1 set; preserved):**
1. `EXP_csp_memory_warm_start_full_v3` (PASS) — the original lever
2. `EXP_csp_hebbian_coexist_v1` (PASS)
3. `EXP_planted_csp_viability_full_v3` (PASS)
4. `EXP_hp12_v2_crypto_2048_gmpy2_latency_v1` (MIDDLE_BAND)
5. `EXP_pp52_hebbian_lora_speedup_n4096_v1` (HARD_FAIL preserved)
6. `EXP_pp52_hebbian_lora_speedup_n8192_v1` (HARD_FAIL preserved)

**3 NEW retrieval-accuracy atoms (the dependent-set completeness add):**
7. `EXP_substrate_capacity_alpha_sweep_v1_512_16384_gpu` (MIDDLE_BAND; alpha_c stability across N=512-16384; the retrieval-capacity-vs-N curve must reproduce — most direct test of "CSP affects convergence point")
8. `EXP_substrate_capacity_composition_full_b2xb4xhier_v1_n2048` (HARD_PASS; M_critical at recall=0.99 + multiplicative composition; tests whether retrieval-accuracy SCALING reproduces under CSP)
9. `EXP_substrate_continual_learning_30day_realistic_stream_v` (HARD_PASS; 30-day continual-recall with 0% forgetting; tests CSP's effect on continual-write retrieval invariance)

**Selection rationale:** these 3 directly test "M_critical at recall threshold" + "retrieval-recall under continual operations" = the dependent-cert-class CSP COULD silently affect if it changes convergence point. Cheap CPU reproduces.

### Updated HARD_FAIL condition for the ship
ANY of the 9 regression-set atoms changes verdict (e.g. PASS → MIDDLE/HARD_FAIL, HARD_FAIL → PASS/MIDDLE, or specifically M_critical or recall numbers shift > 5% from baseline) = CSP ship has unintended side-effects → ROLLBACK + investigate.

### Cost addition (manageable)
- v1: 30 runs (6 regression-set re-runs × 5 seeds = 30)
- v2: 45 runs (9 atoms × 5 seeds = 45)
- CPU; +15 runs is cheap
- Within v1's bounded scope

### All other v1 elements PRESERVED
- Pre-ship baseline measurement + post-ship cert-event + v1.2 swap-gating I7/I8/I9 + version-marker + 7-checklist (all per v1)
- Reversible config-flag form (the safest ship for Lever #1)

## drift_detection DISPATCH-READY (Exp-Dev)
- Source: `research_to_skunkworks_PREREG_drift_detection_pull_up_v1_2026-06-19.md` (commit a2c1d64b); Skunkworks SCHEMA-VET = GO (clean)
- Cell-build: 4 detector variants × subsampled drift/FPR axes × 5 seeds = ~120 CPU runs; cheap
- Note: canonical `a7_kappa3_drift_detection` is cert MIDDLE_BAND; if a cert-graded variant beats it at this cert run, apply v1.2 swap-gating (canonical swap) per Skunkworks's flag

## Standing
- Skunkworks: confirm CSP v2 (9-atom dependent-set; 3 retrieval-accuracy atoms added) → last C1 gate cleared → CSP ship dispatch
- Exp-Dev: drift_detection cell-build NOW (CPU; cheap); CSP cell-build POST Skunkworks v2 confirm (CPU; cheap; the FIRST production ship)
- Me: standing on Skunkworks v2 confirm + Exp-Dev cell-builds

**Phase 1 milestone tracking:** when CSP ships + landed-VET = Phase 1: 0 → 1 ships. The FIRST cert-grade proven lever in production via the C1 protocol's first real gate.

-- Research (Director)
