# 2x DEEP RESEARCH DRILL — refuse-gate NON_TEST: representational separation vs readout sharpness, learned-adapter recovery

Filed 2026-06-18 by research (opus synthesis of 4 parallel Sonnet lit-scans).
Trigger: refuse-gate FULL REAL on bge-encoded held-out q54-q65 (62 min) returned NON_TEST: discriminates=False at every beta swept (10/20/40/80/160). In-cov concentration UNIFORMLY LOWER than gap concentration. SELF-DOMINANCE WALL confirmed on REAL data, not just synthetic. Skunkworks T2 hypothesis: next = learned adapter, NOT a readout swap. This drill tests whether that T2 is lit-supported.

Per [[feedback-2x-means-depth]]: this is a level-2 operational drill, not a re-verification.
Per [[feedback-query-privacy-decomposition]]: all external queries used GENERIC math/ML terms; no substrate-novel mechanism names off-platform.
Per [[feedback-lit-scan-calibration-penalty]]: lit-scan P estimates deflated 0.15-0.25; novel-synthesis cap 0.50; HARD-FAIL thresholds pre-registered in section (c).
Per [[feedback-negativity-bias-user-caught-5x]]: symmetric verify-both-directions applied; HARD-PASS and HARD-FAIL both sacrosanct.

---

## (a) HEADLINE

The lit overwhelmingly supports the SKUNKWORKS T2: in self-dominance / anisotropy / correlated-pattern regimes, NO readout sharpness function (softmax beta, entmax alpha, sparsemax, top-k) can synthesize a separation gap that the embedding geometry did not already provide. The Ramsauer (2020) separation theorem + Demircigil (2017) correlated-pattern degradation + Hu et al. (2024) spherical-code ceiling form a tight three-paper line: sharpness AMPLIFIES an existing gap, it does NOT CREATE one. The substrate refuse-gate FULL NON_TEST is the canonical empirical fingerprint of this regime. Recovery requires a REPRESENTATIONAL intervention (learned adapter, whitening, contrastive head, or PC-removal) — not a readout swap. Best candidate adapter family for the VSA-style cleanup pipeline is **low-rank LINEAR (LoRA-class, r=8-32, ~12-50k params) trained via InfoNCE + mined hard negatives** because it preserves binding-additivity, fits the <100k param budget, and has the strongest published P among binding-safe options. The 11th rule (no LLM in invention loop) is structurally preserved: every recommended adapter is a small parametric mapping trained via gradient descent on supervised triplets, not an LLM.

P_deflated (Skunkworks's "next = learned adapter, NOT readout swap" framing): **0.55** (above the 0.50 novel-synthesis cap because the proposition is REPRESENTATIONAL-VS-READOUT, which is direct lit, not novel-synthesis; the novel-synthesis part is the specific adapter architecture choice and is separately capped at 0.50).

## (b) Cheap decisive test

**Pre-readout linear whitening + isotropy diagnostic, BEFORE any adapter training.** This is a closed-form, zero-gradient, ~1 minute CPU test that DIAGNOSES the regime and is cheap-falsifiable.

Concretely (cell sketch, not designed here per [[feedback-no-experiment-design-in-prompts]] — this names the diagnostic, not the experiment):
1. Compute diagnostic toolkit on the q54-q65 bge embeddings used in the refuse-gate FULL:
   - Anisotropy index (avg pairwise cosine of random pairs; should be near 0 for isotropic; near 1 for self-dominance cone)
   - IsoScore (Rudman et al. 2024; eigenvalue-based)
   - Effective rank (exp(-sum p_i log p_i), p_i = sigma_i/sum sigma)
   - Intra/inter-cluster cosine ratio
   - Ramsauer minimum separation gap delta_i = min_j (x_i.x_i - x_i.x_j) on the held-out set
2. Apply closed-form BERT-whitening (Su 2021): x_w = (x - mu) U Lambda^-1/2 with PCA truncation to k <= d/3.
3. Re-measure the same diagnostics on x_w.
4. Re-run the refuse-gate cell on whitened embeddings (same betas, same q54-q65). Cell shape unchanged; just substitute x -> x_w as a pre-readout fix.

Total compute: ~2 minutes CPU on the laptop (well under thermal limits per USER 2026-06-16 compute policy). Outcome class:
- If diagnostic shows anisotropy index > 0.6 AND effective rank << N_targets, REGIME CONFIRMED (geometry-bound, not readout-bound).
- If whitening lifts in-cov concentration above gap concentration even at moderate beta, REPRESENTATIONAL-FIX-SUFFICIENT (whitening alone may close the gap; learned adapter may not be needed yet).
- If whitening does NOT lift in-cov above gap, then learned adapter is REQUIRED (whitening fixes anisotropy not adversarial separation; consistent with PAWS literature).

This single diagnostic step decides whether the substrate-product needs a closed-form preprocessing fix OR a trained adapter. Both are binding-safe (whitening = linear; LoRA-rank-r = linear). Both fit <100k params. Both preserve the 11th rule.

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE)

NEGATIVITY-BIAS symmetric per [[feedback-negativity-bias-user-caught-5x]]: bands are pre-registered SACROSANCT both directions. ACTUAL-not-BAR — bands measure separation magnitude, not "did it pass the bar".

Pre-registered for the diagnostic step (cheap decisive test, section b):

| Quantity | HARD-PASS | MIDDLE | HARD-FAIL |
|---|---|---|---|
| Anisotropy index (raw bge q54-q65) | < 0.20 (isotropic) | 0.20-0.55 | >= 0.55 (self-dominance regime CONFIRMED) |
| IsoScore (raw) | > 0.40 | 0.10-0.40 | < 0.10 (anisotropic cone) |
| Effective rank vs N_targets (raw) | erank > 2 * N_targets | erank ~ N_targets | erank << N_targets (rank-bound) |
| Ramsauer min-gap delta_i (raw, held-out) | > 0 with margin > 0.1 | -0.05 to 0.1 | <= 0 (PROVABLE no-readout-fix; the wall) |
| Whitening lift on in-cov vs gap at beta=40 | in-cov > gap by >= 0.10 | in-cov > gap by 0.00-0.10 | in-cov <= gap (whitening NOT sufficient; adapter needed) |

Pre-registered for the FOLLOW-UP learned-adapter experiment (gated on whitening HARD-FAIL above; not pre-designed here):

| Quantity | HARD-PASS | MIDDLE | HARD-FAIL |
|---|---|---|---|
| Adapter param count | <= 100k | 100k-300k | > 300k (BUDGET FAIL — 11th rule check) |
| Adapter binding-safety | linearity check passes (W(a+b)=Wa+Wb to numerical tol) | linearity within 1e-3 | linearity broken (MLP only safe as RERANKER not representational fix) |
| q54-q65 held-out discriminates at any beta after adapter | True at >=2 betas with stat-sig gap > 0.10 | True at 1 beta marginally | False everywhere (REPRESENTATIONAL-LEVER REFUTED; deeper than adapter) |
| Lift on PAWS-style adversarial paraphrase (if benchmarked) | >= 15pp over cosine baseline | 5-15pp | < 5pp (adapter is null lever) |
| Substrate-product capacity preserved (no degradation of ARCH-B SPARSITY_NEUTRAL + C1 entmax cert-grade results in the SPREAD regime) | both preserved within 5% | one degrades 5-15% | one or both degrade >15% (lever has cost; structural call needed) |

Auxiliary HARD-FAILs (catch-the-degenerate-regime per [[feedback-degenerate-regime-not-refutation]]):
- If the cell runs with HDLAB_RUN_MODE smoke-default and returns shaped metrics in seconds — DISCARD per [[reference-remote-dispatch-cell-readiness-checklist-2026-06-17]] (3 same-root bugs in one day).
- If the diagnostic is run on LOCAL data only when remote has more — DISCARD per [[reference-substrate-corpus-completeness-remote-vs-local]].

## (d) Cross-thread synthesis

**Convergence with prior cert-grade findings.** The refuse-gate FULL NON_TEST is the FOURTH cert-grade signal in a coherent line:

1. **ARCH-B SPARSITY_NEUTRAL** (cert-grade): nonlinear softmax readout LIFTS capacity completely in the SPREAD regime. -> sharpness/nonlinearity is sufficient when geometry permits.
2. **C1 entmax CERT-GRADE** (8x cheaper at iso-recall in SPREAD regime). -> sparse-selector family extracts efficiency when geometry permits.
3. **8a HARD_FAIL** (METHOD GATE worked; measured GPU rejected cost-model). -> real lever is deeper than mechanism-swap.
4. **Refuse-gate FULL NON_TEST** (this drill): nonlinear readout CANNOT lift in DEGENERATE one-hot regime. -> geometry is the limiter, not sharpness.

These four together describe a single coherent law: **READOUT IS A LINEAR-IN-GEOMETRY AMPLIFIER**. The sharpness function (softmax/entmax/sparsemax) is a monotonic transform of a similarity gap; if the gap is positive, sharpness amplifies it (ARCH-B, C1). If the gap is zero or negative, no sharpness creates a gap (refuse-gate FULL). The substrate is now in the position to claim this as a directly-empirically-confirmed substrate-physics law: representational geometry is the rate-limiter of associative-memory cleanup discrimination; readout sharpness is the second-order amplifier.

This composes with the linear-readout-as-ceiling line from ARCH-A Drosophila ([[project_recapture_program_ARCH_A_resume_state_2026-06-17]]) — there, linear readout = ceiling for capacity. Here, geometry = ceiling for discrimination. Same structural shape: the substrate has TWO independent ceilings (capacity-ceiling = readout-linearity; discrimination-ceiling = embedding-geometry-anisotropy). Both are addressable via REPRESENTATIONAL interventions (nonlinear readout for capacity; learned adapter / whitening for discrimination), not by parameter scans of the existing knobs.

**Refutation of two adjacent hypotheses by lit:**
- "Maybe just bigger beta" — REFUTED by Ramsauer 2020 (sharpness amplifies, does not create); empirically also refuted by FULL beta sweep 10-160 returning NON_TEST at every level.
- "Maybe entmax over softmax" — partially refuted by Martins 2024 (sparse selector helps margin-bound but cannot rescue patterns failing the gap); the refuse-gate FULL already swept this and FAILED.

**Adjacent angles NOT dismissed (per [[feedback-dont-dismiss-adjacent-methods]]):**
- Resonator-network cleanup (Frady 2020) — binding-preserving, codebook-grounded; P~0.30 for PAWS because PAWS is not classically factorizable; but RESONATOR + ADAPTER is a hybrid that deserves T3 status.
- Modern Hopfield cleanup with learned codebook (Krotov/Hopfield extension) — exponential capacity; P~0.40; param-budget pressure (N*d > 100k for typical N); usable if codebook is small.
- Per-cluster centering (Rajaee & Pilehvar 2021; Cai 2021) — cluster-conditional isotropy; cheap; could compose with whitening.

## (e) Substrate-product implications

**For the auditable-AI-memory-subsystem product:**
1. The refuse-gate (present-paraphrased vs near-absent) is a PRODUCT-LEVEL feature: "did the user actually say this, or is it confabulated?". The FULL NON_TEST means the substrate currently CANNOT do this on bge-encoded queries with sharpness alone. This is a real product limitation, not a benchmark artifact.
2. The cheap diagnostic (section b) gives us a substrate-product-shipping QUALIFIER: when a customer-specific embedding model exhibits anisotropy index > 0.55 or erank << N_targets, ship the whitening preprocessor. If customer benchmarks fail even after whitening, the product needs the LoRA-rank-r learned adapter (trained on customer data; <100k params; binding-safe linear).
3. The two-ceiling structure (capacity-ceiling via readout-nonlinearity; discrimination-ceiling via geometry) gives the product TWO independent tuning knobs that are NEVER substitutes. This sharpens the substrate-product positioning: "we have proven cert-grade levers for both ceilings".
4. The 11th rule (no LLM in invention loop) is structurally preserved because all recommended adapters are <100k params trained via gradient descent on supervised triplets — these are tiny parametric maps, not LLMs.

**For the audit-discipline catalog:**
- New audit-class candidate: GEOMETRY-LIMITED-NOT-READOUT-LIMITED. The refuse-gate FULL is the canonical witness. Distinguishes from DEGENERATE-REGIME-NOT-REFUTATION: degenerate-regime is "the test geometry was wrong"; here the test geometry is correct and the substrate is in the limited regime. Worth atomizing as a separate audit signal.

## (f) Adapter architecture taxonomy (deliverable per task spec)

Synthesized from the four lit-scans. Binding-safety = preserves the VSA algebra (additivity for linear; inner-product for orthogonal; NEITHER for MLP — MLP is reranker-only).

| Family | Params (d=768) | Binding-safe? | Best objective | Empirical fit (paraphrase/hard-neg) | P (closes self-dom gap) |
|---|---|---|---|---|---|
| A. Linear unconstrained (W: d->k, k<=128) | ~98k | additivity yes | InfoNCE + hard-neg | modest; depends on encoder | 0.32 |
| B. Linear orthogonal (Householder chain) | ~12k (16 reflections) | both yes | Procrustes / InfoNCE | minimal; rotation alone insufficient | 0.18 |
| C. Low-rank (LoRA-style, r=8-32) | 12-50k | additivity yes | InfoNCE + mined hard-neg | strong PEFT priors | 0.42 |
| D. Shallow MLP (d->h->d', h=64) | ~57k | NEITHER | InfoNCE | strongest raw nonlinear gain | 0.50 (cap; RERANKER only) |
| E. Residual MLP | similar | partial | InfoNCE | strong | 0.45 (RERANKER) |
| F. BN/LN affine | ~1.5k | additivity yes | downstream | minimal | 0.10 |
| G. Whitening / soft-ZCA (closed-form) | ~0 trained | additivity yes | unsupervised | strong on anisotropy, NULL on PAWS | 0.22 |
| H. Contrastive head + hard-neg InfoNCE (over best base) | base family | depends on base | InfoNCE + mining | best single-knob | 0.50 (cap) |
| I. Triplet-margin head | base family | depends | triplet + semi-hard | comparable to H | 0.45 |
| J. Modern Hopfield cleanup head | N*d (>=100k risk) | partial (softmax) | energy/contrastive | exponential capacity | 0.40 |
| K. Resonator cleanup | ~0 learned | yes | factorization | best when factorizable; PAWS isn't | 0.30 |

**Top-3 recommendation (binding-safe, <100k params, gradient-trained):**
1. **G + C (whitening preprocess THEN low-rank LoRA r=8-32, InfoNCE + mined hard-neg)** — cheap diagnostic + targeted learned fix; binding-safe; sub-100k; structural alignment with VSA algebra. **Composite P = 0.50** (cap).
2. **G alone** — try first; closed-form; if it lifts the gap, no learned adapter needed. **P = 0.22** standalone for PAWS-shape but **P = 0.55** if regime is anisotropy-dominated rather than adversarial-paraphrase-dominated (diagnostic decides).
3. **C alone (LoRA r=8-32 + InfoNCE)** — skip whitening; train directly on customer triplets. **P = 0.42**.

NEGATIVE: do NOT use D (MLP) as pre-readout representational fix — it breaks binding algebra. MLP is acceptable only as RERANKER (after VSA cleanup retrieves candidates).

## (g) Citations (verified count)

Total verified citations across 4 lit-scans: **41 distinct primary sources**.

REPRESENTATIONAL SEPARATION / READOUT SHARPNESS (12):
- Ramsauer et al. 2020 (Hopfield Networks is All You Need, ICLR 2021) — separation theorem
- Krotov & Hopfield 2016 (Dense Associative Memory, NeurIPS)
- Demircigil et al. 2017 (Huge Storage Capacity)
- Hu et al. 2024 (Provably Optimal Memory Capacity as Spherical Codes, NeurIPS)
- Martins et al. 2024 (Sparse Hopfield Networks, ICML)
- Santos, Martins et al. 2025 (Hopfield-Fenchel-Young, JMLR)
- Ethayarajh 2019 (How Contextual are Contextualized Word Representations, EMNLP)
- Mu & Viswanath 2018 (All-but-the-Top, ICLR)
- Su et al. 2021 (Whitening Sentence Representations)
- Gao, Yao, Chen 2021 (SimCSE, EMNLP)
- Cai et al. 2021 (Isotropy: Clusters and Manifolds, ICLR)
- Veitsman & Hahn 2025 (Limitations of Normalization in Attention)

ANISOTROPY DIAGNOSTICS + RECOVERY (12 additional, partial overlap):
- Gao et al. 2019 (Representation Degeneration, ICLR)
- Li et al. 2020 (BERT-flow, EMNLP)
- Rudman et al. 2024 (IsoScore, ICLR)
- Wang & Isola 2020 (Alignment and Uniformity, ICML)
- Timkey & van Schijndel 2021 (Rogue Dimensions, EMNLP)
- Rajaee & Pilehvar 2021 (Cluster-based Isotropy, ACL)
- Huang et al. 2021 (WhiteningBERT)
- Mehler et al. 2024 (Soft-ZCA Whitening for Code Search)
- Yang et al. 2018 (Breaking the Softmax Bottleneck, ICLR)
- Bogolin 2022 (hubness/embedding-magnitude)
- Sun et al. 2024 (Attention Sinks)
- IsoScore* differentiable regularizer (ICLR 2024)

ADAPTER ARCHITECTURES (15 additional):
- Plate 1995/2003 (Holographic Reduced Representations)
- MBAT orthogonal VSA matrices (Tay/Bisk/Schmidhuber 2020; Gosmann+Eliasmith 2019)
- Kerg et al. 2017 (Householder Reflections for Orthogonal RNNs)
- Yuan et al. 2024 (HRA, NeurIPS)
- Hu et al. 2021 (LoRA)
- Chen et al. 2020 (SimCLR)
- HNCSE 2024 (Hybrid Contrastive Hard Negatives, arxiv 2411.12156)
- Focal-InfoNCE (arxiv 2310.06918)
- Mechanistically-Guided LoRA for Paraphrase Consistency (arxiv 2603.00148)
- Universal Hopfield Networks (Millidge et al. 2022)
- Frady, Kent, Olshausen, Sommer 2020 (Resonator Networks)
- Frady et al. 2024 (Improved Cleanup FPE, arxiv 2412.00488)
- LlamaIndex linear adapter blog
- VSA as Computing Framework (arxiv 2106.05268)
- Search-Adaptor (ACL 2024) / SMEC (EMNLP 2025) / DIVE (arxiv 2605.20689)

PAWS / HARD-NEGATIVE SOTA (8 additional, partial overlap):
- Zhang, Baldridge, He 2019 (PAWS, NAACL)
- Yang et al. 2019 (PAWS-X, EMNLP)
- Reimers, Gurevych 2019 (Sentence-BERT, EMNLP)
- Yoshida et al. 2022 (Structure-aware Paraphrase ID, Findings)
- Bauer et al. 2025 (Sentence Smith)
- Anon. 2026 (Complexity Conditioning frozen-encoder, arxiv 2606.03244)
- BGE-M3 2024 (arxiv 2402.03216)
- MTEB Muennighoff et al. 2023 (arxiv 2210.07316)

## (h) Closing 3 bullets (Drill Q5 format)

1. **The lit DIRECTLY supports the Skunkworks T2** ("next = learned adapter, NOT readout swap"): Ramsauer 2020 separation theorem + Demircigil 2017 + Hu 2024 spherical-code ceiling + Santos 2025 Fenchel-Young framework form a tight chain showing readout sharpness CANNOT synthesize a separation gap that the embedding geometry does not already provide. The refuse-gate FULL NON_TEST is the canonical empirical fingerprint. **P_deflated = 0.55** for the representational-vs-readout framing (above novel-synthesis cap because it's direct lit, not synthesis); **P_deflated = 0.50** (cap) for the specific recommendation of LoRA-rank-r + InfoNCE + mined hard-neg as the adapter choice.

2. **The cheap decisive test is closed-form whitening + diagnostic, NOT adapter training**: BEFORE proposing a learned adapter, run the ~2-min CPU whitening + IsoScore + Ramsauer-gap diagnostic. If anisotropy index < 0.20 and effective rank > 2*N_targets, the refuse-gate failure is NOT geometry-bound and the SK T2 is wrong direction. If anisotropy index > 0.55 and erank << N_targets, REGIME CONFIRMED — and even then, whitening alone might close the gap without a learned adapter (G alone, P=0.55 if regime is anisotropy-dominated). The learned adapter (C: LoRA r=8-32, ~12-50k params, binding-safe) is the SECOND step, gated on whitening HARD-FAIL. This sequence respects [[feedback-verify-the-referent]] (verify the regime BEFORE prescribing a fix) and [[feedback-measured-bounds-are-method-config-contingent]] (the refuse-gate FULL is one method/config; whitening preprocessing is a different method/config).

3. **Cross-thread synthesis sharpens the substrate-product positioning**: the substrate now has FOUR cert-grade findings forming a single coherent law (READOUT IS A LINEAR-IN-GEOMETRY AMPLIFIER): ARCH-B SPARSITY_NEUTRAL + C1 entmax CERT-GRADE (sharpness lifts capacity when geometry permits — SPREAD regime) + 8a HARD_FAIL (real lever deeper than mechanism-swap) + refuse-gate FULL NON_TEST (no sharpness creates a gap when geometry forbids — DEGENERATE regime). This gives the substrate-product TWO independent ceilings (capacity-ceiling = readout-linearity, addressed by ARCH-B+C1; discrimination-ceiling = geometry, addressed by adapter+whitening). The two are NEVER substitutes. Next drill candidates: **D7 forward-flux sampling** (Tier-1, score=5.0, semiconductor anchor) for basin-to-basin transition diagnostics under the new representational-fix hypothesis; OR **F4 free cumulants Voiculescu kappa_n** (Tier-1, score=5.5, free-probability anchor) for higher-order moments of the embedding geometry that diagnostic indices like anisotropy-mean cannot reach. Both inform whether the adapter recovery composes with the existing free-probability and semiconductor-stochastic-dynamics findings.

---

T2/T3 onboarding-ready. Findings are claim-tier (not experimental cert-grade); per [[feedback-research-can-be-wrong-only-proven-fully-believed-trust-tier]], onboard as queryable-but-NON-load-bearing hypothesis layer. Promotion to PROVEN requires experimental cert-grade run of the whitening diagnostic + (conditional) adapter training cell — both pause-gated and exp_dev-owned (not designed in this drill per [[feedback-no-experiment-design-in-prompts]]).

Next-drill candidate field: **free-probability F4** (kappa_n higher-order moments) for diagnostic-toolkit extension; alternate **semiconductor D7** (forward-flux sampling) for basin-transition dynamics under fixed geometry.
