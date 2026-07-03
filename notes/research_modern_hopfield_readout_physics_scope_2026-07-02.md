# Research: Modern-Hopfield softmax-attention readout — physics/info-theory scope map (5x drill 2/5)

Filed by: research. Trigger: 5x drill 2/5 on Component C readout HF (commit 4cd1d30ba). Domain: physics + information theory only (per refusal-scope instruction — no other domain touched).

## HEADLINE

The observed r@5 collapse (0.050-0.053 at beta={4,8} vs cosine 0.16) is a **sub-critical-beta regime artifact, not a hard physics ceiling**. Ramsauer et al. 2020's argmax sharp-limit theorem bounds *single-pattern one-step-update convergence*, not top-k ranking — softmax attention WEIGHTS preserve cosine's ranking exactly, for any beta>0, by trivial monotonicity. The measured failure implies the readout under test is scoring by the **blended update-output vector** (a smeared multi-pattern mixture at low beta*Delta), not by attention weight, which is exactly Ramsauer's own "metastable state" regime. The Skunkworks attenuation-floor formula and the cell-author's original hard-law claim are BOTH partially right and partially wrong; see verdict below. beta-sweep {50,150,300} is HIGH_EV and cheap; non-equal-norm is a real but unproven SEPARATE lever, not exclusive; the info-theoretic ceiling argument is correct in the long run but does not explain why current output is BELOW cosine.

## 1. Sharp-limit beta regime — computed

Ramsauer et al. (arXiv:2008.02217) Theorem 5 exact bound (verified via full-text PDF extraction, not abstract-only): for separation Delta_i = x_i^T x_i - max_{j!=i} x_i^T x_j, one-step retrieval error epsilon satisfies

    ||x_i_new - x_i|| <= 2(N-1) exp(-beta(Delta_i - 2/N)) M      [Eq. 8-9, valid Delta_i > 2/N]

Solving for target epsilon:

    beta_needed >= ln(2(N-1) M / epsilon) / (Delta_i - 2/N)

(N = number of stored patterns in their notation = our ~100 concepts; M = norm bound; d = ambient dim = our N=2048 — notation collision with the prompt's "N", flagged explicitly here to avoid propagating the clash).

Numerically, with M_patterns=100, target epsilon=0.05, and Delta_cos (gap between top-match cosine and runner-up, NOT max_cos itself) swept 0.02/0.05/0.1:

| Delta_cos | beta_needed |
|---|---|
| 0.02 | 415 |
| 0.05 | 166 |
| 0.10 | 83 |

Separately, the Skunkworks-filed heuristic beta*max_cos/sqrt(N)=O(1) (max_cos, not Delta_cos) gives crossover beta at max_cos={0.1,0.2,0.3}: {452, 226, 151}.

**These two independently-derived criteria land in the same beta range (roughly 80-450) by coincidence of this dataset**, because for k=2% sparse-bipolar vectors (nnz=41 at N=2048), the random-orthogonal noise floor for cosine is ~1/sqrt(41)=0.156 — almost exactly the reported "real content" max_cos~0.1-0.3. That means Delta_cos (true signal) and max_cos (which includes the noise floor) are of comparable order here, so the two formulas numerically agree. **This is dataset-specific, not general** — if the encoder later produces higher max_cos with the SAME thin Delta_cos (e.g. many correlated near-duplicate prototypes), the Skunkworks max_cos/sqrt(N) proxy would overestimate readiness while the true Delta-based criterion stays hard. Recommend re-deriving beta_needed from measured Delta_cos (top1-minus-runner-up gap), not max_cos, for any future config change.

Verdict on (1): beta in {150, 300} is the physically-justified crossover band for THIS config; {50} is sub-critical by both criteria; {1000} is comfortably supra-critical (O(1)-6x per the heuristic, and >> beta_needed at any plausible Delta_cos down to 0.01).

## 2. r@5 vs r@1 sharp-limit divergence — proven, not just asserted

Two independent lit-scans confirm: **no paper (Ramsauer 2020 or follow-ups) states or requires a top-k order-preservation corollary** — the theorem's proof machinery (Jacobian contraction bound) is about convergence of the ITERATED UPDATE to a single fixed point, silent on ranking.

However a trivial, unpublished-because-elementary corollary DOES hold: attention weights p_i = exp(beta*s_i)/Z are a strictly monotone (exp) transform of s_i for a FIXED query row, so **ranking stored items BY ATTENTION WEIGHT reproduces cosine's ranking exactly, for every beta > 0** (Z is a constant across the row, cancels in the ordering comparison). This means: if the readout under test ranks candidates by p_i directly, r@5 CANNOT differ from cosine's r@5 at ANY beta — a hard mathematical fact, not an approximation.

Therefore the observed r@5=0.05 << cosine=0.16 is **diagnostic**: it proves the implementation is NOT ranking by p_i. The only readout consistent with Ramsauer's own framework that gives a DIFFERENT ranking is scoring by the **one-step update output** xi_new = Sum_i p_i * x_i (the weighted SUPERPOSITION of all stored patterns) and then comparing xi_new against the store. At beta below the Section-1 crossover (beta*Delta_cos << ln(M)), this sum is dominated by no single pattern — it is Ramsauer's own "metastable state" (his Section on generalization/robustness), a smeared average over many prototypes. A smeared average vector has LOW cosine similarity to any single stored pattern (it is not even validly IN the equal-norm shell), which mechanically produces poor top-5 recall against the true single target. This is the concrete mechanism behind the Skunkworks attenuation-floor observation — not a new law, a specific consequence of running below the concentration crossover while scoring by the mixed OUTPUT vector instead of the raw weight vector.

Could softmax beat cosine on r@5 in some regime? Yes, in principle, at INTERMEDIATE beta, IF the true retrieval targets form "metastable clusters" of near-duplicate/paraphrase prototypes (plausible for the WordNet-like task's 4-sentences-per-concept structure) — blending over cluster-mates can denoise a noisy query, which is exactly the generalization mechanism Ramsauer et al. present as a FEATURE of modern Hopfield, not a bug. This is untested here and is a genuine, falsifiable, different-from-attenuation-floor hypothesis (see falsifiable predictions).

## 3. Non-equal-norm break

Ramsauer's exponential-capacity Theorem 3 explicitly requires patterns placed on a fixed-radius sphere (M = K*sqrt(d-1)); the clean argmax-reduction picture assumes this equal-norm placement. With unequal norms, the raw dot product score x_i^T xi (NOT cosine) picks up an additive/multiplicative bias toward larger-norm patterns independent of true directional similarity — this is the standard reason production Transformer attention normalizes queries/keys (removing exactly this magnitude confound). Two sub-cases:

- If magnitude is UNCORRELATED (or anti-correlated) with true relevance (e.g. noise/outlier prototypes with inflated norm): unequal-norm storage HURTS r@5 relative to cosine, by swamping the softmax with magnitude-driven false positives.
- If magnitude is a genuine relevance PRIOR (e.g. norm scaled by training-sentence frequency/centrality of the concept, so common/canonical concepts get larger norm): unequal-norm storage gives softmax attention a real EXTRA sufficient statistic unavailable to plain cosine (which ignores magnitude by construction) — this COULD exceed cosine's r@5 ceiling, because it is no longer a monotone transform of the SAME statistic (see Section 4).

This is NOT decidable from physics alone — it is an empirical question about whether the specific magnitude-assignment scheme used correlates with true relevance. Ramsauer's theorem gives no guarantee either way once norms vary; his clean sharp-limit proof simply does not apply outside the equal-radius-sphere premise.

## 4. Info-theoretic ceiling

Classical results (verified, both citable):
- McEliece-Posner-Rodemich-Venkatesh 1987 (IEEE Trans. IT 33(4)): Hebbian-stored Hopfield network capacity M <= N/(2 ln N) (weak/near-all-recall) or N/(4 ln N) (strong/all-pattern-stable) — a union-bound/large-deviations argument over Gaussian-approximated crosstalk.
- Chou 1989 (Kanerva SDM, IEEE Trans. IT 35(3)): the CLEANEST literal Shannon-capacity statement for associative memory — sphere-packing bound <= 1 - h2(delta) bits/dim, achieved at optimal SDM parameters.
- Krotov-Hopfield 2016 / Demircigil et al. 2017: polynomial interaction F(x)=x^n gives capacity ~N^(n-1); exponential F(x)=exp(x) (the modern-Hopfield / softmax limit) gives capacity ~2^(N/2) — exponential in dimension, matching Ramsauer's Theorem 3 regime.
- Classical Hopfield-type memories store only O(N^2/ln N) bits vs the Shannon-achievable N^2 bits for N^2 "synapses" for RANDOM patterns — i.e. operate far below channel capacity; structured (non-random, correlated) patterns close much of that gap (Salavati/Karbasi-line results, arXiv:1301.6917, 1302.1156).

Fixed-encoder ceiling (own derivation, cross-checked by lit-scan, standard detection theory — Neyman-Pearson/Fisher factorization, uncited directly in the associative-memory literature but not novel): for a FIXED encoder producing a fixed joint distribution of (match, interference) similarity scores, that similarity score is a sufficient statistic with a FIXED ROC curve; recall@k is a functional of that ROC. **Any readout that is a strictly monotone function of the SAME statistic, applied per-query-row (cosine, softmax-of-cosine at any beta, any rescaling), cannot exceed the ROC-determined recall ceiling.** A readout CAN exceed it only by using a genuinely different/additional statistic (e.g. magnitude, from Section 3, or a multi-hop/iterative representation that is not a static function of the original pairwise score).

For the specific task (100 concepts, N=2048, k=2% sparse, ~4 sentences/concept): raw information-theoretic slot capacity is NOT the bottleneck — M/N = 100/2048 = 0.049, far below any of the capacity ceilings above (Hopfield strong-recall ceiling alone is N/(4 ln N) ~ 2048/(4*7.6) ~ 67 patterns at N=2048's own ln(N); modern/exponential capacity is orders larger still). The bottleneck is that the ENCODER's induced match-cosine (0.1-0.3) sits barely above the ~0.156 random-orthogonal noise floor for this sparsity/dimension — i.e. the sufficient statistic itself has a weak ROC, not that too many patterns are crammed into too few dimensions. This is an encoder-design finding, not a capacity-exhaustion finding.

## Chain-of-reasoning verdict

**(IV) Different verdict — hybrid of (I) and a corrected (III), with (II) refuted as stated:**

- **(I) HIGH_EV, confirmed by independent derivation.** beta-sweep at {150, 300} (and include {1000} as a supra-critical control, {50} as a sub-critical control already in hand) directly tests the Section-1/Section-2 mechanism: if r@5 recovers toward ~0.16 (cosine parity) as beta crosses the ~150-450 band, that PROVES the current HF is a sub-critical-beta blended-output artifact, not a hard ceiling. If r@5 stays flat/near-zero even at beta=1000, the mechanism diagnosis is wrong and a genuinely different bug is present (e.g. implementation bug in how attention weights are aggregated, or the readout literally isn't using cosine-scaled logits) — cheap and decisive either way.
- **(II) Refuted as stated ("only").** Non-equal-norm is A path to possibly exceeding cosine (Section 3), not the ONLY path — the beta-sweep in (I) is a distinct mechanism that operates even at equal norm, and is expected to at minimum RECOVER cosine parity (not exceed it) once beta clears the crossover, per the trivial monotonicity argument in Section 2. Non-equal-norm's benefit, unlike (I)'s, is NOT guaranteed by physics — it is conditional on magnitude actually correlating with relevance, an unproven empirical premise.
- **(III) Correct in the long run, overclaimed in the near term.** The fixed-encoder/Neyman-Pearson ceiling argument (Section 4) IS correct: no same-statistic monotone readout can exceed cosine's ROC-determined ceiling, and the encoder's thin Delta_cos (barely above noise floor) is indeed the load-bearing long-run lever for raising that ceiling. But "no readout swap CAN help" overclaims: the CURRENT gap (0.05 vs cosine's 0.16) is BELOW the ceiling, not at it — a same-statistic readout (raw attention weight ranking, or supra-critical beta) is expected to RECOVER to ~0.16, which is a real, actionable, near-term win before any encoder work lands. Sequencing: fix the sub-critical-beta / wrong-scoring-target regime first (cheap, (I)), THEN invest in encoder Delta_cos improvement for ceiling-raising (Section 4's real long-run lever). Non-equal-norm storage (Section 3) is a parallel, unproven, higher-risk bet on a genuinely new statistic — worth a small probe but not a substitute for (I).

## Falsifiable predictions

**HARD-PASS** (mechanism confirmed): at beta in {150, 300}, r@5 (measured by ranking on attention WEIGHT, not blended-output-vector similarity) recovers to >= 0.14 (within ~90% of cosine's 0.16), AND at beta=50 r@5 stays near the already-measured ~0.05 floor, AND at beta=1000 r@5 is >= 0.15 (near-exact cosine match, consistent with the Section-2 monotonicity proof for weight-ranked scoring).

**HARD-FAIL** (mechanism wrong / new bug): r@5 stays below 0.08 at ALL of beta in {150, 300, 1000} when scored by attention weight (not blended vector) — this falsifies the sub-critical-beta diagnosis entirely and implicates either (a) an implementation bug unrelated to beta, or (b) Delta_cos is far smaller than the 0.02-0.1 assumed range (i.e. real content's top match and runner-up are nearly indistinguishable, Delta_cos < 0.01, requiring beta > 1000 to concentrate — itself a falsifiable, cheaply-checkable measurement: compute the ACTUAL Delta_cos histogram from the stored real-content prototypes directly, which should be done as a zero-cost diagnostic BEFORE the beta-sweep, since it directly predicts which beta the sweep needs to reach).

**Separate falsifiable prediction on Section 2's metastable-blend hypothesis:** if the SAME beta-sweep is scored by blended-output-vector similarity (xi_new vs store) instead of attention weight, r@5 should be markedly WORSE than weight-ranked scoring at low-to-mid beta (confirming the blend-vs-weight distinction is the mechanism) and converge to the SAME r@5 as weight-ranking once beta is supra-critical (both should ~match cosine at beta=1000, since the blend collapses onto a single pattern at high beta by Theorem 5). If blend-scored and weight-scored r@5 are statistically indistinguishable at ALL beta tested, that refutes the blend-vs-weight mechanism distinction and points to a different explanation.

**HARD-FAIL for the metastable-cluster-denoising upside hypothesis (Section 2, "could softmax beat cosine"):** if the WordNet-like task's 4-sentences-per-concept do NOT cluster tightly in cosine space (i.e., intra-concept sentence-pair cosine is not markedly higher than inter-concept cosine), the denoising-via-blending mechanism has no substrate to act on and should NOT be expected to produce a softmax-beats-cosine regime at any beta; this is a cheap pre-check (compute intra- vs inter-concept cosine before running any blend-scored r@5 test).

## Cross-thread synthesis

Confirms and sharpens two prior threads:
- `modern-hopfield` field (tier-1, fruit-bearing per role-contract field table) — this drill adds a NEW adjacent angle: the weight-ranking-vs-blend-output-ranking distinction, which was not previously in the meta-map's Part 3 rows for this field. Recommend queuing this as a Trigger-C adjacency-cascade candidate.
- Cross-checks the "attenuation floor" MB_STANDARD Skunkworks filed: the floor is REAL as measured, but the filed formula (beta*max_cos/sqrt(N)) is a coincidental proxy for THIS dataset's parameters, not the general physical criterion (which is beta >= ln(2M/eps)/Delta_cos, Delta_cos being the top1-runner-up gap, not max_cos). Recommend Skunkworks re-file the MB_STANDARD with Delta_cos as the primary variable to avoid mis-generalizing to future encoder configs.
- The cell-author's original `PHYSICS_LAW_cannot_exceed_cosine_argmax` demotion was correct to demote (Section 2's weight-ranking proof shows softmax literally cannot do WORSE than cosine when scored correctly — so "cannot exceed" as an absolute law is also wrong in the other direction: under the right scoring convention it is identically equal, not merely bounded above).

## Substrate-product implications

This is a readout-configuration question for the concept-encoder Component C pipeline, not a publication-facing result. Immediate action: (a) run the zero-cost Delta_cos histogram diagnostic on the actual stored prototypes before dispatching the beta-sweep (predicts which beta band actually applies, per HARD-FAIL note above); (b) dispatch the beta={150,300,1000} sweep scored BOTH ways (attention weight vs blended-output vector) to cleanly separate the two falsifiable predictions in one smoke-scale run; (c) treat non-equal-norm storage as a separate, lower-priority, higher-uncertainty probe pending (a)/(b) results, not a required parallel track. Direct exp_dev / cell-author to this note for anchor design — no separate hand-off file per current ferry-deprecation discipline.

## Citations (verified count: 7)

1. Ramsauer et al. 2020, "Hopfield Networks is All You Need," arXiv:2008.02217 (full-text PDF-extracted, Theorem 3/4/5 and Eq. 5/8/9 verified directly, not abstract-only).
2. McEliece, Posner, Rodemich, Venkatesh 1987, "The Capacity of the Hopfield Associative Memory," IEEE Trans. Information Theory 33(4):461-482.
3. Krotov & Hopfield 2016, "Dense Associative Memory for Pattern Recognition," NeurIPS.
4. Demircigil, Heusel, Lowe, Upgang, Vermet 2017, "On a Model of Associative Memory with Huge Storage Capacity," J. Stat. Phys. 168:288-299.
5. Chou 1989, "The Capacity of the Kanerva Associative Memory," IEEE Trans. Information Theory 35(3):281-298.
6. Barnfield, Kim, Nichani, Lee, Lu 2026, "Sharp Capacity Thresholds in Linear Associative Memory: From Winner-Take-All to Listwise Retrieval," arXiv:2605.05189 (top-1 vs top-k capacity gap for LINEAR memory, adjacent not identical to our softmax question).
7. Salavati/Karbasi-line, "Maximum Likelihood Associative Memories," arXiv:1301.6917, and non-binary exponential-capacity follow-up arXiv:1302.1156 (structured-vs-random-pattern channel-capacity gap).

Uncited-but-standard (own derivation, cross-checked, not attributable to a specific paper): monotonicity-preserves-ranking argument (Section 2/4), Neyman-Pearson fixed-sufficient-statistic ceiling (Section 4) — classical detection theory (cf. Kay, *Fundamentals of Statistical Signal Processing Vol. II*, 1998), not associative-memory-specific literature.

## Calibration

Per lit-scan calibration penalty: this is a well-precedented regime (Ramsauer 2020 is directly on-point, not novel synthesis) for Sections 1-2 — P(mechanism diagnosis correct) = 0.65 after deflation (raw confidence ~0.85, deflated 0.20 for the leap from "theorem says X" to "therefore OUR implementation does Y" which is unverified without running the sweep). Section 3 (non-equal-norm) is genuinely uncharted for this substrate — capped at P=0.45 (novel-synthesis cap 0.50, minus small deflation for the real uncertainty in which sub-case applies). Section 4's encoder-is-bottleneck claim: P=0.55 after deflation (fairly well-supported by the noise-floor coincidence but not yet directly measured on real content's actual Delta_cos histogram — that measurement is itself in the HARD-FAIL prediction as a prerequisite).
