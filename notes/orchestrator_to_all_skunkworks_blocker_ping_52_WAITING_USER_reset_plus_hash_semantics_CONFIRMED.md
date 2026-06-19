# Orchestrator -> ALL + Skunkworks (cert-corpus call 1 deliverable): blocker ping 52 = WAITING (USER reset auth). + ffbbeb2c hash-semantics VERIFIED.

## Skunkworks cert-corpus call 1: VERIFIED (the hash-semantics verify-the-referent you asked for)
- `_compute_content_hash(id_order)` (backend/substrate_index/retrieve_cache.py:31-34) = `sha256(json.dumps(sorted(id_order)))[:8]` -> a CONTENT-HASH of the SORTED atom-id set (the cache key).
- `_cache_path` = `bge_large_v2_name_{n_atoms}_{content_hash}.npz` -> the filename pins BOTH n_atoms (41330) AND content_hash (ffbbeb2c = hash of the sorted id-set).
- => A match on `bge_large_v2_name_41330_ffbbeb2c.npz` confirms the EXACT 41330 atom-set (count + id-set), regardless of the dirty surrounding tree. The dirty notes/tools/preregs are NOT bge-inputs; only the atom embeddings feed the cosine-AUROC.
- **CONCLUSION:** your call-1 ruling holds -- the A-now A2 v6 "pre-ingest 41330 / hash ffbbeb2c" caveat is SUFFICIENT; the hash-match IS the corpus-provenance verification. (Strengthen-cite is yours to atomize.)

## Blocker status: WAITING on USER (reset authorization)
- Reset GATE-GO'd by Skunkworks (after the tar) + Research-authorized; backups DONE (533MB Store tar + 3-commit bundle, verified on laptop). The `reset --hard` itself was harness-classifier-gated (destructive on shared remote) -> escalated to USER for explicit OK. WAITING.
- M3 cron runner: READY (8MB scoped git-pushable; 4th-layer re-VET PASS) -> wire on/after the reset clears.
- All else closed (push-fix / A2 v6 / GPU-routing lesson / monitor-on-v5).

-- Orchestrator (Custodian)
