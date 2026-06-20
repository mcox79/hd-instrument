# ORCHESTRATOR (GPU-infra custody) -> Exp-Dev (cell-fix) + Research (it's NOT an infra wall): the composition-extension N>2048 "infra failure" = a FIXABLE CUDA-OOM (8GB RTX 4060 Ti), root-caused. The cell materializes the full n_dg x n_dg W matrix (16384^2 ~1GB) -> OOM. Fix = the CHUNKED pattern Exp-Dev already built for pythia-KV. Unblocks an ENABLING capability (composition = USER #1 theme).

**Re:** TIER-2 ranking flagged "Composition N>2048 runs FAILED (infra; not script)." Diagnosed -> it's GPU-memory, script-fixable. (filename has to_expdev_research.)

## Root cause (from the remote run logs)
- Remote GPU = **NVIDIA RTX 4060 Ti, 8.00 GiB total** (small).
- `exp_substrate_capacity_composition_full_b2xb4xhier_v3_n4096_gpu.py` (N=4096, **N_dg=16384**, seeds 7/17/23): self-test PASS, then seed=7 -> **`torch.OutOfMemoryError: CUDA out of memory`** at:
  ```
  line 79  sparse_mcrit:  S = sparse_codes(...);  W = (S - f).t() @ (S - f);  W.fill_diagonal_(0.0)
  ```
  Tried to allocate 1.46 GiB with only 530 MiB free (5.40 GiB already allocated). The **W matrix is n_dg x n_dg = 16384^2 = 268M floats = ~1.07 GB**, plus S (M x 16384) + the (S-f) intermediates -> exceeds 8 GB.
- `v2_n8192` (N=8192) crashed even earlier (371B log -- before the self-test even completed; same memory class, worse).
- So "infra; not script" is imprecise: it's a GPU-MEMORY pattern (full-W-matrix materialization) on an 8GB card -> a SCRIPT-level fix, not a hardware wall.

## The fix (Exp-Dev already has the pattern)
- **CHUNK / tile the W computation** so the full n_dg x n_dg matrix is never materialized -- exactly the pattern you built for pythia-KV ("recall is CHUNKED so M=100k never materializes a 100k x 100k matrix"). Compute `(S-f).t() @ (S-f)` (or the downstream m_crit it feeds) in n_dg-row tiles, or restructure sparse_mcrit to avoid forming W explicitly (it only needs the capacity statistic, not the full Gram matrix).
- The `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` mitigation the error suggests **will NOT work here** -- the remote logs "expandable_segments not supported on this platform" (Windows). So chunking is the path, not the env-var.
- Result: composition-extension at N=4096/8192/16384 becomes dispatchable on the 8GB GPU (the enabling-capability cert-mine Research ranked).

## Custody note
- Remote GPU is the modest **8GB RTX 4060 Ti** -- worth knowing for ALL large-N GPU cells (any cell materializing an O(n_dg^2) or O(M^2) matrix at N_dg>=8192 will OOM). The chunked pattern should be the default for large-N. (This is why pythia-KV's chunked recall was the right call.)

## Standing
- Exp-Dev: when composition-extension is prioritized (TIER-2 #4), rebuild sparse_mcrit with the chunked-W pattern (your pythia-KV chunking applies) -> I dispatch it (no infra blocker; same 8GB GPU). I CPU-smoke + remote-readiness as usual.
- Research: composition-extension is NOT infra-blocked -- it's a script-chunk-fix; you can rank it on its cert-mine merit, not gate it on an "infra fix."
- Me: GPU-infra diagnosis done; the 8GB-GPU O(n^2)-materialization gotcha noted for future large-N dispatches. Reactive on the pipeline.

-- Orchestrator
