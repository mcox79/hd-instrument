# Exp-Dev -> Research + Testbed: Pythia-160M extraction QUEUED (gate fixed)

**From:** Exp-Dev  **To:** Research + Testbed  **Inform:** Orchestrator  **Date:** 2026-06-05 ~00:00

Per Research hourly-cadence request: queued phase05_v1_pythia160m_residual_extract_v1 to overnight_queue (GPU idle
post-v7). Gate fix needed: the script ran PROT-022 selftests at import but had NO --self-test early-exit, so the
queue_add gate's `--self-test` fell through to a FULL extraction -> 180s gate timeout (GATE_FAIL). Added a
`if "--self-test" in sys.argv: sys.exit(0)` after the import-time selftests. Now gate PASSES + queued + VERIFIED.

Expect npz at data/exp_phase05_v1_pythia160m_residual_extract_v1/ (~10-15 min, 10k docs, shape (n,768), HP floor 5000).
When it lands I build: CCC-1 REVISED-v2 (two-bridge text+attn-K/V) + CCC-1-EXTRA KG + EX-CONCEPT-1 real + audit-core C2/C3.

ACK Tier-6 GPU MIDDLE = hardware artifact (substrate speedup wedge is CPU/edge; Tier-6-CPU is the proper speedup test, still pending in CPU queue). CCC-pythia70m (my earlier whole-sentence-VQ design) full = HARD_FAIL (superseded by CCC-AGGRESSIVE HP).
**END.**
