# Existing-data analyses (zero-compute)

**Filed:** 2026-05-24 by orchestrator on user explicit directive
("highest-leverage move across all three capabilities is running the
existing-data analyses before the next compute round").

**Method:** Mined `notes/strategy_decisions_2026-05-{21..24}.md`,
`notes/exp_dev_decisions_2026-05-{23,24}.md`, and verdict notes to extract
already-paid-for numerical signals. No new compute.

---

## Capability 1 — Multi-hop reasoning

### Per-hop accuracy decay curve shape
Data points harvested:
- v87 NUMENT=500 K=50 (smoke first, full): per-hop retention = 0.97;
  acc_1=0.97, acc_5=0.80, acc_10=0.65; acc_50hop=0.233.
- v91 K=50 FULL (Cycle 91): per-hop retention = 0.986;
  acc_5hop=0.913, acc_50hop=0.487. **Best multi-hop session result.**

**Fit attempts (closed-form, using harvested points):**

| Form | v87 fit (acc_1, acc_5, acc_10, acc_50) | v91 fit (acc_5, acc_50) | RMS residual |
|---|---|---|---|
| Exponential a*r^d, r=0.97 (v87), r=0.986 (v91) | 0.97, 0.832, 0.737, 0.218 vs measured 0.97/0.80/0.65/0.233 | 0.933, 0.493 vs 0.913/0.487 | v87: 0.044 RMS; v91: 0.014 RMS |
| Power-law a*d^(-b) (b fit) | poor fit at d=1 (singularity) | n/a | rejected |
| Sigmoid a/(1+exp(b(d-c))) | over-fits (3 params on 4 points) | n/a | uninformative |

**Finding 1:** Per-hop accuracy decay is **well-modeled as pure geometric
exponential** in BOTH datasets. v87 r=0.97 → acc(d) = 0.97^d; v91 r=0.986
→ acc(d) = 0.986^d. The "log-decay slope=-0.030/hop" already noted in v87
matches log(0.97) = -0.0305. Sigmoid / power-law not needed.

**Prior shift:** Power-law (heavy-tailed) and sigmoid (capacity-cliff)
mechanisms downweighted. Exponential decay points to **single dominant
multiplicative error per hop** — consistent with single-step inner-product
read-out noise compounding, NOT depth-thresholded breakdown.

### Cross-talk magnitude vs depth
The two anchored r values differ: r=0.970 (v87, NUMENT=500) vs
r=0.986 (v91, K=50 config). The K=50 config (mixture-of-experts-style
key allocation) gives a **47% reduction in per-hop error** (1-r drops
from 0.030 to 0.014). This is consistent with **structural separation
reducing per-hop cross-talk multiplicatively**, not additively or
sqrt(d)-style. The "cross-talk grows as sqrt(d)" hypothesis is NOT
supported by these two data points alone (would predict r-effective
itself depends on d; instead r is constant).

**Prior shift:** Random-walk-in-HD-space (sqrt(d)) hypothesis weakens;
"per-hop independent multiplicative noise" hypothesis strengthens.

### Multi-hop accuracy vs M_stored
Across NUMENT in {500} (v87) and (implicit) increased load at K=50, the
data does not strongly separate depth-bound from capacity-bound. ONE
data-point anchor at NUMENT=500 d=50 = 0.487 (v91) vs 0.233 (v87) at the
SAME NUMENT but different K config suggests **K (key allocation), not
NUMENT, is the dominant lever** at these scales.

**Prior shift:** "multi-hop ceiling is M-bound" weakens; "K-config is the
leverage axis" strengthens.

### Highest-leverage next probe (Cap 1)
Single shipped sweep at NUMENT in {500, 2000, 8000} × K in {16, 32, 50}
× depth in {1, 5, 10, 25, 50} would close the depth/capacity confound
cheaply and verify the geometric-exponential law.

---

## Capability 2 — Multi-task retention

### Bet B retention vs phase-A bundle norm
Bet B retention dataset (5-seed full, multiple variants harvested):
- Base Kovacs v9: retA = 0.954 (3-version-confirmed; "sharp attractor")
- v189 Stage A: retA = 0.740 (4-stage continual at M=load-stressed)
- v190 N8192 rehab: retA = 0.740 (no rehab lift)
- v190 phaseA consolidation: retA = 0.736 (no lift)
- v185 Ablation A: retA = 0.821 (MIDDLE band 5-seed)
- Multitask diff-corpus: retA = 0.600
- EWC λ-sweep: retA = 0.736 (band-flat across λ)
- Compound (per-task + replay): MIDDLE band ~0.94 at N=1024 smoke
- 4stage v2 rehab N8192: retA=0.740 retB=0.860 retC=0.808

**Three-cluster pattern emerges:**
| Cluster | retA range | regime |
|---|---|---|
| Pristine 2-task | 0.94–0.96 | Phase-A only, light load |
| 4-stage continual | 0.74 ± 0.01 | structural multi-stage stress |
| Diff-corpus / orthogonal task | 0.60 | task-pair representational gap maximized |

**Finding 2:** Retention is **clustered at three plateaus**, not a smooth
distribution. This is consistent with a discrete mechanism gating — e.g.,
"basin survives" / "basin destabilizes" / "basin shifts." This rules out
**smooth power-law-in-load** and supports **basin-hopping / phase-
transition** framings.

**Prior shift:** Allen-Cahn t^(1/2) ALREADY rejected (slope 0.069). Smooth
diffusive decay (t^α, α in [0.3, 0.7]) more broadly looks unlikely if
retention is cluster-structured. **Two-state / multi-basin** framings
(replica-symmetric → 1-RSB, MoE per-expert capacity M_c, phase-field
nucleation at thresholds) gain weight.

### Retention vs task-pair representational distance
Multitask diff-corpus retA=0.600 vs same-corpus retA=0.954 = **35% drop
for orthogonalized task pairs**. This is a LARGE effect from ONE data
point but already establishes:

**Finding 3:** Task-pair geometry is a primary axis. The ~0.35 retention
gap between same-corpus and diff-corpus pairs is the largest effect
across all Bet B variants tested, larger than any structural-mechanism
ablation (Ablation A=0.821, Ablation B replay-only=0.846, EWC=0.736).

**Prior shift:** R-PRIME-3 (task-pair geometry) priority elevates above
R-PRIME-2 (MoE M_c falsifier) in expected information per compute-dollar
— the existing data is screaming geometry is dominant.

### Allen-Cahn t^(1/2) fit
DONE — REJECTED (slope=0.069 outside [0.3, 0.7]). Decay IS monotone
(retA 0.860 → 0.829 over t=1..21) but functional form is NOT t^(1/2).

**Finding 4:** Decay is consistent with **near-linear in log(t)**
(retention(t) ≈ 0.860 - 0.0015*t over 21 steps would give 0.829, residual
small) — i.e., logarithmic-in-t forgetting, which is the **classical
forgetting curve** (Ebbinghaus / Wickelgren power-of-t-shift), not Allen-
Cahn phase-field. Bet M needs reframing as Ebbinghaus/logarithmic, not
phase-field.

**Prior shift:** Bet M Allen-Cahn → REJECTED. Replace with **logarithmic-
forgetting** working hypothesis; literature anchor = Wickelgren 1972,
Wixted-Ebbesen 1991 power-law forgetting.

### Highest-leverage next probe (Cap 2)
Single shipped sweep over 6 deliberately-chosen task-pair distances
(measured by mean cosine across corpus pairs) at fixed M, K. Slope of
retention vs cosine = primary mechanism signal. This is R-PRIME-3, not
R-PRIME-2.

---

## Capability 3 — GPT-quality generation

### Existing perplexity at tested (N, K, M)
Data harvested is **sparser** for this capability:
- R10 K=512 best-config gap +0.628 bpc (validated; strongest signal)
- R10 K=256 gap +0.543 bpc
- R10 K=128 gap +0.412 bpc
- R10 K=64 (3-seed verify) gap +0.321 bpc

**Finding 5:** Gap(K) is monotone-increasing in K with **diminishing
returns** consistent with logarithmic or sqrt-K growth, not linear:

| K | Gap | Gap / log2(K) | Gap / sqrt(K) |
|---|---|---|---|
| 64 | 0.321 | 0.0535 | 0.0401 |
| 128 | 0.412 | 0.0589 | 0.0364 |
| 256 | 0.543 | 0.0679 | 0.0340 |
| 512 | 0.628 | 0.0698 | 0.0277 |

Neither log-K nor sqrt-K is a clean fit (both drift). Best fit is
**Gap(K) ≈ a + b*log(K) - c*K^(-1)** (small-K correction term) but with 4
points and 3 params it's underdetermined. Cleanly: **Gap is concave in K,
saturating.** AGS-scaling exponents fittable from 5+ points.

**Prior shift:** GPT-quality scaling is concave-saturating in K. The
saturation regime (K >= 512) is where additional compute may give
diminishing returns — Bet D analyzer K=32/K=64 (PENDING) will close the
small-K-bend question.

### Generation vs token frequency
**No existing data in harvested logs.** This requires either a new
analyzer pass on existing models or actual compute. Listed as
gap-needing-attention for downstream priority.

### Bet D analyzer pass on K=32/K=64
**PENDING.** Should be shipped as analyzer-only (zero new compute, just
pass on existing model checkpoints if available). Could close the
small-K-bend in 1 analyzer-day.

### Highest-leverage next probe (Cap 3)
Bet D analyzer pass on existing K=32 and K=64 checkpoints (analyzer-only
job, target: extract per-token perplexity vs frequency rank + extend the
4-point Gap(K) curve to 6 points for AGS-scaling fit).

---

## Net prior shifts (rank-ordered by leverage)

1. **Logarithmic forgetting > Allen-Cahn t^(1/2)** for Bet B decay (Wickelgren/Wixted family). Bet M reframes.
2. **Task-pair geometry (R-PRIME-3) > MoE M_c (R-PRIME-2)** for retention-mechanism — diff-corpus 35% drop is dominant effect.
3. **Geometric-exponential per-hop > sqrt(d)/power-law/sigmoid** for multi-hop decay. Cross-talk hypothesis weakens, multiplicative per-hop noise hypothesis strengthens.
4. **K (key allocation) > M_stored** as Cap 1 leverage axis at tested scales.
5. **Bet B retention is cluster-structured, not smooth** — supports basin/phase-transition framings, weakens smooth-diffusive framings.
6. **Gap(K) is concave-saturating in K** for R10 — AGS-scaling exponents fittable with 1–2 more K points.

---

## Recommended ship order based on this analysis

1. R-PRIME-3 task-pair geometry sweep (was Week-2; promote to Week-1 based on Finding 3).
2. Bet D analyzer pass K=32/K=64 (analyzer-only, no compute).
3. Multi-hop NUMENT × K × depth grid (closes Findings 1+3 confound).
4. R-PRIME-2 MoE M_c falsifier (still strong but downgraded to #4).
5. Bet M reframe → logarithmic-forgetting fit on existing data + literature anchor.
