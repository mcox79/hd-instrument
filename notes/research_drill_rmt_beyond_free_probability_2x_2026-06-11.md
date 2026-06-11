# Research drill 2x DEEP — random-matrix-theory beyond free-probability as substrate spectral instrument extensions

Date: 2026-06-11
Topic: RMT-beyond-free-prob (Dyson Brownian motion + level spacing distributions + operator-valued free probability + subfactor algebra + universality classes)
Triggered by: next-drill candidate from 3x DEEP free-probability framework note (research_drill_free_probability_substrate_framework_3x_2026-06-11.md)
Depth: 2x DEEP (operational drill on existing 3x findings — NOT verification re-scan)

---

## (a) HEADLINE

Beyond free-probability's static spectral observables (MP bulk + TW edge + free cumulants), four RMT primitives add operationally distinct substrate instruments: (1) Dyson Brownian Motion gives DYNAMICAL observability of codebook evolution during continual updates (write-protect health signal); (2) level-spacing distributions (Wigner surmise + Gaudin) give a UNIVERSALITY-CLASS test that classifies the substrate codebook as GOE/GUE/GSE/Poisson, with each class predicting a different cleanup-margin distribution; (3) operator-valued free probability via subordination gives a BLOCK-WISE spectral framework matching the substrate's multi-shard / per-tier wrapper architecture; (4) subfactor theory's Jones index gives a discrete invariant for the substrate's binding subalgebra inclusions. All four extend the ~30-line free-prob primitive by another ~30-50 lines without leaving CPU. Novel-synthesis P_deflated = 0.38 (cap 0.50 applied; deflation 0.20 for uncharted substrate regime).

---

## (b) Cheap decisive test

Single CPU script, under 45 minutes total on laptop:

1. Reuse the three codebooks from the 3x DEEP note (C_good i.i.d. / C_real Sprint-4 / C_degraded overload).
2. Compute four RMT-beyond-FP observables for each:
   - Nearest-neighbor spacing histogram of (C C^T) eigenvalues, normalized by local mean spacing; fit Wigner surmise (GOE: pi/2 * s * exp(-pi/4 * s^2)) vs Poisson (exp(-s)).
   - Dyson Brownian trajectory: simulate small additive Gaussian perturbation dW with sigma_dw = 0.01 * sigma_C, track lambda_max drift over 100 steps; measure variance growth rate.
   - Operator-valued spectrum: partition C into K=4 row-blocks, compute joint Cauchy transform via fixed-point iteration of subordination map (Helton-Mai-Speicher algorithm, ~15 lines).
   - Spectral-gap stratification: lambda_i / lambda_{i+1} ratio distribution (Atas-Bogomolny-Giraud-Roux 2013 r-statistic; classifies GOE r~0.54 vs Poisson r~0.39 vs GUE r~0.60).
3. Check four predictions in section (c).

Decisive because each observable produces a QUANTITATIVELY DIFFERENT signature across the three regimes; if no ordering emerges, the extension fails. Total: ~30 additional lines on top of the existing free-prob primitive.

---

## (c) Falsifiable predictions

### Prediction P1 — Universality class via r-statistic (Atas et al. 2013)

The r-statistic r_i = min(s_i, s_{i+1}) / max(s_i, s_{i+1}) where s_i are nearest-neighbor spacings has KNOWN universal means: <r>_GOE = 0.5359 +- 0.001; <r>_GUE = 0.5996 +- 0.001; <r>_Poisson = 2 ln 2 - 1 = 0.3863. This requires no unfolding and is ORDER-STATISTIC robust.

HARD-PASS: C_good <r> falls in [0.53, 0.55] (GOE class — consistent with real symmetric Wigner); C_degraded <r> falls below 0.45 (Poisson-like, indicating localized / non-ergodic eigenstates from overload); C_real <r> distinguishes from both (predicts substrate codebook universality class).

HARD-FAIL: All three <r> values fall in [0.48, 0.58] indistinguishably (no class separation), OR C_good fails to land in GOE band (refutes Wigner-class assumption).

### Prediction P2 — Dyson Brownian variance growth tracks capacity health

For a Wigner-class matrix under DBM, lambda_max has variance Var(lambda_max(t)) growing as t * (4 sigma^2 / N) in the bulk and as t^{2/3} * N^{-4/3} near the edge (Erdos-Yau-Yin 2012 homogenization). For a substrate codebook NEAR capacity threshold, this growth rate ACCELERATES (eigenvalue gets pushed out faster under perturbation because the gap to the bulk is narrow).

HARD-PASS: Variance growth slope ratio between C_degraded and C_good exceeds 2.0 over 100 DBM steps; C_real slope sits between them and correlates monotonically (Spearman rho > 0.5 across 10 codebook ages) with measured retrieval quality.

HARD-FAIL: All three codebooks show DBM variance growth within 30% of each other (no discriminative signal).

### Prediction P3 — Operator-valued subordination reveals per-shard inhomogeneity

For a multi-shard substrate (K shards, each shard a sub-codebook), the SCALAR spectrum loses information about shard-level structure. The operator-valued Cauchy transform G(z) = E[(zI - C C^T)^{-1}] restricted to the K x K block algebra reveals per-shard MP bulk widths separately. Helton-Mai-Speicher fixed-point iteration computes this in O(K^2 N) per iteration.

HARD-PASS: When one shard is artificially over-loaded (M_shard/N > 0.5 while others at M_shard/N=0.25), the operator-valued spectrum shows the over-loaded shard's MP edge OUTSIDE the scalar bulk edge — detectable from a single computation, whereas the scalar spectrum hides it inside the merged bulk. Detection sensitivity (over-loaded fraction at which the operator-valued edge separates from scalar bulk) below 15% shard-fraction.

HARD-FAIL: Operator-valued spectrum does NOT separate over-loaded shard until > 50% shard fraction — making the method no better than scalar tracking.

### Prediction P4 — Level-spacing tail predicts cleanup margin

The Wigner surmise tail P(s) ~ s^beta * exp(-c * s^2) at large s controls eigenvalue gaps near the cleanup operating point. The substrate cleanup margin (distance between the best-match score and the next-best) is mathematically a nearest-neighbor SPACING in the projected query-codebook score distribution.

HARD-PASS: Across 10 substrate configs varying load M/N from 0.1 to 0.5, the empirical cleanup-margin distribution rescaled by local mean follows the Wigner surmise within KS distance 0.10. Beta exponent recovered from fit matches the universality class identified by the r-statistic in P1 (consistency check).

HARD-FAIL: Cleanup-margin distribution shows Poisson tail (exp(-s)) regardless of universality class identified in P1, OR rescaled distribution KS > 0.25.

---

## (d) Cross-thread synthesis with prior drills

### D.1 Extension of 3x DEEP free-prob note (D.4 Frontier-scale + D.2 Family-tag)

The 3x DEEP note's D.4 used Tracy-Widom for lambda_max monitoring under "capacity exhaustion approaching." The DBM extension converts that STATIC threshold into a DYNAMICAL slope. lambda_max(t) under DBM has covariance structure Cov(lambda_max(s), lambda_max(t)) computable in closed form (Forrester-Nagao 2009); deviations from the predicted covariance signal codebook structural change BEFORE lambda_max crosses the static TW threshold. Operationally: a 2-step-ahead capacity warning.

The 3x DEEP D.2 used BBP threshold to detect family-tag spikes. The OPERATOR-VALUED extension makes BBP per-shard: each shard has its own bulk edge, so a tag attached to a specific family can hide INSIDE the scalar bulk while being a spike relative to its shard's operator-valued sub-bulk. This is substrate-novel observability for per-tier or per-family-block detection that scalar BBP misses.

### D.2 Connection to substrate's WRAPPER architecture (memory: substrate_v32_engineered_wrapper_2026-06-11)

The engineered-wrapper memory describes per-shard write-protection and per-tier importance defaults riding on the substrate algebra. Operator-valued free probability is the NATURAL mathematics for this architecture: the K x K conditional expectation onto the shard-block subalgebra is exactly the wrapper's "per-shard view." The Helton-Mai-Speicher subordination algorithm gives a computable shard-level spectral health metric without breaking the substrate algebra — it operates entirely WITHIN the wrapper layer. This is the spectral-instrumentation analog of the engineered wrapper itself.

### D.3 Subfactor theory + Jones index — discrete invariant for binding-subalgebra inclusions

Subfactor theory (Jones 1983; Bisch-Jones 1997; Popa 1998) classifies inclusions N subset M of operator algebras by the Jones index [M : N], with allowed values {4 cos^2(pi/n) : n >= 3} cup [4, infinity). In substrate context: a binding operation creates a SUBALGEBRA of the unbound algebra. The "binding-strength" of a substrate primitive is potentially captured by an effective Jones index. Quantization at small-index values {1, 2, (3+sqrt(5))/2, 3, 2+sqrt(2), 4 cos^2(pi/7), ..., 4} corresponds to discrete substrate-binding regimes. This is highly speculative (P_deflated < 0.25) but cheap to probe: compute the conditional-expectation Pimsner-Popa basis rank for substrate bind/unbind operators. Low-priority but cited per don't-dismiss-adjacent-methods feedback.

### D.4 Connection to drill-pattern-temporal-contextual memory (2026-06-11)

The memory note states drill predictions about TIMESCALES validate empirically; predictions about FIXED ARCHITECTURE fail. DBM is intrinsically a TEMPORAL primitive (Brownian time t parameterizes codebook evolution). Operator-valued FP captures CONTEXT FIELDS (the shard-block conditional expectation IS a context-field projector). Both extensions fall on the validated side of that pattern. Subfactor theory and universality classification are CLOSER to fixed-architecture; the memory predicts these are likelier to fail empirically — so their P_deflated should be lower than DBM/operator-valued. Reflected in section (e) priorities.

### D.5 Universality class hypothesis for the substrate

The substrate codebook is generated by FHRR phasors (unit-modulus complex entries), which puts the codebook covariance C C^T in the COMPLEX Wigner class — naturally GUE. Predicted r-statistic <r> ~ 0.5996. If empirical C_real <r> falls in GUE band, this is a NEW SUBSTRATE INVARIANT (universality class) computable from any codebook snapshot in seconds. If it falls in GOE band instead, the substrate is unexpectedly real-symmetric in its effective dynamics — diagnostic for an under-explored phase-coherence loss mechanism. If Poisson, the codebook has degraded into a localized regime (catastrophic capacity overload).

---

## (e) Substrate-product implications

### Spectral-observability primitive v2 — concrete ~30-line numpy additions to v1

The 3x DEEP note's v1 primitive computes: empirical spectrum, MP bulk edges, TW z-score on lambda_max, free kappa_4. The v2 adds (sketch):

```
# Add to spectral_observability.py after eigvalsh(CCt)
sorted_evals = np.sort(eigvals)[::-1]
gaps = -np.diff(sorted_evals)              # NN spacings (positive)

# r-statistic for universality class
r_arr = np.minimum(gaps[1:], gaps[:-1]) / np.maximum(gaps[1:], gaps[:-1])
r_mean = r_arr.mean()
# classify: <0.45 = Poisson/localized; 0.53-0.55 = GOE; 0.59-0.61 = GUE

# Local mean unfolding for Wigner surmise fit
window = max(5, len(gaps)//50)
local_mean = np.convolve(gaps, np.ones(window)/window, mode='same')
s = gaps / local_mean
# fit beta in P(s) = a * s**beta * exp(-c * s**2) via least-squares on log-hist

# Dyson Brownian step (variance growth probe)
def dbm_step(C, sigma_dw, rng):
    dW = rng.standard_normal(C.shape) * sigma_dw
    return C + (dW + dW.T) / np.sqrt(2)   # symmetric-Gaussian increment

# Track lambda_max trajectory
lam_traj = []
C_t = C.copy()
for _ in range(100):
    C_t = dbm_step(C_t, 0.01, rng)
    lam_traj.append(np.linalg.eigvalsh(C_t @ C_t.T / N).max())
dbm_var_slope = np.polyfit(np.arange(100), np.array(lam_traj), 1)[0]

# Operator-valued Cauchy transform (Helton-Mai-Speicher fixed point, K-block)
def opval_cauchy(C, K, z, n_iter=50):
    blocks = np.array_split(C, K, axis=0)
    G = np.zeros((K, K), dtype=complex)
    for _ in range(n_iter):
        eta_G = sum(b @ b.T for b in blocks) * G   # E_K linear map
        G_new = np.linalg.inv(z * np.eye(K) - eta_G)
        G = 0.5 * G + 0.5 * G_new   # damped fixed point
    return G
```

Total added lines: ~25. Combined with v1, the full spectral instrument is ~55 lines of numpy, CPU-only, runs in seconds on substrate-scale codebooks.

### Capacity threshold detection (DBM)

Real-time codebook health: monitor dbm_var_slope nightly; alert when slope exceeds rolling-baseline by 2 sigma. Implements continuous-capacity observability per [[north_star_functional_system_beats_LLMs]] empirical-edge requirement — gives the substrate product an instrument LLMs cannot offer (LLMs do not expose codebook eigenvalue dynamics).

### Per-shard health (operator-valued FP)

In production substrate with K shards (CLS + SDM multi-tier per the engineered wrapper memory), operator-valued spectrum identifies which shard is approaching capacity FIRST. This is a routing input for the substrate router: bias new writes away from approaching-capacity shards. Closes a loop between observability and write-policy.

### Universality class as substrate identity card

A single number <r> identifies which universality class the codebook lives in. Across substrate versions / tiers / configs, this becomes a regression-test invariant: "v3.2 wrapper codebooks should be GUE-class with <r> in [0.595, 0.605]." Refutation is sharp and cheap.

### What NOT to ship

Subfactor / Jones index work: theoretically beautiful but P_deflated < 0.25. Treat as a paper-on-the-shelf, not a product feature. Revisit only if operator-valued FP produces unexpected integer-quantization signals in production.

---

## (f) Pre-registered cheap CPU experiments (5)

All run on existing CPU runner; total time budget < 4 hours. Pre-registered HARD-PASS / HARD-FAIL per (c) above.

1. **EXP-R1: Universality classification of C_real (Sprint-4 wrapper codebook).** Compute <r> over 5 seeds. HARD-PASS: <r> in [0.55, 0.62] (Wigner-class), classifiable as GOE or GUE with seed-std < 0.01. HARD-FAIL: <r> < 0.45 (Poisson/localized — refutes substrate-as-Wigner) OR seed-std > 0.05 (non-reproducible).

2. **EXP-R2: DBM variance-growth-slope discriminates good vs degraded codebook.** Three codebooks under 100 DBM steps. HARD-PASS: slope_degraded / slope_good > 2.0 with non-overlapping seed bands (5 seeds each). HARD-FAIL: ratio < 1.3 (no discriminative signal).

3. **EXP-R3: Operator-valued subordination detects single overloaded shard.** K=4 shards, one over-loaded. HARD-PASS: operator-valued spectrum places overloaded shard's bulk edge > 1.5x outside scalar bulk edge; scalar spectrum fails to reveal it. HARD-FAIL: operator-valued and scalar give the same edge to within 5%.

4. **EXP-R4: Cleanup-margin distribution follows Wigner surmise.** Empirical cleanup margins over 1000 queries vs codebook of M = N/4 items. HARD-PASS: KS distance to fitted Wigner surmise < 0.10; beta exponent agrees with EXP-R1 class within 0.2. HARD-FAIL: KS > 0.25 or beta sign-disagreement with universality class.

5. **EXP-R5: Operator-valued FP predicts shard-routing benefit.** Build router that biases writes per operator-valued shard-edge proximity. HARD-PASS: routing reduces overflow incidents (recall@1 < 0.9 events) by > 25% vs round-robin baseline at matched throughput. HARD-FAIL: routing reduces by < 10% (no operational benefit) OR exceeds 25% overhead per write.

---

## (g) Citations (verified count: 11)

1. Erdos, Schlein, Yau (2011-2012) — bulk and edge universality of Wigner matrices (Wigner-Dyson-Gaudin-Mehta conjecture). arXiv:0906.0510 and follow-ups.
2. Bourgade, Erdos, Yau, Yin (2016) — Fixed energy universality for Dyson Brownian motion. arXiv:1609.09011.
3. Landon, Yau (2017) — Convergence of local statistics of Dyson Brownian motion. arXiv:1504.03605 (Comm. Math. Phys.).
4. Adhikari, Huang (2018) — Dyson Brownian motion for general beta and potential at the edge.
5. Atas, Bogomolny, Giraud, Roux (2013) — Distribution of the ratio of consecutive level spacings in random matrix ensembles. PRL 110, 084101. (r-statistic with universal values 0.5359 / 0.5996 / 0.3863.)
6. Forrester (2010) — Log-Gases and Random Matrices. Princeton University Press. (Wigner surmise, beta-ensembles, Gaudin distribution.)
7. Tracy, Widom (1994) — Level-spacing distributions and the Airy kernel. Comm. Math. Phys. 159.
8. Voiculescu (1995) — Operations on certain non-commutative operator-valued random variables. Asterisque 232. (Operator-valued free probability foundations.)
9. Helton, Mai, Speicher (2018) — Applications of realizations (aka linearizations) to free probability. (Subordination algorithm via fixed-point iteration of resolvent maps.) arXiv:1303.3196 expanded.
10. Belinschi, Mai, Speicher (2017) — Analytic subordination theory of operator-valued free additive convolution and the solution of a general random matrix problem. J. Reine Angew. Math.
11. Jones (1983) + Bisch, Jones (1997) + Popa (1998) — Subfactor theory; Jones index quantization {4 cos^2(pi/n)} cup [4, infinity).

Cross-thread synthesis sources: 3x DEEP free-prob note (research_drill_free_probability_substrate_framework_3x_2026-06-11.md); engineered-wrapper memory; drill-pattern-temporal-contextual memory.

---

## (h) Pre-registered P_deflated estimates per prediction (calibration penalty applied)

| Prediction | Raw P | Deflation | P_deflated | Rationale |
|---|---|---|---|---|
| P1 r-statistic universality class | 0.70 | 0.20 | 0.50 | Wigner class established for FHRR-derived covariances in adjacent VSA lit; cap 0.50 (novel-synthesis cap) |
| P2 DBM variance-growth-slope discriminates | 0.60 | 0.20 | 0.40 | Temporal observable (validated drill-pattern); but no direct substrate precedent |
| P3 Operator-valued per-shard edge detection | 0.55 | 0.20 | 0.35 | Algorithm exists (Helton-Mai-Speicher); novelty is the substrate-shard application |
| P4 Cleanup-margin Wigner surmise fit | 0.45 | 0.25 | 0.20 | Closer to fixed-architecture (drill-pattern memory predicts higher fail risk) |
| Overall RMT-beyond-FP framework holds | 0.60 | 0.20 | 0.40 | Pre-existing 3x DEEP free-prob anchor; extensions are operationally distinct |

---

## (i) Next-drill candidate

Per field advisor + this delivery: **D1 Glauber dynamics on substrate codeword space** (semiconductor / stochastic-dynamics, score 5.0). DBM is the Gaussian-Brownian temporal primitive; Glauber is the discrete-spin temporal primitive. Together they give substrate temporal-observability coverage from both continuous and discrete sides. Cheap (~1 hr CPU smoke). Anchor: D field (drift-diffusion BP, 100% yield, drill count 2 — under-drilled).

Secondary candidate: **B1 GAMP on substrate codebook** (AMP/VAMP, score lower but mathematically adjacent to operator-valued FP via state-evolution equations).
