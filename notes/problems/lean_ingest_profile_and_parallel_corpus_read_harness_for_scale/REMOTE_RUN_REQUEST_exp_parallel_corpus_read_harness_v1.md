---
cell: experiments/exp_parallel_corpus_read_harness_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 3600
results_path: data/exp_parallel_corpus_read_harness_v1/metrics_full.json
self_test: green
question: does the process-parallel corpus-read harness scale near-linearly on the IDLE remote box's cores (a clean curve the shared local laptop cannot give)?
gate: per-doc output byte-identical serial-vs-parallel across the worker grid AND throughput scales with worker count; report the curve + the box's own CPU-bound ceiling + 10k-doc projection
kb_referents:
  - data/litbank/coref/conll
  - data/frontend_assets/pos_tagger_ud_ewt_upos.json
  - data/frontend_assets/arc_parser_hashed_ud_ewt.npz
---

WHY REMOTE (owner-suggested): the local box is a SHARED 12-physical-core Intel hybrid (P/E cores + hyperthreading),
so its scaling curve is noisy (serial varied 39-68 s/40-doc between runs) and capped (~4.5x at 8 workers even for
ideal CPU work). An IDLE box gives the clean curve, and a Linux box uses `fork` (copy-on-write) so the parser/tagger
model is shared read-only across workers instead of copied per worker (Windows spawn) -- which should close most of
the ~32% gap to the hardware ceiling we measured locally.

NOTE (GPU vs CPU): this parallelism is CPU-bound (pure-Python parser/tagger; the GIL forces PROCESSES, not threads).
The GPU is NOT used and will not help. Route to `remote_cpu_queue`. The value of the remote box here is its idle,
homogeneous (or at least uncontended) CPU cores.

WHAT THE CELL REPORTS:
- The remote box's own pure-CPU process-scaling ceiling (asset-free busy-loop) -- run FIRST, so even if a reader
  asset is missing on the remote the hardware headroom is still returned (the reader section is guarded).
- The selpref-profile ingest scaling: per-doc BYTE-IDENTICAL serial-vs-parallel (canonicalized digests), throughput
  vs worker count (grid = powers of two up to the remote's PHYSICAL-core count, plus the core count), the fraction
  of the box ceiling achieved, and a 10k-doc projection.

REMOTE-SAFETY: no module-level spaCy/torch; selpref does not invoke spaCy (causation_typed / spacy_pred_gate are
off). `--self-test` is now FAST + ASSET-FREE (~20s: canonicalization order-invariance + a spawn-Pool sanity check;
it does NOT run the full reader, so it clears the 300s guardrail on a cold box -- the earlier dispatch was rejected
because the old self-test cold-paid ~190s of frame-induction training per worker). The real parallel==serial
identity is proven by the guarded FULL run + the local witness. Bare invocation runs FULL (no --mode needed).
Deterministic; the one hash-order-dependent field (sm.entities) is canonicalized before hashing, so the identity
check holds across worker processes regardless of PYTHONHASHSEED.

HARDENING SINCE THE FIRST DISPATCH (2026-09-05): (1) FORK-preferring on Linux -- the parent loads the model once and
workers inherit it copy-on-write (no per-worker model copy/RAM), which should close most of the ~32% gap to the
hardware ceiling seen locally on Windows/spawn; (2) the CPU-ceiling probe runs FIRST and the reader section is
guarded, so a missing asset still returns the box's parallel headroom; (3) PYTHONHASHSEED pinned across parent+
workers; (4) fast asset-free self-test (clears the 300s guardrail). NOTE for interpretation: under the intended
regime (workers <= physical cores, threads=1) the reader is byte-reproducible; if the remote box is OVERSUBSCRIBED,
the affect/subj_role metadata organs can show rare borderline label flips (a located hdlab float-repro sensitivity)
-- the per-worker `identical_to_serial` flags will reveal it if so.

This is verdict-INDEPENDENT validation of the scaling claim; the SOLVED deliverable stands without it (byte-identity
+ local ceiling-relative scaling are already proven). It just confirms near-linear scaling on cleaner hardware.
