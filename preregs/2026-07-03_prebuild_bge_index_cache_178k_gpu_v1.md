# Pre-registration: prebuild_bge_index_cache_178k_gpu_v1

Author: hdi_orchestrator (Director-tasked; Testbed Blocker A+B fixes just landed)
Date: 2026-07-03
Class: Infra rebuild (cache-write only; ZERO substrate-atom mutation)

## Intent

Build the BGE-large NAME-encoded retrieval index cache for the full 177,861-atom substrate. This is the load-bearing prerequisite for the 170K-scale unified re-test cell (Exp 1 + Exp 2C + Exp 3E arms). Prior max cache scale: 43,905 atoms; extrapolation factor ~4x.

## Referent

- Cell: `experiments/exp_prebuild_bge_index_cache_gpu_v1.py`
- Same cell that produced the 41,330-atom cache (verdict PASS in 4188s per `data/exp_prebuild_bge_index_cache_gpu_v1/metrics.json`); CHECKPOINT+RESUME+ASSEMBLE via 1000-atom shards is verified via `--resume-test`.
- Anchor `prebuild_bge_index_cache_178k_gpu_v1` (new metrics dir; internal `anchor_name` field carries `prebuild_bge_index_cache_gpu_v1` cosmetically).
- Cache entry point: `backend/substrate_index/retrieve_cache.py::rebuild_index_cached()` (invoked via AtomEncoder+chunked shard path).

## Pre-conditions verified

- Testbed Blocker A+B fixes merged to main; `PartitionedStore.all_atoms()` succeeds at 177,861 atoms per Testbed report.
- 58 orphan AtomKinds added; no enum errors expected.
- Wikidata PID->rel_type map applied (3 rel_types); no typing regressions expected.
- No existing 178K cache in `data/substrate_index/cached_indices/` (max is 43,905).

## Bands (PASS / FAIL / SATURATION)

- PASS: `verdict=PASS` in emitted metrics.json AND `cache_file` matches `bge_large_v2_name_177861_<hash>.npz` AND `n_atoms == 177861` AND cache file present in `data/substrate_index/cached_indices/` with size ~1.3 GB (extrapolated from 41K=315MB linearly).
- FAIL: any of: `verdict != PASS`, `n_atoms != 177861`, missing cache file post-assemble, HARD_FAIL exit codes 4 or 5 (shard-missing / cache-not-written).
- SATURATION: N/A (deterministic cache-write; no bands to saturate).

## Timeout justification

Prior gpu_v1 at 41,330 atoms: encode_seconds=4182.3s (~70 min). Linear extrapolation to 177,861 atoms: 4182.3 * (177861/41330) = 17,997s (~5 hr). Timeout: 21,600s (6 hr) provides ~20% headroom. Shard-based CHECKPOINT means kill-restart is safe (loses at most ~100s of one chunk).

## Verdict schema

- `verdict`: PASS | HARD_FAIL
- `verdict_msg`: cell summary line
- `n_atoms`: 177,861 (expected)
- `cache_file`: filename produced
- `encoded_chunks` + `resumed_chunks`: sum to `n_chunks = ceil(177861/1000) = 178`
- `elapsed_s`, `encode_seconds`

## Post-build verification

- `data/substrate_index/cached_indices/bge_large_v2_name_177861_<hash>.npz` exists
- `retrieve_cache.py::rebuild_index_cached()` returns True (cache hit) on next invocation, wall < 30s (vs ~5hr rebuild)
- Prior gpu_v1 cache (41,330 atoms) retained (independent hash).

## Notes

- CACHE WRITE ONLY. Zero substrate-atom mutation (Testbed invariant).
- No PROT-020 concerns (`import torch` present per cell L36; GPU path via AtomEncoder+bge-large-en).
- `HDLAB_EXP_NAME=prebuild_bge_index_cache_178k_gpu_v1` routes metrics to `data/exp_prebuild_bge_index_cache_178k_gpu_v1/metrics.json`.
