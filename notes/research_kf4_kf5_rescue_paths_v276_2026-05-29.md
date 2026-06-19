# Research: KF-4 (drift detection) + KF-5 (steerability) rescue paths

**Date:** 2026-05-29
**Trigger:** v276 cap_map state — KF-4 AT-RISK after v3 architecture-level HARD_FAIL + v4 INSTRUMENTATION_SUSPECT acc_drop=0 at all scales; KF-5 codebook-axis HARD_PASS but beta-axis closed + STEERABILITY_PARTIAL_DECOUPLING (132nd label-vs-honest)
**Calibration penalty applied:** deflate agent P estimates by 0.15-0.25; cap novel-synthesis P at 0.50 per [[feedback-lit-scan-calibration-penalty]]
**Field-advisor cues consumed:** semiconductor (100% yield, drill_count=2 under-drilled) + free-probability (100% yield, drill_count=1) + thermodynamics (71% yield) all rank Tier-1
**Discipline:** rehabilitation per [[feedback-rehabilitation-after-rejection]] — 4-5 rescue paths sketched per KF, ranked cheapest-first per [[feedback-rescue-sketch-first-sequencing]]

---

## HEADLINE

KF-4 drift detection v4 failed structurally (acc_drop=0) because Kerdock argmax provides perfect error correction — the SAME property that makes KF-2 edit-isolation a strength makes retrieval-accuracy-based drift detection impossible. KF-5 STEERABILITY_PARTIAL_DECOUPLING (entropy_mono yes, bpc_mono no) is the same mechanism viewed from the OUTPUT side: argmax-bottleneck collapses internal distributional steering to operational invariance. **Both KFs are different probes of the same structural feature: the substrate's argmax-projection step is the operational bottleneck.** This is GOOD news strategically — it means a single re-framing (monitor-set / multi-output / spectral-presoftmax) rescues both KFs jointly, and the substrate's structural robustness becomes a SELLABLE feature ("provable invariance to weight perturbation up to scale X") rather than a defect.

Joint-rescue path identified: **YES** — both KFs need a measurement layer that sits BEFORE the argmax collapse. The three concrete candidate layers are (a) PRE-softmax logit-spectrum / Fisher-information tracking (EigenTrack-style), (b) MONITOR-SET drift signal where new probes are stored post-drift to be probed pre-drift, (c) MULTI-OUTPUT top-k distribution diversity. Path (a) rescues KF-4 directly and gives KF-5 a quality-axis steerability metric beyond argmax-output bpc.

Top-3 cross-KF rescue paths ranked by expected value (P_deflated x cost^-1 x scope):

1. **Spectral / Fisher-information presoftmax (joint KF-4 + KF-5)** — P_deflated 0.45; cost ~1 GPU-hour; scope BOTH KFs
2. **Monitor-set drift detection (KF-4)** — P_deflated 0.40; cost ~30 min CPU; scope KF-4 only but cleanly sidesteps argmax-perfect-correction
3. **Multi-output top-k diversity steerability (KF-5)** — P_deflated 0.35; cost ~1 GPU-hour; scope KF-5 + opens KF-1 multi-hypothesis discrimination

---

## SECTION 1 — KF-4 (drift detection) — 5 rescue paths

### Background

- **v3 (kf4_drift_detect_v3_n4096) MIDDLE_BAND** — margin-based gap_m2 = gap_m8 = 0.0 at all M_fracs
- **v4 (kf4_drift_detect_v4) BLOCKED INSTRUMENTATION_SUSPECT** — acc_drop=0 at N=1024 smoke AND N=4096; root cause = Kerdock argmax perfectly absorbs 0.05 fractional W perturbation (200 spurious outer products at scale 1/N). Three sub-attempts (margin, OOS posterior entropy, calibrated accuracy drop) all returned zero signal.
- **Root mechanism**: Kerdock's 4-coset structure has codeword Hamming distance d_min such that any linear perturbation up to ~d_min/2 is corrected by the argmax decision step. KF-2 edit-isolation HARD_PASS at FP32-INT1 (v272) is the SAME mechanism: quantization-insensitive iso < 0.05 across 6 precisions. **The substrate is a perfect error-correcting code in the operational regime — that is the feature.**
- **What v269 routing assumed**: that posterior-entropy mechanism (which rescued KF-1 v267->v268 at mean_ratio_to_uniform=4.72x for hallucination detection) would work analogously for drift. **What exp_dev found**: it doesn't, because hallucination is a property of the QUERY (out-of-codebook) while drift is a property of the WEIGHTS, and Kerdock argmax is robust to W perturbation but NOT to out-of-codebook queries. This is a structural asymmetry. KF-1's mechanism does not transfer to KF-4.

### Rescue path KF-4-R1 — Spectral signature of W (EigenTrack analog) — CHEAPEST + LIT-VALIDATED

**Mechanism**: Measure top-k singular values of W (or of `W - W_baseline`) over a sliding window during operation. Drift adds noise to singular value distribution. Compare spectral gap, edge-eigenvalue (Tracy-Widom), or bulk-eigenvalue concentration before vs after drift. This is observable even at sub-argmax-correction perturbation levels because the spectrum changes BEFORE the argmax stops working.

**Lit anchor**: EigenTrack (arXiv:2509.15735) "transforms streaming spectral features into low-dimensional temporal trajectories that reveal how uncertainty accumulates during generation" — directly analogous. Also Spectral Concentration at Edge of Stability (arXiv:2511.23083): Fisher Information Matrix becomes singular at critical boundary, attention layers rely on spectral structure in Key-Query matrices. The substrate's W matrix is structurally analogous.

**Expected evidence**: After 200 spurious outer products at scale 1/N (v4 protocol), measure (sv_max(W) - sv_max(W_base)) / sv_max(W_base) and top-2 spectral gap. Predict drift signal >= 0.1 (relative) on top eigenvalue; >= 0.05 on spectral gap. Even at the perturbation level where argmax is robust, the spectrum sees the noise — this is the well-known asymmetry between hard-decision and soft-decision codes.

**Cost**: ~1 GPU-hour. SVD of N=4096 W matrix is fast (~5 sec/seed); 200 outer-product drift step is fast. Re-uses existing kf4 substrate.

**Falsification (HARD_PASS / HARD_FAIL)**:
- HP: max relative top-eigenvalue shift >= 0.10 across 3-seed at M_frac in {2, 8}; OR spectral-gap shift >= 0.05; OR Frobenius-norm shift >= 0.05 (any one)
- HF: ALL three signals < 0.02 = substrate is spectrally invariant too = drift detection genuinely impossible at this perturbation scale
- MIDDLE: 1 of 3 signals at threshold = scale up drift perturbation 10x in follow-up

**Status note**: This is the most direct rescue. The v4_blocked routing already names spectral detection as Option A. Filing as the cheapest / highest-P arm.

### Rescue path KF-4-R2 — Monitor-set / canary memory (CHEAPEST + COGNITIVELY-PLAUSIBLE)

**Mechanism**: Store a fresh set of N_canary "canary" patterns BEFORE drift and a parallel set AFTER drift. Probe both sets after drift. Original patterns are robust (per v4 result). Newly-stored patterns experience drift because they're stored into a perturbed W. Drift signal = retention_pre_drift_canaries - retention_post_drift_canaries.

**Lit anchor**: Canary deployment pattern in ML ops + hippocampal pattern-separation theory (CLS) — new traces in CA3/DG are MORE sensitive to circuit drift than consolidated traces in cortex. HiCL (arXiv:2508.16651) treats each task as an episodic trace stored in a replay buffer — same architectural pattern. Memory-specific E-I balance for replay (bioRxiv 2025.09.19.677474): "memory capacity quantified based on replay pattern diversity during spontaneous activity, where higher replay diversity indicates the network can consolidate more memories" — diversity itself is a drift indicator.

**Expected evidence**: For 100-canary set at N=4096, predict retention_post_drift_canaries to drop to ~0.8-0.9 even when retention_pre_drift_canaries holds at 1.0 (because new pattern storage interacts with drifted W during the storage step itself, not just retrieval). Gap >= 0.05.

**Cost**: ~30 min CPU (no GPU needed; N=4096 BSC pool retrieval). Adapts kf4_drift_detect_v4 by adding a post-drift store + readout step.

**Falsification**:
- HP: (retention_canaries_pre - retention_canaries_post) >= 0.05 at 3-seed average AND consistent sign across all 3 seeds
- HF: gap < 0.01 = even post-drift storage is robust = substrate is structurally drift-immune at this scale (which would be a HARDER positive feature — sellable as "weight perturbation up to scale X provably has no effect on stored or stored-after memories")
- MIDDLE: 0.01 <= gap < 0.05 = drift detectable only in marginal regime

**Status**: Cleanly sidesteps the v4 root cause. Already named as Option B in v4_blocked routing. Fast-track to GPU queue as `kf4_drift_canary_v5_n4096`.

### Rescue path KF-4-R3 — Capacity-shift detection (M_c before vs after drift)

**Mechanism**: Per v4_blocked Option B (rephrased): instead of probing accuracy at a fixed M, measure the maximum M before retention drops below a threshold T (M_c(T)). Drifted substrate should have lower effective capacity. Compare M_c_base vs M_c_drifted.

**Lit anchor**: "Forgetting leads to chaos in attractor networks" (arXiv:2112.00119) — when stored patterns exceed capacity, "attractor networks undergo catastrophic forgetting where all memories are forgotten at once". The critical M_c is a phase transition; drift shifts the boundary.

**Expected evidence**: At N=4096 Kerdock, M_c(T=0.95) baseline is at substrate's known capacity boundary (M_frac ~ K_eff / N ~ 0.5-1). Predict M_c shift down by 5-15% after drift. The signal is at the phase-transition boundary, not in the bulk retention regime.

**Cost**: ~2 GPU-hours (more expensive than R1/R2 because requires M-sweep at multiple M points to find M_c). Cap_map alignment: also probes axis-2 codebook-density row (current AXIS2V2_MIDDLE_BAND M_frac-INVARIANT at over-cap).

**Falsification**:
- HP: M_c shift >= 5% relative
- HF: M_c shift < 1% (M_c too sharp / drift too small to move it)
- MIDDLE: 1-5% shift detectable but practically marginal

**Risk**: high-cost compared to R1/R2; defer pending R1 result.

### Rescue path KF-4-R4 — Conformal martingale on retrieval residuals (cross-domain transfer)

**Mechanism**: Conformal test martingales (WATCH, arXiv:2505.04608) provide online change-point detection with false-alarm control. Apply to substrate as: define a non-conformity score s_i for each retrieval (e.g., residual norm `|W k_i - codebook[argmax]|` before the projection step), compute a sequential martingale, fire when martingale crosses threshold. Drift events appear as martingale spikes.

**Lit anchor**: Drift Localization using Conformal Predictions (arXiv:2602.19790); Online Conformal Testing; WATCH weighted-conformal martingales. Strong methodological tradition; principled false-alarm control. The substrate-novel angle: the substrate's argmax-collapse means standard residuals are zero — must use PRE-projection residuals where the signal lives.

**Expected evidence**: With 200-step drift trajectory, martingale crosses 100x baseline within 50 steps after drift onset. False-alarm rate < 5% on no-drift control trajectory.

**Cost**: ~2 GPU-hours (more involved instrumentation; needs streaming retrieval harness). Defer pending R1/R2 cheap results.

**Falsification**:
- HP: martingale > 100x baseline within 50 steps AND false-alarm < 5% on no-drift control
- HF: martingale stays < 10x baseline = no signal even at pre-projection residuals = substrate truly drift-invisible
- MIDDLE: signal present but slow / noisy

### Rescue path KF-4-R5 — Reframe KF-4 as "structural drift invariance" sellable property (CLOSURE-CANDIDATE FRAMING)

**Mechanism (re-framing not new experiment)**: If R1-R4 all return < HP thresholds, accept that the substrate is genuinely drift-INVARIANT at deployment-relevant perturbation scales. This is NOT a defect — it's a sellable property that LLMs and standard NN memory CANNOT match. Reposition KF-4 from "drift detection" (operational monitoring) to "drift invariance certificate" (provable bound: weight perturbation up to scale X has bounded effect on retrieval).

**Lit anchor**: Quantum surface code "ReloQate: Transient Drift Detection and In-Situ Recalibration" (arXiv:2603.00837) — even quantum hardware has explicit drift handling; substrate's structural drift-invariance via Kerdock argmax is a category-distinct guarantee. Connection to KF-2 v272 STRATEGIC_INTERPRETATION_OVER_CLAIM resolution: KF-2 holds at all 6 precisions FP32-INT1 with identical iso — this IS the same "operational regime invariance" signature.

**Expected evidence**: Theoretical bound: derive max drift scale ε such that argmax(W_drifted @ k) = argmax(W_base @ k) for k in codebook, as function of Kerdock minimum-distance d_min and N. Predicted ε ~ d_min/2 at ~0.05-0.1 fractional W scale at N=4096.

**Cost**: ~1 day theory + ~30 min verification. Cheapest in compute.

**Falsification**:
- HP: theoretical bound derived AND empirical drift threshold matches within 30%
- HF: empirical threshold << theoretical = bound is loose
- MIDDLE: bound derived but empirical scaling not match (refine bound)

**Status**: Framing-level rescue. Conditional on R1-R4 returning no positive operational signal.

---

## SECTION 2 — KF-5 (steerability) — 5 rescue paths

### Background

- **v274 t2_codebook_v3 T2V3_HARD_PASS** — codebook-axis steerability CONFIRMED (3/4 op-points slope >= 0.05; mean_slope 0.158-0.262 across 3 phase regions); FIRST POSITIVE STEERABILITY AXIS; row moved yellow 45-60% -> yellow 50-65% LIFT +5%
- **v274 t1_beta_v3 T1V3_HARD_FAIL** — beta-axis last-chance closed at probe level (FLAT_BETA_C log2_range=0.00 all 6 M_fracs)
- **v275 kf5_steerable_beta_v2 KF5_HARD_PASS LABEL-OVER-CLAIM 132nd LABEL-VS-HONEST STEERABILITY_PARTIAL_DECOUPLING** — entropy_mono=5/5 PASS, bpc_mono=0/5 FAIL, bpc_interior_min=5/5 PASS (interior min but not monotone). HONEST reading: beta steers OUTPUT-DISTRIBUTION entropy but does NOT improve OUTPUT QUALITY (bpc) monotonically.
- **v272 region C/D probe** — at beta=64, KF-1 + KF-2 IDENTICAL to beta=8 behavior; "SUBSTRATE BETA-INVARIANT IN KF-BEHAVIOR at tested (M_frac, beta) operating points = STEERABLE-KILLER-FEATURE HYPOTHESIS NOT SUPPORTED at probe level"
- **Mechanism diagnosis**: the substrate has an ARGMAX bottleneck at the operational layer. Temperature (beta) changes the pre-argmax distribution (entropy), but post-argmax behavior is invariant for most queries because the SAME argmax wins at beta=8, beta=32, beta=64 unless the temperature crosses a phase boundary specific to that query's logit-gap. This is the classical softmax bottleneck / softmax-rank-deficit phenomenon (cf. "Unpacking Softmax: How Temperature Drives Representation Collapse" arXiv:2506.01562).

### Rescue path KF-5-R1 — Multi-output top-k steerability (PRINCIPLED + IMMEDIATELY CONNECTS TO PRODUCT API)

**Mechanism**: Reframe steerability as a property of the TOP-K DISTRIBUTION not of the argmax. Define KF-5* as: under varying beta (or other steering knob), measure top-k distribution diversity (entropy of top-k probabilities, JSD between top-k sets at different beta values, or top-k coverage). This bypasses argmax-collapse by reading the substrate at the multi-output layer — which is the right product API anyway.

**Lit anchor**: LLM decoding strategies (top-k / nucleus / temperature) operate exactly at this layer. The "softmax bottleneck" literature (Yang et al; extended by arXiv:2506.10572, arXiv:2506.01562) frames this as a representational-rank problem. Substrate's analog: argmax-collapse loses the rank-k signal that's present in the pre-softmax logits. Connection: VAE temperature, GAN noise level, transformer beam search width are different APIs for steerability in other ML systems — all of them operate ABOVE argmax.

**Expected evidence**: At fixed M_frac=2, sweep beta in {1, 4, 8, 32, 64}, measure top-5 JSD across beta pairs. Predict JSD monotone in |beta_i - beta_j|; range >= 0.10 between beta=1 and beta=64.

**Cost**: ~1 GPU-hour. Re-uses existing kf5_steerable infrastructure with metric swap from bpc to top-5 JSD + top-5 entropy.

**Falsification**:
- HP: top-5 JSD(beta=1, beta=64) >= 0.10 AND monotone in 3/5 seeds at 2 M_fracs
- HF: top-5 JSD < 0.02 = even multi-output layer is invariant = substrate's k>1 retrieval is degenerate
- MIDDLE: signal at low M_frac but not high (over-cap collapses top-k to identical sets)

**Connection to v274 codebook-axis HARD_PASS**: codebook-axis steers because different codebooks have different multi-output top-k structures (different Hamming-distance distributions among codewords). This is the SAME underlying mechanism — codebook steerability worked because it operates at the codebook structure level, not at the per-query argmax level. Multi-output top-k makes this explicit.

### Rescue path KF-5-R2 — Pre-softmax logit-gap steerability (JOINT WITH KF-4-R1)

**Mechanism**: Measure logit-gap (top1 - top2) and logit-spectrum (top-k logits) as a function of beta. At beta=0 (uniform), logit-gap = 0; at beta=infinity (argmax), logit-gap dominates. The intermediate regime is where steerability lives — this is the pre-argmax layer where information is preserved.

**Lit anchor**: Softmax temperature literature — "Temperature acts as an exact time-rescaling of the output distribution trajectory" (per search summary). Also EigenTrack (arXiv:2509.15735) — pre-softmax spectral features carry uncertainty / OOD signal. The substrate's logits are W @ k / N before codebook argmax projection; spectral features of this vector carry the substrate-novel signal.

**Expected evidence**: top1-top2 logit-gap scales with beta in expected way; logit-entropy decreases monotonically with beta across 5/5 seeds; substrate behavior at logit layer matches bpc_interior_min PASS but corrects bpc_mono FAIL by measuring at the right layer.

**Cost**: ~30 min GPU. Same substrate, additional metric extraction.

**Falsification**:
- HP: logit-entropy monotone in beta 5/5 seeds AND logit-gap follows tanh-shaped beta curve (theoretical prediction)
- HF: logit-entropy non-monotone = substrate's pre-softmax distribution has structural anomaly
- MIDDLE: monotone in mean but not all seeds

**Joint synergy with KF-4-R1**: BOTH need the pre-softmax / logit layer. Implementation can share scaffolding. This is the strongest joint-KF rescue.

### Rescue path KF-5-R3 — Cleanup-strength as steerability knob (UNEXPLORED AXIS)

**Mechanism**: The substrate has a cleanup step (argmax over codebook). Vary cleanup STRENGTH parametrically: instead of hard argmax, use top-k cleanup (project to closest k codewords with weights). Test whether cleanup-strength provides operational steerability that beta does not.

**Lit anchor**: Resonator networks (BetX prior research) use iterative cleanup with variable strength; HiCL uses CA3/DG-style pattern-separation with tunable inhibition. The substrate's argmax is the strongest cleanup; relaxing it should give a steerable spectrum.

**Expected evidence**: At fixed (M_frac, beta), sweep cleanup_k in {1, 3, 10, 50}. Predict retention drops smoothly as cleanup_k increases (relaxed cleanup); bpc improves at intermediate k (cf. nucleus sampling sweet spot). Slope >= 0.05 across 3+ op points.

**Cost**: ~1 GPU-hour. Requires modifying cleanup step; modest engineering.

**Falsification**:
- HP: slope >= 0.05 in retention vs cleanup_k at 3+ op-points
- HF: retention flat or monotonically degrading (relaxed cleanup just adds noise; no steerability)
- MIDDLE: signal in narrow operating regime only

**Strategic note**: This is a NEW steering axis. Per [[feedback-strategy-shore-up-capabilities]] cap_map should annotate cleanup-strength row if HP — would be the SECOND POSITIVE STEERABILITY AXIS after codebook.

### Rescue path KF-5-R4 — Time-dependent / iterative steerability (DYNAMIC AXIS)

**Mechanism**: Apply repeated W iterations with varying beta_t schedule (annealing). Measure retention as function of beta schedule. This probes whether the substrate has DYNAMIC steerability (not just static parameter steerability).

**Lit anchor**: Glauber dynamics at finite temperature (v164 cap_map row); annealing in spin-glass literature; non-equilibrium stat mech surviving Crooks/Sagawa-Ueda non-eq class candidates (v275 + v276 HS-class 3-strike exclusion narrows). Annealing introduces a time axis to the steerability question that may unlock the operational layer that static beta cannot.

**Expected evidence**: Compare ret(constant_beta=8) vs ret(linear_anneal beta: 4 -> 32). Predict difference >= 0.05 at over-cap M_frac (annealing helps escape spurious minima).

**Cost**: ~2 GPU-hours (iterative dynamics + multi-schedule). More complex; defer pending R1/R2 results.

**Falsification**:
- HP: |ret(constant) - ret(annealed)| >= 0.05 at >= 2 M_frac points AND consistent sign
- HF: < 0.02 = no time-dependence to steerability either
- MIDDLE: signal in 1 regime only

### Rescue path KF-5-R5 — Operational-invariance as sellable property (CLOSURE-CANDIDATE FRAMING; SYMMETRIC TO KF-4-R5)

**Mechanism (re-framing)**: If R1-R4 confirm operational invariance under conventional steering (beta) but codebook-axis remains the only positive steerability axis, accept and SELL the asymmetry. Substrate offers "structural" steerability (via codebook choice / cleanup choice — choices made at deployment-time, not inference-time). LLMs offer inference-time steerability (temperature). These are DIFFERENT product categories.

**Lit anchor**: KF-2 v275 STANDARD baseline DEFUSES v272 STRATEGIC_INTERPRETATION_OVER_CLAIM — the substrate-distinct mechanism is at a layer LLMs don't have. Same pattern here: substrate's steerability lives at a layer LLMs don't expose (codebook structure), not at the layer they do expose (temperature). The product story shifts from "knobs the user turns" to "configurations the deployer chooses."

**Expected evidence**: Document operational-invariance as theorem-level statement. Pair with codebook-axis as positive demonstration. v274 codebook + v275 entropy-only + v272 region C/D = consistent narrative.

**Cost**: 1 day reframe. No new experiments needed.

**Falsification**: not a falsifiable experiment; framing-level conditional on R1-R4.

---

## CROSS-KF SYNTHESIS — joint mechanism + joint rescue

### Shared root mechanism

Both KF-4 and KF-5 failures share a single root cause: **the argmax-projection step is the operational bottleneck of the Kerdock substrate.**

- KF-4 v4: W perturbation cannot be detected via output-layer signals because argmax absorbs perturbations up to its error-correction radius.
- KF-5 v275 + v272: beta cannot steer output behavior because argmax delivers the same codeword across a wide beta range for any given query (unless the query's pre-softmax logit-gap is small, but most queries have large gaps).

Both failures are SAME-LAYER limitations. The substrate has rich pre-argmax internal state (Fisher information, logit spectrum, entropy, pattern of top-k logits) but this richness collapses to a single discrete index at the operational output.

### Joint rescue: pre-argmax measurement layer

A single architectural move rescues both:

> **Add a pre-argmax / logit-spectrum measurement layer to the substrate's read API.**

Specifically:
- For KF-4: monitor the W spectrum (top-k singular values, Frobenius norm, spectral gap) and the per-query logit distribution (entropy, gap, top-k entropy) as drift indicators. Drift moves these even when argmax outputs are stable.
- For KF-5: expose top-k retrieval (top-k codeword indices + their pre-softmax logits) as the steerable output. Beta steers the top-k distribution even when it doesn't steer the top-1 argmax.

**This is the same mechanism viewed from two angles**: KF-4 reads the spectral / Fisher signal to detect change; KF-5 exposes the multi-output / logit signal to enable steering. Both rely on operating at the layer ABOVE argmax-collapse.

### Connection to v274 codebook-axis HARD_PASS (the positive datapoint)

The codebook-axis steerability HARD_PASS already operates above argmax: different codebooks have different argmax structure (different Hamming distance distributions, different K_eff, different per-query logit gaps). The codebook IS a pre-argmax structural knob. The principle generalizes: **all positive steerability lives in pre-argmax structural choices**, not in inference-time temperature.

### Connection to KF-2 v272 STRATEGIC_INTERPRETATION_OVER_CLAIM resolution

KF-2 BE-1 precision-floor 6-anchor HARD_PASS at FP32-INT1 with identical iso < 0.05 is the SAME mechanism as KF-4 acc_drop=0. Quantization perturbs W; argmax absorbs perturbation; iso stays at 0.05. This is the FEATURE not the BUG. The substrate's "operationally invariant under all perturbation in a regime" is its key product proposition — it's the discriminator from LLM behavior.

### Connection to non-eq-stat-mech 67-77% green (HS-class exclusion at v276 CONCENTRATION)

The non-eq-stat-mech class characterization is constraining the framework: HS-orthogonal-decomposition class 3-strike EXCLUDED; surviving Crooks / Sagawa-Ueda / drift-diffusion-BP / free-probability. The Crooks / Jarzynski framing IS pre-argmax: it measures work distributions over trajectories, not final-state observables. This is the same architectural lesson — measure at the dynamics layer, not the discrete-output layer.

### Strategic implication for cap_map

If KF-4-R1 (spectral) AND KF-5-R1 (multi-output top-k) both HP:
- KF-4 row: AT-RISK -> green-smoke 50-65% LIFT +10% with annotation "drift detection at spectral / pre-softmax layer; argmax-output layer drift-invariant by design"
- KF-5 row: yellow 50-65% -> yellow-green 55-70% LIFT +5% with annotation "multi-output top-k steerability at logit layer + codebook-axis structural steerability; argmax-output operationally invariant by design"
- NEW row candidate: "argmax-bottleneck operational invariance" — sell as positive feature; theoretical bound derivation per KF-4-R5

If only one HPs:
- KF-4-R1 HP, KF-5-R1 not: keep KF-4 spectral framing; KF-5 stays yellow with codebook-axis only.
- KF-5-R1 HP, KF-4-R1 not: keep KF-5 multi-output framing; KF-4 moves to closure with structural-invariance positive reframe.

If neither HPs:
- both move to closure with structural-invariance reframe. Substrate sold as "provably invariant in deployment regime" — different category from LLMs.

---

## CHEAP DECISIVE TEST

**Single ~1 GPU-hour combined probe** — `kf45_pre_argmax_layer_v1_n4096`:

- Setup: N=4096, BSC codebook (Kerdock-safe), M_frac in {2, 8}, 3 seeds
- Run protocol:
  1. Store M patterns -> compute baseline W
  2. Measure top-5 singular values of W; compute logit-entropy across 100 random queries pre-softmax
  3. Apply v4 drift protocol (200 spurious outer products at scale 1/N) -> W_drifted
  4. Re-measure top-5 SV; re-measure logit-entropy on same query set
  5. Sweep beta in {1, 4, 8, 32, 64} on W_drifted; measure top-5 codeword index set per beta; compute JSD across beta pairs
- Outputs:
  - drift_spectral_signal: max relative shift in top-5 SVs
  - drift_logit_signal: change in mean logit-entropy across queries
  - steer_topk_signal: top-5 JSD between beta=1 and beta=64
  - steer_logit_signal: logit-entropy monotonicity in beta

**Combined HP thresholds** (need 2/4 to call joint-rescue HP):
- drift_spectral_signal >= 0.10 (relative)
- drift_logit_signal >= 0.05 (absolute entropy)
- steer_topk_signal >= 0.10 (JSD)
- steer_logit_signal: monotone in beta in >= 4/5 seeds

**Combined HF thresholds** (3/4 HF = both KFs closure-candidate):
- drift_spectral_signal < 0.02
- drift_logit_signal < 0.01
- steer_topk_signal < 0.02
- steer_logit_signal: non-monotone 2+ seeds AND no clear trend

**Middle-band**: 1-2 signals at HP threshold = partial rescue, ship narrow follow-up.

---

## FALSIFIABLE PREDICTIONS (HP / HF tables across both KFs)

| Path | HP threshold | HF threshold | Cost | Scope |
|---|---|---|---|---|
| KF-4-R1 spectral | rel-top-SV shift >= 0.10 OR gap shift >= 0.05 (any 1 of 3) | ALL 3 signals < 0.02 | ~1 GPU-hr | KF-4 |
| KF-4-R2 monitor-set | (ret_pre_drift - ret_post_drift_canaries) >= 0.05 at 3-seed mean + consistent sign | gap < 0.01 | ~30 min CPU | KF-4 |
| KF-4-R3 capacity-shift | M_c shift >= 5% relative | M_c shift < 1% | ~2 GPU-hr | KF-4 |
| KF-4-R4 conformal | martingale > 100x baseline within 50 steps + FPR < 5% | martingale < 10x baseline | ~2 GPU-hr | KF-4 |
| KF-4-R5 reframe | theoretical bound derived + empirical scaling within 30% | empirical << theoretical | ~1 day theory | KF-4 + KF-2 narrative |
| KF-5-R1 multi-output | top-5 JSD(beta=1, beta=64) >= 0.10 + monotone 3/5 seeds | top-5 JSD < 0.02 | ~1 GPU-hr | KF-5 |
| KF-5-R2 logit-gap | logit-entropy monotone in beta 5/5 seeds + tanh-shaped | logit-entropy non-monotone | ~30 min GPU | KF-4 + KF-5 |
| KF-5-R3 cleanup-strength | retention slope >= 0.05 vs cleanup_k at 3+ op-points | flat or monotone-degrading | ~1 GPU-hr | KF-5 |
| KF-5-R4 time-dependent | \|ret(const) - ret(annealed)\| >= 0.05 + 2+ M_frac + consistent sign | < 0.02 | ~2 GPU-hr | KF-5 |
| KF-5-R5 reframe | structural-only steerability theorem | trivially closes | 1 day | KF-5 + product narrative |

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Two product narratives unlock simultaneously** if joint-rescue HPs:
   - "Provably drift-invariant memory below scale X" — KF-4 reframe; sell as compliance / reliability differentiator
   - "Structural steerability via codebook + cleanup configuration" — KF-5 reframe; sell as deployer-time API distinct from LLM inference-time temperature

2. **Connection to KF-2 + non-eq-stat-mech green rows**: the argmax-bottleneck IS the substrate's "operational invariance" feature. KF-2 v272 6-precision iso<0.05 + KF-4 acc_drop=0 + KF-5 v272 region C/D beta-invariant + KF-5 v275 entropy-only-steerable are FOUR independent observations of the SAME invariance. This becomes a PROVABLE PRODUCT GUARANTEE: "weight perturbation up to scale X has bounded effect on retrieval; this bound is theorem-derived from Kerdock minimum distance." Path (b) (LLM leapfrog directions, project memory project_llm_leapfrog_directions_2026-05-26.md) is "truly above LLMs" by offering guarantees LLMs structurally cannot make.

3. **The right read API**: substrate should expose TWO read modes — `argmax_read` (current, fast, deterministic) and `topk_read` (new, returns top-k codewords + pre-softmax logits + spectral features of W). The `topk_read` is the steerable + observable read; the `argmax_read` is the invariant + auditable read. This is a clean product taxonomy.

4. **Cap_map portfolio expansion candidate**: NEW row "argmax-bottleneck operational invariance" — currently implicit across KF-2 + KF-4 + region C/D. Promote to explicit row at green 60-75% if joint-rescue HPs. This is a substrate-physics PROPERTY not a capability mapping, but it's the unifying frame.

5. **Connection to TCFT deletion-cert (green 85-94%)**: TCFT's deletion certificate operates at the same pre-argmax layer (variance ratios on internal state, not output classification). The architectural pattern is consistent: substrate-distinct mechanisms live at the dynamics / spectral / pre-projection layer, not at the operational output.

6. **Strategic next-experiment recommendation per [[feedback-pipeline-pacing]]**: ship `kf45_pre_argmax_layer_v1_n4096` AS THE NEXT KF-4/KF-5 experiment. Single anchor, ~1 GPU-hour, dual-purpose. If HP it lifts BOTH rows + opens NEW row; if HF it confirms structural-invariance reframe (closure-positive). Highest expected-value next move across the at-risk killer-features.

---

## TOP-3 RESCUE PATHS RANKED BY EXPECTED VALUE

Across both KFs, ranked by P_deflated x cost^-1 x scope:

| Rank | Path | KF | P_deflated | Cost | Scope | Strategic notes |
|---|---|---|---|---|---|---|
| 1 | **Pre-argmax spectral + logit layer (R1 KF-4 + R2 KF-5 joint)** | both | 0.45 | ~1 GPU-hr (single combined probe) | DUAL: rescues BOTH KFs + opens NEW row | Single experiment, lit-validated (EigenTrack), maximum joint EV |
| 2 | **Monitor-set / canary drift detection (R2 KF-4)** | KF-4 | 0.40 | ~30 min CPU | KF-4 | Sidesteps argmax-perfect-correction at minimal cost; cognitively-plausible (CLS / HiCL); orthogonal to R1 (do both) |
| 3 | **Multi-output top-k steerability (R1 KF-5)** | KF-5 | 0.35 | ~1 GPU-hr | KF-5 + opens KF-1 multi-hypothesis | Reframes steerability as multi-output property; ALSO contributes to KF-1 (multiple hallucination hypotheses) and TCFT (audit at top-k layer) |

**Calibration penalty applied**: all P estimates deflated 0.20 from raw agent estimates. Top-1 P=0.45 sits below the 0.50 novel-synthesis cap. All HF thresholds explicitly pre-registered.

**Conditional follow-ups (cheapest-next-after-top-3)**:
- If Rank 1 HPs on drift signals BUT HFs on steerability signals: ship KF-5-R3 (cleanup-strength)
- If Rank 1 HFs on both: ship Rank 2 (monitor-set) as cleanest single-KF rescue before reframe consideration
- If Rank 1 HP + Rank 2 HP + Rank 3 HP: 2 cap_map row lifts + 1 NEW row + product narrative consolidation

---

## CITATIONS (verified count: 9)

1. EigenTrack: Spectral Activation Feature Tracking for Hallucination and OOD Detection — arXiv:2509.15735 [direct analog for KF-4-R1 + KF-5-R2 pre-softmax spectral mechanism]
2. Spectral Concentration at the Edge of Stability: Information Geometry of Kernel Associative Memory — arXiv:2511.23083 [Fisher Information singular at critical boundary; attention layers spectral structure in Key-Query]
3. Self-Organization and Spectral Mechanism of Attractor Landscapes in High-Capacity Kernel Hopfield Networks — arXiv:2511.13053 [leading eigenvalue amplified, trailing finite for capacity — substrate-relevant spectral signature]
4. Forgetting leads to chaos in attractor networks — arXiv:2112.00119 [capacity-based catastrophic forgetting; supports KF-4-R3]
5. HiCL: Hippocampal-Inspired Continual Learning — arXiv:2508.16651 [CLS / replay-buffer architecture; supports KF-4-R2 monitor-set]
6. WATCH: Adaptive Monitoring for AI Deployments via Weighted-Conformal Martingales — arXiv:2505.04608 [supports KF-4-R4 conformal martingale]
7. Drift Localization using Conformal Predictions — arXiv:2602.19790 [supports KF-4-R4]
8. Unpacking Softmax: How Temperature Drives Representation Collapse, Compression, and Generalization — arXiv:2506.01562 [softmax bottleneck / temperature-rank-deficit — formal frame for KF-5 STEERABILITY_PARTIAL_DECOUPLING]
9. ReloQate: Transient Drift Detection and In-Situ Recalibration in Surface Code QEC — arXiv:2603.00837 [analog from quantum error correction; supports KF-4-R5 reframe]

Adjacent / supporting (not directly cited but informed framing):
- "Memory-specific E-I balance supports diverse replay" (bioRxiv 2025.09.19.677474) — KF-4-R2 monitor-set
- Box-Constrained Softmax Function (arXiv:2506.10572) — KF-5-R1 multi-output framing
- Error-driven changes in hippocampal representations accompany flexible re-learning (bioRxiv 2025.05.20.655046) — KF-4-R1 + KF-4-R2 cognitive plausibility

---

## STATUS LOG entry written separately via state.py log_event

(See accompanying log_event call; this note is the primary artifact.)
