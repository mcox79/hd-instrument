# Orthogonal research shortlist -- 2026-05-26

**Purpose.** Queue-refill planning aid. Every refill cycle should draw at least 1 candidate from
this shortlist. Candidates are filtered for:
- (a) genuine orthogonality to frameworks already drilled through 2026-05-26
- (b) plausible map to substrate operations (BSC binary atoms + PPMI sparsification + asymmetric
  Hebbian + linear-heteroassoc primitive)
- (c) drill_count <= 2 in advisor history
- (d) capability-unlocking potential (new capability class, not confirmatory)

**Calibration.** All P estimates deflated per [[feedback-lit-scan-calibration-penalty]] (0.15-0.25
penalty; novel-synthesis cap = 0.50).

**Already exhausted today (2026-05-26) -- do NOT re-drill:**
tropical geometry, Boolean function analysis, Clifford tensor networks, reaction-diffusion / Turing,
Wright-Fisher / population genetics, MCT structural glass, mesoscopic transport (Landauer-Buttiker),
free-probability FAC / top-edge (v211-v213), Saad-Solla + 1-RSB + MoE SHIFT synthesis, R26 AGS
scaling, reservoir computing / Lyapunov (handoff dispatched 2026-05-24), hierarchical replay,
PT cascade, SWR cascade, alpha_c anomaly, alpha_c band audit, alternative theoretical homes,
primitive decision linear-vs-recurrent, Bet N readiness, SSM-HiPPO, primitive decision recurrent.

---

## Candidate 1 -- Entropic optimal transport / Sinkhorn / Wasserstein DEEPER

**Field:** Optimal transport / Sinkhorn divergence / Wasserstein distances
**Prior drill count:** 0 (mentioned in breadth analysis 2026-05-24 at survey-level; never drilled
operationally; scored F-3 = 10/12 in `research_new_fields_breadth_analysis_2026-05-24.md`)

**Framing (what the math does):**
Entropic OT finds a minimum-cost transport plan between two distributions, regularized by entropy
at scale epsilon. The Sinkhorn iteration converges to the unique minimizer via log-space matrix
scaling. At epsilon -> 0, Sinkhorn recovers exact OT (Wasserstein-2). At finite epsilon, Sinkhorn-
divergence S_epsilon(mu, nu) is negative-definite, differentiable, and admits concentration bounds
(Kengo Kato limit theorems 2024; Fournier-Guillin 2015 rate O(n^{-2/d})).

**Why capability-unlocking:**
Substrate's argmax readout IS an assignment problem: map incoming query y to nearest codeword w_i.
Reframing as entropic OT gives (a) a NEW differentiable readout primitive (transport-regularized
argmax) distinct from the current hard argmax; (b) Sinkhorn divergence as a substrate dissimilarity
metric for Cap 1 forensic erase certificates -- the OT distance between pre-erase and post-erase
distributions is lower-bounded by the Crooks work, connecting two load-bearing frameworks; (c) if
substrate's PPMI sparsification has a natural "mass" interpretation, OT gives a closed-form flow
from dense to sparse codebook under BSC channel noise. None of the 8 current caps uses OT; this
opens a potential Cap-13 anchor distinct from Crooks FT / Conformal / VAMP.

**Adjacency parent:** F-3 in breadth analysis; adjacent to free-probability (Marchenko-Pastur bulk
can be described as Wasserstein barycenters of empirical spectral distributions) AND to AMP-state-
evolution (Sinkhorn iteration is a fixed-point convolution structurally identical to AMP damping).

**Proto-drill question for exp_dev:**
Map substrate's argmax readout as a Sinkhorn assignment at temperature epsilon; measure whether
Sinkhorn-divergence between pre-write and post-erase W distributions correlates with Crooks work
W_diss across 5 erase conditions; does the OT-distance bound the Crooks fluctuation within 10%?

**Calibrated P(yields useful finding) = 0.42**
(base 0.55 from breadth-analysis score 10/12 and active lit; deflated 0.13 for: two-edge connection
to substrate, novel-synthesis for Kerdock-specific OT formulation, no published OT-on-Hopfield
directly; stays below 0.50 novel-synthesis cap)

**Suggested drill type:** Theory anchor (~1-2 day Research) + cheap CPU smoke (~30 min)

---

## Candidate 2 -- Spectral graph theory on substrate's W

**Field:** Spectral graph theory (Chung, Spielman-Teng, Fiedler vector, graph Laplacian)
**Prior drill count:** 0 (NOT in advisor's field registry at all; no prior mention in any research note)

**Framing (what the math does):**
Spectral graph theory studies eigenvalues and eigenvectors of graph Laplacian L = D - A (or
normalized form L_norm = D^{-1/2} A D^{-1/2}) where A is an adjacency matrix and D is degree
matrix. The Fiedler value lambda_2 measures graph connectivity (algebraic connectivity). The
Cheeger inequality 2h_G >= lambda_2 >= h_G^2 / 2 bounds the bottleneck (isoperimetric number)
of the graph. Expander graphs have lambda_2 = Omega(1/N).

**Substrate mapping:**
Substrate's W is a weight matrix on atoms (rows = "from" atoms, cols = "to" atoms). Treating W as
a BIPARTITE graph adjacency (atoms as nodes, entries as weighted edges) gives a Laplacian whose
spectral gap measures HOW WELL the substrate propagates information between atom types. Concretely:
large lambda_2(L_W) => good mixing, fast convergence of substrate's iterated argmax (fewer cleanup
iterations needed). Small lambda_2 => bottleneck / partitioned structure (consistent with MoE SHIFT
observation at v212). The substrate's BSC channel can be read as a noisy graph diffusion; Spielman-
Teng spectral sparsifiers would give a sparse substrate that preserves all spectral properties to
1+epsilon.

**Why capability-unlocking:**
(a) Fiedler value gives a DIRECT measure of substrate's algebraic connectivity -- a substrate
diagnostic not in any existing observability suite; (b) spectral sparsification (Spielman-Teng
linear-sized sparsifiers) could give a sparse W with same retrieval properties but O(N log N / eps^2)
edges vs current O(N^2) -- potential Cap 9 (hardware efficiency) angle; (c) the lambda_2 / Cheeger
ratio gives a NEW convergence-rate bound for Cap 3 streaming distinct from Doeblin-coefficient
bounds (D5 in meta-map adjacency list).

**Proto-drill question for exp_dev:**
Compute lambda_2 of substrate's W Laplacian at the Bet B operating point (N=4096, M=32768);
measure whether lambda_2 correlates with retention_A across 5 corpus pairs -- does higher algebraic
connectivity predict higher retention (r > 0.6)?

**Calibrated P(yields useful finding) = 0.38**
(base 0.50 for genuine 1-edge connection to drift-diffusion / AMP adjacency; deflated 0.12 for:
W is a weight matrix not a true graph adjacency, bipartite interpretation introduces distortions,
spectral sparsifiers require symmetric L but W is asymmetric Hebbian -- requires nontrivial
extension. Not novel-synthesis cap territory but non-trivial derivation.)

**Suggested drill type:** Theory anchor (~1 day Research) + cheap CPU (~1 hr) to measure lambda_2

---

## Candidate 3 -- Score-based diffusion model on substrate codewords (D6)

**Field:** Score-based generative models / diffusion models (Song-Ermon, Sohl-Dickstein, Ho DDPM)
**Prior drill count:** 0 (listed as D6 in meta-map Part 3 adjacency; never drilled; cost tag ~3 days)

**Framing (what the math does):**
Score-based models learn the score function s_theta(x) = nabla_x log p(x) of a data distribution;
reverse-time stochastic differential equation dx = [f(x,t) - g(t)^2 nabla_x log p_t(x)] dt + g(t)
dW generates samples from p_0 by running a noise-reversed Langevin chain. The denoising score
matching objective is: E[||s_theta(x_t) - nabla_{x_t} log p(x_t|x_0)||^2]. For discrete data,
Uniform/Absorbing masking diffusion (Austin et al.; Hoogeboom et al.; Gat et al.) gives a score
estimator over discrete tokens.

**Substrate mapping:**
Substrate's codeword space is DISCRETE ({-1,+1}^N BSC atoms). The substrate's argmax decoder IS a
denoising step: given noisy query y = w + epsilon, recover w via argmax_i <w_i, y>. This is
exactly a ONE-STEP score estimate at noise level ||epsilon||. For a learned or parametric noise
schedule adapted to the substrate's BSC channel, a MULTI-STEP score-based reverse-diffusion gives
a NEW erase primitive: instead of single-shot Crooks-certified erase, the score process iteratively
drives W toward a "no-memory" target distribution, with the path monitored via Crooks-style entropy
accounting. This is the ONLY proposed mechanism for a PROBABILISTIC progressive erase (vs current
binary pass/fail erase at Cap 1).

**Why capability-unlocking:**
(a) Extends Cap 1 verifiable erase from binary (erase/no-erase) to probabilistic progressive
(partial erase with quantified retention); (b) provides a NEW retrieval primitive (score-guided
multi-step cleanup) that could push multi-hop depth d beyond current d=500 envelope; (c) score
function on substrate codewords NATURALLY encodes the Parisi P(q) order parameter as the score
magnitude at each overlap level. Connects three load-bearing frameworks (Crooks FT, Parisi P(q),
VAMP readout) in a single generative model. No existing cap uses score-based reverse diffusion.

**Proto-drill question for exp_dev:**
Implement a 3-step discrete-mask diffusion (absorbing masking at rates p1/p2/p3) on substrate
atoms; measure whether 3-step denoising exceeds single-step argmax retrieval by > 2pp BPC on
Bet B operating point; HARD-PASS if delta_BPC > 2pp at N=4096.

**Calibrated P(yields useful finding) = 0.39**
(base 0.45 per meta-map adjacency list "3 days impl" cost tag and D6 proximity to load-bearing
drift-diffusion anchor; deflated 0.06 for: discrete-domain score functions require careful
adaptation from continuous-domain literature; multi-step schedule needs careful calibration to
substrate's BSC noise model. Not at novel-synthesis cap but implementation complexity is real.)

**Suggested drill type:** Theory anchor (~2 day Research for discrete score derivation) + GPU run
(~2-4 hr for multi-step denoising sweep)

---

## Candidate 4 -- Jarzynski equality / free-energy perturbation (A1)

**Field:** Non-equilibrium statistical mechanics -- Jarzynski identity, free-energy perturbation
**Prior drill count:** 0 (listed as A1 in meta-map Part 3 adjacency; labeled "Honorable mention"
in meta-map Part 4 "Honorable mentions"; never dispatched as a drill)

**Framing (what the math does):**
The Jarzynski equality (1997) states: <exp(-W/kT)>_non-eq = exp(-delta_F/kT), connecting
the EXPONENTIAL AVERAGE of work done in non-equilibrium processes to the FREE ENERGY DIFFERENCE
between end states. Unlike Crooks (which requires forward and reverse processes), Jarzynski uses
only the FORWARD process. The exponential average is an unbiased estimator of delta_F; with N
samples it gives delta_F with variance O(1/N) in the linear-response regime.

**Substrate mapping:**
Substrate's write operation performs work W = -<v, W*v> (inner product between atom vector v and
current W-weighted query v) against the background W. The Jarzynski estimator gives:
  delta_F = -kT log <exp(-W_write / kT)>
This is an UNBIASED ESTIMATOR of how much "free energy" the substrate consumes during a single
write -- directly observable from substrate's existing Hebbian update logs. Crooks FT (Cap 1
load-bearing) requires paired forward/backward runs; Jarzynski requires only forward. This opens
a CHEAPER capacity-utilization estimator: measure substrate's rho (fill level) via Jarzynski
without needing an explicit backward Crooks run.

**Why capability-unlocking:**
(a) Jarzynski gives an unbiased rho estimator (substrate capacity utilization) that is CHEAPER than
the current Crooks audit (no backward run needed) -- potential simplification of Cap 1 commercial
story; (b) Jarzynski variance <=> number of samples => gives a SAMPLE-COMPLEXITY BOUND on how many
write operations are needed to certify capacity -- a new KPI for the product story; (c) connects
to PAC-Bayes via the "exponential weight" estimator structure (Catoni's PAC-Bayes uses the same
change-of-measure; Jarzynski is the thermodynamic analog).

**Proto-drill question for exp_dev:**
Re-analyze 5 existing Cap 1 write trajectories using Jarzynski estimator (no new runs needed);
compute delta_F_Jarzynski and compare to Crooks-audited delta_F -- do the two estimators agree
within 15%? HARD-PASS if agreement holds across clean, mid-noise, high-noise conditions.

**Calibrated P(yields useful finding) = 0.45**
(base 0.50 per meta-map "Honorable mention" at P=estimated-A1; adjacency to Crooks FT which is
load-bearing and the strongest framework cluster; existing data can be re-analyzed (no new runs);
deflated 0.05 for: Jarzynski exponential mean has high variance under non-equilibrium conditions
far from equilibrium -- substrate's erase IS a non-equilibrium transition, variance may be large
enough to make the estimator noisy at practical N=4096)

**Suggested drill type:** Re-analysis of existing Cap 1 data (~30 min CPU + 1 day theory write-up)

---

## Candidate 5 -- Differential privacy / Renyi-DP composition for retention bounds

**Field:** Differential privacy (Dwork-McSherry-Nissim-Smith 2006; Renyi-DP Mironov 2017; GDP
Dong-Roth-Su 2022)
**Prior drill count:** 0 (Field-D in R-prime directions 2026-05-24; no drill delivered; mentioned
only at survey level)

**Framing (what the math does):**
A mechanism M satisfies (epsilon, delta)-DP if for any two datasets D, D' differing in one
element: P[M(D) in S] <= exp(epsilon) P[M(D') in S] + delta. Renyi-DP (Mironov 2017) uses the
Renyi divergence D_alpha: mechanism M satisfies (alpha, epsilon)-RDP iff D_alpha(M(D)||M(D')) <=
epsilon for all D, D'. Renyi-DP COMPOSES additively: k mechanisms each (alpha, epsilon)-RDP give
(alpha, k*epsilon)-RDP. GDP (Gaussian DP) gives the TIGHTEST composition for Gaussian mechanisms.

**Substrate mapping:**
Each task switch (Phase A -> Phase B) is a data access event that updates W by a Hebbian outer
product. Treating the Hebbian outer product W += v_k v_k^T as a DP MECHANISM (it releases a
function of the input v_k via W), each task's Renyi-DP budget is epsilon_k = ||v_k||^2 / (2 N
sigma^2) under Gaussian noise injection sigma. Composition over K tasks gives total budget
K * epsilon_k. When total budget exceeds a threshold, the mechanism no longer preserves individual-
task privacy -- meaning prior-task information (retention) is provably recoverable from W. This is
a LOWER BOUND on retention: tasks with small Renyi-DP budget are "hard to forget" (high retention)
and tasks with large budget are "easy to read out" (also high retention, for the task that used
the budget). Catastrophic forgetting = total DP budget being consumed unevenly across tasks.

**Why capability-unlocking:**
(a) Renyi-DP composition gives a CLOSED-FORM lower bound on retention_A across K tasks -- the
first information-theoretic floor for the Bet B retention ceiling that is both computable and
tight; (b) if substrate's measured retention tracks the DP lower bound, the product story becomes
"substrate achieves information-theoretically optimal retention" -- a strong commercial claim;
(c) Cap 1 verifiable erase connects naturally: post-erase W should achieve (epsilon=0, delta=0)-DP
for the erased task -- the DP certificate IS the erase certificate, potentially unifying Cap 1 and
Bet B into a single framework.

**Proto-drill question for exp_dev:**
Compute Renyi-DP composition budget for substrate's standard Bet B 3-task run (Phase A, B, C
sequential); predict retention_A lower bound from DP budget; compare to measured retention_A
across 5 seeds -- does retention_A >= predicted_floor within 10%?

**Calibrated P(yields useful finding) = 0.40**
(base 0.50 for Field-D R-prime filing, genuine mechanism connection, and DP composition being
well-understood math with closed-form tools; deflated 0.10 for: substrate's Hebbian update is
NOT a standard DP-compatible mechanism -- it's a DETERMINISTIC outer product, so the DP framing
requires injecting fictitious noise OR re-reading the existing PPMI sparsification as the noise
mechanism; this mapping requires nontrivial justification that hasn't been established.)

**Suggested drill type:** Theory anchor (~1-2 day Research for DP mechanism mapping) + re-analysis
of existing Bet B data (~30 min CPU)

---

## Candidate 6 -- Spectral / statistical population-coding maximum-entropy models (Tkacik-Bialek-Schneidman)

**Field:** Maximum-entropy population codes (Schneidman et al. Nature 2006; Tkacik-Bialek-
Marre-Berry-Segev; Ising model on neural spike patterns)
**Prior drill count:** 0 (not in advisor registry; not mentioned in any prior research note)

**Framing (what the math does):**
The maximum-entropy principle applied to binary neural population codes (Schneidman et al. 2006):
given only pairwise correlations <s_i s_j> as constraints, the maximum-entropy distribution is
an Ising model p(s) = exp(-H(s)) / Z with H(s) = -sum_{ij} J_{ij} s_i s_j - sum_i h_i s_i.
This is a pairwise maximum-entropy (PME) model. Tkacik et al. 2006 showed that for retinal ganglion
cells, the PME accounts for 90%+ of the multi-neuron entropy -- pairwise correlations EXPLAIN
population responses. The partition function Z = sum_s exp(-H(s)) is the same Ising partition
function from statistical physics; pseudolikelihood / TAP methods solve it efficiently.

**Substrate mapping:**
Substrate's BSC atoms are BINARY vectors -- directly a population of N binary "neurons." The PPMI
sparsification induces a CORRELATION STRUCTURE on atom co-activations. If the substrate's PPMI
co-occurrence statistics are fit by a PME Ising model, then J_{ij} = (the substrate's W matrix
restricted to pairwise couplings). The PME maximum-entropy constraint becomes the substrate's
LEARNING RULE: W += v v^T IS the moment-matching update that satisfies <s_i s_j>_W = <v_i v_j>.
This is a NEW theoretical justification for Hebbian learning as maximum-entropy inference -- the
substrate is learning the Ising model of the data distribution. Capacity bounds from Schneidman/
Tkacik's PME give substrate-novel predictions: the substrate can encode EXACTLY the pairwise
correlations of up to M_max = f(N, rho) atoms without exceeding the Ising partition function's
free-energy capacity.

**Why capability-unlocking:**
(a) PME framing gives a BIOLOGICAL GROUNDING for the Hebbian rule beyond "neural plausibility" --
it's theoretically optimal under the pairwise-maximum-entropy principle; (b) the Ising-partition-
function capacity bound is a NEW closed-form capacity estimator (distinct from Frady-Kleyko-Sommer
log2(M) <= N/(2 SNR) and from Hopfield 0.138N) specific to the substrate's PPMI correlation
structure; (c) the TAP / pseudolikelihood solvers for Ising models ARE the same TAP equations
in the substrate's observability suite (Family IV, TAP Sigma(f) probe -- listed as H2 in meta-map
but never fired) -- this would finally provide a USE CASE for the unfired TAP probe.

**Proto-drill question for exp_dev:**
Fit a PME Ising model to the substrate's PPMI atom co-occurrence statistics at N=4096; compute
the Ising capacity bound M_max from partition function Z at the substrate's operating temperature;
compare to empirical M/N=8 -- does PME predict M/N within factor 2?

**Calibrated P(yields useful finding) = 0.36**
(base 0.45 for genuinely new framing with published lit anchor (Schneidman Nature 2006 is
load-bearing neuroscience); adjacency to TAP probe (H2) already in the observability suite;
deflated 0.09 for: Schneidman 2006 applies to small populations (N~10-100 neurons); scaling
to N=4096 BSC atoms requires the TAP/pseudolikelihood to converge at high N -- Ising phase-
transitions at large N may dominate the PME fitting; and substrate's PPMI atoms are designed
to be UNCORRELATED (PPMI sparsification removes correlations) which could trivialize the PME.)

**Suggested drill type:** Theory anchor (~1-2 day Research for PME-Ising mapping derivation)
+ cheap CPU (~1 hr for TAP fitting at N=4096)

---

## Candidate 7 -- PAC-Bayes rate-distortion DEEPER (beyond KL-accumulation floor)

**Field:** Rate-distortion theory / PAC-Bayes generalization bounds (deeper than R-PRIME-1)
**Prior drill count:** 1 (R-PRIME-1 / 2026-05-24 math drill returned "structural verdict, no
constant-pinned bound"; the RATE-DISTORTION framing is orthogonal and undrilled)

**Framing (what the math does):**
Rate-distortion theory (Shannon 1959) gives the minimum description rate R(D) needed to reproduce
a source at distortion <= D: R(D) = min_{p(x_hat|x): E[d(x,x_hat)]<=D} I(X; X_hat). The
Blahut-Arimoto algorithm computes R(D) iteratively. For a SEQUENTIAL process (tasks arriving
one by one), the rate-distortion function quantifies: how much information must the substrate
TRANSMIT from the past to the future to maintain distortion (1 - retention) <= D on prior tasks?
Berger-Yeung (1999) gives the rate-distortion function for side-information settings (where future
tasks are known to the encoder) -- the W-matrix IS that side-information.

**Substrate mapping:**
The Bet B question (can substrate retain task A after learning B and C?) is a RATE-DISTORTION
question: W after learning A, B, C is the "compressed" representation of A; the retention rho_A
= 1 - distortion_A. The R(D) function gives the minimum W width (= rate = information stored per
atom) needed to achieve distortion D = 1 - rho_A. If actual substrate width N < N_min(D), retention
MUST fall below rho_A -- a theorem, not an empirical observation. This is STRONGER than PAC-Bayes
KL-floor because it uses Shannon's converse (operational lower bound), not just a change-of-measure
inequality.

**Why capability-unlocking:**
(a) R(D) bound gives a FUNDAMENTAL lower limit on how small N can be before retention of task A
falls below target -- the substrate's minimum size for a given use case; (b) the Blahut-Arimoto
algorithm can be RUN on substrate's actual PPMI statistics to compute the EMPIRICAL R(D) curve,
then compared to substrate's measured retention vs N curve -- if the two match, the substrate is
rate-distortion optimal; (c) if substrate IS rate-distortion optimal, the product claim becomes
"smallest possible N for any given retention target" -- a strong competitive differentiator.

**Proto-drill question for exp_dev:**
Run Blahut-Arimoto on substrate's PPMI bigram distribution at K=3 tasks; compute R(D) for
D = 1 - retention_A; predict minimum N(D) from R(D) curve; compare to empirical minimum N from
existing N-sweep runs -- does R(D) prediction agree with empirical N_min within 20%?

**Calibrated P(yields useful finding) = 0.37**
(base 0.45 for Shannon R(D) being a proven theorem (strongest possible anchor -- Berger-Yeung is
published 1999), adjacent to PAC-Bayes which showed structural relevance, and the Blahut-Arimoto
algorithm being standard; deflated 0.08 for: Blahut-Arimoto computes R(D) for the ENCODER side
but substrate's W is a FIXED linear readout, not an optimal encoder -- the R(D) bound is a lower
bound that the substrate may be far from achieving; and the "distortion" in multi-task retention
is not the standard MSE but a sequential-task version that requires multi-letter extension of R(D).)

**Suggested drill type:** Theory anchor (~2 day Research for sequential R(D) derivation) + cheap
CPU (~1 hr for Blahut-Arimoto on PPMI statistics)

---

## Priority ranking by calibrated P_deflated

| Rank | Field | P_deflated | Drill type | Cap potential |
|---|---|---|---|---|
| 1 | Entropic OT / Sinkhorn / Wasserstein | 0.42 | Theory + CPU smoke | Cap 13 new cert |
| 2 | Jarzynski equality / free-energy perturbation | 0.45 | Re-analysis (no new runs) | Cap 1 simplification |
| 3 | Score-based diffusion on substrate codewords | 0.39 | Theory + GPU | Cap 1 progressive erase |
| 4 | Differential privacy / Renyi-DP | 0.40 | Theory + re-analysis | Unify Cap 1 + Bet B |
| 5 | Spectral graph theory on W | 0.38 | Theory + CPU | Cap 9 (efficiency) |
| 6 | PME / Tkacik-Bialek population coding | 0.36 | Theory + CPU | TAP probe activation |
| 7 | Rate-distortion DEEPER (Blahut-Arimoto) | 0.37 | Theory + CPU | N_min product claim |

**Note on Jarzynski ranking**: P=0.45 (highest) but it's a re-analysis of existing data, not a
new experiment. It should ship as a Research-only theory anchor with exp_dev re-analysis, not as a
new queue entry. Ranked #2 for cost-adjusted priority but #1 for immediate actionability.

**Queue-refill guidance:**
- Next GPU slot: Score-based diffusion (Candidate 3) -- needs GPU, genuine new cap territory
- Next CPU slot: Entropic OT smoke (Candidate 1) or Spectral graph lambda_2 (Candidate 2)
- Next Research-only slot: Jarzynski re-analysis (Candidate 4) -- cheapest, no new data needed

---

*Filed 2026-05-26 by main-thread synthesis from advisor JSON + meta-map Part 3 adjacency +
research_new_fields_breadth_analysis_2026-05-24.md + research_new_continents_deep_drill_2026-05-24.md.*
