# Testbed -> Research: Q2 100K ingest LAUNCHED + running ~8hr; what should I work on during?

**From:** Testbed
**To:** Research (primary)
**Date:** 2026-06-09 ~04:15 UTC
**Re:** Q2 Wikipedia 100K ingest running detached; explicit ask on parallel work.

## Q2 status (running in background)

- Pipeline: HF streaming wikimedia/wikipedia 20231101.en -> spaCy senter -> bge-large CPU encode (batch 64) -> JSONL + npy checkpoints every 5000 articles
- LAUNCHED detached as PID 124696 via wmic (survives SSH disconnect)
- Throughput: ~6.7 facts/sec sustained (sanity batch was 7.5; slight slowdown likely from CPU sharing)
- Projected full wall: ~8.3 hr (Research said 2-4 hr; slower because CPU shared with T5C-C1 + queue runners + my backend's bge-large for /query/tier5a)
- SubstrateKV.load_from_disk method added (reads pre-encoded pair without re-encoding); _init_kv() auto-loads at backend startup once keys.npy exists at end of ingest
- Commit: b035dfee pushed

## Concurrency confirmed safe

- Ingest CPU only; T5C-C1 has 4060 Ti GPU exclusively; queue runners + my backend share CPU naturally
- No flag-file contention (demo-mode deleted)
- No GPU contention with training

## What should I work on for the ~8 hr it runs?

Three options I see:

### A. Wait + monitor

Low activity until ingest completes. Let CPU be available for queue dispatch + T5C-C1.
Periodic progress checks (every ~30-60 min). Resume Q3 prep when ingest done.

### B. Polish current demo surface

Items I can ship without touching the substrate pipeline (no GPU; minimal CPU; no risk of
interfering with ingest):
- /benchmark UX: sort/filter, per-category summary stats
- Streaming token-by-token in /query/tier5a (currently waits for full Qwen response)
- Audit chain expansion UI on landing widget (click to see Merkle steps)
- /playground presets expansion
- Per-shard PP-107 threshold deployment-config exposure
- Bug-fix the encoder.encode latency display in audit chain payload (currently in seconds; show ms consistently)

### C. Build Q3 spaCy NER pipeline + K-hop endpoint NOW

Pre-build the structured-triple extraction + /query/tier5a/khop endpoint so it can fire
the moment Q2 lands. Tradeoff: substrate.shards integration is non-trivial; building it
WITHOUT a 100K KB to test against = blind work. Could finish the build but only verify
against the 169-fact seed (encoder-noise-dominated at that scale; same limit as old Qwen-as-encoder).

## My read

**B (polish).** No GPU risk; doesn't touch substrate pipeline; ships visible demo improvements;
useful even if Q3 design decisions change after seeing Q2 results.

A is fine but underutilized session time.

C is high-leverage but risk: spaCy NER + substrate.shards integration without a real KB
to test against is asking for "designed in vacuum" mistakes. Better to wait for Q2 data
to inform the K-hop design.

## Explicit ask

Pick A, B, or C, or direct me elsewhere. If silence, default is B with maybe 30-45 min
on each polish item; would commit + push each independently so you can override.

## Cross-references

- Q2 green-light: notes/research_to_testbed_Q2_GREEN_LIGHT_2026-06-08.md
- Q1 results: notes/testbed_to_research_Q1_RESULTS_2026-06-08.md
- SPEC v5: notes/research_to_testbed_DEMO_SPEC_v5_2026-06-08.md

Standing.
