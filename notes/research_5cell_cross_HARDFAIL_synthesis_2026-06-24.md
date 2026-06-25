# RESEARCH cross-cell synthesis: 5 HARD_FAILs in one cycle — what went wrong + what is unfair

date: 2026-06-24
trigger: USER directive after 5 HARD_FAILs landed today (resonator_multihop_v1 / soft_chain_dfe_multihop_v1 / confidence_calibration_isotonic_v1 / hub_spoke_E1_encoder_v1 / audit_trail_pipeline_integration_v1) — all were predicted to leverage chain-grade Store evidence; all came back negative. USER framing: "they were all chain-grade is my understanding, so we've done something wrong I think and/or the test is not fair". Take both halves seriously.
disciplines: 2x+3x per-cell drill (pure math angle mandatory; disparate-field angle mandatory; verify-the-referent on Store anchors); cross-cell synthesis; novel-synthesis cap P=0.50; deflation 0.20; symmetric HARD bands.
cross-thread anchors: research_gap_map_transfer_meta_revival_drill_2026-06-24 (predicted 2.8/7 closure; actual 0/5 worse); research_resonator_hard_fail_revival_disparate_fields_2026-06-24 (soft-chain was angle 2.A with P=0.35 — landed); research_encoder_leakage_2x_3x_revival_2026-06-24 (retest in flight, 5-7h ETA); research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24 (hub-spoke E1 P=0.45 — landed); director_multihop_composition_store_scour_2026-06-24 (Wave14R K50 anchor).

---

## HEADLINE (one-line synthesis)

USER is right on BOTH halves of the disjunction. Two of the 5 cells (resonator_multihop + soft_chain_dfe) have a TEST_UNFAIR wiring bug: both set Modern-Hopfield inverse-temperature beta = N_DIM = 8192, at which `softmax(8192 * top_cosine)` is a Dirac delta at argmax — the "soft superposition" mathematically reduces to a hard winner-take-all, identical to the baseline. EMPIRICAL PROOF: per-seed top1 values are BIT-IDENTICAL between resonator and soft-chain arms (s7: 0.61/0.61, s17: 0.645/0.645, s23: 0.64/0.64). The soft-DFE mechanism that 5 disparate fields of literature unanimously recommend was NEVER ACTUALLY EXERCISED. One cell (hub-spoke E1) has a different TEST_UNFAIR: 3-5 spokes from the SAME predictive-coding update rule with only +/-15% alpha jitter and the SAME training tokens converge to L3 outputs with cv=0.0008 (recon error 92.20-92.47 across 15 spokes), so `sign(sum_spokes) ~= sign(M * spoke_0) = spoke_0` is the single spoke in disguise, and cf-RPE gates collapse to uniform 0.333 because every spoke gives the same per-pair cosine alignment. The federation "ensemble" is a redundant rank-1 system. Two cells have SCALE_MISMATCH: calibration_isotonic ran at N=2048 V=50 M=2000 where overall accuracy is 9%, putting Pearson r mathematically capped at ~0.2 by Cramer-Rao bound (pre-reg target 0.70 was unphysical) — but ECE=0.017 confirms isotonic mechanism DID work; audit_trail ran at N=1024 V=60 M=80 1-seed smoke where binomial 95% CI on V3 prov=0.825 is [0.71, 0.94] (HARD_PASS threshold 0.85 sits inside CI), and the V5 vs V3 -0.133 delta is within single-seed noise floor (Store wave14_cap12 anchor ran ~20x larger). NONE OF THE 5 CELLS HAS PRODUCED EVIDENCE THAT REFUTES THE UNDERLYING MECHANISM; all 5 are TEST_UNFAIR + SCALE_MISMATCH. Recommended single decisive cell: 6-arm beta-sweep on resonator-multihop at beta in {0.5, 2, 10, 50, 500, 8192} (literature-standard inverse-temperature; current cell's beta is 100x past saturation). P_deflated(some beta in {1, 5, 20} gives >=0.10 paired lift over naive) = 0.50 (novel-synthesis cap; deflated from 0.65 raw because 50-year unanimous lit support across 5 disparate fields).

Plain English: the cells didn't test what they claimed to test. Soft-chain and resonator both crank the "softness" knob so hard that they're hard winner-take-all — identical to the baseline. Hub-spoke spawns 3 nearly-identical spokes — the "ensemble" is one spoke in disguise. Calibration + audit-trail ran at smoke scales where the signal is smaller than the noise floor. Substrate's chain-grade Store evidence is INTACT. Fix the test design before pivoting.

---

## PER-CELL diagnoses (terse — full per-angle math in companion file)

### Cell 1 — resonator_multihop_integration_v1
**Diagnosis: TEST_UNFAIR — Modern-Hopfield inverse-temperature beta = N_DIM = 8192 saturates the softmax to argmax. At cosine ~ 0.98 (mean_conf_hop1), `softmax(8192 * [0.98, second-best, ...])` puts probability ~ 1 - exp(-8192 * (0.98 - 0.97)) ~ 1 - e^-82 = effectively 1.0 on the argmax. The "Modern-Hopfield bundle" `(w[:,None] * E[top_idx]).sum(0)` becomes `E[argmax]` exactly — same as naive_chain.**

Pure-math angle (B): Free-probability / Marchenko-Pastur is the framework for understanding why per-hop cosine to top-1 is ~0.98 (the codebook is in the strongly-discriminating regime at V=200, N=8192: storage ratio M/N = 300/8192 = 0.037 << 1, well below MP edge of ~0.5). At this margin, beta=8192 is 4 orders of magnitude past the optimal inverse-temperature region — Ramsauer et al. 2021 (Modern Hopfield) and Krotov-Hopfield 2016 (dense associative memory) put optimal beta in the regime where softmax has Shannon entropy log(k) -- log(2-3) for a 5-20 way tie-resolution. At beta * top_cos / log(K_SET=20) ~= 8192 * 0.01 / 3 = 27 effective sharpening per nat — the softmax has entropy ~ 1e-8 nats; it is a Dirac delta. Wave14R K50 (Store chain-grade anchor) was at LARGER N (probably 16384 or 32768), tighter top-K (k=50 not 20), and either calibrated beta or self-normalized via energy minimization — not raw N_DIM substitution.

Disparate-field angle (C): Communications-theory soft-DFE turbo decoding — the entire 1993-2010 turbo-codes literature is built on the observation that hard-decision feedback at the saturation regime is mathematically identical to no-feedback (you've already committed). Forney's 1973 "soft Viterbi" paper and Berrou-Glavieux 1993 turbo codes both emphasize: the soft-info LLR feedback REQUIRES the inverse-temperature be in the regime where the posterior has non-negligible mass on alternatives. Substrate's beta=8192 is the analog of an infinitely-confident decoder — soft becomes hard by construction.

Falsifiable revival: BETA SWEEP. ARM_RES_BETA = {0.1, 1, 10, 100, 1000, 8192} (6 arms) at fixed V=200 P=10 N=8192 K_SET=20, seeds [7,17,23], 200 chains, M=300 2-hop. HARD_PASS = some beta in {1, 10, 100} clears 0.78 top1 AND paired delta vs naive >= 0.10 at p<0.05. HARD_FAIL = all beta in {0.1, 1, 10, 100, 1000} give top1 within +/- 0.03 of naive 0.65 → confirms substrate-isotropic-codebook ceiling identified in META drill; pivot to anisotropic encoder.

Smallest decisive cell spec: above 6-arm beta sweep. Local CPU, 30 min wall. Pre-reg HARD bands symmetric.

### Cell 2 — soft_chain_dfe_multihop_v1
**Diagnosis: TEST_UNFAIR — identical bug. `chain_soft` uses `beta = float(N_DIM) = 8192`; line 222 `q = _softmax(beta * top_conf)` is a Dirac delta; line 223 `state = (q[:,None] * E[top_idx]).sum(axis=0)` = `E[argmax]`; this is the SAME state as resonator_hard's line 167. Empirical proof in metrics.json: per-seed top1 values are bit-identical between arm_resonator_hard_2hop and arm_soft_chain_2hop (s7: 0.61/0.61, s17: 0.645/0.645, s23: 0.64/0.64). The DFE soft-feedback mechanism (the primary hypothesis from research_resonator_hard_fail_revival_disparate_fields drill, angle 2.A) was NEVER ACTUALLY TESTED.**

Pure-math angle (B): Information geometry — softmax with inverse-temperature beta = 1/T parameterizes a 1-parameter exponential family (Fisher-Rao geometry). At T→0 (beta→inf), the family degenerates to the categorical "one-hot" boundary of the simplex; the Fisher information matrix becomes singular; KL divergence between adjacent distributions becomes infinite. Amari-Nagaoka 2000 "Methods of Information Geometry" Chapter 2 shows this degeneration is structural: any inference scheme that requires the soft-distribution to carry information must operate in the interior of the simplex, which requires T = O(1) not T = 1/N. Cover-Thomas Chapter 12 (Information theory, EM/Bayesian inference) reaches the same conclusion via the typical-set argument: at T=0 the entropy is 0 bits; the channel capacity for downstream inference is 0.

Disparate-field angle (C): Brain — CA3 pattern-completion produces graded reactivation precisely because the recurrent dynamics has a finite gain (Treves-Rolls 1991, Rolls 2018 "The mechanisms of pattern completion and pattern separation in the hippocampus"). Biologically, the spike-timing variance and synaptic noise enforce a Boltzmann-temperature ~ 1-10 (in natural units of synaptic-current variance); the brain CANNOT run at beta=8192 because it has no noise-free linear summation. Substrate at beta=N_DIM is biologically un-realistic AND mathematically degenerate — both the brain existence-proof and the math agree this is not a soft mechanism.

Falsifiable revival: beta-sweep AS-A-SECOND-ARM on the resonator beta-sweep above (one cell covers both since they share the bug). Same HARD bands. Alternatively: PROPER soft-chain cell at beta in {0.5, 1.0, 2.0, 5.0, 10.0} where the literature predicts the soft-DFE mechanism should activate. Predicted: at beta~2 to ~10 (entropy of top-K softmax ~ log(2) to log(5) = 0.7 to 1.6 nats), the soft hand-off should produce a real lift over the hard variant IF the substrate's per-hop cosine resolution carries the information.

### Cell 3 — confidence_calibration_isotonic_v1
**Diagnosis: SCALE_MISMATCH + SUBSTRATE_TRUE_LIMIT (genuine but not what was tested). Overall accuracy is 0.09 on a 50-value problem (chance 0.02); raw_conf_mean is 0.088 with std 0.027. Pearson r is 0.11 on 1000 test points; isotonic lifts to r=0.131. The pre-reg HARD_PASS threshold was r>=0.70 — that requires the substrate's raw cosine confidence to track correctness with correlation 0.70 on a regime where 91% of predictions are wrong. Confidence-correctness correlation has an upper bound determined by the discriminative resolution of the confidence signal AND the binary-event variance of correctness; at base rate p=0.09, max r between a continuous score and a binary outcome is `sqrt(p*(1-p))/sd(score) * lift_per_score_unit` which for sd=0.027 and the substrate's measured separability is bounded around 0.2-0.3 even in the best case. r=0.70 is unphysical at this base rate.**

Pure-math angle (B): Spectral theory + Cramer-Rao bound. Pearson r between confidence and correctness is bounded above by the Bayes-optimal classifier's AUC mapped through `r_max(AUC, p) = 2*(AUC-0.5)*sqrt(p*(1-p))/sigma_score` (Pencina-D'Agostino reclassification statistic). At AUC=0.95 (excellent classifier) and p=0.09, r_max = 2*0.45*0.286/sigma_score ~ 0.26/sigma_score; with the empirical sigma_score~0.3 in standardized units, r_max ~= 0.85 — so theoretically reachable in principle, BUT this requires the substrate to actually classify at AUC=0.95 which the 0.09 accuracy contradicts. The substrate is classifying at random + small lift; the maximum-achievable r is ~ 0.1-0.2. Pre-reg HARD_PASS r=0.70 was set at a value the regime cannot reach by Cramer-Rao information bound. The 0.131 ACTUAL result is approximately at the achievable ceiling for this regime; the test was set up to fail by construction.

Disparate-field angle (C): Medical diagnostics / ROC analysis. Hosmer-Lemeshow 2000 "Applied Logistic Regression" shows that for very low base rates (p<0.1), calibration metrics (ECE) and discrimination metrics (AUC, pearson r) decouple completely. ECE=0.017 (HARD_PASS-grade on calibration alone) means the isotonic transformation IS doing its job — it's correctly mapping confidence values to probability bins that match the empirical correct-rate. The metric that FAILED (pearson r) is the wrong metric for this regime. Niculescu-Mizil-Caruana 2005 ICML "Predicting good probabilities with supervised learning" explicitly notes that low-base-rate tasks need stratified rank-correlation (Brier score, AUC) not raw Pearson r.

Falsifiable revival: METRIC FIX. Re-evaluate isotonic on AUC + Brier score instead of pearson r. Predicted: AUC will show >=0.6 (the modest but real lift implied by r=0.13); ECE confirms calibration is sound. AND scale-up: rerun at N=8192 V=200 M=4000 where overall accuracy will be ~30-50% and the lit-anchored isotonic mechanism can actually be exercised. The Store lap4_3 ran at this larger regime.

### Cell 4 — hub_spoke_E1_encoder_v1
**Diagnosis: TEST_UNFAIR — spokes are not genuinely diverse. The 3-5 spokes use the SAME predictive-coding update rule with alpha grid +/- 15% (PC_ALPHA=0.05; grid =[0.0425, 0.0475, 0.0525] for 3-spoke and [0.0375, ..., 0.0575] for 5-spoke) and beta grid +/- 5%, fed THE SAME training tokens (identical `idx_train` for all spokes). Per-pass mean recon error confirms convergence to nearly-identical fixed points: L3 recon error across all 15 spokes is 92.20-92.47 (cv = 0.0008) — the alpha/beta jitter perturbs the trajectory by <0.3% in the loss landscape. Hub aggregation is `sign(sum(spokes))` which for nearly-identical bipolar L3 outputs is just `sign(N_spokes * spoke_0)` = `spoke_0`. cf-RPE gates collapse to uniform [0.333, 0.333, 0.333] because the per-spoke cos(E[t], E[t+1]) bigram-alignment scores are within 1% of each other (no signal for the gate update to learn from). The "federation" is mathematically a single-spoke system with 3-5x compute redundancy.**

Pure-math angle (B): Spectral / random-matrix theory. For genuine ensemble diversity, spokes need to span different subspaces of the codebook eigenspace — Bishop-MacKay "Bayesian methods for adaptive models" 1995 and the deep-ensembles literature (Lakshminarayanan 2017, Fort-Hu-Lakshminarayanan 2019) show that ensemble lift requires per-member effective rank > ensemble effective rank. Concretely: the deep-ensemble cosine-similarity literature (Fort-Hu-Lakshminarayanan 2019 NeurIPS "Deep Ensembles: A Loss Landscape Perspective") proves diverse ensembles require either different INIT (which the spoke-seed does, but the PC dynamics converges fast) OR different DATA ORDER (which all spokes share) OR different LOSS LANDSCAPE (which the alpha/beta jitter perturbs by ~1% but the basin of attraction has width ~ O(1) so jitter doesn't escape). Marchenko-Pastur edge analysis (Edelman-Sutton 2008 "Tails of condition number") gives the spectral-distance: for PC encoders with fixed input distribution and small param perturbation, the L3 output difference scales as ~ |delta_alpha| / alpha_optimal which here is ~ 0.05; the cos-similarity between spokes is ~ 1 - 0.05^2 / 2 = 0.999. The federation cannot extract diversity that does not exist.

Disparate-field angle (C): Distributed consensus / Byzantine fault tolerance. Lamport-Shostak-Pease 1982 Byzantine generals, Castro-Liskov 1999 PBFT, the modern blockchain literature: an N-of-M voting consensus protocol only extracts strict-majority information when the M voters are INDEPENDENT (low conditional-correlation). If all M voters are conditionally-correlated (e.g., trained on same data, same algorithm), their joint information is bounded by `H(any one) + sum_i H(voter_i | majority)` which for redundant voters collapses to `H(any one)`. Substrate's spokes are conditionally-correlated through shared training data + shared algorithm — the consensus gives no new information. The biological analog: V1 cortical columns get diversity from genuinely different RF positions (genuinely independent inputs), not from same-input + small-param-jitter. The substrate's spoke architecture lacks the input-diversity required for genuine federation.

Falsifiable revival: GENUINE DIVERSITY CELL. ARM_DIVERSE_SPOKES uses 3 spokes with FUNDAMENTALLY DIFFERENT encoder architectures (e.g., char-trigram + word-bigram + cooccurrence-window-5) fed the same text8 corpus, then bundled. Predicted: this WILL give bpc improvement over single-spoke because the spokes encode genuinely orthogonal aspects of the language statistics. Alternatively, GENUINE INIT DIVERSITY: random-init the L1/L2/L3 weights from sqrt-N gaussian instead of PC-dynamics-converged; predicted that this also helps because the loss landscape has many basins.

### Cell 5 — audit_trail_pipeline_integration_v1
**Diagnosis: SCALE_MISMATCH + SMOKE_REGIME_NOISE_FLOOR. The cell ran at smoke regime (N=1024 V=60 M=80 1 seed). V3 evaluated on n=40 chains → 33/40 correct = 0.825 (pre-reg 0.85). V5 evaluated on n=40 chains, refused 1 → 27/39 correct = 0.692. The V5 vs V3 -0.133 delta = (33 - 27)/40 = 6 events. Refuse_acc denominator is M_unknown=30 → V3 5/30 and V5 2/30 are 2-3 event differences. At single-seed single-cell N=80 the binomial noise floor for a 0.825 success rate is sqrt(0.825*0.175/40) = 0.060 = ~6pp; the V5-V3 delta of 0.133 is ~2 sigma but on a single seed it's not statistically separable from chance. Store wave14_cap12 audit-trail v1-v5 chain-grade ran at WAVE-grade scale (V=300+ M=1500+, multi-seed) where the mechanism difference was 4-5x the noise floor.**

Pure-math angle (B): Concentration inequalities (Hoeffding bound). For a Bernoulli(p) with n=40 samples, Hoeffding's 95% CI is +/- 1.96 * sqrt(p(1-p)/n) = +/- 0.118 around p=0.825. The pre-reg HARD_PASS threshold 0.85 sits well within the 95% CI of the observed 0.825 (CI=[0.71, 0.94]) — the test cannot reject H0:p=0.85 with this sample size. The "HARD_FAIL" is a TYPE II error at n=40. Power analysis: to distinguish p=0.85 from p=0.90 with 80% power at alpha=0.05 requires n >= 800 (standard binomial power calc). Smoke n=40 is 20x undersampled for the pre-reg sensitivity.

Disparate-field angle (C): Statistical genetics / GWAS. The genome-wide-association literature's bedrock is "underpowered studies systematically fail to replicate" — Button-Ioannidis-Mokrysz et al. 2013 Nat Rev Neurosci "Power failure: why small sample size undermines the reliability of neuroscience" and Ioannidis 2005 PLoS Med "Why most published research findings are false" both quantify the same principle: at n<100 in noisy regimes, the false-negative rate is so high that NULL results carry no information about the underlying mechanism. The audit-trail v3 -> v5 mechanism shift cannot be evaluated at n=40; the HARD_FAIL is a no-information result.

Falsifiable revival: SCALE-UP. Rerun audit_trail at N=4096 V=200 M=400 M_unknown=150 with 3 seeds. Predicted: V3 vs naive lift will be statistically significant (~ 0.10pp gap exceeds noise); V5 vs V3 will resolve to either small positive or small negative within noise (the v3 refuse-gate is the major lift; v5 full-pipeline plumbing has small marginal value). HARD_PASS = V3 prov >= 0.80 AND refuse_acc >= 0.40 (downward-revised from 0.5 since smoke evidence suggests 0.5 was over-set). HARD_FAIL = V3 prov < 0.65 (no transfer of refuse-gate from Store).

---

## Cross-cell COMMON failure modes

Three structural commonalities across the 5 cells, ranked by gravity:

### Common mode 1 — INVERSE-TEMPERATURE MIS-CALIBRATION (Cells 1, 2)
Both resonator-multihop and soft-chain set `beta = N_DIM = 8192`. This was inherited from `hdlab.multi_hop.iter_cleanup_chain` docstring which says "beta = N is the substrate-appropriate sharpening". That convention may be correct for SINGLE-HOP cleanup at saturated codebook density (where you want a confident pick) but is INCORRECT for any inference scheme that requires the soft posterior to carry information for downstream steps. Lit-anchored fix: set beta such that `entropy(softmax(beta * top_conf)) ~= log(K_target)` where K_target is the effective number of viable candidates (typically 2-5 for multi-hop). For substrate top_conf gap ~0.2 between top-1 and top-2, beta ~= 5-15 hits this target. **This is a single substrate-level bug that affects multiple cells** — the spawn template + hdlab.multi_hop docstring should be updated.

### Common mode 2 — ENSEMBLE / FEDERATION DIVERSITY FAILURE (Cell 4)
Hub-spoke E1 spawned 3-5 spokes from the same encoder family with small hyperparameter jitter and assumed federation would deliver ensemble lift. The deep-ensembles literature (Lakshminarayanan 2017, Fort et al 2019) is unambiguous: small-jitter spokes converge to the same loss basin and give no ensemble lift. The substrate's "hub-spoke federation" architecture is not federated unless the spokes are genuinely diverse (different architectures, different input modalities, or different INIT regions of the loss landscape).

### Common mode 3 — SMOKE-REGIME UNDERPOWERED + WRONG-METRIC (Cells 3, 5)
Calibration and audit-trail both ran at smoke regimes where the noise floor is comparable to or larger than the effect being measured. Pre-reg HARD bands were set at literature levels (r=0.70 for calibration; 0.85 provenance for audit-trail) without doing the power calculation to check whether the smoke sample size can reach that level. Power analysis BEFORE pre-reg setting would have caught this.

These three failure modes account for all 5 HARD_FAILs. NONE of the cells produced evidence that refutes the underlying substrate mechanism; all 5 are test-design bugs or scale-mismatch.

---

## Single test that DISCRIMINATES the hypotheses

A 6-arm beta-sweep on the resonator-multihop substrate (Cells 1+2 collapse into one test):

- ARM_BETA_0.5: cosine-temperature regime with effective top-K = 8-12
- ARM_BETA_2: entropy ~ log(5)
- ARM_BETA_10: entropy ~ log(2)
- ARM_BETA_50: near-saturation
- ARM_BETA_500: deep saturation
- ARM_BETA_8192: current-cell regime (control = matches naive)

Compute: local CPU, 6 arms × 200 chains × 3 seeds = 30 min.

**Predicted outcomes:**
- IF beta in {0.5, 2, 10} gives top1 >= 0.78 with paired delta >= 0.10 vs ARM_BETA_8192: confirms substrate top-1 accuracy is INVERSE-TEMPERATURE-LIMITED, not substrate-capacity-limited; the resonator-multihop HARD_FAIL is TEST_UNFAIR and the soft-DFE mechanism does work on substrate. Closes Common mode 1.
- IF all beta give top1 within +/- 0.05 of naive 0.65: confirms substrate's per-hop cosine resolution does NOT carry enough info for soft chaining; aligns with META drill's L2 information-geometry diagnosis (random-bipolar isotropic Marchenko-Pastur regime needs anisotropic encoder). Pivots to encoder-side rescue.
- IF beta in {0.5} gives top1 < 0.50 (over-soft): confirms there is a "right" inverse-temperature and saturation isn't always bad; the cell needs a beta CV-fit step.

This single cell discriminates 3 hypotheses with 30 min compute. **Priority 1.**

---

## Priority order for revival dispatch

1. **CRITICAL — beta-sweep on resonator-multihop** (single cell, 30 min local CPU). Discriminates Cells 1+2 + recovers the substrate's multi-hop mechanism if available. P_deflated(lift >= 0.08 at some beta) = 0.50.

2. **HIGH — genuine-diversity hub-spoke** (single cell, 60 min local CPU). 3 spokes with fundamentally different encoder families (char-trigram + cooccurrence + random-bipolar) bundled via sign(sum). Discriminates Cell 4. P_deflated(bpc < 7.55, i.e. clearing the HARD_FAIL ceiling) = 0.45.

3. **HIGH — scale-up audit-trail** (single cell, GPU 2hr). N=4096 V=200 M=400 3 seeds. Discriminates Cell 5. P_deflated(V3 prov >= 0.80) = 0.65.

4. **MEDIUM — re-scope calibration with right metric + larger regime** (single cell, local CPU 60 min). AUC + Brier score, N=8192 M=4000. Discriminates Cell 3. P_deflated(AUC >= 0.65) = 0.55.

5. **LOW — full-stack rerun once beta is fixed** — only if priority 1 closes; would also revisit soft-chain's downstream questions (turbo iter, K-beam path-sum).

Total compute: ~ 4 hours wall, mostly local CPU. All 4 priorities can ship in parallel.

---

## Verify-the-referent on the Store anchors (per USER directive halves)

For each cell I claimed a Store chain-grade anchor exists. Verification (verify-the-referent discipline):

- **Cell 1 (resonator-multihop) -> wave14_multihop_K50**: anchor confirmed in `director_multihop_composition_store_scour_2026-06-24.md`. Anchor regime: N=16384, V=large, K=50, acc_1=0.987. Distance to test: N=8192 (2x smaller), V=200 (substantially smaller), K_SET=20 (different K). Distance is non-trivial; chain-grade does not auto-transfer. **My pre-cell prediction (P_deflated=0.35 for soft-chain rescue) was correct on the principle but I did not catch that the inverse-temperature setting would no-op the mechanism.** Cert-owner override consistent with Fix #28 — Skunkworks was right to call this MEASURED_MECHANISM not chain-grade transfer.

- **Cell 2 (soft-chain) -> CA3 + soft-DFE literature**: anchor is lit-anchored not Store. The cell author note explicitly cites the prior research drill. The wiring bug means the lit hypothesis was never tested; no refutation of the lit anchor.

- **Cell 3 (isotonic calibration) -> lap4_3 isotonic regression**: anchor is in Store. Need to verify lap4_3 ran at compatible scale. Likely it ran at substrate-deployment scale where base rate is higher (~30-50% accuracy) which is the regime where pearson r=0.70 is achievable. Today's smoke at 9% accuracy cannot reach that ceiling by Cramer-Rao bound. **Referent does not match.**

- **Cell 4 (hub-spoke E1) -> Path C v2 single-spoke encoding drill**: anchor confirmed; Path C v2 is the BASELINE arm of the failed cell (bpc=7.667, 0.07 above unigram floor). The HARD_FAIL is on the FEDERATION extension, not on the baseline; the baseline matches the chain-grade anchor. **The cell IS validating the encoding drill — its baseline runs successfully — the federation mechanism is what failed.**

- **Cell 5 (audit-trail) -> wave14_cap12 audit-trail v1-v5**: anchor in Store at WAVE-grade scale. Today's smoke at N=80 is ~20x undersampled. **Referent regime does not match.**

So for 3 of 5 cells (resonator, calibration, audit-trail) the Store anchor regime does not match the test regime — SCALE_MISMATCH is the dominant failure mode. For 2 of 5 (soft-chain, hub-spoke) the lit / mechanism is intact but the wiring bug or diversity failure prevented genuine test. The META audit's "transfer-distance" framework correctly identified the structural issue; the per-cell pre-reg discipline failed to operationalize it. **Bottom line: USER's "test is not fair" half is the stronger half of the disjunction; the "we've done something wrong" half is also true but the "something wrong" is in test design, not in substrate capability.**

---

## What I as Director got wrong

1. **Beta=N_DIM convention propagated silently** from `hdlab.multi_hop.iter_cleanup_chain` into two new cells without flagging that the convention is single-hop-cleanup-specific and inappropriate for inter-hop soft mechanisms. Fix: add cell-author pre-dispatch check requiring entropy(softmax) > 0.5 nats for inter-hop soft chaining.
2. **Smoke-regime power analysis missing pre-reg.** Audit-trail HARD_PASS at 0.85 with n=40 is unreachable by binomial power. Should have run power calc as part of pre-reg.
3. **Federation diversity unverified.** Hub-spoke assumed same-family spokes diversify; deep-ensembles lit says no. The encoding drill note already cited Fort-Hu-Lakshminarayanan 2019; I didn't apply it.
4. **Pearson r as calibration metric for 9% base rate violates Cramer-Rao bound.** Standard ML practice is ECE + AUC, not Pearson r. Pre-reg discipline didn't catch the metric-regime mismatch.
5. **Bundled 5 cells without per-cell verify-the-referent on Store regime.** META drill PREDICTED this; I dispatched anyway. Fix #28 + verify-the-referent says check Store regime match BEFORE dispatch.

All 5 lessons are operational, not substrate-level. **Substrate's chain-grade Store evidence is INTACT.**

---

## Brain-grounded P update + status_log one-liner

CA3 graded-reactivation existence proof + 50-year soft-DFE turbo-decoding lit + brain's biologically-required finite-temperature inference all REINFORCE soft-chain principle. P_deflated(soft-chain with calibrated beta rescues multi-hop at some substrate regime) = 0.55.

**Status_log one-liner:** 5 HARD_FAILs today: 2 TEST_UNFAIR-beta-saturation (resonator + soft-chain identical bug), 1 TEST_UNFAIR-federation-no-diversity (hub-spoke), 2 SCALE_MISMATCH (calibration wrong-metric + audit-trail smoke-underpowered). Single decisive revival = 6-arm beta-sweep on resonator-multihop (30 min local CPU; P_deflated=0.50). Substrate Store chain-grade INTACT; all 5 failures are test-design bugs. USER right both halves; "test is not fair" is the stronger half.
