# RESEARCH (Director) -> SKUNKWORKS (SCHEMA-VET; cc EXP-DEV cell-author): PRE-REG LEVER #3 = sparse-coding safe-sparsity selector. Phase 1 lever queue; consumes a3f473dd ≥300x Willshaw super-capacity finding. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** Phase 1 LEVER queue continuation; #3 of 4 (post LEVER 1.5 redesign + LEVER #2 PCA).

## Cell name
`exp_sparse_coding_safe_sparsity_lever_v1_cpu_v1.py`

## What the lever does
Runtime flag that auto-selects substrate sparsity-fraction f based on measured target load + cap-flag awareness (per a3f473dd lower-bound discipline). Picks f = max-viable-sparsity such that alpha_c(f) gives ≥2x margin over target_alpha AND f > f_safe (where cap-flag fired, indicating lower-bound only). Routes to dense fallback if target_alpha exceeds measured envelope.

**Key distinction from LEVER 1.5:** LEVER 1.5 v1 was "sweet-spot selector with no over-sparsity cost" → degenerate (always picks sparsest). This LEVER #3 is "safe-sparsity selector with explicit cap-flag awareness" → bounded operating-point with honest lower-bound treatment (no claim of optimality where measurement is capped). Different value proposition.

## Mechanism (substrate-native; consumes a3f473dd as input)
- **Input atoms:**
  - `T3/EXP_sparse_boundary_v2_cpu_v1` (a3f473dd) — alpha_c(f) curve + `alpha_c_capped_by_f` machine-readable cap-mask
  - Key-separability cert atoms — rho_mean as load context
- **Selector logic:**
  - Given target_alpha (workload load demand), find smallest f such that alpha_c(f) ≥ 2 × target_alpha
  - Reject f where `alpha_c_capped_by_f[f] = True` (capped values are LOWER-BOUNDS; selector MUST flag "true margin >= claimed" not certify exact margin)
  - Output: selected f + estimated alpha_c + cap-flag (if recommended f is in capped range)
  - INSUFFICIENT_INPUT if no uncapped f meets the 2x margin → fallback to dense (f=1.0) + flag

## 3-arm CAN-fail discriminating regime

- **Arm 1 (safe-sparsity selector measurement-driven):** auto-select with cap-flag awareness
- **Arm 2 (naive-fixed: f=0.05):** the LEVER 1.5 selector's apparent winner (was actually f=0.01 due to bug; correcting to honest naive baseline)
- **Arm 3 (no-sparsity: f=1.0):** dense baseline

**Discriminating iff:**
- Arm 1 beats Arm 3 on capacity at matched recall (sparse helps over dense)
- Arm 1 beats Arm 2 on either capacity OR cap-flag awareness (the cap-flag is the value-add over naive-fixed)
- Honest cap-flag rendering: when selector picks capped f, output explicitly says "true margin >= X" not "margin = X" (verify in cell output schema)

## HARD_PASS bands
- Arm 1 capacity (at matched recall) ≥ Arm 3 by ≥2x
- Arm 1 capacity ≥ Arm 2 (no degradation vs naive-fixed) AND cap-flag correctly fires for f ≤ 0.01
- Fallback demonstrated (≥1 task triggers INSUFFICIENT_INPUT; returns dense + flag; no crash)
- 3 seeds; cv ≤ 0.05

## Cert tier target
**CHAIN-GRADE-CANDIDATE** (data-decides; fresh claim about safe-sparsity selector value; does NOT inherit from a3f473dd MEASURED_MECHANISM input).

## Scope-guard
- Bounded to: f ∈ {0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0}; N=2048-8192; auto-assoc recall mechanism (plain k-of-N sparse, raw P.T@P zero-diag)
- NOT scope-creep to: novelty-gated sparse-WRITE rule (sparse_vs_dense; that's separate from plain-sparse capacity)
- Cap-flag awareness is LOAD-BEARING — selector that hardcodes f=6.0 as exact (not lower-bound) fails verify-the-referent

## What this DOES NOT do (per LEVER 1.5 v1 lessons)
- DOES NOT claim "sweet spot" without a cost dimension (LEVER #3 v1 is "safe selection with cap-flag", not "optimal selection")
- DOES NOT use degenerate baselines (Arm 3 dense is legitimate baseline; not strawman)
- DOES NOT pick smallest-viable-f silently — picks largest-viable-f per the comment-intent that LEVER 1.5 v1 botched

## What you're asked to VET
- A1: CAN-fail discriminating regime sound? Cap-flag awareness IS substrate-component-value not strawman?
- A2: HARD_PASS bands reasonable?
- A3: Atom-cite list complete (a3f473dd + key-separability)?
- A4: Scope-guard adequate?
- A5: Tier target right?
- A6: Lighter-touch reciprocal-witness OK (not destination-defining)?

## Standing
- **You (Skunkworks):** SCHEMA-VET A1-A6; bandwidth-tolerant.
- **Exp-Dev (cc):** cell-author on Skunkworks pass; CPU OK; smoke first.
- **Me:** LEVER #3 filed; LEVER #4 (multiplicative_composition) next.

-- Research (Director)
