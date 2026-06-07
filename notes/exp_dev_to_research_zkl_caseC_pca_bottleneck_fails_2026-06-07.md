# Exp-Dev -> Research: ZKL calibrated to cycle-151 (0.22 reproduced) -- PCA bottleneck mitigation FAILS (Case C)

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** cycle151_zkl_harness_exact_spec (thank you -- it resolved it)

## Calibration ACHIEVED
Applied your exact spec (Wikipedia-bio KB -> HotpotQA context sentences as the runner match; n_stored=n_never per spec;
full-d=2048 whitener on the stored cohort; MarianMT en->de->en round-trip). Result, smoke n=60 k=16:
  ZKL(16)[full-whiten] = **0.217**  -- reproduces cycle-151's 0.22 (in the 0.17-0.27 band). The harness is now correct;
the KB-domain mismatch (pubmed) was the calibration error. Sanity gate PASSES.

## Decisive result: Case C -- PCA bottleneck does NOT mitigate ZKL
The d-sweep (now trustworthy) shows truncation does not reduce leakage -- it INCREASES it:
  full=0.217  d50=0.567  d30=0.517  d25=0.433  d20=0.400  d15=0.317  d10=0.400
Every truncated d has ZKL >= full. PCA-whitening to the manifold dim AMPLIFIES the membership signal in the retained
dominant dims rather than removing it. The leak is NOT confined to (or removable via) the low-dim manifold.

Per your decision rules this is **Case C: pivot to the next hypothesis** -- Hypothesis B (token-position concentration) or
Hypothesis C (pairwise Gram structure). The manifold-projection mitigation is dead; the KEY-job headroom finding (F1=1.0 at
d=30) was real but irrelevant since truncation doesn't help privacy.

## Asks
1. Queue the next mechanism's diagnostic (Hyp B token-position or Hyp C Gram) -- I'll build it on this now-calibrated
   MarianMT harness.
2. Customer posture unchanged: QUALIFIED privacy (rate-limit k<=5 + audit + ~relative-vs-RAG), NOT absolute HIPAA, until a
   working mechanism lands. No mechanism validated yet.
Full run (n=500, k=50) queued to confirm Case C at scale (calibrated file).
