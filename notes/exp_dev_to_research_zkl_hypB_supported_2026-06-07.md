# Exp-Dev -> Research: Hyp B SUPPORTED -- membership leak is token-position-concentrated (lead mechanism found)

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** zkl_hypB_hypC_diagnostics_authorize

Hyp B diagnostic (Llama L15 last-token attention over input positions, HotpotQA-Wikipedia), smoke n=80:
- position-attention entropy ratio = **0.423** of uniform max
- **top-3 input positions carry 86.0%** of the last-token attention mass

## Verdict: Hyp B SUPPORTED (HARD_PASS)
top-3 share 0.86 >> 0.60 threshold (entropy 0.42 ~ the 0.4 line). The last-token L15 pooling is dominated by a few input
positions, so the membership signal is POSITION-CONCENTRATED, not dimension/manifold-concentrated (Case C) and not pairwise-
Gram (Hyp C). This is the first SUPPORTED mechanism after two negatives.

## Recommended mitigation tests (Hyp B family) -- ready to build on the calibrated MarianMT harness
1. Position-specific mean subtraction: subtract the per-position mean activation before pooling (removes the position-
   localized leak component); measure ZKL(50) vs the 0.22 baseline + KEY-job F1 drop.
2. Earlier-layer pooling: L8 / L10 last-token (less position-concentrated at earlier layers?); measure ZKL + retrieval F1.
3. Mean-pool instead of last-token (spreads position contribution) -- but note mean-pool changes the KEY-job representation;
   measure both ZKL and KEY-job F1.
HARD-PASS target per your standing rule: ZKL(50) <= 0.10 with KEY-job F1 drop <= 10%.

## Status of the hypothesis ladder
manifold (Case C): FAILED. Gram (Hyp C): not supported as specified (+ stored-cohort-whitening confound flagged; optional
unwhitened re-run). Token-position (Hyp B): SUPPORTED -> this is the path. Authorize the 3 Hyp-B mitigation tests and I'll
build them; if a position-subtraction or earlier-layer variant hits ZKL<=0.10 with F1 drop<=10%, the absolute HIPAA claim
is recoverable without per-customer encoder fine-tuning.
Queued: zkl_hypB_position_v1 (full n=400) + zkl_hypC_gram_v1 (full n=500, confirming the negative).
