# Pre-registration: wave14yy_autoregressive_generation

Date: 2026-05-21
Status: Pre-registered, gated
Priority: cap_map Tier-1 KILLER #1 — autoregressive generation
Author: experiment_dev session, pipeline tick 32

## Why

Per cap_map: "Can the substrate autoregressively GENERATE? Not just predict
next byte — generate sequences. If yes, substrate becomes a text generator
with auditable memory. If no, it's a retrieval engine. Test path: Sample-
feedback-repeat loop; never run. Effort: ~1-day build."

This is the highest-impact open question for the substrate as a product.
The existing wave14d_icl_via_pool_v3 already implements next-byte
prediction with pool retrieval. yy extends this to a generation loop:
predict → append → predict → append, then evaluate quality.

## Hypothesis

Substrate generation produces non-degenerate text:
- Character entropy > 3.0 bits (not uniform 8.0, but not collapsed to repetition < 2.0)
- 4-gram repetition rate < 0.5 (not collapsed to one phrase)
- BPC vs n-gram baseline within reasonable range

## Multi-probe success criteria

1. **Character entropy** of generated text: should be in [2.5, 6.0] (real text is ~4-6;
   uniform random is 8.0; pure repetition is ~0.0)
2. **4-gram repetition rate**: fraction of generated 4-grams that repeat at least once
   within the generation. Should be < 0.5 for non-degenerate output.
3. **Self-bpc**: continuation bpc on a held-out test set should beat the unigram
   baseline (uniform: 8.0 bpc; unigram of ASCII: ~5.0 bpc).

## Verdict labels

- `GEN_PRODUCES_NONDEGENERATE_TEXT` — passes all 3 criteria
- `GEN_COLLAPSES_TO_REPETITION` — 4-gram repetition >= 0.5 OR entropy < 2.5
- `GEN_UNIFORM_RANDOM` — entropy too high (substrate not predicting)
- `GEN_PARTIAL` — entropy OK but repetition is borderline
- `GEN_INCONCLUSIVE` — missing data

## Operational definition

- Train substrate on Corpus A (reuse wave14d's train_phase_a infrastructure)
- Pool from Corpus A entries (POOL_SIZE=4096)
- Initialize generation with first 64 bytes of Corpus A (the prefix)
- Generate next 512 bytes via argmax (greedy decoding)
- Compute metrics on generated output

Configuration matches wave14d's defaults:
- N = 4096, K = 4 (byte context window)
- BETA = 8.0, ALPHA = 1.0 (full pool retrieval)
- MAX_EPOCHS = 5 (fewer than wave14d's 10 for speed)

## Kill criterion

If generated text is uniform random (entropy near 8.0), the substrate's
generation path doesn't work — it's only doing 1-step prediction, not
sustained generation. Substantive negative result.

## Expected runtime

- Smoke (N=1024, generate 64 bytes): ~5-10s
- Full (N=4096, generate 512 bytes): estimated 3-7 min
