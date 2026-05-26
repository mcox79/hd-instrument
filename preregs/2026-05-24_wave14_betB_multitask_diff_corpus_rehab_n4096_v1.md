# Prereg — wave14_betB_multitask_diff_corpus_rehab_n4096_v1

**Date**: 2026-05-24
**Author**: orchestrator exp_dev role (inline)
**Cap_map cell**: U1 On-device personalization + U7 Cross-modal binding — UNSURE Tier 2 (joint probe)

## Trigger

v190 cap_map U1/U7 ⚪ -> 🟡 PARTIAL FIRST-EVER joint probe (v1: retention_A=0.600 gain_C=3.76 at N=2048 5-seed; CONDITIONAL transfer signal — new-corpus uptake robust but original-corpus retention degraded). v190 filed 3 U1/U7 rehab axes; this prereg covers axis 2 (larger N for retention floor).

## Mechanism

Identical to v1: Phase A on corpus_a (English bytes); Phase C on hex-encoded numerical corpus with A-replay (single-shared-W). Compute retention_A (BPC on held-out A after C) and gain_C (BPC reduction on C vs zero-W baseline). 5 seeds {7, 17, 23, 31, 41}. Only N (2048 -> 4096) changes.

## Falsifier statements

| Band | Threshold | Interpretation |
|---|---|---|
| **HARD-PASS** | mean retention_A >= 0.70 AND mean gain_C >= 0.30 across 5 seeds | U1/U7 cross-corpus retention rehab passes via N-scaling; U1/U7 🟡 -> ✅ track |
| **HARD-FAIL** | mean retention_A <= 0.30 OR mean gain_C <= 0.05 | Either catastrophic forgetting OR new-corpus uptake collapses with bigger N |
| **MIDDLE** | intermediate | N=4096 lifts retention partially but does not clear HARD-PASS 0.70 (joins axis 1 as second saturation point; structural-separation axis routing required) |

## Substrate-product reading

- HARD-PASS: substrate transfers across corpus types with intact retention via N-scaling; portfolio gains new ✅ row.
- HARD-FAIL: bigger N hurts cross-corpus learning; structural mechanism issue.
- MIDDLE: N=4096 lifts vs v1 retA=0.600 but does not clear HARD-PASS 0.70; pre-register axes 1 (MoE structural separation) and 3 (weighted-replay) as remaining rehab paths.

## Discipline citations

- per [[feedback-no-smoke]]: bands falsifiable BEFORE running.
- per [[feedback-rehabilitation-after-rejection]]: rehab axis 2 of v190 3-axis U1/U7 rehab list.
- per [[feedback-envelope-expansion-fail-bands]]: envelope-expansion drill on U1/U7 PARTIAL row from v190.

## Smoke

PASSED (smoke at N=1024 single-seed: retA=0.843 gain_C=3.676 -> MULTITASK_DIFF_HARD_PASS). Smoke at smaller-than-FULL N already clears HARD-PASS — promising signal that N-scaling helps. FULL N=4096 + 5 seeds is the definitive test.
