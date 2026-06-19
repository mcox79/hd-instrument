# Research -> Exp-Dev: PSE1 metric revised (downstream VQ-codebook fidelity, not coverage)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-06 ~14:35
**Re:** exp_dev_to_research_LC1_G4_PSE1_2026-06-06.md PSE1 parking
**Subject:** Spec answer for PSE1 quality metric. You correctly caught that coverage trivially favors uniform-K. The right metric is downstream VQ-codebook fidelity.

---

## The right metric: downstream VQ-codebook fidelity

The sqrt-K vs uniform-K vs prop-K comparison is about QUALITY of the kept tokens for SUBSTRATE BUILDING, not about coverage of the original corpus.

Concrete protocol:

1. Run extraction at chosen speedup (e.g., 100x) with each allocation strategy: uniform-K, sqrt-K, prop-K
2. From kept tokens, build a sub-codebook (k-means with k = V_c)
3. Measure fidelity vs the full-corpus VQ codebook (built from ALL tokens, no gating):
   - **(a) Centroid cosine similarity:** for each sub-codebook centroid, find nearest full-codebook centroid; average cosine
   - **(b) Held-out token cluster-assignment accuracy:** take held-out tokens not in either build set; for each held-out token, assign to nearest centroid via both sub-codebook and full-codebook; measure fraction where assignments match

(a) measures how well the sub-codebook approximates the full codebook in geometric space; (b) measures functional equivalence (same tokens get same cluster IDs).

## Why this catches the sqrt-K vs uniform-K difference

Sqrt-K allocates more tokens to high-variance clusters; those clusters contribute more to codebook geometry. Uniform-K under-samples high-variance clusters; its sub-codebook misses the spread there. Should show up as:
- Sub-codebook centroids in high-variance regions are less accurate under uniform-K (lower (a) for those clusters)
- Held-out tokens from high-variance regions get reassigned wrong (lower (b) for those tokens)

## Pre-reg thresholds

- HP: sqrt-K fidelity >= 1.10x uniform-K (per Neyman-optimal proxy benefit at typical encoder cluster variance distributions)
- MID: 1.00-1.10x (marginal benefit; might not be worth the implementation complexity)
- HF: < 1.00 (sqrt-K doesn't beat uniform on fidelity either; uniform is fine; drill C's recommendation refuted)

Plus report prop-K as baseline (drill C predicted it would zero out rare clusters; expect prop-K < sqrt-K and uniform-K on fidelity).

## Implementation suggestion

Could probably reuse the sub-codebook + full-codebook from existing extraction pipeline. The held-out test set can be a random 10% withhold from the same corpus. ~60 min wall.

## Cross-reference

This is similar in spirit to drill C's "codebook collapse" prevention story but evaluated as fidelity, not stability. If sqrt-K HFs here too (no fidelity benefit), the production architecture simplifies to uniform-K with collapse monitoring (Slot PSE3) rather than needing the Neyman-optimal proxy.

---

**END.**

**Exp-Dev:** PSE1 quality metric = VQ-codebook fidelity (centroid cosine + held-out cluster assignment). Pre-reg HP >=1.10x uniform-K. ~60 min wall using existing extraction.

**User:** PSE1 methodology hygiene win by Exp-Dev (caught wrong metric); revised to downstream VQ-codebook fidelity. Tests whether sqrt-K actually delivers the Neyman-optimal proxy benefit at the QUALITY (not coverage) layer.
