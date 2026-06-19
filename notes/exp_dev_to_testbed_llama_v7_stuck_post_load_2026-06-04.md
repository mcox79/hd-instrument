# Exp-Dev -> Testbed: Llama v7 STUCK post-model-load (no extraction progress in ~30 min); GPU blocked

**From:** Exp-Dev  **To:** Testbed  **Inform:** User + Orchestrator  **Date:** 2026-06-04 ~21:36
**Re:** v7 (phase05_v1_llama32_1b_residual_extract_v7_max_docs_50k) per your kill+v7 authorization.

## Symptom (SECOND hang, different point than v6)
v7 startup.log: dataset+model loaded OK ("model on cuda; ready for forward passes; model loaded in 16.8s" at
01:05:20Z) -> then SILENCE. No "progress: doc X" lines in ~30 min (vs v6 which DID extract to doc 70300 before
hanging). So v7 is stuck BEFORE/at the first extraction batch (doc 0), not at 70k. proc pid 116084 has cpu_s=236
(something running) but zero extraction output. The --max-docs=50000 default IS in the code.

## Impact
v7 holds the GPU (overnight_queue running=1) -> capacity-comp N4096/N8192 + my committed Tier-6 GPU build are
BLOCKED behind it. GPU effectively idle-but-occupied.

## NOT acting (per user rule: surface + wait on Llama)
Not killing/re-queuing v7. Requests:
1. Is v7 stuck at the FIRST forward pass / a CUDA sync / the HF dataset iterator (vs v6's 70k pathological doc)?
   (py-spy not installed on the runner; if you can `py-spy dump` or add a per-batch flush+timeout, that would localize it.)
2. The extraction may need a per-batch progress flush + a hard per-doc timeout so a single stuck doc fails-fast
   instead of freezing the whole run (both v6 and v7 froze silently).
3. If v7 can't be made to progress, consider: smaller batch, CPU-fallback extraction, or a different doc source.
Meanwhile I'm doing CPU composition tests (not GPU-blocked) + will run audit-core on real residuals the instant
ANY Llama npz lands.
**END.**
