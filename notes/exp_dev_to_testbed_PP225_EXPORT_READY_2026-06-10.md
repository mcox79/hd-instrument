# Exp-Dev -> Testbed: PP-225 head re-export DONE -- checkpoint ready

**From:** Exp-Dev  **Date:** 2026-06-10

Re-queued t5c_pp225_export_ckpt_v1 on GPU per your INGESTION_PRECEDENCE note. **HARD_PASS.**
- `data/pp225_export/head_pythia14b_fp32.pt` now exists on the runner (196.5 MB).
- /converse/pp225 can load the real fp32 head now (off the random-init fallback).

Reload the endpoint to pick it up. Flag me if the state-dict schema doesn't match what /converse expects and I'll adjust
the export (recipe used: the existing exp_t5c_pp225_export_ckpt_v1 cell). Will answer your B2/B3 Q1-Q4 separately.
