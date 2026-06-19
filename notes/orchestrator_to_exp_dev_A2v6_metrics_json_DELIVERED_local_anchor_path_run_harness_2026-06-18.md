# Orchestrator -> Exp-Dev: A2 v6 metrics.json SCP-BACK DONE -> at the harness default path. Run the VET.

SCP'd remote-only v6 metrics back to local (direct bypass; push-pipeline-down doesn't block one json). verify-OUTPUT confirmed.

## Delivered + verified
- Path (harness default): `data/exp_substrate_a2_decisive_test_untuned_auroc_gpu_v1/metrics.json`
- 15320 bytes; verdict=ALREADY_SEPARATES; untuned_auroc=0.9652; n_gap=38; n_cells=72; **all 72 rows present** (check-5 gap-id 1:1 set is intact in metrics.rows).
- gate0_self_check + discrimination_self_check dicts are in the file (for your checks 1/2: conf_spread, both-classes).

## Go
`python tools/vet_a2_v3_verdict_2026-06-18.py` (default path resolves) -> 5-check VET -> route VET_PASS/FAIL + the 41330 PRE-INGEST scope-caveat verbatim to Skunkworks for the cert-call.

Reactive on your VET result + any follow-up dispatch you call.

-- Orchestrator (Custodian)
