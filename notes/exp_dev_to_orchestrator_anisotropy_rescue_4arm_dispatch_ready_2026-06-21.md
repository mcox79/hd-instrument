# EXP-DEV -> ORCHESTRATOR cc SKUNKWORKS/RESEARCH: anisotropy-rescue 4-arm cell AUTHORED + dispatch-ready (the cell that was waiting on me). Brief.

**Date:** 2026-06-21T15:55Z
**Cell:** `exp_anisotropy_rescue_4arm_sweep_v1_gpu` (commit ba867605)

## This was the genuine "waiting on exp_dev" item (USER asked) -- now cleared
Research pre-reg'd + Skunkworks SCHEMA-VET'd (BUILD-WITH-CONDITIONS) the sparse-fan-in/fly-LSH anisotropy-rescue; I'd been on the parallel whitening-revival (isotropization) path + hadn't authored this distinct one. Now authored.

## Skunkworks's 2 conditions applied
- **C1 (LOAD-BEARING, verified):** pre-flight KILL gate = **ARM1_RAW >= 0.80** (direct: raw superposition already holds -> no anisotropy problem), NOT the miscalibrated mean_cos<0.20 (which would mis-kill at chance). Real pythia keys are in the collapse regime (GATE-2 proof) -> the gate un-blocks.
- **C2 (storage class):** ARM A/C-superposition = M-INDEP O(d'^2); ARM B fly-LSH = O(M) per-memory-COMPRESSED (reported as bits/mem, NOT M-indep). Distinct storage questions, reported separately.

## 4 arms + controls + smoke gate (all in)
A cerebellar K=5 sparse-fan-in+kWTA+superposition (control A'=dense-Gaussian must HARD-FAIL); B fly-LSH+median-subtract+WTA-tag (control B'=Charikar must underperform); C compose A->B; D attention upper-bound (calibration). Per-arm HARD-PASS/FAIL/MIDDLE bands per drill section (c). Smoke gate = ARM A K-sweep peak@K=5 (Litwin-Kumar).

## Validation
- selftest PASS: anisotropic raw collapses (0.00); fly-LSH B rescues (1.0) + compose C (0.91); isotropic decode-meter (1.0). (ARM A sparse-fanin-superposition stays collapsed on the extreme synthetic -- still a superposition; real milder keys data-decide.)
- smoke PASS (pythia-160m): pipeline end-to-end; calibration-flag correctly fires (ARM D=0.45<0.80 under-trained). NOTE smoke signal: B'(Charikar) > B(fly-LSH) at under-trained smoke -> if it holds at full, ARM B HARD-FAILs (WTA not load-bearing); full pythia-2.8b decides.

## Dispatch (GPU)
anchor `anisotropy_rescue_4arm_sweep_v1_gpu`, RUN_MODE=full (pythia-2.8b fp16, proj768, M={1k,3k,10k}, 5 seeds, expand5x). Mixed GPU(encode)+CPU(arms; superposition W-build d'=3840 + fly-LSH tags, query-sampled MAX_Q=1500). Est ~60-120min; suggest timeout 9000s (2.5h), per-seed ckpt (CONFIG_VERSION includes params). Queue AFTER the whitening-revival (GPU busy). Verify-it-starts.

On land -> Skunkworks landed-VET (per-arm bands + C1 kill-check + C2 storage-class). This + whitening-revival = the 2 parallel anisotropy-break paths; cheaper+higher-recall wins as the substrate storage path.

-- Exp-Dev
