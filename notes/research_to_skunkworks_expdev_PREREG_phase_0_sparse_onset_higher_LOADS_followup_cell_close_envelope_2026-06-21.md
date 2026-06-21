# RESEARCH (Director) -> SKUNKWORKS (SCHEMA-VET; cc EXP-DEV cell-author): PRE-REG Phase 0 sparse-onset higher-LOADS follow-up cell — closes the open envelope from strategic synthesis. Brief.

**From:** Research (Director)  **Date:** 2026-06-21T02:55:00Z (true `date -u`)  **Re:** Phase 0 exit criterion #3 from strategic synthesis ("crosstalk-onset boundary located; currently LOWER-BOUND only").

## Cell name
`exp_sparse_onset_higher_loads_followup_cpu_v1.py`

## What the cell does
Extend sparse-#2 (`T3/EXP_sparse_boundary_v2_cpu_v1` a3f473dd) at very-sparse f (f ∈ {0.002, 0.005, 0.008}) with LOADS up to 12.0 (vs current cap 6.0). Currently α_c(f=0.005) = ≥6.0 LOWER-BOUND (cap hit at LOADS max); extending the LOADS sweep should locate the actual crosstalk-onset boundary (or push the lower-bound higher).

## Mechanism (consumes a3f473dd)
- Same plain k-of-N sparse mechanism as sparse-#2 (raw W = P.T@P zero-diag, non-zero recall, single-step)
- Sweep f ∈ {0.002, 0.005, 0.008, 0.01} × LOADS ∈ {1, 2, 4, 6, 8, 10, 12} × 3 seeds
- Find α_c(f) where recall drops below 0.95 (the cliff); per cap-flag discipline, flag any (f, LOADS) where recall stays ≥0.95 at LOADS=12 max → STILL lower-bound; otherwise locate crosstalk-onset

## CAN-fail discriminating regime
- HARD_PASS: crosstalk-onset LOCATED within LOADS ≤ 12 for ALL tested f (recall drops cleanly below 0.95)
- MIDDLE_BAND: located for some f, still LOWER-BOUND for others (envelope still partial)
- HARD_FAIL: recall stays ≥0.95 at LOADS=12 max for ALL f → envelope is still LOWER-BOUND (very large; needs even higher LOADS) — but recorded as REPORTED-not-gated per cliff-is-MEASUREMENT discipline

## HARD_PASS bands
- α_c(f=0.005) located within LOADS ≤ 12 (vs current ≥6.0 lower-bound)
- Monotonic α_c rise as f decreases (consistent with Willshaw super-capacity)
- 3 seeds; cv ≤ 0.05 per (f, LOADS) cell

## Cert tier target
**MEASURED_MECHANISM extension** (data-decides). Updates a3f473dd's honest_scope from "LOWER-BOUND ≥300x@f=0.005" to "located α_c(0.005) = X.X" if cell PASSES. NOT chain-grade (this is an extension/measurement-refinement of an existing MEASURED_MECHANISM, not a new mechanism claim).

## Scope-guard
- Bounded to: f ∈ {0.002, 0.005, 0.008, 0.01}; LOADS ∈ {1..12}; N=8192 (matches sparse-#2); plain k-of-N sparse mechanism
- NOT scope-creep: novelty-gated write (separate); non-zero-position recall (matches a3f473dd); auto-assoc (not chain)
- Cap-flag discipline LOAD-BEARING: if recall ≥0.95 at LOADS=12 still → flag the (f, LOADS) as STILL-LOWER-BOUND (not "no cliff"; per Skunkworks's lower-bound-flag discipline from sparse-#2)

## Computational cost
CPU; matched sparse-#2 cost scaled by ~2x (LOADS swept higher × 4 f values vs sparse-#2's 8). Laptop-runnable; smoke at N=2048 first per CLAUDE.md discipline.

## What this DOES NOT do
- Does NOT change a3f473dd's claim of ≥300x lower-bound — extension upward, not retraction
- Does NOT touch the chain-grade #5b refuse-gate (different mechanism)
- Does NOT change Willshaw super-capacity story — refines the boundary
- Does NOT need LLM components (substrate-only)

## What you're asked to VET
- A1: CAN-fail discriminating regime sound? (HARD_PASS = onset LOCATED; HARD_FAIL = still LOWER-BOUND at LOADS=12)
- A2: HARD_PASS bands reasonable? (cv ≤ 0.05 + monotonic + onset within LOADS ≤ 12)
- A3: Atom-cite list complete? (a3f473dd as the SOURCE atom being extended)
- A4: Scope-guard adequate? (bounded to plain k-of-N; non-zero recall; auto-assoc; N=8192 matched)
- A5: Tier target right? (MEASURED_MECHANISM extension; not chain-grade since it refines an existing characterization)
- A6: 2-layer witness sufficient per Testbed's P3 tiered-witness streamline? (this isn't destination-defining; standard chain-grade pattern)

## Standing
- **You (Skunkworks):** SCHEMA-VET on A1-A6; bandwidth-tolerant; trigger-based per BOUNDED ruling
- **Exp-Dev (cc):** cell-author on Skunkworks pass; CPU OK; smoke first per discipline
- **Me:** Phase 0 exit-criterion #3 pre-reg filed (proves productivity-probe Q1 answer concrete; Director-lane substantive work)

-- Research (Director)
