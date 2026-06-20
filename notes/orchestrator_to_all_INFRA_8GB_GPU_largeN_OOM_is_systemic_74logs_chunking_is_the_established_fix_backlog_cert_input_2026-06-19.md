# ORCHESTRATOR (GPU-infra custody) -> ALL: INFRA CONTEXT for the backlog-certification -- the 8GB RTX 4060 Ti is a SYSTEMIC large-N constraint. 74 remote logs show CUDA-OOM (large-N capacity/composition/scaling/storage/KG). The fix is ESTABLISHED (chunking/serialization -- already applied in several RESCUE versions). Large-N enabling certs need the CHUNKED pattern, not a plain re-dispatch.

**Re:** extends my composition-extension OOM diagnosis to the whole backlog (USER directive = certify the backlog). (filename has to_all.) Honestly scoped below.

## The pattern (from a remote-log scan for OutOfMemoryError)
- **74 overnight_queue logs contain CUDA OOM.** Almost all are large-N (n8192 / 16384 / 32768 / 65536) experiments that materialize an O(n^2) or O(M^2) matrix on the **8GB** GPU: capacity (moe/sharding/n_scaling/modern_hopfield), composition (b2xb4xhier / q_a3 cross-layer n32768 / patternb_1M), storage (continuous_embedding n16384), sparse-vs-dense large-N, KG-sharded-50k, codebook, etc.
- **HONEST SCOPE (not 74 currently-blocked):** the naming shows the team ALREADY knows the fix -- several have `_RESCUE_serialized` / `chunked_codebook` / `n_scaling_..._rescue` / `gpu_large_n_rescue_serialized` versions = chunked/serialized rebuilds that DID run. So a chunk of the 74 are HISTORICAL OOMs that were subsequently rescued. The systemic CONSTRAINT is real; the count of still-blocked is smaller (per-experiment check needed).

## Why this matters for the backlog-certification (the planning input)
- For the enabling-capability certs that are large-N (composition-extension N>2048, capacity beyond N2048, sparse-vs-dense-large-N, KG-sharded), a **plain re-dispatch will OOM** -- they need the chunked/serialized rebuild FIRST (the pythia-KV chunked-recall pattern; the existing RESCUE versions are the template). So budget cert-effort = "chunk-rebuild + dispatch", not "just re-run".
- For NEW large-N enabling cells (effrank/neurogenesis/etc. at N>=8192): default to the chunked pattern up front (avoid the OOM round-trip). The 8GB card materializes ~1GB at n_dg=16384 for a single n^2 matrix -> 2-3 such allocations OOM.

## Custody action (mine, going forward)
- I'll CPU-smoke + flag any large-N GPU cell that materializes O(n^2)/O(M^2) at dispatch-readiness (pre-empt the OOM, like I caught composition-extension). The "is it chunked?" check joins my dispatch-readiness review for n>=8192 GPU cells.
- Option (not my call): a bigger remote GPU would remove the constraint wholesale, but chunking is the zero-cost path + already the established pattern. Flagging the hardware reality (8GB) for awareness.

## Standing
- Exp-Dev/Research: large-N enabling certs need the chunked rebuild (template = your RESCUE/serialized versions + pythia-KV chunking); not infra-walls, just chunk-fixes. composition-extension is the worked example (separate note).
- Me: 8GB-GPU O(n^2) gotcha now part of my large-N dispatch-readiness check. Reactive on the pipeline.

-- Orchestrator
