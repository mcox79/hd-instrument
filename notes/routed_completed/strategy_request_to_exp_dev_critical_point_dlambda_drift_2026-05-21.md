# Strategy → Experiment Dev: Critical-point / Griffiths-phase δ(λ) drift gating test

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev (session 5)
**Date**: 2026-05-21 ~23:00 EDT
**Topic**: Revised critical-point gating test (per Research v85 deepdrill); δ(λ) drift = best 1-GPU-hour ROI

## Context

Per cap_map v82 → v85 honest recalibration cascade: substrate's
critical-point hypothesis (META P=50-65%) recalibrated to P=0.05
truly-critical (codimension-2 fine-tuning structurally implausible).
But aggregated P=0.75 "in extended critical regime" (tricritical 0.30
+ Griffiths 0.25 + RFOT mosaic 0.20).

**Substrate-product UPGRADE** discovered via Research v85: Griffiths
phase offers continuously-tunable avalanche exponent τ ∈ [1.20, 1.52]
(Cota-Odor-Ferreira arXiv:1801.06406, 2018) — substrate operator tunes
control parameter → selects operating exponent. **LARGER engineering
opportunity than single critical point.**

**Research-recommended gating test**: dynamical exponent **δ(λ) drift
measurement** (per Agent B Sonnet 2x analysis). Best 1-GPU-hour ROI
identified.

## Experiment spec

**Mechanism**: at substrate N=4096, Kerdock v4 codebook, current
operating parameters (α=0.153, β=32):

1. Run 3-5 short simulations at distinct values of control parameter
   λ ∈ {α, T} bracketing the transition (e.g., α ∈ {0.10, 0.13, 0.153,
   0.18, 0.22})
2. At each λ, measure ρ(t) (substrate density / overlap relaxation
   from random initialization) over O(10³) relaxation steps
3. Extract dynamical exponent δ(λ) from power-law fit ρ(t) ∝ t^(-δ(λ))
4. Plot δ(λ) vs λ

**Multi-probe success criteria**:

| Pattern | Substrate-physics interpretation | Substrate-product implication |
|---|---|---|
| **δ pinned across λ range** (within seed variance) | True criticality | V2.G STACK cheap construction (~0.05 P prior) |
| **δ drifts monotonically with λ** | **Griffiths phase** | Continuously-tunable engineering knob; SUBSTRATE-PRODUCT UPGRADE per [[feedback-value-creation-not-competition]] |
| δ has discontinuous jump at specific λ | First-order transition / tricritical | Substrate-product TBD; further investigation |
| δ noise-only (no λ dependence above seed variance) | Substrate not in extended critical regime | V2.G STACK requires explicit engineering (modal subcritical phase) |

**Kill criterion**: extraction fails (no power-law fit at any λ value;
R² < 0.7 across all λ) → protocol incompatible at N=4096; revert to
4-signature stack from cap_map v84 as fallback.

**Implementation outline**:
- Standard substrate init at random ±1 with no stored patterns
- Glauber dynamics with parametric (α, T) sweep
- Log ρ(t) = (1/N) Σᵢ ⟨sᵢ(t) sᵢ(0)⟩ (overlap with init state)
- Power-law fit on log-log axis; extract δ per λ
- 5 seeds per λ value for variance estimate

**Suggested name**: `wave14_critical_point_dlambda_drift_smoke_v1`

**Cost estimate**: ~1 GPU-hour total (per Research v85; 5 short sims
× O(10³) relaxation steps each at N=4096).

## Pre-armed 5 PROT-004 rescue sketches

If δ(λ) drift test returns ambiguous (e.g., δ extracted but neither
pinned nor monotonic):

1. Increase relaxation length to O(10⁴) — longer trajectories give
   tighter δ fits
2. Switch λ axis (try T-sweep if α-sweep ambiguous, or vice versa)
3. Larger N=8192 for one λ value to check FSS
4. Combine with S.2 AT-eigenvalue analytic (v84 fallback stack)
5. Apply surrogate-data null (S.4 Calvo 2026 methodology) to confirm
   δ signal vs randomized-couplings baseline

## Routing context

This test is the **revised gating test** per cap_map v85. It
SUPERSEDES my earlier 3-signature stack proposal (cap_map v82) and
the 4-signature stack (cap_map v84) as the optimal-ROI 1-GPU-hour
discriminator.

- Outcome shapes V2.G Bet Z STACK construction cost (cheap if
  Griffiths confirmed; expensive if subcritical or ambiguous)
- Outcome informs whether to pivot substrate-product story to
  "Griffiths-phase engineering knob" (better than fine-tuned point)

## Sequencing recommendation

Phase 1 (Bet S + Lane C smoke + Bet X) stays priority once
continual_8N_2000edits clears. THIS critical-point test slots IN
PARALLEL once Phase 1 first item picks up (cheap; orthogonal to
Phase 1 capability tests).

## What I will NOT do unilaterally

- Build (Experiment Dev scope)
- Claim Griffiths phase or criticality before δ(λ) drift result
- Promote V2.G STACK construction without smoke result

## Cross-references

- `notes/research_triple_point_deepdrill_2026-05-21.md` (v85 source;
  δ(λ) drift recommendation in Agent B section)
- `notes/research_critical_point_protocol_2026-05-21.md` (v84
  4-signature fallback stack)
- `notes/substrate_capability_map.md` v85 (cap_map promotion)
- `notes/meta_request_to_strategy_v2g_phase_track_2026-05-21.md`
  (V2.G context)

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
