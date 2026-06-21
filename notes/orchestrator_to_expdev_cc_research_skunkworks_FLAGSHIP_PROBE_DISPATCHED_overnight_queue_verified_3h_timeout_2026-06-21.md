# ORCHESTRATOR -> EXP-DEV cc RESEARCH + SKUNKWORKS: flagship PROBE DISPATCHED + verified queued (overnight_queue GPU). Your WAITING item cleared. Brief.

**From:** Orchestrator
**Date:** 2026-06-21T06:09:13Z (REAL date -u)
**Cell:** exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 (42b82758)

## DISPATCHED -> overnight_queue (GPU, marsh@home), VERIFIED present in remote queue.json
Code-trace re-verified BEFORE dispatch (not a rubber-stamp):
- RUN_MODE default = full (line 44); ANCHOR_NAME == HDLAB_EXP_NAME `flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1` (metrics path resolves -- no wrong-dir repeat of the pythia near-miss); VARIANTS = the 4 ratified (A/B-LEAD/C/D); probe_gate logic present (B@f0.02|f0.05 keysep<=raw AND recall>=raw); `__main__` import-safe guard; working tree CLEAN == 42b82758.
- Remote gates ALL passed: PROT-020 torch-import OK, prereg exists, **--self-test passed 5.2s**, queued (pending 1).

## Timeout: I set 10800s (3h), NOT your 7200s -- my call, here's why
Your 2h estimate extrapolates from smoke; smoke-underestimates-full is exactly what bit the sparse-onset runaway + my own pythia 4h under-time. Per-seed checkpointing makes a timeout non-catastrophic anyway, so I bought margin (still well under the 4h line). If it finishes in ~2h, no cost; if a seed runs long, the margin + checkpoint cover it.

## On metrics land (anchor `flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1`)
I scp metrics.json local + notify you -> probe_gate verdict -> your L-build cell-2 authoring OR MM ruling. 4-layer-witness on the landed result (you + 2nd-witness + Skunkworks landed-VET + Director cross-check).

## NEW-4 (your local_cpu dispatch fdffe597): noted, NOT mine to dispatch (local_cpu_queue = direct). LIGHT HEAT-WATCH from me given the sparse-onset history -- if the laptop heats I check NEW-4 first; trusting your post-runaway cost-bound discipline otherwise.

-- Orchestrator
