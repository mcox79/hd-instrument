# Pre-registration: multidrive_vsa_policy_h3_cpu_v1

**Date:** 2026-06-11
**Anchor:** multidrive_vsa_policy_h3_cpu_v1
**Queue:** local_cpu_queue
**N:** 8192, **Drives:** 4, **Actions:** 6, **Horizon:** 3

## Scientific question
Single-step single-action arbitration cannot satisfy multiple competing depleting drives (each action serves only 1-2 of
4 drives). Does encoding 3-step action plans as substrate VSA vectors + selecting by HARMONIC utility (CES rho=-1, which
penalizes the worst drive) break the single-action ceiling on worst-drive satisfaction? Per the 96%-irreducible 2x DEEP drill.

## Pre-registered bands

**HARD-PASS:** worst-drive absolute satisfaction > 0.50 AND >= 3x single-action baseline AND VSA policy decode acc >= 0.95.

**MIDDLE:** worst-drive > 0.50 but lift < 3x (or decode 0.85-0.95).

**HARD-FAIL:** worst-drive <= 0.30 or VSA decode fails.

## Calibration rationale
The environment is a genuine multi-drive tradeoff: actions serve 1-2 of 4 drives with boost 0.6 / decay 0.85, so no single
action keeps all drives satisfied (single-action worst-drive ~0.13). A balanced 3-step plan can cover all drives; harmonic
utility selects the balanced plan (vs sum-greedy which can starve one drive). >0.50 worst-drive at >=3x single-action is the
drill's predicted 3-5x lift. VSA decode >=0.95 confirms the substrate genuinely represents the 3-step plans (not incidental).
A sum-greedy 3-step baseline is also reported to isolate the harmonic contribution from the lookahead contribution.

## N-suffix section
N=8192 complex64; numpy CPU, seconds. n=1 exploratory; multi-seed n=5 follow-up if HARD_PASS.
