# Testbed -> Exp-Dev: PHASE4A-1 sentence-transformers installed; MiniLM-L6-v2 verified loadable

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** Research + Orchestrator + User  **Date:** 2026-06-05
**Re:** `research_to_exp_dev_phase4a_GO_signal_post_V1_complete_2026-06-05` (16:34) Testbed Ask 1

## PHASE4A-1: DONE

`sentence-transformers 5.5.1` installed in `C:\dev\hd-instrument\.venv\` on marsh@home runner via pip. Smoke verified:

```
sentence-transformers version: 5.5.1
loading sentence-transformers/all-MiniLM-L6-v2 ...
model loaded in 1.7s
  embedding dimension = 384
encoded 3 texts in 0.194s; shape=(3, 384) dtype=float32
cuda available: True
  device: NVIDIA GeForce RTX 4060 Ti
```

MiniLM-L6-v2 (22M params; 384-dim per Research's spec) loads cleanly from HF cache, CUDA-accelerated on the 4060 Ti.

## Encode throughput notes

- 3 short sentences in 0.194s (cold cache, includes startup)
- After warmup, MiniLM on a 4060 Ti typically does 500-2000 sentences/sec depending on batch size + sequence length
- For V_c <= 100k corpus, this is plenty -- 100k abstracts at MAX_TOK_LEN=64 would be ~2-3 min wall

## What this enables (immediate; per Research's GO signal note)

- **Phase 4 work at V_c <= 100k** -- MiniLM is the off-the-shelf drop-in until the distilled 22-26M student is ready (PHASE4A-2; ~$15 cloud)
- Substrate encoder pipeline now has a working 384-dim sentence encoder on the runner without waiting for distillation
- Compatible with existing substrate concept-LM workflows (the 384-dim feature space pairs with substrate at N=4096 via Hadamard projection or random projection patterns we already use)

## Standing items (unchanged)

- **PHASE4A-2 distilled student training** (~$15 cloud H100; ~2-4h wall) -- waits on your handoff training script
- **PHASE4A-6 Wikipedia cache extraction** (~$200-400 cloud H100; ~8-10h overnight) -- Day 6-7 of Phase 4a; not urgent
- **FAISS HNSW env fix** (~$0.50 cloud CPU Linux) -- gates HP-12 V2 1M scale
- **Llama-1B weights local** (optional; gates V2-3 HotpotQA-1B negative rescue + Test 3 live extraction speed)

Standing by for next ask.

## What I did NOT do

- Did NOT install any other Phase 4a deps (e.g., distillation frameworks like KD-PyTorch); waiting for your handoff to know which trainer you'll use
- Did NOT pre-cache any larger sentence-transformer models (e.g., all-mpnet-base-v2 768-dim); only MiniLM-L6-v2 per Research's spec

---

**END.**

**Exp-Dev:** sentence-transformers + MiniLM-L6-v2 ready on the runner. Encode test green (CUDA + 384-dim + ~0.2s for 3 sentences cold). Phase 4a immediate work at V_c <= 100k is unblocked.

**Research:** PHASE4A-1 done in ~10 min (incl. install + verify). PHASE4A-2 + -6 cloud asks queued for when Exp-Dev hands off training script and/or Day 6-7 timing arrives.

**User:** Same pattern as the gmpy2 install -- $0 cost, ~10 min wall, runner-side. Phase 4a now buildable at V_c<=100k scale without waiting for the distilled student.
