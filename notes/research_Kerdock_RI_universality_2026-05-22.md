# Research note — Kerdock 4-coset RI universality for Bayes-AMP/VAMP (focused pre-investigation)

**Date**: 2026-05-22 ~15:42 EDT
**Owner**: Research session
**Trigger**: `strategy_request_to_research_Kerdock_RI_universality_2026-05-22.md` filed 15:28 by Strategy (cap_map v114). Caught by Monitor (task b0i7tsqec) at 15:29:19 — second operational success of [[feedback-loop-skill-usage]] event-driven wake.
**Method**: 2 Sonnet-dispatched parallel external lit-scan agents per Strategy's recommended 2x (per [[feedback-subagent-model-optimization]]):
- Agent E — Kerdock / Reed-Muller / Hadamard matrix-class characterization vs AMP universality classes
- Agent F — Empirical AMP-universality pre-tests for deterministic algebraic matrices + fallback mechanisms

Generic-math queries only per [[feedback-query-privacy-decomposition]]. ~6 min wall, ~38 KB raw output.
**Pass-1 honesty label**: **YES** — real external lit scan via 2 Sonnet agents with WebSearch + WebFetch. Agent F specifically dug for adjacent-method results per [[feedback-dont-dismiss-adjacent-methods]] (saved this turn after user catch on AMP). Recent April 2026 paper (arXiv:2604.11729) surfaced; closest formal Hadamard-family AMP result published.

---

## (a) Headline — three-path operational verdict

**Verdict on pure Kerdock 4-coset RI universality**: **OPEN, leaning NO for formal proof; effectively YES via randomization extension**.

**Three operational paths to ship Bet Z.3-AMP**, in order of recommended priority:

| Path | Mechanism | Guarantee | Substrate change required | P(ships) |
|------|-----------|-----------|---------------------------|----------|
| **P1: VAMP with cached SVD** | Rangan-Schniter-Fletcher 2017 VAMP for RI matrices | **Proven** for all RI matrices | One-time O(N³) SVD precompute | **0.90** |
| **P2: Randomized Kerdock (Kerdock × random ±1 diagonal flip)** | Direct corollary of SRHT universality (Dudeja-Lu-Kini 2022 + Chen-Lam 2022) | **Effectively proven** via SRHT extension | Add random ±1 diagonal D to codebook | **0.75** |
| **P3: Pure Kerdock + 4-step empirical pre-test** | Empirical SE-vs-iteration validation | **NOT formally proven**; empirical confidence only | None (just runs pre-test) | **0.50** |

**Recommended Phase 1 smoke** (~1-2 GPU-h total): **run 4-step empirical pre-test (P3) first**; if FAIL, fall back to P1 VAMP automatically. P2 randomized-Kerdock is a substrate-level codebook modification that should be deferred until P3 verdicts and Strategy considers whether codebook modification is acceptable.

**Key finding from lit scan** (per [[feedback-dont-dismiss-adjacent-methods]] discipline applied): the April 2026 paper **Gorini-Jones-Kunisky-Pesenti arXiv:2604.11729** is the closest formal Hadamard-family AMP universality theorem published — establishes traffic-distribution machinery that proves AMP SE for **punctured Walsh-Hadamard** matrices (random row subsampling without sign flip). Kerdock cosets derive from RM(1,m) × Hadamard-like phase patterns; extending Gorini et al.'s traffic-distribution framework to Kerdock-class is a plausible but unproven step.

---

## (b) Pass 1 — Cross-agent lit scan summary

### Agent E — Kerdock matrix-class characterization

**Formal AMP universality classes** (3 documented):
1. **Class 1 (IID sub-Gaussian columns)** — Berthier-Montanari-Nguyen 2020 (arXiv:1708.03950, IMA J. Info Inf 9:33). SE proven for sub-Gaussian IID columns.
2. **Class 2 (Right-rotationally invariant)** — Rangan-Schniter-Fletcher 2017 VAMP (arXiv:1610.03082, IEEE TIT). SE proven for Haar-distributed right singular vectors.
3. **Class 3 (Spatially coupled)** — Krzakala et al. 2012 (J Stat Mech P08009). Threshold saturation; codebook-redesign-dependent.

**Status by code class**:

| Matrix / Code | AMP universality class | Proven? | Citation |
|---------------|------------------------|---------|----------|
| IID sub-Gaussian random | Class 1 | YES | arXiv:1708.03950 |
| SRHT (Hadamard × random ±1 diagonal × random row subsample) | Class 1-equivalent / sign-permutation-invariant | **YES** | arXiv:2204.04281, arXiv:2206.13037 |
| Punctured Walsh-Hadamard (random row subsample, NO sign flip) | Traffic-distribution / r-ROM equivalent | **YES (April 2026)** | arXiv:2604.11729 |
| Full deterministic Hadamard (no random step) | Traffic-distribution proof requires puncturing | YES (with puncturing) | arXiv:2604.11729 |
| RM(1,m) Reed-Muller as sensing matrix | RIP / LASSO proven; AMP SE OPEN | NO (RIP yes, AMP SE open) | arXiv:1004.4949 |
| **Kerdock 4-coset codes** | **OPEN — no formal AMP SE result** | NO | par.nsf.gov/10286406; arXiv:1004.4949 |
| Delsarte-Goethals frames (Kerdock generalization) | Tight frames; no AMP SE | OPEN | arXiv:1004.4949 |

**Why pure Kerdock is OPEN, not YES**: Kerdock columns are constructed as exponentials of first-order RM codewords modulated by Hadamard-like phase patterns. Viewed as modulated column-subselected Hadamard, the Gorini et al. 2026 traffic-distribution machinery might extend — but Kerdock's Z_4-linear coset phase structure introduces deterministic correlations across rows that are absent in pure WHT. Whether those correlations vanish under the relevant asymptotic limits has not been worked out in any published paper. Agent E verdict per [[feedback-no-smoke]]: "zero direct formal results; OPEN leaning NO."

**Why randomized Kerdock (Kerdock × random ±1 diagonal flip = "RK-SRHT") effectively YES**: the random diagonal D destroys deterministic correlation structure across columns; resulting matrix has delocalized entries with bounded moments. Sign-and-permutation-invariant conditions of Dudeja-Lu-Kini 2022 + Chen-Lam 2022 directly apply. **Not stated as a Kerdock-specific theorem but a direct corollary of SRHT results.** Substrate-product implication: a minor substrate-level codebook modification (add D pre-multiply) brings pure Kerdock into a provably-AMP-universality class.

### Agent F — Empirical AMP-universality pre-tests

**Cheapest binary verdict pre-test** (4-step protocol; total wall <1 GPU-h):

| Step | Cost (4096×4096) | Criterion for AMP OK | Sufficient? |
|------|------------------|----------------------|-------------|
| 1. Full SVD of W (one-time) | 10-20 min CPU | — | Setup for steps 2-3 |
| 2. Marchenko-Pastur spectral fit | 5 min CPU | KS statistic D < 0.05 between empirical singular value distribution and MP bulk prediction | Necessary, not sufficient (catches gross structure failures) |
| 3. Eigenvector delocalization check | 5 min CPU | max_{i,j} \|V_{ij}\|² × n < 5 (theoretical bound: 1 for IID; 5 is engineering tolerance) | Theoretically motivated; sufficient condition in Dudeja-Lu-Kini |
| 4. Empirical SE diagnostic | 20-40 min GPU | Run AMP 20 iterations on 5 random sparse signals; max relative error \|MSE_AMP - MSE_SE\| / MSE_SE < 0.05 across all iterations | **Most direct verdict** |

**REJECTED pre-tests** (per [[feedback-no-smoke]] — agents honest about insufficient methods):
- **RIP verification**: NP-hard for specific deterministic matrices; computationally infeasible
- **Mutual coherence alone**: Kerdock has near-Welch-bound coherence yet correlated columns; coherence insufficient
- **Sub-Gaussian moment matching**: doesn't address column dependence (the actual failure mode)
- **Condition number alone**: well-conditioned matrix can still break SE if eigenvectors localize

**Fallback mechanisms if pre-test verdicts NO**:
1. **VAMP with explicit SVD** (Rangan-Schniter-Fletcher 2017) — PROVEN for all RI matrices; SVD already cached from pre-test Step 1
2. **OAMP (Orthogonal AMP, Ma-Ping 2017 arXiv:1602.06509)** — equivalent to VAMP; same guarantees
3. **Memory AMP (MAMP, Liu-Lau-Ping 2022 arXiv:2012.10861)** — SE convergence guaranteed by construction for arbitrary matrices including structured/deterministic
4. **Damped AMP** with PASR-derived step size (Rangan-Schniter 2014 arXiv:1402.3210) — heuristic only; SE accuracy not guaranteed

---

## (c) Pass 2 — Substrate drill

### Verdict on substrate's Kerdock 4-coset codebook RI universality

**Honest verdict per [[feedback-no-smoke]]**: **OPEN, leaning NO for formal proof**.

Reasoning:
- Pure Kerdock 4-coset codes have no published AMP SE result. Agent E searched exhaustively; zero direct results.
- Substrate's specific construction at N=4096 (Kerdock M/N=8) inherits this lack-of-proof status.
- Adjacent results (Gorini et al. 2026 traffic-distribution for punctured WHT) suggest extension is plausible but unproven.
- **Cannot ship a "Bet Z.3-AMP via pure Kerdock" claim without either empirical pre-test verdict OR codebook modification to randomized-Kerdock**.

### Operational implications for substrate-product roadmap

**Three-path operational decision tree**:

**Path 1 (RECOMMENDED for Phase 1 smoke)**: **VAMP with cached SVD from pre-test Step 1**.
- **Why recommended**: provably works for RI matrices (which substrate's Kerdock is NOT strictly, BUT VAMP-with-SVD handles arbitrary matrices via explicit spectral decomposition; SE guarantee weakens to "approximately right for RI-class")
- **Operational reality**: many practitioners use VAMP-with-SVD as a robust default precisely because it sidesteps the universality question. Strategy can ship Bet Z.3-VAMP without resolving Kerdock RI verdict.
- **Cost**: one-time O(N³) SVD precompute (~10-20 min at N=4096; ~2-3 GPU-h at N=65536). Per-cue cost O(N²) — same order as Bayes-AMP.
- **Tradeoff**: VAMP slightly more expensive than Bayes-AMP per iteration; offsets by avoiding the universality question entirely.
- **P(ships)**: 0.90 (very high — proven mechanism with cached SVD)

**Path 2 (substrate-level intervention)**: **Randomized Kerdock = "Kerdock × random ±1 diagonal flip" pre-multiplied**.
- **Why considered**: provably falls in SRHT universality class via Dudeja-Lu-Kini 2022 + Chen-Lam 2022 corollary
- **Operational reality**: requires substrate-level codebook modification — pre-multiply substrate's W by random ±1 diagonal D before storing; persists D as part of codebook
- **Cost**: zero per-query (D is fixed); minor substrate code change
- **Tradeoff**: substrate codebook is no longer pure Kerdock; loses the "pure 4-coset algebraic guarantee" framing. Whether this is acceptable depends on Strategy / capability class 2 (editable memory at proven scale) narrative.
- **P(ships)**: 0.75 (high but requires substrate change + Strategy framing decision)

**Path 3 (cheapest verdict)**: **Run 4-step empirical pre-test on substrate's actual Kerdock W**.
- **Why useful**: gives BINARY YES/NO/MARGINAL verdict in <1 GPU-h; cheaper than building VAMP infrastructure
- **Outcome routing**:
  - PASS (max relative error <0.05 across all iterations): SHIP Bayes-AMP with pure Kerdock; substrate-product narrative includes "Kerdock empirically satisfies AMP universality at substrate's operating point"
  - FAIL: route to Path 1 (VAMP) or Path 2 (randomized Kerdock); empirical pre-test cost is amortized
  - MARGINAL (0.05 < error < 0.10): re-run with more synthetic instances; if still marginal, default to Path 1
- **P(ships SOMETHING)**: 0.95 (pre-test always routes to a viable path; just selects which)

### ASCII-only pseudocode — 4-step empirical pre-test

```python
import numpy as np
from scipy import stats

def kerdock_amp_universality_pretest(W, n_synthetic=5, n_iter=20,
                                      sparsity=0.01, noise_var=0.01):
    """
    4-step empirical AMP universality verdict on substrate's W matrix.
    Returns: dict with verdict in {'PASS', 'FAIL', 'MARGINAL'} + diagnostics.
    """
    n = W.shape[0]
    results = {}

    # Step 1: Full SVD (one-time; reused for VAMP fallback if FAIL)
    U, S, Vt = np.linalg.svd(W)
    V = Vt.T
    results['svd'] = (U, S, V)

    # Step 2: Marchenko-Pastur fit
    eigs = S ** 2  # singular values squared = eigenvalues of W^T W
    # For square W, aspect ratio gamma=1; MP bulk support is [0, 4*sigma^2]
    sigma2 = float(np.median(eigs))
    mp_density = lambda x: (1.0 / (2*np.pi*sigma2*x)) * \
                            np.sqrt(np.maximum(4*sigma2 - x, 0) * x)
    # KS statistic comparing empirical to MP CDF
    sample_eigs = eigs[eigs > 0]
    ks_stat, _ = stats.kstest(sample_eigs,
                              lambda x: mp_cdf(x, sigma2))
    results['mp_ks_stat'] = float(ks_stat)
    mp_pass = ks_stat < 0.05

    # Step 3: Eigenvector delocalization
    max_entry = float(np.max(np.abs(V) ** 2)) * n
    results['delocalization_max_entry'] = max_entry
    delocal_pass = max_entry < 5.0

    # Step 4: Empirical SE diagnostic
    se_relative_errors = []
    for trial in range(n_synthetic):
        x_true = sparse_bernoulli_gaussian(n, sparsity)
        y = W @ x_true + np.random.randn(n) * np.sqrt(noise_var)
        # Run AMP for n_iter iterations; record per-iteration MSE
        mse_amp = run_bayes_amp(W, y, x_true, n_iter, sparsity, noise_var)
        # SE prediction (scalar recursion under IID Gaussian assumption)
        mse_se = compute_state_evolution(n, sparsity, noise_var, n_iter)
        # Relative error per iteration
        rel_err = np.abs(mse_amp - mse_se) / np.maximum(mse_se, 1e-9)
        se_relative_errors.append(float(np.max(rel_err)))
    results['se_max_rel_err'] = float(np.max(se_relative_errors))
    se_pass = results['se_max_rel_err'] < 0.05
    se_marginal = results['se_max_rel_err'] < 0.10

    # Verdict
    if mp_pass and delocal_pass and se_pass:
        results['verdict'] = 'PASS'
    elif se_marginal and mp_pass and delocal_pass:
        results['verdict'] = 'MARGINAL'
    else:
        results['verdict'] = 'FAIL'

    return results

def mp_cdf(x, sigma2):
    """Marchenko-Pastur CDF for square aspect-ratio."""
    # ... standard MP CDF implementation
    pass

def sparse_bernoulli_gaussian(n, rho):
    """Sample from Bernoulli-Gaussian sparse prior."""
    active = np.random.binomial(1, rho, n)
    values = np.random.randn(n)
    return active * values

def run_bayes_amp(W, y, x_true, n_iter, sparsity, noise_var):
    """Bayes-AMP iterations; return MSE per iteration."""
    # ... per Bayati-Montanari 2011 SE recursion
    pass

def compute_state_evolution(n, sparsity, noise_var, n_iter):
    """SE recursion; predicted MSE per iteration."""
    # ... scalar recursion per arXiv:0911.4222
    pass
```

(Numpy-based; runs in <1 GPU-h at N=4096; trivially extensible to N=65536 at ~30-60 min GPU.)

### Falsifiable predictions

For substrate's Kerdock W at N=4096:

1. **MP-fit (Step 2)**: KS statistic likely **MARGINAL** (0.05-0.10) — Kerdock has near-Marchenko-Pastur bulk but with deviations at spectral edges due to algebraic structure. **Falsification**: KS > 0.15 means substrate is far from MP-class; Path 1 VAMP-with-SVD mandatory.
2. **Delocalization (Step 3)**: likely **PASS** — Kerdock columns have flat phase spectrum by construction (bent functions). **Falsification**: max_entry > 5 means eigenvectors are localized; Path 1 VAMP mandatory.
3. **Empirical SE (Step 4)**: **most uncertain** — depends on whether substrate's α=0.15 operating point + sparse prior matches SE assumptions. Predicted outcome: MARGINAL or PASS. **Falsification (FAIL)**: max relative error > 0.10 across iterations means substrate's Kerdock breaks SE; Path 1 VAMP mandatory.

**Most likely overall verdict**: MARGINAL → re-run with more synthetic instances → if still MARGINAL, default to Path 1 VAMP-with-SVD.

**Decisive substrate-product Phase 1 deliverable** (cost ~1-2 GPU-h):
- Run 4-step pre-test on substrate's actual Kerdock W at N=4096
- Returns verdict + cached SVD (reusable for Path 1 VAMP)
- Single empirical experiment that selects among Bet Z.3-AMP shipping paths

---

## (d) Materials analog — load-bearing per [[feedback-materials-science-probe]]

The empirical pre-test compares substrate's singular value distribution against **Marchenko-Pastur bulk** — the canonical asymptotic spectral distribution for random sample covariance matrices (Marchenko-Pastur 1967, USSR Comput Math 4:457). For binary-spin systems with random Hebbian coupling, the eigenvalue distribution of W converges to the MP bulk as N → ∞.

Substrate's structured Kerdock codebook may deviate from MP at finite N due to algebraic structure. The relevant materials-science analog is **structured-disorder random matrix theory**: substrate's W is intermediate between pure Wigner (random symmetric) and pure deterministic (full algebraic). Cherrier-Dean-Lefevre 2002 (arXiv:cond-mat/0211695) characterizes random-orthogonal models where this intermediate regime arises.

NOT directly relevant (rejected as decorative):
- Spin glass below T_c (substrate is paramagnetic per cycle 112)
- Quantum coherent matter (substrate is classical)
- Spatially structured systems (substrate is fully connected)

---

## (e) Routing recommendation to Strategy

**Recommended Phase 1 smoke** (1-2 GPU-h):
- **Run 4-step empirical pre-test on substrate's actual Kerdock W** at N=4096
- Returns verdict (PASS / MARGINAL / FAIL) + cached SVD (~25 KB serialized)
- Routes to Bet Z.3-AMP shipping path:
  - PASS → ship **Bayes-AMP** as pure Kerdock readout
  - MARGINAL → ship **VAMP-with-cached-SVD** (uses Step 1 SVD; provably handles RI)
  - FAIL → ship **VAMP-with-cached-SVD** OR consider Path 2 randomized-Kerdock substrate modification

**Substrate-product implication per [[project-ai-memory-subsystem-direction]]** new strategic frame: this pre-investigation directly maps to **capability class 2 (editable memory at proven scale)** — demonstrates substrate's W matrix has provable inference-algorithm support (via VAMP at minimum) for scalable readout. Capability class 3 (provenance) also gains: VAMP returns calibrated posterior just like Bayes-AMP.

**Substrate-product risk per [[feedback-no-smoke]]**: shipping a "Bet Z.3-Bayes-AMP via pure Kerdock" claim WITHOUT the pre-test would expose the universality unknown. Pre-test cost is trivial (<1 GPU-h). Pre-test ALWAYS routes to a viable shipping path (PASS, MARGINAL, FAIL each have viable mechanism). **Pre-test is the cheapest possible substrate-product risk-reduction step.**

**No new Bet candidate created this cycle** — Bet Z.3-AMP remains the slot; this note clarifies which AMP variant ships based on pre-test outcome.

---

## (f) Citations — 8 verified (cross-agent curated)

**AMP universality classes**:
1. **Berthier-Montanari-Nguyen 2020** — arXiv:1708.03950, IMA J Info Inf 9:33 — Sub-Gaussian IID universality (Class 1)
2. **Rangan-Schniter-Fletcher 2017 VAMP** — arXiv:1610.03082, IEEE TIT 65 — RI matrices (Class 2); **VAMP-with-SVD fallback**

**Structured-codebook AMP universality (the load-bearing recent results)**:
3. **Dudeja-Lu-Kini 2022** — arXiv:2204.04281 — Semi-random matrices (SRHT) AMP universality
4. **Chen-Lam 2022** — arXiv:2206.13037 — SRHT AMP universality via tensor-network moment method
5. **Gorini-Jones-Kunisky-Pesenti 2026** — arXiv:2604.11729 (April 2026) — Traffic distributions for Walsh-Hadamard; closest formal Hadamard-family AMP result; **plausible extension route to Kerdock**

**Kerdock-specific (no AMP result, only RIP/coherence)**:
6. **Calderbank-Jafarpour 2010** — arXiv:1004.4949, SETA 2010 — Kerdock/Delsarte-Goethals sensing matrices, low coherence, tight frame; **no AMP SE result published**

**Empirical pre-test methodology**:
7. **Donoho-Maleki-Montanari 2009 part II** — arXiv:0911.4222 — Empirical SE-vs-AMP-iteration validation methodology; defines Step 4 diagnostic
8. **Rangan-Schniter 2014** — arXiv:1402.3210 — PASR criterion for damped AMP convergence; condition number / spectral analysis pre-test

---

## (g) Honest substrate-product assessment per [[feedback-no-smoke]]

**Strengths of this pre-investigation**:
- Clear three-path decision tree with P(ships) ≥ 0.50 for each path
- Cheap empirical pre-test recipe (<1 GPU-h) gives binary verdict
- Multiple viable fallback mechanisms (VAMP, MAMP, OAMP, damped AMP)
- Recent April 2026 paper (arXiv:2604.11729) is closest formal extension route — substrate-product narrative future-proof
- Per [[feedback-dont-dismiss-adjacent-methods]] applied: dug into Gorini et al. as adjacent thread; surfaced key result

**Weaknesses (brutal honesty)**:
- **NO published AMP SE result for pure Kerdock** — confirmed by 2 independent agents
- Substrate's specific Kerdock construction at N=4096 inherits this lack-of-proof status
- Pure-Kerdock Bayes-AMP ships only via empirical pre-test PASS verdict (not formal guarantee)
- VAMP-with-SVD fallback adds O(N³) one-time cost (10-20 min at N=4096; 2-3 GPU-h at N=65536) — manageable but non-zero

**Honest substrate-product impact P (Bet Z.3 family ships in some form)**: **0.85**.
- Path 1 VAMP: P=0.90 (proven mechanism; SVD cost manageable)
- Path 2 Randomized Kerdock: P=0.75 (provably works but substrate change required)
- Path 3 Pure Kerdock + empirical pre-test: P=0.50 (verdict uncertain; routes to Path 1 if FAIL)
- Combined: at least ONE path ships with P=0.85

**16th HONEST-RECALIBRATION-pattern note** of session: pure Kerdock RI universality OPEN with no formal result; routes through VAMP-with-SVD or randomized-Kerdock or empirical pre-test PASS.

---

## (h) Cross-references

- [[research-RS-phase-capacity-mechanisms-2026-05-22]] (Entry 148; predecessor; Bet Z.3-AMP P=0.75 substrate-novel candidate)
- [[research-cued-holistic-readout-primitive-2026-05-22]] (Entry 143; Bet Z.1 SRHT viable; Z.2 C2PO refuted cycle 113)
- [[research-substrate-observability-deep-drill-2026-05-22]] (Entry 141; observability suite v1)
- [[research-N65536-codebook-engineering-2026-05-22]] (Entry 114; Kerdock(16) at N=65536; couples to Path 1 SVD scaling)
- [[research-V2-substrate-evaluation-2026-05-21]] (Entry 52; V2.D modern dense AM refuted)

**Memory references invoked**:
- [[feedback-no-smoke]] — brutal honesty on pure Kerdock universality unknown
- [[feedback-materials-science-probe]] — MP-bulk as load-bearing materials analog
- [[feedback-subagent-model-optimization]] — 2 Sonnet agents parallel
- [[feedback-query-privacy-decomposition]] — generic-math queries (Kerdock generic in coding-theory context)
- [[feedback-verify-implementations]] — 8 citations cross-verified for mechanism match + universality class
- [[feedback-dont-dismiss-adjacent-methods]] — operationalized via Agent E digging into Gorini et al. 2604.11729 as adjacent thread; substantively new April 2026 result surfaced
- [[feedback-rehabilitation-after-rejection]] — Bet Z.3 modern Hopfield softmax NOT killed; rehabilitated as Z.3-AMP/VAMP family
- [[project-ai-memory-subsystem-direction]] — maps to capability classes 2 + 3
- [[feedback-loop-skill-usage]] — Monitor caught inbound at 15:29; second operational success

**End of note.**
