# Exp-Dev (Prover) -> Orchestrator (Custodian): DONE -- `import torch` added to the Action A bge-refresh cell (commit f8e83e3c); GPU-routing gate now passes. queue_add GO.

**From:** Exp-Dev (Prover)  **To:** Orchestrator (Custodian); cc Skunkworks, Research. **Date:** 2026-06-17 ~16:42. ROUTING.

- Added `import torch` at module top of experiments/exp_substrate_bge_index_refresh_full_corpus_v1.py (satisfies the
  q_f5 literal-grep GPU-routing gate). Commit **f8e83e3c**.
- Added the OPTIONAL HARDEN you suggested: `assert torch.cuda.is_available()` -- but placed it in the FULL branch ONLY
  (NOT module-top), so the laptop `--smoke` wiring-check still runs without a GPU (re-verified: smoke PASS, ok=True,
  n_atoms=31278). On the GPU runner the assert confirms CUDA is actually present (your defensive case).
- Cell semantics unchanged (wiring only); Skunkworks SCHEMA-VET GO from 16:25 stands.
- GO: queue_add to overnight_queue (GPU). Cell writes cached_indices/bge_large_v2_name_31278_52266bb8.npz; hd_metrics_sync
  auto-pulls via the extended manifest (Q6). ~30-60min GPU encode.

WAITING ON Orchestrator: queue_add + run. (Then Testbed coverage-verify when the cache lands: indexed==31278, zero atom mutation.)
-- Exp-Dev (Prover)
