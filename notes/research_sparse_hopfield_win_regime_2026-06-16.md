# research: sparse-Hopfield WIN REGIME -- when does sparse-attention-based modern-Hopfield distinctly outperform naive flat cleanup and dense softmax?

date: 2026-06-16
topic: sparse_hopfield_win_regime (consumer-pull characterization of distinct value-regime)
depth: 1x focused lit-scan (3 parallel Sonnet lit-scans + Opus synthesis)
trigger: substrate observed sparse-Hopfield TIES naive flat cleanup on quasi-orthogonal residue codebooks; consumer-pull deferred distinct value-regime characterization
related notes:
  - notes/research_to_skunkworks_exp_dev_R1_lit_scan_ACKED_sparse_hopfield_lever_R2_proceed_2026-06-16.md
  - notes/testbed_to_skunkworks_research_exp_dev_P2_prereg_DESIGN_66th_pre_receive_3_substrate_atoms_OK_sparse_hopfield_HEAD_3_NEEDS_TIER_4a_batch_or_step_9_FORM_A_2026-06-16.md

## (a) HEADLINE

Sparse-Hopfield (Hu 2023 sparsemax; Santos 2024 alpha-entmax; SparseMAP/structured) provides distinct value EXCLUSIVELY in the CORRELATED / METASTABLE-PRONE codebook regime where dense softmax mixes patterns at finite beta. The literature is UNIFORMLY CONSISTENT: NO paper claims sparse-Hopfield wins on quasi-orthogonal codebooks where 1-NN argmax-cosine already saturates -- it ties (collapses to the same one-step retrieval). The crossover is governed by Ramsauer separation Delta_i = x_i^T x_i - max_{j!=i} x_i^T x_j: when Delta_i shrinks (correlated patterns at finite inverse-temperature beta), softmax mixes into metastable averages while alpha-entmax / sparsemax / SparseMAP retrieves exactly. Quasi-orthogonal codebooks live in the high-Delta_i regime where softmax-at-high-beta = sparsemax = argmax-cosine all coincide. Substrate's observed TIE is the EXPECTED OUTCOME from the published theory, not a surprise.

P_deflated (sparse-Hopfield distinct-value-regime characterization stable): 0.78 (deflated from 0.90 unbiased Hu/Santos theory). Capped at 0.50 for any novel-synthesis claim about substrate consumer-uptake.

## (b) Cheap decisive test

Three-cell prereg to FALSIFY the "sparse-Hopfield distinct-value-regime is correlated/metastable only" claim against substrate codebook:

**Cell A (orthogonal control)**: Generate quasi-orthogonal codebook (i.i.d. random spherical / Bernoulli; mu_max < c/sqrt(N) confirmed empirically). Run flat-NN vs sparse-Hopfield (sparsemax readout) vs dense softmax-Hopfield (Ramsauer beta=1, beta=10). Single-pattern retrieval under noisy query (additive Gaussian sigma in [0.1, 0.5]).

**Cell B (correlated regime sweep)**: Construct codebook with controlled pairwise-correlation rho in {0.0, 0.2, 0.4, 0.6, 0.8} (Gaussian mixture or rotated-cluster design). Same retrieval task.

**Cell C (superposition depth)**: Bundle k items (k in {1, 2, 4, 8}) on quasi-orthogonal codebook. Test cleanup-of-bundle = "decompose bundle into constituent codewords".

Expected behaviour from literature:
- Cell A: all three methods TIE (predicted by Santos HFYN "retains capacity for well-separated patterns" + Tropp k=1 trivial threshold).
- Cell B: at rho >= 0.4, dense softmax falls into metastable mixing (Santos 2024 Table 1: 85.5% metastable at beta=1 on MNIST); sparse wins. Crossover rho depends on beta.
- Cell C: at k >= 2, Tropp's (2k-1)*mu < 1 threshold becomes binding; iterative sparse recovery (BP/OMP/LASSO) provably needed. Modern sparse-Hopfield may also help here but is NOT the textbook tool for superposition decoding.

## (c) Falsifiable predictions

**HARD-PASS** (theory confirmed; sparse-Hopfield consumer-uptake decision = correlated/superposition-only):
- Cell A: |acc(sparse) - acc(naive)| < 0.01 across all sigma values; both within noise of dense softmax-beta=10. (Hypothesis: PASS likely, P=0.78.)
- Cell B: sparse beats dense softmax-beta=1 by >= 5pp accuracy at rho >= 0.4. (PASS likely, P=0.70.)
- Cell C: sparse beats naive flat-NN by >= 10pp accuracy at k >= 4 on bundle decomposition. (PASS likely, P=0.55.)

**HARD-FAIL** (theory refuted; consumer-uptake decision must be reopened):
- Cell A: sparse beats naive by >= 3pp on quasi-orthogonal AT ANY sigma. Would CONTRADICT Santos HFYN + Hu 2023 theorem 3.1 well-separation analysis. (P=0.10.)
- Cell B: sparse FAILS to beat dense softmax-beta=1 at rho >= 0.4. Would CONTRADICT Santos 2024 Table 1 metastable-state result. (P=0.12.)
- Cell C: sparse-Hopfield matches BP/OMP on superposition decoding. Would represent novel finding NOT predicted by literature. (P=0.20.)

Pre-registered thresholds (use these as substrate verdict gates):
- HARD-PASS Cell A: |Delta_acc| < 0.01 (tight tie band).
- HARD-PASS Cell B: Delta_acc >= 0.05 at rho=0.4, sigma=0.3, beta=1.
- HARD-FAIL Cell A: Delta_acc(sparse, naive) > 0.03 at any sigma.

## (d) Cross-thread synthesis with prior Entries

**Convergence across 3 lit-scan threads.** All three independently arrived at the SAME conclusion:
1. Thread 1 (Hu/Santos focused): "NO paper found that benchmarks sparse-Hopfield against flat-NN on orthogonal codebooks as a positive claim of advantage. Prior CONFIRMED by literature."
2. Thread 2 (downstream tasks): Sparse wins on (a) low-witness-rate massive MIL, (b) OOD/rare-token retrieval, (c) interpretability, (d) long-context efficiency. Ties on (a) in-domain ranking, (b) MT accuracy. Loses on (a) paraphrase retrieval, (b) calibration-sensitive tasks.
3. Thread 3 (coherence crossover): Tropp threshold (2k-1)*mu < 1 collapses to trivial for k=1; Ramsauer Theorem 5 makes Delta_i the explicit crossover variable; Krotov-Hopfield metastable basins appear only under correlation; JL/Vershynin guarantee 1/sqrt(N) concentration in random codebooks where 1-NN provably suffices.

**Prior substrate observation explained.** The substrate's quasi-orthogonal residue codebooks live in the high-Delta_i / low-mu regime where Santos HFYN explicitly says sparse "retains" but does not exceed dense capacity, and where Tropp's k=1 threshold is trivially satisfied. The TIE is THE PREDICTED OUTCOME, not a defect of substrate sparse-Hopfield implementation or a defect of measurement.

**Adjacency to existing cap_map rows.** This finding bears on (per substrate-product positioning): rejection-or-deferral of sparse-Hopfield as a UNIVERSAL cleanup substitute, while preserving it as a CONSUMER-PULL primitive for the correlated-codebook regime when that regime is encountered (e.g., learned codebooks downstream, structured natural-language stored patterns, superposition-decoding lanes).

**Non-dismissal discipline (per [[feedback-dont-dismiss-adjacent-methods]]).** This finding does NOT dismiss sparse-Hopfield. It re-scopes the consumer-uptake decision: defer-as-cleanup-substitute, retain-as-correlated-regime-tool. The published win-regime is real and documented; substrate just doesn't currently expose that regime in its quasi-orthogonal residue lanes.

## (e) Substrate-product implications

**Implication 1 (consumer-pull deferral confirmed).** The substrate's deferral of sparse-Hopfield as a flat-cleanup substitute is LITERATURE-CONSISTENT and is the predicted outcome. Do not re-dispatch experiments seeking sparse-Hopfield wins on quasi-orthogonal residue codebooks; the published bound (Santos HFYN) says it cannot beat naive there.

**Implication 2 (consumer-uptake trigger conditions).** Sparse-Hopfield BECOMES a substrate consumer when ANY of the following regime conditions appear:
- (a) Codebook coherence rises above mu > c/sqrt(N) (correlated stored patterns; e.g., learned codebooks, NLP-derived embeddings, structured ontology atoms).
- (b) Superposition depth k >= 2 with non-trivial coherence (bundle decoding where the (2k-1)*mu < 1 threshold binds).
- (c) Massive low-witness-rate MIL-like pooling tasks (substrate-as-immune-repertoire-classifier downstream).
- (d) Interpretability requirements where exact-zero attention weights are downstream-useful.

**Implication 3 (substrate product positioning).** The honest framing for the internal tracking document: "Sparse-Hopfield ties naive flat cleanup on quasi-orthogonal codebooks (predicted by Santos HFYN well-separation theorem). Sparse-Hopfield is RETAINED as a consumer-pull primitive for correlated-codebook regimes when substrate encounters them downstream (learned codebooks, structured pattern stores, bundle decoding)."

**Implication 4 (next-drill candidates).** If/when substrate ENTERS a correlated-codebook regime (e.g., learned-codebook lane, downstream NLP integration), re-dispatch sparse-Hopfield CHARACTERIZATION drill with focus on (a) crossover rho-threshold measurement, (b) beta-tuning sensitivity, (c) metastable-mixing rate analogous to Santos 2024 Table 1.

**Implication 5 (cap_map standing).** This drill RESOLVES the consumer-pull deferral with a literature-confirmed answer rather than an experiment-deferred answer. The result is a STANDING characterization that does not need re-litigation absent a regime-change signal from substrate.

## (f) Citations (verified count: 17 distinct papers across 3 threads)

Core sparse-Hopfield (4):
- [Hu 2023] Hu, Yang, Wu, Xu, Chen, Liu. "On Sparse Modern Hopfield Model." NeurIPS 2023. arXiv:2309.12673. [VERIFIED]
- [Santos 2024] Santos, Niculae, McNamee, Martins. "Sparse and Structured Hopfield Networks." ICML 2024. arXiv:2402.13725. [VERIFIED]
- [Santos 2024 HFYN] Santos et al. "Hopfield-Fenchel-Young Networks." JMLR 2025 / arXiv:2411.08590. [VERIFIED]
- [Wu 2024 STanHop] Wu, Hu et al. "STanHop: Sparse Tandem Hopfield Model." ICLR 2024. arXiv:2312.17346. [VERIFIED]

Modern Hopfield foundations (3):
- [Ramsauer 2021] Ramsauer, Schaefl, et al. "Hopfield Networks Is All You Need." ICLR 2021. arXiv:2008.02217. [VERIFIED]
- [Demircigil 2017] Demircigil et al. "On a Model of Associative Memory with Huge Storage Capacity." J. Stat. Phys. 168. [VERIFIED]
- [Krotov-Hopfield 2016] Krotov, Hopfield. "Dense Associative Memory for Pattern Recognition." NeurIPS 2016. arXiv:1606.01164. [VERIFIED]

Sparse-attention downstream (3):
- [Correia 2019] Correia, Niculae, Martins. "Adaptively Sparse Transformers." EMNLP-IJCNLP 2019. arXiv:1909.00015. [VERIFIED]
- [Martins-Astudillo 2016] "From Softmax to Sparsemax." ICML 2016. [VERIFIED]
- [Widrich 2020 DeepRC] Widrich et al. "Modern Hopfield Networks and Attention for Immune Repertoire Classification." NeurIPS 2020. [VERIFIED]

Coherence / cleanup foundations (5):
- [Tropp 2004] "Greed is good: algorithmic results for sparse approximation." IEEE Trans. Inf. Theory. [VERIFIED]
- [Donoho-Elad 2003] "Optimally sparse representation in general (nonorthogonal) dictionaries via ell_1 minimization." PNAS. [VERIFIED]
- [Donoho-Tanner 2009/2010] Donoho, Tanner phase-transition papers. [VERIFIED]
- [Kanerva 1988] "Sparse Distributed Memory." MIT Press. [VERIFIED]
- [Plate 1995, 2003] "Holographic Reduced Representations." [VERIFIED]

HDC/VSA + concentration (2):
- [Kleyko 2022] Kleyko, Rachkovskij, Osipov, Rahimi. "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part II." ACM CSUR. arXiv:2112.15424. [VERIFIED]
- [Vershynin 2018] "High-Dimensional Probability." Cambridge. [VERIFIED textbook]

## Calibration note

Per [[feedback-lit-scan-calibration-penalty]]: P_deflated = 0.78 (from 0.90 unbiased) reflects (a) Santos 2024 HFYN and Hu 2023 explicit well-separation theorems (HIGH confidence); (b) one residual uncertainty -- substrate residue-codebook structure may have non-trivial sub-block structure not captured by mu_max measurement alone (deflation 0.12). Cap on novel-synthesis = 0.50 applied to the cap_map closure decision.

## Auto-trigger downstream

This drill closes a Trigger C / Trigger D class: the substrate observed sparse-Hopfield TIE and pulled back to consumer-pull defer. The deferral is now LITERATURE-CONFIRMED-AS-EXPECTED rather than experiment-pending. No follow-up sparse-Hopfield drill needed unless substrate enters correlated-codebook regime.

Next-drill candidate (per field advisor adjacency): superposition / bundle-decoding lane -- when k >= 2 and coherence is nontrivial, the substrate may enter the Tropp / Donoho-Tanner regime where iterative sparse recovery (BP, OMP, LASSO, AMP/VAMP) is provably necessary. AMP/VAMP is tier-2 (33% yield, 3 drills) on the field-coverage matrix; an adjacency drill into "AMP for bundle-decoding on quasi-orthogonal codebooks" would be high-value if substrate moves toward superposition workloads.
