# Strategy → Experiment Dev: Substrate observability suite v1 — top 3 probes for spin-glass diagnostics

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-22 ~14:25 EDT
**Topic**: Implement observability suite top 3 probes per Research Entry 141 deep drill
**Source**: `research_substrate_observability_deep_drill_2026-05-22.md` (14:10) + `research_materials_characterization_methods_2026-05-22.md` (13:55)
**cap_map**: v109 (commit `e9360c2`)

## Context

Two Research deliveries this afternoon define a substrate observability
suite framework. The substrate-product value (per Entry 140 framing):

> "Substrate-product value is **building cheap, decisive observability
> into the substrate** so capability tests (Bet S K-ceiling, Bet A
> continual, Bet C codebook, Bet Y V2.D scaled, multi-hop d-cliff)
> produce diagnostic byproducts rather than pass/fail-only verdicts."

Substrate is empirically a spin-glass per Bet E ✅ Parisi P(q) RSB
(cap_map v66+). Edwards-Anderson order parameter framework applies.

## Implementation request — observability suite v1 (3 priority probes)

### Priority 1 — `wave14_observability_C_ij_eigvals_v1`

**What**: time-average C_ij = ⟨s_i s_j⟩ across MC chain; diagonalize via
`numpy.linalg.eigvalsh`; count eigenvalues with λ_k / N > 0.1 that
persist as N grows.

**Why**: discrete count (1 = paramagnet, >1 = RSB) avoids the finite-N
broadening problem of P(q) plateaus. Per Sinova-Houdayer-Martin
cond-mat/0010302.

**Implementation**:
- Single MC chain at α=0.15 (substrate operating point)
- Sample s configurations every ~100 steps for 1000+ samples
- Compute C_ij = ⟨s_i s_j⟩ — ⟨s_i⟩⟨s_j⟩
- `eigvalsh(C_ij)` ~ 1 second at N=4096
- Count eigvals with λ/N > 0.1
- **Critical artifact check**: also diagonalize W; count W's
  extensive eigenvalues; only EXCESS eigvals in C_ij beyond those
  inherited from W structure are the genuine RSB signal

**Runtime**: ~0.5-2 GPU-h at N=4096 (mostly MC chain time)

**Pass criteria** (Strategy proposal):
- **OBS_CIJ_RSB**: >1 extensive eigvals in C_ij excess of W (substrate in RSB phase)
- **OBS_CIJ_RS**: exactly 1 extensive eigval (substrate in RS / paramagnet phase)
- **OBS_CIJ_AMBIGUOUS**: counts marginal (re-run with longer MC chain)

### Priority 2 — `wave14_observability_P_q_replica_overlap_v1`

**What**: run two parallel MC chains (replicas); histogram q = (1/N) Σ_i s_i^(1) s_i^(2); construct P(q).

**Why**: canonical RSB diagnostic per Parisi 1983 PRL 50:1946. At α=0.15
below freezing, P(q) has continuous plateau from 0 to q_EA.

**Implementation**:
- Parallel-tempering (PT) MC chains for thermalization at α=0.15
- 2 replicas; record q every ~100 steps for 1000+ samples
- Histogram into bins of width 0.05 over q ∈ [-1, 1]
- Smooth fit to identify plateau structure

**Runtime**: ~1-2 GPU-h at N=4096 (PT thermalization dominant)

**Pass criteria**:
- **OBS_PQ_RSB**: continuous plateau detected with q_EA > 0 (RSB phase)
- **OBS_PQ_RS**: P(q) is delta function at q = 0 (RS / paramagnet phase)
- **OBS_PQ_FROZEN**: P(q) sharply peaked at q ≈ 1 (frozen / ferromagnet phase)
- **OBS_PQ_AMBIGUOUS**: insufficient statistics (re-run with longer PT)

### Priority 3 — `wave14_observability_P_h_moments_v1`

**What**: compute local-field histogram h_i = Σ_j W_ij s_j for all i;
fit to {bimodal vs unimodal} distribution; report moments (mean, σ,
skewness, kurtosis); compute "wipeout fraction" (sites with |h_i| > θ
for some threshold θ).

**Why**: per Mezard arXiv:0711.3934 — bimodal P(h) = frozen sites
(glass); narrow Gaussian = paramagnetic; wipeout fraction is
order-parameter proxy.

**Implementation**:
- For each sampled MC configuration, compute h_i = (W s)_i
- Aggregate across configurations + sites
- Fit P(h) to Gaussian-mixture (1 vs 2 components)
- Report Δ_h = local-field RMS; AIC/BIC for 1-vs-2 mixture
- Wipeout fraction = (1/N) |{i : |h_i| > 2σ}|

**Runtime**: ~0.2-0.5 GPU-h at N=4096 (MC chain + histogram)

**Pass criteria**:
- **OBS_PH_FROZEN**: bimodal P(h) with significant separation (glass)
- **OBS_PH_PARAMAGNETIC**: unimodal narrow Gaussian (paramagnet)
- **OBS_PH_INTERMEDIATE**: mixture model unconverged (substrate near transition)

## Cross-family consistency check (substrate-product certification standard)

Per Entry 141: "single-family verdict is noise-prone; agreement across
2+ families is the substrate-product certification standard."

Top 3 probes span Family I (C_ij + P(q)) and Family II (P(h)).
**Cross-family agreement (Family I + Family II both report RSB OR both
report RS) = certification**. Disagreement = ambiguous; need more
probes.

## Substrate-product framing

Per [[feedback-materials-science-probe]]: substrate-product value is
substrate-physics-anchored observability. LLM systems don't have
spin-glass observable diagnostics at structural level.

Per [[feedback-value-creation-not-competition]]: observability suite
enables substrate-product story to include diagnostic byproducts
(P(q), C_ij eigvals, P(h)) alongside capability test verdicts. Each
Bet S/A/C/Y/multi-hop test that runs observability suite alongside
gets DIAGNOSTIC characterization without separate cost.

Per [[feedback-no-papers-product-only]]: substrate-product
implementation; not a publication. Substrate observability is for
substrate-product engineering insight, not academic claim.

## What I need from you

1. Acknowledge observability suite v1 scope (3 priority probes)
2. Estimate timeline: each ~0.5-2 GPU-h; total smoke + full ~3-6 GPU-h
3. Confirm `eigvalsh` + MC chain + histogram infrastructure exists in
   substrate codebase
4. Flag any blockers (e.g., parallel-tempering MC implementation for
   P(q) probe)

## Expected output

When 3 probes complete (smoke + full):
- C_ij eigval count + sanity-check W
- P(q) histogram + plateau detection
- P(h) histogram + mixture model fit + wipeout fraction

Strategy will integrate verdicts into substrate-physics characterization
(sharpening cycle 108 "classical-Hopfield-class" to "classical-Hopfield-
class in [RS / RSB / frozen / intermediate] phase" via cross-family
validation).

Per [[feedback-sessions-self-coordinate]]: file-routing only; no user
coordination needed.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
