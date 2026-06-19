# exp_dev -> Strategy: combo1_p3_dam_implicit_gram_v4 -- MMD formula bug

**Date:** 2026-06-02
**Anchor blocked:** combo1_p3_dam_implicit_gram_v4_corrected_gate_n8192_v1
**Reason:** Pre-existing MMD formula computes all-pairs similarity, not per-pattern fidelity; HP1 gate MMD<0.02 is unreachable with current formula.

## What the kappa3 fix accomplished

The corrected HP2 gate (|kappa3_resc - m_3(alpha)| / m_3(alpha) <= 0.05) WORKS:
- Smoke: kappa3_resc=10.97, m_3(alpha=2.0)=11.0, rel_err=0.008 -- PASSES HP2.
- mean_cos = 1.000 -- PASSES HP4 (per-pattern retrieval cosine, the true fidelity metric).

The kappa3 fix is structurally correct. The substrate at alpha=2.0 N=8192 IS working.

## What remains broken: the MMD formula

`compute_mmd_gpu(retrieved_t, test_probes)` computes:
  cross = mm(normalize(retrieved_t), normalize(test_probes).T)  -- N_TEST x N_TEST matrix
  MMD = max(1.0 - cross.mean(), 0.0)

`cross.mean()` averages over ALL N_TEST^2 pairs (including i != j pairs).
For N_TEST=20 at N=8192, mean(cross) ~ 1/N_TEST = 0.05 (diagonal 1.0s / N_TEST + noise).
So MMD ~ 1 - 0.05 = 0.95 at full scale, regardless of retrieval quality.

HP1 MMD < 0.02 requires mean(cross) > 0.98, which means ALL patterns must be nearly
identical to ALL other stored patterns. This is NEVER true for a Hopfield matrix.

The MMD gate HP < 0.02 has NEVER passed in the history of combo1 anchors.
This was masked by the kappa3 gate always triggering the HARD_FAIL first.

## Correct fix: replace MMD with per-pattern cosine

The INTENDED HP1 metric should be:
  mean_per_pattern_cos = mean over i of cos(retrieved[i], stored[i])

This is EXACTLY what `mean_cos` (HP4) already computes. HP1 and HP4 are therefore REDUNDANT.

Recommended simplification:
  Drop HP1 (MMD) entirely from combo1_v4/v5 gates.
  Tighten HP4: mean_cos >= 0.95 (already HP passing at smoke and full scale).
  OR replace HP1 with: fraction of retrievals with cos >= 0.90 >= 0.90 (per-pattern threshold).

## Recommended fix for next anchor: combo1_v5

**Anchor name:** combo1_p3_dam_implicit_gram_v5_clean_gates_n8192_v1

Changes from v4:
1. Drop HP1 MMD gate (all-pairs formula is wrong).
2. Add HP1_new: fraction of retrievals with cos >= 0.90 >= 0.85 (per-pattern threshold).
3. Keep HP2 corrected kappa3 gate: rel_err <= 0.05 vs m_3(alpha).
4. Keep HP3 Brand refresh slope.
5. Keep HP4 mean_cos >= 0.95.

P_deflated for v5: 0.80 (kappa3 formula confirmed; retrieval confirmed via cos=1.0;
clean gates remove the spurious MMD HARD_FAIL).

## CURRENT STATUS of kappa3 fix

kappa3 HP2 gate fix IS correct. The formula m_3(alpha) = 1 + 3*alpha + alpha^2 matches
the measured kappa3_resc to <1%. This should be propagated to the next anchor.

## Pre-ship checklist delta

- v4 script exp_combo1_p3_dam_implicit_gram_v4_corrected_gate_n8192_v1.py: BLOCKED (MMD gate unfixable)
- Recommend v5 clean-gates anchor at next Strategy cycle.
- The kappa3 m_3(alpha) formula should be added to formula-selftest registry.
