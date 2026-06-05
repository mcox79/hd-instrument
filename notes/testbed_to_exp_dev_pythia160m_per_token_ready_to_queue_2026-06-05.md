# Testbed -> Exp-Dev: Pythia-160M per-token extraction ready; please queue

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** User + Orchestrator + Research  **Date:** 2026-06-05
**Re:** `research_to_testbed_3_authorizations_pertoken_kgqa_gpu_2026-06-05.md` (Action 1)

## User authorization + research request

User authorized 2026-06-05 ~08:30: augment Pythia extraction with `--per-token` flag to unblock EX-CONCEPT-1 REAL. Existing per-doc HARD_PASS run preserved (different output filename).

## Script + smoke

Same script (`experiments/exp_phase05_v1_pythia160m_residual_extract_v1.py`) with new `--per-token` flag. Commit `34137e9`. Smoke regression: BOTH modes work end-to-end with synthetic residuals locally.

**Per-doc smoke (unchanged)**:
```
extraction mode: perdoc (final-token only per doc)
50 synth docs -> residuals shape (50, 768) -> residuals.npz
verdict=HARD_FAIL (50 < 2500 docs floor; expected smoke behavior)
```

**Per-token smoke (NEW)**:
```
extraction mode: pertoken (all token positions per doc)
50 synth docs -> 509 tokens total -> residuals shape (509, 768) -> residuals_per_token.npz
keys: ['residuals', 'doc_indices', 'doc_boundaries']
  doc_indices[:10] = [0,0,0,0,0,0,0,0,0,1]   (CSR: doc 0 = rows 0-8)
  doc_boundaries[:5] = [0, 9, 19, 23, 32]    (doc i = residuals[boundaries[i]:boundaries[i+1]])
verdict=HARD_FAIL (50 < 2500 docs floor; expected smoke behavior)
```

## npz format spec (per-token mode)

```python
loaded = np.load('residuals_per_token.npz')
loaded['residuals']        # (sum_T, 768) float32; concatenated per-token residuals
loaded['doc_indices']      # (sum_T,) int64; for each row, which doc it came from
loaded['doc_boundaries']   # (n_docs+1,) int64; CSR-like; doc i = residuals[bounds[i]:bounds[i+1]]
```

Per-doc consumption pattern (for VQ + concept-ID sequences):
```python
for i in range(len(doc_boundaries) - 1):
    start, end = doc_boundaries[i], doc_boundaries[i + 1]
    doc_tokens = residuals[start:end]   # (T_i, 768) for doc i
    doc_id = doc_indices[start]         # original doc index
    # VQ each token -> concept_id sequence for substrate Hebbian writes
```

Per-token sidecar: `residuals_per_token_meta.json` with `n_tokens_total`, `extraction_mode=pertoken`, etc.

## What's preserved (per-doc mode)

The existing per-doc HARD_PASS npz (`residuals.npz`, shape `(n_docs, 768)`) is NOT modified or re-extracted. The per-token mode emits a SEPARATE file (`residuals_per_token.npz`). Your audit-core C2/C3 build on `residuals.npz` continues unaffected.

## Queue command (PowerShell on marsh@home)

```powershell
git -C C:\dev\hd-instrument pull origin main
bash tools/orchestrator/queue_add.sh overnight_queue \
  phase05_v1_pythia160m_residual_extract_v1 \
  experiments/exp_phase05_v1_pythia160m_residual_extract_v1.py \
  preregs/2026-06-04_phase05_v1_pythia160m_residual_extract_v1.md \
  3600 \
  --rerun-as phase05_v1_pythia160m_residual_extract_v1_per_token \
  -- --per-token
```

(Reuses existing prereg; the extraction-mode is now a CLI flag so the same anchor script handles both. Different `--rerun-as` keeps the data dirs separate so the per-doc HARD_PASS run isn't overwritten.)

## Expected wall + log shape

Same model load (~5-10s) + same dataset iter + per-token forward (~50-100ms per doc; same forward pass, slice differs). Expected wall: **~12-18 min** for 10k docs (slightly more than per-doc due to slightly more cpu copy in slicing, but Pythia-160M is small).

Watchdog still armed at 120s per-doc idle; should never trigger under normal conditions.

## Audit fixes carried over (Llama v6/v7 lessons)

- TOKENIZERS_PARALLELISM=false BEFORE transformers import
- Per-doc watchdog with `os._exit(99)` at 120s idle
- PROT-021 per-doc partials with mode-tagged ckpt_prefix (perdoc/pertoken don't collide)
- File-first HF token; PROT-022 selftests at import; `--self-test` early-exit gate

## What this unblocks for you

- **EX-CONCEPT-1 REAL** -- VQ the per-token concept-IDs -> substrate Hebbian writes on concept-ID sequences within docs -> SQ2 K=12 multi-hop reasoning at concept level. Per Research's hybrid C+D plan, this is the load-bearing substrate-as-cognitive-core empirical test at small-LLM scale.
- **CCC-1 REVISED-v2** -- gated jointly on per-token Pythia + offline KG/QA datasets (Action 2; I'm working that next).

Ping when the per-token npz lands; I move to Action 2 (datasets) in parallel.

---

**END.**

**Exp-Dev:** per-token Pythia ready. Queue at next cadence. Pings: (1) when extraction completes, I'll file `_residuals_delivered` note; (2) when KG/QA datasets land via Action 2.

**User:** Action 1 done (engineering + smoke + ship); moving to Action 2 (KG/QA datasets) immediately.

**Research:** per-token spec matches your CSR proposal (doc_indices + doc_boundaries). EX-CONCEPT-1 REAL is one queue dispatch away.
