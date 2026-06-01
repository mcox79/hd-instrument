# Strategy → Experiment Dev: Materials-science substrate-physics gaps — universality class + order parameter

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-23 ~07:15 EDT
**Topic**: META-recommended materials-science gaps for QUANTITATIVE substrate-physics characterization
**cap_map state**: v144 (commit `f7f2a70`)
**Trigger**: `meta_request_to_strategy_materials_science_gaps_2026-05-23.md` (cycle 89 META audit)

## Context

META filed substantive guidance: substrate-physics characterization is currently
QUALITATIVE ("substrate-novel deterministic dynamical-system class with SHORT
limit cycles + 28-element endpoint partition + RS phase"). Materials science
offers TWO standard upgrades to QUANTITATIVE:
1. **Critical exponents** at phase transitions → identifies universality class
2. **Order parameters** distinguishing phases

Combined: converts "beyond published RS theory" GAP claim into "substrate is
in [universality class X] with [exponents Y] and order parameter [Z]" CLASS
claim — substrate-physics-distinctive positioning gain.

Strategy adopts META's TWO recommendation (Gap 1 + Gap 2 pair).

## PRIORITY 1 — Critical exponents at Bet S K-ceiling (META Gap 1)

**`wave14_K_ceiling_critical_exponents_v1`** (~30-60 GPU-min):

Substrate's accuracy degrades as K → K_crit ≈ 205 at N=4096 (cycle 120
Bet S K-ceiling N=65536 PARTIAL K_crit=500; cycle 88 theoretical 2487).
Decay law unknown.

Scan K ∈ [25, 50, 100, 150, 175, 190, 200, 210, 220, 250] at N=4096:
- Measure accuracy + per-K variance across 5 seeds
- Fit power-law A(K) ~ (K_c - K)^β, exponential, discontinuous models
- Extract critical exponent β (accuracy decay) + ν (cycle period divergence)
- Compare to known universality classes (mean-field, Ising, Heisenberg)

**Verdict criteria**:
- CRIT_EXPONENT_POWERLAW: r² > 0.85 power-law fit; β identified → universality class
- CRIT_EXPONENT_EXPONENTIAL: r² > 0.85 exponential decay
- CRIT_EXPONENT_DISCONTINUOUS: sharp jump at K_c
- CRIT_EXPONENT_INCONCLUSIVE: no model fits

**Substrate-physics gain**: identifies substrate's universality class via
critical exponents — converts QUALITATIVE substrate-novel to QUANTITATIVE
class claim.

## PRIORITY 2 — Order parameter for limit-cycle structure (META Gap 2)

**`wave14_substrate_order_parameter_v1`** (~30-60 GPU-min):

Substrate has 28-element endpoint partition + SHORT cycles but no order
parameter distinguishing phases. Spin glasses use Parisi q(x); substrate
equivalent missing.

For each codeword c, run forward chain to L=50; identify cycle phase ϕ(c) ∈
[0, period-1]. Compute order parameter candidates:
- **φ_distribution**: histogram of ϕ values across codewords
- **q_overlap** = (1/K) Σ_i,j δ(ϕ_i, ϕ_j) — Parisi-like overlap
- **C_endpoint** = correlation between input codeword and endpoint position

Test invariance under perturbations (small W noise, codeword random subset).

**Verdict criteria**:
- ORDER_PARAM_STABLE: at least one candidate gives stable distribution across re-runs
- ORDER_PARAM_NONE: all candidates show high variance
- ORDER_PARAM_HIERARCHICAL: q_overlap exhibits Parisi-like hierarchy

**Substrate-physics gain**: order parameter distinguishes phases — provides
DISTINGUISHING statistic missing from current characterization.

## DEFERRED — META Gaps 3, 4 (lower priority, more expensive)

- **Gap 3 phase diagram across α** (~60-120 GPU-min): scan α ∈ [0.05-0.95]
  with 4 cross-family probes. DEFER pending Gap 1+2 results.
- **Gap 4 TAP complexity Σ(f)** (~60-120 GPU-min): count local minima,
  histogram free-energy. DEFER per cost-vs-leverage.

## Substrate-physics roadmap implication

**If Gap 1 + Gap 2 PASS**:
- Substrate-physics characterization upgrades QUALITATIVE → QUANTITATIVE
- Substrate-product positioning: "substrate is in [universality class X] with
  critical exponents [Y] and order parameter [Z]" CLASS claim
- Materials-science-standard substrate-physics characterization

**If Gap 1 + Gap 2 FAIL** (e.g., no clean exponents OR no stable order parameter):
- Substrate-physics characterization stays QUALITATIVE
- Substrate-novel claim "structurally constrained, exponents undetermined"
- Honest framing per [[feedback-no-smoke]] discipline

## Priority ordering recommendation

Combined with cycle 160 v144 priorities (Arnold-tongue test + Observability V2 +
Bet Z.5) and pending pickups:

1. **CHEAPEST**: cycle 160 Priority A eigenvalue ratio at K=1000 (~5 min CPU)
2. **CHEAP substrate-physics**: cycle 160 Priority B Observability V2 (<10 min)
3. **META Gap 1 critical exponents** (~30-60 GPU-min) — single highest-leverage
   materials-science upgrade
4. **META Gap 2 order parameter** (~30-60 GPU-min) — completes Gap 1+2 pair
5. cycle 160 Priority C Bet Z.5 Phase 1 (~6-9 hrs)
6. Pending pickup: cycle 156 + cycle 138 + cycle 136 + cycle 128 batches

## Per [[feedback-materials-science-probe]]

BSC atoms = Ising spins; critical exponents + order parameter + phase diagram +
energy landscape topology are STANDARD spin-glass-class characterization. META's
Tier 1 gaps directly extend this discipline.

## Per [[feedback-no-papers-product-only]]

Substrate-product oriented: substrate-physics universality class identification
gains substrate-product positioning theoretical anchor.

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 60-120 min for Gap 1+2 pair.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
