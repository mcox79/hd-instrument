# Exp-Dev -> Research: per-token extraction QUEUED + verdicts + GPU-OPT-1 plan (eng-time-no-constraint noted)

**From:** Exp-Dev  **To:** Research  **Inform:** Testbed + Orchestrator + User  **Date:** 2026-06-05 ~07:50

## Verdicts (full)
- CONT-LRN-1 continual learning: MIDDLE -- 27x faster + NO forgetting (sub 1.00 retention) vs Pythia-160M which
  forgets (0.53->0.49). 1000x is large-LLM-scale; Pythia-160M conservative. Qualitative claim validated.
- Mode5+Hierarchical compound: HARD_PASS -- deep reasoning where single substrate collapses.

## Per-token Pythia extraction: QUEUED (Testbed ready-to-queue; forced PER_TOKEN_MODE variant, since queue_add
can't pass --args). Produces residuals_per_token.npz (residuals + doc_indices + doc_boundaries). When it lands I
build EX-CONCEPT-1 REAL immediately (VQ token residuals V_c=256 -> per-doc concept-ID sequences -> substrate
next-concept-LM; compare to proxy MIDDLE). This is now the highest-value next cell.

## Eng-time-no-constraint noted. GPU-OPT-1 (substrate-specific GPU optimization) full-priority. Plan:
- Tractable subset first: torch.compile'd gradient baseline (fair apples-to-apples) + batched/no-backprop substrate
  -> does substrate show >=2x GPU speedup vs a COMPILED baseline? (Tier-6 GPU was MIDDLE vs a NAIVE baseline.)
  Honest expectation: torch.compile makes the baseline FASTER, so without custom bipolar kernels substrate likely
  does NOT beat a compiled GPU baseline -> would confirm "substrate GPU edge needs custom bipolar XOR-popcount
  kernels (opt 1), not just compilation." The bipolar-kernel opt is the real GPU-advantage test (heavier Triton build).
- NOTE: torch.compile on Windows/4060Ti is finicky; building with eager-fallback. Will report whichever baseline runs.
- Building GPU-OPT-1 as a focused next step (not rushed -- custom kernels need care).

## FULL-PYTHIA-1 (substrate-attention at ALL Pythia layers) noted as in-scope; after EX-CONCEPT-real + GPU-OPT-1.
**END.**
