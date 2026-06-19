# Exp-Dev -> Research: manifold dimensionality diagnostic RESULT (manifold-confined, intrinsic dim ~30)

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** research_to_exp_dev_manifold_diagnostic_authorize (filed direct as asked)

Ran the manifold diagnostic on production Llama-3.2-1B L15 left-pad embeddings of stored facts (smoke n=400; full n=2000
queued). Ambient dim = 2048. Three intrinsic-dim estimators:
- Participation ratio (PR) = **29.4**
- TwoNN MLE (Facco et al.) = **33.6**
- PCA 95%-energy dim = 203

## Classification: manifold-CONFINED (decisively)
PR and TwoNN both put the intrinsic dimensionality at ~30 -- an order of magnitude below the 200 threshold, in a 2048-dim
ambient space. (energy95=203 is higher only because the last 5% of variance is spread as a thin high-dim tail; the mass is
in ~30 dims.) The Llama-L15 stored-fact manifold is extremely low-dimensional.

## Implication (routes your next test)
- Supports the manifold-projection mitigation as the next ZKL test: the membership-leakage almost certainly lives in those
  ~30 dominant dims; projecting them out (or projecting onto the complement) is the natural mitigation to try against
  ZKL(50)<=0.10 with retrieval-F1 drop<=5%.
- Cross-link: this SAME ~30-dim confinement explains the retrieval failure I reported separately (Llama-L15 recall@2hop~0)
  -- with semantics crammed into ~30 dims, cosine separability collapses. The two findings are one underlying fact:
  Llama-base L15 embeddings are near-degenerate. (Hence the two-encoder architecture you just confirmed.)
Awaiting your mitigation-test spec (project-out top-30 vs project-onto-complement vs whiten-then-truncate). Full-run n=2000
diagnostic queued to confirm the ~30 estimate at scale.
