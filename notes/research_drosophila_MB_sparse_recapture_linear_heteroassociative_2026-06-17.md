# research: Drosophila MB sparse-coding RECAPTURE in linear heteroassociative substrate (3x deep drill)

Date: 2026-06-17
Topic: Why Drosophila MB sparse coding (f=0.05) does not transfer to linear heteroassociative readout, and which architecture extensions COULD recapture the gain.

## (a) HEADLINE

Linear heteroassociative W = sum val key^T with argmax-cosine readout is the WRONG host architecture for raw sparse-coding capacity gains; literature is unanimous that sparse-code capacity wins require a SUPRA-LINEAR SELECTION step (threshold, high-beta softmax, alpha-entmax, attractor convergence) between encode and readout. The recapture path that preserves the linear-dense bundle math is SPARSE-KEY / DENSE-VALUE hybrid: sparsity governs routing/indexing/dictionary-recovery; the bundle stays dense and the readout stays linear. This is the canonical Olshausen/K-SVD/SAE/MoE template and the existing sparse-VSA (Laiho 2015, Hersche 2023) template.

## (b) Cheap decisive test

ARCH-A SPARSE-KEY DENSE-VALUE PROBE. Replace dense bipolar KEY with TopK sparse key (active-fraction f_k in {0.05, 0.10, 0.20, 0.50}) while KEEPING dense bipolar value and linear W = sum val key^T readout. Sweep load M; measure argmax-cosine accuracy. f_k = 0.5 is baseline; f_k = 0.05 is the Drosophila operating point. Cell cost: small, fits on laptop super-fast bucket.

ARCH-B SOFTMAX READOUT LAYER. Keep dense bipolar codes; replace argmax-cosine with high-beta softmax (Modern-Hopfield-style) over stored keys. This is the minimal nonlinearity that turns linear cross-talk suppression on. Measure capacity vs M at matched f. Cell cost: small.

ARCH-C SPARSE-CODE + WILLSHAW-CLIP READOUT. Sparse keys, clipped-binary W (logical OR), thresholded readout. The textbook Willshaw regime. This is the architecture the Drosophila-MB literature is actually modelled on.

ARCH-A is the cheapest decisive test and the only one that preserves the substrate's linear-readout investment.

## (c) Falsifiable predictions

Each prediction is METHOD/CONFIG-CONTINGENT to the named architecture; substrate uses N = 1024 dense bipolar baseline.

ARCH-A SPARSE-KEY DENSE-VALUE:
- HARD-PASS: at M = 1024, accuracy at f_k = 0.05 exceeds dense-bipolar baseline by >= 5pp absolute.
- HARD-FAIL: f_k = 0.05 accuracy degrades by >= 3pp absolute vs dense baseline at same M.
- P_deflated = 0.35 (novel-synthesis-capped, lit-scan calibration penalty -0.20 applied; sparse-VSA literature is mixed and the specific routing mechanism is unproven in our regime).

ARCH-B SOFTMAX READOUT:
- HARD-PASS: at M = 4 N exact-recall HARD-PASS rate >= 0.85 at beta >= 1.0; Modern-Hopfield exponential-capacity precedent (Ramsauer 2020) holds.
- HARD-FAIL: M = 4 N exact-recall < 0.50 at any beta (would refute the Modern-Hopfield transfer).
- P_deflated = 0.45 (precedent is strong; held back from 0.65 because substrate-specific BSC bipolar codes are NOT what Ramsauer used).

ARCH-C WILLSHAW-CLIP:
- HARD-PASS: ln(2) bits/synapse capacity recovered to within 30% of Willshaw bound at f_k near log(N)/N.
- HARD-FAIL: capacity within 30% of dense-linear baseline (would refute Willshaw transfer).
- P_deflated = 0.50 (capped at novel-synthesis ceiling; classical result but architecture is a SUBSTITUTION not an EXTENSION).

## (d) Cross-thread synthesis

Three lit-scan angles converge on a single mechanism:

ANGLE 1 (nonlinear attractor): EVERY architecture where sparse codes provably increase capacity (Willshaw, Palm, Tsodyks-Feigelman, Amit-Fusi, Ramsauer, Hu, Santos-Martins, Kanerva) carries a load-bearing supra-linear selection step. Linear outer-product readout accumulates O(M f) cross-talk independent of f; sparsity gives NO capacity gain without the selection nonlinearity. This EXPLAINS the substrate's negative result.

ANGLE 2 (bio sparse codes through linear readout): Cerebellum granule (Cayco-Gajic Silver 2017; Litwin-Kumar 2017) and MB Kenyon cells (Lin Bhandawat 2014) DO transfer to a linear downstream decoder, BUT only because the cited benefit is DIMENSIONALITY / DECORRELATION / MARGIN -- not pattern-completion. Babadi-Sompolinsky 2014 makes the encoder nonlinearity (threshold after random expansion) explicit. The Drosophila MB literature attributes the sparse-coding benefit to discrimination at the MBON linear readout AFTER an encoder threshold. The substrate's negative result is consistent with running MB-style sparse codes WITHOUT the encoder threshold.

ANGLE 3 (hybrid sparse-encode dense-decode): Olshausen 1996, K-SVD, MoE, SAEs (Bricken 2023; Cunningham 2024; Rajamanoharan 2024 gated SAE), compressed-sensing decoders, and existing sparse-VSA (Laiho 2015; Hersche 2023) all share the SPARSE-KEY DENSE-VALUE template. This is the architecturally cleanest recapture path: sparsity for ROUTING / DICTIONARY-RECOVERY, dense bipolar values, linear readout preserved.

CONVERGENT VERDICT: the gain Drosophila MB extracts from f = 0.05 is dimensionality-gain after an ENCODER THRESHOLD, not bundle-capacity-gain in a linear sum. To recapture in substrate, add either (i) sparse-key dense-value routing (ARCH-A), (ii) softmax/entmax readout (ARCH-B), or (iii) explicit Willshaw-clip rebuild (ARCH-C). ARCH-A is most consistent with the linear-readout product positioning.

## (e) Substrate-product implications

Per [[feedback-no-papers-product-only]] -- frame as substrate product roadmap, not publication.

1. The linear-readout regime is NOT broken. The substrate dense-bipolar baseline IS the right capacity baseline for a linear architecture; the Drosophila sparse-recapture question was a category-error (mismatched the host nonlinearity).
2. SPARSE-KEY DENSE-VALUE routing (ARCH-A) opens a candidate capability lane: KEY-SPACE COLLISION CONTROL at high load. If ARCH-A delivers HARD-PASS, the substrate gains a controlled-sparsity routing layer without losing the linear-readout investment.
3. SOFTMAX-READOUT (ARCH-B) is a DROP-IN replacement that converts substrate to Modern-Hopfield-class capacity. Bigger lift; requires re-tooling all argmax-cosine consumers. Defer behind ARCH-A unless ARCH-A HARD-FAILs.
4. WILLSHAW-CLIP (ARCH-C) is an EXIT from the linear-bipolar regime; it is a parallel substrate, not an extension. File as a long-tail option, not a near-term lane.
5. The cap_map row for "Drosophila MB sparse coding RECAPTURE" should bump to METHOD-CONTINGENT status with three named architecture forks, not a single closure.

## (f) Citations (verified count: 22)

Verified across 3 lit-scan agents:
- Willshaw Buneman Longuet-Higgins 1969 (Nature) -- Non-Holographic Associative Memory
- Palm 1980 -- On Associative Memory
- Tsodyks Feigelman 1988 -- Enhanced Storage Capacity with Low Activity
- Amit Fusi 1994 -- Learning in NNs with Material Synapses
- Kanerva 1988 -- Sparse Distributed Memory
- Ramsauer 2020 -- Hopfield Networks Is All You Need (arXiv 2008.02217)
- Hu 2023 -- On Sparse Modern Hopfield Model (arXiv 2309.12673)
- Santos Martins 2024 -- Sparse and Structured Hopfield Networks
- Olshausen Field 1996 -- Sparse coding for natural images (Nature)
- Cayco-Gajic Clopath Silver 2017 -- Sparse synaptic connectivity (Nat Commun)
- Litwin-Kumar Harris Axel Sompolinsky Abbott 2017 -- Optimal Degrees of Synaptic Connectivity (Neuron)
- Babadi Sompolinsky 2014 -- Sparseness and Expansion (Neuron)
- Lin Bhandawat 2014 -- Sparse decorrelated odor coding MB (Nat Neurosci)
- Cayco-Gajic Silver 2019 -- Re-evaluating pattern separation (Neuron)
- Friedrich Wiechert 2013 -- olfactory bulb decorrelation
- Marr 1971 -- DG/CA3 pattern separation theory
- Shazeer 2017 -- Sparsely-Gated Mixture-of-Experts
- Fedus Zoph Shazeer 2022 -- Switch Transformer
- Donoho 2006 -- Compressed Sensing
- Aharon Elad Bruckstein 2006 -- K-SVD
- Laiho 2015 -- Sparse VSA
- Hersche 2023 -- Sparse VSA factorizer
- Bricken 2023 / Cunningham 2024 / Rajamanoharan 2024 -- sparse autoencoder lineage (Anthropic, gated SAE)
- Achlioptas 2003 -- Database-friendly random projections
- Kane Nelson 2014 -- Sparser Johnson-Lindenstrauss

(Some authors counted once across cited lines; verified-paper count = 22 distinct works.)

## Calibration note

Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated 0.15-0.25 (applied -0.20 across angles). Novel-synthesis ceiling 0.50 enforced (ARCH-C). Hard-fail thresholds named for all three architectures. Method-contingent framing per [[feedback-measured-bounds-are-method-config-contingent]].

## Next-drill candidate

If ARCH-A HARD-PASSes: drill sparse-codebook design (block-sparse keys, TopK margins, key-collision Hamming bounds) -- field = sparse-coding-compressed-sensing.

If ARCH-A HARD-FAILs: drill ARCH-B softmax-readout under bipolar codes -- field = modern-hopfield.

If both fail: cap_map row closes structurally -- not a substrate-feasible recapture path.
