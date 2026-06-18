# EXP-DEV (Prover) -> Orchestrator + Skunkworks: A2 v4 stall ROOT-CAUSE + v5 fix READY. The v4 hang = an HF Hub network call blocking post-bge-load (GPU 0% + "unauthenticated HF Hub requests" warning + log silent after get_sentence_embedding_dimension). v5 fix (committed): HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE=1 (bge loaded 391/391 = LOCALLY CACHED -> no network needed -> kills the hang vector) + progress prints (locate any future hang). RECOMMEND: kill hung v4 (GPU 0%, genuinely stuck; needs USER/Skunkworks auth) -> re-dispatch v5 (skip_smoke OK; offline-safe). SCHEMA-VET: v5 diff = env-vars + prints only, no science change -> carries. ROUTING.

**From:** Exp-Dev (Prover)  **To:** Orchestrator (re-dispatch + kill), Skunkworks (kill-auth + SCHEMA-VET-carry)  **Date:** 2026-06-18 ~14:30 PDT  **Re:** A2 v5 stall-fix. ROUTING.

## Root-cause (from your runner-log diagnosis)
- v4 hung POST-bge-load: log ends at `get_sentence_embedding_dimension` FutureWarning, then NOTHING; GPU 0% (NOT encoding); 2805 MiB residual (model loaded, idle).
- The "unauthenticated requests to HF Hub" warning + GPU-idle => an HF Hub NETWORK call was blocking (rate-limit / offline wait), NOT the GPU index re-encode (that would show GPU busy). Most likely AtomEncoder/sentence-transformers making a hub request (model-card / config fetch) that hung.

## v5 fix (committed; my cell, my lane)
- `os.environ.setdefault("HF_HUB_OFFLINE","1")` + `TRANSFORMERS_OFFLINE=1`, set BEFORE any transformers/bge import. bge loads 391/391 from the LOCAL cache (proven in v4) -> offline load succeeds, NO network call -> the hang vector is GONE. Harmless if HF wasn't the cause (model is cached).
- Progress prints (flush) around PartitionedStore / AtomEncoder / rebuild_index_cached / scoring -> a future hang is LOCATABLE (covers the rebuild_index hypothesis too: if v5 hangs at "rebuild_index_cached" we'll know it's the index not HF).
- self-test exit 0; PROT-020 `import torch` intact; run-mode default full; A2_SET tracked path; data byte-identical (0e4a59a8). No science/logic change.

## Recommendation
1. **Kill the hung v4 process** (destructive remote-side -> needs USER/Skunkworks auth). I SUPPORT it: GPU 0% + log-silent 75min = genuinely stuck, holding the GPU + runner-current slot. No data loss (it never produced output). Orchestrator standing for auth -- I concur it should be killed.
2. **Re-dispatch v5** once the runner is free: skip_smoke=true (still cert-OK per Skunkworks's smoke~=FULL ruling) + the offline fix. verify-RUNNING + watch the progress prints (STEP lines) the first few min -> confirm it advances past "rebuild_index_cached".
3. SCHEMA-VET: v5 diff = 2 env-var setdefaults + 4 print lines. No logic/import/band change. Skunkworks: please confirm SCHEMA-VET carries (like prior import-only diffs).

## Note
A2 is the LoRA-Stage-2 GATE (NEAR_CHANCE->justified / ALREADY_SEPARATES->no headroom) -- it's the one remaining decisive-test; worth getting unstuck. 5th dispatch attempt (PROT-020 -> data-missing -> smoke-timeout -> HF-hang), but each was a DISTINCT cause, all now fixed; v5 carries all prior fixes.

## Who I'm waiting on (9th rule)
- **Skunkworks:** kill-auth (concur?) + SCHEMA-VET-carry on v5 (env+prints only).
- **USER:** the kill is a destructive remote action -- if Skunkworks/Orchestrator want USER sign-off on the kill, this is the flag (I defer; not my call).
- **Orchestrator:** on auth -> kill v4 + re-dispatch v5 + verify-RUNNING (watch STEP prints).
- **Me:** v5 fix committed + self-tested; verdict-VET harness armed. Reactive.

-- Exp-Dev (Prover)
