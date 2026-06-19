# Research note — Multi-hop chain composition rehabilitation at N=65536

**Date**: 2026-05-22 ~19:05 EDT
**Owner**: Research session
**Trigger**: `strategy_request_to_research_multihop_chain_rehabilitation_N65536_2026-05-22.md` filed 18:51 by Strategy (cap_map v121). Monitor caught at 18:51:46. User directive: *"research negative results 2x"* — applying [[feedback-rehabilitation-after-rejection]] 2x discipline.
**Method**: 2 Sonnet-dispatched parallel external lit-scan agents per Strategy's recommended 2x:
- Agent G — Mechanism diagnosis (why multi-hop degrades at large N when 1-hop is clean)
- Agent H — Rehabilitation mechanisms (what can restore deep-chain composition at N=65536)

Generic-math queries only per [[feedback-query-privacy-decomposition]]. ~5 min wall, ~38 KB raw output.
**Pass-1 honesty label**: **YES external lit scan** via 2 Sonnet agents with WebSearch + WebFetch. Both agents applied [[feedback-dont-dismiss-adjacent-methods]] discipline — Agent G dug eigenvalue/spectral literature (arXiv:2103.14324, Lucibello 2024 arXiv:2403.01907); Agent H dug iterative inference / VAMP / EP family directly extending Entry 148's chain-posterior-inference thread.
**Strategic frame alignment**: maps to **capability class 4 (cognitive architecture composition)** of [[project-ai-memory-subsystem-direction]] — deep-chain reasoning is the substrate-product test of structural composability. Lane D agent memory SDK Demo 1 depends on chain composition at N=65536.

---

## (a) Headline — mechanism diagnosis + top rehabilitation

**Empirical curve** (substrate N=65536, K=100, FULL): per-depth acc {1:0.983, 5:0.817, 10:0.567, 25:0.250, 50:**0.217**} vs N=4096 K=100 FULL (cycle 96 NEW HIGH): acc_50hop=0.767. **3.5× degradation at 16× larger N.** 1-hop retrieval IDENTICAL across N. Plateau at depth 25-50 well above random (1/K=0.01).

**Mechanism diagnosis (Agent G primary candidate, P=0.70)**: **Signal eigenvalue near-degeneracy at large N**.

Standard cleanup-cross-talk theory (noise ∝ (K-1)/N) is **FALSIFIED** by the data — predicts decreasing noise at larger N (substrate's K/N drops from 0.024 at N=4096 to 0.0015 at N=65536), but observation is opposite. The crosstalk hypothesis is dead.

The mechanism that survives: at fixed K with growing N, the K signal eigenvalues of W cluster more tightly near eigenvalue 1 (Marchenko-Pastur bulk stays bounded; signal eigenvectors become near-orthogonal but mutually less directionally separable in the high-dim signal subspace). Each W application during a chain hop causes the retrieval state to **drift within the K-dim signal subspace** rather than converging stably on the correct codeword. Analogous to power-iteration instability when top eigenvalues are nearly equal — repeated W application does NOT converge to top eigenvector; it wanders within the degenerate cluster.

**Plateau at ~0.22** = system settles into a stable "confused" attractor within the K-dim signal subspace (mixture of K signal eigenvectors with partial overlap to correct codeword in ~22% of chains). This is NOT Marchenko-Pastur bulk noise; it's within-signal-subspace confusion.

**Rehabilitation primary candidate (Agent H top mechanism, P=0.65)**: **Per-hop Resonator Network iteration** (Frady-Kent-Olshausen-Sommer 2020 Neural Computation 32:12).

Replace the per-hop argmax (hard nearest-neighbor commit) with iterative resonator dynamics that maintain a SUPERPOSITION estimate and use nonlinear updates to suppress wrong candidates without early hard commitment. Cost: T·O(K·N) per hop with T~10-30 iterations = ~6.5×10^9 ops for 50-hop chain at N=65536 K=100 (offline-feasible, ~30-60 GPU-min).

**Why Resonator Networks fit substrate's failure mode**: argmax commits prematurely while the K signal eigenvectors are still mixed in the retrieved state; resonator dynamics resolve the mixture iteratively before committing. Directly addresses the signal-subspace-drift mechanism.

**Predicted acc_50hop with resonator rehabilitation at N=65536 K=100**: **0.45 - 0.65** (median 0.55). **Hard falsification**: if <0.30 with T=20 iterations, mechanism insufficient; substrate-level restructuring needed (hierarchical codebook or bidirectional storage).

---

## (b) Pass 1 — Cross-agent external lit scan

### Agent G — Mechanism diagnosis

**Rejected hypotheses** (per [[feedback-no-smoke]] discipline):
1. **Standard cleanup cross-talk (K-1)/N**: predicts SHRINKING noise at large N. Falsified by data.
2. **Resonator limit cycles**: failure mode is convergence-to-spurious-fixed-point, not per-hop noise. Would show low 1-hop accuracy. Falsified (1-hop=0.983 at both N).
3. **Dense AM chain dynamics (Krotov-Hopfield 2016)**: single-step framework, no multi-hop analysis. N/A.

**Surviving primary mechanism — Signal eigenvalue near-degeneracy**:
- Hebbian W = (1/N) Σ_μ ξ_μ ξ_μ^T has K "signal" eigenvalues near 1 (for near-orthogonal codebook patterns)
- At fixed K, growing N → signal eigenvalues cluster MORE tightly near 1
- Signal eigenvectors become near-orthogonal in absolute terms BUT mutually less directionally separable
- Repeated W application = drift within K-dim signal subspace (power-method instability for degenerate top eigenvalues)
- Per-hop retention starts ~0.98 (1-hop has full SNR) → drops mid-chain as drift escapes correct-codeword basin → plateaus when settled into confused-subspace attractor

**Quantitative consistency**:
- Per-hop retention r at N=4096: 0.767^(1/50) ≈ 0.9947
- Per-hop retention at N=65536 from depth 5: 0.817^(1/5) ≈ 0.960
- Per-hop retention at N=65536 from depth 10: 0.567^(1/10) ≈ 0.944
- Plateau implies non-constant per-hop retention — drift escapes basin then stabilizes

**Citations** (Agent G):
- Plate 1995 HRR (IEEE TNN 6:3) — foundational chain inversion error model
- Kleyko 2022 VSA review (arXiv:2106.05268 + arXiv:2301.10352) — standard (K-1)/N crosstalk (now falsified)
- Frady-Kent-Olshausen-Sommer 2020 Resonator Networks I & II (Neural Computation 32:12; arXiv:1906.11684)
- Krotov-Hopfield 2016 (arXiv:1606.01164) Dense AM
- Lucibello et al. 2024 (arXiv:2403.01907) Hebbian-Hopfield capacity + spectral analysis
- arXiv:2103.14324 — eigenvalue spectrum with arbitrary Hebbian length (spectral structure analysis)

### Agent H — Rehabilitation mechanisms

**5 candidate rehabilitation mechanisms** ranked by P(restores acc_50hop > 0.5 at N=65536):

| Mechanism | How it restores composition | Cost per hop | P(ships) | Citation |
|-----------|---------------------------|--------------|----------|----------|
| **Resonator Network per-hop iteration** | Maintains superposition; avoids hard argmax commit; iterative resolution within K-dim signal subspace | O(T·K·N), T~10-30 | **0.65** | Frady et al. 2020 Neural Computation 32:12 |
| **Forward-backward EP / VAMP on chain** | Computes soft marginals at each hop; backward pass corrects forward errors; aggregates uncertainty across hops | O(D·N) total | **0.55** | Rangan et al. arXiv:1610.03082; Knoblauch-Palm 2020 Neural Computation 32:1 |
| **Per-hop sparse cleanup filter** | Threshold-AMP after each hop; sparsifies before next hop | O(N) per hop | **0.50** | Krotov-Hopfield 2016; Mofrad et al. 2021 Neural Computation 33:9 |
| **Bidirectional chain inference** | Backward messages from distal hops correct early commitments (Viterbi-on-chain analog) | O(D·N) total | **0.45** | Mofrad et al. 2021 Neural Computation 33:9 |
| **Hierarchical multi-scale binding** | Route composition through coarse-sparse → dense-fine layers; reduces effective chain length | O(N log N) per hop | **0.35** | General hierarchical AM lit |

**REJECTED rehabilitation mechanisms** (per [[feedback-no-smoke]]):
- **Per-hop β scaling alone**: doesn't reduce accumulated error variance across 50 hops; insufficient as standalone
- **Block coding without iteration**: helps single-step capacity, not error-propagation cascade
- **Scaling N further**: capacity/N ratio fixed; doubling N doesn't help flat architecture (arXiv:2402.04875 Remy et al. 2024 explicit)

---

## (c) Pass 2 — Substrate drill on top mechanism

### Why Resonator Networks fit substrate's specific failure mode

The eigenvalue near-degeneracy diagnosis (Agent G) and the Resonator Networks rehabilitation (Agent H) are **structurally complementary**:

- **Diagnosis**: substrate fails because each per-hop argmax commits to a winner WHILE the retrieval state is still mixed across multiple near-degenerate signal eigenvectors
- **Rehabilitation**: Resonator dynamics maintain the mixture as an explicit superposition, iteratively resolve the mixture via nonlinear updates, then commit AFTER resolution

This is exactly the mechanism class my Entry 148 Bet Z.3-AMP analysis flagged sub-question 3 ("cued holistic readout" — posterior over which patterns activated). Resonator Networks ARE the Bayesian-posterior-readout substrate-applicable instance for chain composition, predating VAMP-on-chain by ~5 years.

**Cross-thread convergence**: Bet Z.3-AMP family (Entry 148) + Bet Z.3-VAMP (Entry 149 three-path decision tree) + Resonator Networks (this Entry 151) **all converge on the same mechanism class**: iterative posterior-inference readout that avoids premature hard commitment. Substrate-product narrative: **substrate's primary readout primitive should be iterative-posterior, not single-step argmax**.

### ASCII-only operational pseudocode (Resonator per-hop chain)

```python
import numpy as np

def resonator_chain_retrieval(W, codebook, query, depth=50,
                              T_inner=20, tau_anneal=True):
    """
    Resonator-cleaned chain retrieval at large N.
    W: N x N coupling matrix (substrate's Hebbian)
    codebook: K x N matrix of stored ±1 codewords
    query: initial N-vector cue
    depth: chain depth (50 for substrate's setup)
    T_inner: resonator iterations per hop
    Returns: chain of D retrieved codewords + per-hop confidence
    """
    K, N = codebook.shape
    q = query.copy()
    chain = []
    confidences = []
    for hop in range(depth):
        # Warm-start from standard lookup
        scores = codebook @ q
        weights = softmax(scores, tau=1.0)
        x_hat = (weights[:, np.newaxis] * codebook).sum(axis=0)
        # Resonator inner loop: iteratively resolve K-dim signal-subspace mixture
        for t in range(T_inner):
            tau = 1.0 / (1.0 + 0.5 * t) if tau_anneal else 0.5
            # Nonlinear cleanup step (sign-based resonator from Frady et al. 2020)
            x_hat = np.sign(codebook.T @ np.sign(codebook @ x_hat))
            scores = codebook @ x_hat
            weights = softmax(scores, tau=tau)
            x_hat = (weights[:, np.newaxis] * codebook).sum(axis=0)
        # Commit to hard codeword for next hop
        winner_idx = int(np.argmax(scores))
        q_next = codebook[winner_idx].copy()
        confidence = float(np.max(softmax(scores, tau=0.1)))
        chain.append(winner_idx)
        confidences.append(confidence)
        # Apply W for next hop (substrate's chain dynamics)
        q = np.sign(W @ q_next)
    return chain, confidences


def softmax(x, tau=1.0):
    x = x / tau
    x = x - np.max(x)
    e = np.exp(x)
    return e / np.sum(e)
```

**Cost analysis**:
- Per-hop: T·O(K·N) = 20·100·65536 ≈ 1.3×10^8 ops
- 50-hop chain: 6.5×10^9 ops total
- At ~10^10 ops/sec GPU throughput: ~0.7 sec per chain
- Multi-seed (5-seed × 10 trial chains = 50 chains): ~35 sec runtime
- **Feasible Phase 1 smoke cost: ~5-15 min wall (with PyTorch GPU)**

### Cheaper variant — forward-only iterative cleanup (P=0.50)

```python
def forward_iterative_chain(W, codebook, query, depth=50, T_inner=5):
    """Lighter rehabilitation: 5 iterations soft cleanup per hop.
    Cost: O(5·K·N) per hop = 5× standard chain cost."""
    # ... (similar to above but T_inner=5; no tau annealing; no sign-based resonator)
```

This is the substrate-product fallback if full Resonator iteration is too expensive at scale.

### Falsifiable predictions

For substrate at N=65536, K=100, with Resonator per-hop rehabilitation (T_inner=20):

1. **acc_50hop predicted range**: **0.45 - 0.65** (median 0.55).
   - Lower bound 0.45: residual error propagation if eigenvalue clustering is severe
   - Upper bound 0.65: optimistic if eigenvalue separation is sufficient at K=100
   - **Hard falsification**: acc_50hop < 0.30 → mechanism insufficient; substrate-level restructuring needed

2. **K-scaling falsifiability** (substrate test with smaller K):
   - **K=50 at N=65536** prediction: acc_50hop ≈ 0.65-0.80 (less crowding in signal subspace; less per-hop drift)
   - **K=25 at N=65536** prediction: acc_50hop ≈ 0.80-0.90
   - Falsification: if K=50 doesn't improve significantly over K=100, eigenvalue-degeneracy hypothesis is wrong

3. **N-scaling intermediate test**:
   - **N=16384, K=100** prediction: acc_50hop in [0.70, 0.75] (monotone with N)
   - Falsification: if N=16384 acc_50hop < 0.5 OR > 0.85, monotonic N-degradation hypothesis falsified

4. **Spectral validation test**:
   - Compute top-K eigenvalues of W at N=4096 vs N=65536
   - Prediction: at N=65536, top-K eigenvalues span < 0.01 (tightly clustered near 1); at N=4096, span > 0.03
   - **Direct mechanism falsification test** — single eigvalsh call

---

## (d) Materials analog — load-bearing per [[feedback-materials-science-probe]]

The signal-eigenvalue-near-degeneracy mechanism has a direct materials-physics analog: **degenerate-state diffusion in random-matrix-theory eigenspace**. When the top-K eigenvalues of a random symmetric matrix cluster (Wigner semicircle with structured tail), repeated matrix application leads to diffusion within the degenerate subspace — same mathematics as quantum-mechanical mixing of nearly-degenerate energy eigenstates, or classical-statistical-mechanics mixing of nearly-degenerate Hamiltonian eigenmodes.

**Relevant materials precedents**:
- **Quantum eigenvalue level statistics** (Mehta 1991; Wigner 1955): nearly-degenerate eigenvalues cluster according to Tracy-Widom distributions at edges; bulk eigenvalues follow Marchenko-Pastur with sample-size-dependent fluctuations
- **Random matrix product diffusion** (Furstenberg 1963; Cohen-Newman 1984): Lyapunov exponents of random matrix products characterize drift rates within degenerate-eigenvalue clusters
- **Anderson localization vs delocalization**: in a different regime, eigenvector localization at large N causes opposite drift direction; substrate's near-degenerate cluster is the delocalized analog

NOT directly relevant (rejected as decorative — 17th HONEST-RECALIBRATION-pattern note candidate):
- Spin glasses with full RSB (substrate is RS-phase per cycle 112)
- Continuous-variable systems with phonon spectra
- Quantum coherent matter

---

## (e) Routing recommendation to Strategy

**Proposed Phase 1 smoke** (15-30 GPU-min total):

1. **Resonator chain smoke at N=65536, K=100, depth=50, T_inner=20** (5-15 GPU-min)
   - Verify acc_50hop > 0.30 (basic mechanism check)
   - If PASS: scale to full multi-seed FULL with T_inner sweep [5, 10, 20, 30]
   - If FAIL: route to mechanism #2 (forward-backward EP/VAMP)

2. **K-scaling smoke** at N=65536 (5 GPU-min): K ∈ {25, 50, 100} acc_50hop curve
   - Validates eigenvalue-degeneracy hypothesis
   - If K=50 shows >0.5 acc_50hop with standard cleanup (no resonator) → eigenvalue-degeneracy is the right mechanism

3. **Spectral validation** (1 GPU-min): top-K eigenvalues of substrate's W at N=4096 vs N=65536
   - Single eigvalsh call (already done in observability suite v1 at smaller scale)
   - Confirms or refutes the diagnosis directly

**Strategic significance** per [[project-ai-memory-subsystem-direction]]:
- **Capability class 4 (cognitive architecture composition)**: deep-chain reasoning at N=65536 is THE substrate-product test of structural composability
- Lane D agent memory SDK Demo 1 depends on chain composition at this scale
- If rehabilitation succeeds (acc_50hop > 0.5): substrate-novel iterative-posterior readout primitive (Resonator + VAMP convergent thread)
- If rehabilitation fails (acc_50hop < 0.30): hierarchical/multi-scale substrate restructuring becomes the next priority

**Substrate-product proposal — Resonator Network as core readout primitive**:
- Replaces per-hop argmax across all multi-hop tests
- Couples to Bet Z.1 SRHT (Entry 143) + Bet Z.3-AMP/VAMP (Entry 149) — all three are iterative-posterior-inference family
- **Unified substrate-product narrative**: substrate's readout primitive is iterative posterior, not single-step argmax. This is the substrate-novel mechanism class that distinguishes from LLM attention (single-pass softmax).

---

## (f) Cross-thread synthesis with Entries 141, 143, 148, 149

This is the 4th R-note this session that converges on iterative posterior inference:

| Entry | Note | Thread |
|-------|------|--------|
| 141 | Observability suite v1 (C_ij + P(q) + P(h)) | Family I+II Parisi q(x) probes (diagnostic) |
| 143 | Bet Z.1 SRHT + Bet Z.2 C2PO | Compressive readout + 2-pulse echo (refuted at cycle 113) |
| 148 | RS-phase capacity extension | **Bet Z.3-AMP/VAMP posterior inference (substrate-novel)** |
| 149 | Kerdock RI universality | Three-path decision tree for Bayes-AMP vs VAMP vs randomized |
| **151 (this)** | **Multi-hop rehabilitation** | **Resonator Network = iterative posterior inference applied to chain depth** |

**Unified substrate-product framing**: substrate's empirical 57× capacity gain (Entry 148 mystery) + 1-hop excellence + multi-hop N-degradation (Entry 151 mystery) ALL point to substrate operating optimally with **iterative posterior inference readout** rather than single-step argmax. This is the substrate-novel readout primitive class.

**Bet Z family unification** proposal to Strategy:
- Bet Z.1 SRHT — compressive readout (sparse activation posterior)
- Bet Z.3-AMP/VAMP — posterior over which patterns activated
- **Bet Z.4-Resonator (NEW from this note)** — iterative-posterior chain composition

All three are iterative-posterior-readout family. Capability classes 2 + 3 + 4 simultaneously.

---

## (g) Citations — 8 verified (cross-agent merged)

**Mechanism diagnosis (Agent G)**:
1. **Plate 1995 HRR** — IEEE Trans Neural Networks 6:3, 623-641 — foundational chain inversion error model
2. **Kleyko et al. 2022** — Artificial Intelligence Review 55:4523, arXiv:2106.05268 — VSA capacity review (standard crosstalk now falsified)
3. **Lucibello et al. 2024** — arXiv:2403.01907 — Hebbian-Hopfield capacity + spectral analysis (signal-eigenvalue clustering grounding)
4. **arXiv:2103.14324** — Eigenvalue spectrum with arbitrary Hebbian length (spectral structure)

**Rehabilitation (Agent H)**:
5. **Frady-Kent-Olshausen-Sommer 2020** — Neural Computation 32:12, arXiv:1906.11684 — Resonator Networks I & II (PRIMARY rehabilitation mechanism)
6. **Knoblauch-Palm 2020** — Neural Computation 32:1 — Iterative retrieval + block coding heteroassociative capacity
7. **Mofrad et al. 2021** — Neural Computation 33:9 — Chain-of-tournaments bidirectional sequence retrieval
8. **Remy et al. 2024** — arXiv:2402.04875 — Provable length and compositional generalization (rejects pure N-scaling rehabilitation)

Cross-reference to Entry 148:
- **Rangan-Schniter-Fletcher 2017 VAMP** — arXiv:1610.03082 — forward-backward EP/VAMP for chain inference (secondary candidate; convergent with Resonator Networks family)

---

## (h) Honest substrate-product assessment per [[feedback-no-smoke]]

**Strengths of this rehabilitation analysis**:
- Standard crosstalk theory FALSIFIED honestly (predicts opposite direction)
- Mechanism diagnosis (signal eigenvalue clustering) grounded in spectral literature + falsifiable via direct eigvalsh test
- Top rehabilitation candidate (Resonator Networks) has substrate-applicable pseudocode + cost analysis + falsifiable acc_50hop range
- Cross-thread convergence with Entries 148/149 — substrate-product narrative unifies on iterative-posterior readout primitive class
- 5 rehabilitation candidates ranked; no smoke

**Weaknesses (brutal honesty)**:
- **Mechanism diagnosis is novel synthesis, not directly cited** — Agent G explicit: "This mechanism has no direct citation in the lit — it is a gap — but it is grounded in the eigenvalue spectrum literature". Substrate-product positioning includes a substrate-novel mechanism claim that needs empirical confirmation via the spectral validation test.
- **acc_50hop prediction range 0.45-0.65 is wide** — depends heavily on actual eigenvalue separation at substrate's specific Kerdock construction
- **No published mechanism guarantees acc_50hop > 0.5 at N=65536 K=100** — Resonator Networks have not been tested in this regime in published literature
- **Hard falsification at acc_50hop < 0.30** means substrate-level restructuring would be needed if rehabilitation fails

**Honest substrate-product impact P (Resonator Network rehabilitation ships)**: **0.55-0.70**.
- Lower bound: mechanism is novel synthesis; substrate-specific eigenvalue distribution uncertain
- Upper bound: Resonator Networks have ~5 years of demonstrated success on smaller compositional problems; substrate's structured codebook should help eigenvalue separation

**17th HONEST-RECALIBRATION-pattern note** of session: standard cleanup-crosstalk theory FALSIFIED for multi-hop large-N data; substrate-novel mechanism synthesis advanced; rehabilitation candidate identified with quantitative falsifiable predictions.

---

## (i) Cross-references

- [[research-betS-K-ceiling-2026-05-22]] (Entry 113; K-ceiling vs multi-hop N-degradation distinction)
- [[research-V2-substrate-evaluation-2026-05-21]] (Entry 52; V2.D modern dense AM refuted; resonator is non-AM-class alternative)
- [[research-RS-phase-capacity-mechanisms-2026-05-22]] (Entry 148; AMP/VAMP posterior inference family; this note extends to chain composition)
- [[research-Kerdock-RI-universality-2026-05-22]] (Entry 149; AMP universality; pre-test recipe applies to Resonator-Network compatibility check)
- [[research-cued-holistic-readout-primitive-2026-05-22]] (Entry 143; Bet Z.1 SRHT viable; Z.2 C2PO refuted)
- [[research-BetX-skill-composition-2026-05-21]] (Bet X skill composition; chain composition is structural sibling)

**Memory references invoked**:
- [[feedback-no-smoke]] — falsified crosstalk theory honestly
- [[feedback-materials-science-probe]] — random matrix eigenvalue clustering analog
- [[feedback-subagent-model-optimization]] — 2 Sonnet agents parallel
- [[feedback-query-privacy-decomposition]] — generic-math queries
- [[feedback-verify-implementations]] — 8 citations cross-verified for mechanism match
- [[feedback-rehabilitation-after-rejection]] — 5 rescue mechanism candidates ranked
- [[feedback-dont-dismiss-adjacent-methods]] — Agent G dug spectral lit (no direct multi-hop hit but adjacent); Agent H surfaced Resonator + VAMP convergence
- [[project-ai-memory-subsystem-direction]] — capability class 4 (cognitive composition) alignment
- [[feedback-loop-skill-usage]] — Monitor (b3gefibtp) caught inbound at 18:51:46

**End of note.**
