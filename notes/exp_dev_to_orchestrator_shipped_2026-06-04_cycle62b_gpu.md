# Exp-Dev -> Orchestrator: shipped 2026-06-04 cycle 62b (GPU batch, user-requested)

**From:** Exp-Dev  **To:** Orchestrator (inform)  **Date:** 2026-06-04

## Summary
User asked for more high-priority experiments with a GPU focus. GPU was idle (1c REM-replay had already
completed; CPU full at 6 pending). Shipped 2 GPU-class experiments, both grounded in the 3x
substrate-training N-threshold drill (research_drill_substrate_training_n_threshold_3x_2026-06-04.md), which
provides verbatim CHEAP-DECISIVE-TEST + N-sweep + HP/MID/HF bands and notes GPU feasibility.

## Shipped (overnight_queue / GPU, 21600s each)
1. **substrate_training_n_threshold_sweep_512_8192_v1_gpu** -- the drill's central test: cf-RPE
   substrate-as-training, BPC gap vs N in {512,1024,2048,3072,4096,8192}, x {bipolar, continuous} codings,
   3 seeds. Tests whether the substrate has the predicted N_threshold ~2000-4000 (and whether continuous
   coding lowers it). Smoke: small-N already learns (~1.1 nat) -> hints a LOWER threshold than the drill's
   bipolar-outer-product estimate (bigram has only ~V distinct contexts, not M_eff~500-1000). Decisive either way.
2. **substrate_modern_hopfield_p_nthreshold_sweep_512_8192_v1_gpu** -- the drill's modern-Hopfield
   companion (sub-q4 + modern_hopfield_upgrade_path_3x): does polynomial-p=4 retrieval lower the
   N_threshold vs classical p=2? Bank retrieval, p in {2,4} x same N grid, M_bank=3000, 3 seeds. HP =
   N_thresh(p4) < N_thresh(p2). Smoke: both p learn at tiny N (-> MIDDLE; full grid resolves threshold-lowering).

## State
- GPU: n-threshold running + modern-Hopfield-p pending (both occupied).
- CPU: 6 pending (Phase 1a Drosophila MB + 1b topological + kappa3 family + poly-p4 factorial) + 1 running.

## Scope / discipline
- Both grounded in an explicit 3x Research drill with pre-registered bands (not padding).
- No verdict interpretation. PROT-018 (N-swept, no _nN suffix) / 021 / 022 enforced; smoke dirs cleared
  before each ship (PROT-021 contamination guard); ASCII-only; GPU template (assert cuda + batched matmul).
- Caught + fixed two real bugs pre-ship: a sim-normalization error (unit-norm codes vs /n) and a smoke-grid
  verdict guard.

**END.** GPU now fed with the two highest-value N-threshold experiments; verdicts will propagate to Orchestrator.
