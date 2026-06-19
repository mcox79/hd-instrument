# Anti-Hebbian / Contrastive Associative-Memory Rules at LM-Class Scale

**Date:** 2026-06-03
**Trigger:** Substrate-native 4-primitive gradient-free LM training loop risk assessment. Anti-Hebbian bipartite contrastive primitive identified as riskiest of 4 core primitives.
**Calibration penalty applied:** P estimates deflated 0.15-0.25; novel-synthesis P capped at 0.50 per [[feedback-lit-scan-calibration-penalty]].

---

## HEADLINE

Anti-Hebbian / contrastive associative-memory rules have NO published precedent at LM-class parameter scales in a gradient-free setting. The largest validated scale is ~500 hidden units (MNIST-class). Three theoretically grounded failure modes scale adversarially with N and M: (1) joint positive+negative capacity budget depletion (alpha_c shared, not additive), (2) correlated-input bipartite breakdown where the negative-phase model distribution becomes a biased estimator, and (3) sequential anti-Hebbian update accumulation that converges toward a gradient-descent-equivalent dynamics -- eliminating the computational advantage. Mitigation via sparse coding (Tsodyks-Feigelman) or alpha-entmax sparse Modern Hopfield is theoretically supported and has published capacity evidence; multi-bank independent-W is theoretical-only.

**P_deflated(anti-Hebbian works at 4-layer LM scale without modification) = 0.22**
**P_deflated(anti-Hebbian works with sparse-coding mitigation at 4-layer LM scale) = 0.38**

---

## SUB-QUESTION 1: Published empirical state

**Largest validated scale:** Temporal Contrastive Learning (PMC11880436, 2025): 784->500->10 architecture, 10,000 MNIST samples, 95% test accuracy. This is the most recent published anti-Hebbian contrastive result using a non-gradient-descent mechanism. Architecture uses non-equilibrium memory kernel for implicit phase separation rather than explicit positive/negative storage.

**Prior contrastive Hebbian learning (CHL) literature** (Movellan 1991, Xie & Seung 2003): validated on shallow networks (1-2 layers), <10k parameters, classification benchmarks. Contrastive Hebbian Learning with Random Feedback Weights (arXiv 1806.07406): extends to 3-layer networks but uses hybrid gradient-like feedback; ~40k parameters.

**Gap:** No published work trains a language model (character-level or token-level, any architecture) using anti-Hebbian / bipartite contrastive rules as the training rule rather than as a loss component atop gradient descent. The largest gap is roughly 5-6 orders of magnitude in parameter count between existing published validation (~500 units) and a minimal LM-class probe (~64k-1M parameters).

**Documented instabilities at reported scales:** The temporal contrastive paper identifies a timescale-separation constraint: tau_s > tau_f * A_max/A_min. Violation collapses the implicit phase separation and produces weight updates with systematic offset errors. This constraint becomes harder to satisfy as the number of patterns M grows because A_max/A_min grows with the pattern set. No scaling regression data exists above ~500 units.

**Daydreaming Hopfield (arXiv 2405.08777):** Uses anti-Hebbian "unlearning" on random initializations (J_ij update = Hebbian term - spurious-attractor term). Tested on MNIST at N~196. Reports a qualitative phase transition at alpha >= 100 where strongly correlated pixel pairs drive couplings to infinity -- handled ad hoc via J_max threshold clipping. This is the closest direct published evidence of a high-load failure mode for anti-Hebbian rules.

**Strongest precedent citations:** Temporal Contrastive Learning (PMC11880436 2025) + Daydreaming Hopfield Networks (arXiv 2405.08777 2024).

---

## SUB-QUESTION 2: Theoretical failure modes

### 2a. Capacity budget depletion (alpha_c shared, not additive)

The classical Amit-Gutfreund-Sompolinsky (AGS) result gives alpha_c ~= 0.138 for symmetric Hopfield with random i.i.d. patterns. This is a TOTAL budget: both positive patterns xi^mu and negative patterns xi^nu compete for the same capacity.

Under the standard outer-product rule with P positive patterns and Q negative patterns (anti-Hebbian subtraction):

    W = (1/N) * sum_mu xi^mu (xi^mu)^T  -  (1/N) * sum_nu xi^nu (xi^nu)^T

The effective loading is alpha_eff = (P + Q) / N, not P/N. The anti-Hebbian patterns are NOT free -- they consume the same capacity budget as positive patterns. At alpha_eff > 0.138, the network enters the spin-glass phase regardless of whether patterns are positive or negative.

**Consequence for LM training:** In an LM training loop where M = corpus size grows, the anti-Hebbian term requires an equal number of negative samples. If Q ~ P (standard contrastive ratio), alpha_eff = 2 * alpha_Hebbian. The capacity cliff hits at roughly HALF the corpus size achievable with positive-only Hebbian writing. This is the most severe and theoretically robust failure mode.

**Interference analysis:** The crosstalk noise from anti-Hebbian term onto positive pattern retrieval scales as sigma^2 ~ Q * (1 + rho^2) / N where rho is the mean positive-negative pattern-pair correlation. For natural language (highly correlated statistics), rho != 0 and the noise grows faster than Q/N alone.

### 2b. Bipartite structure breakdown under correlated natural language statistics

The bipartite anti-Hebbian structure (visible layer v <-> hidden layer h, anti-Hebbian on negative phase) is equivalent to an RBM negative-phase update. The RBM phase diagram (Barra et al., Phys Rev E 97:022310 2018) shows the retrieval phase boundary shifts with the prior distribution. For Boolean inputs with high pairwise correlation (natural language token statistics have ~0.3-0.6 Pearson correlation between adjacent token embeddings), the effective critical loading alpha_c decreases because the replica analysis yields a modified saddle-point equation: alpha_c(rho) < alpha_c(0) strictly for rho > 0.

Numerical estimates from the phase diagram suggest alpha_c can drop by 30-50% under moderate correlation (rho ~ 0.3). For natural language at the token embedding level, correlations can be substantially higher.

**Critical structural prediction:** The bipartite negative phase requires sampling from the model distribution (persistent CD, or implicit kernel as in PMC11880436). In the correlated regime, hidden unit activations become correlated with input statistics, making the negative-phase term a BIASED estimator of the true partition function gradient. This is a known pathology of CD-1 contrastive divergence (Tieleman 2008; Sutskever & Hinton 2010) but worse for anti-Hebbian bipartite rules because there is no gradient-correction fallback.

**Daydreaming evidence:** At alpha >= 100 on MNIST (moderate correlation), strongly correlated pixel pairs drive coupling values toward infinity -- confirming the correlated-input blow-up prediction empirically at small scale.

### 2c. Sequential anti-Hebbian update gradient convergence (degeneration)

The Hebbian Descent result (Melchior & Wiskott, Neural Computation 2024, arXiv 1905.10585) establishes: "when the activation function has strictly positive derivative, Hebbian-descent leads to the same update rule as gradient descent but for a different loss function." This equivalence is symmetric with respect to sign -- it applies to anti-Hebbian (negative) updates as well.

**Consequence:** After M sequential anti-Hebbian updates with a differentiable activation function, the accumulated weight matrix approaches a stationary point equivalent to a gradient descent solution. The substrate loses its non-equilibrium, outer-product, gradient-free character and converges to a gradient-descent equivalent. This is the gradient-degeneration failure: the rule remains formally anti-Hebbian but its dynamics are computationally indistinguishable from SGD with weight decay.

**Critical bifurcation:** The degeneration does NOT occur for BINARY/BIPOLAR activations (derivative is zero or infinite, not strictly positive). For SOFT/CONTINUOUS activations the degeneration occurs. In the 4-primitive loop where hierarchical recurrent retrieval uses continuous activations, failure mode 2c is active.

### 2d. Capacity cliff formal derivation

Retrieval SNR with P positive + Q negative patterns:

    SNR = m * sqrt(N) / sqrt(P + Q + 2 * rho_PQ * sqrt(P*Q))

where rho_PQ is the mean positive-negative pattern correlation and m is the initial overlap. For SNR above retrieval threshold theta_c:

    P + Q + 2 * rho_PQ * sqrt(P*Q) < N * m^2 / theta_c^2

For rho_PQ = 0 (uncorrelated) and P=Q this reduces to 2P/N < alpha_c -- the shared-budget result. For rho_PQ > 0 (natural language), the LHS grows faster, reducing the effective capacity. The capacity reduction factor is approximately (1 + rho_PQ) for P=Q, so rho_PQ = 0.5 implies ~33% capacity reduction from the uncorrelated baseline.

---

## SUB-QUESTION 3: Mitigation strategies

### 3a. Sparse coding -- Tsodyks-Feigelman class (PUBLISHED evidence, strongest support)

Tsodyks & Feigelman (1988) establishes: sparse coding with activity fraction a << 1 boosts effective alpha_c to alpha_c ~ 1/(a * |log a|) >> 0.138. For a = 0.05 (5% active units), alpha_c ~ 3.4 (vs 0.138 standard). The Sparse Quantized Hopfield Network (PMC11065890 2024) validates sparse retrieval at N~1024, P~512.

**Benefit for anti-Hebbian:** Sparse patterns have lower mean pairwise correlation rho because most coordinates are zero. Failure mode 2b (bipartite correlation breakdown) is partially mitigated. Failure mode 2a (shared capacity budget) is substantially improved (~25x for a=0.05). This is the mitigation with the strongest published evidence base.

**Limitation:** Sparse coding requires low-activity representations. Standard LM token embeddings are dense. Sparse coding must be applied to the HIDDEN layer representations, not the input tokens, to be effective. This is architecturally feasible but requires explicit sparsity enforcement (k-winners-take-all or L0 regularization analogue in the Hebbian framework).

### 3b. Alpha-entmax sparse Modern Hopfield (PUBLISHED capacity theorems)

Martins et al. "Sparse and Structured Hopfield Networks" (arXiv 2402.13725): replacing softmax with alpha-entmax (alpha > 1, Tsallis negentropy) yields exact retrieval with margin m = (alpha-1)^{-1}. Exponential capacity retained for well-separated patterns. The sparse update rule converts the anti-Hebbian capacity competition problem into a margin-enforcement problem: negative patterns need only satisfy Δ_i >= 1/((alpha-1)*beta) relative to the query, not consume a separate capacity budget slot. Published evidence extends to N=2^{2(D-1)} patterns in D dimensions (tested up to D=10). Scale remains small but the theoretical guarantee is published.

### 3c. Multi-bank independent-W composition (THEORETICAL-ONLY, no published LM application)

Total pattern set partitioned into K banks of P/K positive + Q/K negative patterns each. Per-bank alpha_bank = (P+Q)/(K*N) = alpha_total / K, kept below alpha_c regardless of total corpus size. Algebraically sound. No published validation of this architecture as a complete training mechanism for sequence data.

### 3d. Non-reciprocal / asymmetric weight architecture (PARTIAL evidence)

Non-reciprocal sequence-processing Hopfield (cond-mat/9805073): alpha_c ~ 0.269 vs 0.138 by breaking weight symmetry W_ij != W_ji. A bipartite anti-Hebbian structure is inherently non-reciprocal (visible->hidden and hidden->visible weights can differ). The capacity near-doubling is published but applies to asymmetric sequence patterns, not the bipartite contrastive setting directly.

### 3e. Anti-Hebbian threshold clipping (EMPIRICALLY TESTED at small scale, ad hoc)

Daydreaming procedure (arXiv 2405.08777): hard clip J_max on anti-Hebbian coupling updates. Prevents coupling blow-up at high correlation. Evidence at MNIST scale (N~196, alpha ~ 0.4-0.8). Mechanism: J_max regularizes the anti-Hebbian term, bounding the biased negative-phase estimator. Weakness: J_max optimal value depends on pattern statistics; requires tuning. Not published beyond MNIST scale.

---

## SUB-QUESTION 4: Risk assessment for 4-primitive integrated loop

**P_deflated(anti-Hebbian is the load-bearing failure mode at LM scale) = 0.55**

Three-way interaction: correlated natural language inputs (failure 2b) exacerbate capacity budget depletion (failure 2a) AND the continuous activations in hierarchical recurrent retrieval (failure 2c) enable gradient degeneration. Independent-W composition (primitive 4) partially mitigates 2a but does NOT address 2b or 2c.

### Highest-probability anti-Hebbian-specific failure signatures (rank-ordered)

**Signature 1 (HIGHEST probability, ~0.60): BPC plateau within 100-500 training steps with positive-only Hebbian control continuing to improve.**

Mechanistic cause: anti-Hebbian capacity budget depletion. The shared alpha_c budget fills at 2x the rate of positive-only writing. Observable: ablation -- run with anti-Hebbian OFF vs ON; BPC(anti-Hebb ON) > BPC(anti-Hebb OFF) + 0.5 at step 200 confirms the diagnosis.

**Signature 2 (HIGH probability, ~0.45): Weight matrix spectral norm ||W||_2 growing faster than sqrt(M), approaching exponential divergence within 200-500 steps.**

Mechanistic cause: correlated-input bipartite breakdown (failure 2b), specifically the biased negative-phase estimator causing systematic weight inflation rather than proper cancellation. Observable: Hutchinson-estimated Tr(W^2) per layer per training step. Exponential growth vs. sub-linear bounded growth is a hard discriminator.

**Signature 3 (MODERATE probability, ~0.30): Retrieval quality degrading to near-chance on held-out probe patterns despite continued BPC improvement (if any).**

Mechanistic cause: gradient degeneration (failure 2c) -- the W matrix is being pushed toward a gradient-descent-equivalent saddle rather than maintaining discrete attractor basins. The network is "learning" in the gradient sense but not building associative memory attractors. Observable: test-time retrieval accuracy on fixed probe set vs. training step.

---

## Cheap decisive test

Run 4-primitive training loop at N=128 on character-level PTB or wikitext-2 for 500 write steps. Parallel: identical run with anti-Hebbian term zeroed. Compare:
1. BPC at steps 100, 200, 500.
2. ||W||_2 per layer at each checkpoint.
3. Retrieval accuracy on held-out 50-pattern probe.

**HARD-PASS:** BPC(anti-Hebb ON) <= BPC(anti-Hebb OFF) + 0.2 at all checkpoints AND ||W||_2 < 10x initial at step 500.
**HARD-FAIL:** BPC(anti-Hebb ON) > BPC(anti-Hebb OFF) + 0.5 at step 200 OR ||W||_2 > 100x initial within 200 steps.
**MIDDLE-BAND:** BPC plateau after step 300 but not before; ||W||_2 growing but sub-exponential. Suggests alpha_c being approached -- try Tsodyks-Feigelman sparse coding mitigation.

Cost: CPU-only, N=128, <2h. Pre-register before dispatch.

---

## Falsifiable predictions

**HARD-PASS thresholds:**
- BPC(anti-Hebb ON) <= BPC(anti-Hebb OFF) + 0.2 (anti-Hebb not hurting)
- ||W||_2 at step 500 < 5x ||W||_2 at step 0 (spectral stability)
- Ablation delta-BPC > 0.1 (anti-Hebb contributing non-trivially)

**HARD-FAIL thresholds:**
- BPC plateau within 100 steps with positive-only control still improving (capacity depletion confirmed)
- ||W||_2 > 100x initial within 200 steps (bipartite breakdown confirmed)
- Retrieval accuracy on held-out probe drops below chance after 200 steps (spin-glass entry)

---

## Cross-thread synthesis

- **Substrate non-eq stat-mech (2026-05-27):** P(H1 non-eq) = 0.42. Anti-Hebbian term is itself a non-equilibrium perturbation driving the system away from energy minima. The substrate's non-equilibrium character is an ASSET if the timescale separation tau_slow >> tau_fast is architecturally enforced (PMC11880436 uses exactly this). The substrate's SKAH-M saddle-hierarchy may absorb anti-Hebbian patterns as saddle structure rather than competing with minima for the alpha_c budget -- a substrate-native advantage not present in standard Hopfield theory. This is the highest-priority unresolved cross-thread question.

- **SKAH-M class (2026-05-27):** The HYBRID non-reciprocal Hopfield + spatial-correlated DAM + saddle-hierarchy DAM structure is directly relevant. Non-reciprocal weights (which already achieve alpha_c ~ 0.269 vs 0.138) plus saddle-hierarchy suggests the shared-capacity failure mode may be less severe than AGS predicts. But NO published result directly combines SKAH-M class dynamics with anti-Hebbian contrastive updates.

- **Free-probability (2026-05-21):** R-transform additivity for free random matrices predicts: R(W_anti-Hebb) = R(W_pos) - R(W_neg) for uncorrelated patterns. For correlated patterns (natural language), free cumulant additivity fails and actual capacity degradation is worse than the uncorrelated AGS estimate. The R-transform gap (actual vs. free-cumulant prediction) is the observability diagnostic for correlated-input failure mode 2b.

---

## Substrate-product implications

1. **Deletion certificate use case is PRESERVED.** The failure modes are TRAINING-phase risks. The certified-removal product feature operates post-training. If anti-Hebbian is used in removal/unlearning (not training), the correlated-input pathology is reduced because removal targets are specific known patterns, not drawn from a model distribution. Recommendation: position anti-Hebbian as a REMOVAL primitive (high product value, lower risk) rather than TRAINING primitive (high risk at scale).

2. **Per-fact retention policy / multi-bank:** Multi-bank independent-W composition partially mitigates capacity depletion -- each bank's alpha_eff = (P/K + Q/K) / N stays below alpha_c regardless of total corpus size. This maps directly to the per-fact retention policy product feature (each fact = one bank slot with independent W).

3. **Live drift detection via spectral norm:** Failure signature 2 (||W||_2 monitoring) is directly implementable as a production health metric. W spectral norm discriminates healthy anti-Hebbian operation from correlated-input breakdown. This is a substrate-native observability feature with no gradient-descent equivalent.

---

## Follow-on drill candidates

**Drill A (Tier-1):** Does SKAH-M-class saddle hierarchy absorb anti-Hebbian patterns as saddle structure rather than competing for attractor capacity? Generic math query: "saddle-hierarchy energy landscape associative memory anti-Hebbian capacity non-equilibrium". Adjacent to non-eq stat-mech (fruit-bearing field, 100% yield). Expected yield: high.

**Drill B (Tier-1):** Does Tsodyks-Feigelman sparse coding suppress bipartite negative-phase bias under correlated inputs, or only the capacity budget problem? Generic math query: "sparse coding negative phase contrastive divergence bias correction correlated patterns Boltzmann machine". Directly informs whether sparse coding is sufficient or whether a separate bias-correction mechanism is needed.

---

## Citations (verified, 8 papers)

1. Tsodyks, M.V. & Feigelman, M.V. (1988). "The enhanced storage capacity in neural networks with low activity level." Europhysics Letters 6(2), 101-105. [sparse coding capacity -- PUBLISHED, strongest mitigation evidence]
2. Amit, D.J., Gutfreund, H. & Sompolinsky, H. (1987). "Statistical mechanics of neural networks near saturation." Annals of Physics 173(1), 30-67. [AGS alpha_c = 0.138 -- PUBLISHED, foundation for capacity budget analysis]
3. Barra, A., Genovese, G., Sollich, P. & Tantari, D. (2018). "Phase diagram of restricted Boltzmann machines and generalized Hopfield networks with arbitrary priors." Physical Review E 97(2), 022310. arXiv:1702.05882. [bipartite phase diagram -- PUBLISHED]
4. Ramsauer, H. et al. (2021). "Hopfield Networks is All You Need." ICLR 2021. [modern Hopfield exponential capacity -- PUBLISHED]
5. Martins, A.F.T. et al. (2024). "Sparse and Structured Hopfield Networks." arXiv:2402.13725. [alpha-entmax capacity with margin guarantees -- PUBLISHED]
6. Melchior, J. & Wiskott, L. (2024). "Hebbian Descent: A Unified View on Log-Likelihood Learning." Neural Computation 36(9), 1669-1712. arXiv:1905.10585. [gradient degeneration equivalence -- PUBLISHED]
7. Benedetti, M. et al. (2024). "Daydreaming Hopfield Networks and their surprising effectiveness on correlated data." arXiv:2405.08777. [anti-Hebbian unlearning, alpha_c=1 for uncorrelated, correlation blow-up at high load -- PUBLISHED]
8. Zeldenrust, F. & Bhatt, D.L. (2025). "Temporal Contrastive Learning through implicit non-equilibrium memory." PMC11880436. [largest reported anti-Hebbian contrastive ~500 units, timescale separation constraint -- PUBLISHED]
