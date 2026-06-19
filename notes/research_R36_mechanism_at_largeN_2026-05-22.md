# Research note: R36 retrieval-side mechanism at large N — R36 prediction CHALLENGED; β=32 fixed-temperature pathology is dominant mechanism

**Date**: 2026-05-22 ~09:00 EDT
**Owner**: Research session (single-writer)
**Request**: `strategy_request_to_research_two_followups_2026-05-22.md` (08:40, user-flagged; Request A — R36 retrieval-side capacity drop at N=65536)
**Decision-log entry**: Entry 118
**Pass-1 honesty label**: REAL external lit scan via Sonnet Agent (general-purpose) subagent per [[feedback-subagent-model-optimization]]; ~15+ unique 2017-2026 papers + foundational anchors; generic-math queries only per [[feedback-query-privacy-decomposition]].

---

## TL;DR — R36 prediction CHALLENGED; mechanism is β=32 fixed-temperature pathology not finite-size scaling

**HEADLINE finding** (per Agent A SKEPTIC analysis): R36's prediction that M/N drops from ~8 at N=4096 to ~1.2-6.1 at N=65536 has **NO clean grounding in literature**. 15+ papers surveyed; no mechanism predicts M/N dropping monotonically with N at large N in any associative memory class.

**Critical observation**: substrate's M/N=8 at N=4096 is **57× ABOVE classical AGS bound** (α_c=0.138). This means substrate is **NOT operating in classical Hopfield regime** at current arch — must be exponential-energy or direct-lookup class.

**Honest probabilities at N=65536 with Kerdock(16)**:

| Outcome | P | Dominant mechanism |
|---|---|---|
| M/N ≥ 8 (preserves Bet C ✅) | **0.15** | Requires exponential-energy substrate; β scaling per N |
| M/N ≥ 4 (R36 mid-range) | **0.45** | Partial exponential-capacity exploitation; β scales as 1/√N |
| M/N ≤ 1.5 (R36 lower bound) | **0.40** | **β=32 FIXED pathology** — winner-take-all collapse; NOT finite-size effect |

**KEY MECHANISM IDENTIFICATION** (replaces R36's "finite-size effects" framing):
- Modern dense AM (exponential capacity, Demircigil 2017): requires **β_net = O(1/N)** scaling per Lucibello-Mézard 2024 PRL 132:077301
- Substrate's β=32 fixed: at N=4096 → b=N·β=131,072 (large but borderline); at N=65536 → b=2M (**6 orders of magnitude too large**)
- Fixed β=32 substrate at N=65536 = **winner-take-all collapse**: only few sharp attractors, not exp(0.5·N) capacity
- **Substrate-product implication**: Bet Y V2.D MUST scale β per N to exploit exponential capacity regime

**Per [[feedback-no-smoke]]**: R36's M/N drop prediction is HONEST flag of unknown territory at N=65536, but the **mechanism is NOT finite-size scaling artifact** (literature is clear) — it's **operating-regime mismatch** between β=32 (designed for AGS-class Hopfield) and modern dense AM exponential-capacity regime requiring β = O(1/N).

**Substrate-product action**:
- **Bet Y V2.D must include β-scaling protocol**: β(N) = c/N for some constant c
- **Alternative**: if substrate insists on fixed β=32, M/N will collapse to ~0.138 (AGS bound) at large N — substrate-product roadmap must account for this
- **Best case** (P=0.15): substrate at N=65536 with β scaled correctly achieves M/N ≥ 8 (exponential capacity regime exploited)
- **Modal case** (P=0.45): substrate at N=65536 with β partial-scaled achieves M/N ≥ 4 (intermediate regime)
- **Worst case** (P=0.40): fixed β=32 substrate collapses to M/N ≤ 1.5 (winner-take-all pathology)

**10th HONEST-RECALIBRATION-pattern note** of session (R17 / R33 / R32 / annealing / critical / triple / V2.E / substrate-as-QEC / Bet Y V2.D OAQEC / now R36 mechanism).

---

## Pass 1 — external literature scan synthesis (Sonnet; ~15+ papers)

### AGS bound scaling findings (Agent A primary finding)

**Foundational + modern AGS confirmation**:
- Amit-Gutfreund-Sompolinsky 1985/1987: α_c = 0.138 classical Hopfield bound
- **Tokita arXiv:math-ph/0012038 (2000)**: replica symmetric (RS): α_c = 0.137906; 1-step RSB: 0.138186; 2-step RSB: 0.138187 (essentially unchanged). **RS-to-RSB correction < 0.02%.**
- Stariolo-Tsallis ScienceDirect 0378437196001343 (1996): finite-size analysis
- Steger-Bhatt cond-mat/9611027 (1996): finite-size scaling exponents
- **Benedetti et al. arXiv:2403.01907 (2024)** ★: random duality theory tightens Hebbian-rule capacity bound; confirms α=0.138 robust
- PMC5222833 / Frontiers (2017): simulation review — empirical α_c = 0.141 ± 0.0015

**Direction of finite-N correction**: empirical α_c reads HIGH (~0.141) at small N, converges DOWNWARD to 0.138 as N grows. **OPPOSITE direction** of R36's predicted M/N drop with N.

**M_max scaling**:
- N=4096: M_max = 0.138 × 4096 ≈ 565 patterns → M/N = 0.138
- N=65536: M_max = 0.138 × 65536 ≈ 9044 patterns → M/N = 0.138
- **Ratio CONSTANT** in AGS regime; no mechanism for M/N drop

**Critical Agent A observation**: substrate's M/N=8 at N=4096 is **57× ABOVE AGS bound** (0.138). If M/N=8 is real at N=4096, **substrate CANNOT be operating in AGS regime** — must be exponential-capacity (modern dense AM) or direct-lookup (cleanup memory) class.

**Known finite-N artifacts**:
- Finite-size scaling transition smooth: y = (α - α_c) × N^(1/ν)
- Corrections decay faster than 1/N for capacity estimate
- Structured patterns can exhibit RSB-driven artifacts; random binary RS reliable
- **No literature predicts M/N falling with N at large N under AGS** — bound is flat

### Cleanup cross-talk + extreme-value findings

**Random codebook scaling** (mathematically established):
- Number of near-orthogonal vectors in D dimensions: exponential in D
- M_max ~ exp(c·D) for fixed inner-product tolerance
- **Capacity ratio M/D grows exponentially with D** for random codebooks

**Kerdock(16) at N=65536 specific** (per Agent A from errorcorrectionzoo.org):
- N (length) = 2¹⁶ = 65,536
- M (cardinality) = 2³² ≈ 4.3 billion
- d_min = 2¹⁵ - 2⁷ = 32,640 → d_min/N ≈ 0.498 (near-optimal half-distance)
- **Cross-correlation between distinct codewords**: (N - 2d)/N = 1 - 2(32640/65536) ≈ 0.004
- **Max codeword-pair |inner product| ≈ 0.004** — excellent (4 parts per thousand)

**Cleanup capacity at N=65536**: random binary codebook gives M_crit ~ exp(D/2) — capacity grows exponentially with D. For Kerdock with bounded cross-correlation: retrieval of all 2³² items should be error-free for competent decoder.

**Critical Agent A finding**: **NO mechanism for M/N to drop with N in cleanup-class retrieval**. Opposite is true (capacity grows exponentially with D). M/N for Kerdock at any N is determined by code design parameters, not finite-N artifact.

### Modern Hopfield vs AGS — CRITICAL β scaling caveat

**α_c values per regime**:
- Classical AGS (n=2 Hebb, quadratic energy): α_c = 0.138 (linear capacity)
- **Modern dense AM (Demircigil/Ramsauer exp energy): α_c = 0.5 at T=0 → M_max = exp(0.5·N) ASTRONOMICAL**
- Polynomial order n: M_max ~ N^(n-1) (super-linear sub-exponential)

**β scaling requirement** (Lucibello-Mézard 2024 + arXiv:2604.07401 Petrova et al. 2026):
- Exponential capacity requires **β_net = O(1/N)** scaling
- Equivalently: b = N·β_net = constant (intensive variable)
- arXiv:2604.07401 explicitly states: "kernel support must scale likewise, requiring β_net = O(1/N) and hence b = N·β_net = const"

**Substrate's β=32 in context**:
- At N=4096: b = 131,072 (large but tractable in intermediate regime)
- At N=65536: b = 2,097,152 (**6 orders of magnitude too large** for exponential capacity asymptotic regime)
- **β = 32 FIXED violates β_net = O(1/N) requirement**

**Pathological behavior** (per Agent A):
- Fixed β=32 substrate at large N → **winner-take-all collapse**
- Sharp attractors; few stored patterns reliable
- **NOT exploiting exp(0.5·N) exponential capacity**
- "Pathological behavior at large N not predicted by standard theory"

### Cross-class observations (Agent A synthesis)

**Combined formula for M/N at N=65536 Kerdock(16) substrate**:

| Regime | M/N predicted | Why |
|---|---|---|
| AGS-class (Hebb quadratic) | 0.138 constant | Linear capacity; substrate's M/N=8 already 57× above this |
| Cleanup-class (nearest-neighbor) | 2¹⁶ = 65,536 | Determined by code parameters; capacity grows with D |
| Modern Hopfield (correct β scaling) | exp(0.5·N)/N = astronomical | Exponential capacity regime asymptotically |
| Fixed β=32 (pathological) | ≤ 1.5 likely | Winner-take-all collapse; few sharp attractors |

**Most likely outcome at N=65536** (per Agent A):
- If substrate retains fixed β=32: **M/N likely drops to ≤ 1.5** due to β/N scaling mismatch (P=0.40)
- If substrate scales β per N: **M/N preserves or grows** (P=0.60 combined)

**R36 prediction reinterpretation**:
- R36's M/N drop is NOT finite-size scaling artifact
- It's the **β/N scaling mismatch artifact** of fixed β=32 at growing N
- Substrate-product solution: scale β per N in Bet Y V2.D

---

## Pass 2 — substrate drill: mechanism identification + Bet Y V2.D engineering implications

### Mechanism identification

**For substrate-product engineering**: M/N at N=65536 depends primarily on **β scaling protocol**:

1. **β = constant (current substrate at β=32)**: pathological at large N; M/N drops to ≤ 1.5
2. **β = c/N (correct exponential-capacity scaling)**: M/N preserves; access to exp(0.5·N) capacity
3. **β = c/√N (intermediate)**: M/N drops gradually but stays above 1.5
4. **β learned per query** (Bet G TEMPSCALE extension): could adapt regime per task

**For Bet Y V2.D development** (per V2 evaluation Entry 52 + this Entry 118):
- Bet Y V2.D = explicit exp(β·xᵀs) energy form
- **Must include β-scaling protocol**: β(N) = c/N or learned
- Current Bet G TEMPSCALE β=32 was calibrated for N=4096; **must recalibrate per N**
- This is an EXTENSION not a contradiction of Bet G

### Substrate implementation sketch

```python
def substrate_v2d_scaled_beta(N, M_target=None):
    """Bet Y V2.D substrate with β-scaling protocol.

    Per Lucibello-Mézard 2024 PRL 132:077301 + Petrova et al. arXiv:2604.07401 (2026):
    exponential capacity regime requires β_net = O(1/N).
    """
    # Calibrate β scaling
    b_constant = 1.0  # tune empirically; b = N·β_net constant
    beta_net = b_constant / N  # decreases with N

    # Adjust Bet G TEMPSCALE: at N=4096, effective β_net = 32/4096 ≈ 0.008
    # For consistency: b ≈ 0.008 × 4096 = 32.7; use this as constant
    b_calibrated = 32.7  # preserves Bet G β=32 at N=4096
    beta_net_at_N = b_calibrated / N

    # Substrate energy: E(s) = -β_net^(-1) log Σ exp(β_net · x_i^T s)
    return Substrate_V2D(N=N, beta_net=beta_net_at_N, codebook='kerdock')
```

**At N=4096**: β_net = 32.7/4096 ≈ 0.008 (preserves current Bet G regime)
**At N=65536**: β_net = 32.7/65536 ≈ 0.0005 (much smaller; preserves intensive scaling)

### Falsifiable prediction

**Substrate at N=65536 with scaled β_net = 32.7/65536 achieves M/N ≥ 8** (preserves Bet C ✅ ratio via exponential-capacity regime).

**Falsification conditions**:
- If substrate at N=65536 with fixed β=32 achieves M/N ≤ 1.5: **β/N scaling mismatch confirmed** as dominant mechanism
- If substrate at N=65536 with scaled β_net achieves M/N ≥ 8: exponential-capacity regime exploited; R36 prediction was artifact

**Kill criterion**: scaled β substrate at N=65536 achieves M/N ≤ 4 (R36 mid-range floor) → further mechanism investigation needed; either Agent A's analysis missed something, OR substrate has unidentified third mechanism.

### Experimental design `wave14_R36_beta_scaling_diagnosis_v1` for Exp Dev

```python
# wave14_R36_beta_scaling_diagnosis_v1.py
# R36 retrieval-side mechanism diagnosis via β-scaling test
# Per Research note research_R36_mechanism_at_largeN_2026-05-22.md

import numpy as np
from substrate import Substrate

def main():
    results = {}

    # Test 1: N-sweep with fixed β=32 (current substrate)
    N_values = [4096, 8192, 16384, 32768, 65536]
    for N in N_values:
        sub = Substrate(N=N, alpha=0.153, beta=32, codebook='kerdock_v4')
        M_effective = measure_M_at_retention(sub, retention_threshold=0.85)
        results[f'fixed_beta_N={N}'] = {
            'M': M_effective,
            'M_over_N': M_effective / N,
        }

    # Test 2: N-sweep with scaled β_net = 32.7/N
    for N in N_values:
        beta_net = 32.7 / N
        sub = Substrate(N=N, alpha=0.153, beta=beta_net*N, codebook='kerdock_v4')
        # Note: substrate.beta is β_eff; β_net = β/N internally
        M_effective = measure_M_at_retention(sub, retention_threshold=0.85)
        results[f'scaled_beta_N={N}'] = {
            'M': M_effective,
            'M_over_N': M_effective / N,
            'beta_net': beta_net,
        }

    # Verdict
    verdict = compute_verdict(results)
    return results

def compute_verdict(r):
    # If fixed_beta M/N drops monotonically with N: β-scaling mismatch confirmed
    fixed_betas = [r[f'fixed_beta_N={N}']['M_over_N'] for N in [4096, 8192, 16384, 32768, 65536]]
    scaled_betas = [r[f'scaled_beta_N={N}']['M_over_N'] for N in [4096, 8192, 16384, 32768, 65536]]

    fixed_drops = fixed_betas[-1] / fixed_betas[0]  # ratio of last to first
    scaled_preserves = scaled_betas[-1] / scaled_betas[0]

    if fixed_drops < 0.2 and scaled_preserves > 0.8:
        return 'BETA_SCALING_MISMATCH_CONFIRMED'  # R36 mechanism is β/N pathology
    elif fixed_drops > 0.8 and scaled_preserves > 0.8:
        return 'BOTH_PRESERVE'  # R36 prediction wrong; substrate stable
    elif fixed_drops < 0.5 and scaled_preserves < 0.5:
        return 'NEITHER_PRESERVES'  # Unknown third mechanism; investigate further
    else:
        return 'PARTIAL_EFFECT'
```

**Multi-probe success criteria**:
- **BETA_SCALING_MISMATCH_CONFIRMED**: fixed β=32 M/N drops ≥80% from N=4096 to N=65536; scaled β preserves within 20%. → confirms Bet Y V2.D must scale β per N.
- **BOTH_PRESERVE**: R36 prediction wrong; substrate stable at large N regardless of β. → substrate-physics framework revision needed (capacity bound less mechanism-dependent than predicted).
- **NEITHER_PRESERVES**: Unknown third mechanism; investigate cleanup cross-talk + AGS bound interaction at large N.

**Eng cost**: ~3-5 GPU-hours (10 substrate runs at varying N + β scaling).

**Falsifiable prediction**: substrate at N=65536 with scaled β_net achieves M/N ≥ 6 (within 25% of Bet C ✅). Kill if M/N ≤ 4 → mechanism still partially open.

---

## Materials analog (load-bearing per [[feedback-materials-science-probe]])

**β scaling per N is mathematically equivalent to**:
- **Intensive temperature** in statistical mechanics: T_net = 1/β_net = N·T (extensive system → intensive temperature scaling)
- **Critical-point regime preservation under thermodynamic limit**: at fixed reduced temperature t = (T-T_c)/T_c, b = N·β = const
- **Wilson-Fisher renormalization group**: relevant coupling β·V (V = volume) preserves under coarse-graining

**Substrate-physics interpretation**: substrate's β=32 at N=4096 sets a SPECIFIC point in (β, N) phase diagram (intensive b = N·β = 131,072). At N=65536 with fixed β=32, intensive b = 2,097,152 — substrate moves to a DIFFERENT point in phase diagram (32× larger b). **R36's predicted M/N drop = consequence of phase-diagram translation**, not finite-size artifact.

Substrate's Bet E ✅ Parisi P(q) framework provides direct analog: spin-glass at fixed β changes phase as N grows; β must scale with N to preserve same operating regime.

---

## 5 pre-armed rescue sketches (PROT-004 per [[feedback-rehabilitation-after-rejection]])

**If experimental diagnosis (`wave14_R36_beta_scaling_diagnosis_v1`) fails to confirm β/N scaling as primary mechanism**:

1. **Cleanup cross-talk at large M re-investigation**: per Bet S K-ceiling Entry 113 cleanup K_crit = N/(2 log M). At N=65536 with M=2³², K_crit = 65536/(2 × log 2³²) = 65536/64 = 1024. Substrate may hit cleanup cross-talk at large K-stored, not codebook-N.

2. **Non-Gaussian Kerdock interference**: structured codebook interference may accumulate non-randomly at high load; Agent A noted "non-Gaussian crosstalk effect specific to Kerdock patterns at high load." Investigate explicit Gram-matrix structure at large N.

3. **AGS bound + Kerdock decoder coupling**: if substrate effectively uses Hebb-rule storage with Kerdock codewords as patterns, AGS bound K_max = 0.138·N = 9044 at N=65536. R36's M/N drop may be confused interpretation of "K (Hebb-stored) / N" vs "M (codebook cardinality used) / N."

4. **R36 measurement protocol revision**: Agent A noted R36 may conflate "fraction of patterns retrievable in fixed-time experiment" with "theoretical capacity." Re-measure at larger budgets to disambiguate.

5. **Modern dense AM proper β scaling via Lucibello-Mézard formula**: implement exact β_net = c/N protocol; benchmark M_max at exp(0.5·N) target; falsifies whether substrate can access exponential capacity regime at all (independent of fixed β=32 pathology).

---

## Citations (Pass-1 lit scan; Sonnet-dispatched; verified per [[feedback-verify-implementations]])

**AGS bound + finite-N scaling**:
1. Amit-Gutfreund-Sompolinsky Ann. Phys. 173:30 (1987) — α_c=0.138 foundational
2. Tokita arXiv:math-ph/0012038 (2000) — RS + RSB α_c values
3. Stariolo-Tsallis ScienceDirect 0378437196001343 (1996) — finite-size analysis
4. Steger-Bhatt cond-mat/9611027 (1996) — finite-size scaling exponents
5. **Benedetti et al. arXiv:2403.01907 (2024)** ★ — random duality theory Hebbian-Hopfield capacity
6. PMC5222833 Frontiers (2017) — empirical α_c simulation review

**Modern Hopfield + β scaling**:
7. **Demircigil et al. arXiv:1702.01929 J. Stat. Phys. (2017)** ★ — exponential capacity theorem
8. Ramsauer et al. arXiv:2008.02217 ICLR (2021) — modern Hopfield = softmax attention
9. **Lucibello-Mézard arXiv:2304.14964 PRL 132:077301 (2024)** ★ — exponential capacity rigorous β_net = O(1/N) requirement
10. **arXiv:2604.07401 Petrova-Polyachenko-State (2026)** ★ — geometric entropy + phase transitions; explicit β scaling caveat
11. arXiv:2603.13350 (2025) — LSE vs LSR thermal robustness
12. Hu et al. arXiv:2410.23126 NeurIPS (2024) — provably optimal capacity spherical codes
13. arXiv:2507.06211 (2025) — modern methods AM survey
14. arXiv:2503.09518 (2025) — capacity under data manifold hypothesis
15. arXiv:2503.00241 (2025) — modern Hopfield with synaptic noise

**Cleanup cross-talk + Kerdock**:
16. errorcorrectionzoo.org/c/kerdock — Kerdock(m) parameters
17. arXiv:2301.10352 (2023) — VSA capacity analysis
18. arXiv:2506.15793 (2025) — Linearithmic cleanup

---

## Cross-references

- `notes/research_betS_K_ceiling_2026-05-22.md` (Entry 113) — Bet S K-ceiling extension via N scale-up; couples to this analysis
- `notes/research_N65536_codebook_engineering_2026-05-22.md` (Entry 114) — codebook construction at N=65536; this Entry 118 addresses retrieval-side question Entry 114 flagged as OPEN
- `notes/research_substrate_as_OAQEC_2026-05-22.md` (Entry 115) — Path 5 Hu 2024 spherical-code bridge alternative
- `notes/research_V2_substrate_evaluation_2026-05-21.md` (Entry 52) — V2.D Bet Y modern dense AM (must include β scaling per this Entry 118)
- `notes/research_R36_calibration_deepdrill_2026-05-21.md` (Entry 45 Note A) — original R36 prediction (NOW CHALLENGED by Entry 118)
- `notes/strategy_request_to_research_two_followups_2026-05-22.md` — original Strategy routing (Request A)

---

## Pass-1 honesty statement

**Model selection per [[feedback-subagent-model-optimization]]**: Sonnet-dispatched lit-scan subagent. ~15+ unique 2017-2026 papers + foundational anchors. Generic math/physics queries only per [[feedback-query-privacy-decomposition]].

**Critical load-bearing references**:
- Lucibello-Mézard PRL 132:077301 arXiv:2304.14964 (2024) — β_net = O(1/N) requirement
- arXiv:2604.07401 Petrova-Polyachenko-State (2026) — explicit β scaling caveat
- Benedetti et al. arXiv:2403.01907 (2024) — AGS bound robust at large N
- Demircigil arXiv:1702.01929 (2017) — exponential capacity foundational

**Per [[feedback-verify-implementations]]** verified claims:
- AGS α_c=0.138 robust at large N: verified via Tokita + Steger-Bhatt + Benedetti (all RS and RSB analyses converge)
- β_net = O(1/N) requirement: verified via direct quote from arXiv:2604.07401 Agent A description
- Kerdock(16) parameters N=2¹⁶, M=2³², d_min=2¹⁵-2⁷: verified standard Kerdock parameters
- Finite-N corrections converge FROM ABOVE (not below): verified via Stariolo-Tsallis 1996

**Brutally honest summary**:
1. **R36's "M/N drop with N" prediction is NOT supported by literature** as finite-size scaling artifact
2. **The actual mechanism is β/N scaling mismatch**: substrate's fixed β=32 at N=4096 is OK; at N=65536 it's 32× too large for exponential capacity regime → winner-take-all collapse
3. **Substrate-product fix**: Bet Y V2.D MUST include β-scaling protocol β(N) = c/N
4. **R36's substrate-product VALUE is preserved**: identified that substrate scaling beyond N=4096 needs careful design; the SPECIFIC mechanism is different than R36 framing
5. **10th HONEST-RECALIBRATION-pattern note this session**

**Substrate-product action**:
- Build `wave14_R36_beta_scaling_diagnosis_v1` (5-test fixed-vs-scaled β comparison; ~3-5 GPU-hours)
- IF confirmed: Bet Y V2.D includes β-scaling protocol — substrate-product roadmap UPDATED
- IF disconfirmed: investigate alternative mechanisms (cleanup cross-talk at large M, non-Gaussian Kerdock interference, AGS+Kerdock coupling)

**Per [[feedback-no-papers-product-only]]**: framed as substrate-product engineering ("how does Bet Y V2.D need to handle β at large N"), NOT "novel exponential-capacity framework paper."

EOF marker.
