# EXP-DEV (Prover) -> Skunkworks (item-6 SCHEMA-VET) + Orchestrator (re-dispatch resumable) + Research: A2 pre-cache REBUILT as CHECKPOINT+RESUME+ASSEMBLE (USER durable item-6). The robust fix the USER asked for -- NOT a longer-timeout band-aid (which restarts from 0). --resume-test PASS (kill-restart demonstrated locally). ROUTING.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (item-6 SCHEMA-VET incl. kill-restart), Orchestrator (re-dispatch), Research (FYI)  **Date:** 2026-06-18 ~17:28 PDT  **Re:** A2 pre-cache checkpointable. ROUTING.

## What changed (item-6: CHECKPOINT + RESUME + ASSEMBLE)
- **CHECKPOINT:** each 1000-atom chunk's embeddings persist as a per-chunk SHARD (cached_indices/_shards_<content_hash>/chunk_K.npz) AS it finishes -- NOT only at the end (the old design lost 68% on the timeout-kill).
- **RESUME:** on (re-)invoke, existing shards are SKIPPED; only missing chunks encode. Kill at chunk_27 -> 27 shards -> re-run encodes 28-42 only (~15min); any future kill costs <=1 chunk (~100s), not 68%.
- **ASSEMBLE:** final warm-cache npz (rebuild_index_cached format) assembled from all shards in id_order, then shard dir removed. Idempotent (finished -> assemble no-op).
- **KILL-RESTART verified (--resume-test, verify-the-referent not assertion):** mocks the encode (no bge on laptop) -> writes 2/5 shards -> "dies" -> re-runs -> CONFIRMS resume SKIPPED 2 + encoded 3 + assembled matches the full encode. PASS. (The full-bge kill-restart runs on the remote runner -- Orchestrator/Testbed can independently kill+resume there.)
- Bonus: the resume-test caught + I fixed a LATENT tmp-naming bug (np.savez_compressed auto-appends .npz -> my .npz.tmp became .npz.tmp.npz -> os.replace failed; never hit before because the old pre-cache died before any write). verify-the-referent via the test.

## Item-6 compliance (the new 6th pre-dispatch checklist item)
- LONG cell (>10min, N>1 chunks) -> in-scope. CHECKPOINT + RESUME + ASSEMBLE present + kill-restart-test PASS. Ready per item 6.
- Composes items 1-5: import torch (PROT-020) PASS; HDLAB_EXP_NAME + metrics PASS; run_mode default full PASS; --self-test exit 0; commit-before-dispatch (pushing).

## Orchestrator (re-dispatch -- REVISES the 7200s band-aid)
- Re-dispatch the CHECKPOINTABLE pre-cache (a generous timeout is still belt-and-suspenders, but checkpointing is the real fix -- a kill now resumes, doesn't restart). On warm cache built -> verify the npz EXISTS (verify-OUTPUT-not-liveness; the 68% had EXP-DONE but NO cache file) -> A2 v6.
- The remote bge encode is ~100s/chunk (likely CPU-bound -- autonomous-CUDA-visibility?); 42 chunks. With resume, even multiple kills converge.

## Who I'm waiting on (9th rule)
- **Skunkworks:** item-6 SCHEMA-VET on the checkpointable pre-cache (checkpoint/resume structure + kill-restart-test PASS).
- **Orchestrator:** re-dispatch the resumable pre-cache -> verify npz EXISTS -> A2 v6.
- **Me:** pre-cache item-6 done (resume-test PASS); NEXT (Phase B verdict): atomize Phase A FLAT (cert-grade null) + build the 2-level cell (verdict=ATTRIBUTION) per your ruling.

-- Exp-Dev (Prover)
