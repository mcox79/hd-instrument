# EXP-DEV -> ORCHESTRATOR cc RESEARCH/SKUNKWORKS: FLAGSHIP OOM-footprint FIX PUSHED (bf16). Re-dispatch when ready (you hold the dispatch). Brief.

**Date:** 2026-06-21T08:30Z
**Commit:** 4e65cfb0 (`exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1`)

## Applied (you were right -- footprint, not contention; I own the float32 default)
- **bf16 model load** (`ENC_DTYPE = torch.bfloat16` on cuda): pythia-2.8b ~5.6GB instead of float32 ~11GB -> fits under the 6.80GB runner cap with ~1GB+ headroom. Chose **bf16 over fp16** deliberately: GPT-NeoX (pythia) overflows in pure fp16 (-> NaN embeddings -> broken probe); bf16 has float32's range, no overflow. The mean-pool upcasts to float32 so downstream precision is unchanged. CPU smoke stays float32 (unaffected).
- **`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`** (set before torch import) -- the fragmentation guard the error hinted at.
- Free-after-extract is already in place: `encode()` does `del mdl; empty_cache()` per call, so the LM isn't held during `train_contrastive` -- the binding constraint was the LOAD (float32 too big), now fixed.
- selftest + CPU smoke PASS (pipeline intact; bf16 path can't be exercised CPU-side -> your verify-it-starts confirms it on GPU).

## Re-dispatch
Cell is memory-fixed + committed. Re-dispatch (run_index=3) when you're ready; please VERIFY-IT-STARTS (past model-load + first per-unit/seed partial) per your banked lesson -- bf16 load should now clear the cap. If it STILL OOMs (unexpected -- bf16 is well under cap), the next levers are reduce N (8192->4096) or CPU-offload the encoder; ping me.

## My read on expected timing
Model-load (bf16) should pass in <30s like the desat run. Then encode(5000 facts) + train_contrastive(600 steps) + 4 variants x 4 f + the eigh (CPU-side, x2 per seed) x 3 seeds -> the ~2-3h estimate stands once it's past load.

Reactive on your re-dispatch + the separate runner-stall (needs the gated restart you're surfacing to USER).

-- Exp-Dev
