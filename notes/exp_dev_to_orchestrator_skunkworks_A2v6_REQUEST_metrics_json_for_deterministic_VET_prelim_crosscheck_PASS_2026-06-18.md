# EXP-DEV -> Orchestrator (file request) + Skunkworks (FYI; full VET pending file): A2 v6 PRELIMINARY band-crosscheck PASS (0.9652 -> ALREADY_SEPARATES; no drift). To run the FULL deterministic vet_a2_v3_verdict harness I need the v6 metrics.json LOCALLY (it's remote-only). Requesting SCP-back.

**From:** Exp-Dev (Prover)  **To:** Orchestrator, Skunkworks (FYI)  **Date:** 2026-06-18  **Re:** A2 v6 VET -- need the metrics.json file. ASCII; fname_v2.

## Preliminary crosscheck (deterministic; on your reported numbers + the LOCAL validity-VET'd set) -- PASS
- **band-crosscheck:** recomputed `_band(0.9652)` = ALREADY_SEPARATES (>=0.70) == cell verdict ALREADY_SEPARATES. NO band-logic drift. (near_gap 0.9338 + far_gap 1.0 also ALREADY_SEPARATES.)
- **gap-count:** local a2_gap_balanced_v1.jsonl = 72 total / 38 gaps -- matches your n_gap=38 / n_cells=72.
- **gate0 (reported):** PASS 72/72, run_mode=full, metrics_source=measured_bge -> no smoke/synthetic slip (pending file confirm of the gate0 dict).
- **discrimination (reported):** discriminates=true, both classes + spread -> no degenerate NON_TEST.
- **coincidental-mention:** Tarjan/Hopcroft scored-as-gaps but high-confidence = the refuse-gate precision limit the eval EXPECTS (report-not-fail; baked into verdict_msg).

## Why I still need the metrics.json (verify-the-referent, not the summary)
The vet harness runs 5 deterministic checks against the ACTUAL metrics.json -- check (5) corpus-completeness requires the 38 gap-item ids IN `metrics.rows` to 1:1-match the validity-VET'd gap-id set (not just the COUNT), and checks (1)/(2) read the actual gate0_self_check + discrimination_self_check dicts (conf_spread > 1e-6). I run the harness on the real file -- I do NOT VET_PASS off the reported summary (that's the trust-the-referent discipline).

## Ask (single-dispatch: you own this chain's remote I/O)
SCP the single v6 metrics.json back to its local anchor dir so the harness default path resolves:
`data/exp_substrate_a2_decisive_test_untuned_auroc_gpu_v1/metrics.json` (or tell me the exact local path you drop it at and I point the harness there). Small file; push-pipeline-down doesn't block a direct SCP of one json (same bypass you used to dispatch).

## On file arrival (my next action)
`python tools/vet_a2_v3_verdict_2026-06-18.py <path>` -> full 5-check VET -> route VET_PASS/FAIL + the 41330 PRE-INGEST scope-caveat verbatim to Skunkworks for the cert-call. (B-beta gate: ALREADY_SEPARATES => LoRA Stage-2 has NO headroom; a calibrated threshold suffices -- but that's Skunkworks's verdict-VET call, scoped pre-ingest.)

## Standing (9th rule)
- Orchestrator: SCP the v6 metrics.json local (the one blocker for my deterministic VET).
- Skunkworks: full A2 v6 verdict-VET incoming once I run the harness on the real file (pre-ingest scope-caveat carried).
- ME: preliminary crosscheck PASS; HOLDING full VET for the file; continuing Item 1 (PART_OF cell) meanwhile.
- Waiting on: Orchestrator (v6 metrics.json SCP-back), then Skunkworks (verdict-VET), USER/infra (push-fix -> C/43892).

-- Exp-Dev (Prover)
