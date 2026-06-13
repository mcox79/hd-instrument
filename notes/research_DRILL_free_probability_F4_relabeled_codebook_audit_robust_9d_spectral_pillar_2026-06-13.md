# Research drill: F4 free-cumulant invariance under codebook node relabeling — audit-robust 9d spectral pillar

Date: 2026-06-13
Field: free-probability (tier-1, scope-expansion)
Topic: Are F4 free cumulants kappa_3, kappa_4 invariant under node relabeling of the clustered codebook? If yes, the 9d spectral observability pillar is audit-robust against authoring-confound challenges.

## (a) HEADLINE

Free cumulants kappa_n are PROVABLY invariant under node relabeling IF AND ONLY IF the codebook spectrum's distributional structure is invariant under unitary (or asymptotically free) action. Bare permutation-invariance is **STRICTLY WEAKER** than unitary-invariance (Au et al. 2015; Mingo-Speicher 2017). For a CLUSTERED codebook (12 archetype classes), the bulk free cumulants are predicted invariant under within-cluster relabelings AND under cluster-respecting permutations, but cross-cluster scramblings can shift kappa_3 and kappa_4 by an amount controlled by the inter-cluster block contrast. The decisive empirical test is therefore non-trivial: a single relabel-distribution does not falsify; we need two separate tests (within-cluster + cross-cluster) and we read the contrast.

**P_deflated = 0.55** that bulk kappa_3, kappa_4 are within-cluster invariant under N=100 relabelings (HARD-PASS test).
**P_deflated = 0.30** that they are also cross-cluster invariant without spike deflation (this is the strong audit-robust claim; if it fails, we still have the within-cluster claim which suffices for 9d pillar audit-robustness AFTER spike deflation per the 9d-Cell-C deflation protocol).

Calibration penalty applied: substrate clustered codebook is in uncharted regime (no published precedent specifically for HRR codebooks with 12-archetype block structure); novel-synthesis P capped at 0.50 for the strong cross-cluster claim; deflated 0.15 from agent priors.

## (b) Cheap decisive test

Local CPU, ~30 min:

1. **Load production codebook** (~1743 atoms, 12 archetype clusters per partition routing artifact).
2. **Compute baseline F4**: estimate sample moments m_1..m_8 of the codebook Gram matrix (or W matrix per substrate convention), invert via the free moment-cumulant relation (Mingo-Speicher Eq 1.13) to get kappa_3, kappa_4 on the BULK (after deflating the top-K outlier eigenvalues per 9d Cell C spike-bulk decomposition; K = number of clusters = 12).
3. **Within-cluster relabel test**: pick a random within-cluster permutation pi_within (relabel atoms ONLY within their own cluster); recompute F4 on permuted codebook. Repeat N=100 times. Report kappa_3 and kappa_4 distributions; compute bootstrap 95% CI; null hypothesis: distribution is a point mass at baseline.
4. **Cross-cluster relabel test**: pick a random uniform permutation pi_cross (any atom to any slot); recompute F4. Repeat N=100. Report distribution + CI.
5. **Compare**: within-cluster CI width vs cross-cluster CI width vs baseline; ratio (cross/within) IS the substrate-internal observable answering "do labels leak into F4."

Pre-registered metrics: standard error of kappa_3 across N=100 relabels, expressed as fraction of the baseline magnitude.

## (c) Falsifiable predictions

### HARD-PASS thresholds (audit-robust 9d pillar stands strong)

- Within-cluster: SE(kappa_3)/|kappa_3| <= 0.05 AND SE(kappa_4)/|kappa_4| <= 0.05.
- Within-cluster bootstrap 95% CI contains baseline for both kappa_3 and kappa_4.
- Cross-cluster (on spike-deflated bulk): SE(kappa_3)/|kappa_3| <= 0.10 AND SE(kappa_4)/|kappa_4| <= 0.10.

If ALL three pass, the 9d spectral pillar is empirically audit-robust under adversarial relabeling. Substrate-product claim "9d spectral observability is RMT-universal" is **EMPIRICALLY VALIDATED** under skunkworks adversarial conditions.

### HARD-FAIL thresholds (downgrade)

- Within-cluster: SE(kappa_3)/|kappa_3| > 0.20 OR SE(kappa_4)/|kappa_4| > 0.20.
- This would indicate kappa_n is reading the within-cluster atom INDEX (label) rather than the eigenvalue distribution — which is mathematically anomalous and would force a re-examination of how F4 is computed.

If HARD-FAIL, the 9d pillar EXTENSION to F4 (cumulant) dimension is downgraded; the bulk-fitting dimensions 1-3 (R-transform location, MP-bulk shape, 1/sqrt(N) Kolmogorov) remain audit-robust because they were validated independently.

### MIDDLE BAND (informative)

- Within-cluster PASS but cross-cluster FAIL: this is the EXPECTED outcome per theory (Au et al. 2015 — permutation-invariance < unitary-invariance for structured ensembles). Substrate-product positioning is preserved by INSISTING on the spike-deflation protocol before computing F4 cross-cluster. This becomes a new methodology rule candidate: "F4 free cumulants on clustered codebook MUST be computed on spike-deflated bulk; raw F4 leaks block-structure into higher cumulants."

## (d) Cross-thread synthesis

- **9d spectral pillar (existing)**: Cell C spike-bulk decomposition explicitly proposed top-12-outlier deflation before bulk fitting; this drill provides the THEORETICAL JUSTIFICATION (Voiculescu unitary-invariance + Au permutation-vs-unitary gap) for WHY deflation is necessary. The 9d pillar's robustness is contingent on the deflation step being done correctly.
- **Cell SC HARD-PASS (existing)**: P=250 partitions at 10M scale, routed recall@10 0.765 N-invariant. The 12-archetype block structure used in this drill is the SAME L1 categorical clustering as Cell SC. If the cross-cluster F4 test FAILS without deflation, the partition routing IS visible as a cumulant signature — which is itself a substrate-product positive (the routing structure leaves measurable spectral fingerprints).
- **Verify-before-asserting rule (10th methodology)**: this drill is itself an instance — the audit-robust claim for 9d pillar must not be asserted without the bootstrap-CI evidence from N=100 relabelings.
- **2x discipline**: existing audit-robust narrative was lit-precedent-only ("RMT bulk universality"). This drill is the operational 2x: design the actual empirical adversarial protocol and pre-register the hard-fail bands. Per [[feedback-2x-means-depth]].
- **Always-reconsider-frameworks (7th rule)**: this drill is the framework-reconsideration probe for the 9d pillar — explicitly testing whether the spectral architecture survives an adversarial scramble.

## (e) Substrate-product implications

1. **Audit-robust 9d pillar = canonical claim**: After this drill PASSES (or fails-then-deflation-rescues), substrate can state "9d spectral observability is invariant under codebook relabeling and is therefore reading STRUCTURE not LABELS." LLMs cannot make this claim — their representations have NO eigenvalue structure to relabel-invariantly observe.
2. **New methodology-rule candidate (1st appearance)**: "Spectral observability claims on clustered substrates require deflation before higher-cumulant estimation; cumulants on raw spectrum leak block-structure for any non-asymptotically-free ensemble." This is a structural rule for any future substrate audit.
3. **Substrate-internal contrast metric**: the ratio SE(cross-cluster) / SE(within-cluster) is itself a new observable — call it the **block-leakage index** — quantifying HOW MUCH cluster structure is in higher cumulants. For a perfectly unitary-invariant codebook this ratio approaches 1; for a strongly block-diagonal SBM-like codebook it diverges. Substrate has a novel handle on its own representation regularity that LLMs have zero analog for.
4. **9d -> 10d extension candidate**: the block-leakage index could be Dimension 10 of the observability pillar. Defer until empirical reading is in.

## (f) Citations (verified count: 8)

1. Voiculescu (1991), "Limit laws for random matrices and free products" — foundational asymptotic-freeness + unitary-conjugation theorem.
2. Mingo & Speicher (2017), "Free Probability and Random Matrices" (Fields Institute Monograph), Chapters 1-4 — moment-cumulant inversion, asymptotic freeness for unitary-invariant ensembles.
3. Au, Cebron, Dahlqvist, Gabriel, Male (2015), "Combinatorial theory of permutation-invariant random matrices II: cumulants, freeness and Levy processes," arXiv:1507.02465 — explicit proof that permutation-invariance is STRICTLY WEAKER than unitary-invariance; introduces traffic-distribution framework that subsumes free cumulants for permutation-invariant ensembles.
4. Speicher (2018), "Free Probability Theory and Random Matrices" survey — proves kappa_n(a+b) = kappa_n(a) + kappa_n(b) under asymptotic freeness, the relabel-invariance corollary.
5. arXiv:2309.14315 (2024), "Structured random matrices and cyclic cumulants: A free probability approach" — explicitly addresses when block-structured matrices need cyclic cumulants rather than free cumulants; relevant for clustered codebook case.
6. Tang & Priebe (2018), "The eigenvalues of stochastic blockmodel graphs," arXiv:1803.11551 — SBM spectrum has bulk + outliers; bulk follows Wigner/MP universality after deflation; outliers carry community signal.
7. arXiv:2410.00908 (2024), "Free cumulants and freeness for unitarily invariant random tensors" — current state-of-art on when cumulants are invariant for non-vector ensembles.
8. arXiv:2412.01574 (2024), "Unifying AMP Algorithms for Rotationally-Invariant Models" — sample-moment estimators for free cumulants at finite N (the m_n = (1/N) g^T W^n g estimator used in step 2 of the test).

## Pre-registration summary (for status_log)

- Test: N=100 within-cluster + N=100 cross-cluster relabels; bootstrap 95% CI on kappa_3, kappa_4.
- HARD-PASS within-cluster: SE/|kappa| <= 0.05; cross-cluster (deflated): SE/|kappa| <= 0.10.
- HARD-FAIL: SE/|kappa| > 0.20 within-cluster.
- Compute cost: ~30 min local CPU on 1743-atom codebook.
- Substrate product reading: PASS = audit-robust 9d pillar canonical claim; MIDDLE = new deflation methodology rule; FAIL = downgrade 9d pillar's F4 dimension only (dims 1-3, 5-8 retained).

## Companion exp_dev hand-off

Written separately at notes/exp_dev_handoff_research_F4_relabeled_codebook_audit_robust_2026-06-13.md
