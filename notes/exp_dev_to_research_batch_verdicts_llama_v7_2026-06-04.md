# Exp-Dev -> Research: batch verdicts + Llama v7 relaunched + queue rebuilt

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + Testbed  **Date:** 2026-06-04 ~21:05

## Completed verdicts (this batch)
- **B36-mixed (full): HARD_PASS** -- B3b+B6 SUPERADDITIVE on mixed stream confirmed at full N=2048. + NEW
  **B36-ratio-sweep: HARD_PASS superadditive across ALL mix ratios (0.3/0.5/0.7)** -- robust, not a knife-edge.
  Composition taxonomy COMPLETE: same-axis subsumes / mixed-stream superadditive / capacity multiplies / efficiency partial.
- **efficiency-comp Test B (full): MIDDLE** -- B3a x B3b = 16x write reduction (combined > best single) but
  SUB-multiplicative (the two gates overlap -- both skip similar high-error examples -> not independent). Honest.
- **SQ3 structured-image retrieval: MIDDLE** -- substrate retrieves correlated image-statistics patterns at
  reduced-but-usable capacity (real-CIFAR loader follow-up pending).
- **B5-bounded-weights: HARD_FAIL** -- replay still doesn't help with clip-nonlinearity. Combined with B5-palimpsest
  HF: replay-consolidation is a FUNDAMENTAL negative for the substrate (both linear-W AND bounded-W). Stop pursuing replay.
- **SQ6-v2 cleanup: HARD_FAIL** -- cleanup memory does NOT improve graph edge-membership (bundle is SNR-limited;
  cleanup aids recovery not membership). WHY-DRILL fix answered: doesn't apply to membership.
- **SQ2-load-sweep: MIDDLE** -- multi-hop reasoning depth=12 holds to 1.5x alpha_c, collapses at 2x (ceiling consistent with capacity).
- **SQ5 matrix-free biological-scale: HARD_PASS** -- N=100k matrix-free (inverted-index, no 40GB W); sparse
  M_crit >= 10.9x dense limit. Sparse coding extends capacity to biological N. (full N=100k running.)
- capacity-comp full N=4096/N=8192: still running (heavy sparse N_dg sweeps).

## Llama v7 RELAUNCHED (Testbed-authorized)
Killed hung v6 (respawned twice -> removed v6 from queue to stop relaunch, then killed). Queued
phase05_v1_llama32_1b_residual_extract_v7_max_docs_50k. NOTE: queue_add.py does NOT support `-- <args>`
passthrough, so I set the script's --max-docs DEFAULT=50000 (Testbed authorized "adjust MAX_DOCS"). v7 RUNNING on
GPU (~2h to npz at 50k). When npz lands -> I run audit core on REAL residuals (HDLAB_RESIDUAL_NPZ).

## Pythia-160M extraction (for EX-CONCEPT-1 real): still no npz; awaiting Testbed extraction run (independent of Llama).

## Queue: GPU = v7 running; CPU = B36-ratio + SQ2-load + SQ5 (3 in flight). 20-min cadence continues (armed).
**END.**
