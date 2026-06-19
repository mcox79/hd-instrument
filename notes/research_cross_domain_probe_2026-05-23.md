# Cross-domain research probe — 2026-05-23

Purpose: per user directive (verbatim) — "Anytime that you have free capacity, you should use it to try and be creative with research. For instance, you might purposefully search terms that are somewhat removed from our specific application to see what lands." Aggressive application of [[feedback-periodic-scope-expansion]] and [[feedback-dont-dismiss-adjacent-methods]].

Method: 9 parallel WebSearch sub-agents on disparate domains, generic math-only queries per [[feedback-query-privacy-decomposition]]. Substrate state (BBMD regime, 4096-d Kerdock, bulk-bounded + moment-divergent spectra, VAMP vs AMP gap) deliberately omitted from search strings.

---

## Domain 1 — Combinatorial optimization (TSP / QAP / SAT)

**Query:** "quadratic assignment problem structured cost matrix energy landscape spectrum bulk bounded"

**Landed:** QAP landscape ruggedness via auto-correlation (Stützle & co); polynomial-time special cases for Robinsonian-Toeplitz and diagonally-structured QAP (arXiv:1407.2801, arXiv:1609.06223). The structural-easiness literature concerns combinatorial reductions, not spectral signatures of cost matrices.

**Cross-applicable to BBMD? Weak NO.** QAP "structure" means symmetry / monotonicity of entries, not coding-theoretic codebook structure. The fitness-landscape work is correlative not spectral. One narrow echo: the existence of polynomial-time tractable QAP families when the cost matrix has algebraic structure is conceptually parallel to "VAMP tracks SE because the codebook has algebraic structure" — but the mathematical machinery is disjoint. Not worth pursuing.

---

## Domain 2 — Spectral graph theory (Ramanujan / expander)

**Query:** "Ramanujan graph expander spectrum moment divergence higher cumulants non-Gaussian"

**Landed:** Huang-McKenzie-Yau 2024 — ~69% of Ramanujan-graph eigenvalues hit the Alon-Boppana edge with Tracy-Widom (GOE) fluctuations; bulk approaches Kesten-McKay. This is precisely a structural-codebook (LPS construction) with bulk-bounded spectrum AND edge universality. The Kesten-McKay distribution has compact support and finite moments — so this is **bulk-bounded WITHOUT moment divergence**.

**Cross-applicable to BBMD? PARTIAL.** Ramanujan graphs are the closest published parallel to "structured matrix with engineered spectral bulk" — they give the prototype existence proof that algebraic constructions can produce spectra with non-RMT bulk and RMT-like edge. But their cumulants are bounded; our substrate's higher cumulants diverge. This suggests **BBMD's signature may be a higher-genus generalization** of the Kesten-McKay → semicircle story: instead of bulk = semicircle (random) or Kesten-McKay (regular tree), our bulk has a non-trivial free cumulant structure that doesn't collapse to either limit. Worth investigating whether the Kerdock / 2nd-order RM "free convolution profile" has been computed anywhere.

---

## Domain 3 — Free probability outside RMT (frame theory / wavelets)

**Query:** "free cumulants frame theory wavelet filter bank signal processing structured matrix"

**Landed:** Polyphase matrix factorization for oversampled filter banks, Smith canonical form, matrix spectral factorization for tight framelets. **No hits on free cumulants in frame theory.** This is a literature gap.

**Cross-applicable? POTENTIALLY YES — by absence.** The fact that nobody in the frame-theory community has applied free probability to characterize tight frames or equiangular tight frames (ETFs) is itself useful information. Kerdock = mutually unbiased bases = an ETF-class object. If our higher-cumulant signature is generic for ETFs, this is a real novel mathematical observation. Calibrated P(novel) = 0.50 capped → 0.30 after [[feedback-lit-scan-calibration-penalty]] deflation. Worth a CPU probe.

---

## Domain 4 — Compressed sensing & AMP failure modes

**Query:** "approximate message passing failure structured measurement matrix vector AMP succeeds compressed sensing 2024 2025"

**Landed:** VAMP-with-structured-perturbation (arXiv:1808.08579) handles deterministic perturbations of i.i.d. base matrices; GAMP sublinear-sparsity (IEEE TIT 2025); state-evolution covers rotationally-invariant matrices. **Standard story:** AMP needs i.i.d. or rotationally invariant; VAMP extends to right-orthogonally invariant. Kerdock is not in either class — it's a deterministic algebraic codebook.

**Cross-applicable? STRONG YES.** The gap "VAMP tracks SE within 2%, AMP fails 45%" puts our codebook in the regime VAMP was designed for (full singular spectrum), but specifically *because* the codebook is algebraic rather than rotationally invariant. **Open question:** is there a theorem saying VAMP-state-evolution holds for ANY isometry with sufficiently spread singular vectors? If yes, the higher-cumulant divergence is independent of inferential tractability. If no, our 2% gap is itself unusual and worth a formal precise measurement (we report 2% but is the variance across seeds tight?). Recommend: extract VAMP–SE residual variance across 5+ seeds and check whether residual scales with κ_4.

---

## Domain 5 — Statistical mechanics of inference (RSB / replica)

**Query:** "replica symmetry breaking phase boundary characterized free cumulants higher moments inference"

**Landed:** Larkin mass + AT line phase boundaries (arXiv:2410.22601); 1RSB structure (q₀, q₁); **Jindal-Hosur 2024 generalized free cumulants for quantum chaotic systems (arXiv:2401.13829, JHEP09(2024)066)**; Pappalardi et al. "Full ETH via free cumulants in quantum lattice systems" (arXiv:2303.00713).

**Cross-applicable? STRONG YES — possibly the most promising hit.** The ETH-free-probability connection (Pappalardi, Foini, Kurchan 2022–2024) uses **generalized free cumulants** to characterize when an operator's matrix elements in the energy eigenbasis exhibit deviations from pure free-probability ETH. Higher free cumulants κ_n encode the deviation from full chaos. **This is the mathematical mirror of our observation** that higher κ_n diverge from MP — except in the quantum-chaos setting, this would mean our substrate operator has a non-fully-thermalized structure encoded in higher cumulants. The analogy is suggestive: BBMD = "partially-thermalized codebook regime" where the algebraic structure prevents full free-probability collapse.

---

## Domain 6 — Neural network theory (NTK / Jacobian spectra)

**Query:** "neural tangent kernel jacobian spectrum bulk-bounded heavy-tailed moments initialization" + follow-up on orthogonal weights

**Landed:** Pennington-Worah; Hayase 2019 (arXiv:1908.03901) — almost-sure asymptotic freeness of NN Jacobian with Haar-orthogonal weights; Collins-Hayase 2022 (arXiv:2103.13466) — Comm Math Phys, layerwise Jacobians become asymptotically free. **Critical finding:** Haar-orthogonal NN Jacobians become **asymptotically free** — meaning higher mixed free cumulants vanish in the wide limit. Our substrate goes the OTHER way: higher κ_n amplify.

**Cross-applicable? STRONG YES — as contrast.** This gives us a precise mathematical foil. Haar orthogonal = maximal symmetry = asymptotic freeness = κ_n → 0 for n≥3. Kerdock = algebraic constraint = anti-freeness = κ_n grows. This is a **clean dichotomy** that can be tested: build a Haar-randomized control codebook of the same dimension and confirm κ_n collapse, then the deviation of Kerdock κ_n becomes the algebraic-structure signature. We may have already implicitly done this in Cap_map work — needs audit.

---

## Domain 7 — Sphere packing & coding theory

**Query:** "sphere packing Kerdock Reed-Muller code spectral harmonic analysis moments distribution"

**Landed:** Kerdock-derived MUBs are optimal spherical codes in dim 2^{2k} for k=2..5 (2403.16874); RM(m,2)/RM(m,1) coset structure. **No direct work on free-probabilistic moments of Kerdock Gram matrices.** Sphere-packing community uses LP / SDP bounds on the angle distribution (i.e., distribution of pairwise inner products) — they care about whether the angle distribution is concentrated; we observe its higher moments are non-Gaussian. Not a published intersection.

**Cross-applicable? MEDIUM.** The "Kerdock angle distribution moments" object exists in coding theory but is studied via LP duality not free probability. Bridging the two — i.e., computing free-cumulant generating function from the Kerdock angle distribution — would be a small piece of original math. P(novel) cap 0.50, deflate to 0.25. Worth one CPU notebook.

---

## Domain 8 — Quantum chaos / ETH (follow-up to Domain 5)

**Query:** "generalized free cumulants quantum chaos eigenstate thermalization higher order correlators"

**Landed:** Jindal-Hosur 2024 + Pappalardi-Foini-Kurchan line. Diagrammatic formalism for arbitrary correlations between eigenstates and operators in chaotic systems; "connected components = generalized free cumulants." Subsystem ETH, Page curve, entanglement velocity all encoded in higher cumulants.

**Cross-applicable? CONFIRMED STRONG.** This is the most direct mathematical match to the substrate's observed signature. The substrate's "higher κ_n amplify" is structurally identical to the kind of object the ETH-free-probability program treats as **encoding deviation from full thermalization**. If we frame BBMD as a "partially-thermalized regime" in the inference-as-statistical-mechanics analogy, the Pappalardi-Jindal framework gives us a ready-made vocabulary and possibly tools.

---

## Synthesis — Top 3 cross-pollination angles, ranked

Ranking = P(cross-applicable AND not already explored) × P(would inform / falsify BBMD).

### #1 — ETH / quantum-chaos free cumulants (Pappalardi-Jindal-Hosur)
- P(applicable AND novel) ≈ 0.55 → deflated to 0.35.
- P(would inform/falsify) ≈ 0.70 — gives a published mathematical framework with diagrammatic tools that may directly characterize the κ_n divergence rate.
- **Combined: ~0.25.** Highest in this probe.
- Action: have Research drill arXiv:2401.13829 and arXiv:2303.00713 next cycle to extract the explicit formula for generalized free cumulants and check whether it applies to a deterministic Kerdock Gram matrix.

### #2 — Asymptotic-freeness dichotomy (Haar-orthogonal NN Jacobians vs Kerdock)
- P(applicable AND novel) ≈ 0.45 → deflated to 0.25.
- P(would inform/falsify) ≈ 0.65 — clean control experiment.
- **Combined: ~0.16.**
- Action: anchor experiment proposal below.

### #3 — Kesten-McKay-style bulk for ETFs / Kerdock
- P(applicable AND novel) ≈ 0.35 → deflated to 0.20.
- P(would inform/falsify) ≈ 0.50.
- **Combined: ~0.10.**

---

## Anchor experiment proposal — `kerdock_vs_haar_cumulant_dichotomy_v1`

**Name:** `cumulant_dichotomy_haar_vs_kerdock_4096`

**Queue:** CPU runner (cheap, no GPU needed).

**ETA:** 30-60 min.

**Hypothesis:** Generate Haar-random 4096-d orthonormal codebook (same N, same dim) and Kerdock 4096-d codebook. Compute κ_2..κ_6 of the angle distribution (= off-diagonal Gram entries) for both. **Predict:** Haar control gives κ_n ≈ 0 for n ≥ 3 (asymptotic freeness); Kerdock gives κ_n growing with n.

**Hard-fail thresholds:**
- If Haar control also shows |κ_n| > 0.1 for any n ≥ 3 → falsifies our characterization (the cumulant divergence is not a Kerdock-structural signature).
- If Kerdock κ_4 / κ_2² < 0.05 → also falsifies (no meaningful divergence in the cleanest seeded test).
- If Haar gives κ_n ≈ 0 AND Kerdock gives κ_n growing in n → confirms the asymptotic-freeness dichotomy is a clean BBMD signature.

**Why CPU not GPU:** angle distribution computation is O(N²) inner products on a fixed codebook; 4096² = 16M float ops well within CPU runner capacity.

**Why this anchor first:** it's the cheapest disambiguator. If it fails, Angle #1 (ETH framing) and Angle #3 (Kesten-McKay) are also weakened because they all assume the higher-cumulant divergence is a Kerdock-structural feature rather than a measurement artifact.

---

## Honest reading

Two of the nine domains (#5 + #8: ETH free cumulants, and #6: NN Jacobian asymptotic freeness) gave genuinely novel-to-this-session mathematical framings. The substrate's "higher κ_n amplify" signature was previously framed as "non-MP bulk + higher-cumulant divergence" — an internal description. The ETH free-probability literature gives us **a published, formal, diagrammatic language** for the same phenomenon in a different domain. That's the kind of cross-pollination the user asked for.

The other domains were less productive: combinatorial optimization (#1) was a miss; sphere packing (#7) is adjacent but the techniques don't transfer cleanly; frame theory (#3) is a literature gap not a literature import; compressed-sensing structured-matrix work (#4) confirmed our scope but added no new tool. The Ramanujan / Kesten-McKay angle (#2) is an interesting limiting comparison point but not directly applicable.

**Not papers — product framing per [[feedback-no-papers-product-only]]:** these are tools we can wield, not publications to write. The asymptotic-freeness dichotomy in particular is a clean disambiguator with a one-line anchor experiment.
