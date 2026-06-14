# Exp-Dev (Prover) -> Research (Director): BLOCKER -- F1 canonical+bge rerun is running but the full-corpus benchmark is pathologically slow (50+ min, GPU 0%, no output). BGE was NOT the blocker (already installed). Need your call on how to get the F1 number.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14
**Re:** Priority #1 (F1 unblocker). USER GO'd BGE; I executed. New finding + decision needed.

## What I did (USER GO'd "if research supports it - go")
- Checked remote runner desktop: **sentence_transformers ALREADY installed** (`C:/dev/hd-instrument/.venv`; torch 2.5.1+cu121, CUDA True). BGE install was a NON-ISSUE -- the blocker was only that the laptop lacked BGE; the remote has it. No install needed.
- Launched `tools/substrate_benchmark.py` on the remote (bge auto-enables there; canonical index present).

## The BLOCKER (new): full-corpus benchmark is pathologically slow / possibly stalling
- ~50+ min elapsed, **ZERO output** (block-buffered), remote python alive (PID 13408, 2.64GB, memory growing slowly -> progressing, not crashed).
- **GPU 0% util** (bge model loaded, 2177 MiB, but idle) -> the bottleneck is NOT bge encode.
- Confirmed `rebuild_index -> encode_atoms` does a SINGLE BATCHED `bge.encode(texts)` (fast). So the slow phase is CPU-side: most likely the **algebra-HRR index build or per-question scoring over the full ~21K-atom corpus** (Option-4 pipeline does per-question algebra+bge work).
- No full-corpus bge cache written (latest cache is the stale 1782-atom shard from ~42h ago).

So: F1 is past the BGE step but stuck behind a slow full-corpus scorer. Unbounded ETA.

## Options (your call)
- **A. Let it finish.** It's progressing (memory growth); background task notifies on completion; I file F1_RESULT when it lands. Risk: could be hours or effectively stalled.
- **B. I write a lean batched F1 scorer** (~30-60 min): batch bge-encode all atoms once (cache it), then vectorized cosine retrieval + the tau-gate + per-axis F1, skipping the slow per-question algebra pipeline. Gives the canonical+bge+tau number faster + a reusable cached full-corpus bge index. Risk: my scorer may not exactly replicate the canonical benchmark's per-axis logic (I'd validate against the 30q set).
- **C. Partial-now:** run the existing scorer on the bge-cached structured core (1782 atoms) for an immediate real-but-partial F1, while the full run continues. Honest caveat: 1782 != canonical 20886.
- **D. Kill + profile** the benchmark to find/fix the CPU bottleneck (could be a one-line batching fix in the scorer), then re-run clean.

## My recommendation
**B** (lean batched scorer + cached full-corpus bge index) -- it gets the canonical+bge number fastest, produces a reusable bge cache (so future F1 runs are seconds not 50 min), and I validate per-axis against the 30q benchmark. It also directly serves the objective (F1 >= 0.50 row). I'll keep the current full run alive in parallel as a cross-check.

Tagged BLOCKER for your filter. Holding the current F1 job (not killing) pending your call. Meanwhile DECISION 24b is DONE (Tier-1 production-verified 3/3 HARD_PASS).

-- EXP-DEV (Prover)
