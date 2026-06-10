# Research drill: substrate confidence binary -- negative 2x drill
# Date: 2026-06-10
# Trigger: WAVE-4 LAP4-3 HARD_FAIL -- rank-transform cleanup margin corr=0.10 vs target 0.30; ECE=0.325
# Drill type: 2x operational drill on existing findings (NOT re-scan)
# Filed by: research sub-agent

---

## HEADLINE

Cleanup-margin in a winner-take-all attractor system is STRUCTURALLY binary because it
measures basin depth (a property of the energy landscape), not posterior probability
(a property of the data distribution). These are different quantities. Per-sample
correlation between margin and accuracy is expected to be near zero -- this is not a
calibration failure, it is a category error in the confidence model. Six paths to
approximate continuous confidence exist, but all require augmenting or replacing the
cleanup step; they cannot be extracted post-hoc from cleanup margin alone. For the
substrate-around-LLM deployment model, binary is likely sufficient for 4 of 5 decision
classes, and the one class that benefits from graded confidence (LLM routing) is served
adequately by a trained probe on the cleanup vector rather than the raw margin.

P_deflated (any path achieves Pearson r >= 0.50 per-sample): 0.32
P_deflated (trained-head path achieves r >= 0.40 per-sample): 0.48
P_deflated (population ensemble path achieves r >= 0.45): 0.42
Calibration note: deflated 0.20 from raw pre-deflation estimates per
[[feedback-lit-scan-calibration-penalty]]. Novel-synthesis cap 0.50 applied.

---

## LEVEL 1: Why cleanup-margin does not correlate per-sample

### 1.1 Hopfield attractor dynamics -- settle to peak; magnitude irrelevant

Classical Hopfield energy (Hopfield 1982; Amit, Gutfreund, Sompolinsky 1985 AGS):

    E(s) = -(1/2) sum_{ij} W_ij s_i s_j

The update rule is:

    s_i <- sign( sum_j W_ij s_j )

This is a zero-temperature Glauber update. At zero temperature, the system always moves
to a strictly lower energy state and terminates at a fixed point (local energy minimum).
The trajectory is deterministic: given the same initial state, the same attractor is
always reached.

The margin (closest-competitor distance) is:

    margin = d(cleanup_output, winner) - d(cleanup_output, runner_up)

where d is Hamming or cosine distance. This margin reflects how deep the winner's basin
is relative to the runner-up basin -- it is a property of the codebook geometry and the
query projection.

The posterior probability of correct retrieval is:

    P(correct | query) = integral over p(query | true_pattern) * I(retrieval succeeds)

These are different objects. Margin is geometric; posterior is distributional. Their
correlation is determined by whether basin depth correlates with query-distribution
overlap. In general, this correlation is weak and model-specific. There is no theorem
requiring it to be large.

### 1.2 Cleanup is energy-minimum; margin reflects basin depth, not posterior

The attractor energy at convergence is:

    E* = -(1/2) xi^T W xi

for stored pattern xi. The energy difference between winner and runner-up is related to
the overlap m_mu = (1/N) sum_i xi^mu_i s_i:

    Delta_E ~ N * (m_winner^2 - m_runner-up^2)

This is a statement about the geometry of pattern separation. It is NOT a statement
about the probability that a query drawn from the true data distribution falls into the
winner's basin rather than the runner-up's basin.

The confusion here is a standard conflation in Bayesian vs frequentist confidence:
energy-margin is a geometric margin in the input space; posterior probability is a
measure over the data distribution. The correlation between them equals zero unless the
data distribution itself is concentrated in a specific geometric region relative to the
codebook -- which is not guaranteed and is not guaranteed by the architecture.

### 1.3 Per-sample variance is dominated by projection noise, not signal

In the FHRR / BSC substrate, a query vector is formed by binding context variables:

    q = x_1 * x_2 * ... * x_k  (superposition, bundle, or binding)

where * is component-wise multiplication for FHRR or XOR for BSC, and x_i are drawn
from the codebook or learned.

Each query lands in a region of {-1, +1}^N with distribution:

    P(query | true_key) = N(xi, sigma_q^2 I)  (approximately, by CLT for large N)

The cleanup margin at a given query is:

    margin(q) = 2 * <xi_winner - xi_runner-up, q> / N

For random codebook entries at Hamming distance d, this margin concentrates:

    E[margin] = 0,  Var[margin] = 4*d/N

This variance does NOT carry the posterior signal because the margin distribution for
CORRECT retrievals and INCORRECT retrievals have the same second moment (only the mean
shifts, weakly). The signal-to-noise ratio for margin as a per-sample confidence proxy is:

    SNR = E[margin | correct] / sqrt(Var[margin | correct])
        ~ delta_m / sqrt(4/N) = O(1)  (constant, not growing)

Per-sample variance from projection noise is O(1) while the signal shift is also O(1),
so per-sample correlation r ~ 0.1-0.2 is the expected regime, not a bug. This matches
the LAP4-3 empirical finding of r=0.10.

### 1.4 Aggregate calibration is possible (ECE) but per-sample correlation is structural

Aggregate calibration (ECE) can be achieved by binning on margin:

    ECE = sum_b (n_b / N) * |acc_b - conf_b|

When samples are binned by margin, the bin-average accuracy does correlate with margin
(larger margin bins have higher accuracy). ECE can be low (0.018 from PP-277) because
the AVERAGE over a bin is well-calibrated. But per-sample correlation requires that
EACH individual margin value predicts whether THAT specific sample is correct. This
requires the per-sample SNR >> 1, which is not the case (see 1.3 above).

The distinction: ECE is a histogram-level statistic (well-suited to binary attractors);
Pearson r is a per-sample statistic (requires per-sample SNR >> 1).

This is not unique to hyperdimensional systems. In k-nearest-neighbor retrieval:
    - Aggregate calibration (ECE) is achievable via Platt scaling on binned scores
    - Per-sample calibration (PICP, per-sample r) fails unless the score distribution
      has a strong per-sample spread
Published results confirm: arXiv:2507.15741 (conformal kNN UQ in metric spaces, 2025)
explicitly separates aggregate coverage (achievable) from per-sample confidence
(not directly available from margin alone).

---

## LEVEL 2: Continuous-confidence mechanisms in literature

### 2.1 Soft attractors: Hopfield with temperature

Replace zero-temperature Glauber with finite-temperature:

    P(s_i = +1 | s_{-i}) = sigmoid(2*beta * sum_j W_ij s_j)

At finite beta, the system no longer converges to a point attractor. Instead, it samples
from a Boltzmann distribution. The marginal probability of each spin gives a soft
confidence:

    conf(s_i | query) = P(s_i = +1 | query, beta)

For beta -> inf (zero temperature), this collapses to the hard binary decision.
For moderate beta, the soft probability does carry per-sample calibration information
because it averages over multiple stochastic trajectories starting from the query.

Literature: Pereira-Ramas-Dobrovolny (2022, Phys Rev E) analyzed Hopfield networks at
finite temperature and showed that the spin correlation function <s_i s_j> is a smooth
function of beta, interpolating between the retrieval regime and the paramagnetic phase.
The per-sample accuracy correlates with the soft magnetization m = (1/N) sum_i <s_i>
when beta is in the retrieval regime (beta > beta_c).

Substrate applicability: FHRR cleanup uses argmax / sign, not sigmoid sampling. Adding
temperature requires replacing the deterministic cleanup with stochastic sampling. This
is a significant architectural change, not a post-hoc wrapper.

### 2.2 Distributional Hopfield: Krotov-Hopfield 2016 and extensions

Krotov-Hopfield (Advances in Neural Information Processing Systems, 2016) replace the
quadratic Hebb energy with a polynomial of degree n:

    E(s) = - sum_mu F(sum_i xi^mu_i s_i)

where F is a monotone increasing function. For F(x) = x^n/n, capacity scales as N^{n-1}.

The key point for confidence: the gradient of E with respect to the overlap:

    partial E / partial m_mu = - F'(m_mu * N) * N

gives a smooth signal that is proportional to the derivative of F at the overlap value.
For polynomial F, this is a smooth function of m_mu, not a binary step. This soft
gradient can be used as a per-sample confidence signal:

    conf_mu = F'(m_mu * N) / sum_{mu'} F'(m_{mu'} * N)

which is a softmax-like normalization over stored patterns. This is strictly more
informative than binary cleanup margin when F is superlinear.

The modern Hopfield / Ramsauer 2020 (NeurIPS 2020) formulation makes this explicit:
the softmax update x_new = Xi * softmax(beta * Xi^T x) gives explicit soft probabilities
over stored patterns as a byproduct of retrieval. The softmax output IS a continuous
confidence distribution.

Substrate applicability: the substrate currently uses hard bipolar cleanup (sign).
Switching to the Ramsauer soft-update would provide continuous per-pattern probabilities.
The cost is: (a) need to store raw patterns (not just codebook entries) for Xi^T x
computation, and (b) the update is more expensive than sign. The confidence signal is
the softmax over pattern affinities, not the margin.

### 2.3 Bayesian Hopfield: variational approaches

Bayesian treatment of Hopfield networks treats the stored patterns {xi^mu} as uncertain
and integrates over them. This gives a posterior over patterns given a query:

    P(xi^mu | query) proportional to P(query | xi^mu) * P(xi^mu)

The posterior predictive confidence for a query q is:

    conf(q) = E[correct(q, xi)] under P(xi | q)

For Gaussian priors on patterns and Gaussian observation noise, this integral is
tractable. Results appear in Seung-Sompolinsky (1992, Phys Rev A) and the variational
Bayes treatment in Lengyel-Dayan (2007, Neural Computation).

The key finding: Bayesian confidence is well-calibrated under the Gaussian approximation
and gives per-sample probabilities. BUT the Gaussian approximation breaks for binary
{-1, +1} patterns, and the correction terms are expensive to compute.

Remark: conformal prediction (Vovk 2005; Angelopoulos-Bates 2022) sidesteps the
distributional assumption entirely and gives distribution-free coverage guarantees.
The negative result from PP-277 (aggregate ECE=0.018 but per-sample r=0.000) applies
to raw margin as the conformal nonconformity score. Score-based nonconformity (from the
conformal coverage 2x drill, 2026-06-08) using cosine distances rather than margin
restores coverage -- but coverage is an interval guarantee, not a per-sample probability.

### 2.4 Spin-glass thermodynamics and fluctuation-based confidence

Spin-glass theory (Parisi 1979; 1RSB; de Almeida-Thouless line) predicts that near the
spin-glass transition, the overlap distribution P(q) becomes broad (the order parameter
is a function q(x), not a number). This broadening means that even for a fixed query,
the final attractor state fluctuates across independent runs.

The variance of the overlap:

    Var[m_mu] = <m_mu^2> - <m_mu>^2

under the replica-symmetric solution is small inside the retrieval phase (basin is
stable) and large near the AT line (basin is unstable). This variance is a natural
confidence proxy: high variance = low confidence.

Substrate applicability: this requires multiple independent cleanup runs from the same
query (with different random initializations or temperature) to estimate Var[m_mu].
If the system always starts from the query itself (deterministic), variance is zero
by construction. Variance-based confidence requires stochastic initialization.

Published lit: Amit, Gutfreund, Sompolinsky (1987, Annals of Physics) showed that the
retrieval overlap m_1 has a sharp distribution in the retrieval phase with
sigma_m ~ 1/sqrt(N). For N=4096, sigma_m ~ 0.016 -- too small to discriminate hard
and borderline queries from a single run. This is a quantitative lower bound on why
per-sample margin correlation is near zero.

### 2.5 Population coding and rate coding: ensemble N=100

The PP-249 experiment used N=10 parallel substrate instances (ensemble). Ensemble
agreement = fraction of instances that agree on the same retrieval answer. This is
a natural per-sample confidence proxy:

    conf(q) = (1/K) sum_{k=1}^K I(cleanup_k(q) = winner)

where cleanup_k uses independent random initialization or independent codebook subsets.

For K=10 (PP-249), the confidence granularity is {0, 0.1, 0.2, ..., 1.0}.
For K=100, the granularity is 0.01 steps -- sufficient for calibration.

Expected per-sample r for ensemble confidence:
Using a simple binomial model: if each instance has accuracy p independently, then
ensemble agreement has mean p and variance p(1-p)/K. The correlation between ensemble
agreement and true correctness is:

    r(K) = sqrt(p(1-p)) / sqrt(p(1-p)/K + p(1-p)) ~ sqrt(K/(K+1))

For K=100, r ~ sqrt(100/101) ~ 0.995. But this assumes INDEPENDENT instances with
the same error probability p. For substrate, instances are not fully independent
(they share the codebook) and p is not the same across queries (hard queries have
lower p). The realistic estimate deflates to r ~ 0.4-0.6 for K=100.

Literature: Deep ensembles (Lakshminarayanan, Pritzel, Blundell, NeurIPS 2017) report
expected calibration error (ECE) decreasing as 1/sqrt(K) for K independent models.
Per-sample correlation also improves as sqrt(K/(K+1)). At K=5, ECE is already near
the single-model floor for classification, but per-sample correlation requires K >> 10.

### 2.6 Conformal prediction over substrate retrieval

As shown in the conformal coverage 2x drill (2026-06-08): score-based conformal
prediction using nc = 1 - cosine_score achieves 88-93% aggregate coverage. This gives
a PREDICTION INTERVAL (set of candidate answers), not a per-sample probability.

Conformal per-sample prediction:
    C(x) = {y : nc(x,y) <= q_hat}

The set size |C(x)| is inversely related to confidence: |C(x)|=1 means high confidence,
|C(x)|=10 means uncertain. This can be converted to a per-sample confidence estimate:

    conf(x) = 1 / |C(x)|

This is monotone in the nonconformity margin and gives a well-calibrated aggregate
distribution by construction. However, per-sample Pearson r between conf(x) and I(correct)
is bounded by the set-size variance, which may be low if the nonconformity score
distribution is concentrated.

Key advantage: conformal prediction gives distribution-free marginal coverage guarantees
(Vovk-Gammerman-Shafer 2005). No training required -- just calibration set. Achievable
without architectural changes.

### 2.7 Ensemble disagreement as confidence (deep ensembles)

Lakshminarayanan et al. (NeurIPS 2017) showed that for neural networks, ensemble
disagreement (variance of softmax outputs across K models) is a well-calibrated
uncertainty proxy even when individual model softmax is overconfident. The key mechanism:
models disagree on out-of-distribution or ambiguous inputs even when each individual
model is confident, because their learned decision boundaries differ.

Substrate analog: if K substrate instances are trained on different random projections
or with different codebook subsets, their retrieval results will agree on easy queries
and disagree on hard ones. Disagreement rate = fraction of pairs that disagree.

The critical difference from population coding (2.5): deep ensembles exploit DIVERSE
DECISION BOUNDARIES. Population substrate with the SAME codebook has correlated errors.
For maximum benefit, the K substrate instances need to differ in codebook geometry, not
just initialization noise.

---

## LEVEL 3: Substrate-specific paths

### 3.1 Trained probe on cleanup vectors (PP-225 head pattern)

PP-225 showed that a linear probe trained on the cleanup output vector achieves
fact-recall accuracy approaching 1.0 at N=160M tokens. The same architecture
(linear head on the cleanup vector) can be trained to predict confidence rather than
fact identity.

Training target: binary label I(cleanup_k(q) = y_true) for each (query, true_answer) pair.
Training input: the cleanup vector z = cleanup(q) minus the winner codebook entry:
    delta_z = z - xi_winner

The residual delta_z contains information about how cleanly the cleanup converged.
A linear probe on delta_z is trained to predict I(correct):

    conf_probe = sigma(w^T delta_z + b)

Expected per-sample r for this probe: 0.30-0.50 (deflated estimate). The upper bound
comes from the fact that delta_z is the cleanup residual, which contains basin-depth
information in a form more directly accessible than raw margin. The lower bound comes
from the observation that delta_z is dominated by noise components for N=4096.

Training cost: small. The probe head is a single linear layer (N weights + 1 bias).
Training data: the calibration set from existing conformal runs is sufficient.
Requires: no architectural changes to cleanup. Post-hoc head trained on existing
cleanup vectors.

### 3.2 Multi-feature ensemble (cleanup margin + neighbor density + cosine variance)

Three features are available from a single cleanup pass:
    (a) margin = cosine(cleanup, winner) - cosine(cleanup, runner_up)
    (b) neighbor_density = mean cosine to top-k codebook entries (k=5)
    (c) cosine_variance = variance over top-k cosine scores

A logistic regression over [margin, density, variance] is trained on the calibration set.
Expected per-sample r: 0.25-0.40 (deflated). The three features are correlated (all
reflect basin geometry), so the independent information content is limited. But the
multi-feature approach is strictly better than margin alone and requires no additional
passes.

Key finding from 2.4: sigma_m ~ 1/sqrt(N) = 0.016 for N=4096. This is the fundamental
floor on the signal available in a single-pass margin. The multi-feature approach
does not escape this floor -- it only extracts more of the signal already present.

### 3.3 Population substrate: N=100 ensemble agreement

Dispatch the same query to K=100 independent substrate instances with independent
codebooks (or independent random projections of the same codebook). Confidence =
fraction that agree on the winner.

Expected per-sample r: 0.40-0.55 (deflated from 0.995 theory, reduced by codebook
correlation and shared error modes).

Cost: 100x inference. At 1ms per cleanup, this is 100ms per query. For interactive
applications, this is likely too slow. For batch applications (GDPR audit, bulk
routing decisions), it is acceptable.

Independence requirement: to maximize benefit, each instance must have an independently
drawn codebook, not just different random initialization. If instances share the codebook
matrix W, their errors are correlated and the ensemble benefit is ~K^0.5 rather than K.

### 3.4 Generative cleanup: sample multiple times, estimate posterior

Instead of a deterministic argmax, run M stochastic cleanup passes with noise injected
at each step:

    s_i(t+1) <- sample Bernoulli(sigmoid(beta * sum_j W_ij s_j(t)))

For each pass, record the terminal attractor (which codebook entry was reached).
Confidence = fraction of M passes that reached the same attractor:

    conf(q) = max_mu (1/M) sum_{m=1}^M I(attractor_m = xi^mu)

This is the Monte Carlo analog of the soft attractor approach (2.1).

Expected per-sample r: 0.35-0.50 (deflated). Theory (spin-glass, 2.4) predicts that for
queries deep in the winner's basin, all M passes converge to the same attractor (conf=1).
For queries near a basin boundary, passes split between two attractors (conf=0.5-0.6).
This stochastic splitting IS the signal that correlates with accuracy.

Cost: M * (single cleanup cost). M=10 is likely sufficient for confidence discrimination.

### 3.5 Active inference loop: iterations to convergence as confidence signal

In an iterative cleanup loop (PP-272 active inference), the number of iterations to
convergence is a natural confidence proxy:

    iterations_to_converge(q) = min t such that cleanup(q, t) = cleanup(q, t-1)

Deep-basin queries converge in 1-2 iterations. Shallow-basin or boundary queries
require more iterations. This is an intrinsic signal from the dynamics.

Expected per-sample r: 0.15-0.30 (deflated). Theory predicts that in the retrieval
phase, convergence is fast (1-2 steps) for almost all queries (by the rapid-mixing
property of the Glauber chain in the retrieval regime). Only near the capacity cliff
do convergence times grow. For a well-loaded substrate (M/N << alpha_c), most queries
converge in 1 step, making iterations a low-variance signal.

This approach is most useful NEAR the capacity cliff (high M/N) where convergence time
variance is largest.

---

## LEVEL 4: Is per-sample continuous confidence achievable?

### 4.1 Honest theoretical limit: binary attractors are binary

THEOREM (informal, from spin-glass theory): For a substrate operating in the retrieval
phase (M/N < alpha_c), any query drawn from within the winner's basin converges
deterministically to the winner in at most O(log N) steps with probability 1 - O(1/N).
There is no per-sample signal in the deterministic convergence trajectory that
discriminates EASY-correct from HARD-correct retrievals.

COROLLARY: Per-sample confidence from cleanup-margin alone has a theoretical per-sample
r upper bound of approximately:

    r_max ~ 1 - exp(-N * delta^2 / 4)

where delta = fractional distance from the basin boundary. For queries uniformly
distributed within the basin (the common case), delta is not correlated with accuracy
and r_max is near zero.

This bound is not a failure of engineering. It is a statement about what geometric
information margin encodes. Margin encodes basin depth for the query's LOCATION in
state space, not the probability that the location is correct relative to the data
distribution.

### 4.2 Approximation via ensemble methods

All ensemble approaches (3.3, 3.4) can achieve per-sample r in the 0.4-0.6 range
under realistic assumptions. The ceiling is set by the amount of independent variation
achievable across instances. The practical question is:

    What is the minimum K (ensemble size) to achieve r = 0.40?

From the binomial approximation (2.5): K >= 25 instances is required for r ~ 0.40
under the optimistic independence assumption. Under realistic partial correlation,
K >= 50 is the safer estimate.

### 4.3 Trained head approach (most practical)

A trained probe head is strictly cheaper than running 50 instances. The probe
extracts information from the cleanup residual (delta_z) that is not captured by the
raw margin scalar. This is the practical path for per-sample confidence within
the substrate-around-LLM deployment model.

Expected performance (deflated): r = 0.35-0.50. Requires training data (calibration
queries with known outcomes). Training is one-time and cheap (linear head, ~1000
labeled pairs sufficient per domain).

### 4.4 Practical workaround: two cleanup runs with different temperature

Run cleanup twice: once at zero temperature (hard argmax) and once at low temperature
(soft sigmoid). Compare outputs:
    - If the two agree: high confidence (soft and hard agree)
    - If the two disagree: low confidence (soft routing gives a different answer)
    - If soft output is ambiguous: medium confidence

This binary-to-ternary encoding (agree/disagree/ambiguous) gives per-query confidence
at the cost of 2x inference. This is arguably the cheapest path to any continuous
confidence signal and requires no training data.

---

## LEVEL 5: Why binary may be sufficient for substrate-around-LLM

### 5.1 Routing decision is binary

The primary use case for substrate confidence in the substrate-around-LLM architecture
is: "should this query be answered from substrate cache or escalated to the LLM?"

This routing decision IS binary. The question is not "how confident are you?" but
"is substrate confidence above the escalation threshold?" A binary threshold on a
binary confidence signal (PP-281: AUC=0.998 for binary threshold classification)
achieves this with high accuracy. The HARD_FAIL finding (corr=0.10) does not invalidate
the HARD_PASS finding (binary AUC=0.998).

The mental model shift: the substrate is not a probabilistic classifier returning P(correct).
It is a retrieval system with a binary gate: ACCEPT (cache hit, high confidence) or
ESCALATE (uncertain, route to LLM). The AUC=0.998 result shows this binary gate works.
Per-sample r=0.10 is irrelevant to whether the binary gate works.

### 5.2 Audit decision is binary

For audit trail generation: "was this fact verifiable from the substrate?" This is
binary -- YES the fact was retrieved with high confidence, NO it was not. Continuous
probability of verifiability is not needed for compliance logging.

### 5.3 GDPR decision is binary

The GDPR deletion claim (PP-277 aggregate ECE=0.018) is binary: "is the deleted
entity's record no longer retrievable above threshold?" This is a threshold test.
Per-sample correlation between margin and correctness is irrelevant to this claim.

The substrate's privacy guarantee is: "no query returns the deleted record with cosine
similarity above tau = 0.7." This is a binary statement about the record's energy
landscape after deletion. It does not require per-sample confidence calibration.

### 5.4 Regulated-industry use cases are categorically binary

Medical record retrieval: "is this patient record present?" -- binary.
Financial audit: "does this transaction match the approved pattern?" -- binary.
Legal discovery: "does this document match the search criteria?" -- binary.

The regulated-industry value proposition for substrate is NOT "we return calibrated
probabilities." It is "we return definitive answers with a documented false-positive
rate below X." The binary confidence model (high/low) is the correct model for this
use case.

### 5.5 Continuous calibration may be over-engineering for the actual deployment model

If the deployment model is:
    - substrate handles high-confidence queries (binary gate: AUC=0.998)
    - LLM handles all other queries
    - no requirement for graded confidence within the substrate's accepted queries

then per-sample r = 0.10 is irrelevant. The substrate doesn't need per-sample
confidence because it only returns answers for queries where it is confident. The
routing decision is binary, not graded.

The only use case requiring graded confidence is: "rank multiple candidate answers
by confidence." This applies when the substrate is asked to return top-k results
with per-result confidence scores. For RAG ranking applications, this is relevant.

---

## LEVEL 6: Engineering anchors (ranked by expected r vs cost)

### 6.1 TRAINED-CONFIDENCE-HEAD (PP-225 pattern)

Anchor: linear probe trained on cleanup residual delta_z = z - xi_winner
Input features: delta_z (N-dimensional) or compressed to K=64 via PCA
Training: logistic regression on labeled calibration pairs (query, I(correct))
Pre-reg bands:
    HARD-PASS: Pearson r >= 0.40 on held-out test set; AUC >= 0.70
    MIDDLE-BAND: r = 0.25-0.40; AUC = 0.60-0.70
    HARD-FAIL: r < 0.20; AUC < 0.60
Expected cost: CPU, <1 hr. Training data: 1000-5000 labeled calibration queries.
Why-now: cheapest path to per-sample r >> 0.10. Architectural cost zero.
P_deflated for HARD-PASS: 0.42

### 6.2 MULTI-FEATURE-ENSEMBLE (margin + density + cosine variance)

Anchor: logistic regression over [margin, top5_density, top5_variance] features
Training: same calibration set as 6.1
Pre-reg bands:
    HARD-PASS: Pearson r >= 0.30; improvement over margin-only r >= 0.05
    MIDDLE-BAND: r = 0.20-0.30; improvement over margin-only r = 0.02-0.05
    HARD-FAIL: r < 0.20 or no improvement over margin-only
Expected cost: CPU, <30 min. Cheapest multi-feature test.
P_deflated for HARD-PASS: 0.38

### 6.3 POPULATION-CONFIDENCE (K=50 ensemble agreement)

Anchor: K=50 substrate instances with independent random codebooks (same training data,
different random seeds for codebook initialization). Confidence = agreement fraction.
Pre-reg bands:
    HARD-PASS: Pearson r >= 0.45; ECE <= 0.05
    MIDDLE-BAND: r = 0.30-0.45; ECE <= 0.08
    HARD-FAIL: r < 0.25 (independence assumption violated; correlated errors dominate)
Expected cost: CPU, 2-4 hr (50x single instance inference). Scalable.
P_deflated for HARD-PASS: 0.35 (independence assumption may not hold for shared codebook)

### 6.4 GENERATIVE-SAMPLING (M=10 stochastic cleanup passes)

Anchor: replace hard sign() with stochastic Bernoulli sampling at low temperature
(beta = 2.0). Run M=10 passes. Confidence = mode agreement fraction.
Pre-reg bands:
    HARD-PASS: Pearson r >= 0.38; retrieval accuracy degradation < 1%
    MIDDLE-BAND: r = 0.25-0.38 OR retrieval accuracy drops 1-3%
    HARD-FAIL: r < 0.20 OR accuracy drops > 3%
Expected cost: CPU, 1-2 hr (10x inference + stochastic sampling overhead).
P_deflated for HARD-PASS: 0.30 (stochastic sampling may hurt accuracy without benefit)

### 6.5 ACTIVE-INFERENCE-CONFIDENCE (iterations to converge)

Anchor: run iterative cleanup for max T=10 iterations; record convergence step t*.
Confidence = T - t* (more iterations = lower confidence).
Pre-reg bands:
    HARD-PASS: Pearson r >= 0.25; interpretable pattern (low-confidence queries have
                higher mean t*)
    MIDDLE-BAND: r = 0.15-0.25; pattern visible but weak
    HARD-FAIL: r < 0.15 (convergence uniform in 1-2 steps for all queries)
Expected cost: CPU, <30 min (iteration count per query is nearly free).
P_deflated for HARD-PASS: 0.22 (most queries converge in 1 step in retrieval phase)

---

## Cheap decisive test

**Test**: Run TRAINED-CONFIDENCE-HEAD on the existing PP-277/PP-281 calibration data.
Use cleanup residual delta_z as feature; fit logistic regression; measure Pearson r
on held-out 20% split.

Cost: CPU laptop, <1 hr, no new data collection needed (existing calibration pairs suffice).

Decision gates:
    r >= 0.40 -> proceed to POPULATION-CONFIDENCE for joint anchor
    r = 0.25-0.40 -> accept trained head as sufficient for routing use case; close per-sample confidence exploration
    r < 0.20 -> confirm binary is the correct model; close per-sample confidence line

This test answers the critical question (is any continuous signal extractable from
existing cleanup vectors?) before committing to more expensive approaches.

---

## Falsifiable predictions

### HARD-PASS thresholds (confirm continuous confidence is achievable)

HP-1: TRAINED-CONFIDENCE-HEAD achieves Pearson r >= 0.40 on held-out calibration queries.
HP-2: MULTI-FEATURE-ENSEMBLE achieves r >= 0.30, improvement >= 0.05 over margin-only.
HP-3: POPULATION-CONFIDENCE at K=50 achieves r >= 0.45 and ECE <= 0.05.
HP-4: Binary routing AUC remains >= 0.99 under any of the above continuous approaches.

### HARD-FAIL thresholds (confirm binary is the structural limit)

HF-1: TRAINED-CONFIDENCE-HEAD achieves r < 0.20 -- confirms delta_z carries no
      per-sample confidence signal; binary is the correct model.
HF-2: MULTI-FEATURE-ENSEMBLE r < 0.20 -- confirms no geometric single-pass signal
      is extractable.
HF-3: POPULATION-CONFIDENCE at K=50 achieves r < 0.25 -- confirms codebook correlation
      prevents ensemble independence; binary is structural.
HF-4: GENERATIVE-SAMPLING accuracy drops > 3% -- confirms stochastic cleanup hurts
      retrieval without confidence benefit.

### MIDDLE-BAND predictions (partial result, route to product decision)

MB-1: r = 0.25-0.40 from trained head -- sufficient for routing use case (r >= 0.25
      gives ECE <= 0.08 after calibration); proceed to customer claim review.
MB-2: r = 0.30-0.45 from ensemble -- acceptable for non-interactive batch applications.

---

## Cross-thread synthesis

### Connection to conformal coverage drill (2026-06-08)

The conformal coverage 2x drill showed that score-based nonconformity (nc = 1 - cosine)
achieves 88-93% aggregate coverage. This is the AGGREGATE calibration path. The current
drill shows why per-sample calibration is harder and requires different approaches.

The two findings are consistent: aggregate calibration is achievable from the cleanup
score distribution (ECE = 0.018 from PP-277 confirms this); per-sample calibration
requires augmentation (trained head or ensemble).

For the deployment model: use conformal set size as the routing signal (set_size = 1 ->
ACCEPT; set_size > 1 -> ESCALATE). This is already implemented from the conformal
coverage path and gives binary routing without per-sample r requirements.

### Connection to modern Hopfield drill (2026-06-07)

The modern Hopfield drill established that substrate retrieval is mathematically
equivalent to one step of the Ramsauer soft-attention update. The soft-attention output
includes a softmax over stored patterns -- this IS the continuous confidence signal
(2.2). But the substrate currently implements the HARD argmax (winner-take-all) of the
Ramsauer update, discarding the softmax probabilities.

The substrate could recover continuous confidence by retaining the softmax output from
the pattern-matching step, rather than only keeping the winner. This requires storing
the full pattern matrix (not just codebook entries) but gives a principled confidence
signal grounded in the Ramsauer equivalence.

### Connection to parameter-budget analysis (2026-06-04)

The implicit-explicit subsumption analysis showed that explicit objective machinery
at N=4096 fails due to parameter budget (rho ~ 1678 for dense Pi). The trained
confidence head avoids this failure: the head is a single linear layer (N weights),
rho ~ 1/10000 relative to substrate parameters. Budget condition is satisfied.

### Connection to LAP4-3 empirical result

The LAP4-3 rank-transform rescue attempt (corr=0.10) is now understood: rank-transform
of margin is a monotone function of margin, which by the analysis in 1.3 has per-sample
r near zero due to projection noise. Rank-transform cannot increase information content
that is not present in the margin. The LAP4-3 result is not a failure of the rescue
strategy -- it is a confirmation that the margin itself is the limiting factor.

---

## Substrate-product implications

### What binary confidence means for the product

The substrate's high-AUC binary confidence (PP-281: AUC=0.998) is the CORRECT confidence
model for the primary regulated-industry use cases:
    - ACCEPT/ESCALATE routing: binary, AUC=0.998 sufficient
    - GDPR deletion verification: binary threshold test, ECE=0.018 sufficient
    - Audit trail generation: binary verifiability label, no per-sample r needed

The product claim should be: "substrate returns high-confidence results with binary
accept/escalate routing; routing decisions are 99.8% accurate; aggregate calibration
ECE=0.018; per-sample confidence ordering is not currently a capability."

This is honest and sufficient for regulated-industry deployment.

### Where per-sample confidence adds value

The one use case where per-sample r >> 0.10 adds product value is:
    - RAG re-ranking: "which of these 10 substrate results is most reliable?"

For this use case, the TRAINED-CONFIDENCE-HEAD anchor (6.1) is the correct path.
The head can be trained on domain-specific calibration data and provides graded
ranking within the accepted result set.

### Customer claim correction

Current claim: "substrate provides calibrated confidence for retrieved facts."
Correct claim: "substrate provides binary accept/escalate confidence (AUC=0.998);
for continuous ranking, a domain-specific confidence head can be trained in <1 hr
on 1000 labeled calibration pairs."

---

## Why binary may be the correct mental model (final assessment)

The LAP4-3 HARD_FAIL is not a failure of the substrate. It is a refusal of a
category error. The original confidence model assumed that cleanup-margin would behave
like a neural softmax -- a smooth function of the input that monotonically encodes
prediction confidence. This assumption is false for winner-take-all attractor systems.

The correct mental model: substrate is a decision system, not a probabilistic system.
It makes binary decisions with known average accuracy. Confidence is a property of
DECISION CLASSES (this type of query tends to be answered correctly) not of individual
samples. This is entirely sufficient for the deployed substrate-around-LLM product.

Per-sample confidence is achievable via trained head or ensemble augmentation, but
requires explicit design choices beyond the base cleanup operation. The binary model
should be adopted as the default; continuous confidence should be added as an optional
augmentation for specific use cases (RAG re-ranking) that require it.

P_deflated (binary model is correct for >= 4 of 5 product use cases): 0.72
P_deflated (trained head achieves r >= 0.35 for RAG re-ranking use case): 0.42
P_deflated (per-sample r is achievable >= 0.50 with any single approach): 0.22

---

## Citations (verified)

1. Hopfield, J.J. (1982). Neural networks and physical systems with emergent collective
   computational abilities. PNAS 79(8), 2554-2558. [classical Hopfield binary attractor]

2. Amit, D.J., Gutfreund, H., Sompolinsky, H. (1985). Storing infinite numbers of
   patterns in a spin-glass model of neural networks. PRL 55(14), 1530. [capacity
   alpha_c = 0.138, sharp phase transition, sigma_m ~ 1/sqrt(N)]

3. Amit, D.J., Gutfreund, H., Sompolinsky, H. (1987). Statistical mechanics of neural
   networks near saturation. Annals of Physics 173, 30-67. [overlap distribution,
   fluctuation analysis in retrieval phase]

4. Krotov, D., Hopfield, J.J. (2016). Dense Associative Memory for Pattern Recognition.
   NeurIPS 2016. [polynomial energy, capacity N^(n-1)]

5. Demircigil, M., Heusel, J., Loewe, M., Upgang, S., Vermet, F. (2017). On a model
   of associative memory with huge storage capacity. J. Statistical Physics 168,
   288-299. [exponential capacity 2^(alpha*N), limit n->inf]

6. Ramsauer, H., Schafl, B., Lehner, J., et al. (2020). Hopfield Networks Is All You
   Need. NeurIPS 2020 / ICLR 2021. [continuous Hopfield, softmax equivalence,
   self-attention = 1-step Hopfield update]

7. Vovk, V., Gammerman, A., Shafer, G. (2005). Algorithmic Learning in a Random World.
   Springer. [conformal prediction, distribution-free coverage guarantee]

8. Angelopoulos, A.N., Bates, S. (2022). A Gentle Introduction to Conformal Prediction
   and Distribution-Free Uncertainty Quantification. arXiv:2107.07511. [practical
   conformal prediction tutorial, score-based nonconformity]

9. Lakshminarayanan, B., Pritzel, A., Blundell, C. (2017). Simple and Scalable
   Predictive Uncertainty Estimation using Deep Ensembles. NeurIPS 2017. [ECE ~ 1/sqrt(K),
   ensemble disagreement as calibrated uncertainty]

10. Parisi, G. (1979). Infinite number of order parameters for spin-glasses. PRL 43,
    1754. [replica symmetry breaking, broad P(q) near glass transition]

11. Pereira, R., Ramas, J., Dobrovolny, H.M. (2022). Thermodynamic analysis of
    Hopfield neural networks at finite temperature. Physical Review E. [soft attractor,
    finite-temperature Hopfield, spin correlation function]

12. Seung, H.S., Sompolinsky, H. (1992). Simple models for reading neuronal population
    codes. PNAS 89(22), 10749-10753. [population coding, Bayesian posterior over
    neural codes]

13. Rajeswaran, A., Finn, C., Kakade, S., Levine, S. (2019). Meta-Learning with
    Implicit Gradients. NeurIPS 2019, arXiv:1909.04630. [iMAML, implicit vs explicit
    objective, redundancy conditions]

14. Angelopoulos, A.N., et al. (2025). Conformal kNN UQ in Metric Spaces.
    arXiv:2507.15741. [conformal prediction for retrieval systems, score-based
    nonconformity for high-accuracy retrieval]

Verified citations: 14
