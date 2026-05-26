# Prereg: MoE Shift/Partition 3-arm rebuild v2 (DMPK bimodality instrumentation)

**Date:** 2026-05-25
**Script:** experiments/exp_wave14_moe_shift_partition_v2.py
**Queue:** overnight_queue (GPU; ~4-6 GPU-hrs + ~12 min DMPK overhead = ~5-7 GPU-hrs total)
**Handoff:** notes/exp_dev_handoff_research_mesoscopic_xtalk_diagnostic_2026-05-25.md
**Parent:** experiments/exp_wave14_moe_shift_partition_v1.py (smoke passed; v2 adds DMPK)
**Walk-back note:** Smoke at N=512, K=[1,2,4], 1 seed: effect_size_d=0.446 < 1.0, lift=0.068 borderline.
Full run registered at N=4096, K=[1,2,4,8], n=5 seeds per the walk-back gate.

## Primary hypothesis (unchanged from v1)

Structural separation (SHIFT arm) provides K-fold capacity gain over matched-parameter
SINGLE arm, while PARTITION arm tracks SINGLE (null control).

## New in v2: DMPK bimodality instrumentation (additive only)

Per notes/exp_dev_handoff_research_mesoscopic_xtalk_diagnostic_2026-05-25.md:
- `compute_dmpk_signature()`: SVD spectrum of per-expert W_k matrices
- `compute_gate_overlap()`: off-diagonal |<p_k, p_j>|^2 gate overlap
- Adds `mesoscopic_verdict` secondary verdict (ADDITIVE -- does NOT gate primary)

## Pre-registered bands (primary -- unchanged from v1)

Per notes/exp_dev_handoff_research_moe_rebuild_2026-05-24.md:
- HARD-PASS: Arm A exceeds Arm C by > 0.15 at M = 2*baseline AND mode-collapse safe AND monotone
- HARD-FAIL: Arm A tracks Arm C within +/-0.05 AND mode-collapse present
- MIDDLE: Arm A exceeds Arm C by 0.05-0.15
- INSTRUMENTATION-FAIL: degenerate gating or alpha_c not extractable

## Pre-registered bands (secondary DMPK -- additive)

Per notes/exp_dev_handoff_research_mesoscopic_xtalk_diagnostic_2026-05-25.md:
- MESOSCOPIC_PASS: K=4, Arm A bimodality_ratio >= 1.0, Arm B <= 0.4, separation >= 0.6
- MESOSCOPIC_MIDDLE: separation [0.2, 0.6]
- MESOSCOPIC_FAIL_NO_DISCRIMINATION: separation < 0.2 AND both arms bimodal
- MESOSCOPIC_FAIL_BOTH_UNIMODAL: both arms unimodal (a_bim < 0.5)

## Overhead budget

DMPK SVD at N=4096 GPU: ~3 sec per cell. 240 cells total -> ~12 min added (~3% overhead).
