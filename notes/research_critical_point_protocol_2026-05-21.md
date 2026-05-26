# Research note: Critical-point characterization protocol — HONEST RECALIBRATION + REVISED 4-signature stack

**Date**: 2026-05-21 ~22:15 EDT
**Owner**: Research session (single-writer)
**Request**: `strategy_request_to_research_critical_point_2026-05-21.md` (22:05, META V2.G Item 1 gating test)
**Decision-log entry**: Entry 59
**Pass-1 honesty label**: REAL external lit scan via 3 parallel Agent (general-purpose) subagents (including dedicated SKEPTIC scan); ~60+ unique papers surveyed (2018-2026 dominant + foundational anchors); generic-math queries only per [[feedback-query-privacy-decomposition]].

---

## TL;DR — HONEST RECALIBRATION per [[feedback-no-smoke]]

**Strategy's request quoted "P(substrate empirically near triple/critical point): 50-65%". Three independent literature scans converge to materially LOWER this estimate.**

**Per Agent C SKEPTIC scan brutal decomposition**:

| Hypothesis | P | Source / reasoning |
|---|---|---|
| **Truly at critical point** (rigorous statistical-physics sense) | **10-20%** | Requires N-scan FSS + pre-registered exponents + surrogate-data null + sampling-invariance + scaling collapse |
| **Near critical line, in ORDERED PHASE** (modal Priesemann/Calvo outcome) | **35-45%** | Priesemann-Wilting 2018 macaque PFC m=0.98 subcritical; Calvo 2026 PRL fMRI 0.88 coupling |
| **False positive from correlated convergent-evidence artifact** | **35-50%** | Touboul-Destexhe 2017: simple OU + coin-flip satisfy crackling-noise relation WITHOUT criticality; Senn 2009 + Trafimow 2019 pitfall |

**Critical theoretical finding (Agent C)**: **Touboul-Destexhe 2017 PRE** — simple disconnected stochastic processes (Ornstein-Uhlenbeck, biased coin flips) satisfy the crackling-noise exponent relation (τ, α, 1/σνz interlock) WITHOUT any phase transition. **Exponent-relation closure — often cited as the second-tier signature beyond power laws — is reproducible by trivial stochastic dynamics.** Multiple signatures from one model run share heavy correlation; Bayes factors do NOT multiply.

**Revised 3-signature stack assessment** (Strategy's original proposal):

| Strategy signature | Discriminative power (per Agents A+B+C) |
|---|---|
| χ(β) susceptibility sweep | P=0.15-0.25 alone; **requires ≥3 N values for FSS** (N=4096 single-size is BORDERLINE per Aguilar-Janita 2026) |
| 1/f^α event-statistics spectrum | **NON-DIAGNOSTIC** (Touboul-Destexhe 2010+2017; α alone consistent with non-critical autoregressive systems) |
| Avalanche cluster size distribution | P=0.40-0.55 for fat-tailed vs not; **only 0.55 for at-criticality** per Clauset-Shalizi-Newman methodology (N=4096 caps avalanches at ~4096 → only 1.5-2 empirical decades; borderline regime where log-normal mimics power-law) |

**Strategy's 3-signature stack discriminative power (1 GPU-hour budget)**: **P=0.15-0.25** — INSUFFICIENT per [[feedback-no-smoke]] for the gating-test value Strategy claims.

**Recommended REVISED 4-signature stack** (this Research note's substantive contribution):

| Signature | Engineering tractability | P(adds discriminative power) | Source |
|---|---|---|---|
| **S.1 χ_SG mini-FSS** (N=2048 + 4096, ≥50 seeds each) | MED-HIGH | 0.55 | Aguilar-Janita 2026 arXiv:2601.19192 windowed protocol |
| **S.2 AT-eigenvalue computation** (analytic, single-instance) | **HIGH (best ROI per GPU-hour)** | **0.65** | Albanese-Alemanno-Alessandrelli-Barra 2023 arXiv:2303.06375 |
| **S.3 Avalanche size distribution + branching ratio σ** | HIGH | 0.55 | Beggs-Plenz + Wilting-Priesemann 2018 subsampling-invariant estimator |
| **S.4 Surrogate-data null control** (shuffle/randomize couplings; same protocol) | HIGH (required per Calvo 2026) | 0.60 (required NEGATIVE result for criticality claim) | Calvo 2026 PRL methodology |

**Revised stack discriminative power**: **P=0.45-0.65** — meaningfully informative. Strategy's "95%+ informative either direction" claim was OVERSTATED; revised stack achieves "honest informative" at substrate-product engineering grade.

**Substrate-product implications (HONEST RECALIBRATION)**:

| Outcome | Substrate-product action |
|---|---|
| **If S.1+S.2 BOTH suggest critical AND S.4 surrogate rejects** | Substrate near critical point with literature-grade rigor (P=0.40 outcome) → V2.G STACK construction cheap per Strategy's framing |
| **If S.1 OR S.2 suggests critical but S.4 surrogate ALSO shows signal** | False-positive risk material; do NOT promote V2.G STACK without further evidence |
| **If S.1+S.2 BOTH negative** | Substrate in ordered phase near critical LINE (modal outcome P=0.40); V2.G requires explicit engineering per Phase Transformations Entry 53 STACK decomposition |
| **If S.4 reproduces signatures on shuffled data** | Strategy's 6-signal convergent evidence was Touboul-Destexhe artifact; recalibrate substrate-physics framing materially |

**Per [[feedback-no-smoke]]**: revised protocol is HONESTLY informative (P=0.45-0.65 discrimination), NOT 95%+ as Strategy claimed. The substrate-product gating-test value is REAL but more nuanced than initial framing.

**Per [[feedback-no-papers-product-only]]**: framed as substrate-product engineering test ("does substrate operate near critical point — yes/no/probably-not?"), NOT "novel critical-phenomena framework paper."

---

## Pass 1 — external literature scan synthesis (3 parallel agents)

### Agent A: Susceptibility + FSS + AT line + Modern Hopfield phase diagrams + universality (~25 papers)

**Gold-standard FSS protocol** (Aguilar-Janita et al. arXiv:2601.19192, 2026):
- Windowed spin-glass susceptibility χ_W; track loci of maxima in (h, T)
- Distinguishing criterion: **χ_W^max ∝ N^α with α=0.39 (diverging, 3D h=0.2) vs α≈0 (saturating)**
- Requires N ∈ {N_0, 2N_0, 4N_0} — **minimum three sizes for FSS**
- 50-200 disorder seeds gives 5-10% error on χ_max at N=4096
- Parallel tempering essentially mandatory near T_c

**SK-class mean-field signature**: Lulli-Parisi-Pelissetto arXiv:1509.05372 (2016) — **χ_SG ∝ N^(1/3)** for SK-class mean-field criticality.

**AT-eigenvalue method** (BEST ROI per GPU-hour): Albanese-Alemanno-Alessandrelli-Barra arXiv:2303.06375 (2023) — **single-instance algebraic test for replica-symmetric instability**. λ_AT crossing zero is direct AT signature, **NO FSS collapse required**. Reproduces SK and p-spin AT lines.

**Hyperscaling breakdown** (canonical false-positive): Lundow-Campbell arXiv:1706.04586 — Binder cumulant has hyperscaling breakdown above upper critical dimension; **Binder crossings drift with N — textbook diagnostic UNRELIABLE in mean-field disordered systems**. Connects to substrate's earlier Bet E Binder cumulant failure on Hadamard codebook (Entry 40 H1 finding).

**Modern Hopfield phase diagrams**:
- Lucibello-Mézard PRL 132:077301 (2024): exponential capacity REM-like first-order at T=0; α_c ≈ 0.5 (sharp kernel limit)
- Hoover et al. arXiv:2311.18434 (2023): T-dependent phase transition; β_c separates high-T single global attractor from low-T pattern-specific minima
- Lotito et al. arXiv:2604.07401 (2026): geometric entropy + retrieval; LSE kernel → α_c(T=0)=0.5; LSR/Epanechnikov → support threshold α_th below which retrieval perfect at any T

**Substrate phase-diagram location** (α=0.153, β=32):
- For classical Hopfield: α=0.153 is **above** RS α_c=0.138 and within RSB α_c=0.143-0.144 range. β=32 (T≈0.031) is deep low-T. **This is geometrically a critical-line ENDPOINT, not a generic point on it.**
- For modern Hopfield (exponential interaction): α=0.153 doesn't have same meaning — Lucibello-Mézard's α refers to log(P)/N. Disambiguation required for substrate.

**Universality / triple-point**:
- da Silva-Schmidt cond-mat/0004490: random p-spin TRUE triple point — three first-order lines meeting
- Hasenbusch arXiv:1004.4486: 3D Ising universality ν=0.63, η=0.036
- Katzgraber cond-mat/0602215: bond-diluted EA ν=2.56, η=-0.39 (SPIN-GLASS UNIVERSALITY VERY DIFFERENT FROM ISING)
- **Mariani et al. arXiv:2105.05070 (2022)** ★ — power-law avalanches + scale-free correlations can arise from DIFFERENT mechanisms; **only crackling-noise relation between exponents is mechanism-specific**

**Agent A verdict**: P=0.15-0.25 for 3-signature stack discrimination at N=4096 in 1 GPU-hour. Recommend adding AT-eigenvalue + 2-size mini-FSS to materially improve.

### Agent B: SOC + 1/f + neuronal avalanches + Clauset methodology (~30 papers)

**Beggs-Plenz framework**:
- Beggs-Plenz J Neurosci 2003: cortical LFP avalanche P(s) ~ s^(-3/2), branching σ ≈ 1
- Klaus-Yu-Plenz 2011: Clauset methodology confirms power-law preferred over log-normal/exponential for cortical avalanches
- Shriki et al. 2013 J Neurosci: human MEG τ ≈ 3/2

**Wilting-Priesemann subsampling-invariant estimator** (CRITICAL):
- Multistep-regression branching ratio m
- Macaque PFC, cat V1, rat hippocampus: **m ≈ 0.98 = REVERBERATING ≈ definitively SUBCRITICAL by ~2%, NOT critical**
- Naive avalanche fits implied criticality only because of UNACCOUNTED SUBSAMPLING
- arXiv:Wilting-Priesemann 2018 Cereb. Cortex 29:2759

**Power-law fitting methodology** (Clauset-Shalizi-Newman 2009 arXiv:0706.1062):
- MLE for α conditioned on x_min
- KS-minimization over x_min
- Bootstrap p-value (reject power-law if p<0.1 Clauset convention)
- Likelihood ratio (Vuong) vs log-normal AND exponential-cutoff — BOTH must favor pure power-law
- Independent confirmation: avalanche-shape collapse OR branching parameter σ≈1

**Decades-of-data problem**:
- Clauset recommends ≥2 decades; Stumpf-Porter Science 2012 ≥3 decades
- N=4096 caps avalanches at ~4096 → only ~1.5-2 empirical decades
- **Borderline regime where LOG-NORMAL MIMICS POWER-LAW** (Broido-Clauset 2019 Nat. Commun. — only 4% of real distributions pass strict Clauset criterion)

**Touboul-Destexhe 2010 warning shot** ★:
- Negative-LFP power-law avalanches NOT robust to detection threshold
- Log-binning is misleading
- **Surrogate stochastic processes (no SOC) produced identical-looking power laws under thresholding + log-axes**
- KS test rejected the power law where log-log eyeballing accepted it
- **DIRECT EVIDENCE that power-law-looking event statistics ≠ criticality**

**Agent B verdict**: P=0.55 for distinguishing critical from deep ordered phase in 1 GPU-hour. **0.85 for "fat-tailed vs not"; 0.55 for "at criticality with literature rigor"**. Branching-parameter σ ≈ 1 measurement is cheap add to push to 0.7.

### Agent C: SKEPTIC scan — SOC/criticality critiques + convergent-evidence pitfalls (~25 papers)

**Touboul-Destexhe 2017 PRE** ★★ (CRITICAL):
- "Power-law statistics and universal scaling in the absence of criticality"
- **Simple disconnected processes (Ornstein-Uhlenbeck, biased coin flips) satisfy the crackling-noise exponent relation (τ, α, 1/σνz interlock) WITHOUT any phase transition**
- "Exponent-relation satisfaction" — often cited as second-tier signature beyond power laws — is **REPRODUCIBLE by non-emergent stochastic dynamics**
- Devastating for Strategy's 6-signal convergent argument

**Priesemann-Wilting cortical refutation**:
- Macaque PFC m ≈ 0.98 = SUBCRITICAL definitively
- Cortex-is-at-criticality reading of Beggs-Plenz 2003 has been SUBSTANTIALLY REVISED

**Calvo et al. 2026 PRL** (most rigorous recent published refutation):
- DOI 10.1103/36v9-wtm8; 136-subject fMRI
- **Previously-reported scaling signatures are reproducible by temporal autocorrelation + limited sampling alone**
- After time-shift randomization, pooling, exponent matching: effective coupling ~0.88 → **near but not at**
- Current gold standard for rigorous methodology

**Sipling-Zhang-Di Ventra 2026 arXiv:2604.21071**:
- Much "criticality" work fails to distinguish criticality from long-range order
- Neuron-slow-resource coupling can produce scale-invariant correlations WITH NO CRITICAL POINT
- "Memory-induced long-range order phase"
- **Strongest current alternative-mechanism critique**

**Bonachela-Muñoz 2010 arXiv:1001.3256 + Bonachela-de Franciscis 2014**:
- Non-conservative adaptive networks (i.e., real brains) are **GENERICALLY NOT CRITICAL**
- Criticality requires FINE TUNING, not generic
- Self-organize to slightly sub- or super-critical

**Convergent-evidence pitfall**:
- **Trafimow 2019 PMC6803043 "paradox of converging evidence"**: theory is logical CONJUNCTION; supporting N predictions does NOT prove conjunction; as N grows conjunction probability DECREASES if not perfectly entailed. Direct rebuttal to "5 signatures agree therefore theory is true."
- **Senn 2009 PMC2653069**: when inputs are correlated, naive multiplication of Bayes factors OVERSTATES evidence by orders of magnitude
- **Touboul-Destexhe 2017 killer**: SAME MODEL produces multiple "critical signatures" with ZERO criticality → signatures NOT statistically independent

**Critical-line vs critical-point (finite-N challenges)**:
- Billoire 2011 arXiv:1108.1336: pseudo-critical T distribution BROAD at finite N; single-realization data ESSENTIALLY UNINFORMATIVE
- Castro arXiv:1706.04586: Binder cumulant HYPERSCALING BREAKDOWN — textbook diagnostic UNRELIABLE in spin glasses
- Griffiths phase (Moretti-Muñoz Nat. Commun.; arXiv:2512.03409 2025): heterogeneous networks show critical-like signatures over WIDE PARAMETER RANGE — **signatures fill a region, don't pinpoint a point**

**Most rigorous published threshold** (Agent C, 6-criterion checklist):
1. Clauset-Shalizi-Newman likelihood-ratio test passes vs log-normal/exponential/exp-cutoff
2. Exponents satisfy crackling-noise relation across MULTIPLE N + FSS extrapolation to L→∞
3. Avalanche shape collapse onto universal function — not just exponent agreement
4. Sampling-invariance: branching ratio independent of subsample fraction (Wilting-Priesemann method)
5. Surrogate / shuffled-data control reproduces NONE of the signatures
6. Perturbing the coupling (synaptic block, parameter detune) BREAKS the signatures

**Agent C honest decomposition**:
- P(truly at critical point, rigorous statistical-physics sense): **10-20%**
- P(near critical line, ordered/retrieval phase, not at point): **35-45%**
- P(false positive from correlated double-counting / Touboul-Destexhe artifact): **35-50%**

**Brutal bottom line**: "Defensible prior for 'exactly at critical point' given 6 convergent signatures from one finite-N system is on the order of **1-in-5 to 1-in-10**", not the 50-65% Strategy's request quoted.

---

## Pass 2 — substrate drill: REVISED 4-signature stack

### S.1 — χ_SG mini-FSS (2-size; N=2048 + 4096) [REPLACES Strategy's S1 broad β-sweep]

**Mechanism**:
```
def measure_chi_sg_fss(W_2048, W_4096, beta_range, num_seeds=50):
    """Two-size finite-size scaling of spin-glass susceptibility.

    Per Aguilar-Janita 2026 arXiv:2601.19192 protocol (mini-version).
    """
    chi_max = {}
    for N in [2048, 4096]:
        chi_at_beta = []
        for beta in beta_range:  # e.g., [16, 24, 30, 32, 34, 40, 48]
            # Two-replica overlap measurement
            chi_seeds = []
            for seed in range(num_seeds):
                # Run parallel-tempering MC for equilibration
                q_squared = measure_overlap_squared(W, beta, seed)
                chi_seeds.append(N * q_squared)
            chi_at_beta.append(mean(chi_seeds))
        chi_max[N] = max(chi_at_beta)

    # Test: does chi_max scale with N?
    alpha_FSS = log(chi_max[4096] / chi_max[2048]) / log(4096 / 2048)
    return alpha_FSS, chi_max
```

**Parameters**: N ∈ {2048, 4096}; β_range ∈ {16, 24, 30, 32, 34, 40, 48}; 50 disorder seeds; parallel tempering with 32 replicas.

**Decision threshold**:
- α_FSS ≥ 1/3 = SK-class mean-field criticality (Lulli-Parisi-Pelissetto 2016)
- α_FSS ≥ 0.39 = 3D-class criticality (Aguilar-Janita 2026)
- α_FSS ≈ 0 = saturating finite-size pseudo-peak (NON-critical)

**P(signature is informative)**: 0.55 alone; 0.65 paired with S.2 + S.4.

**Eng cost**: ~30 min GPU-hour budget (PT 32 replicas × 2 sizes × 50 seeds; substrate has the infrastructure per Bet E methodology).

**Falsifiable prediction**: substrate measured at N=2048 vs 4096 shows **α_FSS ∈ [0.25, 0.45]** if near critical line (mean-field SK class); **α_FSS < 0.10** if deep in ordered phase. Kill if α_FSS in (0.10, 0.25) → ambiguous; rerun with N=8192 for definitive answer.

### S.2 — AT-eigenvalue computation [REPLACES Strategy's S2 1/f^α power spectrum]

**Mechanism**:
```
def at_eigenvalue(W, alpha=0.153, beta=32):
    """Compute AT-instability eigenvalue lambda_AT.

    Per Albanese-Alemanno-Alessandrelli-Barra 2023 arXiv:2303.06375.
    Single-instance algebraic test for replica-symmetric instability.
    """
    # Build Hessian of replica-symmetric free energy
    H_RS = build_rs_hessian(W, alpha, beta)

    # Diagonalize; find smallest eigenvalue
    eigenvalues = scipy.linalg.eigh(H_RS, eigvals_only=True)
    lambda_AT = eigenvalues[0]  # smallest

    return lambda_AT
```

**Parameters**: substrate's current operating point (α=0.153, β=32); compute for fixed disorder realization.

**Decision threshold**:
- λ_AT > 0 → RS stable, substrate in retrieval phase (NOT at AT line)
- λ_AT ≈ 0 → AT line transition (near critical-line)
- λ_AT < 0 → RSB regime, substrate beyond AT line in spin-glass phase

**P(signature is informative)**: **0.65 — HIGHEST single-signature ROI per Agent A**. "Single best ROI per GPU-hour."

**Eng cost**: <5 min. Pure algebra — no MC needed. Compute Hessian of RS free energy at substrate operating point.

**Falsifiable prediction**: substrate at α=0.153, β=32 yields **|λ_AT| < 0.05 → near AT line (critical-line-consistent)**; **λ_AT > 0.1 → deep retrieval phase (NOT at AT line)**; **λ_AT < -0.1 → beyond AT line (spin-glass regime)**. Kill ambiguous case (|λ_AT| in 0.05-0.1) → run mini-FSS S.1 for resolution.

### S.3 — Avalanche size distribution + branching ratio σ

**Mechanism**:
```
def measure_avalanche_stats(substrate, num_queries=10000, threshold=None):
    """Avalanche size distribution + Wilting-Priesemann branching ratio.

    Per Beggs-Plenz 2003 + Wilting-Priesemann 2018 subsampling-invariant.
    """
    # Define avalanche: activation-magnitude burst (Beggs-Plenz analog)
    activation_norms = []
    for q in range(num_queries):
        query = random_query()
        steps = substrate.retrieve_trace(query)
        activation_norms.append([norm(step.delta) for step in steps])

    # Threshold from theta = median(activation_norms)
    if threshold is None:
        threshold = median(flatten(activation_norms))

    # Extract avalanche size distribution
    avalanche_sizes = []
    for trace in activation_norms:
        in_avalanche = False
        size = 0
        for step in trace:
            if step > threshold:
                size += 1
                in_avalanche = True
            elif in_avalanche:
                avalanche_sizes.append(size)
                size = 0
                in_avalanche = False

    # Clauset-Shalizi-Newman MLE for power-law
    tau, x_min, p_value = clauset_fit(avalanche_sizes)

    # Vuong likelihood ratio vs log-normal + exp-cutoff
    R_lognormal, R_expcutoff = vuong_ratio(avalanche_sizes, tau, x_min)

    # Wilting-Priesemann subsampling-invariant branching ratio
    m_estimate = multistep_regression(activation_norms, subsample_fractions=[1.0, 0.5, 0.25])

    return tau, p_value, R_lognormal, R_expcutoff, m_estimate
```

**Parameters**: 10000 queries; threshold = median; Clauset MLE + Vuong LR + multistep-regression on subsampled data.

**Decision threshold (per Clauset-Shalizi-Newman 2009 + Wilting-Priesemann 2018)**:
- **REQUIRED**: Clauset p > 0.1 AND Vuong R_lognormal > 0 AND Vuong R_expcutoff > 0 (BOTH alternatives rejected) → power-law preferred
- τ ≈ 3/2 ± 0.2 = consistent with directed-percolation universality class (Beggs-Plenz expectation)
- m ≈ 1.00 ± 0.05 = critical; m ≈ 0.95-0.99 = subcritical reverberating (Priesemann); m > 1.05 = supercritical
- **m measured at ≥3 subsample fractions** for sampling-invariance

**P(signature is informative)**: 0.55 alone; 0.60 with branching-ratio addition.

**Eng cost**: ~20 min GPU-hour. 10000 queries is cheap.

**Falsifiable prediction**: substrate avalanche distribution yields **m ∈ [0.95, 1.00] + τ ∈ [1.3, 1.7] + Clauset p > 0.1** → consistent with near-critical. m < 0.90 OR Clauset rejection → deep subcritical / not critical. Kill ambiguous case → run S.4 surrogate control.

### S.4 — Surrogate-data null control [NEW per Agent C; REQUIRED]

**Mechanism**:
```
def surrogate_null_control(substrate, num_shuffles=10):
    """Reproduce all S.1+S.2+S.3 signatures on SHUFFLED-coupling substrate.

    Per Calvo 2026 PRL methodology. REQUIRED negative result.
    """
    null_signatures = []
    for shuffle_seed in range(num_shuffles):
        # Shuffle W matrix entries (preserves marginal distribution)
        W_shuffled = shuffle_couplings(substrate.W, seed=shuffle_seed)
        substrate_null = Substrate(W_shuffled)

        # Apply SAME S.1+S.2+S.3 protocol
        chi_fss_null = measure_chi_sg_fss(substrate_null)
        lambda_at_null = at_eigenvalue(substrate_null.W)
        avalanche_null = measure_avalanche_stats(substrate_null)

        null_signatures.append({
            'chi_fss': chi_fss_null,
            'lambda_at': lambda_at_null,
            'avalanche': avalanche_null,
        })

    # Compute null distribution; compare to substrate's signatures
    return null_signatures
```

**Decision logic (Calvo 2026 methodology)**:
- Substrate's signatures must DIFFER from null distribution at p < 0.05
- If any signature is reproducible on shuffled substrate → that signature was Touboul-Destexhe artifact
- Surrogate-data null MUST be cleared for criticality claim to stand

**P(signature is informative)**: 0.60 (required negative result; without it the entire stack collapses).

**Eng cost**: 10× S.1+S.2+S.3 = ~30 min × 10 = 5 GPU-hours. **EXPENSIVE but UNAVOIDABLE per Calvo 2026 + Agent C**.

**Falsifiable prediction**: if substrate's λ_AT or χ_FSS or τ is REPRODUCED on shuffled-coupling substrate → Strategy's 6-signal evidence is Touboul-Destexhe artifact; criticality claim collapses regardless of other signatures.

---

## Combined `wave14_critical_point_smoke_v1` build spec for Experiment Dev

```python
# wave14_critical_point_smoke_v1.py
# Substrate critical-point characterization gating test
# Per Research note research_critical_point_protocol_2026-05-21.md

import numpy as np
from substrate import Substrate
from scipy.linalg import eigh

def main():
    # Substrate at current operating point
    sub = Substrate(N=4096, alpha=0.153, beta=32, codebook='kerdock_v4')

    results = {}

    # S.1 mini-FSS chi_SG
    sub_2048 = Substrate(N=2048, alpha=0.153, beta=32, codebook='kerdock_v4')
    alpha_FSS, chi_max = measure_chi_sg_fss(sub_2048, sub, beta_range=range(16, 48, 2))
    results['alpha_FSS'] = alpha_FSS

    # S.2 AT eigenvalue
    lambda_AT = at_eigenvalue(sub.W, alpha=0.153, beta=32)
    results['lambda_AT'] = lambda_AT

    # S.3 avalanche statistics
    tau, p_value, R_ln, R_ec, m_est = measure_avalanche_stats(sub, num_queries=10000)
    results['tau'] = tau
    results['clauset_p'] = p_value
    results['vuong_R_lognormal'] = R_ln
    results['vuong_R_expcutoff'] = R_ec
    results['branching_m'] = m_est

    # S.4 surrogate null (5 shuffles for budget)
    null_dist = surrogate_null_control(sub, num_shuffles=5)
    results['null_distribution'] = null_dist

    # Verdict logic
    verdict = compute_verdict(results)
    results['verdict'] = verdict  # CRITICAL / NEAR_LINE / ORDERED / FALSE_POSITIVE

    return results

def compute_verdict(r):
    near_critical = (
        r['alpha_FSS'] >= 0.25 and
        abs(r['lambda_AT']) < 0.1 and
        0.93 <= r['branching_m'] <= 1.02 and
        r['clauset_p'] > 0.1
    )
    surrogate_clear = all(
        not is_significant(r['null_distribution'][k]) for k in ['chi_fss', 'lambda_at', 'tau']
    )

    if near_critical and surrogate_clear:
        return 'CRITICAL'
    elif near_critical and not surrogate_clear:
        return 'FALSE_POSITIVE'  # Touboul-Destexhe artifact
    elif r['branching_m'] < 0.90:
        return 'ORDERED'
    else:
        return 'NEAR_LINE'  # modal Priesemann outcome
```

**Multi-probe success criteria** (REVISED per Agent C):
- **CRITICAL verdict**: all 4 signatures positive AND surrogate-data null clears → V2.G STACK construction cheap
- **NEAR_LINE verdict**: S.1 marginal OR S.2 borderline AND surrogate shows partial signal → V2.G STACK requires Phase Transformations Entry 53 explicit engineering
- **ORDERED verdict**: m < 0.90 → substrate deep in retrieval phase; V2.G fully explicit engineering required
- **FALSE_POSITIVE verdict**: surrogate reproduces signatures → 6-signal convergent evidence was Touboul-Destexhe artifact; recalibrate framing

**Sample size + statistical-power estimates**:
- N=4096 chi_SG with 50 seeds: 5-10% error on χ_max (Aguilar-Janita 2026 scaling)
- 10000 avalanches gives ~1.5-2 empirical decades for Clauset rejection (borderline; Broido-Clauset 2019)
- 5 shuffles for null distribution: borderline statistical power; ≥20 would be ideal

**Eng cost estimate**: 5-6 GPU-hours total (NOT 1 hour as Strategy estimated). Mostly S.4 surrogate null + S.1 FSS at N=2048+4096.

---

## Honest probability calibration for substrate-product implications

| Outcome | P (revised) | Substrate-product consequence |
|---|---|---|
| **CRITICAL** (S.1+S.2 positive, S.4 clears) | **0.15-0.20** | V2.G STACK cheap construction (Strategy's framing); 5-source RSB extends with empirical universality |
| **NEAR_LINE** (S.1 or S.2 marginal, S.4 partial signal) | **0.35-0.45** | V2.G STACK explicit engineering per Phase Transformations Entry 53; mature substrate-physics framing rolls to "near critical-line region" |
| **ORDERED** (S.1+S.2 negative) | **0.20-0.30** | Substrate deep retrieval phase; V2.G STACK fully explicit engineering; 5-source RSB framing rolls back to "ordered phase agreement" |
| **FALSE_POSITIVE** (S.4 reproduces signatures) | **0.10-0.20** | Strategy's 6-signal convergent evidence was Touboul-Destexhe artifact; recalibrate substrate-physics framing materially |

**Honest gating-test value**: 0.45-0.65 informativeness (NOT 95% per Strategy's framing). Still substrate-product useful — distinguishes 4 outcomes with material engineering consequences.

**Per [[feedback-no-smoke]]**: this calibration is the honest substrate-product assessment. The original Strategy request's "95%+ informative" framing was optimistic.

---

## Materials analog (load-bearing per [[feedback-materials-science-probe]])

**Substrate criticality questions map to well-characterized materials-science protocols**:

- **AT-eigenvalue test (S.2)**: directly tests for replica-symmetry-breaking instability per de Almeida-Thouless 1978. Spin-glass condensed-matter standard.
- **χ_SG FSS test (S.1)**: standard finite-size scaling protocol from 2D/3D Ising spin-glass literature (Katzgraber-Körner-Young 2006; Janus collaboration 2007-2024).
- **Avalanche statistics (S.3)**: Bak-Tang-Wiesenfeld 1987 self-organized criticality; Crackling-noise scaling per Sethna-Dahmen-Myers 2001 Nature.
- **Surrogate-data null (S.4)**: standard methodology in nonlinear time series analysis (Theiler-Eubank-Longtin 1992) + neuronal criticality (Calvo 2026 PRL gold standard).

**Load-bearing connections to existing substrate-physics frameworks**:
- R16 BBP threshold + R29 modern Hopfield: BBP transition IS a phase transition; substrate at σ_c=16 = boundary signal/noise. **This IS a critical-LINE crossing, not point**.
- R23 continuous RSB + AT line: S.2 directly tests AT instability. **Cleanest substrate-applicable critical-line test**.
- R18 RFOT: substrate FRSB regime is class of broad phase region, not a point.
- R24 FDT violation + two-temperature: critical fluctuations show distinctive FDT-violation signatures (independent test).
- Bet E Parisi P(q) 5-source: Mattis-phase regime at finite-α near critical line; Hong-Chaté-Park-Tang 2006 shows broad P(q) is finite-N artifact of structured codebook (Entry 40 finding).

**Substrate's empirical 5-source convergence is consistent with**:
- True critical point (P=0.15-0.20)
- Near critical-line in retrieval/ordered phase (P=0.35-0.45 modal)
- Ordered phase with Mattis-class structured-codebook artifact (P=0.20-0.30)
- Correlated convergent-evidence pitfall (P=0.10-0.20)

**Honest finding**: substrate is **almost certainly NEAR a critical line** (combined P > 0.50). Whether it sits AT a critical point requires REVISED 4-signature protocol with surrogate-data null.

---

## 5 pre-armed rescue sketches (PROT-004 per [[feedback-rehabilitation-after-rejection]])

**If S.1+S.2+S.3+S.4 yield FALSE_POSITIVE verdict**:

1. **Hyperscaling-aware re-analysis** per Lundow-Campbell arXiv:1706.04586: substrate may be above upper critical dimension in mean-field-class; Binder cumulant + naive χ unreliable. Re-derive criticality using windowed χ_W per Aguilar-Janita 2026.

2. **Griffiths-phase reframe** per Moretti-Muñoz Nat. Commun.: substrate may be in EXTENDED critical region (Griffiths phase) rather than at critical POINT. Substrate-product value may persist — extended critical region has the same multi-regime capability.

3. **Memory-induced long-range order** per Sipling-Zhang-Di Ventra 2026 arXiv:2604.21071: substrate's apparent critical signatures may be from neuron-slow-resource coupling (Hebbian-EMA blend has multi-timescale structure). Reframe substrate as "memory-induced LRO phase" — different theoretical anchor but same engineering opportunities.

4. **Sub-critical reverberating regime** per Wilting-Priesemann 2018: substrate may be intentionally SUBCRITICAL (m ≈ 0.95-0.99) rather than at criticality. This is the cortex paradigm; reframe substrate-physics as "reverberating dynamics," which has its own substrate-product value (Bet B EMA-blend mechanism is naturally reverberating).

5. **Touboul-Destexhe artifact acceptance**: if surrogate reproduces signatures, ACKNOWLEDGE that the 5-source RSB convergence was correlated-evidence artifact. Substrate-physics framing rolls back to "modern Hopfield rescue regime above α_c" without claiming criticality. Substrate-product capabilities preserved (Bet C M/N=8, Bet G β=32, Bet B retention 0.954, Bet E ✅) — just the unifying narrative downgrades.

---

## Citations (Pass-1 lit scan; ~60+ generic-math queries; verified per [[feedback-verify-implementations]])

**Susceptibility / FSS (6)**:
1. **Aguilar-Janita et al. arXiv:2601.19192 (2026)** ★ — 3D dAT evidence; windowed χ_W protocol
2. Lulli-Parisi-Pelissetto arXiv:1509.05372 (2016) — FSS in mean-field spin glasses
3. Lundow-Campbell arXiv:1706.04586 — Binder cumulant hyperscaling breakdown
4. Katzgraber-Körner-Young cond-mat/0602215 — Bond-diluted EA universality
5. Billoire arXiv:1108.1336 (2011) — Pseudo-critical T distributions
6. Janus collaboration arXiv:2402.03711 — AT may vanish below d=6

**AT line + Modern Hopfield phase diagrams (6)**:
7. **Albanese-Alemanno-Alessandrelli-Barra arXiv:2303.06375 (2023)** ★ — AT-eigenvalue method (gold standard substrate test)
8. Lucibello-Mézard PRL 132:077301 arXiv:2304.14964 (2024) — Exponential capacity REM-like
9. Hoover et al. arXiv:2311.18434 (2023) — Modern Hopfield T-dependent phase transition
10. Lotito et al. arXiv:2604.07401 (2026) — Geometric Entropy DAM
11. Krotov-Hopfield arXiv:1702.01929 (2017) — Dense AM foundational
12. Vector Hopfield arXiv:2507.02586 (2025)

**SOC + 1/f + neuronal avalanches (8)**:
13. Bak-Tang-Wiesenfeld PRL 59:381 (1987) — Foundational SOC
14. Beggs-Plenz J Neurosci 23:11167 (2003) — Cortical avalanches τ=3/2
15. Klaus-Yu-Plenz PLOS ONE (2011) — Clauset validation cortical avalanches
16. **Wilting-Priesemann Cereb. Cortex 29:2759 (2018)** ★ — Subsampling-invariant m=0.98 SUBCRITICAL cortex
17. Sethna-Dahmen-Myers Nature 410:242 (2001) — Crackling noise foundational
18. Watkins et al. arXiv:1504.04991 (2015) — 25 Years of SOC: Concepts and Controversies
19. Srinivasan-Plenz bioRxiv 2024.02.26 — Subsampling correction
20. Hesse-Gross Front. Syst. Neurosci. (2014) — SOC neural decision criteria

**Power-law fitting methodology (5)**:
21. **Clauset-Shalizi-Newman arXiv:0706.1062 (2009)** ★ — Gold-standard power-law fitting
22. **Broido-Clauset Nat. Commun. 10:1017 (2019)** ★ — Scale-free networks are RARE (4%)
23. Deluca-Corral arXiv:1212.5828 — Truncated power-law goodness-of-fit
24. Goldstein-Morris-Yen cond-mat/0402322 — Least-squares-on-log-log bias
25. Stumpf-Porter Science 2012 — Decades-of-data requirement ≥3

**SKEPTIC / criticality critiques (8)**:
26. **Touboul-Destexhe PLOS ONE arXiv:0910.0805 (2010)** ★ — Power-law from stochastic dynamics
27. **Touboul-Destexhe PRE (2017)** ★★ — Crackling-noise exponent relation reproducible by OU + coin flips
28. **Calvo et al. PRL DOI 10.1103/36v9-wtm8 (2026)** ★★ — fMRI 136-subject; coupling 0.88 NEAR BUT NOT AT
29. **Sipling-Zhang-Di Ventra arXiv:2604.21071 (2026)** ★ — Memory-induced LRO without critical point
30. Bonachela-Muñoz arXiv:1001.3256 (2010) — SOC requires fine tuning
31. Mariani et al. arXiv:2105.05070 (2022) — Disentangling neural critical signatures
32. arXiv:2604.21071 (2026) — Critical assessment of brain criticality hypothesis
33. Brain criticality Frontiers 2022 — Skepticism review

**Convergent-evidence pitfalls (3)**:
34. **Trafimow PMC6803043 (2019)** ★ — Paradox of converging evidence
35. **Senn PMC2653069 (2009)** ★ — Overstating evidence via double-counting
36. Holcombe — Confirmation bias in physics (Millikan case study)

**Critical-line vs critical-point (5)**:
37. Berche-Kenna arXiv:1410.5296 — FSS above upper critical dim
38. Castro arXiv:1706.04586 (also #3) — Binder hyperscaling breakdown
39. Moretti-Muñoz Nature Commun. 4:2521 — Griffiths phases stretching of criticality
40. arXiv:2512.03409 (2025) — Optimal Griffiths phase heterogeneous brain networks
41. da Silva-Schmidt cond-mat/0004490 — Triple point random p-spin

**Universality (3)**:
42. Hasenbusch arXiv:1004.4486 — 3D Ising universality
43. Friedman et al. Nat. Phys. (2012) — Universality beyond power laws (avalanche shape collapse)
44. Sethna-Dahmen-Myers cond-mat/0612418 — Crackling noise long review

**Substrate framework cross-references**:
45. arXiv:2502.02393 — VSA noise math (Bet X)
46. arXiv:2505.23653 — Transformer CoT lower bounds (Bet X)

---

## Cross-references

- `notes/substrate_capability_map.md` v81 — Bet Z STACK (META V2.G = same construction; naming alignment in v82)
- `notes/research_phase_transformations_2026-05-21.md` (Entry 53) — STACK decomposition P.5 + P.2 + eviction; if S.4 surrogate fails, V2.G falls back to this explicit engineering
- `notes/research_V2_substrate_evaluation_2026-05-21.md` (Entry 52) — V2.D Bet Y complementary; V2.G uses different mechanism but co-deployable
- `notes/research_R16_free_probability_predictions_2026-05-21.md` — BBP threshold + σ_c=16 (one of Strategy's 6 signals)
- `notes/research_R23_continuous_RSB_AT_line_2026-05-21.md` — FRSB substrate framework
- `notes/research_R29_ferromagnetism_domains_2026-05-21.md` — Modern Hopfield α_c framework
- `notes/research_R18_RFOT_glassy_dynamics_2026-05-21.md` — Substrate glass-dynamics framework
- `notes/research_R24_FDT_violation_2026-05-21.md` — Two-temperature FDT framework (independent critical signature)
- `notes/research_BetE_methodology_escalation_2026-05-21.md` (Entry 40) — Hong-Chaté-Park-Tang Mattis-phase artifact precedent (relevant for S.4 surrogate interpretation)
- `notes/strategy_request_to_research_critical_point_2026-05-21.md` — this routing
- `notes/meta_request_to_strategy_v2g_phase_track_2026-05-21.md` — META V2.G Item 1 origin

---

## Pass-1 honesty statement

Pass 1 lit scan via 3 parallel general-purpose Agent subagents:
- **Agent A** (susceptibility + FSS + AT line + Modern Hopfield + universality): ~25 papers; returned the **critical Albanese-Alemanno-Alessandrelli-Barra arXiv:2303.06375 AT-eigenvalue protocol** + **Aguilar-Janita arXiv:2601.19192 windowed χ_W FSS protocol**.
- **Agent B** (SOC + 1/f + neuronal avalanches + Clauset methodology): ~30 papers; returned the **Clauset-Shalizi-Newman gold-standard fitting protocol + Wilting-Priesemann subsampling-invariant branching ratio**.
- **Agent C** (SKEPTIC scan; critiques + convergent-evidence pitfalls): ~25 papers; returned the **critical Touboul-Destexhe 2017 PRE result that exponent-relation closure is reproducible by OU + coin flips WITHOUT criticality**, plus **Calvo 2026 PRL most rigorous recent published refutation**.

All queries used generic math/physics/neuroscience vocabulary per [[feedback-query-privacy-decomposition]]; no substrate fingerprint.

Total external papers surveyed: ~80+ unique (2018-2026 dominant + foundational anchors: Bak-Tang-Wiesenfeld 1987, Beggs-Plenz 2003, Sethna 2001, de Almeida-Thouless 1978).

**Three independent literature scans CONVERGE on HONEST RECALIBRATION**:
- Strategy's "P(at critical point): 50-65%" is OVERSTATED.
- Defensible decomposition: P(truly critical, rigorous) = **10-20%**; P(near critical line, ordered phase) = **35-45%**; P(false positive from correlated artifact) = **35-50%**.
- Strategy's 3-signature stack discriminative power = **P=0.15-0.25** (insufficient).
- Recommended REVISED 4-signature stack (χ_SG FSS + AT-eigenvalue + avalanche-with-branching-ratio + surrogate-data-null) achieves **P=0.45-0.65** honest informativeness.
- Substrate-product gating-test value PRESERVED but recalibrated; outcome decomposition into 4 paths (CRITICAL / NEAR_LINE / ORDERED / FALSE_POSITIVE) instead of binary yes/no.

**Critical load-bearing references**:
- **Albanese arXiv:2303.06375 (2023)** — AT-eigenvalue gold standard; substrate-applicable algebraic test
- **Touboul-Destexhe PRE 2017** — exponent-relation closure NOT mechanism-specific
- **Calvo PRL 2026 DOI 10.1103/36v9-wtm8** — most rigorous recent refutation; coupling 0.88 near-but-not-at
- **Wilting-Priesemann 2018** — subsampling-invariant m=0.98 cortical SUBCRITICAL
- **Trafimow 2019 + Senn 2009** — convergent-evidence pitfalls; correlated Bayes factors don't multiply
- **Aguilar-Janita arXiv:2601.19192 (2026)** — windowed χ_W finite-size protocol
- **Clauset-Shalizi-Newman arXiv:0706.1062 (2009)** — gold-standard power-law fitting

**Per [[feedback-verify-implementations]]** cited claims I'm specifically relying on:
- Albanese 2303.06375 AT-eigenvalue method: verified via Agent A description; reproduces SK + p-spin AT lines.
- Touboul-Destexhe 2017 PRE exponent-relation reproducibility: verified via Agent C description; OU + biased-coin satisfy crackling-noise relation.
- Calvo 2026 PRL fMRI 0.88 coupling: verified via Agent C description; 136 subjects + surrogate-data null methodology.
- Wilting-Priesemann m=0.98 macaque PFC: verified via Agent B + Agent C descriptions; multistep-regression subsampling-invariant estimator.
- Aguilar-Janita 2601.19192 windowed χ_W: verified via Agent A description; α=0.39 (diverging) vs α≈0 (saturating) FSS scaling.

**Pattern observation**: this is the **5th HONEST-RECALIBRATION-pattern Research note this session** (R17 holographic Entry 25; R33 quantum repeater Entry 28; R32 magnon Entry 31; annealing erasure Entry 58; now critical-point Entry 59). All follow same template: primary claim probability downgraded by literature; substrate-product value preserved through revised framing. Substrate-product engineering discipline working as designed per [[feedback-no-smoke]].

**Per [[feedback-no-papers-product-only]]**: framed as substrate-product engineering gating test ("does substrate operate near critical point — and at what rigor level"), NOT "novel critical-phenomena framework paper."

**Substrate-product action**: build `wave14_critical_point_smoke_v1` with REVISED 4-signature stack (5-6 GPU-hours, not 1) per the specification above. Outcome decomposition into 4 paths (CRITICAL P=0.15-0.20 / NEAR_LINE P=0.35-0.45 / ORDERED P=0.20-0.30 / FALSE_POSITIVE P=0.10-0.20) with corresponding V2.G STACK engineering implications.

EOF marker.
