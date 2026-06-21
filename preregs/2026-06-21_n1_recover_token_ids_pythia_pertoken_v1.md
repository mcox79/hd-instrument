# Prereg: n1_recover_token_ids_pythia_pertoken_v1

**Date:** 2026-06-21
**Anchor name:** n1_recover_token_ids_pythia_pertoken_v1
**Script:** experiments/exp_n1_recover_token_ids_pythia_pertoken_v1.py
**Queue:** remote_cpu_queue
**Dependency:** MUST run AFTER phase05_v1_pythia160m_residual_extract_pertoken_v1 HARD_PASS is confirmed AND the npz is present at data/exp_phase05_v1_pythia160m_residual_extract_pertoken_v1/residuals_per_token.npz on marsh@home.
**N1 dependency:** The N1 substrate-native LM cell MUST NOT be dispatched until this anchor exits PASS and token_ids are confirmed present in the source npz.

## Problem statement

The per-token residual extraction cell saved residuals, doc_indices, doc_boundaries but discarded token_ids (input_ids). The npz at data/exp_phase05_v1_pythia160m_residual_extract_pertoken_v1/residuals_per_token.npz has shape residuals=(49634,768) with NO token_ids key. The N1 substrate-native LM cell requires real token sequences to measure token-level BPC; without token_ids the BPC metric is meaningless.

## Fix

CPU-only data-recovery: re-tokenize the same corpus in the same order with the identical tokenizer call, align via doc_boundaries, append token_ids to the npz in place. No model load, no GPU.

## Tokenizer call replicated (verbatim from source extraction cell)

Source function `_extract_residual_per_token_one_doc`:
```python
enc = tokenizer(doc, return_tensors="pt", truncation=True, max_length=MAX_TOK_LEN)
# MAX_TOK_LEN = 64
attn = enc.get("attention_mask")
if attn is not None:
    t_real = int(attn[0].sum().item())
else:
    t_real = int(input_ids.shape[1])
```

Recovery cell replication (no torch, return_tensors=None):
```python
enc = tokenizer(doc, return_tensors=None, truncation=True, max_length=64, padding=False)
attn = enc.get("attention_mask")
t_real = int(sum(attn)) if attn is not None else len(enc["input_ids"])
ids = enc["input_ids"][:t_real]
```

The `return_tensors=None` + `padding=False` path for a single-doc encoding produces identical tokenization output as `return_tensors="pt"` with `truncation=True, max_length=64`. The attention_mask sum is identical (no padding = all 1s; truncation behavior identical).

## Alignment logic

For each of the n_docs extraction docs (indexed by doc_boundaries), we assert that the re-tokenized length equals `doc_boundaries[i+1] - doc_boundaries[i]`. If the source extraction skipped docs (error handling), a greedy lookahead scan (MAX_LOOKAHEAD=50) finds the matching corpus doc. HARD ASSERT: every per-doc length matches AND the flat token_ids total equals residuals.shape[0]=49634.

## What happens on mismatch

If any extraction doc cannot be aligned within the lookahead window, the cell raises RuntimeError with a precise diagnostic (which extraction doc index, expected vs got token count, and sample retok lengths from surrounding corpus). The verdict is HARD_FAIL (written to metrics.json). The orchestrator signal is: fall back to GPU re-extraction that saves token_ids at extraction time (instrument the source cell to add token_ids to the npz before re-running).

## Pre-registered threshold bands

HARD-PASS: alignment succeeds for ALL n_docs docs; total token_ids == residuals.shape[0]; npz re-saved with token_ids key; os.replace succeeds; final verify confirms token_ids present.

MIDDLE-BAND: not applicable (this is a one-shot data-recovery; either it works for all docs or HARD_FAIL).

HARD-FAIL: any of:
  - Source npz not found (wrong runner, not remote_cpu_queue)
  - Any per-doc length mismatch that cannot be resolved by greedy lookahead
  - npz rewrite fails (disk error, compression error, replace fails)
  - Final verify shows token_ids absent
  - Corpus download fails or has fewer rows than extraction doc count

Note: calibration-probe band policy (+-50%) is not applicable here. This is a deterministic data-recovery cell (alignment either succeeds or fails; there is no "effect size" to calibrate).

## Idempotency

If the npz already has token_ids, the cell prints ALREADY_RECOVERED and exits PASS without rewriting. Safe to re-run.

## PROT-018 N-suffix

No _nN suffix. The token count is derived from the source npz (49634 tokens over 6000 docs), not a swept hyperparameter.

## N-suffix section

No _nN suffix; production N/token-count = data-derived (49634); rationale: this is a recovery cell, not a scale sweep.

## Timeout estimate

No smoke wall time available (CPU-only tokenizer + datasets; corpus download dominates).
Estimate basis:
- Dataset download: ~30s (already cached on runner from prior extraction)
- Tokenizer load: ~5s
- Re-tokenize 6000 docs at ~64 tokens each: ~10s (CPU tokenizer is fast)
- npz rewrite (49634 x 768 float32 = ~150MB uncompressed): ~30-60s compressed
- Total estimate: ~120-180s plus any cold-cache dataset download overhead

timeout_s = 1800 (30 min; generous margin for cold download + compression of large npz)

## Smoke profile

--smoke mode aligns only the first 5 docs (fast local gate); does NOT rewrite the npz. Use to verify alignment logic without running the full re-tokenization sweep.

## Queue

remote_cpu_queue (marsh@home). The source npz only exists on remote. Do NOT route to local_cpu_queue or overnight_queue; this cell is pure CPU.

## Post-ship dependency note for N1 cell

The N1 substrate-native LM experiment MUST declare a dependency on this recovery anchor completing with verdict=PASS. Specifically:
1. Ship this anchor to remote_cpu_queue first.
2. Confirm metrics.json verdict=PASS and that npz keys include token_ids.
3. ONLY THEN dispatch the N1 cell.
