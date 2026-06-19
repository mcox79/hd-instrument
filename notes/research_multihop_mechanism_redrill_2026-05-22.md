# Research note — Multi-hop N=65536 mechanism RE-DIAGNOSIS + revised rehabilitation (post-Resonator-refutation)

**Date**: 2026-05-22 ~19:30 EDT
**Owner**: Research session
**Trigger**: `strategy_request_to_research_multihop_mechanism_redrill_2026-05-22.md` filed 19:17 by Strategy (cap_map v124). Monitor caught at 19:17:51. **2x-research-after-rejection drill** per user directive "2x negative research right".
**Method**: 3 fresh Sonnet-dispatched parallel external lit-scan agents (per Strategy's recommended 2-3x):
- Agent I — High-D mechanisms (curse of dim / hubness / DPI / Markov walk / information bound)
- Agent J — Revised rehabilitation candidates (excluding refuted Resonator)
- Agent K — Codebook + substrate-level restructuring + V3 trigger criteria

Generic-math queries only per [[feedback-query-privacy-decomposition]]. ~7 min wall, ~57 KB raw output.
**Pass-1 honesty label**: **YES** — real external lit scan via 3 Sonnet agents with WebSearch + WebFetch. Generic-math queries. All agents informed of cycle-124 refutations to avoid re-proposing Resonator.

---

## (a) HONEST acknowledgment of Entry 151 calibration failure per [[feedback-no-smoke]]

**My Entry 151 predicted**:
- Signal-eigenvalue-near-degeneracy mechanism (Agent G): P=0.70
- Resonator Network rehabilitation: P=0.65, acc_50hop ∈ [0.45, 0.65]

**Cycle 124 empirical results**:
- Spectral validation smoke: **SPECTRAL_FLAT** — eigenvalue cluster prediction FALSIFIED
- Resonator FULL: acc_50hop = **0.200** (UNDERPERFORMED argmax baseline 0.250)

**Calibration miss**: Resonator P=0.65 with predicted range [0.45, 0.65] → actual 0.200. Hard-fail threshold (<0.30) breached. **Both hypotheses wrong**.

**Calibration discipline applied this cycle**: all P estimates below deflated ~0.15-0.25 from agent baseline. Top candidate P does NOT exceed 0.50. **Saving as memory**: lit-scan-based predictions can be wildly wrong when substrate is in uncharted regime; calibration must penalize confident predictions accordingly.

---

## (b) NEW mechanism diagnosis (replacing falsified eigenvalue-degeneracy)

**KEY NEW META-FINDING (cross-agent)**: the empirical data (1-hop=0.983 IDENTICAL across N + plateau at 0.22 ≫ random 0.01) constrain the mechanism tightly. The constraints rule out:
- Distance concentration alone (would also degrade 1-hop)
- Pure noise saturation (plateau at 0.22, not 0.01)
- Eigenvalue degeneracy (FALSIFIED at smoke)
- Resonator-class iterative-posterior cycling (FALSIFIED at FULL)

**Surviving primary diagnosis (combined P=0.45)**: **Hubness × DPI information contraction**.

Mechanism story:
1. **Hubness (Radovanović-Nanopoulos-Ivanović 2010, JMLR 11:2487)** — in high-D, k-occurrence distribution becomes skewed; a small subset of codebook patterns ("hubs") appear as nearest neighbor of many other patterns. At N=4096 hub effect mild; at N=65536 hub effect strong.
2. **DPI / Data Processing Inequality contraction** — chain composition X₀ → X₁ → ... → X₅₀ is a Markov chain; mutual information I(X₀; X_n) ≤ C^n × I(X₀; X₁) where C is per-hop channel contractivity < 1. Compounding over 50 hops with C ≈ 0.95 gives floor ~ 0.08; with hubness creating near-absorbing states, floor rises to ~0.22.
3. **Plateau explanation**: once chain enters a hub's basin, repeated argmax cleanup keeps it there; the 0.22 plateau equals stationary distribution mass on non-hub correct attractors.
4. **3.5× degradation N=4096→N=65536**: as N grows, hub effect amplifies; effective channel contractivity C drops; DPI bound tightens.

**Quantitative consistency**:
- Per-hop retention at N=4096: 0.9947 (1-hop clean, smooth chain)
- Per-hop retention at N=65536 (from depth 5): 0.958 (early-chain) → drops to 0.944 mid-chain → plateaus
- Non-stationary per-hop retention = signature of absorbing-state dynamics (Agent I)

**Other surviving candidates** (lower P; not mutually exclusive with hubness × DPI):
- Walk dynamics in absorbing-state Markov chain (P=0.35) — overlaps with hubness story
- Distance concentration with non-uniform discriminability (P=0.30) — partial contributor
- Volume concentration alone (P=0.15) — insufficient on its own

**Rejected explicitly**:
- Standard crosstalk (K-1)/N — already falsified
- Eigenvalue near-degeneracy — falsified cycle 124
- Resonator-class iterative-posterior cycling — falsified cycle 124
- Emergent pattern correlations at scale — no mechanism in lit

---

## (c) NEW top rehabilitation candidate (post-Resonator refutation)

**KEY STRUCTURAL DISTINCTION uncovered by Agent J**: Resonator failed because it is **LOOPY-ITERATIVE** — re-applies posterior correction within a hop, creating fixed-point cycling in high-interference regimes. The chain itself is a TREE (no loops). Tree-exact methods (forward-backward EP / VAMP-on-chain) are **structurally different** from Resonator and do NOT share its failure mode.

**Top rehabilitation candidate (P=0.40)**: **VAMP-on-chain forward-backward EP** (single-pass, NOT iterative within hops).

Why structurally different from Resonator:
- Chain has NO LOOPS (just sequential hops). Forward-backward message passing is tree-exact — analogous to Kalman smoother (exact on chains by construction).
- Resonator iterates WITHIN each hop trying to resolve posterior superposition → cycles when interference high. VAMP forward-backward passes WITHIN-HOP cleanup once; messages flow ACROSS hops to incorporate downstream evidence into upstream beliefs.
- Mechanism directly addresses chain degradation: each hop's cleanup benefits from full chain context, not just local noisy input.

**Revised rehabilitation candidate ranking** (all P heavily deflated per calibration penalty):

| Candidate | Structural class vs Resonator | Substrate change | Calibrated P |
|-----------|------------------------------|------------------|--------------|
| **VAMP-on-chain (forward-backward EP, single-pass)** | DIFFERENT (tree-exact, not loopy) | Readout-only | **0.40** (TOP) |
| Per-hop sparse cleanup filter | DIFFERENT (threshold per hop, not iterative) | Readout-only | 0.38 |
| Bidirectional single-pass EP | DIFFERENT (Betteti-Baggio-Zampieri 2026 two-timescale class) | Readout-only | 0.30 |
| Hierarchical multi-scale binding | DIFFERENT (compresses chain depth via hierarchy) | Codebook redesign | 0.28 |
| Resonator Network iteration | REFUTED at FULL | — | 0.00 (out) |

**Critical caveat**: even VAMP-on-chain may NOT clear acc_50hop > 0.5 at N=65536 K=100. Binary ±1 codebook violates VAMP's Gaussian-prior assumption; tree-exact VAMP may still hit the same information-theoretic capacity ceiling (DPI bound). **If single-pass VAMP-on-chain also fails, that pushes substrate-product roadmap toward V3 substrate investigation.**

---

## (d) Substrate-level (V3) candidates if all readout rehabilitation fails

Per Agent K's substrate-level lit scan + V3 trigger criteria:

| Substrate change | Mechanism | Redesign cost | Calibrated P |
|------------------|-----------|---------------|--------------|
| **Sparse codebook (Tsodyks-Feigelman 1988)** | Reduce per-hop crosstalk ∝ M·a² instead of M | LOW (codebook only) | **0.35** |
| Asymmetric directed W (Derrida-Gardner-Zippelius 1987) | Direct chain coupling; no symmetric crosstalk accumulation | HIGH (changes problem class to hetero-assoc) | 0.50 (P higher but blocks auto-assoc) |
| Clique codes (Gripon-Berrou 2011) | Clustered block-sparse, O(N log N) capacity | MEDIUM | 0.45 |
| Redundancy-maximization weights (Bodnar 2025 arXiv:2511.02584) | PID-trained W; Hopfield capacity 0.14 → 1.59 | LOW (weight rule only) | 0.35 |
| Long-Sequence Hopfield Memory (arXiv:2306.04532) | Nonlinear kernel for sequence elements | MEDIUM | 0.40 |

**V3 trigger criteria (Agent K synthesis from lit)**:
1. Per-hop accuracy excellent (≥0.95) + chain accuracy collapses super-linearly with depth = **GEOMETRIC failure, not dynamics**. Substrate-level intervention warranted. **Substrate matches this condition.**
2. Multiple independent readout methods plateau below chance-beating thresholds = energy landscape lacks directional structure for chaining (Ramsauer 2020 ICLR 2021 documents spurious meta-stable attractors no readout can escape).
3. Tsodyks-Feigelman threshold: M > α_c(a) · N → per-hop error floors non-zero by construction. Must reduce M or sparsify.

**Substrate's empirical pattern (per-hop OK + chain collapse) matches V3 trigger #1.** This is the strongest substrate-product implication: if VAMP-on-chain also fails, V3 sparse-codebook investigation is the next path.

---

## (e) Pass 2 — Operational synthesis

### ASCII-only pseudocode: hub census (cheapest diagnostic test)

```python
import numpy as np

def hub_census(codebook, N=65536, K=100):
    """
    Cheapest empirical test for hubness mechanism.
    codebook: K x N matrix of stored ±1 codewords.
    Returns: k-occurrence distribution + hub concentration metrics.
    """
    # Compute K x K similarity matrix
    sim = codebook @ codebook.T / N  # K x K cosine
    np.fill_diagonal(sim, -np.inf)   # exclude self-NN
    # For each codeword i, find its top-k nearest neighbors
    # (k=1 = nearest neighbor of i)
    nearest = np.argmax(sim, axis=1)  # length K
    # k-occurrence: how many times does each codeword appear as someone's NN?
    k_occurrence = np.bincount(nearest, minlength=K)
    # Hub concentration metrics
    skewness = float(np.mean(((k_occurrence - k_occurrence.mean()) /
                              k_occurrence.std() + 1e-9) ** 3))
    top10_share = float(np.sort(k_occurrence)[-10:].sum() / K)
    hubness_score = skewness  # > 1.0 = significant hubness
    return {
        'k_occurrence': k_occurrence,
        'skewness': skewness,
        'top10_hub_share': top10_share,
        'hubness_present': skewness > 1.0
    }
```

**Cost**: ~5 min CPU at N=65536 K=100. Single matrix multiply + bincount.

### ASCII-only pseudocode: single-pass VAMP-on-chain (top rehabilitation)

```python
def vamp_chain_forward_backward(W, codebook, query, depth=50,
                                 prior_sparsity=0.01):
    """
    Tree-exact forward-backward EP on chain.
    NOT iterative within hops — single forward + single backward pass.
    Structurally different from Resonator's loopy iteration.
    """
    K, N = codebook.shape
    # Forward pass — compute soft posterior at each hop
    forward_post = []
    q = query.copy()
    for hop in range(depth):
        scores = codebook @ q  # K-vector log-likelihoods
        # Soft posterior with sparse prior
        log_post = scores - logsumexp(scores)
        forward_post.append(log_post)
        # Apply W for next hop using POSTERIOR EXPECTATION not argmax
        weights = np.exp(log_post)
        weights /= weights.sum()
        q_expected = (weights[:, np.newaxis] * codebook).sum(axis=0)
        q = np.sign(W @ q_expected)
    # Backward pass — incorporate downstream evidence
    backward_msg = np.zeros(K)
    smoothed_post = []
    for hop in reversed(range(depth)):
        smoothed = forward_post[hop] + backward_msg
        smoothed = smoothed - logsumexp(smoothed)
        smoothed_post.insert(0, smoothed)
        # Update backward message for next hop back
        backward_msg = log_chain_transition(smoothed, codebook)
    # Commit hard codewords from smoothed posteriors
    chain = [int(np.argmax(p)) for p in smoothed_post]
    return chain, smoothed_post

def logsumexp(x):
    m = np.max(x)
    return m + np.log(np.sum(np.exp(x - m)))

def log_chain_transition(post, codebook):
    """Log P(next | current) under chain transition model."""
    # Approximate via expected next-hop given current posterior
    weights = np.exp(post - np.max(post))
    weights /= weights.sum()
    return weights @ codebook  # K-vector message
```

**Cost**: O(D·K·N) total = 50·100·65536 ≈ 3.3×10⁸ ops per chain. ~30 sec at GPU throughput.

### Falsifiable predictions (calibrated)

For substrate at N=65536, K=100:

1. **Hub census test** (~5 min CPU):
   - If hubness_present (skewness > 1.0) AND top10_hub_share > 0.30: **hubness × DPI mechanism CONFIRMED**. Diagnosis aligned with empirical data.
   - If hubness absent (skewness < 0.5): mechanism is something else (most likely DPI contraction without hubness, or another mechanism not yet surfaced).

2. **VAMP-on-chain rehabilitation** (~30 min GPU):
   - Predicted acc_50hop: **0.30 - 0.50** (median 0.40, calibration-deflated)
   - **Hard fail threshold**: acc_50hop < 0.25 → tree-exact methods don't help; V3 substrate restructuring needed
   - **Soft success**: 0.30 < acc_50hop < 0.50 → mechanism partially diagnosed; iterate
   - **Strong success**: acc_50hop > 0.50 → rehabilitation works; deploy

3. **Per-hop conditional accuracy test**:
   - P(X_{t+1} = correct | X_t = wrong) at N=65536: if ≈ 0 → absorbing-state trapping confirmed
   - Same metric at N=4096: if ≈ 0.1-0.3 → non-trivial recovery (consistent with weaker hubness)
   - This test directly distinguishes hubness from pure noise

4. **Sparse codebook V3 test** (if VAMP fails): Tsodyks-Feigelman a=0.05 codebook at N=65536 K=100 → predicted acc_50hop in [0.30, 0.50] from theory.

---

## (f) Materials analog — load-bearing per [[feedback-materials-science-probe]]

The hubness × DPI mechanism has a direct materials-physics analog:
- **High-dimensional similarity hubness** (Radovanović 2010) = high-D random vector geometry with non-uniform centrality measure; analogous to **random matrix product trapping in attractor basins** (Cohen-Newman 1984 Lyapunov exponents).
- **DPI contraction over Markov chain** = classical-statistical-mechanics **mixing time / spectral gap** (Levin-Peres-Wilmer 2017). Substrate's chain composition has a Markov chain interpretation with K-state transition matrix; mixing time determined by spectral gap of transition matrix.
- **Plateau at 0.22 ≫ random 0.01** = stationary distribution mass on non-hub correct attractors; analogous to **biased random walk on disordered energy landscape**.

NOT relevant (per [[feedback-no-smoke]]):
- Spin glasses below T_c (substrate is RS-phase)
- Continuous-variable systems with phonon dispersion
- Quantum coherent matter

---

## (g) Routing recommendation to Strategy

**Recommended Phase 1 smoke** (~10-40 GPU-min total; decisive in 1 cycle):

1. **Hub census test** (~5 min CPU): cheapest diagnostic; directly validates/refutes new mechanism diagnosis
2. **VAMP-on-chain forward-backward smoke** (~10 GPU-min) at K=10, depth=20 for fast verdict
3. **Per-hop conditional accuracy diagnostic** (~5 GPU-min): distinguishes hubness from pure noise
4. **If steps 1-3 negative**: proceed to V3 substrate investigation (sparse codebook Tsodyks-Feigelman P=0.35)

**V3 substrate investigation pathway** (if all readout-side fails):
- **Sparse codebook (Tsodyks-Feigelman)** = LOWEST cost / theoretical-direct mechanism — recommended V3 path
- **Asymmetric directed W (Derrida-Gardner-Zippelius)** = HIGHEST P but changes problem class (auto-assoc → hetero-assoc) — substrate-product narrative cost
- **Redundancy-maximization weights (Bodnar 2025)** = LOW cost weight-rule-only change — backup V3 path

**Strategic significance per [[project-ai-memory-subsystem-direction]]**:
- Maps to capability class 4 (cognitive architecture composition)
- Lane D agent memory SDK Demo 1 depends on chain composition at N=65536
- If VAMP-on-chain works (P=0.40): substrate-product narrative includes "iterative-posterior readout via tree-exact forward-backward EP — structurally distinct from Resonator's failure mode"
- If VAMP fails AND V3 sparse codebook works (combined P~0.50): substrate-product narrative pivots to "substrate operates optimally with sparse codebook for deep-chain composition"
- If BOTH fail: substrate-product chain-composition story remains 1-hop excellent; multi-hop bounded at moderate N (4096-8192 range)

---

## (h) Honest substrate-product assessment per [[feedback-no-smoke]]

**Strengths of this re-diagnosis**:
- ALL previous hypotheses (crosstalk, eigenvalue degeneracy, Resonator) FALSIFIED honestly
- New mechanism candidates surfaced via [[feedback-dont-dismiss-adjacent-methods]] discipline (hubness lit + DPI lit + tree-exact-vs-loopy structural distinction)
- Calibration penalty applied throughout (all P deflated from baseline)
- Hub census is cheapest possible decisive empirical test (~5 min CPU)
- V3 substrate-level pathway identified with cost-vs-P tradeoff

**Weaknesses (brutal)**:
- **Combined hubness × DPI mechanism has P=0.45 — NOT confidently diagnosed**. May also be wrong.
- VAMP-on-chain P=0.40 (calibrated) is LOWER than Resonator's P=0.65 was; honest about uncertainty
- Substrate may be in a regime where NO published rehabilitation works (chain composition at N=65536 K=100 with fully-connected binary ±1 dense codebook)
- If hub census shows skewness < 0.5, this entire re-diagnosis is also wrong (need another iteration)

**Honest substrate-product impact P (some rehabilitation ships)**: **0.40 - 0.55**.
- Lower bound 0.40: VAMP-on-chain may also fail; substrate truly may be in uncharted territory at this regime
- Upper bound 0.55: V3 sparse-codebook fallback has cheap-cost / theoretical-direct mechanism; some path likely ships

**18th HONEST-RECALIBRATION-pattern note** of session. **Calibration discipline operational**: all P estimates penalized; range conservative; hard-fail thresholds explicit.

**Memory saved this cycle**: lit-scan-based predictions can be wildly wrong when substrate is in uncharted regime. **Calibration penalty mandatory** for any P > 0.5 in such contexts.

---

## (i) Citations — 8 verified (cross-agent merged)

**New mechanism (hubness + DPI)**:
1. **Radovanović-Nanopoulos-Ivanović 2010** — JMLR 11:2487 — Hubs in space (KEY new framework)
2. **Beyer-Goldstein-Ramakrishnan-Shaft 1999** — ICDT Springer LNCS 1540 — "When is nearest neighbor meaningful?" foundational distance concentration
3. **Polyanskiy-Wu 2015** — arXiv:1512.06429 — Strong DPI for input-constrained additive noise channels
4. **Zhang et al. 2024** — arXiv:2401.00422 — Curse of dimensionality unified treatment

**Top rehabilitation (VAMP-on-chain tree-exact)**:
5. **Rangan-Schniter-Fletcher 2017 VAMP** — arXiv:1610.03082 — Forward-backward EP foundational
6. **Minka 2001** — UAI 2001, arXiv:1301.2294 — Expectation Propagation foundational

**Substrate-level (V3 pathway)**:
7. **Tsodyks-Feigelman 1988** — EPL 6:101 — Sparse coding capacity boost (V3 primary path)
8. **Betteti-Baggio-Zampieri 2026** — arXiv:2603.03201 — Sequential retrieval dynamical theory (NEW March 2026 result; identifies "collapse regime" matching substrate's failure mode)

**Cross-references**:
- [[research-multihop-chain-rehabilitation-N65536-2026-05-22]] (Entry 151; FALSIFIED; this note supersedes)
- [[research-RS-phase-capacity-mechanisms-2026-05-22]] (Entry 148; AMP/VAMP family; VAMP-on-chain extends Entry 148 sub-q 3)
- [[research-Kerdock-RI-universality-2026-05-22]] (Entry 149; AMP universality pre-test recipe applies to VAMP-on-chain too)

---

## (j) Memory references invoked

- [[feedback-no-smoke]] — Entry 151 calibration failure acknowledged openly
- [[feedback-rehabilitation-after-rejection]] — applying 2x-research drill (cycle 125 second attempt per Strategy cycle 93 → cycle 100 precedent)
- [[feedback-dont-dismiss-adjacent-methods]] — hubness lit + DPI lit + tree-exact-vs-loopy structural distinction all surfaced via discipline
- [[feedback-subagent-model-optimization]] — 3 Sonnet agents parallel
- [[feedback-query-privacy-decomposition]] — generic-math queries
- [[feedback-verify-implementations]] — 8 citations cross-verified
- [[feedback-materials-science-probe]] — hubness + DPI + Markov mixing time analogs load-bearing
- [[project-ai-memory-subsystem-direction]] — capability class 4 alignment
- [[feedback-loop-skill-usage]] — Monitor (b3gefibtp) caught inbound at 19:17:51

**End of note.**
