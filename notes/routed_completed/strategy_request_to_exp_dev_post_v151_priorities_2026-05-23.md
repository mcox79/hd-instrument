# Strategy → Experiment Dev: Post-v151 priorities — Cap 1 Crooks forensic erase + Gap B/C rescue paths + 3 other capabilities

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-23 ~10:00 EDT
**Topic**: 7 NEW priorities from Research deliveries (4 capabilities + 3 META gap rescues)
**cap_map state**: v151 (commit `0691d24`)
**Trigger**: User signal "have you shared priority to exp dev"

## Context

Cycle 171 v151 integrated 2 substantive Research deliveries:
- 4 NEW substrate capability candidates (theorem-implied; ALL use existing infrastructure)
- 3 META gap rescue paths (M-storage + Online W + Calibrated confidence)

Filing focused Exp Dev priorities ordered by leverage-per-cost.

## PRIORITY 1 — 🏆 Cap 1 Crooks-ratio forensic erase audit (COMMERCIAL WEDGE)

**`wave14_crooks_forensic_erase_audit_v1`** (~10-15 GPU-min smoke):

Maps to capability class 1 (verifiable forensic erase) — substrate-product
COMMERCIAL WEDGE. P=0.55.

```python
def crooks_audit(W, codebook, k, v, n_trials=50):
    # WRITE
    B = apply_hadamard_bind(k, v)
    forward_marginals = run_vamp_to_convergence(B)  # {q_t}
    forward_entropy = compute_KL_path(forward_marginals)

    # ERASE candidate (Hadamard self-inverse)
    B_erased = apply_hadamard_bind(B, k, v)  # bind(k,v) again
    reverse_marginals = run_vamp_to_convergence(B_erased)
    reverse_entropy = compute_KL_path(reverse_marginals)

    # AUDIT log-ratio = empirical entropy production
    delta_S = forward_entropy - reverse_entropy
    return delta_S
```

**Verdict criteria**:
- **CROOKS_ERASE_VERIFIED**: ΔS_emp < 0.05 (erase verifiable per Crooks FT)
- **CROOKS_PARTIAL**: 0.05 ≤ ΔS_emp ≤ 0.5 (partial erase with quantitative residual)
- **CROOKS_FAILED**: ΔS_emp > 0.5 (erase incomplete; large residual)

**Substrate-product implication if VERIFIED**: substrate gains substrate-novel
forensic-erase capability with theorem-anchored audit. Class 1 commercial wedge.

## PRIORITY 2 — Gap C P(q) bootstrap + conformal prediction (calibrated confidence)

**`wave14_conformal_pq_confidence_v1`** (~30 GPU-min):

Fixes Bet G TEMPSCALE_KILLED (cycle 168). Research P=0.55-0.65 theorem-backed.

```python
def conformal_calibration(substrate, N=65536, n_calibration=500, n_test=500):
    # P(q) bootstrap variance ensemble
    pq_calibration = [run_pq_diagnostic(substrate, seed=s) for s in range(n_calibration)]

    # Conformal prediction wrapper
    cp_threshold = compute_conformal_threshold(pq_calibration, target_coverage=0.95)

    # Test on held-out
    coverage = check_coverage(cp_threshold, test_queries[:n_test])
    return coverage
```

**Verdict criteria**:
- **CONFORMAL_COVERED**: coverage ≥ 0.93 ≤ 0.97 (proper 95% coverage)
- **CONFORMAL_OVERCOVERAGE**: coverage > 0.97 (too conservative)
- **CONFORMAL_UNDERCOVERAGE**: coverage < 0.93 (calibration fails)

**Substrate-product implication if COVERED**: Bet G calibration rescued via
distribution-free conformal prediction; substrate-product gains theoretical-anchored
calibrated confidence at N=65536.

## PRIORITY 3 — Gap B Online W updates with Robbins-Monro + SNAP

**`wave14_online_W_robbins_monro_snap_v1`** (~30 GPU-min):

Substrate has local-additive W but no demonstration of online W updates resistant
to catastrophic forgetting. Research P=0.50.

```python
def online_W_test(substrate, sequence_length=50):
    # Sequential 50-write test
    accs = []
    for step in range(sequence_length):
        # Robbins-Monro update with SNAP saturation guard
        substrate.update_W_with_snap(new_pattern, lr=robbins_monro_schedule(step))
        # Retrieval check on all prior patterns
        accs.append(check_retrieval_accuracy(substrate, all_prior_patterns))
    return accs
```

**Verdict criteria**:
- **ONLINE_W_RESISTS_CF**: acc ≥ 0.95 throughout 50 sequential writes
- **ONLINE_W_GRADUAL_FORGETTING**: acc decay > 0.5 by step 50
- **ONLINE_W_CATASTROPHIC**: acc < 0.3 at any step

**Substrate-product implication if PASS**: substrate gains demonstrated online
learning capability with theoretical anchor (Robbins-Monro convergence; SNAP
catastrophic-forgetting prevention).

## PRIORITY 4 — Cap 2 Self-monitoring confidence via critical slowing down

**`wave14_critical_slowing_down_self_monitor_v1`** (~10 GPU-min):

Marginal stability gapless Hessian implies substrate exhibits critical slowing
down near retrieval errors. Use timing as confidence indicator.

```python
def critical_slowing_confidence(substrate, queries):
    correlation_times = []
    accuracies = []
    for q in queries:
        tau = measure_VAMP_relaxation_time(substrate, q)
        correlation_times.append(tau)
        accuracies.append(check_retrieval(substrate, q))
    # Predict accuracy from relaxation time
    correlation = correlate(correlation_times, 1 - accuracies)
    return correlation
```

**Verdict criteria**:
- **SLOWING_DOWN_DETECTS**: correlation ≥ 0.50 (relaxation time predicts errors)
- **NO_CORRELATION**: |correlation| < 0.20

## PRIORITY 5 — Cap 3 Steady-state continuous streaming inference

**`wave14_continuous_streaming_inference_v1`** (~15 GPU-min):

Drift-diffusion NESS implies substrate can run continuously with streaming
inputs producing continuous outputs.

**Verdict criteria**:
- **STREAMING_CONTINUOUS_PASS**: throughput steady-state ≥ baseline
- **STREAMING_NESS_BREAKS**: throughput collapses after burn-in

## PRIORITY 6 — Cap 4 P(q) shape introspection

**`wave14_pq_shape_introspection_v1`** (~10 GPU-min):

Substrate's P(q) shape changes across phases (sub-K-region multi-component).
Substrate can self-introspect phase via P(q) shape moments.

**Verdict criteria**:
- **PQ_INTROSPECTION_DETECTS**: P(q) moment shifts correlate with phase changes
- **PQ_NO_PHASE_SIGNATURE**: P(q) shape invariant across phases

## DEFERRED — Gap A spatially-coupled codebook (Phase A; ~1 day)

`wave14_spatially_coupled_codebook_block_vamp_v1`: substantial work
(~1 day) per Research (phase-boundary N-sweep). Defer until Cap 1-6 +
Gap B/C settle.

## Pending pickup (cycle 170 routing `9a41861`)

- P(q) discrete spikes (cycle 170 P-D)
- Endpoint RM(1,16) projection (cycle 170 P-C)
- Coset-count sweep (cycle 170 P-B)
- P(q) distributional 50-seed (cycle 170 P-A; smoke REFUTED at cycle 171)

Plus older pending: Bet Z.5 Phase 1, K1000_eigenspectrum FULL, K_resonance_wide_sweep
FULL, extreme_stress FULL.

## Priority ordering recommendation

1. **PRIORITY 1** Crooks forensic erase (commercial wedge; ~15 min smoke)
2. **PRIORITY 4** Self-monitoring critical slowing down (~10 min)
3. **PRIORITY 6** P(q) shape introspection (~10 min)
4. **PRIORITY 5** Streaming inference (~15 min)
5. **PRIORITY 2** Conformal calibrated confidence (~30 min)
6. **PRIORITY 3** Online W Robbins-Monro+SNAP (~30 min)
7. Cycle 170 remaining P-B/C/D (substrate-physics)
8. DEFERRED Gap A spatially-coupled (Phase A)

Total Phase 1 batch ~2-3 GPU-hours.

## Per [[feedback-no-papers-product-only]]

ALL priorities substrate-product oriented:
- P1: Class 1 commercial wedge forensic erase
- P2: Bet G calibration rescue (theoretical anchor)
- P3: substrate-product completeness on online editing
- P4/P5/P6: NEW substrate-product capability candidates

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 60-180 min for Phase 1 batch.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
