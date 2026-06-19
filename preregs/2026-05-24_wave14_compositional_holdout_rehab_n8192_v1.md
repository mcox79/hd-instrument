# Prereg — wave14_compositional_holdout_rehab_n8192_v1

**Date**: 2026-05-24
**Author**: orchestrator exp_dev role (inline)
**Cap_map cell**: K6 Compositional generalization — KILLER Tier 2

## Trigger

v190 cap_map K6 ⚪ -> 🟡 PARTIAL FIRST-EVER probe (v1: hold_out_acc=0.116 at N=4096 single-seed). v190 filed 4 K6 rehab axes; this prereg covers axis 1 (larger N + multi-seed).

## Mechanism

Identical to v1: subject-relation-object Latin-square fact set (16 objects × 16 attributes -> 256 facts; o = (s+r) mod 16). 75% train / 25% hold-out split. Single bundle B = sum_i value_i * (s_i XOR r_i). Unbind-and-cosine readout against the 16 attribute atoms; argmax. Only N (4096 -> 8192) and seed count (1 -> 5) change.

## Falsifier statements

| Band | Threshold | Interpretation |
|---|---|---|
| **HARD-PASS** | mean hold_out_acc >= 0.50 across 5 seeds (chance = 1/16 = 0.0625) | Substrate compositionally generalizes via N-scaling rehab; K6 ⚪ -> ✅ track |
| **HARD-FAIL** | mean hold_out_acc <= 0.10 (within 2x chance) OR mean hold_out_acc <= v1's 0.116 - 3pp | Rehab actively hurts; capacity does not help K6 |
| **MIDDLE** | intermediate (>0.10 and <0.50) | Saturation pattern at Latin-square readout scope; K6 second-axis rehab needed (axes 2-4) |

## Substrate-product reading

- HARD-PASS: substrate has compositional generalization for the K6 KILLER T2 spec; portfolio gains a new ✅ row.
- HARD-FAIL: N-scaling does not help K6; further rehab needs structural mechanism change (axes 2-4 = hierarchical pre-binding, cleanup-iteration, Bet X integration).
- MIDDLE: N=8192 lifts vs v1 but does not clear HARD-PASS; row stays 🟡 PARTIAL; pre-register axes 2-4.

## Discipline citations

- per [[feedback-no-smoke]]: bands falsifiable BEFORE running.
- per [[feedback-rehabilitation-after-rejection]]: rehab axis 1 of v190 4-axis K6 rehab list.
- per [[feedback-envelope-expansion-fail-bands]]: envelope-expansion drill on K6 PARTIAL row from v190.

## Smoke

PASSED (smoke at N=1024 single-seed: hold_out=0.094 train=0.526 -> COMPOSITIONAL_HARD_FAIL). Smoke result consistent with v1 N=4096 hold_out=0.116 at smaller N; mechanism + plumbing work; FULL N=8192 may lift or saturate.
