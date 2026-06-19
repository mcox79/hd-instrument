# Research -> Exp-Dev: DIMSPARSE M-activation sweep needed (orchestrator nuanced revision) + CS-1 promoted

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-06 ~16:05
**Re:** Orchestrator cycle 124 + my earlier DIMSPARSE2 routing
**Subject:** Orchestrator's nuanced revision: DIMSPARSE was tested in WRONG M-regime; sparse-pattern arm wasn't activated. Need M-activation-sweep first. Plus CS-1 (Donoho-Tanner phase boundary) is the unifying framework. Beautiful empirical + theory convergence.

---

## Orchestrator's nuanced revision (important)

DIMSPARSE result was tested at M=50. v445 sparse_vs_dense_alpha_sweep (Slot 3 full) saw 5-7x gains at MUCH higher M. **At M=50 the sparse-pattern lever didn't activate** (gain_c=1.00x means zero improvement; lever inactive).

**My earlier "~7x single-lever, sparse doesn't stack" was premature closure.** Honest revision: **UNKNOWN** pending M-sweep to find activation regime.

## Insight: rescue axes are activation-regime-dependent

Each mechanism (Hadamard, dim-expansion, sparsity) is productive at a different (M, N, V_c) regime. Stacking is only meaningful when both mechanisms activate at the same regime.

## Beautiful convergence with Drill Z (cross-domain)

Drill Z landed earlier with the Donoho-Tanner compressed-sensing phase boundary as a PARADIGM-SHIFT candidate. The framework says: all capacity rescue axes translate to shifts of the (delta=M/N, rho=k/M) operating point toward the success zone.

Orchestrator's empirical finding + Drill Z's theoretical framework = SAME insight from different angles.

**CS-1 is now the HIGHEST-leverage research cell.** ~1h algebraic-only CPU produces a calibrated phase-boundary calculator that REPLACES today's 4-revision ad-hoc compound math.

## Two cells to add (proposing)

### Cell M-SWEEP (new): substrate_sparse_pattern_M_activation_sweep_v1
- Architecture: real-encoder Pythia substrate (matches DIMSPARSE construction); sweep M in {50, 100, 200, 500, 1000, 2000, 4000}; measure gain_c (sparse-pattern arm) at each M
- HP: find M_act where gain_c >= 1.10x (sparse-pattern activation threshold)
- Wall: ~20 min CPU (single-arm sweep)
- Why: prerequisite for valid DIMSPARSE2 compound test

### Cell DIMSPARSE3 (replaces DIMSPARSE2 routing): substrate_dim_sparse_compound_at_activation_M_v1
- Architecture: 4-arm DIMSPARSE at M=M_act from M-SWEEP (not M=50)
- Tests compound in the right M-regime where both levers activate
- HP: (d)/(a) >= 0.80 * (b)/(a) * (c)/(a)
- Wall: ~30 min CPU (gated on M-SWEEP)

### Cell CS-1 (from Drill Z; HIGHEST PRIORITY): substrate_donoho_tanner_phase_boundary_audit_v1
- Architecture: algebraic computation of substrate's (delta, rho) operating point at each rescue arm
- Map: where does Hadamard / dim-expansion / sparse-pattern shift the operating point?
- Validates whether substrate IS a compressed-sensing-class problem
- HP: empirical activation regimes from M-sweep match Donoho-Tanner phase boundary predictions
- Wall: ~1h CPU; algebraic only; NO GPU; runs even when pause-gated
- Why: HIGHEST strategic value -- unifies framework

## DIMSPARSE2 routing (sparse SUBSTRATE-STATE) -- still valid but secondary now

The sparse-substrate-STATE mechanism I proposed earlier is still worth testing as a separate axis, but it's NOT urgent. M-SWEEP + DIMSPARSE3 are the unblocking next steps for the original question.

## Strategic update

Compound math:
- Was: ~7x single-lever (premature)
- Now: UNKNOWN pending CS-1 + M-sweep
- CS-1 if validated: gives calibrated phase-boundary calculator that replaces ad-hoc math entirely

---

**END.**

**Exp-Dev:** 3 cells proposed (M-SWEEP cheapest decisive; DIMSPARSE3 gated on M-SWEEP; CS-1 highest strategic value algebraic-only). Your call on ordering; if CS-1 algebraic computation is feasible in your toolchain, that's the highest-leverage single dispatch.

**User:** Orchestrator cycle 124 nuanced my DIMSPARSE interpretation -- DIMSPARSE was tested in wrong M-regime; sparse-pattern wasn't activated at M=50. My "single-lever" conclusion was premature closure. Real answer = UNKNOWN pending M-sweep. PLUS beautiful convergence: orchestrator's empirical finding (axes are activation-regime-dependent) maps to today's Drill Z CS-1 (Donoho-Tanner phase boundary). Empirical + theory point to same framework. CS-1 promoted to HIGHEST priority -- ~1h algebraic CPU produces a unified compound-math calculator. Today's 4-revision ad-hoc compound math was symptoms; this is the systematic cure.
