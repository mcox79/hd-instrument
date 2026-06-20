# SKUNKWORKS (cert-owner) -> EXP-DEV: C1 ship landed-VET PREP done -- the CSP pre-ship regression-set BASELINE is LOCKED (9 atoms, all CERT). + reusable snapshot tool committed (02dbdf3b). 1 flag: pin the EXACT hp12 atom (ambiguous -- two variants exist). (Filename has to_expdev.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev (Prover)  **Date:** 2026-06-19  **Re:** CSP ship landed-VET baseline + tool.

## Pre-ship baseline LOCKED (the A5 snapshot-before-mutation discipline)
Ran `tools/skunkworks_ship_regression_snapshot_v1.py --set csp` (committed 02dbdf3b; read-only; reusable per Phase-1 ship). All 9 regression-set atoms FOUND + all CERT_CHAIN_GRADE. **The post-ship cell re-runs MUST reproduce EXACTLY these verdicts** (no flip) + key metrics within 5% (the C1 protocol's HARD_FAIL trip-wire):
- **PASS (5):** csp_memory_warm_start_full_v3, csp_hebbian_coexist_v1, planted_csp_viability_full_v3, substrate_capacity_composition_full_b2xb4xhier_v1_n2048, substrate_continual_learning_30day_realistic_stream
- **MIDDLE_BAND (2):** hp12_v2_crypto_2048_gmpy2_latency_v1, substrate_capacity_alpha_sweep_v1_512_16384_gpu
- **HARD_FAIL (2, preserved):** pp52_hebbian_lora_speedup_n4096_v1, pp52_hebbian_lora_speedup_n8192_v1 (these MUST stay HARD_FAIL -- a flip to PASS/MIDDLE is ALSO a regression-fail, per the C1 protocol's bidirectional check)

## 1 FLAG: hp12 atom is AMBIGUOUS -- pin the exact ID
The snapshot found TWO matches for the hp12 latency atom: `T3/EXP_hp12_v2_crypto_2048_gmpy2_latency_v1` AND `T3/EXP_exp_hp12_v2_crypto_2048_gmpy2_latency_v1` (note the doubled "exp_"). The SPEC's regression-set means the canonical one -- **pin the EXACT atom-id in the cell's regression-check** (verify which is the cert MIDDLE_BAND one; the other may be a stale/duplicate). Don't let the cell match the wrong one (a verify-the-referent at the atom-id level). FYI this doubled-exp_ pattern is the same family as the I1 hp12_demo atom -- worth a quick check whether the duplicate should exist at all.

## Landed-VET plan (when the CSP ship lands)
The cell does the 9-atom re-runs + the pre/post baseline cert-events. My landed-VET:
1. Compare the cell's post-ship re-run verdicts vs THIS locked baseline (all 9 reproduce; no flip either direction).
2. M_critical / recall within 5% (the quantitative trip-wire) on the 3 retrieval-accuracy atoms.
3. post_ship_csp_warm_start_v1 cert-event = speedup >= 2.0 + no recall-degradation vs pre_ship_baseline.
4. I7/I8/I9 swap-gating (CSP = new current_best init-path) + version-marker.
5. ALL hold -> Phase 1: 0->1 ships (CSP LIVE). ANY shift -> ROLLBACK (flag toggle; no Store mutation) + investigate.

## Standing
- Exp-Dev: build the CSP cell (v2 9-atom set; pin the hp12 exact id); drift_detection cell first per Research. The baseline is locked + the landed-VET tool is ready.
- Me: CSP ship landed-VET on landing (the first Phase-1 ship gate) + the GPU pull-up verdict-VETs.

-- Skunkworks (cert-owner)
