# Strategy → Experiment Dev: Post-v144 priorities — Arnold-tongue gate + Observability V2 + Bet Z.5

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-23 ~07:10 EDT
**Topic**: New priorities from cycle 160 v144 Research deliveries
**cap_map state**: v144 (commit `f7f2a70`)
**Trigger**: User signal "do you have new priorities for exp dev"; Research K-resonance + fresh angles delivered substantive new directions

## Context

Cycle 160 v144 integrated 2 Research deliveries:
1. **K-resonance**: Arnold-tongue mode-locking framework P=[0.30, 0.50] — NOT Kerdock-algebraic; cheap decisive test is eigenvalue ratio at K=1000
2. **Fresh angles**: Observability V2 (chi_4 + Kovacs + avalanche) + Bet Z.5 Absorbing Diffusion Ensemble + Bundle Decomposition

3 NEW priorities emerge, ordered by leverage-per-cost.

## PRIORITY A — Eigenvalue ratio at K=1000 (CHEAPEST decisive test)

**`wave14_K1000_eigenspectrum_check_v1`** (~5 min CPU):

Direct test of Arnold-tongue mode-locking framework. Compute W's top-10
eigenvalues at K=1000 N=65536; check λ₁/λ₂ ratio against rational values.

```python
import numpy as np
# Build W at N=65536 K=1000 (Hebbian outer-product)
eigs = np.linalg.eigvalsh(W)
sorted_eigs = np.sort(np.abs(eigs))[::-1]
ratio = sorted_eigs[1] / sorted_eigs[0]
print(f"lambda_2/lambda_1 = {ratio}")
# Check against rational values
for m, n in [(1, 2), (2, 3), (1, 3), (3, 4), (1, 4), (3, 5), (2, 5)]:
    if abs(ratio - m/n) < 0.01:
        print(f"COMMENSURABILITY CONFIRMED at {m}/{n}")
```

**Verdict criteria**:
- **K1000_RATIONAL_COMMENSURABLE**: λ₁/λ₂ ∈ {0.5, 0.667, 0.333, 0.75, 0.25, 0.6, 0.4} ± 0.01 → Arnold-tongue mechanism CONFIRMED
- **K1000_IRRATIONAL_NEAR**: ratio close to irrational (e.g., 0.5±0.05 but not within 0.01) → partial framework
- **K1000_IRRATIONAL_FAR**: ratio not near any rational → Arnold-tongue REFUTED

**Single decisive test**. ~5 min CPU. If PASS: Arnold-tongue framework
empirically supported; substrate-physics characterization gains theoretical
anchor.

## PRIORITY B — Observability Suite V2 (3 cheap probes, <10 min total)

Extends cycle 109 observability_suite_v1. 3 NEW spin-glass probes per
Research fresh angles delivery:

**`wave14_chi4_dynamic_overlap_v1`** (~30 sec):
- Compute χ₄(t) = N · Var_runs[(1/N) Σ_i s_i(0) s_i(t)] across 100 noisy retrievals
- Predicted RS-phase + K/N≈0.0015: χ₄(t*) < 10
- Verdict CHI4_RS_CONSISTENT < 10 / CHI4_HIDDEN_RSB > 50

**`wave14_kovacs_hump_v1`** (~5 min):
- Double-quench protocol: β_high → β_low → β_target measure energy overshoot
- Predicted RS-phase: amplitude independent of t_w
- Verdict KOVACS_RS_INDEPENDENT / KOVACS_BROAD_RELAXATION grows with log(t_w)

**`wave14_avalanche_size_distribution_v1`** (~1 min):
- P(ΔE) energy-drop magnitude per spin-flip during argmax relaxation
- Predicted ABBM mean-field universality: P(ΔE) ~ ΔE^(-3/2)
- Substrate RS-phase: steeper exponent expected
- Verdict AVAL_ABBM_FIT / AVAL_STEEPER / AVAL_NONPOWER

Total <10 min. Substrate-physics characterization extension.

## PRIORITY C — Bet Z.5 Absorbing Discrete Diffusion Ensemble Smoother

**`wave14_betZ5_diffusion_smoother_phase1_v1`** (~4-6 hrs impl + 2-3 GPU-hrs):

NEW readout primitive with **posterior error CERTIFICATE** (missing from VAMP).
arXiv:2507.07586 (2025) PROVES O(1/√K) Bayesian recovery for K denoising passes.

**Phase 1**: Train small MLP denoiser on N=4096 substrate chains with 10%
masking; K=50 ensemble passes; compare posterior mean vs VAMP; compare variance
vs ground truth.

**Verdict criteria**:
- **BETZ5_PHASE1_PASS**: posterior mean ≈ VAMP + variance calibrated → ship as Bet Z.5
- **BETZ5_PHASE1_PARTIAL**: posterior mean ≈ VAMP but variance miscalibrated
- **BETZ5_PHASE1_KILLED**: posterior mean diverges from VAMP → diffusion framework wrong

Substrate-product implication if PASS: substrate-product gains THIRD readout
primitive with theoretical-anchor posterior error bound. Extends operating
envelope beyond backward-smoother d=500.

## Priority ordering recommendation

1. **PRIORITY A** eigenvalue test (~5 min CPU; cheapest decisive)
2. **PRIORITY B** Observability V2 (~10 min GPU; substrate-physics characterization extension)
3. **PRIORITY C** Bet Z.5 Phase 1 (~6-9 hrs total; NEW readout primitive)

## Pending pickup from earlier routings (re-emphasize)

- **`7138bc9` cycle 160 K-resonance batch**: wave14_K_resonance_fine_sweep_v1 +
  wave14_K_resonance_full_sweep_v1 + wave14_demo_1_K1000_smoother_v1 +
  wave14_forward_argmax_K1000_v1
- **`a750734` cycle 156 substantive batch**: head-to-head VAMP/smoother + Demo
  2 5-seed + N=524K + cross-task 5-seed
- **`f919da8` cycle 138 retraction Phase 1**: FULL still pending
- **`d6caeba` cycle 136 batch remainder**: Bet A FULL + extreme_stress FULL + smoother extreme_K FULL
- **`c1acdbd` cycle 128**: extreme_stress FULL long-overdue

## Per [[feedback-no-papers-product-only]]

All priorities substrate-product oriented:
- P-A: substrate-physics mechanism characterization (Arnold-tongue framework)
- P-B: substrate-physics observability extension (matsci probes)
- P-C: substrate-product NEW readout primitive (theoretical-anchor posterior error)

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 5 min (P-A) → 10 min (P-B) → 6-9 hrs (P-C).

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
