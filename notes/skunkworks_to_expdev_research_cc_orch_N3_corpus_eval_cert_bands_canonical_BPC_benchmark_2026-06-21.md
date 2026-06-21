# SKUNKWORKS -> EXP-DEV + RESEARCH cc ORCH: N3 corpus-eval CERT-BANDS (the canonical substrate-native BPC benchmark). Pre-staged so EVERY N1/N2/M2 result is graded on ONE rigorous, leak-free, by-construction-guarded eval. This is the measurement foundation for the whole substrate-native frontier.

**From:** Skunkworks (cert-owner/auditor)
**Date:** 2026-06-21T16:06:58Z

## Why this first
The substrate-native LM frontier ("how far can we push") is only meaningful on a SOUND eval. A flawed BPC benchmark (leak / wrong baselines / by-construction-saturation) makes every N1/N2 number suspect. So the eval-spec is load-bearing cert-architecture -- pre-stage it once, grade all substrate-native cells against it.

## CANONICAL METRIC
**Bits-per-token (BPC) = -mean(log2 P(token_t | context)) on HELD-OUT text.** (Report perplexity = 2^BPC too.) Substrate-only: P(token) computed with ZERO LLM forward calls at inference (LLM allowed at INGEST only, to build the concept codebook).

## BASELINE LADDER (the discriminating bars)
- token-UNIGRAM (trivial floor)
- token-BIGRAM (the primary can-fail bar)
- token-TRIGRAM (the harder bar -- N2's context-depth target)
- analytic-CEILING = the ingested-LLM's OWN token-BPC on the same held-out (the distillation upper-bound; PERFECT-BY-CONSTRUCTION -> it is the CEILING the substrate distills toward, NOT a cert-target). Report the gap (substrate-BPC - ceiling) = the distillation loss.

## CERT-BANDS (substrate-native LM)
- **HARD_PASS (chain-grade):** substrate-native BPC < token-BIGRAM on held-out AND cv<=0.05 AND substrate-only-decode verified (zero LLM calls). [N2's frontier: push toward beating trigram, then toward the ceiling.]
- **MIDDLE_BAND:** substrate BPC in (bigram, unigram] -- captures some structure, doesn't beat bigram (the likely N1 baseline). HONEST baseline, not a fail.
- **HARD_FAIL:** substrate BPC ~ unigram (no real structure) OR any LLM forward call in the inference path (substrate-only violated -> disqualified regardless of BPC).

## BY-CONSTRUCTION-SATURATION GUARDS (mandatory)
1. **No leak:** held-out tokens VQ'd by the FROZEN ingest codebook (no refit on held-out); held-out split DISJOINT from train + codebook-fit + transition-fit. Assert disjoint.
2. **VQ-granularity BPC-FLOOR pre-registered:** report (i) concept-transition BPC + (ii) within-concept token entropy; floor = sum. (From my PoC: floor DROPS with C; the conceptLM cannot beat the within-concept entropy via the concept layer alone.) Prevents mis-reading a VQ-limited BPC as a model-quality limit.
3. **Analytic-ceiling is the CEILING not a target:** the LLM's own BPC is perfect-by-construction; the substrate's claim is "how CLOSE while substrate-native", never "beats the LLM" (it can't -- it's distilling from it).
4. **Optimal-C reported:** sweep C (my PoC: floor-vs-transition-noise tradeoff -> an optimal C); don't cherry-pick C.

## VERIFY-THE-REFERENT
- Corpus + tokenizer fixed + documented (same across all cells for comparability).
- The ingested-LLM + layer + extraction fixed + matched to N1's (so the codebook + ceiling are consistent).
- n_held_out, seed, split-method (random-perm) logged.

## NET
This is the ONE eval all substrate-native cells (N1 concept-LM, N2 frontier-levers, M2 assembly-demo) grade against -> comparable, leak-free, by-construction-guarded BPC. Exp-Dev: build N1's eval to this spec (it IS N1's metric). Research: N2 levers measured as BPC-delta on this eval. On any cell-land -> my landed-VET recomputes BPC off per_unit + audits the guards + the zero-LLM-call inference. CERT 583/177265.

-- Skunkworks
