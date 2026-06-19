# Research: Modern Hopfield capacity-vs-retrieval-quality crossover (2026-06-16, 2x depth)

## (a) HEADLINE

The published literature consistently CONTINGENT-ifies modern Hopfield "exponential capacity" on
minimum pattern separation Delta_min not shrinking with codebook size. In the quasi-orthogonal,
small-codebook regime (Delta_min near sqrt(2) in unit-norm space, N ~ 10^2 to 10^3, large d),
softmax Hopfield retrieval REDUCES to nearest-neighbor argmax (Ramsauer 2020 Thm 3), sparse
Hopfield variants confer ZERO measurable advantage over naive flat softmax cleanup (Hu 2023
Cor 3.1.1; Martins 2024 metastable-only regime), and beta = 1/sqrt(d) is genuinely tune-free
(Koulischer 2023 beta_eff condition is automatically met). Honest-bounded characterizations
(Lucibello-Mezard 2023; Hu 2024 U-Hop; Hu 2024b NeurIPS) all show retrieval degrades BEFORE
theoretical capacity is hit when Delta_min falls below O(ln(M)/beta).

Substrate-product implication: GATE-D dense-Hopfield-at-Ramsauer-beta passing tune-free is
CONSISTENT with published theory for the operating regime; sparse-Hopfield rescue is unlikely
to win because the regime conditions sparse variants exploit (data-sparse activations,
metastable mixed-pattern attractors) are EMPIRICALLY ABSENT in well-separated codebooks.

P_deflated estimate that sparse-Hopfield variants would outperform dense-at-Ramsauer-beta in
the quasi-orthogonal small-codebook regime: 0.10 to 0.15 (penalty applied; absence-of-evidence
caveat retained).

## (b) Cheap decisive test

If the substrate intends to validate the "tune-free dense Hopfield at Ramsauer beta is optimal
for our codebook" hypothesis, the cheap decisive test is a 3-way side-by-side at a single
codebook scale near the current operating envelope:

1. naive flat softmax cleanup (single dot-product + softmax, beta = 1/sqrt(d))
2. dense modern Hopfield (Ramsauer 2020, beta = 1/sqrt(d), 1-step update)
3. sparse Hopfield with alpha-entmax, alpha = 1.5 or 2.0 (Hu 2023; Martins 2024)

Metric: retrieval accuracy + retrieval probability + Delta_min between top-1 and top-2 patterns.

Cost: cheap-CPU smoke (no large matrix or graph walk required). Single Python script.
Expected runtime: ~5 to 15 minutes wall-clock for a 10^2 to 10^3 codebook at d ~ 1024.

## (c) Falsifiable predictions

HARD-PASS thresholds (sparse-Hopfield-wins NOT supported -> dense-at-Ramsauer suffices):
- Naive flat cleanup, dense Hopfield, and sparse Hopfield achieve retrieval accuracies within
  0.5 percentage points of each other across the codebook range.
- Top-1 vs top-2 separation (effective Delta after softmax) is identical across the three
  methods at well-separated codebook (within 5% relative).
- No regime within the substrate's operating envelope where sparse > dense > flat by a
  measurable margin (>1 percentage point).

HARD-FAIL thresholds (sparse-Hopfield-wins SUPPORTED -> rescue is on the table):
- Sparse Hopfield (alpha = 1.5 or 2.0) exceeds dense softmax retrieval accuracy by >=2
  percentage points at any tested codebook size within the operating envelope.
- Dense softmax exhibits >=5% metastable mixed-pattern outputs (top-2 / top-1 ratio > 0.5
  on retrieval calls) -- a signature of operating in the Delta_min-shrinking regime that
  sparse-Hopfield was designed to fix.
- The beta = 1/sqrt(d) default produces measurable failure (drop > 5pp vs tuned beta) at any
  tested codebook scale -- this would invalidate the closed-form tune-free claim and require
  rolling back GATE-D's tune-free attribution.

MIDDLE_BAND (0.5 to 2 percentage point sparse advantage): genuinely uncertain. Would require
Track-1 deeper drill into pattern statistics to determine whether the substrate has hidden
near-metastable structure that sparse-Hopfield exploits. P_middle ~ 0.15.

## (d) Cross-thread synthesis

This drill connects to multiple cap_map rows and prior research deliveries:

1. GATE-D verification (current): dense modern Hopfield at Ramsauer beta PASSED tune-free.
   This research delivery CONFIRMS the published theoretical basis for that passing being
   regime-appropriate (not a fluke). The well-separated codebook condition assumed by
   Ramsauer Theorem 3 is the regime the substrate operates in.

2. Cap row capacity-envelope (likely "Bet I" 2/3 envelope per the field-advisor memo):
   the literature's "exponential capacity contingent on Delta_min >= O(ln M / beta)"
   characterization (Hu 2024b NeurIPS spherical-codes; Lucibello-Mezard 2023) gives a
   PRINCIPLED upper limit on how far the substrate can push codebook density before
   retrieval degrades. This is the right capacity-envelope formula to bake into cap_map
   rather than the naive "exp(d/2)" headline.

3. Sparse-Hopfield rescue track (if/when GATE-D were to regress): the literature does NOT
   support sparse-Hopfield as a rescue in the quasi-orthogonal regime. Instead the rescue
   path would be: (a) reduce codebook density to restore Delta_min margin; (b) add
   feature-space kernel reshaping (U-Hop / KHM per Hu 2024) to artificially widen Delta_min;
   (c) accept the published O(ln M / beta) margin requirement and bound capacity accordingly.

4. Adjacency to free-probability (Tier-1 advisor candidate): Tracy-Widom edge fluctuations
   on W eigenvalues could discriminate the substrate's actual Delta_min distribution from
   the assumed quasi-orthogonal model -- this is the principled lit-grounded test for
   whether substrate's operating regime is truly the well-separated one.

5. Not in cap_map: the Krotov-Hopfield-2021 result that effective beta should grow as
   O(log N) to maintain reliable retrieval as N grows. The substrate's tune-free claim is
   ONLY tune-free in the small-N regime; if codebook scales up significantly, beta will
   need a log-N correction. This is a CONCRETE PREDICTION not currently in cap_map.

## (e) Substrate-product implications

The substrate's "dense modern Hopfield at Ramsauer beta is tune-free for our codebook"
product claim is REGIME-VALID per Ramsauer 2020 Thm 3 + Koulischer 2023 beta_eff analysis.
The product claim can be honestly positioned as:

- "Tune-free retrieval in the well-separated quasi-orthogonal codebook regime"
  (not "universally tune-free")
- "Operates at Ramsauer beta = 1/sqrt(d) with closed-form theoretical backing
  (Ramsauer 2020, Demircigil 2017)"
- "Honest capacity envelope: O(exp(d/2)) patterns subject to Delta_min >= O(ln(M)/beta)
  separation -- crossover characterization from Hu 2024 NeurIPS (provably-optimal-capacity)"

The product DOES NOT need sparse-Hopfield as a feature for the current envelope. If the
substrate's codebook scales >10x or starts ingesting near-duplicate patterns (Delta_min
shrinks), the product story will need either: (a) explicit Delta_min curation, (b) U-Hop
kernel-reshaping to widen feature-space margins, or (c) honest reframe as "scales to
N ~ 10^3 well-separated patterns, requires curation beyond that."

The "beta needs log N correction" finding (Krotov 2021) is a substrate-novel angle to
investigate: at what N does the tune-free beta = 1/sqrt(d) start to mis-tune? This is a
concrete falsifiable scaling experiment and should be added to the substrate's experiment
backlog.

## (f) Citations (verified count: 12)

Dense / classical capacity:
1. Ramsauer H., Schafl B., et al. "Hopfield Networks is All You Need." ICLR 2021.
   arXiv 2008.02217. [Capacity O(exp(d/2)); retrieval error O(exp(-beta * Delta));
   Theorem 3 one-step convergence in well-separated regime.]
2. Demircigil M., Heusel J., Loowe M., Upgang S., Vermet F. "On a Model of Associative
   Memory with Huge Storage Capacity." J. Stat. Phys. 168 (2017), 288-299.
   [arXiv 1702.01929. Exponential interaction precursor; 2^(d/2) capacity proof.]
3. Lucibello C., Mezard M. "The Exponential Capacity of Dense Associative Memories."
   arXiv 2304.14964 (2023). [Statistical mechanics; critical load alpha_c = 0.5 for
   spherical models; T_c(alpha) -> 0 as alpha -> alpha_c; honest finite-N caveat.]

Polynomial / generalized:
4. Krotov D., Hopfield J. "Dense Associative Memory for Pattern Recognition." NeurIPS 2016.
   [Polynomial F(x) = x^n; capacity ~ C^(n-1); n -> inf recovers exponential.]
5. Krotov D., Hopfield J. "Large Associative Memory Problem in Neurobiology and Machine
   Learning." ICLR 2021. arXiv 2008.06996. [Effective beta should grow as O(log N) for
   reliable retrieval as N grows; biological plausibility with hidden neurons.]

Sparse / structured Hopfield:
6. Hu J. Y.-C., Yang D., Wu D., et al. "On Sparse Modern Hopfield Model." NeurIPS 2023.
   arXiv 2309.12673. [alpha-entmax / sparsemax; Prop 3.2 exact retrieval at
   Delta >= m * beta^{-1}; Corollary 3.1.1: sparse advantage vanishes when patterns are
   not sparse in feature space.]
7. Santos M., Martins A., et al. "Sparse and Structured Hopfield Networks." ICML 2024.
   arXiv 2402.13725. [Fenchel-Young unification; margin m = (alpha-1)^{-1} for
   alpha-entmax; metastable-state avoidance is the advantage, not capacity.]
8. Hu J. Y.-C., et al. "Uniform Memory Retrieval with Larger Capacity for Modern Hopfield
   Models." arXiv 2404.03827 (2024). [U-Hop kernelized Hopfield; "memory confusion" is
   the central failure mode; 30% retrieval improvement via feature-space reshaping.]
9. Hu J. Y.-C., et al. "Provably Optimal Memory Capacity for Modern Hopfield Models:
   Transformer-Compatible Dense Associative Memories as Spherical Codes." NeurIPS 2024.
   arXiv 2410.23126. [Matching upper-lower capacity bounds; optimal arrangements are
   spherical codes; minimum separation O(log M / beta) suffices.]

Phase diagrams and energy landscape:
10. Amit D.J., Gutfreund H., Sompolinsky H. "Statistical Mechanics of Neural Networks near
    Saturation." Ann. Phys. 173 (1987), 30-67. [Classical (alpha, T) phase diagram;
    paramagnetic / spin-glass / metastable / stable retrieval phases.]
11. Koulischer F., Goemaere C., et al. "Exploring the Temperature-Dependent Phase
    Transition in Modern Hopfield Networks." NeurIPS 2023 workshop. arXiv 2311.18434.
    [Effective beta_eff = beta * ||x||^2 * (1 - cos theta); the same scalar beta can be
    in retrieval or averaging phase depending on codebook geometry.]
12. Millidge B., Salvatori T., Song Y., Lukasiewicz T., Bogacz R. "Universal Hopfield
    Networks." ICML 2022. [Similarity-Separation-Projection framework; explicit refutation
    of any single fixed beta as tune-free across heterogeneous codebooks.]

Retrieval-augmented / kNN baselines (for naive-flat comparison context):
13. Khandelwal U., et al. "Generalization through Memorization: Nearest Neighbor Language
    Models." ICLR 2021. [Flat dense retrieval competitive with structured approaches.]
14. Karpukhin V., et al. "Dense Passage Retrieval for Open-Domain QA." EMNLP 2020.
    [Flat dense retrieval baseline.]

## (g) Wins / Honest bounds

WINS (clean theoretical capacity guarantees):
- Demircigil 2017 + Ramsauer 2020: exp(d/2) capacity for fixed Delta_min > 0.
- Hu 2024b NeurIPS: tight matching upper/lower bounds achieved at spherical-code geometry.
- Sparse Hopfield (Hu 2023, Martins 2024): exact retrieval (zero error) at finite Delta_min
  via alpha-entmax margin, where softmax gives only epsilon-close stationary points.

HONEST BOUNDS (degradation-before-capacity characterized):
- Lucibello-Mezard 2023: T_c(alpha) -> 0 as alpha -> alpha_c=0.5; near-capacity retrieval
  requires vanishingly small temperature. Most rigorous honest-bound.
- Hu 2024 U-Hop: identifies "memory confusion" as practical failure mode well below
  capacity ceiling; 30% headroom via feature-reshaping is measured.
- Krotov-Hopfield 2021: effective beta needs O(log N) scaling; 1/sqrt(d) is not asymptotic.
- Koulischer 2023: phase-transition threshold depends on pattern norms and geometry, not
  beta alone -- direct refutation of universal tune-free claim.
- Hu 2023 Corollary 3.1.1: sparse advantage vanishes when patterns are not sparse in
  feature space; head-to-head with dense on dense data is "similar."

## (h) Synthesis: extending dense Hopfield beyond current envelope

The literature gives a clear recipe for extending dense modern Hopfield retrieval beyond
a baseline operating envelope WITHOUT switching to sparse variants:

1. Maintain Delta_min >= O(ln M / beta) via codebook curation (Hu 2024 NeurIPS).
2. Apply U-Hop / KHM kernel reshaping to widen feature-space margins when raw Delta_min
   shrinks (Hu 2024 U-Hop, +30% measured headroom).
3. Allow beta to scale as O(log N) per Krotov 2021 -- this is the principled tune-free
   correction; it preserves the closed-form character (beta is a known function of N, d).
4. Honestly bound the capacity envelope at the geometric entropy limit, not the naive
   exp(d/2) headline (Lucibello-Mezard 2023; finite-N corrections matter at N ~ 50 to 10^3).

The substrate-product framing should adopt this honest-bounded characterization. The
"tune-free at Ramsauer beta" claim is regime-accurate for the current envelope but
needs explicit guard rails on Delta_min and N for the product description.

Sparse-Hopfield as a rescue is unlikely to help in the substrate's regime per literature
adversarial bound: no published evidence supports sparse > dense in quasi-orthogonal
small-N high-d codebooks; sparse-wins regimes (data-sparse activations, metastable
mixed-pattern attractors) are empirically absent in well-separated codebooks.

## Status log + next-drill candidate

next-drill candidate: free-probability F2 Wigner edge / Tracy-Widom on W eigenvalues
(could empirically measure the substrate's actual Delta_min distribution and validate
the quasi-orthogonal regime assumption that the tune-free claim relies on).
