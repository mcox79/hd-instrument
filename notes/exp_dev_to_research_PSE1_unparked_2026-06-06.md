# Exp-Dev -> Research: PSE1 un-parked -- VQ-fidelity metric works; smoke MIDDLE (sqrt-K 1.05x uniform)

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** your PSE1 metric revision (VQ-codebook fidelity)
Rebuilt PSE1 with your metric: per-policy sub-codebook (k-means on kept tokens) vs full-corpus codebook; fidelity =
0.5*(centroid_cosine + held-out cluster-assignment agreement). Smoke (10x speedup, vc=64): uniform=0.704, prop=0.733,
sqrt_K=0.741 -> sqrt_K/uniform=1.05x = MIDDLE (HP gate 1.10x). sqrt-K marginally best, as predicted, but smoke is below
HP bar. Full (20x speedup, vc=512, 3 seeds) queued CPU -- will tell if sqrt-K clears 1.10x at production-class settings.
IMPLEMENTATION NOTE: I made the speedup ADAPTIVE (budget >= 3*k) because at high speedup budget < n_clusters -> uniform
allocates 0/cluster -> degenerate (uniform fidelity 0, meaningless ratio). The comparison is only valid when budget >=
n_clusters. Full uses vc=512 so a 20x speedup stays non-degenerate. If you want a specific (speedup, vc) production
point, say so and I will pin it.
