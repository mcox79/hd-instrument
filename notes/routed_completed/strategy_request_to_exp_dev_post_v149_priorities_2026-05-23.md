# Strategy → Experiment Dev: Post-v149 priorities — Bet Z.5 + Observability V2 remainder + N=1M + multi-component order params

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-23 ~09:45 EDT
**Topic**: New Exp Dev priorities after v149 (cycle 168 META mixed + chi_4 FULL)
**cap_map state**: v149 (commit `855a837`)
**Trigger**: User signal "exp dev has no priorities from you"

## Context

Cycle 168 v149 confirmed Gap 1 EXPONENTIAL universality class at FULL + Gap 2
ORDER_PARAM_NONE REFUTED at FULL. Substrate-product holds at v148. Pipeline
GPU idle ~30 min. New priorities to maintain queue depth.

## PRIORITY 1 — Bet Z.5 Phase 1 Absorbing Discrete Diffusion Ensemble Smoother

**`wave14_betZ5_diffusion_smoother_phase1_v1`** (~4-6 hrs impl + 2-3 GPU-hrs):

Re-emphasize cycle 161 v144 Priority C. Still pending pickup. NEW substrate-novel
readout primitive with **posterior error CERTIFICATE** (missing from VAMP/smoother).

arXiv:2507.07586 PROVES O(1/√K) Bayesian posterior recovery. Phase 1:
- Train small MLP denoiser on N=4096 substrate chains with 10% masking
- K=50 ensemble passes
- Compare posterior mean vs VAMP; compare variance vs ground truth

Substrate-product implication if PASS: THIRD readout primitive with theoretical
posterior error bound. Extends operating envelope beyond backward-smoother d=500.

## PRIORITY 2 — Observability V2 remaining probes (Kovacs + avalanche)

**`wave14_kovacs_hump_v1`** (~5 min):
- Double-quench protocol β_high → β_low → β_target at energy=E_eq
- Measure non-monotonic overshoot amplitude
- Verdict KOVACS_RS_INDEPENDENT / KOVACS_BROAD_RELAXATION

**`wave14_avalanche_size_distribution_v1`** (~1 min):
- P(ΔE) energy-drop per spin-flip during argmax relaxation
- Power-law slope predicts smooth-cascade vs avalanche-trapping
- Verdict AVAL_ABBM_FIT / AVAL_STEEPER / AVAL_NONPOWER

Completes Observability Suite V2 (chi_4 already at FULL CHI4_RS_CONSISTENT).

## PRIORITY 3 — N=1M substrate stress test (16× beyond V2.D)

**`wave14_substrate_N1048576_v1`** (~60-120 GPU-min):

N=524K at FULL CONFIRMED (cycle 165 — 8× V2.D). Push 1 more doubling.

Backward-smoother readout at N=1048576 multi-hop chain composition.

**Verdict criteria**:
- N1M_SCALES: smoother@N=1048576 acc ≥ 0.50
- N1M_PARTIAL: acc 0.30-0.50
- N1M_KILLED: acc < 0.30

Substrate-product positioning: 16× beyond Bet Y V2.D scope at FULL.

## PRIORITY 4 — Multi-component order parameter tests (cycle 169 2x drill informed)

**`wave14_order_param_sub_K_region_v1`** (~30 GPU-min):

Cycle 168 META Gap 2 ORDER_PARAM_NONE REFUTED 3 single-component candidates
(φ_distribution + q_overlap + C_endpoint). Test MULTI-COMPONENT:

- Sub-K-region order parameters:
  - q_overlap restricted to K=900-1500 BROAD K-resonance band (cycle 165)
  - q_overlap restricted to K=100-500 normal cycle regime
  - q_overlap restricted to K=2000+ longer cycles regime
- Per-cycle-period order parameters

**Verdict criteria**:
- ORDER_PARAM_SUB_REGION_STABLE: at least one sub-region q_overlap > 0.85
  seed-consistency
- ORDER_PARAM_HIERARCHICAL: Parisi-like q(x) with multiple plateaus
- ORDER_PARAM_GLOBAL_NONE_CONFIRMED: all sub-regions also unstable

## PRIORITY 5 — Bet A continual-edit FULL multi-seed (long-overdue)

**`wave14_betA_continual_edit_N65536_5seed_v1`** (~60-120 GPU-min):

Cycle 132 smoke KILL never got proper 5-seed FULL. Cycle 157 v2 EXACT
match v1 smoke confirms single-seed reproducibility. But Research playbook
5-seed discipline missing.

Substrate-product completeness on continual-edit axis at N=65536.

## Pending pickup (still warrant attention)

- K1000_eigenspectrum_check_v1 FULL (was running ~44 min last check — possibly done?)
- K_resonance_wide_sweep_v1 FULL
- extreme_stress FULL (cycle 128 long-overdue)

## Total queue suggested

5 NEW priorities + pending pickups; smoke + FULL = 10-15 runs; ~8-12 GPU-hours total.

Recommended priority ordering:
1. **PRIORITY 2** Observability V2 Kovacs + avalanche (cheapest; ~6 min total)
2. **PRIORITY 3** N=1M stress test (substrate-product scope expansion)
3. **PRIORITY 4** Multi-component order parameter (substrate-physics gap)
4. **PRIORITY 5** Bet A 5-seed (substrate-product completeness)
5. **PRIORITY 1** Bet Z.5 Phase 1 (LONGEST; NEW primitive)
6. Pending pickup K1000_eigenspectrum + K_resonance_wide_sweep + extreme_stress

## Per [[feedback-no-papers-product-only]]

All priorities substrate-product oriented (Observability + scope + readout primitive
+ substrate-physics characterization).

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 30-90 min for P2 (cheapest) → full batch ~6-12 hrs.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
