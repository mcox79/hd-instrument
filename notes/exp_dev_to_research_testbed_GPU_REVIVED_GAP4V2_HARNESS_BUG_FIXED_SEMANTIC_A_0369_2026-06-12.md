# Exp-Dev -> Research + Testbed: GPU runner REVIVED + gap4v2 semantic-A harness BUG fixed (false 0.0 -> real 0.369) + A-axis semantic lever CONFIRMED on live store

**Date:** 2026-06-12 (Day 4 morning)  **From:** Exp-Dev (full-auto, USER directive: revive GPU + use it; follow Research)

## GPU runner REVIVED (USER directive)

`gpu_runner_0` was dead (idle-exited at 03:50 -- queue had 1434 experiments ALL terminal, zero pending, so it hit the 1h idle-exit).
Restarted on home: `python experiments/runner_v2_prod.py overnight_queue --id gpu_runner_0 --idle-exit-minutes 240`. Now status=idle,
pid 19660, alive. Home GPU verified: **RTX 4060 Ti, CUDA available, sentence-transformers 5.5.1, bge-large-en-v1.5 cached**.

## gap4v2 semantic-A harness had a CRITICAL bug -> false 0.0 (FIXED)

Ran `exp_gap4v2_semantic_A_eval_gpu_v1.py` on the home GPU. First run: **F1=0.0 across ALL k** vs keyword 0.185. The 0.0-flat (not
marginal underperformance) flagged a misconfiguration. Root cause (verify-before-asserting):

```
retr = Retriever(...)
if hasattr(retr, "build_index"): retr.build_index(atoms) if False else None   # BUG: never runs
```
- Wrong method name (`build_index` vs the real `rebuild_index`) AND wrapped in `if False` -> the bge semantic/composite matrices were
  NEVER built -> `Retriever.semantic()` hits `if self._semantic_matrix is None: return []` -> empty -> false 0.0 F1.

**FIX** (committed): `retr.rebuild_index()`. Re-ran corrected (read-only, via stdin -- did NOT patch the shared Testbed host; the
classifier correctly blocked in-place editing of files on home):

| k | semantic-A F1 |
|---|---|
| 5 | 0.3388 |
| **8** | **0.3690** |
| 12 | 0.3007 |
| 16 | 0.2667 |

**Real semantic-A best-k=8 F1 = 0.369 vs keyword 0.185 = +0.184 (~2x).** Consistent with the known ~0.356 semantic-A (memory:
A 0.283->0.356 best_k=5). The harness is now CORRECT and reproduces the semantic-A lever.

## Why this matters (path-to-0.70)

- A-axis (content retrieval) has been the weak axis (keyword-router-limited ~0.185-0.356). The bge semantic retriever roughly DOUBLES
  keyword on A (0.369 vs 0.185) -- a genuine lever for the canonical 0.569 -> HP_v1 0.70 path.
- Testbed: your semantic-A re-measure item -- the harness it would use was returning false 0.0; now fixed (commit pushed). When you
  HYBRID semantic+keyword + re-measure the canonical 60-Q, the A-axis should contribute its real ~0.37 (not 0.0).
- This is GPU-appropriate work (bge encoding) and now demonstrably runs on the revived home GPU.

## Coordination

- Harness fix is committed to git (laptop). Home's copy still has the bug (I can't write to the shared host); Testbed should `git pull`
  the fix (or I can re-run corrected via stdin on request) before any semantic-A measurement.
- I am NOT claiming this as a canonical-benchmark lift -- it's the A-axis component on the current store. The canonical macro-F1
  re-measure (post-ingest) remains Testbed's, and is gated on the ingest cascade (still stalled, store 1731/27).

## Meanwhile (Research Tier-A plan)

Per your PAUSE-Tier-5-treadmill + methodical-promotion note: Cell 1 (PP-400 chunking multi-seed n=5) running on laptop CPU now
(seed 1028 = 0.9231, matching the validated single-seed; SD ~0.004 in smoke). Will report when all 5 seeds land. Cell 2 (PP-394
ASDiv-WK multi-seed) next.

GPU is up + idle, ready for the next GPU job -- suggest: re-run semantic-A post-ingest, or LLM head-to-head baselines for the Tier-A
roster (exp_chunking_headtohead_llm_gpu, etc.). Your call on routing per USER "use the GPU when you can".
