# Research: 3x Deep Drill -- Multi-Channel Gradient Orchestration Failure at Small Scale

**Date:** 2026-06-04
**Trigger:** Task prompt (orchestrator dispatch, 3x depth)
**Topic:** Why K=8 channel multi-objective gradient orchestration with learned precision weighting + PCGrad conflict projection fails to converge for ANY seed at ~10k-param char-LM scale
**Calibration note:** Per [[feedback-lit-scan-calibration-penalty]] -- all P estimates deflated 0.15-0.25; novel-synthesis cap 0.50

---

## HEADLINE

At ~10k parameter scale, K=8 channel multi-objective orchestration fails convergence due to a **compounding four-way binding**: (1) PCGrad cycle pathology drives gradient norm toward zero when K>4 channels form conflict cycles; (2) homoscedastic precision-weighting (sigma_k) collapses to suppress all non-dominant loss channels when loss magnitudes are heterogeneous across auxiliary signals; (3) total auxiliary machinery parameters (500-5000) constitute 5-50% of the base model, creating destructive shared-representation interference; (4) multi-channel neuromodulatory orchestration is empirically a **scale-dependent regime** -- biological systems operate it at 10^11 neuron / 10^15 synapse scale, which is 7-11 orders of magnitude above a 10k-param network. All four factors likely bind simultaneously, not sequentially.

---

## Five Sub-Questions: Algebraic Findings

### (1) MGDA / MOGD Convergence Conditions -- When Does K-Objective GD Converge?

**Core theorem (Desideri 2012 MGDA):** A Pareto stationary point x* satisfies: there exists no common descent direction d such that nabla_i f(x*)^T d < 0 for all i = 1..K simultaneously. MGDA finds the minimum-norm convex combination of task gradients:

    d* = argmin_{alpha in Delta_K} || sum_k alpha_k * g_k ||^2

If d* = 0, the algorithm has reached a Pareto stationary point (or is stuck at one). Under L-smooth objectives and full gradient computation, MGDA converges to a Pareto stationary point. Under stochastic gradients, convergence requires additional conditions (Sener-Koltun 2018 notes this as an open problem for their MGDA-based MTL framing; see also arxiv 2405.19440 for recent convergence under generalized smoothness).

**Critical failure mode for K=8 at small scale:** The Pareto stationary condition becomes harder to escape as K grows. With K=8 objectives, the convex hull of {g_1, ..., g_8} has higher dimensionality, and the minimum-norm combination can be the zero vector without any single objective being at its minimum. This is the "false Pareto stationarity" problem -- the optimizer finds a point where no shared descent exists, even though each individual loss is far from converged. At small N (~10k params), the shared parameter space is highly constrained, making this false-stationarity trap more likely because the geometry of the loss landscape cannot accommodate 8 simultaneously-descending directions in low-dimensional parameter space.

**Algebraic bound (informal):** For K objectives with conflicting gradients in R^p parameter space, a conflict-free common descent direction requires: the intersection of the K half-spaces {d : g_k^T d < 0} to be non-empty. By a simple counting argument, when K approaches the effective rank of the gradient matrix (which is bounded by min(K, p)), the probability of a non-empty intersection decays. At p~10k and K=8 with correlated auxiliary losses, effective rank may be low (2-4), making empty-intersection likely.

**P (convergence of K=8 MOGD at 10k-param scale):** P_deflated = 0.15 -- convergence to a useful Pareto point is unlikely at this scale without gradient space regularization.

---

### (2) PCGrad Cycle Pathology -- Algebraic Norm Collapse

**PCGrad projection (Yu et al. 2020 NeurIPS):** For tasks i, j with g_i . g_j < 0 (conflicting inner product):

    g_i^{proj} = g_i - (g_i . g_j / ||g_j||^2) * g_j

The projected gradient has norm:

    ||g_i^{proj}||^2 = ||g_i||^2 - (g_i . g_j)^2 / ||g_j||^2

Since (g_i . g_j)^2 / ||g_j||^2 = ||g_i||^2 * cos^2(theta_{ij}), this simplifies to:

    ||g_i^{proj}||^2 = ||g_i||^2 * sin^2(theta_{ij})

**Observation 1 -- Near-antiparallel collapse:** When g_i and g_j are nearly antiparallel (theta ~= pi, cos ~= -1), sin^2 ~= 0, so ||g_i^{proj}|| ~= 0. If multiple channel pairs are near-antiparallel, each projection drives toward zero.

**Observation 2 -- Cyclic conflict compounding:** PCGrad applies K projections sequentially for each task gradient. If g_1 conflicts with g_2, g_2 conflicts with g_3, ..., g_7 conflicts with g_8, and g_8 conflicts with g_1 (conflict cycle of length K=8), then after sequential projections, the resultant gradient for task 1 undergoes: proj onto normal of g_2, then the result is projected onto normal of g_3, etc. If each projection reduces norm by factor sin(theta_k), the final norm scales as:

    ||g_1^{final}|| ~ ||g_1|| * prod_{k=2}^{K} sin(theta_{1k})

For K=8 channels with average conflict angle theta = 120 degrees (common in antagonistic multi-objective settings), sin(120) = sqrt(3)/2 ~ 0.866, so:

    product over 7 projections: 0.866^7 ~ 0.37

But for K=8 channels with stronger conflicts (theta ~ 150 degrees, sin = 0.5):

    0.5^7 ~ 0.0078 -- effective gradient collapse by factor ~128

**Observation 3 -- Sparse gradient regime:** If auxiliary loss signals are computed on rare events (phasic signals fire infrequently), most steps have sparse gradients. PCGrad projections over near-zero vectors amplify noise and produce near-zero results with unpredictable sign.

**PCGrad theory limitation (Yu et al. 2020):** PCGrad is proved to reduce "PCGrad conflict" (the sum of negative inner products) but has NO theorem guaranteeing convergence to a Pareto stationary point. Liu et al. (CAGrad, 2021) showed PCGrad can fail to converge when gradient conflicts are cyclic and noted it is a heuristic without convergence guarantee. GCond (2025, arxiv 2509.07252) further identifies PCGrad's hard projections as "nullifying useful gradient components."

**Diagnosis for K=8:** Four tonic + four phasic channels are almost certainly in conflict (tonic and phasic signals represent competing modulation directions by design). The resulting cyclic conflict graph likely contains cycles of length 4-8, driving norm collapse by factor ~10-128 per step when phasic gradients are sparse.

---

### (3) sigma_k Precision-Weighting: Saturation and Collapse

**Cipolla / Kendall-Gal 2018 loss formulation:** For K tasks with homoscedastic uncertainty sigma_k > 0:

    L_total = sum_k [ (1/sigma_k^2) * L_k + log(sigma_k) ]

Optimizing over sigma_k at fixed L_k: dL/d(sigma_k) = -2*L_k/sigma_k^3 + 1/sigma_k = 0 => sigma_k^2 = 2*L_k

So at the optimal sigma_k, the task weight (1/sigma_k^2) = 1/(2*L_k). Tasks with larger loss receive LOWER weight -- this is the intended regularization.

**Failure mode 1 -- Dominance collapse:** If the primary language model loss is 10-100x larger than auxiliary losses, the optimizer drives sigma_{primary} large (to reduce its weight) and sigma_{aux,k} small (to increase auxiliary weights). But small sigma_k means 1/sigma_k^2 -> infinity, which drives those auxiliary gradients to dominate, creating an oscillatory regime where the optimizer alternately suppresses primary and auxiliary channels.

**Failure mode 2 -- Degenerate collapse to sigma_k -> infinity:** For tasks where L_k approaches zero (or near-zero, as may occur when a phasic signal rarely fires), the optimal sigma_k -> infinity, driving task weight 1/sigma_k^2 -> 0. The log(sigma_k) regularizer grows without bound, creating a runaway positive feedback: near-zero loss -> large sigma -> near-zero weight -> task no longer contributes to parameter updates -> task stays near-zero loss -> sigma grows further. With 4 phasic channels that fire rarely, all four sigma_k values can diverge simultaneously.

**Failure mode 3 -- Precision oscillation:** The sigma_k parameters are trained by gradient descent simultaneously with the main model parameters. If sigma_k updates are coupled to noisy loss signals (rare-event phasic losses), precision values oscillate at a timescale faster than model parameters can adapt. This instability is distinct from static weight mistuning -- it is a coupled oscillator pathology. Liebel-Korner 2018 and the 2025 analytical uncertainty paper (arxiv 2408.07985) identify this as a core practical failure mode.

**Key algebraic observation:** With K=8 tasks, 4 of which are phasic (event-triggered, therefore intermittent), the L_k for phasic channels has high variance over mini-batches. The learned sigma_k cannot track this variance without dedicated momentum / EMA stabilization. Gradient updates to sigma_k alternate between large-loss updates (when the event fires) and near-zero-loss updates (when it does not), creating a bimodal sigma_k update distribution that prevents convergence.

**P(sigma_k stabilizes at K=8 with 4 intermittent channels):** P_deflated = 0.20. Intermittent phasic losses are structurally incompatible with the Cipolla formulation unless sigma_k is EMA-smoothed with a long window (>>batch frequency of phasic events).

---

### (4) Capacity Bottleneck: Auxiliary Machinery vs. Model Size

**Parameter budget analysis:**
- Base char-LM: ~10k parameters
- 8x sigma_k scalars: 8 params (trivial)
- PCGrad: 0 learnable params, but K^2 = 64 dot-product + projection operations per step
- Layer-zone gain: 4 layers x 8 channels = 32 params
- If sigma_k uses an MLP estimator per task: 8 x ~100-500 params = 800-4000 params
- Total auxiliary: 840-4040 params = **8-40% of base model**

**Destructive interference at small capacity:** The Stanford Hazy Research MTL analysis (2020) and theoretical work on shared-module capacity state explicitly: when the shared module capacity is too small, there is destructive interference between tasks -- each task's gradient updates perturb the shared representation in directions that harm other tasks. At 10k params shared across 8 objectives, the effective per-task capacity is ~1250 params, which is below the threshold for independent task learning in a char-LM even for the PRIMARY task alone.

**Formal capacity insufficiency argument:** Let W be the shared parameter matrix. For the primary task with effective information content H_1 bits and auxiliary tasks with collective information content H_aux bits: if params(W) < H_1/efficiency, the primary task underfits. Adding 8 auxiliary signals each with their own gradient contribution does not increase model capacity but does increase the gradient noise applied to those same params. The signal-to-noise ratio for any single gradient direction scales as 1/K in the worst case (uniform conflict), so at K=8, gradient SNR is 1/8 of single-task learning.

**P(K=8 auxiliary orchestration helps at 10k-param scale):** P_deflated = 0.12. Capacity analysis strongly predicts negative transfer dominating any positive auxiliary signal.

---

### (5) Scale-Dependence: Multi-Channel Neuromodulation as a Scale-Gated Regime

**The biological analogy gap:** The brain operates ~10^11 neurons with ~10^15 synaptic weights. A 10k-param char-LM has ~10^4 parameters. The ratio is 10^11. Neuromodulatory precision weighting in the brain (Friston 2009 free-energy; Yu-Dayan 2005 ACh; Schultz 1997 dopamine RPE) works via:

- **Dedicated modulator circuits** separate from the signal-processing network: basal ganglia, locus coeruleus, and VTA are distinct parameter banks, not shared with the cortical computation
- **Hierarchical precision allocation** at multiple timescales simultaneously (fast phasic ~50ms; slow tonic ~minutes) in a high-dimensional embedding space
- **~10^8-scale modulatory neurons** modulate 10^11-scale signal neurons: the ratio of modulator to signal is ~1:1000

In a 10k-param model, attempting to replicate this architecture means: 8 modulator channels on ~10k shared parameters. There is no separation of modulator vs. signal capacity. ALL gradient updates from all 8 channels act on the same 10k weights simultaneously.

**Algebraic scale argument:** Let p_s = signal parameters, p_m = modulator parameters. In the brain, p_m/p_s ~ 10^8/10^11 = 10^-3. In a 10k-param model with ~40 modulator params (sigma_k + zone gains), p_m/p_s ~ 40/10000 = 4x10^-3. The ratio is superficially comparable. But the absolute capacity p_s is the binding constraint: the brain's cortex can maintain 10^11-dimensional subspaces for each channel without interference. A 10k network cannot maintain even 2 orthogonal task subspaces at meaningful capacity, let alone 8.

**Free-energy / precision-weighting theory (Friston):** Precision weighting in the brain functions as a FILTERING mechanism on prediction error signals that are themselves computed in a high-dimensional space. At small scale, there is nothing meaningful to filter -- the prediction error space is too low-dimensional for precision-based channel selection to have discriminative power.

**P(multi-channel orchestration works below 100k params):** P_deflated = 0.10. The literature strongly suggests this is a scale-gated regime. Below ~100k params, the machinery cost dominates the signal benefit.

---

## BINDING ORDER: Which Sub-Question Binds First?

Based on the algebraic analysis, the binding order at K=8, ~10k params is:

**1st binding: PCGrad cycle pathology + gradient norm collapse (Sub-Q 2)**
- Acts immediately from step 1 of training
- Compounding 7-projection norm reduction by factor ~10-128 (angle-dependent)
- Produces near-zero effective gradients for most channels most of the time
- This alone is sufficient to prevent convergence

**2nd binding: sigma_k collapse for phasic channels (Sub-Q 3)**
- Phasic signals (event-triggered) have intermittent loss signals
- sigma_k for phasic channels diverges (failure mode 2 above) within first 100-500 steps
- Even if PCGrad is fixed, sigma_k collapse would prevent auxiliary signal from reaching the model

**3rd binding: Capacity bottleneck + negative transfer (Sub-Q 4)**
- Acts over longer training horizon (not immediate)
- Even if gradient orchestration were perfect, 8 tasks on 10k params produces destructive interference
- Degrades primary task below single-task baseline

**4th binding: Scale-dependence (Sub-Q 5)**
- Fundamental but slowest to manifest
- Would prevent the regime from ever working even with perfect engineering fixes at this scale
- Suggests 100k+ params as minimum threshold

**Sub-Q 1 (MGDA convergence theorems):** Not directly binding because the implementation uses PCGrad rather than MGDA; however, the false-Pareto-stationarity analysis predicts why even a fixed PCGrad would stall in high-K low-p regimes.

---

## Recommended Design Changes (Ranked by Likely Impact)

### R1 -- Scale first (highest leverage)
Scale model to 100k-500k parameters before reintroducing multi-channel orchestration. This single change addresses binding constraints 3 and 4 simultaneously, and partially relaxes constraint 2 (higher-dimensional gradient space reduces probability of full-cycle conflict).

**Why before anything else:** The capacity bottleneck and scale-dependence analyses show the architecture is fundamentally operating below the regime where multi-channel modulation provides benefit. Fixing gradient mechanics (PCGrad, sigma_k) without addressing scale will produce a system that converges but provides no benefit over single-task learning.

### R2 -- Channel pruning to K=2-3 most-orthogonal channels
Apply Gram-Schmidt or PCA to the K=8 gradient vectors during a burn-in phase to identify the 2-3 channels with near-orthogonal gradient directions. Drop the remainder.

**Algebraic justification:** With K=2 near-orthogonal channels (cos(theta) ~ 0), PCGrad projection leaves norm almost unchanged (sin(90) = 1.0). With K=2, no conflict cycles are possible. The sigma_k optimization landscape has a unique minimum for 2 channels. Negative transfer reduces to a two-task problem with known solutions.

**Practical protocol:** Run 100 steps of training with K=8, compute the K x K gradient correlation matrix G_{ij} = E[g_i . g_j / (||g_i|| ||g_j||)], select the 2-3 channels with lowest mean |G_{ij}| (most orthogonal), discard the rest.

### R3 -- Replace PCGrad with naive gradient sum or MGDA
For K <= 4 channels, replace PCGrad with: (a) simple gradient sum (baseline, no projection overhead), or (b) MGDA minimum-norm combination.

**Why:** PCGrad has no convergence guarantee and produces the compounding norm-collapse failure described above. MGDA has convergence guarantees to Pareto stationary points under smoothness conditions (arxiv 2405.19440). NashMTL (Navon et al. ICML 2022) provides the strongest guarantees (Pareto-front coverage + scale invariance) but at higher computational cost (quadratic program per step). For K=2-3, simple gradient sum is often competitive with projection methods.

### R4 -- sigma_k initialization and stabilization protocol
If Cipolla-style weighting is retained:
- Initialize log(sigma_k^2) = log(L_k_init) where L_k_init is the expected initial loss for task k
- Apply EMA smoothing to the loss signal used for sigma_k updates: L_k_ema = 0.99 * L_k_ema + 0.01 * L_k_batch
- Clip sigma_k to [sigma_min, sigma_max] = [0.01, 100] to prevent divergence
- Use separate learning rates for sigma_k vs. main model params: lr(sigma) ~ 0.01 * lr(model)

### R5 -- Decouple phasic and tonic channels architecturally
Do not mix phasic (event-triggered, sparse) and tonic (always-on) channels in a single sigma_k optimization. Treat them as separate optimization problems:
- Tonic channels: standard Cipolla weighting, update every step
- Phasic channels: fixed weight (not learned), activated only when event occurs, accumulated via gradient EMA over event window

**Justification:** The Cipolla formulation assumes all tasks provide signal at every step. Phasic tasks violate this assumption. Separating them prevents sigma_k collapse failure mode 2.

---

## Cheap Decisive Test

**Pre-registered ablation sequence (algebraic predictions, no empirical verification):**

1. Run K=1 (primary task only): should converge. If not, architecture issue unrelated to multi-channel orchestration.
2. Run K=2 (primary + single most-orthogonal tonic channel, naive gradient sum): predicted to converge with >80% seed success at 10k params.
3. Run K=2 with PCGrad: predicted to converge at similar rate to K=2 naive sum (since two channels = one potential conflict, no cycle pathology).
4. Run K=4 (primary + 3 channels, MGDA): predicted 40-60% seed convergence rate at 10k params; PCGrad failure modes begin here.
5. Run K=4 at 100k params: predicted 60-80% seed convergence.
6. Run K=8 at 100k params with R1-R5 fixes: predicted 40-60% seed convergence.

---

## Falsifiable Predictions: HARD-PASS / HARD-FAIL

### HARD-PASS thresholds (pre-registered)
- HP1: K=2 (primary + 1 tonic channel, naive gradient sum, 100k params) converges all 3 seeds, primary task loss below K=1 single-task baseline. P_deflated = 0.60.
- HP2: K=4 (4 most-orthogonal channels, MGDA, 100k params) converges 2/3+ seeds with primary loss within 5% of K=1 baseline. P_deflated = 0.45.
- HP3: Gradient correlation matrix analysis shows fewer than 3 of 28 channel pairs with cos(theta) < -0.3. P_deflated = 0.35.

### MIDDLE BAND
- MID1: K=2 converges at 10k params but primary loss is worse than K=1 (negative transfer confirmed at small scale). P = 0.55.
- MID2: K=4 at 100k params converges but provides no lift over K=1; auxiliary channels carry near-zero gradient weight.

### HARD-FAIL thresholds (pre-registered)
- HF1: K=2 (naive gradient sum, no PCGrad) fails to converge at 100k params for all 3 seeds. This would indicate a deeper architecture bug unrelated to the four failure modes identified here.
- HF2: sigma_k values for all phasic channels diverge (|log sigma_k| > 5 within 500 steps) even after EMA smoothing fix. This would refute the intermittent-loss hypothesis.
- HF3: Gradient correlation matrix shows K=4 channels all with near-zero cross-correlation despite measuring different auxiliary objectives. This would refute the cycle-pathology hypothesis.

**P_deflated overall for "multi-channel orchestration works at small scale with minimal redesign (K=8, ~10k params)": 0.05-0.08** -- near-zero; all four failure modes bind simultaneously.

**P_deflated for "multi-channel orchestration works at moderate scale (K=4, ~100k params) with R1-R5 fixes applied": 0.40-0.50** -- viable with careful engineering; convergence likely but benefit over single-task baseline uncertain.

---

## Cross-Domain Probe: Meta-Learning (MAML/Reptile) and Evolutionary Strategies

### MAML/Reptile as anchor for multi-objective convergence

**Algebraic connection:** MAML (Finn et al. 2017) optimizes theta such that a single gradient step from theta reaches a good solution for many tasks simultaneously. The meta-update is:

    theta <- theta - beta * sum_k nabla_theta L_k(theta - alpha * nabla_theta L_k(theta))

This is structurally similar to the K-channel orchestration problem: both seek a shared parameter state from which K objectives can be jointly satisfied. The key MAML insight is that the meta-loss is a SCALAR (sum over tasks), not a multi-objective problem -- this is why MAML converges when naive multi-objective GD does not.

**Reptile (Nichol et al. 2018):** Reptile avoids second-order terms and approximates the meta-update as: theta <- theta + sum_k (theta_k_star - theta), where theta_k_star is the per-task fine-tuned solution. The convergence proof relies on tasks sharing a common "center of mass" in parameter space. This is algebraically equivalent to assuming low gradient conflict.

**Direct relevance:** For a K-channel auxiliary loss system, the MAML framing suggests reinterpreting the problem as: find theta such that each auxiliary task can be well-solved with a SMALL additional update (like MAML's inner loop). This naturally limits the conflict: each auxiliary channel only needs to point "somewhere useful from theta," not simultaneously at its own global minimum. This is mechanistically different from PCGrad (which tries to satisfy all objectives simultaneously in each step) and may be more tractable at small scale.

**Practical transfer:** Replace the K-channel simultaneous optimization with: (1) take a primary-task gradient step, (2) take ONE auxiliary-channel gradient step (round-robin through K channels), (3) repeat. This is a sequential multi-task update (analogous to Reptile task sampling) that avoids all gradient conflict by construction, at the cost of slower auxiliary task convergence. For K=8 at 10k params, this may be the only regime that converges.

### Evolutionary Strategies as gradient-conflict-free alternative

**ES (Salimans et al. 2017):** ES has no gradient computation and therefore no gradient conflict by construction. Multi-objective ES using Pareto-dominance ranking sidesteps the PCGrad pathology entirely.

**ES convergence:** Guaranteed under mild conditions (Beyer ES analysis). Sample complexity scales as O(p / sigma^2) where p is parameter count. For p=10k, this is tractable.

**Recommendation:** ES is a viable diagnostic tool: run ES-based K=8 multi-objective optimization as a baseline. If ES converges where gradient methods fail, this confirms the failure is in gradient mechanics (PCGrad + sigma_k) rather than in the loss landscape itself. If ES also fails to improve over single-task, this implicates the capacity bottleneck / scale-dependence as the binding constraint.

---

## Cross-Thread Synthesis

- **Spin-glass / false Pareto stationarity:** The false-Pareto-stationarity trap (Sub-Q 1) is algebraically analogous to the spurious local minima in Hopfield energy landscapes. Both involve a system finding a low-gradient-norm state that is not the global optimum. The SKAH-M substrate work (memory: project_substrate_skahm_class_confirmed) is relevant: multi-basin hierarchical energy landscapes are the substrate's strength, and the same geometry that creates retrieval capacity also creates false-stationarity traps for gradient-based optimization ON the substrate.

- **Precision weighting + substrate:** The Friston free-energy / precision-weighting framework is the theoretical parent of both the Cipolla sigma_k formulation and the substrate's neuromodulatory design. The failure of sigma_k at small scale reinforces that precision weighting is a high-dimensional phenomenon -- it requires enough capacity to meaningfully differentiate prediction-error precision across channels.

- **PCGrad pathology + gradient orthogonality:** The gradient correlation matrix analysis recommended in R2 is a cheap test that would also validate the substrate's channel orthogonality assumptions. If auxiliary loss gradients are highly correlated with the primary loss gradient, the substrate design has a fundamental dependency problem regardless of scale.

---

## Substrate-Product Implications

1. **Defer multi-channel orchestration to >= 100k param models:** The auxiliary orchestration machinery should be validated first at a scale where the capacity bottleneck is not binding.

2. **Channel orthogonality is a first-class design constraint:** Before deploying K>2 auxiliary channels, compute the empirical gradient correlation matrix across 100 training steps. Reject any channel pair with |cos(theta)| > 0.3 (too correlated) or cos(theta) < -0.3 (too conflicting).

3. **Phasic channels require separate convergence infrastructure:** The sigma_k formulation is not compatible with event-triggered losses without EMA smoothing + clipping. Any product implementation of phasic modulation must separate the precision-weighting update from the event occurrence.

4. **MAML-style sequential update as default for K>4:** For K>4 auxiliary channels at any scale, the round-robin sequential update (Reptile analog) provides a convergence guarantee that PCGrad lacks.

5. **ES as diagnostic baseline:** Before re-running gradient-based K=8 experiments at any scale, run an ES baseline (population=50, 200 steps) to determine whether the loss landscape supports multi-objective improvement. If ES fails, problem is capacity/scale; if ES succeeds, problem is gradient mechanics.

---

## Citations (Verified: 18 sources)

1. Desideri J-A (2012). Multiple-gradient descent algorithm (MGDA) for multiobjective optimization. CRAS 350(5-6):313-318. https://www.sciencedirect.com/science/article/pii/S1631073X12000738

2. Sener O, Koltun V (2018). Multi-task learning as multi-objective optimization. NeurIPS 2018. arxiv 1810.04650.

3. Yu T, Kumar S, Gupta A et al. (2020). Gradient surgery for multi-task learning. NeurIPS 2020. arxiv 2001.06782. https://proceedings.neurips.cc/paper/2020/file/3fe78a8acf5fda99de95303940a2420c-Paper.pdf

4. Kendall A, Gal Y, Cipolla R (2018). Multi-task learning using uncertainty to weigh losses. CVPR 2018. arxiv 1705.07115. https://openaccess.thecvf.com/content_cvpr_2018/papers/Kendall_Multi-Task_Learning_Using_CVPR_2018_paper.pdf

5. Liu B et al. (2021). Conflict-averse gradient descent for multi-task learning (CAGrad). NeurIPS 2021.

6. Navon A et al. (2022). Multi-task learning as a bargaining game (NashMTL). ICML 2022. arxiv 2202.01017. https://arxiv.org/abs/2202.01017

7. Finn C, Abbeel P, Levine S (2017). Model-agnostic meta-learning (MAML). ICML 2017. arxiv 1703.03400.

8. Nichol A, Achiam J, Schulman J (2018). On first-order meta-learning algorithms (Reptile). arxiv 1803.02999.

9. Salimans T et al. (2017). Evolution strategies as a scalable alternative to reinforcement learning. OpenAI arxiv 1703.03864.

10. Lin X et al. (2019). Pareto multi-task learning. NeurIPS 2019.

11. Friston K (2009). The free-energy principle: a rough guide to the brain. Trends in Cognitive Sciences 13(7):293-301.

12. Yu AJ, Dayan P (2005). Uncertainty, neuromodulation, and attention. Neuron 46(4):681-692.

13. Schultz W (1997). A neural substrate of prediction and reward. Science 275(5306):1593-1599.

14. arxiv 2405.19440 (2024). MGDA converges under generalized smoothness, provably.

15. arxiv 2408.07985 (2024). Analytical uncertainty-based loss weighting in multi-task learning. https://arxiv.org/html/2408.07985v1

16. GCond (2025). Gradient conflict resolution via accumulation-based stabilization. arxiv 2509.07252. https://arxiv.org/html/2509.07252v1

17. Hazy Research Stanford (2020). When multi-task learning works -- and when it does not. https://hazyresearch.stanford.edu/blog/2020-03-01-multi_task_transfer_learning

18. Liebel L, Korner M (2018). Auxiliary tasks in multi-task learning. arxiv 1805.06334.

---

*Note written by research sub-agent 2026-06-04. Calibration penalty applied throughout. P estimates deflated 0.15-0.25; novel-synthesis cap 0.50. Algebraic + lit-scan only; no empirical verification performed.*
