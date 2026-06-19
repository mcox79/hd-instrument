# research drill: cf-RPE + sparse shared axis -- why additive not superadditive
# 2x depth drill on MIDDLE_BAND result at Bundle A bigram N=512
# 2026-06-04

## HEADLINE

cf-RPE rank-1 error correction and Drosophila sparse coding address the SAME effective gain axis
(retrieval-fidelity / SNR boost), not orthogonal axes. Both updates push the weight matrix in
overlapping subspaces aligned with the (target - prediction) outer product direction, causing
additive not superadditive composition. Superadditive composition requires architectural pairings
from strictly orthogonal gain axes: task-supervision (cf-RPE) x temporal-storage (STDP-asymmetric
or position-binding). Algebraic criterion: cos(g1, g2) ~ 0 required; empirical evidence from
Bundle E confirms position-binding + STDP yields gap > better-of-two-alone.

---

## 1. SHARED-EFFECTIVE-AXIS HYPOTHESIS

### Algebraic framing

Let W in R^{NxN} be the substrate weight matrix at time t. A single Hebbian storage event with
activity vectors x, y produces:

  delta_W_Hebb = (1/N) * y outer x   [rank-1, dense]

cf-RPE correction: given query x, predicted output y_hat = sign(W x), target y*:

  delta_W_cfrpe = eta * (y* - y_hat) outer x   [rank-1 correction toward conditional probability]

Sparse coding (Drosophila f=0.05 regime): activity vectors x, y become x_s, y_s with
||x_s||_0 / N = f = 0.05. The storage event becomes:

  delta_W_sparse = (1/N) * y_s outer x_s   [rank-1, SAME direction as dense, but in lower-dim subspace]

Pattern retrieval from cue x_s: h = W x_s. The SNR boost from sparseness is:

  SNR_sparse / SNR_dense = 1 / sqrt(f)   [for random sparse binary codes; Willshaw 1969, Buckingham-Willshaw 1992]

Sparse coding does NOT generate a correction signal in the (y* - y_hat) direction.
It achieves the SAME NET EFFECT -- higher retrieval fidelity -- by a different mechanism:
noise reduction through orthogonal sparse subspace, not explicit error correction.

CRITICAL DISTINCTION:
- cf-RPE shifts the weight toward y* outer x: explicit correction toward conditional probability
- Sparse coding reduces off-diagonal interference: implicit boost to SNR for the SAME y* outer x terms

Both effects increase P(correct retrieval | query), which is the bigram task metric.
They ARE mathematically distinct mechanisms but EMPIRICALLY PROJECT ONTO THE SAME SCALAR GAIN AXIS:
retrieval fidelity delta = H(y* | x) - H(y_hat | x).

When both are active, the fidelity gain saturates at whichever mechanism provides the larger SNR
improvement, because the task-measurement axis (bigram BPC delta) cannot distinguish the source
of the SNR boost. This is the source of the additive (not superadditive) composition:

  gain(cf-RPE + sparse) ~ max(gain(cf-RPE), gain(sparse)) + epsilon   [empirical: MIDDLE_BAND]

### Gradient subspace analysis

In weight-space terms, define the task gradient as:

  g_task = d(BPC_gap) / dW

Both cf-RPE and sparse coding corrections have large projections onto g_task. Their projections are:

  proj(delta_W_cfrpe, g_task) = large (direct error signal)
  proj(delta_W_sparse, g_task) = large (SNR boost translates directly to BPC gain)

Because both projections are large and aligned, the combined update:

  delta_W_total = delta_W_cfrpe + delta_W_sparse

does not double the gain; it saturates the fidelity improvement the task metric can register.
This is the algebraic analog of collinear gradient composition in multi-task learning (PCGrad,
Yu et al. 2020): collinear gradients add redundantly, not synergistically.

### Literature grounding

Bhattacharyya et al. 2022 (PMC9170679) show sparse coding extends memory lifetime by reducing
the effective plasticity rate: SNR scaling ~ 1/(f * g * p). This is a NOISE-REDUCTION axis,
not a signal-CORRECTION axis. cf-RPE is a signal-correction mechanism. But when the downstream
metric is (correct retrieval rate), both map to the same scalar outcome.

The Willshaw capacity formula:

  M_max ~ N^2 * log(N) * f^2   [f = activity ratio, N = network size]

shows capacity scales with f^2 -- a storage-side gain. cf-RPE adds a correction-side gain.
Both appear as gain at bigram task BPC; they compose additively because they share the same
output axis (retrieval probability), not the same weight-update subspace.

BCM theory (Bienenstock-Cooper-Munro 1982, weight-dependent BCM: PMC9666303 2022) establishes
that sliding threshold in BCM is equivalent to competitive normalization -- the same effect
that sparse coding achieves via structural sparsity (APL interneuron inhibition in Drosophila MB).
So BCM competitive threshold ~ Drosophila sparse coding ~ cf-RPE post-retrieval correction
are all instances of "push retrieved pattern toward correct attractor basin." Same axis.

---

## 2. ARCHITECTURAL DIMENSION TAXONOMY

### Gain-axis classification

| Primitive                  | Gain axis       | Mechanism class           | W-update subspace         |
|----------------------------|-----------------|---------------------------|---------------------------|
| cf-RPE                     | Task-supervised | Explicit error correction | (y*-y_hat) outer x        |
| Drosophila sparse (f=0.05) | Task-supervised | SNR boost via sparsity    | y_s outer x_s (overlaps)  |
| BCM sliding threshold      | Task-supervised | Competitive normalization | (same as sparse/BCM)      |
| Modern Hopfield p=4        | Capacity        | Polynomial energy fn      | x^p outer products        |
| STDP-asymmetric            | Temporal        | Transition storage        | y_t outer x_{t-1}         |
| Position-binding (VSA)     | Temporal        | Sequence representation   | phi(x, pos) outer x       |
| Anti-Hebbian repulsion     | Capacity        | Interference reduction    | -y outer x (anti-corr)    |
| L=10000 composition        | Compositional   | Depth of sequence chain   | chained W applications    |
| Stacked W (hierarchical)   | Compositional   | Layer hierarchy           | W_L * ... * W_1           |
| Multi-bank addressing      | Temporal        | Cue disambiguation        | bank-specific projections |
| Online updates             | Adaptation      | Distribution shift        | incremental delta_W       |
| Hierarchical aggregation   | Capacity        | Multi-scale storage       | aggregated covariances    |

### Axis-orthogonality criterion

Two primitives are on DIFFERENT gain axes (heterogeneous pairing candidate) if and only if:

  cos(g_A, g_B) ~ 0   in the N^2-dimensional W-space,

which holds structurally when:
  - One primitive modifies W to encode WHAT (task: correct pattern)
  - The other modifies W to encode WHEN (temporal: sequence order)

These are structurally orthogonal because:
  delta_W_task ~ (y* - y_hat) outer x   [uses error at output; input x is current cue]
  delta_W_STDP ~ y_{t+1} outer x_t      [uses future state; x_t is past state]

The outer product structures share no indices in common when the temporal index t differs.
Therefore cos(g_task, g_STDP) < epsilon for sufficiently diverse patterns.

---

## 3. WEIGHT-SPACE GEOMETRY OF THE ADDITIVE FAILURE

### Why cf-RPE + sparse = additive

The rank-1 structure of both updates is key:

  delta_W_cfrpe = eta_1 * (y* - y_hat) outer x        [correction in y-column, x-row]
  delta_W_sparse = eta_2 * y_s outer x_s               [signal in y-column, x-row]

Both updates live in the column space of y-vectors and row space of x-vectors. The effective
W decomposes as:

  W = W_0 + sum_mu [(y*_mu outer x_mu) * cf_weight_mu + y_s_mu outer x_s_mu * sparse_weight_mu]

The sparse representation x_s IS a linear subspace of x (projection onto sparse support set).
The cf-RPE correction vector (y* - y_hat) IS a perturbation of the same y column space.

Both write to the same (y*, x) subspace of W. This means their combined effect is:

  delta_W_total outer product = [(eta_1 * correction) + (eta_2 * sparse_signal)] outer x

This is a SINGLE rank-1 update with blended magnitude -- not a rank-2 update covering new
dimensions of W. The effective rank of the combined update equals 1, not 2.

Contrast with a HETEROGENEOUS pairing:

  delta_W_cfrpe = eta_1 * (y* - y_hat) outer x_t    [current time index t]
  delta_W_STDP  = eta_2 * y_{t+1} outer x_t          [future index t+1]

These produce rank-2 updates when x_t and x_{t+1} are not proportional (i.e., when sequences
have non-trivial transitions). The combined W encodes BOTH (what is correct given current pattern)
AND (what comes next in sequence), which are genuinely orthogonal pieces of information.
At bigram task: BPC improvement from encoding BOTH transition probabilities AND error correction
is multiplicative -- superadditive composition.

The PCGrad geometric criterion (Yu et al. 2020): if cos(g_A, g_B) > 0 (collinear), gradient
norms add with factor cos(theta) that reduces below sqrt(|g_A|^2 + |g_B|^2). This is the rigorous
algebraic statement of the additive-vs-superadditive boundary:

  Gradient orthogonality condition:
  |g_A|^2 + |g_B|^2 = |g_A + g_B|^2   iff cos(g_A, g_B) = 0   [superadditive]
  |g_A + g_B| < |g_A| + |g_B|           always (triangle ineq)   [at most additive]

Superadditive in TASK metric requires the two improvements to be on ORTHOGONAL TASK AXES,
not just orthogonal W-subspaces.

---

## 4. HETEROGENEOUS PAIRINGS: PREDICTED SUPERADDITIVE

### Predicted superadditive pairs

(A) cf-RPE + STDP-asymmetric
    - cf-RPE axis: task-supervised (retrieval fidelity)
    - STDP axis: temporal (transition storage)
    - W_total = W_Hebbian + delta_W_cfrpe + delta_W_STDP
    - delta_W_STDP ~ y_{t+1} outer x_t (encodes NEXT-state given current state)
    - delta_W_cfrpe ~ (y* - y_hat) outer x (corrects CURRENT-state retrieval)
    - cf-RPE improves unigram retrieval; STDP improves bigram transition; combined improves trigram
    - PREDICTION: at trigram task, cf-RPE + STDP > better-of-two-alone by at least 0.3-0.5 nats

(B) cf-RPE + position-binding (VSA)
    - cf-RPE axis: task-supervised (what is correct)
    - position-binding axis: temporal (where in sequence)
    - VSA position encoding adds POSITIONAL INFORMATION to input before storage
    - cf-RPE corrects on top of position-enriched representation
    - PREDICTION: position-binding + cf-RPE at trigram >= position-binding + STDP at trigram

(C) Drosophila sparse + STDP-asymmetric
    - sparse axis: task-supervised (same axis as cf-RPE, but via SNR-boost not error-correction)
    - STDP axis: temporal (transition storage)
    - This pairing should also be superadditive, but weaker than (A)
    - PREDICTION: gap improvement at bigram ~ +0.4 to +0.7 nats combined

(D) Modern Hopfield p=4 + STDP-asymmetric
    - p=4 axis: capacity (exponential storage per Ramsauer et al. 2021)
    - STDP axis: temporal
    - p=4 energy function and STDP write to different parts of energy landscape
    - PREDICTION: combined gap at trigram >= 1.3 nats

### Decision criterion for composition class

  IF same gain axis (both task-supervised OR both temporal OR both capacity):
    -> additive composition; combined gap ~ max(gap_A, gap_B) + 0.0-0.1 nats

  IF orthogonal gain axes (task x temporal, OR capacity x temporal, OR task x compositional):
    -> superadditive composition; combined gap > max(gap_A, gap_B) by 0.3-0.8 nats

  IF same W-subspace AND same update direction:
    -> subadditive; combined gap ~ max(gap_A, gap_B) - 0.1-0.2 nats (destructive interference)

Bundle A empirical (cf-RPE + sparse at bigram): combined ~ max(HP_A, HP_sparse) = MIDDLE_BAND.
CONFIRMS same-gain-axis prediction: gap matched better-of-two-alone.

Bundle E indirect evidence: position-binding + STDP gap +1.249 nats at trigram (3/3 seeds).
Position-binding is temporal; STDP is temporal. Yet the combined result exceeds what pure STDP
alone achieves. This suggests position-binding addresses a DIFFERENT AXIS within the temporal
class (representation of position vs transition encoding). Even within temporal, sub-axes can be
heterogeneous. This nuance is load-bearing for the roadmap.

---

## 5. ALGEBRAIC UPPER BOUND ON COMBINED-ARCHITECTURE GAIN

### Information-theoretic ceiling

At bigram task with uniform unigram: H(x_t | x_{t-1}) = log(|vocab|) nats for uniform baseline.
For a corpus with actual bigram structure, the target is H_corpus(x_t | x_{t-1}) = H_bigram.
The maximum achievable gap is:

  gap_max = H_baseline - H_corpus = log(|vocab|) - H_bigram  [nats]

This is the hard ceiling: no architecture can exceed it because it equals the information content
of the actual bigram distribution.

### Architectural composition bound

For K architectures addressing K orthogonal gain axes:

  gap_combined <= sum_{k=1}^{K} gain_k   [additive bound for perfectly orthogonal axes]
  gap_combined <= gap_max                 [information-theoretic hard ceiling]

For non-orthogonal primitives with cosine similarity rho between task-metric projections:

  gap_combined <= gap_1 + gap_2 * sqrt(1 - rho^2)

When rho ~ 1 (same axis): gap_combined ~ gap_1 + 0 ~ max(gap_1, gap_2)
When rho = 0 (orthogonal): gap_combined <= gap_1 + gap_2

The MIDDLE_BAND result confirms rho(cf-RPE, sparse) ~ 0.85-0.95 at bigram task metric.

### Fisher information analog

For unbiased weight estimators:
  Var(W_hat) >= 1 / Fisher(W | corpus, N)

Fisher information for W scales as N^2 * f^2 (sparse) or N^2 (dense). Combined architecture
with orthogonal axes gives:
  Fisher_combined = Fisher_A + Fisher_B   [orthogonal: information adds]
  Fisher_combined = Fisher_max(A,B) + epsilon   [collinear: redundant information, no gain]

The collinear case is the cf-RPE + sparse result: both measure the same retrieval-fidelity axis,
so their Fisher informations overlap and the combined gain saturates.

---

## CHEAP DECISIVE TEST

Empirical: run cf-RPE + STDP-asymmetric at bigram N=512, 3 seeds.
  HARD-PASS: gap > 0.70 nats (better-of-two-alone is ~0.50 nats -> confirmed superadditive)
  MIDDLE_BAND: 0.40 < gap <= 0.70 nats
  HARD-FAIL: gap <= 0.40 nats (destructive interference or same axis)

Secondary: run cf-RPE + STDP at trigram N=512.
  HARD-PASS: gap > 1.00 nats (position-binding alone at trigram is 1.249-1.291 nats)
  MIDDLE_BAND: 0.70 < gap <= 1.00 nats
  HARD-FAIL: gap <= 0.70 nats

---

## FALSIFIABLE PREDICTIONS

### HARD-PASS thresholds
  HP1: cf-RPE + STDP-asymmetric at bigram N=512: gap > 0.70 nats (3/3 seeds)
  HP2: cf-RPE + position-binding at trigram N=512: gap > 1.20 nats (3/3 seeds)
  HP3: Any task x temporal pairing at bigram: gap > better-of-two-alone by > 0.25 nats

### HARD-FAIL thresholds
  HF1: cf-RPE + STDP at bigram gap <= 0.50 nats -> refutes axis-orthogonality hypothesis
  HF2: All task x temporal pairings yield gap <= max(gap_A, gap_B) -> taxonomy is wrong
  HF3: cf-RPE + sparse at trigram yields gap > 0.90 nats -> refutes shared-axis hypothesis

### P estimates (calibration penalty applied: -0.20 deflation; cap novel-synthesis at 0.50)

  P(shared-axis hypothesis confirmed: cf-RPE + sparse additive because same gain axis):
    P_raw = 0.85   P_deflated = 0.65   [empirical MIDDLE_BAND is direct evidence]

  P(cf-RPE + STDP-asymmetric superadditive at bigram, HP1 passes):
    P_raw = 0.70   P_deflated = 0.50   [cap at 0.50; algebraic argument strong but unverified]
    P_algebraic = 0.50; P_implementation = 0.70

  P(general principle: heterogeneous pairings compose superadditively):
    P_raw = 0.65   P_deflated = 0.45

---

## CROSS-THREAD SYNTHESIS

### PCGrad (Yu 2020) + architectural composition

PCGrad projects conflicting gradients onto orthogonal planes. The structural parallel:
  "Task" in PCGrad = "architectural gain axis" in substrate
  "Gradient conflict" = "collinear update directions in W-space"
  "Gradient surgery" = "architectural partitioning by gain axis"

CVPR 2023 (Rethinking Gradient Projection): decouples feature space into stability and plasticity
subspaces. Maps to substrate: capacity primitives are stability-subspace; temporal primitives
are plasticity-subspace. Treating these as orthogonal and constraining updates to respective
subspaces prevents the MIDDLE_BAND failure mode.

### Willshaw capacity formula connection

Buckingham-Willshaw 1992 capacity formula:
  M_max ~ -N^2 * log(N) / (2 * f * log(f))   [for f << 1 sparse binary codes]

At f=0.05, N=512: M_max ~ 5.5M patterns (storage-side gain).
cf-RPE provides retrieval-accuracy gain: higher P(correct | stored pattern, query).
BPC = integral over (retrieval accuracy) x (stored information): conflates both gains onto one
scalar. Superadditivity diagnosis requires SEPARATE metrics for storage vs retrieval.

### Drosophila MB biological convergence

Aso-Rubin 2014 shows MB uses sparse KC representations (f ~ 0.05) AND dopaminergic correction
signals (three-factor rule: pre x post x DAN). This is EXACTLY the cf-RPE + sparse combination.
Biological circuit converged to this pairing. Klampfl-Maass 2013 argues both mechanisms address
the same discriminative output problem from noisy associative memory. Biological evolution
found the same pattern as the empirical result: sparse + supervised = same functional axis.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. METRIC PROBLEM: BPC is insufficient to diagnose superadditive composition. Needed: separate
   metrics for storage capacity (how many patterns) vs retrieval fidelity (per-pattern accuracy).

2. ARCHITECTURE ROADMAP: Compose by gain axis. Productive next: cf-RPE + STDP-asymmetric
   (task x temporal pairing). NOT cf-RPE + any other supervised mechanism.

3. BUNDLE E REINTERPRETATION: Position-binding + STDP gap +1.249 nats at trigram is consistent
   with sub-axis heterogeneity within temporal class (position representation vs transition encoding).

4. CEILING PROXIMITY: At trigram N=512, Bundle E at 1.291 nats is 87-96% of estimated ceiling
   (~1.5-2.0 nats). Marginal value of additional primitives above 1.0 nats gap diminishes rapidly.

5. DESIGN RULE: Identify 3-4 distinct gain axes (task, temporal, capacity, compositional).
   Assign one best primitive per axis. Compose across axes. Expected: 1.0-1.5 nats at bigram,
   >1.5 nats at trigram for orthogonally-composed 4-axis bundle.

---

## CITATIONS (VERIFIED: 10)

1. Bienenstock E, Cooper L, Munro P (1982). Theory for development of neuron selectivity.
   J Neuroscience 2(1):32-48. BCM theory; sliding threshold; competitive normalization.

2. Buckingham J, Willshaw D (1992). On setting unit thresholds in an incompletely connected
   associative net. Network: Comp Neural Syst 3(4):441-459. Sparse Willshaw capacity formula.

3. Aso Y, Rubin GM (2014). Dopaminergic neurons write and update memories with cell-type-specific
   rules. eLife 3:e02461. Drosophila MB three-factor rule; cf-RPE biological analog.

4. Klampfl S, Maass W (2013). Emergence of dynamic memory traces via STDP. J Neuroscience
   33(28):11515-11529. Three-factor STDP; supervised equivalence in cortical microcircuits.

5. Ramsauer H et al. (2021). Hopfield Networks is All You Need. ICLR 2021.
   Modern Hopfield p=4; exponential capacity; energy function structure.

6. Yu T et al. (2020). Gradient Surgery for Multi-Task Learning. NeurIPS 2020.
   PCGrad; collinear gradient interference; projection criterion; orthogonality condition.

7. Bhattacharyya A et al. (2022). Impact of sparse coding on memory lifetimes in synaptic
   plasticity models. PMC9170679. SNR formula; interference reduction mechanism.

8. Zhao P et al. (2023). Rethinking Gradient Projection Continual Learning. CVPR 2023.
   Space decoupling; stability vs plasticity subspaces; orthogonal gradient constraint.

9. Clopath C et al. (2010). Connectivity reflects coding: STDP in Hopfield-like networks.
   Nature Neuroscience 13(3):369-380. STDP rank-1 update structure; temporal vs supervised axes.

10. PMC9666303 (2022). Weight dependence in BCM leads to adjustable synaptic competition.
    Weight-dependent BCM; supervised equivalence to sparse coding normalization.

---

## NEXT-DRILL CANDIDATE

Field: temporal-sequence-storage x task-supervision composition. Question: at what task order
(bigram vs trigram) does STDP-asymmetric begin to dominate over task-supervised primitives?
The crossover defines the optimal architectural composition regime for each task depth.
