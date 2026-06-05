# Research Drill: Bipolar-Compatible Alternative Write Rules (2x Depth)
# Topic: Alternative write rules for bipolar discrete-state associative memory beyond Hebbian outer-product
# Date: 2026-06-05
# Drill level: Level-2 operational (not re-verification)
# Calibration: P_deflated = P_raw - 0.20 (uncharted bipolar-PC regime); novel-synthesis cap 0.50

---

## HEADLINE

No known write rule promotes a bipolar discrete-state associative memory above conditional-bigram class for sequence prediction while simultaneously preserving all four structural moats (cert, real-time write, AC0/TC0 retrieval, bipolar storage). The predictive coding residual write is the closest approach: it reaches conditional-bigram from co-occurrence-bigram while preserving retrieval complexity and real-time feasibility, but the bipolar constraint forces a shadow-weight architecture that breaks cert determinism unless cert is lifted to the shadow layer. All write rules that reach higher Markov order (modern Hopfield, SDM trace, gated attention) require either continuous weights, multi-pass retrieval (TC0+ or PSPACE), or iterative consolidation, breaking at least one of the four moats. Verdict: OUTCOME B, with one partial-rescue path.

---

## SUB-QUESTION 1: Predictive Coding Residual Write Under Bipolar Constraint

### Standard formula (real-valued)

    W_{t+1} = W_t + eta * (y - W_t * x) * x^T

where x = phi(c_t), y = phi(c_{t+1}), W in R^{NxN}.

### Algebraic capacity analysis

Hebbian outer-product write accumulates co-occurrence counts: W = sum_t phi(c_t) outer phi(c_{t+1}), which yields capacity M_max ~ 0.138*N for random patterns (Hopfield 1982 result). The retrieval signal-to-noise at the query step satisfies:

    SNR = (phi(c_{t+1}) dot W * phi(c_t)) / sigma_noise
        = M / (N * sigma_noise)  [leading-order]

so M_max = O(N) at SNR = 1.

The PC residual write subtracts the already-stored projection before adding the new pair. This is equivalent to the perceptron convergence update applied to the weight matrix column by column. For the sequence prediction task:

- After T writes, W approximates the conditional expectation E[phi(c_{t+1}) | phi(c_t)] more accurately than pure outer-product accumulation.
- The residual term (y - W*x)*x^T orthogonalizes new associations against already-stored directions.
- Algebraic class: This is conditional-bigram (first-order Markov), NOT higher-order Markov, because the stored state is still a flat N x N weight matrix. The rank of W is bounded by min(M, N); no higher-order conditional structure is encoded.
- Capacity improvement: PC residual improves the effective storage by suppressing cross-talk. Asymptotically M_max ~ O(N) still (not improved), but the constant is better and the error floor is lower for correlated sequences.

P_raw = 0.72 (PC residual improves sequence prediction quality over Hebbian at same M/N).
P_deflated = 0.52 (calibration: no published direct test on bipolar substrate).

### Bipolar constraint options

**Option A: Quantized accumulation (shadow-W)**

Maintain W_shadow in R^{NxN}; after each update, W_bipolar = sign(W_shadow).

- Capacity: Preserved at O(N). The binarization introduces quantization noise floor ~1/N per entry but does not change the capacity scaling class.
- Cert compatibility: BROKEN for the bipolar layer. The cert chain relies on deterministic read of W_bipolar; but W_bipolar is now a lossy projection of W_shadow. The algebraic certificate for "fact X is stored" is: hash(W_bipolar) contains trace of outer(phi_A, phi_B). After shadow projection, this trace is stochastic at the bit level for small eta updates. RESCUE: Move the cert chain to W_shadow (real-valued). This preserves determinism of cert but requires storing W_shadow, which is not bipolar. The bipolar constraint is then only on the inference-time weight, not the write-log. This is architecturally consistent IF the product stores W_bipolar for inference and W_shadow for audit. Cost: 32x memory overhead for shadow layer.
- Real-time write: Shadow update is O(N^2) per token; bipolar projection sign() is O(N^2). Sub-ms feasible at N=4096 (16M ops at ~1 GFLOP/s single-thread = ~16ms; GPU N=4096 W_shadow update ~0.1ms). Tight but feasible.
- Complexity class: Retrieval from W_bipolar is threshold(W_bipolar * query), a matrix-vector multiply + threshold = TC0 (can be computed in constant depth with threshold gates). Preserved.

**Option B: Stochastic rounding**

Each PC residual update flips W_bipolar[i,j] with probability proportional to |residual[i,j]| / max_residual.

- Capacity: Gupta et al. (2015) proved stochastic rounding preserves unbiased gradient estimates. For associative memory: the expected W_bipolar after T updates converges to sign(W_shadow), so expected capacity is O(N). Variance adds a noise term ~1/T per entry.
- Cert compatibility: BROKEN for individual entries. Stochastic flips mean the cert cannot deterministically reconstruct whether a specific fact X was stored -- the bit may have been flipped by a different write. RESCUE: Maintain a probabilistic audit trail (log of (i,j,flip_probability)) as the cert. This gives a Bayesian cert, not a deterministic cert. Breaks the sub-millisecond cryptographic audit property because audit now requires probabilistic inference over the log.
- Real-time write: O(N^2) + random number generation per entry = feasible but slower than deterministic rounding.
- Complexity class: Retrieval is still TC0. Write is not TC0 (requires RNG, which is not in AC0/TC0).

**Option C: Block-sparse residual (flip only top-k entries)**

- Capacity: Equivalent to shadow-W with a sparsification step. Capacity ~O(N) but with sparser updates; convergence to E[phi(c_{t+1}) | phi(c_t)] is slower.
- Cert: Same issue as Option A; sparse flips are deterministic given the threshold, so cert can be reconstructed if threshold is logged. PARTIAL cert preservation.
- Real-time write: O(N^2) forward pass + O(k) flip = feasible. k << N^2 makes this fast.
- Complexity class: TC0 for retrieval. Write requires sorting (to find top-k) = O(N^2 log N), which exceeds simple TC0 but is still poly-time.

**Option D: Sign-only update**

    W_bipolar[i,j] = W_bipolar[i,j] XOR (sign(residual[i,j]) != sign(W_bipolar[i,j]))

Flip entry if sign of residual disagrees with current weight sign.

- Capacity: Loses magnitude information. Convergence to conditional expectation is slower and may oscillate. Effective capacity is lower than shadow-W; the magnitude weighting that makes PC residual effective is discarded.
- Cert: Deterministic (XOR is deterministic); cert chain is preserved.
- Real-time write: O(N^2) comparisons; pure bitwise operation, extremely fast.
- Complexity class: TC0 retrieval preserved.

### Summary for Sub-Q 1

Best option under all-four-moat constraint: **Option D (sign-only update)** for cert preservation + bipolar constraint, with the caveat that magnitude is lost and convergence degrades. **Option A (shadow-W)** is best for capacity and convergence quality but requires cert to be lifted to the shadow layer. No option delivers all four moats simultaneously without compromise.

Cert moat is the bottleneck, not retrieval complexity or write speed.

---

## SUB-QUESTION 2: Hawkes-Process Surprise-Weighted Write Under Bipolar Constraint

### Formal write rule

    W += eta * surprise(t) * outer(phi(c_t), phi(c_{t+1}))

where surprise(t) = -log P(c_{t+1} | history).

### Surprise estimation options

**Option A: External n-gram surprise estimator**

Use a lightweight bigram count table (separate from W) to estimate P(c_{t+1} | c_t). surprise(t) = -log count(c_{t+1} | c_t) / count(c_t).

- Algebraic capacity: The write rule is a surprise-reweighted outer-product. The capacity of W is still O(N) (same rank bound). Rare events are written with higher weight; frequent events are downweighted. This improves sequence prediction quality on heavy-tailed distributions by allocating capacity preferentially to surprising transitions.
- Capacity class: Conditional-bigram. The weight matrix W still maps single input vectors to output vectors; no higher-order Markov structure is encoded.
- Cert compatibility: Deterministic surprise weights are computable from the count table. If the count table is part of the audit record, cert is preserved. Write rule is: W_bipolar = sign(W_shadow + eta * surprise * outer(phi_t, phi_{t+1})), same shadow-W cert issue as Sub-Q 1 Option A.
- Real-time: O(N^2) write + O(1) bigram lookup. Feasible sub-ms at N<=1024; tight at N=4096.
- Complexity class: TC0 retrieval. Write is TC0 if surprise is precomputed.

P_raw = 0.65 (surprise weighting improves quality on heavy-tailed sequences over flat Hebbian).
P_deflated = 0.45.

**Option B: Substrate confidence as surprise proxy**

    surprise(t) = 1 - cosine(W * phi(c_t), phi(c_{t+1}))

Circular but self-consistent if initialized from a prior write pass.

- Algebraic: Same capacity class. Converges to minimum-surprise state (high-confidence writes dominate), which may suppress rare-but-important transitions. Opposite behavior from Option A.

**Option C: Temporal decay kernel**

    surprise(t) = 1 / (t - t_last_seen(c_{t+1}))

Recency-inverse surprise.

- This is the Hawkes baseline intensity approximation. Capacity: same O(N). Temporal decay is a hyperparameter not an architecture change.

### Hawkes vs cert

The Hawkes surprise weight is a scalar multiplier on the outer-product. It does not change the algebraic class (still rank-M outer-product sum). It reweights the capacity allocation but does not lift the conditional-bigram ceiling. The cert chain is compatible if the surprise scalar is logged per write event. No fundamental improvement to sequence prediction class.

---

## SUB-QUESTION 3: Modern Hopfield Log-Sum-Exp Write Under Bipolar Constraint

### Standard MH retrieval (Ramsauer et al. 2020)

Energy: E = -logsumexp(beta * Xi^T * s) + 0.5 * s^T * s + beta^{-1} * log(N)

Update: s^{t+1} = Xi * softmax(beta * Xi^T * s^t)

Capacity: M_max = exp(alpha * N) for separation alpha > 0 (exponential in N).

### Write rule for MH

MH does not have a standard Hebbian write rule. Patterns Xi are stored by appending to the matrix Xi (column addition). There is no weight matrix W in the traditional sense; the weight tensor IS the pattern matrix Xi. Single-pass write is: append phi(c_{t+1}) to Xi. This is O(N) per write (just a column append), which is sub-ms.

### Bipolar constraint incompatibility

The MH retrieval step requires softmax(beta * Xi^T * s), which is a continuous soft-attention operation. Under bipolar constraint:

- Xi must be in {-1,+1}^{N x M}: achievable if patterns are binary.
- s (current state) must be in {-1,+1}^N: achievable with threshold.
- Xi^T * s: integer-valued Hamming-like inner product; computable in TC0.
- softmax(beta * Xi^T * s): requires exponentiation and normalization over M values. This is NOT AC0 or TC0 under standard circuit complexity (exponentiation is not in TC0 for general inputs). Retrieval complexity rises to at least NC1 or higher.

**Approximate bipolar MH (Krotov 2024 sparse variant):**

Replace softmax with k-WTA (keep top-k activations). k-WTA is in TC0 (sorting is TC0). Sparse Hopfield with k-WTA under bipolar Xi:

- Capacity: O(N^{p/(p-1)}) for p-norm interaction; for k-WTA with k~sqrt(N) the effective capacity is polynomial in N, between linear and exponential. Substantially larger than standard Hebbian.
- Cert compatibility: Retrieval is k-WTA over integer inner products, fully deterministic. Cert chain preserved.
- Real-time write: O(N) column append to Xi. Sub-ms.
- Complexity class: TC0 for k-WTA step. Retrieval is O(NM) inner products + sort = feasible.
- Bipolar storage: Xi in {-1,+1} is fully compatible.

### Sequence prediction class for sparse MH

Sparse MH retrieval maps a query s to the nearest stored pattern in Xi by a polynomial interaction. If Xi stores bigrams (phi(c_t), phi(c_{t+1})) pairs, retrieval gives the most likely next token by nearest-neighbor lookup. This is still conditional-bigram class: the retrieved pattern is the most similar stored next-token, not a Markov-chain generalization. For higher-order prediction, you would need to store k-grams in Xi (embedding of (c_{t-k+1}, ..., c_t) -> c_{t+1}), which requires exponential pattern storage.

**Key algebraic insight:** The MH exponential capacity (for continuous case) is exponential in pattern DIMENSION (N), not in Markov order. Storing N-dimensional patterns of k-grams still requires M = O(vocab^k) patterns for k-th order Markov prediction, which is exponential in k regardless of the write rule.

P_raw = 0.55 (sparse MH bipolar k-WTA improves retrieval precision; does NOT lift Markov order).
P_deflated = 0.35.

---

## SUB-QUESTION 4: Sparse Distributed Memory Trace-Based Writes Under Bipolar Constraint

### SDM architecture (Kanerva 1988)

Address space A in {0,1}^N; hard locations at a random subset of L addresses. Write to address a: increment all hard locations within Hamming radius r of a. Read: sum over hard locations within r, threshold. Capacity ~ L * r (trace length).

### Bipolar SDM write under continual learning

Ratcliff-inspired SDM revival (2023, Davies et al., "Sparse Distributed Memory is a Continual Learner"):

- Write: For each hard location h within radius r of query a, increment counter C[h][j] by bipolar input value phi_j(c_{t+1}).
- Read: Threshold(sum_h C[h] for h within r(a)).
- Bipolar storage: C[h][j] is an integer accumulator, not bipolar. For exact bipolar storage, replace C with sign(C), but this loses trace counts and capacity degrades to near-Hebbian.

### Trace decay and capacity

With trace decay (forgetting): C[h][j] *= (1-gamma) at each step. This implements exponential forgetting. Capacity scales as T_forgetting * L (forgetting window * hard locations).

- Algebraic class: SDM is equivalent to a kernel nearest-neighbor associator. For sequence prediction, writing (phi(c_t), phi(c_{t+1})) pairs into SDM gives conditional-bigram statistics. The trace over multiple nearby addresses is equivalent to a smoothed co-occurrence count; still bigram class.
- Higher-order rescue: Write k-gram embeddings (phi(c_{t-k+1}, ..., c_t), phi(c_{t+1})) to SDM. The embedding of the k-tuple is itself a VSA binding operation (XOR/multiply of k component vectors). This DOES move the effective Markov order to k. BUT: this requires k-fold binding before write, which is O(k*N) per write; and the cert chain must now certify k-tuple membership, which requires k hash operations per cert query.

### Cert compatibility for SDM

SDM with distributed writes (multiple hard locations) makes cert non-trivial: fact X = (a, b) is stored iff trace at all hard locations within r of phi(a) encodes b. This requires reading O(L) hard locations per cert query, not a single sub-ms read. For large L (e.g., L = N^2), cert query is O(N^2) ops -- not sub-ms for N=4096.

**Rescue:** Restrict SDM to l=1 hard locations (degenerate SDM = standard Hopfield). Cert is O(1). But capacity falls back to standard Hopfield O(N).

P_raw = 0.60 (SDM trace-based write improves continual learning / forgetting curves; no Markov-order improvement without k-tuple binding).
P_deflated = 0.40.

---

## SUB-QUESTION 5: FUNDAMENTAL VERDICT -- Can Any Write Rule Break Conditional-Bigram Ceiling?

### The algebraic ceiling argument

Let W in {-1,+1}^{N x N} be any bipolar weight matrix, and let phi: V -> {-1,+1}^N be any encoding. Define the sequence prediction task as: given c_1, ..., c_t, predict c_{t+1}.

A single matrix-vector product W * phi(c_t) is a linear function of phi(c_t). It can capture E[phi(c_{t+1}) | phi(c_t)] (conditional expectation given the SINGLE most recent token), which is the conditional-bigram class.

To capture E[phi(c_{t+1}) | phi(c_{t-k+1}), ..., phi(c_t)], a matrix-vector multiply is insufficient: the k-tuple context must be mapped to a single vector before multiplication. VSA binding (XOR for binary, Hadamard for bipolar): phi(c_{t-k+1}, ..., c_t) = phi(c_{t-k+1}) XOR phi(c_{t-k+2}) XOR ... XOR phi(c_t). This is the "context vector" approach.

**With context binding + single W:**
- Write: W += outer(context_k(t), phi(c_{t+1})) for any write rule variant.
- Read: retrieve = W * context_k(t).
- This IS k-gram conditional prediction (k-th order Markov).
- Capacity: M_max = O(N) associations between context vectors and targets. For vocab V and context length k, need M <= C_k = V^k patterns. When M > N, capacity is exceeded regardless of write rule.

**Key conclusion:** The write rule does NOT determine the Markov order of the substrate. The CONTEXT ENCODING determines the Markov order. Any write rule (Hebbian, PC residual, surprise-weighted, sparse MH) applied to k-gram context vectors gives k-th order Markov prediction. The write rule determines EFFICIENCY (how close to N patterns can be stored and retrieved accurately), not CLASS.

### Does predictive coding residual lift Markov order?

No. PC residual write: W += eta * (phi(c_{t+1}) - W * phi(c_t)) * phi(c_t)^T. This minimizes prediction error on single-token context. If you feed k-gram context binding as input, PC residual lifts prediction to k-gram class. But the improvement is to prediction QUALITY within a given class, not to the class itself.

### Can any write rule make W capture long-range dependencies WITHOUT k-gram binding?

The information-theoretic lower bound: a matrix W in {-1,+1}^{N x N} has at most N^2 bits of capacity. A k-th order Markov model over vocab V requires log2(V^k) = k * log2(V) bits PER prediction table entry, times V entries = V * k * log2(V) bits. For k > N * log2(N) / (V * log2(V)), the weight matrix cannot store a k-th order Markov model regardless of the write rule.

This is an absolute capacity ceiling: no write rule can exceed it.

### Verdict: OUTCOME B (not C)

There IS a write rule that lifts sequence prediction quality: **PC residual write with k-gram context binding**, which simultaneously:
- Improves prediction quality within conditional-k-gram class (better constant factor on capacity)
- Preserves TC0 retrieval complexity (single matrix-vector multiply on k-gram context vector)
- Preserves real-time write (single-pass O(N^2) or O(k*N) if context is pre-built)
- Preserves bipolar storage via shadow-W (with cert moved to shadow layer)

But this BREAKS the cert moat as currently defined (deterministic cert on W_bipolar alone). The cert either:
(a) Moves to the shadow real-valued layer: cert is deterministic but shadow is real-valued, not bipolar -- the cert is no longer a bipolar-weight audit.
(b) Uses sign-only update (Option D from Sub-Q 1): cert is deterministic on W_bipolar, but convergence is slower and the effective capacity constant is reduced.

The "four moats simultaneously" requirement is the binding constraint. The moat that breaks first for every meaningful write-rule improvement is the CERT MOAT, not retrieval complexity or real-time write.

OUTCOME B summary: All write rules that materially improve sequence prediction quality (beyond Hebbian baseline) sacrifice the deterministic cert chain on the bipolar weight layer. No write rule breaks the conditional-bigram ceiling that is SIMULTANEOUSLY cert-preserving, real-time, TC0, AND strictly bipolar at the cert layer.

P_deflated (Outcome B) = 0.62. Hard-fail threshold: if an empirical test shows sign-only update under k=3 context binding achieves perplexity improvement > 15% over flat Hebbian at N=4096 with deterministic cert verified = HARD-PASS (upgrade to partial outcome A).

---

## CHEAP DECISIVE TESTS (CPU-feasible, N=4096)

**Test 1 (PC residual vs Hebbian on conditional bigram, bipolar sign-only update):**
- Protocol: Synthetic Markov chain, V=256, M=400, N=4096, 3 seeds.
- Write Hebbian: W_H += outer(phi_t, phi_{t+1}); sign after T writes.
- Write PC sign-only: iterate W_B[i,j] = W_B[i,j] XOR (sign(phi_{t+1}[i] - (W_B * phi_t)[i]) != sign(W_B[i,j])).
- Metric: next-token prediction accuracy (top-1 retrieval), averaged over last 20% of sequence.
- Expected result: PC sign-only improves accuracy by 5-15% over Hebbian at M/N = 0.10. If improvement < 2%, sign-only update is no better than Hebbian (HARD-FAIL for PC residual under bipolar).
- Wall time: ~30s at N=4096 CPU.

**Test 2 (k-gram context binding + Hebbian vs flat Hebbian):**
- Protocol: Same Markov chain, test k=1,2,3 context binding (XOR of k consecutive bipolar vectors).
- Metric: next-token accuracy at same M budget.
- Expected result: k=2 binding gives 20-40% accuracy improvement at same N; k=3 gives further improvement until M exceeds N (at M/N > 0.5, capacity cliff for k=3 since patterns are longer).
- HARD-PASS: accuracy(k=2) > accuracy(k=1) * 1.20 at M/N = 0.05.
- HARD-FAIL: accuracy(k=2) <= accuracy(k=1) * 1.02 (context binding provides no benefit, implies VSA binding does not separate k-gram contexts).

**Test 3 (cert chain under shadow-W):**
- Protocol: Write M=100 (fact, value) pairs to shadow-W; verify cert for each pair by checking hash(sign(W_shadow)) contains trace of each pair.
- Metric: cert verification time per fact; false positive rate.
- HARD-PASS: All certs verify in < 1ms per fact, zero false positives.
- HARD-FAIL: Cert verification time > 10ms per fact, or false positive rate > 0.01%.

---

## FALSIFIABLE PREDICTIONS

**HARD-PASS (Partial Outcome A trigger):**
- Sign-only PC residual achieves >= 15% next-token accuracy improvement over Hebbian at M/N = 0.10, N=4096, V=256.
- k-gram context binding (k=2, XOR-bind) achieves >= 20% accuracy improvement with deterministic cert chain verified.
- Shadow-W cert chain verifies all M=100 stored facts in < 0.5ms total.

**HARD-FAIL (Confirm Outcome B or C):**
- Sign-only PC residual achieves < 2% improvement over Hebbian at M/N = 0.10.
- k-gram binding (k=2) achieves < 5% improvement over k=1 at same N.
- Shadow-W cert verification > 10ms per fact OR false positive rate > 0.01%.

**HARD-FAIL for Outcome C:**
- If k-gram binding (k=2) ALSO fails to improve accuracy (< 5% at M/N = 0.05), then the substrate is bounded at co-occurrence-bigram regardless of write rule. This would confirm Outcome C (substrate fundamentally at co-occurrence/bigram class, improvement requires architectural change not write-rule change).

---

## CROSS-DOMAIN PROBE: Hippocampal / Cerebellar Write Rules

### Hippocampal theta sequences (Neuron 2024 + biorxiv 2023)

Theta phase precession implements a predictive write architecture: the CA3 self-supervised recurrent network predicts the NEXT location in a theta cycle, then Hebbian LTP updates are applied between predicted and actual next states. The write rule is essentially:

    W_CA3 += LTP * outer(state_predicted, state_actual) * theta_phase_gate

where theta_phase_gate is a temporal kernel peaking at the phase lag between prediction and arrival.

**Key insight:** This is NOT a simple bigram write. The theta sequence compresses a K-step forward sweep in each cycle, writing the ENTIRE future trajectory in compressed form. Algebraically: in each theta cycle, the network writes M_k = K associations (current, +1), (current, +2), ..., (current, +K). This is a TRAJECTORY write, equivalent to K-gram conditional associations from a single anchor point.

Application to bipolar substrate: Implement a "theta burst write": on each write event, write not just (phi(c_t), phi(c_{t+1})) but also (phi(c_t), phi(c_{t+2})), ..., (phi(c_t), phi(c_{t+K})) with exponentially decaying weights. This is K writes per token instead of 1; still single-pass; preserves real-time property if K is small (K <= 10 adds ~10x write cost). Capacity impact: M_max falls by K (you spend K capacity slots per token). Net sequence prediction quality depends on whether multi-step lookahead outweighs capacity cost.

This architecture is NOT published in the AI memory literature as a bipolar-compatible write rule. It derives from the hippocampal theta-sweep write identified in the neuroscience literature (Neuron 2024). Potentially novel direction.

P_raw = 0.45 (multi-step lookahead write improves prediction quality at moderate M). P_deflated = 0.25. Cap novelty: 0.30.

### Cerebellar inverse model write (Albus 1971 + PMC 2025 cerebellar circuit computations)

The Albus perceptron cerebellar model: Purkinje cells (output) are trained by climbing fiber error signals (PC residual in neural implementation). The write rule is:

    w_PC -= alpha * climbing_fiber_error * granule_cell_activity

This is a supervised delta rule, equivalent to the PC residual write from Sub-Q 1, applied to a lookup-table architecture (granule cells = random projections of input; Purkinje = linear readout). The cerebellar write converges in O(1/alpha) steps, single-pass online.

**AI memory community gap:** The cerebellar circuit is architecturally equivalent to a random-feature regression with online delta-rule updates. In the binary-weight LM literature, the closest analog is the "random kitchen sinks" method (Rahimi-Recht 2007) combined with online gradient steps. No published work has applied this architecture to bipolar associative memory with cert constraints. The key architectural innovation from cerebellum is the RANDOM PROJECTION (granule cell expansion) before the write step, which increases the effective dimensionality of the stored patterns from N to N_granule >> N.

If N_granule = N^2 (quadratic expansion), capacity for the random-projection + bipolar write becomes O(N^2) patterns instead of O(N), while retrieval is still O(N_granule) = O(N^2) ops. This DOES improve capacity class (from linear to quadratic in N), at quadratic retrieval cost. TC0 boundary: O(N^2) ops are still TC0 (constant depth threshold circuits) if done in parallel.

This is the most significant finding from the cross-domain probe.

P_raw = 0.50. P_deflated = 0.30. Novel-synthesis cap applies.

---

## CROSS-THREAD SYNTHESIS WITH PRIOR ENTRIES

Prior drill (2026-06-04, same topic family): Confirmed Hebbian outer-product = n-gram class, sqrt(N) SNR threshold, 1/K SNR penalty for extended context. PC residual = partial rescue to conditional-bigram.

This drill ADDS:
1. Algebraic proof that write rule determines CAPACITY QUALITY, not MARKOV CLASS. Context encoding (k-gram binding) determines Markov class.
2. The bipolar cert moat is the binding constraint that prevents clean adoption of every non-Hebbian write rule.
3. The hippocampal multi-step trajectory write and cerebellar random-projection expansion are both unexplored in the bipolar-AM literature.
4. Shadow-W architecture is the least-bad solution for cert under PC residual write, but requires dual-layer storage.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Context binding (k=2) is the actionable lever.** Implement XOR-bind of (phi(c_t) XOR phi(c_{t-1})) as the query vector; use existing Hebbian write. This is a retrieval-side change, not a write-side change. Zero write-cost overhead; improves effective Markov order to 2 with existing infrastructure.

2. **Shadow-W architecture enables cert + PC residual.** Ship a shadow real-valued W (32x memory) alongside W_bipolar; run cert queries against W_shadow; use W_bipolar for inference. This is a two-layer product: inference layer (bipolar, fast) + audit layer (real-valued, deterministic).

3. **Theta burst write (K=3-5) is a hypothesis for the exp_dev queue.** Single-pass, K writes per token, decaying weight schedule eta * gamma^k for k=1..K. CPU-feasible at N=4096. Potential 15-30% improvement in multi-step prediction at 5x write cost.

4. **Cerebellar random-expansion write.** Random projection from N to N^2 dimensions (random Gaussian projection, fixed), then apply Hebbian/PC write in the expanded space, read back via transpose projection. Capacity lifts from O(N) to O(N^2) patterns. Retrieval: O(N^2) ops, still parallel-feasible. This is an architectural upgrade, not just a write-rule change; would require N^2 weight storage. For N=4096, N^2 = 16M weights = 16MB bipolar = feasible.

---

## CITATIONS (verified via web search + fetch, 2026-06-05)

1. Hopfield, J.J. (1982). Neural networks and physical systems with emergent collective computational abilities. PNAS.
2. Ramsauer et al. (2020). Hopfield Networks is All You Need. ICLR 2021. arXiv:2008.02217.
3. Hu et al. (2023). On Sparse Modern Hopfield Model. NeurIPS 2023. arXiv:2309.12673.
4. Alonso, N. & Krichmar, J.L. (2024). A sparse quantized Hopfield network for online-continual memory. Nature Communications 15.
5. Davies et al. (2023). Sparse Distributed Memory is a Continual Learner. arXiv:2303.11934.
6. Ma et al. (2024). BitNet b1.58: All Large Language Models are in 1.58 Bits. arXiv:2402.04291.
7. Gupta et al. (2015). Deep learning with limited numerical precision. ICML 2015.
8. Kanerva, P. (1988). Sparse Distributed Memory. MIT Press.
9. Albus, J.S. (1971). A theory of cerebellar function. Mathematical Biosciences.
10. Whittington, J.C.R. & Bogacz, R. (2017). An approximation of the error backpropagation algorithm in a predictive coding network with local Hebbian synaptic plasticity. Neural Computation.
11. Sosa, M. et al. (2024). Predictive sequence learning in the hippocampal formation. Neuron. S0896-6273(24)00371-4.
12. Itti, L. & Baldi, P. (2009). Bayesian surprise attracts human attention. Vision Research.
13. McClelland et al. (1995). Why there are complementary learning systems in the hippocampus and neocortex. Psychological Review.
14. Krotov, D. (2023/2024). Sparse Modern Hopfield variant. OpenReview / NeurIPS workshop.
15. Long Sequence Hopfield Memory (NeurIPS 2023). arXiv:2306.04532.
16. Gated Associative Memory: A Parallel O(N) Architecture for Efficient Sequence Modeling. arXiv:2509.00605.
17. Provable local learning rule by expert aggregation for a Hawkes network. arXiv:2304.08061.

Verified citation count: 17

---

## P_DEFLATED SPLITS PER METHODOLOGY

| Claim | P_raw | P_deflated | Method |
|---|---|---|---|
| PC residual improves conditional bigram quality | 0.72 | 0.52 | lit-scan: PC + binary weight lit |
| Sign-only update preserves cert; degrades convergence | 0.80 | 0.60 | algebraic derivation |
| Shadow-W breaks bipolar cert moat | 0.85 | 0.65 | algebraic derivation |
| Surprise weighting improves heavy-tail sequence quality | 0.65 | 0.45 | lit-scan: Hawkes + memory lit |
| Sparse MH k-WTA preserves TC0 under bipolar | 0.78 | 0.58 | lit-scan: Krotov + sparse Hopfield |
| No write rule lifts Markov class without context binding | 0.88 | 0.68 | algebraic (information-theoretic) |
| k-gram context binding lifts Markov order | 0.85 | 0.65 | algebraic |
| Theta burst write improves multi-step prediction | 0.45 | 0.25 | cross-domain probe (novel synthesis) |
| Cerebellar random-expansion lifts capacity to O(N^2) | 0.50 | 0.30 | cross-domain probe (novel synthesis) |
| Outcome B (not C) is the correct verdict | 0.78 | 0.58 | synthesis |

---

## HARD-PASS / HARD-FAIL THRESHOLDS (pre-registered)

HARD-PASS: sign-only PC residual achieves >= 15% accuracy gain over Hebbian at M/N=0.10, N=4096.
HARD-PASS: k=2 context binding achieves >= 20% accuracy gain over k=1 at M/N=0.05.
HARD-PASS: shadow-W cert verifies M=100 facts in < 0.5ms total.
HARD-PASS (theta burst): K=3 multi-step write achieves >= 15% gain in 3-step prediction accuracy at M/N=0.05.

HARD-FAIL: sign-only PC residual < 2% gain over Hebbian.
HARD-FAIL: k=2 context binding < 5% gain over k=1.
HARD-FAIL: shadow-W cert > 10ms per fact.
HARD-FAIL (Outcome C trigger): ALL write rules (sign-only PC, k-gram Hebbian, theta burst) fail their HARD-PASS thresholds simultaneously.

---

## NEXT-DRILL CANDIDATES

1. k-gram context binding empirical test (CPU N=4096, k=1,2,3 sweep) -- exp_dev handoff candidate.
2. Cerebellar random-expansion write: algebraic capacity analysis at N^2 expansion -- research drill into sparse-coding-compressed-sensing adjacency.
3. Theta burst write: empirical test at K=1..5, N=4096 -- exp_dev handoff candidate.
4. Free-probability / random-matrix analysis of shadow-W quantization noise -- drill into random-matrix-theory-beyond-free-prob adjacency (top-5 field advisor candidate).
