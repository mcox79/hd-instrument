# Research note: nonlinear-readout frontier for associative recall over HD/VSA codes

Date: 2026-06-17
Topic: nonlinear readout architectures for content-addressable recall on high-dim distributed reps
Drill type: scope-coverage survey (no recommendations; synthesis is Director's job)

## HEADLINE

The HD/VSA-adjacent literature consensus (caveat: partial) is that softmax-attention / modern-Hopfield is the strongest GENERIC closed-form readout (provably-optimal spherical-code capacity per Hu et al. NeurIPS 2024), but FIVE underexplored families have credible capacity-recovering claims that the current roadmap (linear / softmax-Hopfield / Willshaw) does NOT cover: (1) sparse-Hopfield via entmax/sparsemax (Hu 2023, Santos 2024), (2) random-features Dense AM (Hoover 2024) which decouples parameter count from M, (3) Epanechnikov / compact-support kernel energy (Pham 2025), (4) predictive-coding inference readouts (Salvatori 2021, BayesPCN 2022), and (5) compressed-sensing / OMP / LASSO recovery as a readout. The biggest LITERATURE GAP is that essentially zero published capacity proofs cover structured/compositional codes (bound role-filler products, bundle superpositions) - all assume i.i.d. Gaussian or uniform-on-sphere stored patterns. The "nonlinear readout cures binding crosstalk on VSA codes" question is structurally open.

## Cheap decisive test (per family - 1-day each on small N=1024 grid)

For each candidate family the cheap decisive test is: build a single readout module, evaluate on a SHARED capacity-vs-load curve (M/N from 0.1 to 16), and read off the load at which recall drops below 0.95. Use the same FHRR/HRR substrate, the same stored (key, value) corpus, and the same query distribution. This produces a Pareto frontier (recall@load vs compute) that is directly comparable to the softmax-Hopfield baseline already established. Each family has a distinct cheap-test variant:

- Sparse-Hopfield (entmax-alpha): single hyper-param sweep alpha in {1.0, 1.5, 2.0}; softmax is alpha=1, sparsemax is alpha=2.
- Random-features DAM: sweep feature count D in {N, 2N, 4N, 8N}; capacity should plateau and beat linear at fixed parameter count.
- Epanechnikov compact-support energy: sweep radius r; check finite-basin no-crosstalk-outside-r prediction.
- Predictive-coding readout: small 2-layer PC net; convergence-iters x recall curve.
- OMP/LASSO readout: sweep sparsity k; measure recovery vs linear pseudoinverse at fixed M/N.

## Falsifiable predictions

HARD-PASS thresholds (any of these = the family is load-bearing for the roadmap):
- Sparse-Hopfield (entmax) achieves recall >= 0.95 at M/N >= 8 with strictly lower decoder FLOPs than softmax-Hopfield baseline (literature precedent: Hu 2023 closed-form tighter bound under sparse-pattern regimes).
- Random-features DAM achieves recall >= 0.90 at M/N >= 4 with FIXED parameter count <= 4N (literature: Hoover 2024).
- Epanechnikov readout achieves recall >= 0.95 at M/N >= 2 AND demonstrates ZERO crosstalk to queries outside r (a property softmax does not have; literature: Pham 2025).
- Predictive-coding readout achieves recall >= 0.90 at M/N >= 4 (literature: BayesPCN Yoo 2022 reports hundreds of >10k-D patterns continually).
- OMP / LASSO readout recovers k-sparse stored items from O(k log N) measurements where linear pseudoinverse fails (literature: standard CS).

HARD-FAIL thresholds (any of these = the family is dead for this substrate):
- Recall < 0.50 at M/N = 2 (the regime where softmax-Hopfield is already 1.0).
- Decoder compute > 10x softmax-Hopfield at equal recall (cost-prohibitive).
- Capacity advantage disappears under FHRR-bipolar / sparse-block patterns (i.e. the family only works on i.i.d. Gaussian and breaks under structured HD codes - this is the dominant literature blind-spot).

P estimates (deflated per lit-scan calibration penalty):
- Sparse-Hopfield entmax beats softmax under sparse-pattern regime: P_deflated = 0.45 (lit precedent solid; substrate-novel: untested on VSA codes)
- Random-features DAM beats softmax at fixed param: P_deflated = 0.35 (Hoover 2024 untested on bound HD codes)
- Epanechnikov compact-support beats softmax on crosstalk metric: P_deflated = 0.40
- Predictive-coding readout beats softmax: P_deflated = 0.30 (PC adds iterative cost; recall claims are continual-learning regime, not pure capacity)
- OMP/LASSO beats softmax at low M: P_deflated = 0.25 (cheap to test; likely too sparse-assumption-dependent)
- Novel-synthesis cap on any composed family (e.g. sparse-Hopfield + kNN external memory): 0.50

## Cross-thread synthesis

The four sub-agent scans converged on a CONSISTENT taxonomy. Mapping to roadmap-in-scope:

| Family | In current roadmap? | Literature status | Capacity scaling | Compute |
|---|---|---|---|---|
| Linear / Hebbian | YES (baseline) | strict ceiling at ~0.14 N (classical) | linear in N | O(MN) |
| Softmax / modern Hopfield (Ramsauer) | YES (load-bearing) | provably exp(N/2) capacity, optimal spherical code | exp(N/2) | O(MN) |
| Willshaw / thresholded | YES (redundant) | divergent at low activity | exp at low activity | O(MN) |
| **Sparse Hopfield (entmax/sparsemax)** | **NO** | Hu 2023 tighter bound | same order, better constants | O(kN), k<<M |
| **Random-features DAM** | **NO** | Hoover 2024 NeurIPS | independent of M | O(DN), D fixed |
| **Epanechnikov / compact-support kernel** | **NO** | Pham 2025 | finite-basin no-crosstalk | O(MN) |
| **Polynomial-energy DAM (Krotov-Hopfield)** | partial (softmax is exp-energy special case) | N^(p-1) capacity | as p grows | O(MN^p) naive |
| **kNN / external memory** | **NO** | Wu 2022, exact-recall episodic | Theta(M) cache | O(N log M) |
| **Predictive-coding inference** | **NO** | Salvatori 2021, BayesPCN 2022 | continual-learning regime | O(layers x N) per step |
| **OMP / LASSO / compressed-sensing** | **NO** | classical CS | O(k log N) measurements | O(kNd) |
| **FlyHash / k-WTA / sparse expansion** | partial (Drosophila already cited) | Dasgupta 2017 | sparsity-dependent | O(N) |
| **Hopfield-Fenchel-Young (entropy-parameterized)** | **NO** | Santos 2024 unification | family-wide | varies |
| **Diffusion-as-memory / score-based** | **NO** | Biroli 2025, Hoover 2023 | matches DAM asymptotically | T steps x score-net |
| **GP / kernel-ridge regression** | **NO** | classical, O(N^3) inverse | rank-limited by Gram | O(N^3) train |
| **Linear attention (Performer, RWKV, Mamba)** | **NO** | NEGATIVE: collapses on MQAR | "less mem = worse recall" law | O(N) recurrence |

The CONSENSUS finding across all four scans: softmax / exp-energy is the strongest CLOSED-FORM generic family (Demircigil 2017, Ramsauer 2020, Hu NeurIPS 2024). The DIVERGENCE across scans: sparse-Hopfield (entmax) and random-features DAM both have credible "match-or-beat softmax at lower cost" claims that no out-of-roadmap family else has.

The MQAR (multi-query associative recall) benchmark literature (Arora et al. Zoology) provides a community-standard task surface where these families have been directly compared - linear attention / SSMs collapse, softmax holds, sparse-attention sometimes wins on long-context generalization (AdaSplash 2025).

The lit gap most relevant to the substrate: no published capacity proof covers STRUCTURED / compositional HD codes (role-filler binds, bound bundle superpositions). All known proofs assume i.i.d. Gaussian or uniform-on-sphere patterns. The "does nonlinear readout cure binding crosstalk" question is structurally open. This is a genuine novel-direction angle.

## Substrate-product implications

This survey is informational - synthesis is Director's job. Three observations relevant to product:

1. The current roadmap (linear / softmax / Willshaw) covers the GENERIC strongest family but MISSES at least five additional families with published capacity-recovering claims. A complete capacity-ceiling map of the substrate's readout layer needs each family pre-registered with a cheap-test variant.

2. The random-features DAM family (Hoover NeurIPS 2024) is particularly product-relevant: it DECOUPLES parameter count from stored pattern count M. For a substrate that wants growth without weight-explosion, this is structurally important.

3. The literature blind-spot on STRUCTURED HD codes (no capacity proof on bound role-filler products) means published capacity numbers are upper-bounds-under-i.i.d.; substrate empirical numbers on structured codes are NOT directly comparable to published theory. This is an audit-discipline note: when citing "exponential capacity" from Ramsauer 2020 do not transfer the claim to a bound-bundle workload without explicit re-measurement.

## Citations (verified count: 30 distinct sources across 4 sub-scans)

Modern Hopfield family:
- Ramsauer et al. "Hopfield Networks is All You Need" (2020) - https://arxiv.org/abs/2008.02217
- Krotov & Hopfield "Dense Associative Memory" (2016) - https://arxiv.org/abs/1606.01164
- Demircigil et al. (2017) - https://arxiv.org/abs/1702.01929
- Millidge et al. "Universal Hopfield Networks" (2022) - https://arxiv.org/abs/2202.04557
- Santos et al. "Hopfield-Fenchel-Young Networks" (2024) - https://arxiv.org/abs/2411.08590
- Hu et al. "Sparse Modern Hopfield Model" NeurIPS 2023 - https://arxiv.org/abs/2309.12673
- Santos et al. "Sparse and Structured Hopfield Networks" (2024) - https://arxiv.org/abs/2402.13725
- Krotov "Hierarchical Associative Memory" (2021) - https://arxiv.org/abs/2107.06446
- Hoover et al. "Energy Transformer" NeurIPS 2023 - https://arxiv.org/abs/2302.07253
- Saha et al. "Differentiable Clustering with AM" ICML 2023 - https://arxiv.org/abs/2306.03209
- Hu et al. "Provably Optimal Capacity" NeurIPS 2024 - https://arxiv.org/abs/2410.23126
- Hoover et al. "DAM through Random Features" NeurIPS 2024 - https://arxiv.org/abs/2410.24153
- Wu et al. "U-Hop Uniform Memory Retrieval" (2024) - https://arxiv.org/abs/2404.03827
- Pham et al. "DAM with Epanechnikov Energy" (2025) - https://arxiv.org/abs/2506.10801
- Krotov et al. "Modern Methods in Associative Memory" (2025) - https://arxiv.org/abs/2507.06211
- ICLR 2025 New Frontiers in Associative Memory - https://openreview.net/group?id=ICLR.cc/2025/Workshop/AM

Attention-based readouts:
- Wu et al. "Memorizing Transformers" ICLR 2022 - https://arxiv.org/abs/2203.08913
- Goncalves et al. "AdaSplash" ICML 2025 - https://arxiv.org/abs/2502.12082
- "Long-Context Generalization with Sparse Attention" - https://arxiv.org/abs/2506.16640
- Arora et al. "BASED" 2024 - https://arxiv.org/abs/2402.18668
- Cabannes et al. "Factual Recall via Associative Memories" 2024 - https://arxiv.org/abs/2412.06538
- Zoology / MQAR benchmark - https://github.com/HazyResearch/zoology

Kernel / energy / RBF:
- Nowicki & Siegelmann "Flexible Kernel Memory" (2010) - https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2883999/
- "Adaptive Hopfield Network" (2025) - https://arxiv.org/abs/2511.20609
- "Effects of Feature Correlations on AM Capacity" (2025) - https://arxiv.org/abs/2508.01395
- Biroli et al. "Memorization to Generalization: Diffusion from AM" (2025) - https://arxiv.org/abs/2505.21777
- Hoover et al. "Memory in Plain Sight" (2023) - https://arxiv.org/abs/2309.16750
- Ambrogioni "In Search of Dispersed Memories" (2024) - https://www.mdpi.com/1099-4300/26/5/381

Sparse coding / WTA / PC / CS:
- Palm "Neural associative memories and sparse coding" (2013) - https://www.mit.edu/~9.54/fall14/Classes/class07/Palm.pdf
- Dasgupta et al. "FlyHash" Science 2017 - https://www.researchgate.net/publication/320967614
- Ryali et al. "BioHash" ICML 2020 - http://proceedings.mlr.press/v119/ryali20a/ryali20a.pdf
- Salvatori et al. "AM via Predictive Coding" NeurIPS 2021 - https://arxiv.org/abs/2109.08063
- Yoo et al. "BayesPCN" (2022) - https://arxiv.org/abs/2205.09930
- Karbasi et al. "Noise Facilitation in AM" (2014) - https://arxiv.org/abs/1403.3305
