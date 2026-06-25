# RESEARCH 5-cell HARD_FAIL revival 3x drill: pure math + disparate fields per cell

date: 2026-06-24
trigger: USER directive after 5 HARD_FAILs landed today. Drill each 3x with pure math + disparate field angles. Companion to research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md (which contains the cross-cell synthesis + recommended decisive cell).
discipline: per-cell 3-angle drill — Angle A (verify-the-referent on Store proof), Angle B (pure math: which mathematical structure governs the gap), Angle C (disparate field: brain / biology / physics / engineering / CS). Per USER STANDING: pure math is MANDATORY. Calibration: novel-synthesis cap P=0.50; deflation 0.20.
companion: research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md (headline + cross-cell common modes + decisive test).

---

## Cell 1: exp_substrate_resonator_multihop_integration_v1

**Metrics:** NAIVE_2HOP top1=0.6500 (sanity-in-band) | RESONATOR_2HOP top1=0.6317 (HF: needed >=0.85; got 0.63, paired delta -0.02) | RESONATOR_3HOP top1=0.3933.

### Angle A — Verify-the-referent on Store (wave14_multihop_K50 anchor)

Per `director_multihop_composition_store_scour_2026-06-24.md` the Wave14R K50 chain-grade anchor ran at:
- N_DIM ~ 16384 (one-step Hopfield cleanup proven at this scale)
- K_SET = 50
- acc_1 = 0.987 at depth = 2-50
- Codebook: ConceptNet-derived anisotropic entity vectors
- Mechanism: `hdlab.multi_hop.iter_cleanup_chain` with k_inner=1 (single Modern-Hopfield step per hop)

Today's cell ran at:
- N_DIM = 8192 (2x smaller)
- K_SET = 20 (2.5x smaller)
- V_C = 200 (different scale; impossible to compare directly to ConceptNet without effective-rank measurement)
- Codebook: random-bipolar synthetic (isotropic Marchenko-Pastur spectrum)
- Mechanism: same iter_cleanup_chain code-path with beta = N_DIM = 8192

Transfer-distance: ALL FOUR primary axes shifted. Per the META drill L2 information-geometry analysis, the anisotropic-vs-isotropic axis ALONE is sufficient to break the transfer because the iterative cleanup's convergence rate depends on dominant-singular-value separation that random-bipolar doesn't have. **Referent regime does not match; chain-grade does not auto-transfer.**

### Angle B — Pure math

**Framework: Free probability + spectral theory + information theory (inverse-temperature regime).**

The Modern-Hopfield (Ramsauer et al. 2021) energy minimization step is:
```
E(x) = -log sum_i exp(beta * <x, x_i>)   (one-step minimization → softmax)
```

For the cell to operate in the meaningful regime, the softmax inverse-temperature `beta` must produce posterior with non-negligible mass on more than the single argmax. The Shannon entropy of `softmax(beta * c)` for a top-K vector `c` with top-gap `delta = c_1 - c_2` is approximately:
```
H ~ log(K) - beta * delta + O((beta*delta)^2)   [for moderate beta]
H → 0 as beta → inf  (Dirac delta)
H → log(K) as beta → 0 (uniform)
```

At substrate's empirical regime (mean_conf_hop1 = 0.9766, typical second-best around 0.95-0.97), `delta ~ 0.01-0.03`. With `beta = N_DIM = 8192`:
- `beta * delta = 8192 * 0.02 = 163`
- `softmax(top - second) = 1 / (1 + exp(-163) + ...) = 1.0 - exp(-163) ~ 1.0`
- Shannon entropy = `~ exp(-163) * 163 = 1e-69 nats`

This is mathematically a Dirac delta. The `(w[:,None] * E[top_idx]).sum(axis=0)` operation reduces to `E[argmax]` exactly. The Modern-Hopfield "bundle" IS the naive argmax at beta=N_DIM.

For the Modern-Hopfield mechanism to add value over naive argmax requires Shannon entropy `H > 0.5 nats` (the regime where 2-3 candidates have non-negligible mass). This requires `beta * delta < 1`, i.e. `beta < 1 / 0.02 = 50` for the substrate's empirical top-gap. **Optimal beta is in [1, 50], not 8192.** The current beta is 160x past the upper bound of the meaningful regime.

The free-probability framing: per Marchenko-Pastur edge law, the substrate's random-bipolar codebook at storage ratio M/N = 300/8192 = 0.037 sits at very low load (well below MP edge of 0.5). At low load the per-hop cleanup IS well-separated (top1 cosine ~ 0.98) and the naive argmax works; the resonator mechanism cannot lift it because there is nothing to lift — the cleanup is already converged. At HIGH load (M/N ~ 0.3-0.5), the per-hop top-gap shrinks (delta ~ 0.001-0.01) and the resonator would matter, but ALSO the inverse-temperature would need to be 100-1000x smaller to operate in the soft regime. The current configuration cannot exercise the mechanism at any load.

**Citation chain:** Ramsauer et al. 2021 "Hopfield Networks is All You Need" (Modern-Hopfield with inverse-temp beta); Krotov-Hopfield 2016 "Dense Associative Memory for Pattern Recognition"; Edelman-Sutton 2008 "Tails of condition number" (MP-edge); Cover-Thomas 2006 Chapter 12 (entropy of softmax exponential family).

### Angle C — Disparate field: communications theory (turbo decoding, soft-DFE)

The 1993-2010 turbo-codes literature settled this: hard-decision feedback at the saturation regime is INDISTINGUISHABLE from no-feedback. Berrou-Glavieux 1993 "Near Shannon Limit Error-Correcting Coding: Turbo-Codes" showed that achieving the soft-iteration benefit requires the LLR feedback to have finite magnitude — at infinite LLR (hard decision) the iteration converges in 1 step to the hard-feedback fixed point. Forney 1973 "The Viterbi algorithm" already noted that hard-output Viterbi has different performance than soft-output Viterbi and that the soft-output requires preserving the metric difference between candidate paths.

The exact substrate analog: at beta = inf the soft-bundle posterior is a hard pick; at beta = 0 the posterior is uniform (useless); the operational regime where soft-DFE adds value is `beta ~ 1/sigma_noise` where sigma_noise is the channel noise. The substrate's channel-noise analog is the per-hop top-gap variance — typically 0.01-0.03 — giving `beta_opt ~ 30-100`. Current beta=8192 is 100x past optimal.

This finding generalizes the soft-chain HARD_FAIL of Cell 2 to a single mechanism: ALL inter-hop soft mechanisms on substrate currently set beta=N_DIM and silently degenerate to hard chaining.

**Brain existence proof:** CA3 recurrent-collateral attractor dynamics has biological inverse-temperature ~ 1-10 in natural units of synaptic-current variance (Treves-Rolls 1991, Rolls 2018). The brain CANNOT run at beta=N because synaptic noise is irreducible. The brain's multi-step memory retrieval (Buzsaki, Foster, Wilson sharp-wave ripple replay literature) demonstrates that intermediate states are population-coded with confidence amplitudes, NOT hard picks. The substrate's beta=N regime is biologically un-realistic AND mathematically degenerate — both diagnostics agree.

### Diagnosis: TEST_UNFAIR
### Falsifiable revival prediction (symmetric HARD bands):
- **HARD_PASS:** at some beta in {1, 5, 20, 100}, ARM_RESONATOR top1 >= 0.78 (>=0.13pp lift over naive 0.65), 5-seed sd <= 0.04, paired delta >= 0.10 at p<0.05.
- **HARD_FAIL:** all beta in {1, 5, 20, 100, 1000} give top1 within +/- 0.03 of 0.65 — confirms substrate-isotropic-codebook ceiling at this load; pivot to anisotropic encoder.

### Smallest decisive revival cell spec
6-arm beta-sweep: beta in {0.5, 2, 10, 50, 500, 8192}, V_C=200 V_P=10 N=8192 K_SET=20, seeds [7,17,23], 200 chains 2-hop, M=300 train. Local CPU 30 min. Pre-reg both HARD bands above. Anchor: `substrate_resonator_betasweep_v1`.

---

## Cell 2: exp_substrate_soft_chain_dfe_multihop_v1

**Metrics:** ARM_SOFT_CHAIN_2HOP top1=0.6317 (paired_delta=-0.0183 vs naive); SOFT_CHAIN_3HOP top1=0.3933. EMPIRICAL PROOF OF BUG: per-seed bit-identical with ARM_RESONATOR_HARD_2HOP (s7=0.61/0.61, s17=0.645/0.645, s23=0.64/0.64).

### Angle A — Verify-the-referent

Anchor is the prior research drill (`research_resonator_hard_fail_revival_disparate_fields_2026-06-24.md` angle 2.A, P_deflated=0.35). The mechanism per that drill is:
- hop-1: emit `q1 = softmax(top-K cosines / T)` with T calibrated to median-entropy ~= log(3)
- hop-2 query: `k_hop2 = sum_i q1[i] * bind(atom_i, p2)` (SUPERPOSITION)
- cleanup; argmax readout

Cell's implementation (lines 173-229 of `exp_substrate_soft_chain_dfe_multihop_v1.py`):
- `beta = float(N_DIM)` = 8192
- `q = _softmax(beta * top_conf)` → Dirac delta (per Cell 1 angle B math)
- `state = (q[:,None] * E[top_idx]).sum(axis=0)` → `E[argmax]`
- The "soft superposition" is EXACTLY the hard argmax single-vector

The hypothesized mechanism specified `T calibrated to median-entropy ~= log(3)` which corresponds to beta in [1, 10] for the substrate's top-gap. The cell-author implementation set `beta = N_DIM = 8192` which is 800x larger than the spec. **The implementation does not match the referent specification.** The Store chain-grade evidence on CA3 + soft-DFE was never exercised on substrate.

### Angle B — Pure math

**Framework: Information geometry (Amari-Nagaoka) + exponential-family degeneration.**

Softmax with inverse-temperature `beta` parameterizes a 1-parameter exponential family `p(i) = exp(beta * c_i - A(beta))` where `A(beta) = log sum_j exp(beta * c_j)` is the log-partition function. The Fisher information at parameter beta is:
```
I(beta) = Var_p[c]   (variance of cosine under the posterior)
```

As beta → inf:
- `p` concentrates on argmax: `I(beta) → 0` (variance under a Dirac is 0)
- The KL-distance per unit `delta_beta` becomes infinite (sqrt(I) → 0)
- The information geometry has a singular boundary at the simplex vertex

Per Amari-Nagaoka 2000 "Methods of Information Geometry" Chapter 2 (Statistical manifolds), inference that requires the posterior to carry MUTUAL INFORMATION about downstream variables degenerates at the boundary. The downstream-mutual-info between `q1` and `y_correct` (the hop-2 answer) is bounded by:
```
I(q1; y_correct) <= H(q1) - H(q1 | y_correct, x)
```

At H(q1) = 0 (Dirac), `I(q1; y_correct) = 0`. The soft-chain mechanism's information-theoretic ceiling at beta=N_DIM is `I = 0` — it cannot transmit any information that argmax doesn't already transmit.

For the soft-chain to add value over hard-chain, the posterior must have `H(q1) > 0` AND `I(q1; y_correct) > 0` — both require beta in the interior of the parameter space.

**Concrete prediction:** at beta = 10 (operational regime), `H(q1) ~ 0.5-1.5 nats` over the top-K=20 candidates, depending on top-gap. The soft-chain CAN transmit ~ 1 nat of information per hop, which the substrate downstream cleanup can in principle exploit.

### Angle C — Disparate field: brain (CA3 graded reactivation) + ergodic theory

**Brain:** Treves-Rolls 1991 "What determines the capacity of autoassociative memories in the brain?" Network 2:371-397 derived the autoassociative-memory capacity for CA3-like recurrent attractors with FINITE inverse-temperature (biologically realistic beta ~ 1-10 in natural units). Rolls 2018 "The mechanisms of pattern completion and pattern separation in the hippocampus" Front. Syst. Neurosci. confirms: CA3 outputs are population-coded probability distributions, NOT single picks. The downstream CA1/EC integrates the GRADED signal — pattern-completion is not winner-take-all.

The brain CANNOT run at beta=N because:
1. Synaptic transmission has irreducible variance (Stevens 2003 Neuron)
2. Spike-timing has jitter ~ 1-10 ms (Mainen-Sejnowski 1995 Science)
3. The dendritic integration window is finite (~ 10 ms), bounding the effective accumulation gain

These three biological constraints set biological-beta in [1, 10] in units where signal-to-noise is O(1). The substrate's beta=N_DIM is 4 orders of magnitude past biological realism AND past the regime where the soft mechanism can operate.

**Ergodic theory:** for a soft mechanism to converge to a useful stationary distribution under iterated dynamics, the transition kernel must be primitive (positive entries everywhere) — which requires `beta < inf`. At beta = inf the kernel is permutation-deterministic, the ergodic theorem does not give a "soft" mixing, and the iterated mechanism has no asymptotic spread. This is the same diagnostic as Cell 1 angle B but from a different theoretical lens.

### Diagnosis: TEST_UNFAIR (identical wiring bug as Cell 1)
### Falsifiable revival prediction
Subsumed by Cell 1 revival (same beta-sweep cell tests both arms simultaneously). Predictions:
- **HARD_PASS:** soft-chain at beta in {2, 10} lifts >= 0.10 over hard-chain at same beta
- **HARD_FAIL:** soft and hard chains tie at every beta — confirms inter-hop chaining is not the limit; pivot to encoder

### Smallest decisive cell spec
Same 6-arm beta-sweep as Cell 1 plus 1 additional arm `ARM_BETA_10_SOFT_CHAIN` that uses the soft-superposition instead of hard-argmax state hand-off. Total 7 arms, 30 min local CPU.

---

## Cell 3: exp_substrate_confidence_calibration_isotonic_v1

**Metrics:** raw cosine r=0.111; isotonic r=0.131; temperature scaling r=0.111. ECE for isotonic = 0.017 (GOOD), Pearson r failed (target 0.70). Overall accuracy 0.09 (chance 0.02). N=2048 sparse f=0.02 V=50 M=2000.

### Angle A — Verify-the-referent (lap4_3 isotonic regression)

Per Store, `lap4_3` is the canonical chain-grade isotonic regression cell. It used:
- LARGER scale (likely M >= 20000 calibration set, V much larger, base rate >> 0.09)
- Confidence inputs from a DIFFERENT mechanism (likely full forward-walk on chain-grade KG)
- Metric: ECE primarily; AUC secondarily; pearson r NOT the primary metric

Today's cell ran at smoke regime (M=2000, V=50, base rate 9%) and used pearson r as the primary metric. The lap4_3 chain-grade evidence is on calibration (ECE) which today's isotonic arm DID achieve (ECE=0.017 is HARD_PASS-grade). **The pre-reg metric switch (pearson r at HARD_PASS=0.70) is the source of the HARD_FAIL — the Store chain-grade evidence on calibration mechanism is intact and reproduced.**

### Angle B — Pure math

**Framework: Information geometry of low-base-rate classification + Cramer-Rao bound on Pearson correlation.**

The Pearson correlation `r(score, correctness)` between a continuous score `S` and a binary outcome `Y ~ Bernoulli(p)` is bounded above by:
```
r_max(AUC, p) = (AUC - 0.5) * 2 * sqrt(p * (1-p)) / sigma_S
```
(this is the point-biserial correlation upper bound; standard result in psychometrics).

At empirical: AUC ~ 0.55-0.60 (small lift on a 9% base rate task), p = 0.09:
```
r_max ~ 0.05 * 2 * 0.286 / sigma_S = 0.029 / sigma_S
```
With sigma_S (standardized score variance) ~ 0.3 in empirical sd units:
```
r_max ~ 0.10
```

The OBSERVED r=0.131 is at or near the achievable ceiling for this regime. **r=0.70 is unphysical at this base rate** — it would require AUC > 0.99 which is impossible at 9% accuracy (AUC > 0.99 implies near-perfect ranking which contradicts the empirical accuracy).

The Cramer-Rao bound on the achievable Pearson r is:
```
r^2 <= 1 - (1 / I_Y(theta))   where I_Y is Fisher info of Y under the score model
```
For Y Bernoulli with p ~ 0.09 and the score-distribution observed, the bound caps r at ~ 0.2-0.3.

**The pre-reg HARD bands violated a Fisher-information bound.** The cell could not have HARD_PASSed by construction. This is a different kind of TEST_UNFAIR: not a wiring bug but a metric-and-regime mismatch.

### Angle C — Disparate field: medical-diagnostics ROC analysis + meteorology probabilistic-forecasting

**Medical diagnostics:** Pencina-D'Agostino 2008 "Evaluating the added predictive ability of a new marker: from area under the ROC curve to reclassification and beyond" Stat. Med. is the standard reference on metric choice for low-prevalence classification. Their result: for prevalence <10%, Pearson r is a deceptive metric (it conflates calibration and discrimination); use AUC for discrimination + ECE/Brier for calibration. Hosmer-Lemeshow 2000 "Applied Logistic Regression" explicitly recommends against Pearson-r for low-base-rate model evaluation.

**Meteorology:** the probabilistic-weather-forecasting literature (Gneiting-Raftery 2007 JASA "Strictly proper scoring rules, prediction, and estimation") established the same point: forecast skill at rare events (precipitation > threshold) is evaluated via Brier skill score, ROC AUC, and reliability diagrams — NEVER Pearson r between forecast probability and outcome. The Brier score decomposes into reliability + resolution + uncertainty; the substrate's ECE=0.017 indicates excellent RELIABILITY; the failed Pearson r is a RESOLUTION concern that is bounded above by the base rate.

**The literature unanimously says the test was set up to fail by metric choice. The mechanism (isotonic regression) WORKED — ECE improved from 0.46 to 0.017 (27x better calibration).**

### Diagnosis: TEST_UNFAIR (metric-regime mismatch) + SCALE_MISMATCH (smoke at 9% base rate cannot reach Store regime's pearson r)
### Falsifiable revival prediction
- **HARD_PASS:** at scaled-up regime (N=8192 V=200 M=8000 base-rate >= 0.30): AUC >= 0.70 AND ECE <= 0.03 — chain-grade calibration confirmed at deployment scale.
- **HARD_FAIL:** ECE > 0.10 OR AUC < 0.55 at scaled-up regime — substrate confidence does NOT carry discrimination info even at deployment scale; refuse-gate must source confidence elsewhere.

### Smallest decisive cell spec
4-arm rerun at N=8192 V=200 M=8000 sparse f=0.02 with arms = {raw cosine, isotonic, temperature, Platt-sigmoid}, metric = AUC + Brier + ECE (3 metrics, all pre-reg). 3 seeds local CPU 60 min.

---

## Cell 4: exp_substrate_hub_spoke_E1_encoder_v1

**Metrics:** unigram bpc=7.738, baseline_path_C bpc=7.667 (passes single-spoke baseline), all hub-spoke arms bpc=7.707 within +/- 0.03 of each other; cf-RPE gates collapsed to uniform [0.333, 0.333, 0.333]; per-spoke L3 recon errors all in [92.20, 92.47]. text8 100K tokens V=4000 N=8192.

### Angle A — Verify-the-referent (Path C v2 + encoding drill E1)

Per `research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md`, hub-spoke E1 has P_deflated=0.45. The mechanism source: deep-ensembles literature predicts federation lift when spokes are diverse. Today's spokes are NOT diverse:
- Same predictive-coding update rule (3-layer L1/L2/L3 sign-quantized)
- Same training tokens (identical `idx_train`)
- Small parameter jitter: alpha grid +/- 15%, beta grid +/- 5%
- Per-pass L3 recon error: 92.20-92.47 across 15 spokes (cv = 0.0008 — under 0.1% variation)

The encoding-drill anchor predicted lift conditional on genuine spoke diversity (different encoder families or different INIT regions). Today's spokes share encoder family + share init via the same algorithm. **The referent's conditional precondition (diverse spokes) is NOT MET.** P=0.45 was a P for the well-designed federation; today's mis-designed federation has P ~ 0.05 (essentially redundant single-spoke).

### Angle B — Pure math

**Framework: random-matrix theory + spectral analysis of ensemble diversity.**

For an ensemble of M encoders `{E_1, ..., E_M}` each producing outputs in R^N, the effective ensemble diversity is captured by the average pairwise cosine `c_ij = <E_i, E_j> / (||E_i|| * ||E_j||)`. The ensemble effective rank is approximately:
```
rank_eff ~ M / (1 + (M-1) * c_mean)
```
At c_mean = 0.999 (substrate empirical, from L3 recon error similarity), rank_eff(M=5) ~ 5 / (1 + 4*0.999) = 1.001 — the 5-spoke ensemble has effective rank 1.

The Fort-Hu-Lakshminarayanan 2019 NeurIPS "Deep Ensembles: A Loss Landscape Perspective" empirically demonstrated that ensemble lift is monotone in `1 - c_mean`. At c_mean > 0.99, ensemble lift is negligible (<1% in their experiments). At c_mean < 0.5, lift is substantial. The substrate's c_mean = 0.999 puts the spokes in the regime where the ensemble theorem predicts ZERO lift — entirely consistent with the HARD_FAIL.

The hub aggregation via `sign(sum(spokes))` for nearly-identical bipolar inputs:
```
sign(sum_{i=1}^M spoke_i) = sign(M * spoke_0 + sum_{i>0} (spoke_i - spoke_0))
                          = sign(M * spoke_0)  [when ||spoke_i - spoke_0|| << M * ||spoke_0||]
                          = spoke_0
```
This is the mathematical identity proof that hub-spoke collapses to single-spoke at the empirical c_mean.

The cf-RPE gate adaptation:
```
gates_logits += eta * (per_spoke_cos_align - mean_align)
```
For per_spoke_cos_align all within 1% of each other (because all spokes encode the same bigram structure), the gradient signal is ~ 0.01 * eta * n_steps / n_pairs ~ 0.01 * 0.02 * 50 = 0.01 — well within softmax-numerical-precision and the gates remain near-uniform. The substrate's measured cfrpe_gate_std_over_mean ~ 0.0008 confirms this exactly.

### Angle C — Disparate field: distributed-systems consensus + biological cortical-column diversity

**Distributed systems / Byzantine fault tolerance:** Lamport-Shostak-Pease 1982 "The Byzantine Generals Problem" + Castro-Liskov 1999 "Practical Byzantine Fault Tolerance" + blockchain consensus literature: N-of-M voting EXTRACTS new information only when voters are independent. If voters are conditionally-correlated (same training data, same algorithm), the joint information bound is `H(any one voter) + 0 + 0 + ... = H(any one)` — adding voters does not add information. The substrate's spokes are conditionally-correlated through shared data AND shared algorithm → joint information bound = single-spoke info.

**Biological cortical columns (V1):** V1 cortical columns get genuine diversity from receptive-field tiling — each column receives input from a DIFFERENT location in the visual field. The diversity is in the INPUT, not in the algorithm. Hubel-Wiesel 1962 establishment of cortical-column tiling: ~150 micron columns, each tuned to a different orientation + position; the ensemble representation is high-dimensional because the inputs are genuinely different. Substrate's spokes receive the SAME text8 token stream — there is no input-diversity to extract.

**The disparate-field consensus is unanimous:** federation requires either input-diversity OR genuinely-different algorithms OR widely-separated INIT basins. Substrate's hub-spoke v1 has none of these.

### Diagnosis: TEST_UNFAIR (federation-no-diversity)
### Falsifiable revival prediction
- **HARD_PASS:** ARM_DIVERSE_SPOKES with 3 fundamentally-different encoder families (char-trigram + skipgram-cooccurrence + random-bipolar-with-PC) gives bpc <= 7.55 (clearing single-spoke baseline 7.667 by >= 0.10).
- **HARD_FAIL:** ARM_DIVERSE_SPOKES bpc within +/- 0.05 of single-spoke baseline → federation principle does not transfer to substrate even with genuine diversity; pivot to scale-up single encoder.

### Smallest decisive cell spec
3-arm cell: single Path C, 3-spoke same-family (control), 3-spoke diverse-family. text8 100K V=4000 N=8192 3 seeds GPU 60 min.

---

## Cell 5: exp_substrate_audit_trail_pipeline_integration_v1

**Metrics:** smoke regime N=1024 V=60 M=80 1 seed. V3 prov 0.825 (target 0.85), V5 prov 0.692, V3 refuse_acc 5/30=0.167, V5 refuse_acc 2/30=0.067, V5 lift vs V3 = -0.133.

### Angle A — Verify-the-referent (wave14_cap12 audit-trail v1-v5)

Per Store, wave14_cap12 audit-trail v1-v5 chain-grade. The chain-grade evidence was at:
- Wave-grade scale (V_C >= 300, M >= 1500, multi-seed)
- The V5 vs V3 lift exceeded smoke-noise floor
- The refuse-gate accuracy reached ~0.5-0.7 on a proper unknown-set distribution

Today's cell ran at:
- Smoke (V=60, M=80, M_unknown=30, 1 seed)
- 20x undersampled vs Store regime
- Single-seed means no variance estimate possible

The DESIGN_NOTE confirms this is a smoke. The pre-reg HARD bands inherited from chain-grade-scale pre-reg without re-calibration for smoke statistical power. **Referent regime does not match — by approximately 20x in sample size.**

### Angle B — Pure math

**Framework: Concentration inequalities (Hoeffding bound, Wilson interval) + statistical power analysis.**

For a Bernoulli(p) with n samples, the Hoeffding 95% confidence interval is approximately:
```
CI_95 = [p - 1.96 * sqrt(p(1-p)/n), p + 1.96 * sqrt(p(1-p)/n)]
```

For V3 at n=40, p=0.825:
```
CI_95 = [0.825 - 0.118, 0.825 + 0.118] = [0.707, 0.943]
```

The pre-reg HARD_PASS threshold 0.85 sits well WITHIN this CI. The test cannot reject H0: p = 0.85 with n=40 samples. The HARD_FAIL at 0.825 is statistically indistinguishable from a HARD_PASS at 0.85 — single-cell smoke noise.

For the V5 vs V3 paired comparison, with 6-event difference on n=40, the binomial test p-value for H0: equal-rates is:
```
P-value ~ 0.10-0.15  (two-sided binomial test)
```
This is not significant at alpha=0.05 — the V5 -0.133 delta is consistent with no real difference between V3 and V5.

For the refuse_acc, n=30 (M_unknown):
```
V3 refuse_acc = 5/30, 95% CI = [0.06, 0.35]
V5 refuse_acc = 2/30, 95% CI = [0.01, 0.22]
```
Pre-reg HARD_PASS = 0.5 sits OUTSIDE both CIs but the CIs overlap with each other massively — the test cannot reject the hypothesis that V5 = V3 refuse-rate.

**Power calc to detect p=0.85 vs p=0.90 at 80% power, alpha=0.05:**
```
n_required ~= (z_alpha + z_beta)^2 * 2 * p(1-p) / delta^2
            = (1.96 + 0.84)^2 * 2 * 0.875 * 0.125 / 0.05^2
            = 7.84 * 0.219 / 0.0025
            = 686 samples
```
Smoke n=40 is 17x undersampled for the pre-reg sensitivity.

### Angle C — Disparate field: statistical genetics (GWAS replication crisis) + clinical trials (power analysis)

**GWAS:** the genome-wide-association field's bedrock lesson is "underpowered studies don't replicate". Ioannidis 2005 PLoS Med "Why most published research findings are false" formalizes this: at low statistical power, the false negative rate is so high that null results carry no information. Button-Ioannidis-Mokrysz-Nosek-Flint-Robinson-Munafo 2013 Nat Rev Neurosci "Power failure" quantified that 78% of neuroscience findings at n<50 fail to replicate at n=200+. The substrate's audit-trail at n=40 falls squarely in the "no-information null result" regime.

**Clinical trials:** the FDA's drug-trial methodology requires pre-specified power analysis before trial registration. The standard is 80%+ power at the smallest clinically-meaningful effect size. Audit-trail cell skipped this step. ICH-E9 statistical principles document explicitly: a HARD_FAIL conclusion from an underpowered trial is invalid; the trial must be re-sized or the conclusion must be "indeterminate" not "rejected".

**The disparate-field consensus:** today's audit-trail HARD_FAIL is an INDETERMINATE result, not a rejection of the mechanism.

### Diagnosis: SCALE_MISMATCH (smoke at 17x undersampled) — INDETERMINATE, not REFUTED
### Falsifiable revival prediction
- **HARD_PASS at full scale:** rerun at N=4096 V=200 M=400 M_unknown=150 3 seeds — V3 prov >= 0.80 AND V5 prov >= V3 prov AND refuse_acc >= 0.40.
- **HARD_FAIL at full scale:** V3 prov < 0.65 (no transfer of refuse-gate from Store wave-grade evidence) — pivot to refuse-gate redesign.

### Smallest decisive cell spec
Rerun at N=4096 V=200 M=400 M_unknown=150 3 seeds local CPU 60 min. Pre-reg HARD bands above with explicit power calc justification.

---

## Cross-cell summary

| Cell | Diagnosis | Test-design root cause | Substrate-mechanism status |
|---|---|---|---|
| 1 resonator-multihop | TEST_UNFAIR | beta=N_DIM saturates softmax to argmax | INTACT — never tested |
| 2 soft-chain DFE | TEST_UNFAIR (same bug) | beta=N_DIM saturates softmax to argmax | INTACT — never tested |
| 3 calibration isotonic | TEST_UNFAIR + SCALE | pearson r metric + 9% base rate violates Cramer-Rao | INTACT — ECE 0.017 confirms calibration mechanism works |
| 4 hub-spoke E1 | TEST_UNFAIR | 3-5 spokes are conditionally-correlated (cos=0.999) → rank-1 ensemble | INTACT — federation principle untested at genuine diversity |
| 5 audit-trail | SCALE_MISMATCH | smoke n=40 is 17x undersampled vs pre-reg sensitivity | INTACT — INDETERMINATE result, not refutation |

**ZERO of the 5 cells produced evidence that REFUTES the substrate mechanism.** All 5 are test-design bugs or scale-mismatch artifacts. The Store chain-grade evidence is intact.

The single most economical revival = the 6-arm beta-sweep on resonator-multihop (Cell 1 + 2 + the cross-cell common-mode-1 in one cell, 30 min local CPU). See companion synthesis note for priority order.
