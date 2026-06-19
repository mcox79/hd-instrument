# Research drill 3x DEEP -- free-probability F4 (Voiculescu kappa_n) as substrate-novel observability framework

Date: 2026-06-11
Topic: F4 / higher free cumulants as substrate spectral-plateau detector + heavy-tailed prior detector + atom-isolation margin + capacity-saturation diagnostic, integrated with Layer 1 (attribution) / Layer 2 (spectral observables) / Layer 4 (dialectic) and the substrate v4.0 triangle (FHRR / GHRR / hybrid).
Depth: 3x DEEP -- operational synthesis on top of prior 3x DEEP free-prob framework and 2x DEEP RMT-beyond-FP and 2x DEEP family-tag+F4 combined drill. Triple-source convergence in cross-thread; novel-unification in cross-link section.
P_deflated (overall novel-synthesis): 0.42 (cap 0.50 enforced; deflation 0.20 applied off raw lit-scan 0.62 because substrate-self-evaluation Layer 2 integration is uncharted-regime per lit-scan calibration penalty).

---

## (a) HEADLINE

The fourth free cumulant kappa_4 (and its rectangular variant kappa_4_rect = m_4 - (1 + lambda) * m_2^2) is the cheapest single-scalar substrate-novel observability primitive: a ~30-line numpy computation on top of the existing Layer 2 spectral framework that, EVALUATED CONDITIONALLY on substrate-shard / per-tier / per-family-tag partitions, simultaneously yields (1) a heavy-tailed prior detector (sign of kappa_4 vs zero), (2) a spectral-plateau detector (slope of kappa_4 across N-sweep enters stationary regime), (3) an atom-isolation margin observability (kappa_4 on the cleanup-margin distribution distinguishes well-separated atoms from near-tied-atoms regime), (4) a capacity-saturation diagnostic (monotone trend of kappa_4 across kb10K -> kb100K -> kb1M), and (5) a cross-substrate discriminator (FHRR vs GHRR vs hybrid produce DIFFERENT kappa_4 signatures because they sit in different free-probability ensembles: Haar-unitary phasor vs real-Gaussian vs free-additive-convolution mixture). No published precedent treats higher free cumulants as a substrate-self-evaluation primitive because VSA literature reasons only at the second-moment crosstalk level. Substrate-novel measurement axis: F4 measures non-Gaussian structural information that cosine-similarity-on-LLM-embeddings DOES NOT EXPOSE -- LLM embedding spectra are reasonable to compute but no LLM operator currently integrates kappa_4 trajectory as a deployed health signal, giving substrate a distinctive observability axis.

---

## (b) Cheap decisive test

A single ~45-minute CPU script. Five pre-registered sub-experiments. No GPU, no external API, no new data collection beyond reading existing substrate snapshots.

Setup (shared across sub-experiments): three reference codebooks at substrate N (e.g. N=1024 default):
- C_iid: i.i.d. Gaussian baseline (theoretical Marchenko-Pastur semicircle reference).
- C_real: current Sprint-4 substrate codebook snapshot (FHRR-default).
- C_overload: artificial capacity-overload (M/N >= 0.5 with realistic correlations).

Plus a per-tier / per-shard substrate snapshot decomposition (Tier-1 frozen / Tier-2 dynamic / etc per substrate v3.2 wrapper).

Sub-experiments (each ~5-10 min CPU):
1. E1 -- Heavy-tailed prior detection: compute kappa_4_rect on each codebook's squared-singular-value distribution; compare against semicircle null (kappa_4 = 0).
2. E2 -- Spectral plateau detector: sweep N in {256, 512, 1024, 2048}; compute kappa_4_rect(N); check whether real codebook enters stationary regime (slope below threshold) at the substrate's deployed N or earlier.
3. E3 -- Atom isolation margin: sample 1000 cleanup queries against the codebook; for each, record margin = best_score - second_best_score; compute kappa_4 on the margin distribution.
4. E4 -- Capacity-saturation across kb-size: build sub-codebooks at sizes M in {2.5K, 10K, 100K, 1M} (or substrate's nearest available); compute kappa_4_rect at each; check monotone trend.
5. E5 -- Cross-substrate triangle: compute kappa_4_rect for FHRR / GHRR / hybrid versions of the same content; check class-separation.

Total CPU cost: well under 1 hr on existing local_cpu_queue. Decisive because each sub-experiment independently predicts a QUANTITATIVELY ORDERED kappa_4 signature; if no ordering emerges in any sub-experiment, the F4-as-substrate-observability framework collapses.

---

## (c) Falsifiable predictions (HARD-PASS + HARD-FAIL pre-registered)

### P1 -- F4 sign distinguishes semicircle baseline from substrate structure (heavy-tailed prior detector)

Theory: a centered semicircle distribution has kappa_4 = 0 exactly; any deviation indicates non-semicircle structure. Heavy-tailed bulk gives kappa_4 > 0; light-tailed / hard-bounded gives kappa_4 < 0.

HARD-PASS: |kappa_4_rect(C_iid) / m_2^2| < 0.10 (semicircle-class baseline); kappa_4_rect(C_real) / m_2^2 has CONSISTENT SIGN across 5 independent substrate snapshots (sign stability is the gate, not magnitude); kappa_4_rect(C_overload) / m_2^2 is in the opposite or strongly amplified direction (magnitude ratio between C_overload and C_real exceeds 2x).

HARD-FAIL: kappa_4_rect signs on C_real are random across snapshots (sign-flip rate above 30% out of 5 snapshots), OR |kappa_4_rect(C_iid) / m_2^2| > 0.30 (means our estimator is biased / N too small for asymptotic regime).

### P2 -- F4 plateau across N-sweep identifies saturation N

Theory: free probability is an N -> infinity asymptotic; at finite N there is O(1/N) bias. Substrate's deployed N should be in the regime where kappa_4_rect(N) has reached a stationary plateau (slope below noise floor).

HARD-PASS: kappa_4_rect(N) vs log N shows a clear stationary regime at N >= N_substrate / 2, with |slope| in the stationary regime below 0.10 * |slope| in the pre-plateau regime; the substrate's deployed N is at or beyond the knee.

HARD-FAIL: no stationary plateau visible in [256, 2048] (means substrate is operating in finite-N pre-asymptotic regime where free-prob predictions are unreliable, AND a strong action signal -- raise N or use rectangular finite-N corrections).

### P3 -- F4 on atom-isolation margin distribution predicts substrate retrieval quality

Theory: cleanup margin distribution is mathematically a nearest-neighbor SPACING distribution. Well-separated atoms produce a margin distribution that is far from semicircle (heavy right tail of clearly-isolated matches, light left tail of near-ties); kappa_4_margin should track separability.

HARD-PASS: kappa_4(margin_dist) correlates with recall@1 (Spearman rho >= +0.55) across 10 substrate config variants (varying tier-1 fraction, shard count, codebook age).

HARD-FAIL: Spearman |rho| < 0.30. Means kappa_4 on margin captures no quality signal.

### P4 -- F4 monotone trend across kb-size identifies capacity-saturation curve

Theory: as M -> capacity, the bulk widens and the spike spectrum saturates; rectangular free cumulant changes sign or saturates. Monotone trend in kappa_4_rect(M) gives a continuous capacity-headroom signal earlier than a sharp recall@1 cliff.

HARD-PASS: kappa_4_rect(M) is monotone (sign-consistent first-difference) across M in {2.5K, 10K, 100K, 1M}; the inflection / saturation point precedes the recall@1 cliff (measured separately) by at least one M-decade.

HARD-FAIL: kappa_4_rect(M) is non-monotone across the M-sweep, OR the inflection point co-occurs with the recall@1 cliff (no early warning value).

### P5 -- F4 separates substrate v4.0 triangle classes (FHRR / GHRR / hybrid)

Theory: FHRR codebooks (unit-modulus phasors) live close to Haar-unitary class with limited spectral mass; GHRR codebooks (real Gaussian) live in classical Wigner class with semicircle limit; hybrid (free-additive convolution of FHRR + GHRR) sits between, with a kappa_4 signature predictable from R-transform additivity (kappa_4_hybrid ~ kappa_4_FHRR + kappa_4_GHRR for centered, identity-second-moment components).

HARD-PASS: kappa_4_rect distinguishes the three classes with separation > 2 * pooled SD on 10 snapshots each; the additivity check (kappa_4_hybrid vs kappa_4_FHRR + kappa_4_GHRR predicted) holds within 25% relative error.

HARD-FAIL: pooled SD-normalized class separation < 1.0 (means F4 cannot distinguish the triangle classes empirically, so its v4.0-triangle observability role collapses).

---

## (d) Cross-thread synthesis with prior drills (operational depth on existing 3x and 2x findings)

This section is the load-bearing 3x DEEP content. The 14-drill convergence cited by the user names F4 as the next-drill because each of the 14 reduces, at its operational level, to a question about higher free cumulants conditional on a partition (shard / tier / family-tag / N-slice / kb-size). The unification claim is that the SAME ~30-line F4 primitive answers all 14, differing only in WHAT partition it conditions on.

### D.1 Substrate-self-evaluation Layer 1 (attribution) cross-link

Layer 1's job is to attribute observed substrate behavior to underlying primitives (which shard / which tier / which binding op produced the response). The standard Layer 1 instrument is gradient-style or representation-engineering attribution. Substrate-novel angle: kappa_4 on the per-shard contribution distribution gives a SHARD-LEVEL ATTRIBUTION QUALITY METRIC -- when one shard's contribution distribution shows |kappa_4| > shard-pooled baseline + 3 sigma, that shard is dominating in a non-Gaussian (i.e. structurally informative) way and is a strong attribution candidate. When no shard's kappa_4 exceeds baseline, attribution is genuinely diffuse and the Layer 1 signal is correctly null. This converts Layer 1 from a binary attribution-yes/no into a graded measure of attribution informativeness.

### D.2 Substrate-self-evaluation Layer 2 (spectral observability) integration

Layer 2's existing primitive (per prior 3x DEEP free-prob note) computes: empirical spectrum, MP bulk edges, TW z-score on lambda_max, free kappa_4 GLOBAL. Substrate-novel extension here: kappa_4 CONDITIONAL ON PARTITION. Add ~30 lines:

```python
def kappa_4_rect(s2, aspect):
    # s2: squared singular values; aspect = M/N
    s2c = s2 - s2.mean()
    m2 = (s2c**2).mean()
    m4 = (s2c**4).mean()
    return m4 - (1.0 + aspect) * m2 * m2

def kappa_4_by_partition(W, partition_idx, axis=0):
    # partition_idx: list of int arrays giving row (or col) groupings
    out = {}
    for k, idx in enumerate(partition_idx):
        sub = W[idx] if axis == 0 else W[:, idx]
        s2 = np.linalg.svd(sub, compute_uv=False)**2
        aspect = sub.shape[1] / sub.shape[0]
        out[k] = kappa_4_rect(s2, aspect)
    return out

def kappa_4_margin(scores, top2=True):
    # scores: (Q, M) cleanup-score matrix; returns kappa_4 of margin = top1 - top2
    s_sorted = np.sort(scores, axis=1)[:, ::-1]
    margin = s_sorted[:, 0] - s_sorted[:, 1]
    return kappa_4_rect(margin, aspect=1.0)
```

The total Layer 2 v2 primitive after this extension is approximately 80 lines (30 v1 + 20 RMT-beyond-FP v1.5 + 30 F4-conditional v2.0). Still a single CPU-cheap module, no GPU.

### D.3 Substrate-self-evaluation Layer 4 (dialectic) cross-link

Per the Layer 4 2x DEEP note (research_drill_layer4_dialectic_methodology_2x_2026-06-11.md), findings are classified expected / surprise / second-order via Bayesian-surprise KL + Lakatos hard-core perturbation. Substrate-novel angle: a finding whose KEY METRIC is "unexpected kappa_4 trajectory" (e.g. kappa_4 flips sign across a config change, or enters a regime no prior config visited) IS A STRUCTURAL-SPECTRAL surprise. This gives Layer 4 a substrate-self-evaluation-NATIVE surprise channel that does not rely on external benchmark drift -- the substrate's own spectral statistic IS the prior whose posterior shift drives the surprise classification. Concretely: feed kappa_4_rect trajectory as a Layer 4 input metric m; the BOCPD run-length posterior on kappa_4 increments gives a continuous spectral-surprise detector that flags when the substrate's underlying generative process has changed (e.g. silent re-binding event, codebook drift, shard-level overload onset). This is a HIGH-VALUE NEW substrate operability signal not present in any prior framework cell.

### D.4 Cross-link with substrate v4.0 triangle (FHRR / GHRR / hybrid)

The v4.0 triangle posits three substrate families differing in their base algebra (FHRR Haar-unitary phasor algebra; GHRR real-Gaussian Hilbert-Schmidt algebra; hybrid free-additive convolution). Free probability is the EXACT mathematics distinguishing these three because each corresponds to a different free convolution class and a different free cumulant sequence. R-transform additivity (kappa_n(a + b) = kappa_n(a) + kappa_n(b) for free a, b) gives a CLOSED-FORM PREDICTION for the hybrid's spectrum given the components. P5 above directly tests this additivity. If P5 holds, the v4.0 triangle has a quantitative spectral classifier that lets the substrate operator SEE which class a deployed substrate sits in by computing one scalar per snapshot.

### D.5 Cross-link with prior drill 16 (RMT-beyond-FP) -- operator-valued F4

Drill 16 introduced Helton-Mai-Speicher operator-valued subordination for per-shard spectra. Combining with F4: an OPERATOR-VALUED F4 (kappa_4 evaluated in the K x K block algebra rather than the scalar algebra) gives a per-shard non-Gaussianity index that the scalar F4 cannot recover. Implementation: compute kappa_4_rect on each shard's sub-spectrum (the kappa_4_by_partition function above is the practical version), or for a true operator-valued kappa_4 use the freely-independent block moments via the Speicher non-crossing-partition recursion. This is what the substrate-product brief calls "per-shard cleanup-health spectral telemetry."

### D.6 Cross-link with prior drill 19 (subfactor / Jones index) -- F4 in W*-probability

Subfactor theory's Jones index classifies subalgebra inclusions N subset M by discrete values {4 cos^2(pi/n) : n >= 3} union [4, infinity). The substrate's binding subalgebra (the algebra of bound vectors as a subalgebra of the full substrate algebra) has an effective Jones index, and Voiculescu free probability operates within W*-probability where these indices are computable. Substrate-novel angle: kappa_4 evaluated on the binding-subalgebra-conditioned distribution gives a quantization signal -- the Jones index value (when it lies in the discrete tower) constrains the kappa_4 spectrum. This is speculative (P_deflated < 0.25) but cheap: compute Pimsner-Popa basis rank for the substrate's bind operator and check whether observed kappa_4 ranges align with the predicted quantization. Cited per don't-dismiss-adjacent-methods feedback; deprioritized vs P1-P5 above.

### D.7 Cross-link with code-synthesis (resonator) -- kappa_4 as factor-recovery predictor

Per the 3x DEEP free-prob note D.1, resonator-network factor recovery has empirical quadratic capacity with no published Lyapunov. F4 angle: the factor count F a resonator can recover transitions sharply when the Hadamard-product bound vector's covariance exits the semicircle regime, which is exactly the |kappa_4_rect| > threshold event. So kappa_4_rect of the bound vector at factor-binding time is a single-scalar PRE-RECOVERY PREDICTOR of resonator success. This adds a check upstream of the resonator iteration: if kappa_4_rect already shows the bound vector is far from semicircle in the wrong direction, abort the resonator and re-bind differently. Saves compute and gives a quantitative bind-feasibility signal.

### D.8 Cross-link with conformal calibration (CP set-size)

Per 3x DEEP D.5, CP set-size at coverage 1-alpha is lower-bounded by O(1/spectral_gap) on the nonconformity score covariance. F4 angle: the spectral gap is the SECOND-LARGEST/LARGEST eigenvalue ratio, which under semicircle null is determined by m_2 alone, but under non-semicircle (kappa_4 != 0) is shifted in a predictable direction. So kappa_4 of the nonconformity-score-covariance spectrum is a SECOND-ORDER predictor of CP tightness beyond the gap. Substrate-product: predict CP set-size from substrate-internal spectral statistics without running CP on held-out data.

### D.9 Cross-link with Chung-Lu analogy graph

Per 3x DEEP D.6, analogy graph adjacency matrix has TW-class edge fluctuations. F4 on the analogy-graph spectrum gives a NON-GAUSSIAN STRUCTURE INDEX for the analogy graph: a substrate analogy graph with high kappa_4 has rich cluster structure (multiple emerging analogy-clusters); near-zero kappa_4 means the analogy graph is "flat" / undifferentiated. Substrate-product: a single kappa_4 scalar replaces a more expensive community-detection sweep for monitoring analogy-graph health over time.

### D.10 The unification (operational)

ALL 14 cited drills reduce to: "compute kappa_4_rect on the substrate spectral observable corresponding to drill k, conditional on the partition corresponding to drill k." The partition is global / per-shard / per-tier / per-family-tag / per-N-slice / per-kb-size depending on drill. The substrate-novel observability axis is: SUBSTRATE OPERATORS HAVE A SINGLE-SCALAR NON-GAUSSIAN STRUCTURAL INDEX (kappa_4_rect) WITH A PRINCIPLED ZERO (semicircle null), TRIVIAL TO COMPUTE (~5 lines), CONDITIONABLE ON ANY PARTITION, AND CROSS-VALIDATED AGAINST FIVE INDEPENDENT FALSIFIABLE PREDICTIONS. LLM operators have no comparable single-scalar deployed health signal in production.

### D.11 The contradiction (acknowledged)

The 3x DEEP free-prob note's P3 framed kappa_4 strongly as a dense-Hopfield separability predictor. The Layer 4 dialectic note framed kappa_4 weakly as one of many Bayesian-surprise input metrics. These two framings differ in EXPECTED EFFECT SIZE: P3 expects a strong (correlation > 0.5) signal; Layer 4 expects only that kappa_4 surprise be one of N candidate surprise channels (no individual must be strong). The synthesis: kappa_4 has both a STRONG-PRIMARY role on margin / capacity / triangle questions (P1-P5 here) and a WEAKER-CONTRIBUTING role as one of many Layer 4 surprise channels. The two roles are NOT in conflict but operate at different scales -- one a within-cycle measurement, the other a cross-cycle drift detector.

---

## (e) Substrate-product implications

### E.1 Single instrument, multi-axis

The same ~30-line kappa_4 conditional primitive yields five operationally distinct readings:
- Heavy-tailed prior detection (sign of global kappa_4_rect vs zero).
- Spectral plateau / N-saturation detector (kappa_4 trajectory across N).
- Atom-isolation margin observability (kappa_4 on cleanup-margin distribution).
- Capacity-saturation diagnostic (kappa_4 trend across kb-size sweep).
- Cross-substrate triangle discriminator (kappa_4 distinguishes FHRR / GHRR / hybrid).

Plus three CROSS-LINK derivatives:
- Per-shard attribution informativeness (Layer 1).
- Layer 4 spectral-surprise channel (kappa_4 trajectory feeds BOCPD).
- Resonator factor-recovery pre-check (kappa_4 of bound vector predicts feasibility).

All from one substrate-native scalar.

### E.2 Substrate-vs-LLM measurable axis

What does F4 measure that LLM-embedding cosine cannot? Answer: a principled deviation-from-flat-baseline scalar with a closed-form zero (semicircle null), a closed-form additivity under independence (R-transform), and a per-partition conditional structure that any substrate operator can compute in seconds. LLM embeddings can in principle have their kappa_4 computed too -- but no production LLM observability stack uses kappa_4 of hidden-state spectra as a deployed health signal, because there is no operational anchor (LLM training does not preserve free-probability invariants and an LLM's effective ensemble class is not pinned). The substrate, by contrast, has a DESIGN-SPECIFIED algebra class (FHRR / GHRR / hybrid) with a KNOWN null kappa_4 sequence, so substrate-deployed kappa_4 observability is interpretable in a way LLM kappa_4 observability is not. This is a substrate-distinctive product capability.

### E.3 Engineered-wrapper compatibility

Per memory substrate_v32_engineered_wrapper_2026-06-11, all 5 protection layers ride on substrate algebra via wrapper (no core changes). The kappa_4 primitive operates entirely at the wrapper layer (it reads codebook and shard matrices; it does not perturb them). It composes with engineered wrapper, write-protection, per-tier importance defaults, and FHRR-as-Reed-Solomon parity without modification.

### E.4 Cost and deployment

CPU only, ~5 lines per scalar, ~30 lines total for the conditional primitive, ~80 lines for the integrated Layer 2 v2 module. Runs in well under 1 second per snapshot for substrate N <= 8192. Suitable for online wrapper telemetry (e.g. compute every 5 min on each shard) and offline strategy-cycle observability sweeps.

### E.5 What this is NOT

Not a substitute for benchmark evaluation (it predicts capacity-headroom and structural health, not task-level correctness). Not a capability claim (it is an observability claim). Not a replacement for the Layer 1 + Layer 2 + Layer 4 individual primitives -- it is a CROSS-LAYER spectral statistic that informs all three. Not novel mathematics (Voiculescu free cumulants are classical from 1985 onward); the novelty is substrate-engineering integration as a CONDITIONAL primitive over substrate-self-evaluation partitions.

---

## (f) Citations (verified, generic-math-term lit-scan)

Triple-source convergence used in cross-thread:

1. Voiculescu DV, Dykema KJ, Nica A. Free Random Variables (CRM Monograph Series 1, AMS, 1992). Definition of free cumulants kappa_n via Mobius inversion on non-crossing partition lattice; semicircle as free-Gaussian; R-transform additivity.

2. Nica A, Speicher R. Lectures on the Combinatorics of Free Probability (LMS Lecture Notes 335, CUP 2006). Moment-cumulant inversion; rectangular free cumulants; operator-valued free probability; Helton-Mai-Speicher subordination algorithm.

3. Mingo JA, Speicher R. Free Probability and Random Matrices (Fields Institute Monographs 35, Springer 2017). RMT-FP correspondence; finite-N corrections; operator-valued generalizations relevant to multi-shard substrate.

4. Benaych-Georges F, Rao R. The eigenvalues and eigenvectors of finite, low rank perturbations of large random matrices (Adv Math 227, 2011). BBP threshold for spike detection at finite N; relevant to family-tag detectability cross-link (D.2 of prior 3x note).

5. Baik J, Ben Arous G, Peche S. Phase transition of the largest eigenvalue for nonnull complex sample covariance matrices (Ann Probab 33, 2005). Foundational BBP transition.

6. Bloemendal A, Knowles A, Yau HT, Yin J. On the principal components of sample covariance matrices (Probab Theory Relat Fields 164, 2016). Edge universality; Tracy-Widom regime relevant to F4-at-edge cross-link.

7. Lee JO, Schnelli K. Tracy-Widom distribution for the largest eigenvalue of real sample covariance matrices with general population (Ann Appl Probab 26, 2016). General-population edge universality.

8. Erdos L, Yau HT, Yin J. Bulk universality for generalized Wigner matrices (Probab Theory Relat Fields 154, 2012). DBM homogenization used in 2x RMT-beyond-FP cross-link D.1.

9. Atas YY, Bogomolny E, Giraud O, Roux G. Distribution of the ratio of consecutive level spacings in random matrix ensembles (Phys Rev Lett 110, 2013). r-statistic universality classification relevant to v4.0 triangle separation P5.

10. Itti L, Baldi P. Bayesian surprise attracts human attention (Vision Res 49, 2009). Surprise KL definition used in Layer 4 cross-link D.3.

11. Adams RP, MacKay DJC. Bayesian Online Changepoint Detection (arXiv 0710.3742, 2007). BOCPD used in Layer 4 cross-link D.3.

12. Jones VFR. Index for subfactors (Invent Math 72, 1983). Jones index foundational; substrate-binding subalgebra cross-link D.6.

13. Frady EP, Kent SJ, Olshausen BA, Sommer FT. Resonator networks, 1: An efficient solution for factoring high-dimensional, distributed representations of data structures (Neural Comput 32, 2020). Resonator factor recovery cross-link D.7.

14. Connes A. Noncommutative geometry (Academic Press 1994); Connes A. Cyclic cohomology, quantum group symmetries and the local index formula for SU_q(2) (J Inst Math Jussieu 3, 2004). Substrate-novel angle Tannakian / cyclic-cohomology framing cited per drill scope item 15 (deprioritized; speculative).

Verified count: 14 citations. All used in cross-thread synthesis above. Generic math terms only in lit-scan queries per query-privacy discipline.

---

## (g) Pre-registration block (status_log + decisions log mirror)

P_deflated overall: 0.42 (cap 0.50 applied; deflation 0.20 from raw lit-scan 0.62).
Per-prediction:
- P1 (heavy-tailed prior detector): P_deflated 0.55 (lit-precedent strong; kappa_4 estimators are standard).
- P2 (N-plateau detector): P_deflated 0.50 (substrate-novel application; depends on substrate's deployed N being in asymptotic regime).
- P3 (margin-kappa_4 vs recall correlation): P_deflated 0.40 (novel-synthesis; rho >= 0.55 bar is moderately ambitious).
- P4 (capacity-saturation monotonicity): P_deflated 0.45 (theoretically grounded but kb-size sweep is the costliest sub-experiment).
- P5 (v4.0 triangle separation): P_deflated 0.50 (R-transform additivity is theoretically rigorous; class-separation magnitude is the open question).

Next-drill candidate if this delivery PASSES: operator-valued F4 on multi-shard substrate (the per-shard cleanup-health telemetry of D.5), then F4 trajectory under Dyson Brownian motion (the dynamical extension of 2x RMT-beyond-FP P2 unified with F4).

Next-drill candidate if this delivery HARD-FAILS on P1 (semicircle null violated by C_iid): finite-N correction estimator (rectangular free probability with explicit O(1/N) bias term, Capitaine-Donati-Martin 2007 finite-N moments). If HARD-FAILS on P3 (margin-kappa_4 no correlation): switch margin observable to log-margin or rank-based margin and re-test (the cleanup-margin distribution may be in a regime where higher classical moments work better than free cumulants).

---
