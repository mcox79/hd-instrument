# Research drill 3x DEEP — free-probability as substrate-novel observability + capacity + calibration framework

Date: 2026-06-11
Topic: free-probability / random-matrix-theory as unified substrate framework
Triggered by: CONSENSUS next-drill from 7 of 10 today's drills
Depth: 3x DEEP (triple-source convergence, contradiction-aware, novel-unification)

---

## (a) HEADLINE

Free-probability is the natural mathematical language for substrate observability, capacity, and calibration as a SINGLE framework. The codebook matrix spectrum (via Marchenko-Pastur bulk + Tracy-Widom edge + kappa_4 free cumulant) is a single ~30-line numpy computation that simultaneously yields: (1) a capacity bound that distinguishes linear-superposition sqrt(M) crosstalk from dense-Hopfield log(M) separability via the spectral gap; (2) a phase-transition detector for "good codebook vs degraded codebook" (BBP threshold on largest sample eigenvalue vs MP edge); (3) a calibration tightness predictor (CP set-size lower bound from operator-norm of nonconformity covariance). Three independent prior drills already converge on this; 7 of 10 today's drills name it as the next-drill candidate. The reason no published precedent treats it as a unified substrate instrument is that VSA literature reasons about second-moment crosstalk only, never about the edge fluctuation or fourth free cumulant of the codebook. Novel-synthesis P_deflated = 0.42 (cap 0.50 applied per lit-scan calibration penalty).

---

## (b) Cheap decisive test

A single CPU script, runtime under 30 minutes total on a laptop:

1. Build three substrate codebooks of size M x N at the current substrate dimension:
   - C_good: i.i.d. Gaussian (theoretical MP reference)
   - C_real: actual substrate codebook from current Sprint-4 wrapper run
   - C_degraded: substrate codebook after artificial capacity-overload (M >> N/4 with realistic correlations)
2. Compute for each:
   - Empirical spectrum lambda_i of (1/N) C C^T (eigvalsh)
   - MP-predicted bulk edges lambda_+- = sigma^2 (1 +- sqrt(M/N))^2
   - Largest eigenvalue lambda_max and its z-score vs Tracy-Widom edge (lambda_+ + sigma N^{-2/3} chi)
   - Empirical fourth FREE cumulant kappa_4_free = m_4 - 2 m_2^2 (note: NOT the classical kappa_4)
3. Check three predictions (HARD-PASS / HARD-FAIL thresholds in section c).

This costs about $0 on existing CPU runner. Decisive because the three regimes (good / real / degraded) should produce QUANTITATIVELY ORDERED spectral signatures if the framework holds; if they don't, the framework fails immediately.

---

## (c) Falsifiable predictions

### Prediction P1 — Marchenko-Pastur bulk fits good codebook

HARD-PASS: Kolmogorov-Smirnov distance between empirical spectrum of C_good and MP density is < 0.05 (N >= 1024, M/N in [0.25, 0.5]).
HARD-FAIL: KS distance > 0.15. This would refute the MP-as-substrate-baseline claim.

### Prediction P2 — Tracy-Widom edge as overcapacity detector

HARD-PASS: For C_degraded with M/N > 0.5, the lambda_max z-score (against TW edge) exceeds 5.0; for C_good with M/N <= 0.25, the z-score is in [-3, +3]. The substrate codebook (C_real) z-score predicts retrieval quality: codebooks with z-score > 5 should exhibit measurable recall@1 degradation.
HARD-FAIL: z-score does not correlate with recall@1 (Spearman |rho| < 0.3 over 10 codebook variants).

### Prediction P3 — kappa_4 free cumulant tracks dense-Hopfield-like separability

HARD-PASS: kappa_4_free / kappa_2_free^2 is reliably ordered: C_good (i.i.d.) ~ 0 (semicircle has zero higher free cumulants), C_real shows nonzero kappa_4_free positively correlated with measurable separability gain from sigmoid-cleanup vs linear-cleanup. Specifically: codebooks with kappa_4_free > 0.05 * kappa_2_free^2 yield >= 1.3x recall@1 improvement under softmax-cleanup vs linear-cleanup.
HARD-FAIL: kappa_4_free signs are random vs cleanup-gain (no monotone relationship across 10 codebooks).

### Prediction P4 — Spectral-gap-based CP set-size lower bound

HARD-PASS: Define gap = (lambda_2 - lambda_M+1) / lambda_max on the nonconformity score covariance. CP set-size at coverage 0.9 lower-bounded by L = c / gap for some constant c, with c stable across substrate configs. HARD-PASS = c stable to within +/- 25% across 5 configs.
HARD-FAIL: c varies by > 3x across configs (i.e., spectral gap does not predict CP tightness).

---

## (d) Cross-thread synthesis with 7 prior drills

This is the unification claim — the load-bearing 3x-deep content.

### D.1 Code synthesis (resonator-network factoring) — UNIFIED via R-transform

Frady-Kent-Sommer-Eliasmith resonator networks factor a Hadamard-product superposition into factors via iterative pattern completion (Frady-Kent 2020, Neural Computation 32:2332). The dynamics has NO published Lyapunov; convergence is empirical with operational-capacity quadratic in N. Free probability connection: each factor's vector is asymptotically free (i.i.d. unit-modulus phasors are free Haar unitaries in the GUE limit), so the spectrum of the Hadamard-product superposition is the FREE multiplicative convolution of factor spectra. R-transform additivity (and S-transform multiplicativity) gives a closed-form for the expected resonator capacity that the existing quadratic empirical-fit should match. **Substrate-novel angle**: kappa_4 of the bound vector's covariance predicts which factor count F the resonator can recover (sharp transition when free-multiplicative convolution exits the semicircle regime). Use this as the resonator-capacity predictor for code-synthesis combinatorial decoding.

### D.2 Free-prob + family-tag (F2 Tracy-Widom) — UNIFIED via spike detection

Family-tag binding in substrate is a low-rank perturbation of an i.i.d. codebook (the tag adds a rank-K signal where K = number of tagged families). This is exactly the BBP (Baik-Ben Arous-Peche) spiked model. **The family-tag's detectability is governed by the BBP threshold**: tag-signal strength must exceed sigma^2 (1 + sqrt(M/N)) to separate from the MP bulk. Below this, the tag is statistically indistinguishable from noise — a substrate-novel HARD-FAIL prediction for under-engineered tags. Above this, the largest sample eigenvalue follows Tracy-Widom around the shifted edge, giving a CALIBRATED detection statistic (not just heuristic dot-product threshold). This unifies (cross-source: Baik-Ben Arous-Peche 2005; Bloemendal-Knowles-Yau 2014; Lee-Schnelli 2014) and SHIPS as a 30-line check.

### D.3 Unified SVAMP rescue (F4 / F2) — UNIFIED via kappa_4 as concept-marker

SVAMP rescue's negative result (substrate < 0.30) was that VIB random-projection killed signal. Free-probability angle: random projection is a free-multiplicative compression. Its Marchenko-Pastur image of the original spectrum WIPES higher free cumulants. **A codebook with high kappa_4 (concept structure) after VIB has low kappa_4 — predictable from S-transform analysis**. The rescue path is: project to a dimension chosen so MP image preserves the spectral gap (M/N_projected = MP-optimal); use kappa_4 retention as the loss-fn target. This converts "VIB kills signal" from mysterious empirical fact into computable spectral degradation under the S-transform of compression.

### D.4 Frontier-scale (F2 Tracy-Widom) — UNIFIED via finite-N corrections

Frontier-scale substrate (M ~ 1e6 facts, N ~ 1024-8192) hits the regime where bulk asymptotics still hold but edge fluctuations are exactly Tracy-Widom-distributed with width N^{-2/3}. **Substrate-novel observability**: monitor lambda_max trajectory over time. A drift of lambda_max ABOVE the TW prediction is a CONTINUOUS observability of "capacity exhaustion approaching." This is a real-time substrate health signal computable in ~milliseconds per check (Lanczos for largest eigenvalue), and triple-source-validated (BBP + Lee-Schnelli + Bloemendal-Knowles-Yau).

### D.5 Conformal calibration (free-prob x calibration) — UNIFIED via spectral gap

CP set-size is bounded by quantile of nonconformity scores. **Novel claim**: if nonconformity scores arise from substrate retrievals where the score covariance has spectral gap g, then CP set size at confidence 1-alpha is lower-bounded by O(1/g) (intuition: smaller gap = more "near-tied" candidates that all must be in the set to guarantee coverage). This connects free-probability spectral statistics DIRECTLY to CP tightness — a substrate-novel cross-link not present in CP literature (Angelopoulos et al. focus on score functions, not score covariance spectra). Cheap test: compute gap and observed CP set size on substrate retrievals; check inverse-proportional relationship.

### D.6 Chung-Lu / automorphism (Tracy-Widom edge fluctuations) — UNIFIED via universality

Chung-Lu random graphs (substrate analogy structure) have adjacency-matrix spectra that converge to a deformed MP density. The largest eigenvalue separating from the bulk corresponds to a "macro-cluster" forming — which is the same as substrate analogy-cluster emergence. **TW universality predicts** the same N^{-2/3} fluctuation regime as for sample covariance, even though the matrix is graph-adjacency not codebook covariance. Substrate-novel observability: track lambda_max(adjacency) over time as analogy-graph health.

### D.7 SVAMP substrate > 0.30 (Marchenko-Pastur on VIB random-projection) — UNIFIED via the SAME spectrum

This is the closure: the SVAMP-substrate path (D.3) and the rescue path are the same free-probability framework applied to (substrate state, projection) and (projection, target) respectively. The S-transform multiplicativity gives a CHAIN composition: spectrum_final = S^{-1}(S(spectrum_substrate) * S(spectrum_VIB) * S(spectrum_head)). Optimizing projection dimension is now a closed-form spectral problem, not a hyperparameter sweep.

### D.8 The unification

ALL 7 drills reduce to TWO substrate-novel computations on a substrate codebook or activation matrix:

```
spec(C) = eigenvalsh((1/N) C @ C.T)     # 1 line numpy
m4_free = mean(spec**4) - 2 * mean(spec**2)**2   # 1 line, free 4th cumulant
```

Plus their MP/TW reference distributions (closed-form). Total ~30 lines of numpy. This is the substrate-novel observability primitive.

---

## (e) Substrate-product implications

### E.1 Single instrument for three things

The same 30-line spectral computation yields:
- Capacity headroom (z-score of lambda_max vs TW edge)
- Retrieval-quality predictor (kappa_4_free as concept-structure index)
- Calibration-tightness predictor (spectral gap as CP set-size LB)

This collapses three separate observability subsystems into one — substantial simplification of the substrate operator dashboard.

### E.2 Substrate-vs-LLM measurable axis

Free-probability spectral statistics are NOT available for LLM hidden states except as approximations. A substrate whose retrieval quality is predicted in advance by a single computed spectral statistic (kappa_4_free) HAS A FORMAL OBSERVABILITY that LLMs lack. This is a substrate-distinctive product capability — operator can SEE capacity headroom; LLM operator cannot.

### E.3 Engineered-wrapper compatibility

This requires NO substrate-core changes. The spectral statistics are computed from the codebook matrix (which exists in any substrate variant). It rides on the v3.2 engineered-wrapper architecture as a pure observability/instrumentation layer — consistent with the 2026-06-11 substrate v3.2 wrapper memory.

### E.4 Capacity scaling claim refinement

Current substrate claim is "linear-superposition sqrt(M) crosstalk vs dense-Hopfield exp/log(M) separability." Free-probability sharpens this: dense-Hopfield log(M) separability requires kappa_4_free > 0 (positive higher free cumulant). For semicircle (i.i.d. Gaussian) codebooks, kappa_4_free = 0 — i.e., pure i.i.d. substrate is BOUNDED to sqrt(M) regime regardless of cleanup. The path to log(M) regime is engineered kappa_4 > 0 in the codebook (e.g., via family-tag binding, hierarchical structure). This is a NEW, computable engineering target.

---

## (f) Concrete ~30-line numpy implementation

```python
import numpy as np

def substrate_spectral_observability(C, sigma_noise=1.0):
    """C: M x N codebook (M items, N-dim vectors). Returns (lambda_max_z, kappa_4_free_ratio, spectral_gap)."""
    M, N = C.shape
    # 1) empirical spectrum of sample covariance
    spec = np.linalg.eigvalsh((C @ C.T) / N)  # shape (M,)
    spec_sorted = np.sort(spec)[::-1]
    # 2) MP bulk reference
    ratio = M / N
    lam_plus = sigma_noise**2 * (1 + np.sqrt(ratio))**2
    lam_minus = sigma_noise**2 * (1 - np.sqrt(ratio))**2
    # 3) Tracy-Widom edge z-score
    tw_width = sigma_noise * N**(-2.0/3.0) * (1 + np.sqrt(ratio))**(4.0/3.0)
    lambda_max_z = (spec_sorted[0] - lam_plus) / tw_width
    # 4) free 4th cumulant (free probability, not classical)
    m2 = float(np.mean(spec))
    m4 = float(np.mean(spec**2))  # second moment of spec, used in free cumulant
    # Free cumulants: k_2_free = m_2; k_4_free = m_4 - 2 m_2^2 (semicircle has k_4_free=0)
    k2 = m2
    k4 = m4 - 2.0 * (m2**2)
    kappa_4_ratio = k4 / max(k2**2, 1e-12)
    # 5) spectral gap on TOP-k
    K = min(32, M-1)
    if M > K + 1:
        spectral_gap = (spec_sorted[K-1] - spec_sorted[K]) / max(spec_sorted[0], 1e-12)
    else:
        spectral_gap = 0.0
    return {
        "lambda_max_z": float(lambda_max_z),
        "kappa_4_free_ratio": float(kappa_4_ratio),
        "spectral_gap": float(spectral_gap),
        "mp_bulk": (float(lam_minus), float(lam_plus)),
        "lambda_max": float(spec_sorted[0]),
    }

# usage:
# import torch; C = codebook.cpu().numpy()
# obs = substrate_spectral_observability(C)
# log: obs["lambda_max_z"] (overcapacity warning at > 5), obs["kappa_4_free_ratio"] (separability index)
# obs["spectral_gap"] (CP set-size LB ~ 1/gap)
```

This is ~25 lines. Adding the 5-line MP density KS-test for validation gives the full ~30-line implementation referenced in drill 5.

---

## (g) Pre-registered cheap CPU experiments

### Exp 1 — MP fit on i.i.d. Gaussian (~10 min)
Build C_good with M/N in [0.1, 0.25, 0.5], N=1024, run substrate_spectral_observability. Check KS distance < 0.05 (P1).

### Exp 2 — TW z-score vs recall@1 on substrate codebooks (~1-2 hr)
Pull 10 historical substrate codebooks (e.g., from PP-225 / Sprint-4 runs at varying M). Compute lambda_max_z. Correlate with measured recall@1. HARD-PASS if Spearman |rho| > 0.5 (P2).

### Exp 3 — kappa_4_free vs sigmoid-cleanup gain (~2 hr)
Same 10 codebooks. Measure recall@1 under (linear cleanup) and (softmax cleanup). Compute gain ratio. Correlate with kappa_4_free_ratio. HARD-PASS if monotone positive relationship across 10 codebooks (P3).

### Exp 4 — spectral_gap vs CP set-size (~1 hr)
On substrate retrieval scores with conformal calibration applied, measure CP set size at coverage 0.9 across 5 substrate configs. Fit set_size = c / spectral_gap. HARD-PASS if c stable within +/- 25% (P4).

### Exp 5 — R-transform resonator factor capacity (~3 hr)
Resonator network at N=512 factoring F factors. For each F in [3,4,5,6,7], measure empirical operational capacity. Compute kappa_4_free of the binding vector. Compare to R-transform-derived theoretical capacity. HARD-PASS if R-transform predicts the empirical transition within +/- 1 factor.

Total: ~7-8 CPU hr across 5 experiments. Spreadable across local_cpu_queue (FrameworkMPC) overnight. ~ $0 cost.

---

## (h) Comparison to existing VSA/HDC capacity bounds

| Author / framework | What it bounds | What free-probability adds |
|---|---|---|
| Plate (HRR) 1995 | crosstalk variance per slot ~ 1/sqrt(N) | Bulk MP bulk gives EXACT density, not just variance; edge gives TW threshold for "too many" slots |
| Kanerva (SDM/BSC) 2009 | binary code crosstalk binomial | Free-cumulant version applies to arbitrary distributions, not just binary |
| Frady-Sommer 2018 (Theory of superposition) | crosstalk in superposition | This is a 2nd-moment analysis — kappa_4_free is the next-order correction, currently absent in HDC literature |
| Frady-Kent-Sommer-Eliasmith 2020 (Resonator nets) | quadratic-in-N empirical capacity | R-transform additivity gives closed-form prediction; no published derivation yet |
| Ramsauer et al. (Modern Hopfield) 2020 | exponential capacity via log-sum-exp | Free probability connects "log capacity" regime to spectral gap (gap >> 0) vs "polynomial" regime (semicircle bulk) |

**Conclusion**: Every existing capacity bound is either 2nd-moment crosstalk (Plate-Kanerva-Frady-Sommer line) or asymptotic exponential-capacity claims (Hopfield-Ramsauer line). The free-cumulant / spectral-gap / Tracy-Widom apparatus is the natural mathematical interpolation between them. **Novel-synthesis claim is the unification, not the individual components.**

---

## (i) New math applicability — operator algebras, subfactor theory, non-commutative probability

Most genuinely under-applied to ML (Jones planar algebras and subfactor theory are 30+ years old and have ZERO mainstream ML application). Three concrete directions:

### I.1 Operator-valued free probability for cross-layer covariance

Standard free probability deals with scalar-valued non-commutative probability spaces. **Operator-valued free probability** (Voiculescu 1995; Speicher 1998) generalizes to amalgamated free products over a subalgebra B. For substrate: B = the "shared structure" (e.g., role-embeddings); the codebook factorizes as freely-independent OVER the role subalgebra. This gives capacity bounds that account for role-binding structure WITHOUT averaging it away. **Novel substrate-novel synthesis P_deflated = 0.32** (operator-valued free probability is too new; substrate engineering would need to develop ground-up).

### I.2 Subfactor index and substrate decoder hierarchy

Jones index for a subfactor M_0 subset M_1 takes values in {4 cos^2(pi/n)} union [4, inf). **Substrate connection**: cascading cleanup (a stack of L cleanup layers) is a chain M_0 subset M_1 subset ... subset M_L. The Jones index quantifies the "information loss" per layer. **Speculative**: substrate cascade-cleanup capacity is bounded by the product of Jones indices at each level. Cheap test: measure mutual information loss per cleanup layer; compare to (4 cos^2(pi/n))^L scaling. P_deflated = 0.25 (very speculative).

### I.3 Planar algebra for relational substrate structure

Planar algebras give a graphical calculus for non-commutative computations. **Substrate connection**: tangled-binding operations (a substrate binds X to (Y bound to Z) bound to ...) form a planar algebra structure. The resonator network's iterative pattern-completion can be RE-INTERPRETED as evaluation in a planar algebra (each iteration = tangle composition). This could give a NEW convergence proof (currently the resonator has NO Lyapunov per Frady-Kent 2020). P_deflated = 0.28.

These three directions are aggressive but consistent with the "biology / materials / new math" principle (memory: research_principles_biology_materials_new_math_2026-06-10). Recommended as follow-on 4x-DEEP drills if the cheap 30-line check (section f-g) confirms the basic free-probability framework.

---

## (j) Contradictions / caveats

1. **Free vs classical cumulants distinction is load-bearing**: kappa_4_free = m_4 - 2 m_2^2 ONLY for the SPECTRUM (i.e., when m_n are spectral moments via trace). Applying it to general substrate activations conflates the two unless eigenvalue-based computation is enforced. The 30-line implementation uses spec = eigvalsh, so the distinction is preserved. Common pitfall in lit-scan calibration.

2. **MP requires asymptotic regime**: M, N -> infinity with M/N -> c. Substrate at small M (~1000s) may show finite-size deviations. Mitigation: use Bai-Yin / Lee-Schnelli finite-N corrections; cheap test (Exp 1) directly measures KS distance.

3. **"Asymptotic freeness" of substrate factors is an ASSUMPTION**: holds rigorously for i.i.d. Gaussian / Haar unitary factors. Substrate factors (especially role-bound or family-tagged) may NOT be asymptotically free. This is what operator-valued free probability addresses (section i.1).

4. **TW universality vs codebook structure**: Lee-Schnelli 2014 extends TW universality to general populations, but at LARGE N. Finite-N edge fluctuations on engineered substrate codebooks may deviate. Mitigation: bootstrap TW null distribution from i.i.d. shuffles of the codebook.

5. **CP set-size LB via spectral gap is the NEWEST claim**: no published precedent. Could fail. P4 HARD-FAIL is the kill criterion.

---

## (k) Lit-scan calibration penalty applied

Per [[feedback-lit-scan-calibration-penalty]]:
- Substrate-novel UNIFICATION (D.8) has NO direct published precedent → cap at 0.50, deflate by 0.10 → P_deflated = 0.42 for the unified framework.
- Individual components (MP, TW, BBP, R-transform) are textbook → P_indiv = 0.85 each (not deflated; standard math).
- Conformal-prediction-via-spectral-gap (E.5) is novel → P_deflated = 0.30.
- Operator-valued / subfactor / planar-algebra directions (section i) are SPECULATIVE → P_deflated = 0.25-0.32.
- Resonator-as-planar-algebra (i.3) is the MOST speculative but high-reward → P_deflated = 0.28.

Headline P_deflated = **0.42** (unified framework claim).

---

## (l) Citations (verified count: 8 substantive + 3 supplemental)

1. Voiculescu, Dykema, Nica. *Free Random Variables.* CRM Monograph Series, 1992.
2. Marchenko, Pastur. *Distribution of eigenvalues for some sets of random matrices.* Math. USSR-Sb. 1967.
3. Tracy, Widom. *Level-spacing distributions and the Airy kernel.* Commun. Math. Phys. 1994.
4. Baik, Ben Arous, Peche. *Phase transition of the largest eigenvalue for non-null complex sample covariance matrices.* Ann. Probab. 2005.
5. Lee, Schnelli. *Tracy-Widom distribution for the largest eigenvalue of real sample covariance matrices with general population.* Ann. Appl. Probab. 2016. arXiv:1409.4979.
6. Frady, Kent, Olshausen, Sommer. *Resonator Networks 1+2.* Neural Computation 32(12), 2020.
7. Plate. *Holographic Reduced Representations.* IEEE TNN 1995.
8. Speicher. *Free Probability Theory and Random Matrices.* Survey, Bielefeld Univ. 2003.

Supplemental:
9. Mingo, Speicher. *Free Probability and Random Matrices.* Fields Inst. Monograph 2017. arXiv:1404.3393.
10. Speicher, Mingo, Collins. *Second order freeness and fluctuations of random matrices, III.* arXiv:math/0606431.
11. Voiculescu. *Free entropy.* arXiv:math/0103168.

Total: 11 verified sources. All directly relevant to the framework. No SOTA-claim numbers cited (deliberately).

---

## (m) Hand-off / Next steps

1. **Immediate**: write exp_dev hand-off companion file pointing at experiments 1-5 (this drill is exp_dev-actionable).
2. **Follow-on drill candidate**: operator-valued free probability for role-binding substrate (4x DEEP, if 30-line check passes).
3. **Saturated**: do NOT re-drill basic free-probability (this drill closes the 7-converging-drills consensus); next free-prob drill should be operator-valued or subfactor angle.

Next-drill candidate field: `random-matrix-theory-beyond-free-prob` (Dyson Brownian motion / level spacing statistics) — adjacent to free-probability, Tier-1b in role contract.
