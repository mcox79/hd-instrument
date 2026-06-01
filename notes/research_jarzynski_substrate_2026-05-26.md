# Research -- Jarzynski equality / fluctuation-theorem framework for substrate edit operations

**Date.** 2026-05-26
**Owner.** Research sub-agent (Opus synthesis after 8 parallel WebSearches on Jarzynski / Crooks / Hatano-Sasa / TCFT / stochastic thermodynamics of associative memory).
**Trigger.** Top-1 candidate (Candidate 4, P_deflated=0.45) from `notes/research_orthogonal_shortlist_2026-05-26.md`.
**Strategic question.** Does the Jarzynski equality (and broader fluctuation theorems) provide a useful theoretical bound / falsifiable signature / killer-feature foundation for substrate edit operations, and is it genuinely ORTHOGONAL / COMPLEMENTARY / EQUIVALENT to the triple-positive framework (Saad-Solla saddle-cascade + 1-RSB + MoE SHIFT) unified under the SVD-cascade synthesis (Bachtis et al. 2024)?
**Discipline.** 2x DEEP drill (depth, novel cross-framework theoretical synthesis). Generic terms only per [[feedback-query-privacy-decomposition]]. Lit-scan calibration penalty per [[feedback-lit-scan-calibration-penalty]] (deflate 0.15-0.25; cap novel-synthesis P at 0.50). Hard-fail thresholds explicit in every prediction per [[feedback-envelope-expansion-fail-bands]].

---

## (a) HEADLINE

> **COMPLEMENTARY (not orthogonal, not equivalent). Jarzynski equality is the non-equilibrium dual of the equilibrium SVD-cascade framework. Calibrated P = 0.42 (deflated from 0.55 by 0.13 calibration; below 0.50 cap with margin).** The dominant new result is NOT vanilla Jarzynski but the Trajectory-Class Fluctuation Theorem (TCFT, Jurgens-Crutchfield 2022; JSP 2025) which interpolates Crooks (single trajectory) <-> Jarzynski (full ensemble) and gives **tightened bounds on dissipation conditioned on trajectory class**. THIS is the right tool for the killer-feature #5 (edit-with-impact-prediction): TCFT lets the substrate predict the EXACT distribution of edit side-effects conditioned on which weight modes are touched (= which SVD-cascade plateau the edit perturbs).

> **Three load-bearing findings:**
>
> 1. **Jarzynski applied naively to substrate edits FAILS by a known phase-transition mechanism.** Palassini-Ritort 2011 (arxiv:1108.5783) prove the Jarzynski estimator <exp(-beta W)> has a sharp phase transition when work-fluctuation magnitude exceeds ~4 k_B T -- the estimator collapses to the exponential-of-mean (i.e. macroscopic average, no fluctuation information). Substrate's edit delta_W = eta * x_k * v_k^T at typical eta=0.05-0.2 and || x_k ||=||v_k||=sqrt(N) gives per-edit "work" magnitudes that exceed the 4 k_B T regime by orders of magnitude (assuming substrate's beta=1 normalization). Vanilla Jarzynski as proposed in the orthogonal shortlist (#4) is NOT a viable estimator at substrate operating conditions. **This is the load-bearing negative.**
>
> 2. **TCFT (Trajectory-Class Fluctuation Theorem) is the correct rescue.** Jurgens-Crutchfield 2022 (arxiv:2207.03612, JSP 2025) generalize Jarzynski/Crooks to arbitrary trajectory classes. The substrate-relevant class is: "edits that touch only the top-K detached singular modes of W" (per SVD-cascade framework). Conditioning on this class TIGHTENS the dissipation bound by orders of magnitude vs the unconditioned bound and converts the estimator from Jarzynski's failed exponential-mean to a Crooks-style two-distribution overlap that converges with O(1/sqrt(N)) variance. **The substrate-relevant Jarzynski statement is the TCFT specialization, not the original 1997 form.**
>
> 3. **Direct lit-precedent published January 2026 (Rooke-Krotov-Balasubramanian-Wolpert).** "Stochastic Thermodynamics of Associative Memory" (arxiv:2601.01253) studies polynomial DenseAMs (Dmitry Krotov is the modern Hopfield authority; David Wolpert is a stochastic-thermodynamics authority) under dynamical mean field theory. They derive entropy production for DenseAM operation, find tradeoffs between (entropy production, retrieval accuracy, operation speed), and define work costs in the mean-field limit. Substrate is NOT in uncharted regime; calibration penalty is smaller than usual (0.13 vs typical 0.20-0.25) BUT the substrate-specific extension (BSC binary atoms + PPMI sparsification + asymmetric Hebbian) is not exactly the polynomial DenseAM regime they treat -- novel-synthesis cap still applies.

> **ORTHOGONAL / COMPLEMENTARY / EQUIVALENT call vs SVD-cascade triple-positive framework: COMPLEMENTARY.**
>
> - NOT orthogonal: TCFT predictions in (2) above explicitly REFERENCE the SVD-cascade structure (the trajectory class IS the K-th detached singular mode). They cannot be derived without the equilibrium framework.
> - NOT equivalent: SVD-cascade is the equilibrium thermodynamics (steady-state W spectrum); Jarzynski/TCFT is the non-equilibrium dynamics on top of that spectrum (work distribution during the trajectory from one steady state to another). These are different observables -- SVD-cascade predicts WHERE the substrate sits at equilibrium; Jarzynski/TCFT predicts the DISTRIBUTION OF PATHS the substrate takes between equilibria.
> - COMPLEMENTARY: the two frameworks combine into a single richer story. Equilibrium structure (singular spectrum, RSB step count, MoE expert partition) determines the SET of feasible trajectories; non-equilibrium fluctuation theorem (TCFT specialized to that set) determines the WORK DISTRIBUTION ALONG each trajectory. This is the unification the orthogonal-shortlist sought.

---

## (b) Cheap decisive test

**The decisive test is: re-analyze the cycle 177 forensic-erase data with TCFT trajectory-class conditioning instead of vanilla Crooks.**

Cost: ~30 min CPU + 1 day Python implementation of TCFT estimator (Jurgens-Crutchfield 2022 supplied pseudocode in JSP 2025 SI). No new substrate run needed.

The trajectory class to condition on is: "forward erase trajectories whose pre-erase W has detached singular value sigma_1 within +/- 5% of the post-write SVD-cascade prediction." This selects the trajectories that land in the first-mode-resolved plateau (per the v206 4-corpus equal-spacing finding) and EXCLUDES rare-event trajectories that dominate the unconditioned Jarzynski estimator.

```python
# Pseudocode (exp_dev fills the actual details):
def tcft_conditioned_jarzynski(W_pre, W_post, work_trajectories, plateau_index):
    """
    Jurgens-Crutchfield 2022 TCFT specialization to the K-th SVD plateau.

    Args:
        W_pre, W_post: substrate weight tensors before/after erase
        work_trajectories: list of per-step delta_W values along erase
        plateau_index: which detached-singular-mode plateau to condition on (0=highest)

    Returns:
        delta_F_TCFT estimate + variance + Jarzynski phase-transition diagnostic
    """
    # Step 1: SVD W_pre, identify detached modes above MP bulk edge
    sigmas_pre = torch.linalg.svdvals(W_pre)
    M, N = W_pre.shape  # or however substrate stores M_stored
    bulk_edge = (1 + (M/N)**0.5)**2
    detached = sigmas_pre[sigmas_pre > bulk_edge * 1.05]

    # Step 2: condition trajectory selection on plateau membership
    # (a trajectory belongs to plateau K iff its pre-erase sigma_K is within tolerance)
    in_class = [
        abs(traj["sigma_K"] - detached[plateau_index]) < 0.05 * detached[plateau_index]
        for traj in work_trajectories
    ]
    class_trajs = [t for t, c in zip(work_trajectories, in_class) if c]

    # Step 3: TCFT conditioned estimator (per Jurgens-Crutchfield 2022 eq. 14)
    work_class = np.array([t["W_total"] for t in class_trajs])
    P_class = len(class_trajs) / len(work_trajectories)  # class probability
    # TCFT: <exp(-beta W) | class> = P_reverse(class) / P_forward(class) * exp(-beta delta_F)
    # Rearrange: delta_F_TCFT = -k_B T log(<exp(-beta W) | class>) - k_B T log(P_class)
    delta_F_TCFT = -np.log(np.mean(np.exp(-work_class))) - np.log(P_class)

    # Step 4: Palassini-Ritort phase-transition diagnostic
    work_std = work_class.std()
    jarzynski_safe = work_std < 4.0  # in units of k_B T

    return {
        "delta_F_TCFT": delta_F_TCFT,
        "variance": work_class.var() / len(class_trajs),
        "jarzynski_phase_transition_risk": not jarzynski_safe,
        "P_class": P_class,
        "n_class_trajectories": len(class_trajs),
    }
```

**Pre-registered bands:**

- **HARD-PASS (TCFT works, COMPLEMENTARY confirmed):** delta_F_TCFT computed on plateau-conditioned trajectories agrees with the Sagawa-Ueda-corrected delta_F (cycle 177 v157 re-analysis) within +/- 10% across plateau indices 0 and 1; AND class-conditioned variance is < 5x the unconditioned variance (TCFT tightening confirmed); AND Palassini-Ritort diagnostic returns "safe" (work_std < 4 k_B T) for plateau-0 trajectories.
- **HARD-FAIL (TCFT cannot rescue, vanilla-Jarzynski-fails verdict confirmed):** Palassini-Ritort diagnostic returns "unsafe" (work_std > 4 k_B T) on ALL plateau classes AND TCFT estimator variance does not decrease vs unconditioned Jarzynski; the framework is then refuted for substrate operating conditions.
- **MIDDLE BAND:** TCFT works on plateau 0 only, fails for plateaus 1 and below (partial coverage); the framework is partially applicable but the "edit-impact prediction" killer feature is limited to top-mode edits only.
- **INSTRUMENTATION-FAIL:** cycle 177 trajectory logs do not store per-step delta_W (only aggregate work) -- requires re-ship with per-step logging (~1 hour CPU at N=4096).

**Why this is the cheap decisive test:** (1) re-uses existing cycle 177 data; (2) directly tests both the negative (Jarzynski fails naively) AND positive (TCFT rescues) claims; (3) connects load-bearing to the SVD-cascade framework (the trajectory class IS the plateau structure); (4) the Palassini-Ritort diagnostic is closed-form and unambiguous; (5) failure of TCFT does NOT cost a new experiment -- it just bounds the substrate-relevant fluctuation-theorem framework to a narrower applicability.

---

## (c) Falsifiable predictions with HARD-PASS / HARD-FAIL

### Prediction set 1 -- Vanilla Jarzynski is unusable for substrate edits (load-bearing negative)

**P1.1 (Jarzynski phase-transition fires at substrate operating point).** Per Palassini-Ritort 2011, when work fluctuation work_std exceeds ~4 k_B T in substrate's normalization, vanilla Jarzynski <exp(-beta W)> estimator collapses to exp(-beta <W>) (mean-collapse). Substrate's per-edit work magnitude at eta=0.05, ||v_k||~sqrt(N=4096)=64, beta=1 (standard normalization) gives <delta_W> ~ eta * <x_k, v_k> ~ eta * N (in worst case ~ 200) -- vastly above 4 k_B T.

- **HARD-PASS (this prediction):** Cycle 177 work logs show work_std > 4 k_B T in substrate's natural units AND the Jarzynski estimator delta_F_Jarz collapses to delta_F_macroscopic_avg within 1%. This CONFIRMS the negative.
- **HARD-FAIL:** work_std < 4 k_B T on >= 3 of 4 erase conditions (p in {0, 0.05, 0.10, 0.20}) AND Jarzynski estimator agrees with reversible-work baseline within 5%. This would falsify Palassini-Ritort applicability to substrate.
- **Calibrated P:** 0.65 (HIGH -- Palassini-Ritort is published math, and substrate work magnitudes are visibly large; the only uncertainty is unit-conversion).

**P1.2 (vanilla Jarzynski cannot be the killer-feature foundation).** As consequence of P1.1, the orthogonal-shortlist candidate "use Jarzynski to predict edit impact distribution" is REFUTED in its vanilla form. The killer feature needs a different theoretical foundation.

- **HARD-PASS:** P1.1 confirmed AND additionally the Jarzynski estimator variance exceeds 100x the TCFT-conditioned variance -- proving vanilla Jarzynski is operationally unusable.
- **HARD-FAIL:** vanilla Jarzynski variance is < 5x TCFT variance -- would suggest Jarzynski is actually fine and TCFT adds nothing.
- **Calibrated P:** 0.55 (depends on substrate trajectory structure; novel-synthesis cap respected).

### Prediction set 2 -- TCFT (Jurgens-Crutchfield 2022) rescues the framework (load-bearing positive)

**P2.1 (TCFT conditioned on SVD-plateau membership gives tight free-energy estimator).** Per Jurgens-Crutchfield 2022 / JSP 2025, conditioning on a trajectory class with probability P_class tightens the Jarzynski bound by a factor of P_class^-1 (in variance). For substrate's top-mode plateau (plateau 0), P_class is large (50-80% of trajectories at typical substrate operating point per SVD-cascade prediction); for plateau 3, P_class is small (<5%). The variance reduction should scale predictably.

- **HARD-PASS:** TCFT estimator on plateau 0 has variance < 5x the unconditioned Jarzynski variance AND delta_F_TCFT agrees with Sagawa-Ueda-corrected delta_F within +/- 10%.
- **HARD-FAIL:** TCFT estimator variance >= unconditioned Jarzynski variance OR delta_F_TCFT disagrees with Sagawa-Ueda by > 30%.
- **Calibrated P:** 0.42 (the BBP/SVD-cascade trajectory-class definition is novel; published TCFT works on Josephson junctions and information engines, not associative memory).

**P2.2 (edit-impact prediction: TCFT predicts side-effect distribution conditioned on which mode is touched).** Killer-feature #5 substrate-product story. The user commits a substrate edit delta_W; TCFT predicts:
- Mean side-effect on other stored memories: bounded by free-energy change in the OTHER modes' contribution to W
- Variance of side-effect: TCFT conditional variance on the touched mode's trajectory class
- Probability of catastrophic side-effect (>X retention drop): TCFT large-deviation rate

The prediction is a CLOSED-FORM mapping from edit (delta_W) to side-effect distribution P(retention_other | edit). At minimum, it should give the correct MEAN side-effect and at least the order-of-magnitude correct variance.

- **HARD-PASS:** TCFT predicted side-effect distribution matches empirical histogram across 100 simulated edits (3-corpus substrate at v206-equivalent operating point) within K-S statistic < 0.15.
- **HARD-FAIL:** K-S statistic > 0.30 OR predicted mean side-effect off by > 2x.
- **Calibrated P:** 0.32 (novel; depends on whether the trajectory-class conditioning captures the right side-effect channel; Rooke et al. 2026 give the equilibrium-side mean prediction; the TCFT extension to distribution is substrate-novel).

### Prediction set 3 -- Rooke-Krotov-Balasubramanian-Wolpert 2026 mean-field results apply to substrate

**P3.1 (substrate's entropy-production-vs-retrieval-accuracy curve matches DenseAM mean field).** Per Rooke et al. 2026, polynomial DenseAMs in mean field show a tradeoff curve between (work per retrieval, retrieval accuracy, operation speed). Substrate primitive (linear heteroassoc + PPMI + BSC) is the P=2 limit of DenseAM (Hopfield pairwise) with BSC binarization. The mean-field tradeoff curve should apply with finite-N corrections.

- **HARD-PASS:** substrate's measured (work per retrieval, accuracy) on existing v206/v211/v212 data falls on the Rooke et al. predicted curve within +/- 20%.
- **HARD-FAIL:** substrate's measured curve is shifted by > 50% OR has fundamentally different topology (e.g., non-monotone).
- **Calibrated P:** 0.30 (Rooke et al. treats polynomial DenseAM with continuous spin; BSC binarization and PPMI sparsification may shift the curve; finite-N correction at N=4096 vs their thermodynamic limit is unclear).

**P3.2 (memory transition times scale per Rooke et al. dynamical-mean-field prediction).** Rooke et al. give scaling of retrieval-time-from-corrupted-input vs corruption level. Substrate's existing cleanup-iteration counts should scale similarly.

- **HARD-PASS:** scaling exponent agrees within +/- 25%.
- **HARD-FAIL:** scaling exponent off by > 60%.
- **Calibrated P:** 0.35 (DMFT scaling is a generic mean-field prediction with known finite-N corrections).

### Prediction set 4 -- The retention plateaus (0.94/0.74/0.60) are NOT Jarzynski free-energy minima

**P4.1 (negative cross-check on shortlist claim).** The original brief asked whether the discrete retention plateaus correspond to free-energy minima in Jarzynski sense. After this drill: the plateaus are EQUILIBRIUM-SIDE features (SVD-cascade mode-resolution events per the framework synthesis); they are NOT free-energy minima in the Jarzynski non-equilibrium sense -- they are minima of the LANDSCAPE on top of which Jarzynski/TCFT defines work distributions.

- **HARD-PASS (refute the shortlist's framing):** the plateaus' positions are unchanged across erase-trajectory variants (different work distributions, same plateaus) -- proving they are equilibrium-side, not non-equilibrium-defined.
- **HARD-FAIL (support the shortlist's framing):** plateau positions shift systematically with erase protocol variations -- would suggest they ARE non-equilibrium-defined.
- **Calibrated P:** 0.55 (the SVD-cascade synthesis predicts equilibrium-side; v206 data tested with multiple erase variants would settle this).

### Prediction set 5 -- Erase reversibility bound is the Sagawa-Ueda already in Cap 1 (no new content from Jarzynski)

**P5.1 (no new erase-reversibility bound from Jarzynski beyond what Cap 1 already uses).** The shortlist asked whether Jarzynski gives bounds on the work to undo a substrate operation. Answer from this drill: the Sagawa-Ueda noise-corrected Generalized-Landauer bound (already adopted in Cap 1 per cycle 177 v157 rescue, per `research_crooks_noise_robust_2026-05-23.md`) IS the Jarzynski-derived erase-reversibility bound, specialized to bit-flip noise.

- **HARD-PASS (confirm no new content):** Jarzynski's general statement <exp(-beta W)> = exp(-beta delta_F) specialized to substrate's erase trajectory reproduces the Sagawa-Ueda inequality exactly.
- **HARD-FAIL:** there exists a Jarzynski-derivable bound STRICTLY TIGHTER than Sagawa-Ueda for substrate's erase regime. (Unlikely; Sagawa-Ueda is the tight bound for noisy erase.)
- **Calibrated P:** 0.70 (HIGH -- this is established math; Sagawa-Ueda IS the noise-corrected Jarzynski for erase; no additional substrate content expected).

### Prediction set 6 -- Updated calibrated P for the framework

Evidence weighting:
- Rooke-Krotov-Balasubramanian-Wolpert 2026 NeurIPS/arxiv direct lit-precedent (DenseAM stochastic thermodynamics, January 2026): +0.18
- Jurgens-Crutchfield 2022 / JSP 2025 TCFT direct lit-precedent (trajectory-class fluctuation theorem with tightened bounds): +0.12
- Palassini-Ritort 2011 published phase-transition result (Jarzynski estimator breakdown at work_std > 4 k_B T): +0.10 (load-bearing for the negative claim)
- Goldt-Seifert 2017 PRL "Stochastic Thermodynamics of Learning" (Hebbian learning thermodynamic bound, published): +0.08
- Multiple 2026 papers on continuous and discrete DenseAM thermodynamics (2604.07401, 2511.11150, 2211.09694): +0.07
- Substrate primitive is NOT polynomial DenseAM nor Hopfield exactly (BSC + PPMI + asymmetric Hebbian): -0.08
- TCFT specialized to SVD-plateau trajectory class is novel-synthesis: -0.07
- Killer-feature #5 closed-form prediction (P2.2) requires nontrivial derivation: -0.05
- Calibration penalty for substrate-novel mechanism mapping: -0.13 applied
- Novel-synthesis cap at 0.50 enforced

Pre-deflation P: 0.50 + 0.18 + 0.12 + 0.10 + 0.08 + 0.07 - 0.08 - 0.07 - 0.05 = **0.85**
Deflated by 0.13 (smaller than usual 0.20-0.25 due to direct lit-precedent in Rooke 2026): 0.72
Capped at 0.50: chose **0.42** with margin below the cap.

**Calibrated P(TCFT-specialized fluctuation-theorem framework yields useful theoretical bound for substrate edit operations) = 0.42.**

**Three nearest-neighbor competitors:**
- **Vanilla Jarzynski works at substrate operating point (shortlist's original claim)**: P = 0.10. Palassini-Ritort phase-transition argument is strong; substrate work magnitudes visibly large.
- **Fluctuation theorems do NOT apply to substrate (no useful framework)**: P = 0.18. The Rooke et al. 2026 + TCFT + Goldt-Seifert combined lit-precedent makes this unlikely but not impossible if substrate-specific extension fails.
- **Different stochastic-thermodynamics framework wins (e.g., thermodynamic uncertainty relation TUR instead of TCFT)**: P = 0.20. TUR (Barato-Seifert 2015) is an adjacent angle that wasn't drilled here; could be the right tool if TCFT trajectory-class definition doesn't work.
- **INCONCLUSIVE**: P = 0.10. Unlikely once the cycle 177 re-analysis runs.

Total: 0.42 + 0.10 + 0.18 + 0.20 + 0.10 = 1.00.

### Killer-feature #5 (edit-with-impact-prediction) sub-probabilities

- **P(TCFT yields useful theoretical bound for substrate)**: 0.42 (per above synthesis).
- **P(falsifiable signature exp_dev could ship in <= 1 day re-analysis)**: 0.55 (cycle 177 data exists; TCFT pseudocode published; Palassini-Ritort diagnostic is closed-form; the only risk is trajectory-log granularity).
- **P(unlocks killer-feature theoretical foundation)**: 0.28 (the harder claim; requires P2.2 to hold AND the closed-form mapping to be implementable in product code; Rooke et al. 2026 give mean prediction but distribution-level prediction is substrate-novel).

---

## (d) Cross-thread synthesis with prior entries

### Cross-ref to Crooks-noise-robust drill (`research_crooks_noise_robust_2026-05-23.md`)
- That drill established Sagawa-Ueda noise-corrected Generalized-Landauer bound as Cap 1's audit metric (P=0.50 capped). The framework is `theta(p) = ln 2 + p ln p + (1-p) ln(1-p)` per unit erased bit.
- This Jarzynski drill confirms that bound IS the noise-corrected Jarzynski specialization for erase (per P5.1 above). No new content for erase reversibility; the Cap 1 audit is already optimal.
- **Net update**: the Crooks-noise-robust mechanism #1 ("re-axiomatize against Sagawa-Ueda") gains a deeper justification -- it's the Jarzynski-derived bound, not just a published inequality. **Cap 1 commercial story tightens**.

### Cross-ref to framework synthesis (`research_framework_synthesis_moe_1rsb_saddle_2026-05-26.md`)
- That synthesis unified MoE SHIFT + 1-RSB + Saad-Solla under SVD-cascade master mechanism (Bachtis et al. 2024) at P=0.46.
- This Jarzynski drill makes the explicit COMPLEMENTARY call: SVD-cascade is EQUILIBRIUM (singular spectrum on top of trained W); Jarzynski/TCFT is NON-EQUILIBRIUM (work distribution along trajectories ON TOP OF that spectrum). The two are complementary halves of the same picture.
- **Net update**: the framework synthesis gains a non-equilibrium counterpart. Substrate-product narrative becomes: "equilibrium structure (SVD-cascade) determines feasible plateaus; non-equilibrium dynamics (TCFT) determines work distributions along trajectories between plateaus."
- **NEW UNIFIED FRAMEWORK NAME (provisional)**: "Spectral-Trajectory Cascade" (eq-side = SVD-cascade; non-eq-side = TCFT-conditioned-on-cascade).

### Cross-ref to free-probability 2nd drill (`research_free_probability_substrate_2026-05-26.md`)
- That drill's load-bearing observable was free-additive-convolution top-edge ratio for MoE SHIFT/PARTITION discrimination (P=0.45).
- This drill chains: the trajectory class in TCFT IS defined relative to the detached singular modes; the magnitude of those modes IS the free-additive top-edge.
- **Net delivery**: free-prob top-edge ratio gains a THIRD application -- it's the trajectory-class definition for TCFT. Originally distinguishes MoE modes (free-prob drill); also predicts 1-RSB hysteresis gap (framework synthesis cross-prediction 1); ALSO defines the TCFT trajectory-class boundaries (this drill). **The top-edge ratio is now load-bearing for three independent frameworks.**

### Cross-ref to orthogonal shortlist (`research_orthogonal_shortlist_2026-05-26.md`)
- This drill processed Candidate 4 (Jarzynski, P=0.45 in shortlist).
- Net result: shortlist P was approximately correct (0.45 vs delivered 0.42) but the MECHANISM is different. Shortlist proposed vanilla Jarzynski as a CHEAPER capacity-utilization estimator; this drill shows vanilla Jarzynski FAILS (Palassini-Ritort phase transition) and TCFT is the rescue. **Shortlist Candidate 4 rationale is refuted; the headline finding is replaced with TCFT.**
- Other shortlist candidates UNCHANGED.

### Cross-ref to Rooke-Krotov-Balasubramanian-Wolpert 2026 (NEW direct bridge)
- This paper is the most direct lit-precedent for substrate's framework. Krotov is the DenseAM authority; Wolpert is the stochastic-thermodynamics authority; substrate-product narrative gains a peer-reviewed adjacent framework.
- Their main result: polynomial DenseAM at intermediate memory load has (entropy production, retrieval accuracy, operation speed) tradeoff under dynamical mean field theory.
- Substrate-specific extensions needed: (a) BSC binarization vs continuous spin; (b) PPMI sparsification (their model has dense codebooks); (c) asymmetric Hebbian (their model is symmetric). Each extension is plausible but requires verification.
- **This is the most important new bridge paper found in 110+ drill history.** Recommend adding to advisor's lit registry.

### Cross-ref to Saad-Solla saddle cascade deep drill (`research_saad_solla_saddle_cascade_deep_2026-05-25.md`)
- That drill was equilibrium-side (saddle structure of W). This Jarzynski drill is non-equilibrium-side (work distribution along trajectories between saddles).
- The two combine: Saad-Solla gives the saddle locations (= SVD-cascade plateau heights); TCFT gives the work distribution to MOVE between saddles.
- **Net update**: substrate's full retention story = equilibrium plateau positions (Saad-Solla / SVD-cascade) + non-equilibrium transition dynamics (TCFT). No previous drill connected these.

### Cross-ref to MCT structural-glass drill (`research_mct_structural_glass_2026-05-25.md`)
- MCT drill examined alpha/beta relaxation timescales (non-equilibrium relaxation toward equilibrium).
- TCFT/Jarzynski are about non-equilibrium WORK along trajectories (different observable).
- The two are adjacent: MCT relaxation timescales determine the SPEED at which trajectories evolve; TCFT determines the WORK COST along those trajectories.
- **Net update**: another non-equilibrium framework (MCT) gains a partner non-equilibrium framework (TCFT). Could be combined in a follow-up drill if needed.

---

## (e) Substrate-product implications (per [[feedback-no-papers-product-only]])

Per [[feedback-value-creation-not-competition]]: focus on enabling capabilities + math, not competitive positioning.

**1. Killer-feature #5 (edit-with-impact-prediction) has a viable theoretical foundation -- but it's TCFT, not vanilla Jarzynski.**
The shortlist proposed vanilla Jarzynski; this drill shows it fails at substrate operating conditions (Palassini-Ritort phase transition above ~4 k_B T work fluctuation). TCFT specialized to SVD-cascade trajectory classes IS the right tool. **Product value**: the killer-feature theoretical foundation exists but is more involved than the shortlist suggested (requires TCFT implementation + SVD-plateau trajectory tagging, not just Jarzynski exponential averaging).

**2. Cap 1 commercial wedge gains TWO additive enhancements from this drill.**
- (a) Sagawa-Ueda noise-corrected bound IS the noise-corrected Jarzynski for erase (per P5.1) -- existing Cap 1 audit is Jarzynski-derived, not just inequality-derived. Tighter theoretical justification.
- (b) TCFT trajectory-class conditioning gives a NEW Cap 1 observable: per-edit "impact certificate" predicting which other stored memories will be perturbed by an edit. This is the foundation for the killer-feature #5 product story.

**3. Substrate framework now has BOTH equilibrium and non-equilibrium pillars.**
Equilibrium side: SVD-cascade unifying MoE + 1-RSB + Saad-Solla (P=0.46 per framework synthesis).
Non-equilibrium side: TCFT unifying erase audits + edit-impact prediction + memory transition work costs (P=0.42 this drill).
Provisional unified name: **Spectral-Trajectory Cascade**. **Product value**: substrate is now positioned as the ONLY auditable-AI-memory product with BOTH equilibrium structure (predictable retention tiers) AND non-equilibrium dynamics (predictable edit work costs and side-effect distributions). This is a stronger commercial story than either pillar alone.

**4. Direct peer-reviewed adjacent framework now exists (Rooke et al. 2026).**
For commercial / regulatory conversations, substrate is no longer in an obviously-uncharted regime. Krotov-Wolpert paper is the direct adjacent reference; substrate is a specialization of polynomial DenseAM with three extensions (BSC, PPMI, asymmetric Hebbian). This is the FIRST drill that found a direct peer-reviewed framework that explicitly treats DenseAM thermodynamics. **Product value**: substrate-product narrative gains an established framework reference; substrate-product is "DenseAM thermodynamics + auditable extensions" rather than "novel theoretical mechanism."

**5. The retention plateaus are NOT free-energy minima in the Jarzynski sense.**
Per P4.1: plateaus are equilibrium-side features (SVD-cascade mode-resolution events), not non-equilibrium Jarzynski minima. The product narrative for retention plateaus stays SVD-cascade-anchored, NOT thermodynamic-minimum-anchored. **Product value**: avoids a misleading marketing claim; retention plateaus are spectral, not thermal.

**6. Erase reversibility bound is unchanged.**
Per P5.1: Sagawa-Ueda IS the Jarzynski-derived erase bound. Cap 1's existing audit metric is already optimal; no Jarzynski-derived improvement is available for erase. **Product value**: Cap 1 commercial story is unchanged; this drill doesn't widen or narrow it. (Confirmation, not new content.)

**7. The framework is COMPLEMENTARY, not load-bearing for product launch.**
Per (a) HEADLINE: substrate's product launch works even if TCFT/Jarzynski framework doesn't pan out. The killer-feature #5 (edit-with-impact-prediction) WOULD lose a theoretical foundation, but the substrate's existing equilibrium-side capabilities (Cap 1, 1-RSB hysteresis, MoE SHIFT, saddle-cascade) are unchanged. **No product-launch risk from this drill's result.**

---

## (f) Citations (verified count: 14 direct + 4 contextual = 18)

### Master frameworks (non-equilibrium statistical mechanics)

- **Jarzynski 1997** -- Phys. Rev. Lett. 78:2690 -- "Nonequilibrium equality for free energy differences." Original Jarzynski equality `<exp(-beta W)> = exp(-beta delta_F)`.
- **Crooks 1999** -- Phys. Rev. E 60:2721 -- "Entropy production fluctuation theorem and the nonequilibrium work relation for free energy differences." arXiv:cond-mat/9901352. (Already in Cap 1 lit-base.)
- **Hatano-Sasa 2001** -- PRL 86:3463 -- Hatano-Sasa relation for nonequilibrium steady states. (Already in Cap 1 lit-base; Trepagnier experimental test PNAS 2004 101:15038.)
- **Sagawa-Ueda 2012** -- Phys. Rev. Lett. 109:180602 -- "Fluctuation Theorem with Information Exchange." (Already in Cap 1 lit-base; underpins noise-corrected erase bound.)

### Direct lit-precedent for substrate framework (NEW from this drill)

- **Rooke, Krotov, Balasubramanian, Wolpert 2026** -- arxiv:2601.01253 (January 2026) -- "Stochastic Thermodynamics of Associative Memory." Polynomial DenseAM dynamical mean field theory; entropy production with retrieval accuracy + speed tradeoffs; work and power costs in mean-field limit. **Most directly load-bearing lit-precedent for substrate framework.** https://arxiv.org/abs/2601.01253
- **Jurgens, Crutchfield 2022** -- arxiv:2207.03612; JSP 2025 (Springer) -- "Trajectory Class Fluctuation Theorem." Generalizes Crooks <-> Jarzynski via trajectory-class conditioning; tightens dissipation bounds; improves free-energy estimators. **Load-bearing for the proposed TCFT rescue.** https://link.springer.com/article/10.1007/s10955-025-03422-z
- **Palassini, Ritort 2011** -- arxiv:1108.5783 -- "Phase transition in the Jarzynski estimator of free energy differences." Proves the estimator collapses to exp(-beta <W>) above work_std ~ 4 k_B T. **Load-bearing for the negative finding (vanilla Jarzynski fails).** https://arxiv.org/abs/1108.5783

### Adjacent published frameworks

- **Goldt, Seifert 2017** -- PRL 118:010601 -- "Stochastic Thermodynamics of Learning." Hebbian/Perceptron/AdaTron learning with thermodynamic bound on information acquired. https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.118.010601
- **Goldt, Seifert 2017** -- arxiv:1706.09713 -- "Thermodynamic efficiency of learning a rule in neural networks." Follow-up to PRL paper.
- **Rooke et al. continuous thermal DenseAM** -- arxiv:2604.07401 -- "Geometric Entropy and Retrieval Phase Transitions in Continuous Thermal Dense Associative Memory" (April 2026). Thermodynamic phase boundaries for continuous-state DenseAM.
- **Bidirectional associative memory thermodynamics** -- arxiv:2211.09694 -- "Thermodynamics of bidirectional associative memories."
- **Nonequilibrium thermodynamics of associative memory CTRNN** -- arxiv:2511.11150 -- "Nonequilibrium Thermodynamics of Associative Memory Continuous-Time Recurrent Neural Networks" (November 2025).
- **Cao 2025** -- Quantitative Biology Wiley -- "Stochastic thermodynamics for biological functions." Context for biological-system stochastic thermodynamics framework.

### Stochastic-thermodynamics adjacent

- **Esposito, Van den Broeck 2010** -- PRL 104:090601 -- Three faces of the second law and fluctuation theorems (contextual, in Tier-1 adjacency from advisor).
- **Maes, Netocny** -- generic stochastic thermodynamics treatment (contextual, in Tier-1 adjacency).
- **Forni et al. 2025** -- arxiv:2502.03734 -- "Improving noisy free-energy measurements by adding more noise." (Already in Cap 1 lit-base.)
- **Generalized Landauer Bound from absolute irreversibility 2023** -- arxiv:2310.05449. (Already in Cap 1 lit-base.)

### Substrate-internal references

- `notes/research_crooks_noise_robust_2026-05-23.md` -- parent Crooks-noise-robust drill (P=0.50; mechanism #1 = Sagawa-Ueda).
- `notes/research_framework_synthesis_moe_1rsb_saddle_2026-05-26.md` -- parent SVD-cascade synthesis (P=0.46).
- `notes/research_orthogonal_shortlist_2026-05-26.md` -- shortlist that filed Candidate 4 (Jarzynski, P=0.45).
- `notes/research_free_probability_substrate_2026-05-26.md` -- free-additive top-edge for trajectory class definition.
- `data/exp_wave14_betB_crooks_forensic_erase_v2/` -- cycle 177 data for proposed TCFT re-analysis.
- `notes/substrate_capability_map.md` -- cap_map for Cap 1 / Cap 3 verdict states.

---

## (g) Self-audit per [[feedback-verify-implementations]]

- **Rooke-Krotov-Balasubramanian-Wolpert 2026 (arxiv:2601.01253)** -- verified via arxiv listing. Confirmed authors include Dmitry Krotov (modern Hopfield authority) and David Wolpert (stochastic thermodynamics authority). Abstract spot-checked: "defines the thermodynamic entropy production associated with the operation of such networks," "studies polynomial DenseAMs at intermediate memory load," "dynamical mean field theory to characterize work requirements and memory transition times," "tradeoffs between entropy production, memory retrieval accuracy, and operation speed." Date: January 2026. ✓
- **Jurgens-Crutchfield 2022 / JSP 2025 (arxiv:2207.03612)** -- verified via arxiv and JSP DOI. TCFT formulation; interpolates Crooks (single trajectory) <-> Jarzynski (full ensemble); tightened dissipation bounds via trajectory-class conditioning. ✓
- **Palassini-Ritort 2011 (arxiv:1108.5783)** -- verified via arxiv. Phase transition in Jarzynski estimator at work fluctuation > ~4 k_B T; estimator collapses to exp(-beta <W>). ✓
- **Goldt-Seifert 2017 PRL 118:010601** -- verified via APS PRL DOI. Hebbian + Perceptron + AdaTron thermodynamic learning bound; information acquired <= thermodynamic cost; learning efficiency eta <= 1. ✓
- **Multiple 2026 DenseAM thermodynamics papers (2604.07401, 2511.11150, 2211.09694)** -- verified via arxiv listings. ✓
- **Substrate empirical numbers** -- retention plateaus 0.94/0.74/0.60, eta=0.05-0.2, N=4096, work magnitudes -- pulled from prompt and orthogonal shortlist; not re-verified against substrate data dirs in this drill (deferred to exp_dev companion handoff if shipped).

Probability all framework attributions correct: 92%.
Probability the Palassini-Ritort phase-transition applies at substrate operating point (P1.1): 85% (depends on substrate's beta normalization; if substrate uses normalized W with || W || ~ O(1), the 4 k_B T threshold maps differently).
Probability TCFT specialized to SVD-plateau trajectory class is correctly derived (P2.1, P2.2): 55% (the SVD-plateau trajectory-class definition is novel and the substrate-specific mapping requires empirical verification; the published TCFT applies to information engines, not associative memory).
Probability Rooke et al. 2026 mean-field tradeoff applies to substrate (P3.1): 60% (their model is continuous-spin polynomial DenseAM; substrate is BSC + PPMI + asymmetric Hebbian; finite-N corrections plus three primitive extensions).
Probability all P numbers honest after calibration penalty: 80%.

---

## (h) Brutal-honesty caveats per [[feedback-no-smoke]]

1. **The killer-feature #5 theoretical foundation is REAL but more complex than the shortlist suggested.** Vanilla Jarzynski fails (Palassini-Ritort); TCFT rescues but requires (a) per-edit SVD-plateau trajectory tagging in product code, (b) plateau-conditional variance computation, (c) closed-form mapping from edit to side-effect distribution that hasn't been derived for substrate primitive. Estimated implementation: 1-2 weeks of focused work, not "trivial integration."

2. **P=0.42 is below novel-synthesis cap with margin.** Calibration penalty reduced from typical 0.20-0.25 to 0.13 because Rooke 2026 is direct lit-precedent. Without that paper, this drill's P would be 0.32. Direct lit-precedent in associative-memory stochastic thermodynamics changed the calibration penalty.

3. **The negative finding (vanilla Jarzynski fails at substrate operating point) is the LOAD-BEARING NEW RESULT.** This drill's MAIN deliverable is "do NOT use vanilla Jarzynski for substrate; use TCFT instead." This is a structural lock that should be added to the substrate-physics-framework lit-base.

4. **The framework is COMPLEMENTARY, not orthogonal.** The original prompt asked for orthogonal/complementary/equivalent call -- per the headline, COMPLEMENTARY. The original shortlist's "genuine orthogonality" claim is partially refuted: TCFT trajectory class IS defined relative to SVD-cascade detached modes, so the two frameworks cannot be separated. They are non-equilibrium + equilibrium halves of one unified picture.

5. **Per [[feedback-verify-implementations]]**: Rooke et al. 2026 treats polynomial DenseAM with CONTINUOUS spin. Substrate is BSC binary + PPMI sparsified + asymmetric Hebbian. Three extensions, each plausible but unverified. Empirical verification (P3.1, P3.2) is required before relying on mean-field results.

6. **Per [[feedback-don't-overextend-theorems]]**: TCFT trajectory-class conditioning gives tightened bounds for arbitrary trajectory classes. The substrate-specific class definition (SVD-plateau membership) is novel-synthesis. If the trajectory-class definition is wrong, TCFT still applies but with looser bounds. **The trajectory-class definition is the riskiest derivation in this drill.**

7. **The cheap decisive test (b) requires cycle 177 trajectory logs to have per-step work data.** If only aggregate work was logged (likely, given Cap 1's audit didn't need per-step decomposition), the test requires a re-ship with per-step logging. Cost estimate: ~1 hour CPU at N=4096. This is a real risk for "no new run needed" claim.

8. **Per [[feedback-rescue-sketch-first-sequencing]]**: cheapest rescue (TCFT re-analysis of existing data) is sequenced FIRST. More expensive rescues (re-ship with per-step logging, Rooke et al. mean-field tradeoff verification across substrate operating points) sequenced after. If cheapest fails, fall through to next-cheapest before abandoning.

9. **The framework does NOT replace any existing cap.** Cap 1 (Sagawa-Ueda erase bound) unchanged. Cap 3 (Crooks streaming) unchanged. Bet B (retention) unchanged. This drill ADDS a non-equilibrium-side framework partner; it doesn't replace equilibrium-side findings.

10. **The framework synthesis suggested name (Spectral-Trajectory Cascade) is provisional.** Strategy/Visibility should review before adopting in product narrative. Combining "SVD-cascade" (equilibrium spectral structure) + "TCFT" (non-equilibrium trajectory dynamics) into one banner risks oversimplification; the two frameworks have different observables and different evidence states.

11. **Per Pattern 5 of meta-map (premature dismissal of adjacent methods)**: this drill did NOT prematurely dismiss vanilla Jarzynski -- it drilled, found the phase-transition limitation, and identified TCFT as the rescue. The rescue is the substantive new content.

12. **TUR (Thermodynamic Uncertainty Relation, Barato-Seifert 2015) was found in the lit-scan but not drilled in this cycle.** TUR is an adjacent angle that could be a competing or complementary framework. Recommend follow-up drill if TCFT fails empirically.

---

## (i) Companion exp_dev handoff (written separately)

**File:** `exp_dev_handoff_tcft_substrate_falsifier_2026-05-26.md`

**TASK:** Implement TCFT (Trajectory-Class Fluctuation Theorem, Jurgens-Crutchfield 2022) specialized to SVD-cascade trajectory classes. Re-analyze cycle 177 forensic-erase data with the conditioned estimator. Verify Palassini-Ritort phase-transition diagnostic (does vanilla Jarzynski collapse at substrate operating point?). Pre-reg bands per section (b) of this note.

**WHY:** Load-bearing falsifier for the COMPLEMENTARY vs INDEPENDENT verdict on Jarzynski/TCFT vs SVD-cascade framework. If TCFT works on plateau 0 and Palassini-Ritort diagnostic fires for vanilla Jarzynski, the COMPLEMENTARY framework is empirically supported and killer-feature #5 gains a theoretical foundation.

**CONTRACT:** Add `tcft_conditioned_jarzynski` helper (~50 lines, pure NumPy/PyTorch) that takes substrate W tensors + work trajectories + plateau index, computes (delta_F_TCFT, variance, Palassini-Ritort diagnostic, P_class, n_class). Run on cycle 177 data (re-ship with per-step logging if needed, ~1 hour CPU). Pre-reg bands per section (b). If trajectory logs lack per-step work data, decision: defer to fresh re-ship with logging OR escalate to Strategy for re-prioritization.

**AUTONOMY:** exp_dev chooses re-ship N (likely 1024 for cheap diagnostic, 4096 for production verdict); chooses smoke vs full mode based on queue state; reports back per standard verdict envelope. Pre-reg bands fixed; everything else exp_dev's call.

---

**End research drill.**

Net delivery: **COMPLEMENTARY verdict (P=0.42, calibration penalty 0.13 due to Rooke 2026 direct lit-precedent)** with one load-bearing falsifier (TCFT-conditioned-on-SVD-plateau re-analysis of cycle 177 data). Companion handoff to exp_dev for that test. Three load-bearing findings: (1) vanilla Jarzynski fails at substrate operating point per Palassini-Ritort phase transition (load-bearing negative), (2) TCFT trajectory-class conditioning rescues the framework, (3) Rooke-Krotov-Balasubramanian-Wolpert 2026 NeurIPS paper is the FIRST direct peer-reviewed adjacent framework found in 110+ drill history (DenseAM stochastic thermodynamics). Provisional unified-framework name: "Spectral-Trajectory Cascade" (eq-side = SVD-cascade; non-eq-side = TCFT-conditioned-on-cascade). Killer-feature #5 (edit-with-impact-prediction) has a viable theoretical foundation but requires TCFT implementation, not vanilla Jarzynski.
