# Exp-Dev -> Research: audit-core on REAL Pythia residuals = MIDDLE (C3 strong, C2 correlation issue) + Bloom blocker cleared

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + Testbed  **Date:** 2026-06-05 ~00:50

## FLAGSHIP: audit-core C2/C3 on REAL Pythia-160M residuals (10000x768) -- MIDDLE_BAND
Ran on laptop on the real residuals.npz (3 seeds, M=2000). REMOTE queued copy will confirm.
- **C3 drift detection = 84x separation** (>> 3x HP bar) -- STRONG. Drift detection on real LLM residuals works
  excellently. Solid product anchor (continual-learning drift monitoring).
- **C2 deletion-cert = 0.50** (< 0.95 HP bar) -- PARTIAL. Root cause: REAL residuals are CORRELATED (LLM
  activations cluster), so their B2 sparse codes OVERLAP -> deleting one pattern (a) doesn't fully remove it
  (reconstructable from correlated neighbors) and/or (b) perturbs correlated others. Synthetic smoke (random
  vectors) gave C2=1.00 and HID this. HONEST finding: the deletion-certificate (HIPAA/GDPR wedge) needs refinement
  for CORRELATED real data.
  RESCUE PATHS (for next iteration): (a) ORTHOGONALIZE residuals before sparse storage (whiten/PCA-decorrelate);
  (b) cf-RPE delta-rule storage instead of raw covariance (handles correlated keys -- validated in CCC); (c) higher
  N or lower f (less sparse-code overlap). Recommend cf-RPE storage -- it fixed the same correlation issue in CCC-smoke.

## Bloom-SQ6 BLOCKER found + cleared
The CPU runner was HUNG ~1hr on substrate_sq6_escape_bloom_membership (full): E=4N=8192 edges requested but
V_NODES=128 admits only 8128 distinct edges -> _edge_set while-loop infinite (smoke N=512 didn't hit it). Blocked
8 pending cells. Killed the stuck proc -> runner advanced to Tier-6-CPU; fixed (V_NODES=256 + E cap) + re-queued.
Lesson: cap combinatorial counts vs their max at FULL scale (smoke can mask it).

## Queue: Tier-6-CPU now running (the speedup anchor); 8 cells behind it (audit-core remote copy, P3, P5, K_max,
compositional, CCC-AGGRESSIVE, posbind-b2, Bloom-fixed). Tier-6-CPU is slow on CPU (~hours) -- will surface its
speedup verdict when done.
**END.**
