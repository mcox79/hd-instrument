# Prereq: combo2_p4_l_sweep_parity_hypothesis_v1_n4096

**Date:** 2026-06-02
**Anchor:** combo2_p4_l_sweep_parity_hypothesis_v1_n4096
**Queue:** remote_cpu_queue
**Script:** experiments/exp_combo2_p4_l_sweep_parity_hypothesis_v1_n4096.py

## Hypothesis

COMBO-2 (p=4 DAM + Hadamard hierarchy + signed-AM) L=5/6/7 extension.
Tests parity hypothesis from routing note v343 Item 3: does b_rep oscillate with L (odd/even parity)?

## PROT-022 R2 Theory Step (completed before script)

**Analysis:** b_rep is L-INDEPENDENT. W_signed = W_A - W_B is constructed independently of NKT depth L.
Signed-AM B-repulsion dynamics operate on W_signed only, not on the NKT hierarchy matrices.
Self-test: cos(h(eta_B), eta_B) = -0.968 < 0 (repulsion confirmed algebraically).
Hadamard involution: xi_{L-1}_dec = ctx_L * (ctx_L * xi_{L-1}) = xi_{L-1} exactly.

**Revised prediction:** b_rep FLAT (L-independent, approximately equal for L=5/6/7).
Parity oscillation (b_rep drops at L=6) is NOT predicted by signed-AM algebra.
L_fidelity predicted EXACT-1.0 for all L when alpha << alpha_c=0.138.

**Parity WOULD be novel:** if empirically b_rep < 0.4 at L=6 with flanking values >= 0.9,
that is unexpected and would require follow-on theory investigation.

## Pre-registered Bands

**HARD-PASS (flat, theory-predicted):**
- b_rep >= 0.9 for all L=5/6/7 (5-seed unanimous)
- L_fidelity >= 0.75 for all L (4/5 seeds)

**PARITY_OBSERVED (novel finding, if empirically seen):**
- L=6 b_rep < 0.4 AND L=5 b_rep >= 0.9 AND L=7 b_rep >= 0.9
- Reports as HARD_PASS (novel) -- requires follow-on theory

**MIDDLE:**
- b_rep in [0.5, 0.9) for any L OR L_fidelity in [0.50, 0.75) for any L

**HARD-FAIL:**
- b_rep < 0.4 for any L OR L_fidelity < 0.40 for any L

## Smoke Result

**N_smoke=512, 2 seeds, L=5/6/7:**
- b_rep=1.0 for all L=5/6/7 (flat, as predicted)
- l_fid=1.0 for all L=5/6/7
- Verdict: HARD_PASS (FLAT)

**Walk-back gate:** smoke effect size = b_rep=1.0 flat vs threshold 0.9. d >> 1.0. No walk-back needed.

## Timeout Estimate

- smoke_wall_s ~ 5s (2 seeds x 3 L cells x N=512)
- FULL: N_smoke->N_full = 512->4096 (8x), 2->5 seeds (2.5x), scaling_exp=1.5
- timeout = ceil(1.5 * 5 * 8^1.5 * 2.5) = ceil(1.5 * 5 * 22.6 * 2.5) = ceil(424) -> 600s
- Using 900s for margin.

## Cap_map Impact

- HARD-PASS (flat): PP-48 NKT operating envelope L=5/6/7 confirmed flat (L-independent b_rep)
- PARITY_OBSERVED: NEW FINDING: PP-48 NKT odd-depth-only regime (would be novel)
- HARD-FAIL: PP-48 NKT composition ceiling at L=4 cleanly characterized
