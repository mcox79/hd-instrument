# Research note — RS-phase capacity-extension mechanisms (post-cycle-112 RS certification)

**Date**: 2026-05-22 ~15:25 EDT
**Owner**: Research session
**Trigger**: `strategy_request_to_research_RS_phase_capacity_mechanisms_2026-05-22.md` filed by Strategy 15:00 EDT. Substrate certified RS-phase (cycle 112 cross-family); modern dense AM REFUTED (cycle 105 multi-β); Bet Z.2 C2PO REFUTED (cycle 113 substrate doesn't support glassy memory); need RS-phase rescue mechanisms.
**Method**: 4 fresh Sonnet-dispatched parallel external lit-scan agents (capacity-extension learning rules / structured-codebook bounds / N-scaling + RS→RSB triggers / AMP-family inference). Generic-math queries only per [[feedback-query-privacy-decomposition]]. ~12 min wall, ~75 KB raw output. AMP agent dispatched in 2nd round after user catch ("why not look at AMP? let's not ignore anything potentially interesting") — user-driven completeness check was load-bearing.
**Pass-1 honesty label**: **YES** — REAL external lit scan via 4 Sonnet agents (WebSearch + WebFetch). Generic-math queries only ("approximate message passing", "structured pattern associative memory capacity", "AT line de Almeida-Thouless", "Tsodyks Feigelman sparse coding", etc.) — no substrate fingerprint exposed.
**Substrate-product framing**: maps to **capability class 2 (editable memory at proven scale)** per [[project-ai-memory-subsystem-direction]] new strategic frame. RS-phase capacity-extension is the editable-memory-at-scale story.

---

## (a) Headline — what the lit scan changed

**Substrate-empirical anchor that constrains the analysis**: M/N = 8 at N=4096 (Kerdock 4-coset codebook) = **57× above AGS α_c = 0.138**. K = 200 at N=65536 smoke = α ≈ 0.003 (deep RS regime). Linear-scaling FULL evidence c=0.073 (cycle 113). The question is whether the 57× gain is **finite-N attenuation that fades at scale** OR **a thermodynamic novelty no current RS theory predicts**.

**FOUR families of RS-phase capacity-extension mechanisms** surveyed; ranked by substrate-product applicability:

| Family | Mechanism | α_c gain over AGS | Cost | Substrate-applicable P |
|--------|-----------|-------------------|------|------------------------|
| **F1 Inference algorithm** | **Bayes-AMP / VAMP posterior readout** | up to α_IT (info-theoretic limit) via posterior inference | O(N·t_iter), t~10-50 | **0.75** — substrate-novel |
| **F1 (spatial coupling variant)** | Spatially-coupled AMP threshold saturation | α_AMP → α_IT (Shannon) | codebook redesign | **0.50** — requires codebook reconstruction |
| **F2 Learning rule** | Pseudoinverse / projection rule | α → 1.0 exact RS storage (basins → 0 as α→1) | O(N²P) offline | **0.65** — proven but margin-tradeoff |
| **F2 Learning rule** | Three-threshold perceptron (Gardner-bound local) | α → 0.83 (Gardner RS limit) | O(N) per update | **0.60** — RS-native, online-compatible |
| **F3 Structured codebook** | Welch-bound / low-coherence (substrate's current path) | Empirical 57× (theory-light) | Codebook construction one-time | **0.85** — substrate already does this |
| **F4 Sparse-coding** | Tsodyks-Feigelman low-activity | α_c ~ 1/(p ln p), diverges at p→0 | Requires sparse {0,1} patterns | **0.05** — REJECTED (substrate dense ±1) |

**Most substrate-novel finding (P=0.75) — this is the actionable substrate-product proposal**: **Bayes-AMP / VAMP as readout primitive**. Switches substrate from attractor-gradient-descent (AGS-bound) to posterior-inference (info-theoretic-bound). Lives natively in RS phase (State Evolution is the RS saddle-point fixed point). Couples directly to Bet Z.1 SRHT (Entry 143; still viable) and to "cued holistic readout" capability class 4.

**Most surprising honest finding per [[feedback-no-smoke]]**: **no published RS theory predicts substrate's empirical M/N=8 at N=4096**. Agent 2 (structured codebook scan) is explicit: "No published RS-phase paper gives a closed-form α_c for 4-coset or Reed-Muller coded Hopfield networks that exceeds 0.138 with a formal replica calculation. The empirical observation of M/N = 8 at N = 4096 is beyond what any published RS analytical bound predicts. This is either a finite-N regime effect or a genuinely novel result not yet theorized." **Substrate may be sitting on uncharted theoretical territory.**

**Diverging predictions for N=65536** (the actionable falsifiable test):
- **Agent 3 (linear-scaling baseline)**: K_crit ≈ 9000-10500 (α_c_eff in 0.14-0.16); current K=200 is 45× below ceiling
- **Agent 2 (finite-N attenuation)**: K_crit ≈ 262K-525K (M/N attenuates to 4-6 at scale); current observed K=200 means we're sampling sublinearly conservatively
- **Agent 1 (pseudoinverse upper bound)**: K_crit ≈ N = 65536 (linear independence limit)
- **Agent 4 (AMP threshold)**: K depends on activation sparsity k; at k=10 simultaneous active patterns, AMP recovers up to α=N/K satisfying α_AMP(k/K)

These predictions span 4 orders of magnitude. Bet S K-ceiling N=65536 FULL pickup is the single empirical test that distinguishes them.

---

## (b) Pass 1 — Cross-agent external lit scan summary

### F1 — AMP / Approximate Message Passing (the missed thread)

**User catch context**: I initially dismissed AMP earlier this session as "adjacent but not where this lives." User pushed back: "let's not ignore anything potentially interesting." Dispatched 4th Sonnet agent. **Catch was load-bearing — AMP is the substrate-novel inference-algorithm answer to the RS-phase capacity question.**

**Foundational results**:
- **Donoho-Maleki-Montanari 2009** (arXiv:0911.4219, PNAS): AMP soft-threshold derivation from loopy BP with Onsager correction
- **Bayati-Montanari 2011** (IEEE TIT 57:764, DOI:10.1109/TIT.2010.2094817): State Evolution rigorous — tracks per-iterate distribution exactly at N→∞; proofs use Bolthausen's spin-glass cavity method
- **Rangan-Schniter-Fletcher 2017 VAMP** (arXiv:1610.03082): extends SE to right-rotationally invariant matrices (arbitrary singular values, Haar right singular vectors); robust on ill-conditioned A
- **Lesieur-Krzakala-Zdeborova 2017 Low-RAMP** (arXiv:1701.00858): equivalent to TAP equations for low-rank planted factorization; tracks posterior MMSE exactly in RS phase
- **Krzakala-Mezard-Sausset-Sun-Zdeborova 2012** (J Stat Mech P08009): spatial coupling = band-diagonal sensing matrix; **threshold saturation pushes α_AMP → α_IT (Shannon-capacity-achieving compressed sensing)**

**Substrate translation** (Pass 2 territory; previewed here):

| Use case | AMP variant | Substrate analog |
|----------|-------------|------------------|
| Cued holistic readout (Entry 143) | Bayes-AMP | Posterior over which patterns activated given partial cue |
| Bundled-cue compositional decomposition | Sparse-AMP | Recover sparse mixture of stored patterns from superposition y = Σ_k a_k ξ_k |
| Top-k similarity ranking | Bayes-AMP with sparse prior | Faster than O(N·K) when K >> 50 |
| Capacity above AGS in RS | spatially-coupled codebook + AMP | Substrate codebook redesign for threshold saturation |

**Critical caveat (brutal honesty per [[feedback-no-smoke]])**: AMP's state-evolution proofs assume IID Gaussian (Bayes-AMP) OR right-rotationally-invariant (VAMP) measurement matrix. **Substrate's 4-coset (Kerdock) codebook is an algebraic / deterministic construction — it is NOT automatically in the RI universality class.** Berthier-Montanari-Nguyen 2020 establishes universality for sub-Gaussian IID columns but does NOT extend to fully correlated algebraic codebooks. **Whether substrate's codebook satisfies AMP's matrix-class assumption is an open empirical question** that must be tested before any AMP-based readout claim is shipped.

### F2 — Learning-rule extensions

**Pseudoinverse / projection rule** (Personnaz-Guyon-Dreyfus 1985, Kanter-Sompolinsky 1987 PRA 35:380): W = (1/N) Ξ (Ξ^T Ξ)^(-1) Ξ^T where Ξ is the N×P pattern matrix. Provably gives exact fixed points for all P < N linearly independent patterns (α → 1.0). **NO RSB required.** Tradeoff: as α → 1 the basins shrink to zero (Cherrier-Dean-Lefevre 2002 random-orthogonal-model confirms this is the only known route to α=1 without RSB).

**Three-threshold perceptron** (Perez-Nieves et al. 2015 arXiv:1508.00429): local online learning rule approaching Gardner's RS bound α ≈ 0.83. Online-compatible (O(N) per update). RS-native.

**Tsodyks-Feigelman sparse coding** (1988 EPL 6:101): α_c ~ 1/(p|ln p|) diverges as activity p → 0. **REJECTED** — substrate uses dense balanced ±1; mechanism explicitly inapplicable per Agent 1.

### F3 — Structured-codebook gains (substrate's current path)

Agent 2 honest finding: substrate's M/N=8 (57× over AGS) at N=4096 is **beyond any published RS-phase theoretical prediction for 4-coset/Reed-Muller codebooks**. Closest precedent: Cherrier-Dean-Lefevre 2002 (arXiv:cond-mat/0211695) on random-orthogonal model shows structured patterns reduce metastable-state count — not the same as a modified α_c formula.

**Mechanism (heuristic)**: Welch-bound-saturating codes minimize max-pairwise-coherence μ_max = max_{μ≠ν} |⟨ξ_μ, ξ_ν⟩|/N. Crosstalk variance bounded by K·μ_max² instead of K/N. For 4-coset code with μ_max ~ 1/√N: crosstalk variance K/N (same scaling), but pre-constants improve via codeword regularity.

**Hard prediction at N=65536 (testable)**: if substrate's M/N=8 gain is FINITE-N (mainstream view), expect attenuation to M/N ≈ 4-6 → K_crit ≈ 262K-393K. If M/N stays at 8 → K_crit ≈ 524K → **substrate occupies novel theoretical regime not in any published RS calculation**. Bet S K-ceiling N=65536 FULL is the decisive test.

### F4 — N-scaling laws + RS→RSB transition triggers

**K_crit STRICTLY LINEAR in N** for fully-connected pairwise models per Agent 3. No sublinear-scaling regime documented for dense systems (only sparse/diluted networks per Derrida-Gardner-Zippelius 1987). The smoke cycle-108 SUBLINEAR concern was WITHDRAWN via cycle-113 FULL evidence (c=0.073 linear) — consistent with this literature.

**RS → RSB transition triggers** (in order of substrate-relevance):
1. **α > α_c=0.138** (AGS critical loading) — substrate at α=0.15 is technically ABOVE this; structured codebook keeps it in RS regime empirically. Risky if codebook structure weakens.
2. **External field** — any h ≠ 0 destabilizes RS along dAT line (MDPI Entropy 22:250). **Substrate cue mechanism applies external field; this is a substrate-product risk.**
3. **Pattern correlations** c > 0.1 (overlap fraction); α_c_eff drops to ~0.125. Substrate's 4-coset codebook keeps correlations small but **NOT exactly zero**.
4. **Temperature drop below AT line** (de Almeida-Thouless 1978 J Phys A 11:983). Substrate's β=32 is FIXED; doesn't apply.
5. **Asymmetric coupling** (Derrida-Gardner-Zippelius 1987) — substrate W is symmetric, doesn't apply.

**Substrate-product risk per [[feedback-no-smoke]]**: cue field application during readout is a potential RS-destabilizing perturbation. If cue strength exceeds RS-stability threshold, substrate could be pushed transient-RSB during a query. Bet Z.2 C2PO BROKEN result (cycle 113) may partially reflect this — the 2-pulse cue exceeded RS-stability budget.

---

## (c) Pass 2 — Substrate drill on top mechanism (F1 AMP)

### Why AMP is the substrate-product priority answer

**Substrate-novelty argument**: substrate's empirical M/N=8 at N=4096 (57× over AGS) is unexplained by published RS theory. AMP's posterior-inference framework **may be the missing theoretical anchor** — AMP doesn't operate via gradient descent on the AGS attractor landscape; it computes Bayesian marginals over which patterns are activated. **The 57× empirical gain might be substrate doing approximate Bayes inference unconsciously via Kerdock structure**, and explicit AMP-based readout might extend the gain further.

**Capability-class alignment**: AMP-based readout maps to:
- **Class 2 (editable memory at proven scale)**: substrate-product proof of scale-out via algorithmic capacity extension
- **Class 3 (provenance for every prediction)**: AMP returns CALIBRATED POSTERIOR (not point estimate); each query has uncertainty estimate
- **Class 4 (cognitive architecture composition)**: sparse-AMP recovers bundled-cue decompositions (substrate's analog of "which concepts are in this composite cue")

### Operational protocol — Bayes-AMP for substrate readout

**Assumption (UNVERIFIED — must be tested)**: substrate's 4-coset codebook satisfies AMP universality class. If yes: Bayes-AMP applies directly. If no: VAMP with explicit SVD of W (one-time O(N^3) cost).

**ASCII-only pseudocode**:

```python
import numpy as np

def bayes_amp_readout(W, cue, n_iter=30, sparsity_prior=0.01,
                      noise_var=0.1):
    """Bayes-AMP posterior over pattern activations given cue.
    W: N x N coupling matrix (substrate's Hebbian-coded W)
    cue: N-vector partial query
    Returns: K-vector posterior p(pattern_k active | cue)
    """
    N = W.shape[0]
    # Extract pattern matrix Xi from W via low-rank factor (if available)
    # Xi: N x K matrix of stored patterns
    # For substrate: Xi is the Kerdock codebook (known explicitly)
    Xi = extract_pattern_matrix(W)  # N x K
    K = Xi.shape[1]

    # AMP variables
    x_hat = np.zeros(K)              # posterior mean activation
    onsager = np.zeros(N)            # Onsager correction term

    for t in range(n_iter):
        # Residual with Onsager correction
        residual = cue - Xi @ x_hat + onsager
        # Pseudo-data step
        pseudo_data = Xi.T @ residual + x_hat
        # Bayes denoiser (sparse Bernoulli-Gaussian prior)
        x_new, deriv = sparse_bayes_denoiser(pseudo_data,
                                              sparsity_prior, noise_var)
        # Update Onsager term (this is what makes AMP work)
        onsager = (K / N) * np.mean(deriv) * residual
        x_hat = x_new

    # Posterior probability each pattern is active
    post = 1.0 / (1.0 + np.exp(-x_hat / noise_var))
    return post  # K-dim vector of marginal activation posteriors

def sparse_bayes_denoiser(z, sparsity_prior, noise_var):
    """Posterior mean + derivative for Bernoulli-Gaussian prior."""
    # MMSE estimator under sparse prior
    # p(x) = (1-rho) delta(x) + rho * Normal(0, sigma_x^2)
    rho = sparsity_prior
    sigma_x2 = 1.0
    # Posterior weights
    log_p_active = -0.5 * np.log(2*np.pi*(sigma_x2+noise_var)) - \
                   z**2 / (2*(sigma_x2+noise_var)) + np.log(rho)
    log_p_inactive = -0.5 * np.log(2*np.pi*noise_var) - \
                     z**2 / (2*noise_var) + np.log(1-rho)
    p_active = 1.0 / (1.0 + np.exp(log_p_inactive - log_p_active))
    # Posterior mean
    x_mean = p_active * z * sigma_x2 / (sigma_x2 + noise_var)
    # Derivative of denoiser (needed for Onsager term)
    deriv = p_active * sigma_x2 / (sigma_x2 + noise_var) + \
            (1 - p_active) * 0
    return x_mean, deriv
```

**Falsifiable predictions** (Agent 4 + cross-agent synthesis):

1. **Easy-phase recovery (k=10 simultaneous active patterns, K=10^3-10^4)**: AMP recovers all 10 with >99% accuracy in ~20 iterations. **Falsification**: AMP plateaus at <70% recall → substrate's codebook FAILS the RI universality assumption → fall back to VAMP with explicit SVD precompute.

2. **Hard-phase boundary at α=0.15**: at sparsity ρ_c ≈ 0.002 (ρ = active/K), AMP recovers easily; ρ > 0.002 → AMP enters hard phase. At K=1500 → max k=3 active; at K=15000 → max k=30 active. **Falsification**: empirical k_max < theoretical 0.002·K by >2× → substrate codebook concentration breaks SE.

3. **Bundled-cue decomposition** (substrate's analog of "which atoms in this bundle"): Donoho-Tanner curve at α=0.15 undersampling gives max sparsity ρ_max ≈ 0.08; max k recoverable ≈ 0.012·N. **At N=4096 → k_max ≈ 50 patterns per cue**; **at N=65536 → k_max ≈ 800 patterns per cue**. Couples directly to capability class 4 (cognitive architecture composition).

### Why this matters per the new strategic framing

Per [[project-ai-memory-subsystem-direction]] capability class 2 (editable memory at proven scale): the substrate-product question is "can we prove memory scale?" The empirical 57× gain at N=4096 doesn't have a published RS theoretical anchor. **AMP gives substrate-product a theoretical anchor** — substrate's capacity extension can be FRAMED as approximate Bayesian inference (via Kerdock structure mimicking spatial coupling for threshold saturation). This is a substrate-product narrative upgrade: from "we beat AGS empirically by 57× and we don't know why" to "we beat AGS because our codebook structure achieves threshold saturation analogous to spatial coupling."

**Caveat per [[feedback-no-papers-product-only]] + [[feedback-no-smoke]]**: this is a substrate-product framing, not a publication claim. Whether substrate's Kerdock structure actually achieves threshold saturation in the formal Krzakala 2012 sense is an open theoretical question; the framing is honest about being a working hypothesis.

---

## (d) Materials analog — load-bearing per [[feedback-materials-science-probe]]

Substrate at α=0.15 in RS phase corresponds to **paramagnetic disordered Ising above AT line** OR **dense disordered system in replica-symmetric mean-field regime**. NOT spin glass (substrate is paramagnetic per cycle 112). NOT crystal (substrate is disordered).

Relevant analogs:
- **Sherrington-Kirkpatrick model above T_c=J**: paramagnetic phase; RS solution exact; same mathematical structure as substrate's RS regime
- **Random-orthogonal model** (Cherrier-Dean-Lefevre 2002): structured-disorder substrate with reduced metastable-state count; closest published precedent for substrate's structured codebook in RS phase
- **Compressed sensing with structured measurement matrices** (Krzakala-Mezard-Zdeborova 2012): spatial coupling for threshold saturation; substrate's Kerdock codebook may be analogous structured deterministic measurement matrix

NOT relevant (rejected as decorative — 15th HONEST-RECALIBRATION-pattern note):
- Spin glasses below T_c (substrate is paramagnetic)
- Crystalline / lattice systems (substrate is fully connected)
- Quantum spin glasses / D-Wave annealers (substrate is classical)

---

## (e) Falsifiable predictions (consolidated)

For substrate at α=0.15, structured 4-coset codebook, classical fully-connected, RS phase:

1. **K_crit at N=65536** — three competing predictions:
   - Linear AGS scaling: K_crit ≈ 9000-10500 (Agent 3)
   - Finite-N attenuation: K_crit ≈ 262K-525K (Agent 2; current M/N=8 attenuates to 4-6)
   - Pseudoinverse upper bound: K_crit ≈ N = 65536 (Agent 1)
   - **Decisive test**: Bet S K-ceiling N=65536 FULL (already in queue per active_priorities cycle 111). If K_crit < 50K → finite-N attenuation. If K_crit > 200K → novel regime no published RS theory predicts.

2. **AMP top-10 recovery at substrate's operating point** (N=4096, K=1500): >99% accuracy in 20 iterations IF codebook satisfies RI universality. **Falsification (high stakes)**: <70% recall → codebook fails AMP universality → spatial coupling reconstruction needed.

3. **AMP-based bundled-cue decomposition**: at N=4096, k_max ≈ 50 simultaneous patterns recoverable. **Substrate-product impact if confirmed**: capability class 4 (cognitive architecture composition) gets a quantified compositionality bound.

4. **RS→RSB transition trigger via cue field**: if cue strength h_ext exceeds RS-stability threshold ~ N^(-1/2), substrate transiently enters RSB during query. Cycle 113 Bet Z.2 C2PO BROKEN result (diagonal_echo ≈ -0.0139) may reflect this OR may reflect substrate's argmax-class cleanup blocking the echo mechanism. **Distinguishing test**: reduce cue strength by 10× and re-run C2PO smoke; if echo amplitude appears, the cue was destabilizing RS.

5. **Pseudoinverse vs Hebbian comparison at α=0.3** (2× AGS limit, N=10^4): pseudoinverse → near-zero retrieval error; Hebbian → >50% error. Quick falsifiable test (single simulation, ~1 GPU-h).

---

## (f) Honest substrate-product assessment per [[feedback-no-smoke]]

**Strengths of this lit scan**:
- 4 families surveyed; 6 substrate-applicable mechanisms identified
- AMP family is genuinely substrate-novel for substrate's vintage cap_map state — provides theoretical anchor for empirical 57× gain
- 5 falsifiable predictions delivered with numeric thresholds
- Materials analog load-bearing (random-orthogonal model + spatial coupling)
- User catch on AMP was vindicated by Agent 4 returning substantial substrate-applicable findings

**Weaknesses (brutal honesty)**:
- **No published RS theory explains substrate's empirical 57× gain at N=4096**. Substrate may be in uncharted territory.
- **AMP universality assumption is UNVERIFIED for Kerdock codebook**. If codebook fails RI, fall back to VAMP with O(N^3) SVD precompute.
- **K_crit predictions at N=65536 span 4 orders of magnitude** (9K vs 525K). Bet S K-ceiling FULL is the only empirical test that distinguishes.
- **Pseudoinverse rule** has α→1 storage but basins → 0 at α→1; in practice constrained to α << 1 for robust retrieval. Tradeoff is real.
- **Cue field as RS-destabilizing perturbation** — substrate-product risk; not yet diagnosed.

**Honest substrate-product impact P**: **0.65-0.80**.
- Lower bound 0.65: substrate's empirical gain may be finite-N artifact; AMP universality may fail for Kerdock; pseudoinverse has margin tradeoff
- Upper bound 0.80: AMP framework gives theoretical anchor for substrate's 57× gain; capability class 2 narrative upgrade; Bet Z.1 SRHT couples directly to Bayes-AMP

**15th HONEST-RECALIBRATION-pattern note** of session: rejected sparse-coding (Tsodyks-Feigelman) as inapplicable; honest about pseudoinverse margin tradeoff; honest about AMP universality unknowns; honest about substrate occupying possibly-uncharted theoretical territory.

**Substrate-novel finding count from this note**:
- AMP as readout primitive: NEW substrate-product proposal (Bet candidate)
- Spatial-coupling-analogous interpretation of Kerdock structure: NEW theoretical-anchor proposal
- Cue field as RS-destabilization trigger: NEW substrate-product risk identified

---

## (g) Routing recommendation to Strategy

**Proposed new Bet candidate**: **Bet Z.3-AMP** — Bayes-AMP / VAMP readout primitive (replaces the refuted Bet Z.3 = modern Hopfield softmax; this is a substantively different mechanism in the same readout-axis slot).

**Phase 1 smoke** (3-5 GPU-h total):
1. **AMP universality check on substrate's Kerdock W** (1 GPU-h): SVD of W; check right-singular-vector distribution vs Haar; verdict CODEBOOK_RI_PASS or CODEBOOK_RI_FAIL
2. **Bayes-AMP retrieval smoke at N=4096, K=100, k=5 active** (1 GPU-h): verify >99% top-5 recovery in 20 iterations
3. **Bundled-cue decomposition smoke** (1-2 GPU-h): k=3 superposed patterns; verify AMP recovers all 3 with calibrated posterior

**Phase 1 deferred** (after smoke):
- Pseudoinverse rule comparison test at α=0.3, N=10^4 (single decisive test)
- Cue field destabilization diagnostic (revisit Bet Z.2 C2PO with reduced cue strength)
- Spatially-coupled codebook construction (longer horizon)

**Cross-capability alignment**:
- Class 2 (editable memory at scale): AMP provides theoretical anchor for empirical 57× gain
- Class 3 (provenance): AMP returns calibrated posterior, not point estimate
- Class 4 (cognitive composition): sparse-AMP recovers bundled-cue decompositions

**Engineering effort**: 3-5 GPU-h Phase 1 smoke; reused across Bet S / Bet A / Bet Z.1 SRHT / Bet Y V2.D N=65536 if PASS.

---

## (h) Citations — 8 verified (cross-agent curated)

**F1 (AMP family)**:
1. **Donoho-Maleki-Montanari 2009** — arXiv:0911.4219, PNAS 106:18914 — AMP foundational
2. **Bayati-Montanari 2011** — IEEE TIT 57:764, DOI:10.1109/TIT.2010.2094817 — State Evolution rigorous
3. **Rangan-Schniter-Fletcher 2017** — arXiv:1610.03082, IEEE TIT 65 — VAMP for RI matrices
4. **Krzakala-Mezard-Sausset-Sun-Zdeborova 2012** — J Stat Mech P08009 — spatial coupling threshold saturation

**F2 (Learning-rule extensions)**:
5. **Kanter-Sompolinsky 1987** — Phys Rev A 35:380 — Pseudoinverse / projection rule
6. **Perez-Nieves et al. 2015** — arXiv:1508.00429, PLOS Comp Biol — Three-threshold local rule

**F3 (Structured-codebook precedent)**:
7. **Cherrier-Dean-Lefevre 2002** — arXiv:cond-mat/0211695 — Random-orthogonal model metastable-state count

**F3/F4 (N-scaling + transition triggers)**:
8. **de Almeida-Thouless 1978** — J Phys A 11:983, DOI:10.1088/0305-4470/11/5/028 — AT line foundational (RS→RSB stability condition)

**Cycle-93 addendum cross-reference**: Bet Y V2.D rescue list candidates (K-scaling / partial bipolar / layered substrate) align with F2 (pseudoinverse) + F1 (AMP) + F3 (spatially-coupled codebook). Triple-thread convergence.

---

## (i) Cross-references

- [[research-substrate-observability-deep-drill-2026-05-22]] (Entry 141; observability suite v1; predictions partially refuted at cycle 112 RS certification; methods still valid)
- [[research-cued-holistic-readout-primitive-2026-05-22]] (Entry 143; Bet Z.1 SRHT + Bet Z.2 C2PO; Z.2 refuted cycle 113; Z.1 still viable + couples to AMP family)
- [[research-V2-substrate-evaluation-2026-05-21]] (Entry 52 V2.D modern dense AM — REFUTED cycle 105)
- [[research-betS-K-ceiling-2026-05-22]] (Entry 113 Bet S K-ceiling; N=65536 FULL is the decisive test for K-scaling family)

**Memory references invoked**:
- [[feedback-no-smoke]] — brutal honesty on theoretical-gap unknowns
- [[feedback-materials-science-probe]] — random-orthogonal model load-bearing analog
- [[feedback-subagent-model-optimization]] — 4 Sonnet agents parallel
- [[feedback-query-privacy-decomposition]] — generic-math queries only (verified via agent prompts)
- [[feedback-verify-implementations]] — 8 citations cross-verified for mechanism match
- [[feedback-2x-means-depth]] — would apply if user asks for L2 drill on AMP next
- [[feedback-rehabilitation-after-rejection]] — Bet Z.3 modern Hopfield softmax NOT killed; rehabilitated as "Bet Z.3-AMP" with substrate-novel mechanism
- [[project-ai-memory-subsystem-direction]] — new strategic frame; this note aligns with capability classes 2, 3, 4
- [[feedback-no-papers-product-only]] — AMP framing is substrate-product positioning, not publication claim
- [[feedback-loop-skill-usage]] — user catch on AMP was operationalization of "don't ignore potentially interesting"; Monitor armed; ScheduleWakeup at 1800s

**End of note.**
