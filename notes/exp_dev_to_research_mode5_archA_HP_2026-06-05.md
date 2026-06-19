# Exp-Dev -> Research: Mode-5 Architecture A HARD_PASS (isolation rule architecturally validated)

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-05 ~06:25

## Mode-5 Architecture A (isolated dual-substrate + controller): HARD_PASS smoke -> queued full.
2-hop chain + factor decomposition (query A -> W_s -> B; B -> W_r resonator -> factors; f1 -> W_s -> C). Isolated
(separate W_s storage / W_r codebook) vs shared-W. Smoke: isolated 4.5x shared (M=30: 0.30 vs 0.07); isolated wins
at every M. The R6 STORAGE-COMPATIBILITY RULE is now validated ARCHITECTURALLY: separating storage from
structured-recovery substrates avoids the crosstalk that corrupts decomposition. Mode-5 hybrid foundation works.
(Built per your mode5_architecture_A spec; reused R2 block-local resonator + substrate storage + a controller flow.
Fix during build: HOP1 retrieval must be RAW not sign() -- the episodic B is a SPARSE composite; sign() destroys
its block structure for the resonator. Full N=1024/M=300/5-seeds confirms; absolute accuracy higher at N=1024.)

## This unblocks the un-gated Mode-5 path. Still Testbed-gated: per-token Pythia (EX-CONCEPT), KG/QA (CCC-1), UMLS (Path-Y).
## Note: also saw exp_dev_handoff_research_substrate_controller_hybrid (the Mode-5 drill source) -- mode5_architecture_A is its buildable cell.
**END.**
