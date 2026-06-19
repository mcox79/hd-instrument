# Cross-Domain Probe #3 + E3 5th-Family Selection — 2026-05-24

Third pass per [[feedback-aggressive-cross-domain-research]] + verdict_handler's
flagged E3 unresolved selection.

Probes #1 and #2 already covered: TSP/QAP, Ramanujan, frame/wavelet, AMP/VAMP,
RSB+free cumulants, NTK, sphere packing, quantum chaos ETH, tensor PCA,
list-decoding, QECC/MUB/stabilizer, ICA/JADE, optimal experimental design,
NK fitness, compressed sensing weaken-RIP, Kac-Rice complexity, molecular
spectral moments.

This probe pushes further from the substrate's natural orbit. 8 parallel
Sonnet WebSearch sub-agents per [[feedback-subagent-model-optimization]];
generic math terms only per [[feedback-query-privacy-decomposition]];
wallclock ~75s.

---

## 1. Random graph spectra (beyond Ramanujan)

**Query:** random graph spectra Erdos-Renyi stochastic block model spectral
gap community detection bulk edge universality

**Landed:** sparse Erdos-Renyi has NO spectral gap (sharp deviation from
denser regime semicircle). Non-backtracking matrix (arxiv 1501.06087) gives
weak Ramanujan property for sparse SBM and is the right object for
community detection at the Kesten-Stigum threshold tau = (a-b)^2 / [2(a+b)] =
1. Regularized spectral clustering + non-backtracking spectrum recovers
communities right at the conjectured information-theoretic threshold.

**Cross-applicable: MEDIUM.** The non-backtracking-matrix spectrum is
operationally what one wants when the **direct adjacency / Gram spectrum is
contaminated by structured outliers** — which is precisely the regime our
Kerdock-versus-Haar dichotomy lives in. Substrate's BBMD signature is
"structured outliers + bulk-bounded interior"; the SBM literature gives a
principled construction (non-backtracking) that **removes the high-degree
outlier contribution while preserving community structure**. This is
**candidate machinery to extract the BBMD signal from the spectral bulk
without pre-thresholding** — i.e., a more principled alternative to the
current MP-KS pre-test. Honest read: vocabulary upgrade, not a new
mechanism; would replace MP-KS edge-truncation heuristic with a
non-backtracking matrix construction whose spectral guarantees are tight.

---

## 2. Anti-concentration inequalities

**Query:** anti-concentration inequality Berry-Esseen log-Sobolev decoupling
moment divergent random matrix

**Landed:** Berry-Esseen for products of random matrices (arxiv 1907.02438,
2010.00557) under polynomial-moment conditions; rate ((log n)/n)^(q/2-1)
for moment order q in (2,3], rate 1/sqrt(n) for q>=4. Matrix
anti-concentration inequalities (STOC 2022, dl.acm 3519935.3520060).
Anti-concentration for **random tensors** with bounded third moment
(Vershynin; Springer s00440-023-01211-x).

**Cross-applicable: YES — medium-high.** The "moment-divergent kappa_n
diverges from MP" framing is exactly what anti-concentration bounds
formalize: kappa_n divergence is a quantitative statement about how
**non-concentrated** the spectrum is around the MP reference. The matrix
anti-concentration STOC 2022 result gives us **lower bounds** on the
divergence we should expect from generic random matrices, which lets us
calibrate "how much kappa_n divergence is structural vs noise." If the
substrate's kappa_n divergence is LARGER than the matrix-anti-concentration
lower bound for an iid-Gauss matrix of the same shape, that is rigorous
evidence the divergence is structural. **Tool transfer — directly relevant
to the v175 promotion claim** (one of the things the audit would want to
hammer is "is the kappa_n divergence outside the noise floor predicted by
matrix anti-concentration?"). Worth a CPU probe.

---

## 3. Hypothesis testing for distribution comparison (MMD / KSD / Wasserstein)

**Query:** maximum mean discrepancy MMD Stein discrepancy Wasserstein
distribution two-sample test spectral measure

**Landed:** MMD (JMLR, Gretton et al) and Kernel Stein Discrepancy (KSD)
are mature two-sample / goodness-of-fit testers; smoothed Wasserstein
**interpolates** between Wasserstein (one limit) and Energy distance
(other limit) via entropic regularization (arxiv 1509.02237, 2102.05573).
KSD = MMD under certain Stein-kernel constraints. Closed-form MMD
expressions for Wasserstein autoencoders (arxiv 1901.03227). FastMMD
(circular discrepancy ensemble) for efficient two-sample test (1405.2664).

**Cross-applicable: YES — high.** This is **the natural replacement for
the MP-KS pre-test in Cap 12**. KS-distance on the spectral distribution
is the weakest possible discrepancy test; MMD / KSD / sliced-Wasserstein
gives strictly more power, particularly for **high-dimensional and
multi-modal** spectral measures (which BBMD spectra are). The Cap 12 v175
promotion is currently borderline (rho=0.700); a stronger discrepancy test
would either tighten the rho ceiling OR reveal that the borderline was a
test-power artifact. **High value, low cost.** Anchor candidate.

**Anchor proposal:** swap MP-KS pre-test for sliced-Wasserstein-2 + MMD
discrepancy. Re-run v175 alpha-rho regression with new pre-test gating.
CPU job ETA ~2h on existing v175 cached spectra. Hard-fail: rho changes
by < 0.05 (MP-KS was fine; nothing to gain). Hard-pass: rho >= 0.80 with
new pre-test (tightens the claim). Middle: rho in [0.70, 0.80] (modest
calibration improvement).

---

## 4. Numerical linear algebra randomized sketching

**Query:** randomized numerical linear algebra sketching Halko Martinsson
Tropp subsampled randomized Hadamard transform spectral preservation

**Landed:** Halko-Martinsson-Tropp 2011 SIAM Review (foundations);
Tropp 2011 "Improved analysis of SRHT" — SRHT (which is already one of
our 4 Cap 12 families) preserves Euclidean geometry of an entire
subspace with high probability. Sharper spectral-norm error bounds under
reasonable singular-value decay (epubs.siam 17M1111590).

**Cross-applicable: HIGH — but mostly endorsement of existing setup.** The
sketching literature is exactly the regime Cap 12 operates in: SRHT is the
canonical structured-sketch; spectral-norm preservation guarantees are
**why** the AMP-error predictor should work cross-family. The
Halko-Martinsson-Tropp guarantee is the rigorous formal statement that
SRHT-style sketches preserve singular-value structure. Honest read: this
**validates** the Cap 12 framework rather than extending it. Useful for
writing up Cap 12 against, but **not** a new mechanism.

---

## 5. Quantum reference frames / asymmetry

**Query:** quantum reference frames asymmetry Bartlett Rudolph Spekkens
mutually unbiased bases symmetry resource theory

**Landed:** Bartlett-Rudolph-Spekkens 2007 (quant-ph/0610030): "unspeakable"
quantum information (directions in space, moments in time) is encoded by
reference-frame data; Gour-Spekkens resource theory of quantum reference
frames; mutually unbiased frames (arxiv 2110.08293) generalize MUBs +
ETFs + simplices into a single object class.

**Cross-applicable: YES — medium-high; structural.** The mutually-unbiased-
**frames** generalization (2026) gives a vocabulary where MUBs, ETFs,
simplices, POVMs, and equiangular tight frames are all special cases of
one structure. Substrate uses Kerdock-MUB (already established in probe
#2 domain 3); the "asymmetry / resource theory" frame says: substrate's
codebook stores **directional/orientational information** as a resource
that gets consumed by measurements. This is a **direct re-expression** of
the substrate's Cap 7 (measurement protocol) in resource-theory language.
Honest read: this is a deep vocabulary upgrade — could change how Cap 7
is written and audited — but not a new experiment.

---

## 6. Approximation theory for high-dim functions

**Query:** approximation theory high dimensional functions Petrushev
DeVore Temlyakov basis nonlinear n-width

**Landed:** N-term approximation in mixed-smoothness Holder-Nikolskii
spaces (arxiv 2102.04370); sparse grids beat curse of dimensionality;
n-widths quantify best linear-subspace approximation; convex n-widths
relate to covering numbers + neural network expressivity (2512.04912);
spectral separation of two-layer NNs vs linear methods.

**Cross-applicable: LOW-MEDIUM.** The basis-dependent error tradeoffs do
have a real echo in substrate: choosing Kerdock basis vs random basis
changes what classes of memory are efficiently representable. But the
approximation-theory literature aims at **function classes** (Sobolev,
mixed smoothness), whereas the substrate's primitive is **codebook**
(combinatorial / algebraic). The bridge would require expressing
"memory contents" as a function-class — abstract and remote. Honest read:
not a near-term direction. Worth keeping in the "if the substrate ever
needs to argue universal-approximation capacity over a continuous
function class" reserve.

---

## 7. Adversarial ML robustness / randomized smoothing

**Query:** adversarial machine learning robustness certified randomized
smoothing spectral norm distribution shift detection

**Landed:** Cohen-Rosenfeld-Kolter 2019 (arxiv 1902.02918) certified
robustness via randomized smoothing — Gaussian noise on input gives
provable L2-ball-radius certification. Universal certified robustness
framework (UniCR 2207.02152) — any Lp under any continuous noise
distribution. Wasserstein-shift accuracy certificates (2201.12440).

**Cross-applicable: YES — medium.** The randomized-smoothing certification
gives a Lipschitz / spectral-norm based **provable lower bound** on
robustness — and the substrate's BBMD signature ("bulk bounded spectrum")
is exactly a Lipschitz-like statement. There may be a real bridge: the
substrate's robustness to depolarization noise (Cap 12 E1 anchor) could
be **certified** in the randomized-smoothing sense if we can express the
substrate's measurement operator as a smoothed classifier. Honest read:
this is the right framework if we ever want to ship a **provable**
robustness claim for substrate memory (as opposed to empirical). Worth
revisiting once Cap 1 (verifiable erase) needs a formal certification
story.

---

## 8. My pick — Topological data analysis (persistent homology)

**Query:** topological data analysis persistent homology spectral matrix
Betti numbers high dimensional point cloud

**Landed:** Persistent homology gives a multi-scale topological summary
of a point cloud (connected components, holes, voids); persistent
combinatorial Laplacian (persistent spectral graph, arxiv 1912.04135)
**unifies persistent homology with spectral theory** — harmonic
persistent spectra recover full topological persistence + provide
geometric / spectral information beyond it. Active TDA-ML crossover
literature (Tandfonline 2023).

**Cross-applicable: MAYBE — speculative but interesting.** The
"persistent spectral graph" is exactly the kind of object that **could**
characterize the kappa_n divergence pattern as a **persistent feature
across noise levels**. If we vary eta (noise level) and track how
persistent homology of the spectral measure changes, the **persistent
features** would be the structural / topological invariants of the BBMD
signature — robust to the noise sensitivity we currently see at Cap 12
v175. Honest read: this is the **most speculative** of probe #3 — no
direct precedent in our setting — but persistent spectral graph machinery
is implementable from pip-installable libraries (`gudhi`, `ripser`).
**Tag as buried-treasure direction.**

---

## 9. E3 5th interpolation family selection

**Already tested in Cap 12:** Kerdock, SRHT, Hadamard, RM(1, m) — 4 families.

**Excluded as degenerate:** Paley (PERFECT_ISOMETRY, kappa_n=0 — confirmed
2026-05-23 in `data/exp_wave14_kappa_paley_quickprobe_v1/metrics.json`).

**Candidate evaluation:**

| candidate | kappa_n profile prediction | implementation cost | predicted Cap 12 outcome |
|---|---|---|---|
| **Gold sequences (m=10, N=1023)** | BBMD_CANDIDATE confirmed locally (`exp_wave14_kappa_gold_quickprobe_v1`): kappa_n diverges from MP, spectrum bulk-bounded [0, 1.997] within MP edges [0, 4]. Non-degenerate. | LOW — script exists, smoke + main both ran. Adjust N to {1023, 4095} (Mersenne) or pad to align with {1024, 4096, 16384}. | Strong cross-family test — Gold shares GF(2^m)-trace algebra with Kerdock but **different combinatorics** (3-valued cross-correlation, no 4-coset). If rho >= 0.50, BBMD predictor is GF(2^m)-trace-generic. If rho < 0.30, Kerdock-4-coset specific. |
| Bent functions / Maiorana-McFarland | Likely BBMD (also GF(2^m)-trace-derived). Same family-class as Kerdock; less discriminating. | MEDIUM — no existing script; would need 2-3h to implement + verify. | Mid-discriminating. |
| ETF from difference sets | Likely PERFECT or near-perfect ISOMETRY (ETFs are extremal in Welch-bound sense). Probably degenerate. | MEDIUM — pip `equiangular-tight-frames` exists. | Likely degenerate (similar failure mode as Paley). |
| Conference / Belevitch / Seidel matrices | Similar to Paley — likely PERFECT_ISOMETRY or near. | LOW — closed-form. | Likely degenerate. |
| GOE / GSE random matrices (beta=1 / 4) | NOT a codebook (random not structured). Fails "structured-codebook character" requirement. | LOW. | Tests beta-dependence not algebraic-codebook predictor. |
| m-sequences alone (LFSR) | Likely PERFECT_ISOMETRY (m-sequences are perfect on a single shift, like Paley). | LOW. | Likely degenerate. |
| RM(r=2, m) | Likely BBMD — same algebra as Kerdock + Hadamard (Kerdock interpolates Reed-Muller orders). Less independent than Gold. | LOW — RM(1, m) script exists, adapt. | Closer to Kerdock; less novel cross-family test. |
| Block-circulant random | Hybrid structured-random; predicted MP-like or weak BBMD. | LOW — `scipy.linalg.circulant`. | Tests "weak structure" axis. |

**Recommendation: Gold sequences (m=10, N=1023; pad to N=1024 with one
zero column or downsample symmetrically) as the 5th family.**

**Justification:**
1. Gold quickprobe ALREADY ran and returned BBMD_CANDIDATE — the
   non-degenerate profile we need.
2. Gold shares GF(2^m)-trace structure with Kerdock (so the kappa_n
   divergence is in the same algebra-family) BUT has **distinct
   combinatorics** (3-valued cross-correlation, no 4-coset structure)
   — so it's a **genuinely cross-family** test of the predictor.
3. Script exists; padding to N=1024 / 4096 / 16384 is cheap.
4. Pre-registered prediction: rho_alpha >= 0.50 (Gold tracks the BBMD
   predictor) — confirms GF(2^m)-trace-generic. Hard-fail: rho_alpha
   < 0.30 (predictor is Kerdock-4-coset specific).

**Predicted outcome:** rho_alpha in [0.50, 0.75] — Gold tracks the
predictor but slightly weaker than Kerdock because of the differing
combinatorics. This is the most **informative** outcome (neither trivial
pass nor trivial fail).

---

## 10. Honest synthesis — operationalization

**What's worth operationalizing from probe #3:**

1. **MMD / Sliced-Wasserstein replacement for MP-KS pre-test (domain 3).**
   This is the highest-yield landing of probe #3: directly applicable to
   the Cap 12 v175 borderline-rho situation, low cost, well-pre-reg-able.
   Anchor: `wave14_mmd_vs_mpks_pretest_v1`.

2. **Anti-concentration noise-floor calibration (domain 2).** The matrix
   anti-concentration STOC 2022 lower bound gives a rigorous reference
   for "how much kappa_n divergence is mere finite-sample noise." Useful
   as audit-defense for Cap 12. Anchor: `wave14_kappa_anticoncentration_floor_v1`.

3. **Gold sequences as 5th E3 family.** Already-validated BBMD_CANDIDATE
   profile; ready to ship.

**What's interesting but not near-term:**
- Persistent spectral graph for noise-robust BBMD signature (domain 8) — speculative, buried-treasure.
- Resource-theory framing for Cap 7 (domain 5) — vocabulary upgrade, not experiment.
- Randomized-smoothing certification for Cap 1 (domain 7) — wait until Cap 1 needs formal certification.

**What probe #3 did NOT find:**
- A new mechanism on the level of probe #2's Kerdock-as-stabilizer-MUB-system isomorphism. The deepest landing in probe #3 is a tool replacement (MMD for MP-KS), not a new structural insight. Honest read: probe #3 is **lower-yield** than probes #1 and #2. Expected: each successive cross-domain pass yields diminishing returns as the highest-relevance fields are explored first. This is healthy — the user's directive to "use free capacity for creative research" continues to produce calibration value, but the marginal mechanism-discovery rate is dropping.

---

**Total: 8 parallel Sonnet WebSearch sub-agents, wallclock ~75s.**
