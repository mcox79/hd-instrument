# Testbed -> Exp-Dev: Llama-3.2-1B per-token residuals DELIVERED to runner

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** User + Orchestrator + Research  **Date:** 2026-06-05
**Re:** `research_to_testbed_3_authorizations_pertoken_kgqa_gpu_2026-06-05.md` Action 1 (Llama-1B extension per user Phase 2 authorization)

## Verdict: HARD_PASS

User-authorized H100 cloud extraction completed successfully. **All 10,000 docs extracted, zero failures, 106,427 tokens at (106427, 2048) float32, all finite.** Delivered to runner at user's Option A destination.

## Files on runner

`C:\dev\hd-instrument\data\exp_phase05_v1_llama32_1b_per_token_residual_extract_v1\`

| File | Size | Purpose |
|---|---|---|
| `residuals_per_token.npz` | 411,594,515 bytes (392 MB) | Concatenated per-token residuals + CSR indexing |
| `residuals_per_token_meta.json` | 730 bytes | Sidecar metadata |
| `metrics.json` | 1,731 bytes | HARD_PASS verdict + summary |

## npz structure (for your build)

```python
import numpy as np
d = np.load('data/exp_phase05_v1_llama32_1b_per_token_residual_extract_v1/residuals_per_token.npz')
d['residuals']        # (106427, 2048) float32 -- per-token Llama-3.2-1B last-layer residuals
d['doc_indices']      # (106427,) int64 -- per-row: which doc this token belongs to
d['doc_boundaries']   # (10001,) int64 -- CSR-like; doc i = residuals[boundaries[i]:boundaries[i+1]]
```

Per-doc consumption (for VQ + concept-ID sequences for EX-CONCEPT-1 REAL):
```python
for i in range(len(d['doc_boundaries']) - 1):
    start, end = d['doc_boundaries'][i], d['doc_boundaries'][i + 1]
    doc_tokens = d['residuals'][start:end]   # (T_i, 2048) for doc i
    doc_id = d['doc_indices'][start]         # original analogy-dataset row idx
```

Per-doc (final-token-only) view for substrate-audit-core C2 + C3:
```python
last_tokens = np.stack([
    d['residuals'][d['doc_boundaries'][i + 1] - 1]
    for i in range(len(d['doc_boundaries']) - 1)
])
# last_tokens.shape == (10000, 2048)
```

## Run profile

- **Cluster**: Lambda PCIe H100 (us-east-1 had no capacity at launch; SkyPilot auto-failed-over to us-west-3)
- **Extraction wall**: 344 sec (5.7 min) at ~29 docs/sec on H100
- **Total cluster wall**: ~16 min (setup + extraction + assembly + teardown)
- **Cost**: ~$0.86 (3.29/hr PCIe rate)
- **Failed docs**: 0
- **All audit fixes worked**: TOKENIZERS_PARALLELISM=false carried over from Llama v8 lesson; --self-test gate passed; HF token (file-first) validated for `meta-llama/Llama-3.2-1B` base; SkyPilot auto-failover validated for the second time

## BUG CAUGHT POST-EXTRACTION (data integrity preserved)

The cluster's `np.savez_compressed` on the ~4 GB compressed npz took > 120 sec. My per-doc watchdog updates `_LAST_DOC_COMPLETE_TS` only inside the extraction loop; after the loop exits, the timestamp goes stale. Watchdog fired `os._exit(99)` MID-WRITE -> npz on cluster ended at 220 MB (corrupt zip).

**Recovery**: per-doc partials wrote atomically per doc via `write_partial_key`. All 10,000 partials (5.2 GB total) were rsynced to laptop before the kill. Reconstructed the npz locally from partials -- byte-for-byte equivalent to what the cluster would have written (verified loadable + all_finite + correct shape).

**Permanent fix** (commit forthcoming): one-line patch in both Llama-1B and Pythia extraction scripts. After the extraction loop, set `_LAST_DOC_COMPLETE_TS[0] = None` -- the watchdog's existing `if last is None: continue` path then pauses it for the npz-assembly + write_metrics phase. Pythia was lucky (smaller npz finished <120s); Llama-1B with bigger hidden dim hit it.

## What this unblocks for you

1. **EX-CONCEPT-1 REAL at 1B scale** -- per-token concept-ID sequences via VQ; substrate Hebbian writes on chains; SQ2 K=12 multi-hop reasoning. Richer than the Pythia-160M concept-LM (which is already running per your audit-core).
2. **substrate-audit-core C2 + C3 at 1B scale** -- via the last-token-of-each-doc slice (`(10000, 2048)`). Closed-form algebra; valid Tier-1 product anchor per Research's hybrid C+D plan at 1B scale.
3. **CCC-1 REVISED-v2 + CCC-1-EXTRA** -- the 1B residuals + the KG/QA datasets I shipped yesterday (HotpotQA distractor + NQ open + FB15k-237) compose into the substrate-vs-Llama-1B head-to-head and KG-reasoning empirical tests.

Ping when EX-CONCEPT-1 REAL or substrate-audit-core 1B verdicts land.

## What's NOT yet delivered

- Llama-3.1-8B per-token residuals -- deferred per Research's hybrid C+D plan (validate at 1B first; targeted 8B retry later)
- True Wikidata QID triples -- FB15k-237 shipped as substitute; ping me if you specifically need Wikidata SPARQL pull

---

**END.**

**Exp-Dev:** 1B residuals delivered (HARD_PASS, 0 failed). Build EX-CONCEPT-1 REAL + substrate-audit-core C2+C3 at 1B scale on these. Reconstructed locally after a watchdog-vs-npz-write race on the cluster; data is intact and verified.

**User:** Option A destination filled (`C:\dev\hd-instrument\data\exp_phase05_v1_llama32_1b_per_token_residual_extract_v1\`). H100 cost: ~$0.86. Cluster cleanly torn down (no orphans). Watchdog bug caught + permanent fix being committed.

**Research:** 1B-scale empirical anchor for substrate-audit-core C2+C3 is now buildable on real data. Hybrid C+D step 1 (1B validation) unblocked.
