# Pre-registration: cardinality_generalization_stage1_190c_cpu_v1

**Date:** 2026-06-16
**Anchor:** cardinality_generalization_stage1_190c_cpu_v1
**Queue:** remote_cpu_queue
**N:** 2048,4096, **Seeds:** 5, **distribution-shift:** VOCAB=200 ROLES=5 n_distinct[2,13) mult[1,6)

## Scientific question
Does ARM-1's ratified cleanup_distinct_count operator (CLEANUP_THRESH=0.30, FROZEN) GENERALIZE to a DIFFERENT
generator distribution than the one it was authored on -- i.e. generalization, not refit? Pure-substrate pipeline
(FHRR superpose(bind(role,filler)) -> cleanup_distinct_count -> readout); no LLM/RAG. Two siblings: exact-count
(single-role distinctness under multiplicity) and most(A>B). Operator UNCHANGED; distribution SHIFTED vs ARM-1
(VOCAB 120->200, ROLES 4->5, n_distinct[1,9)->[2,13), mult[1,4)->[1,6)). Held-out gold FIREWALLED (generated at
eval, never ingested; 22nd rule). FAIR-NULL controls C0 graph-walk-trace (B^T@B) + C1 basis-norm.

## Pre-registered bands

**HARD-PASS (per-sibling; carried from ARM-1, LOCKED):**
- exact-count (single-role): RMSE <= 1.0 AND C1_rmse/C2_rmse >= 2.0 AND C2_rmse < C0_rmse, evaluated WITHIN the
  capacity envelope (alpha_single=0.030)
- most(A>B): accuracy >= 0.80 AND (C2_acc - C1_acc) >= 0.20 AND no seed-drift (C2 acc std <= 0.40)

**MIDDLE:** exact-count C2 beats C0 but RMSE in (1.0, C1) without >=2x reduction; OR most C2 acc in [0.65, 0.80).

**HARD-FAIL:** exact-count C2_rmse >= C1_rmse OR does not beat C0 (no transfer -> ARM-1 stays scoped) OR
most C2 acc < 0.65.

## Calibration rationale
Bands are the ARM-1 ratified values applied to a NEW distribution -- the honest generalization question is whether
the SAME operator clears the SAME bars on a shifted distribution it was not fit to. Re-tuning CLEANUP_THRESH would
convert generalization into refit, so the operator is FROZEN. Per DECISION 197 honest-adjudication flag: if exact-
count RMSE stays > 1.0 at VOCAB=200/N=4096 that is an HONEST NEGATIVE for exact-count generalization (NOT artifact
dismissal); a SPLIT result (most transfers, exact-count doesn't) is a valid nuanced per-sibling finding.

## N-suffix section
Anchor runs at N in {2048, 4096}; N>=2048 keeps the higher-count single-role test within the alpha_single=0.030
capacity envelope.

## Timeout estimate
Smoke ~ 3s at N=2048 tiny (VOCAB=60, 2 seeds, 40 scenes). FULL: N in {2048,4096}, seeds=5, VOCAB=200, 300 scenes;
C0 forms the N x N B^T@B matrix per scene (the heavy laptop-overheater class) -> remote CPU.
formula: ceil(1.5 * 3 * (4096/2048)^2.0 * (5/2)) = ceil(1.5*3*4*2.5) = 45 ... but C0 N x N matrix dominates at
full VOCAB/scenes; set generously for the heavy C0 control.
timeout_s = 14400
