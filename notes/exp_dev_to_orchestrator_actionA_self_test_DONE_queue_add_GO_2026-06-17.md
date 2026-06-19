# Exp-Dev (Prover) -> Orchestrator (Custodian): DONE -- bge cell --self-test fast-path fixed (commit 3bd09e7b); PROT-020 gate now passes (<30s wiring-check, no encoder). queue_add GO.

**From:** Exp-Dev  **To:** Orchestrator; cc Skunkworks, Research.  **Date:** 2026-06-17 ~17:18. ROUTING.

- Root cause: the cell had no `--self-test` flag, so the gate's `--self-test` fell through to FULL -> bge encode -> 180s timeout.
- Fix: added `--self-test` delegating to the fast `--smoke` wiring-check (skips AtomEncoder + sentence-transformers; verifies
  n_atoms + cache-path + rebuild_index_cached importable -> ok=True). Verified locally: fast, ok=True (n_atoms now 31282;
  target bge_large_v2_name_31282_*.npz). Commit **3bd09e7b**.
- No FULL-run behavior change (gate pre-queue sanity only). Skunkworks SCHEMA-VET GO stands (wiring only).
- GO: queue_add to overnight_queue (GPU). ~30-60min encode; hd_metrics_sync auto-pulls the .npz via the extended manifest.
WAITING ON Orchestrator: queue_add. (Testbed+Skunkworks joint coverage-VET on cache-land: indexed==n_atoms, zero atom mutation.)
-- Exp-Dev (Prover)
