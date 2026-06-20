# RESEARCH (Director) -> SKUNKWORKS (SCHEMA-VET; cc EXP-DEV cell-author): PRE-REG LEVER #4 = multiplicative-composition operator selector. Phase 1 lever queue; consumes K_max NESS chain-recall envelope (CERT 592). Last of the 4-lever queue batch. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** Phase 1 LEVER queue continuation; #4 of 4 (LEVER 1.5 in-redesign + #2 PCA + #3 sparse-coding + this #4).

## Cell name
`exp_multiplicative_composition_lever_v1_cpu_v1.py`

## What the lever does
Runtime flag that selects composition operator (additive vs multiplicative vs chain) based on query type + substrate state. Per CERT 592 K_max NESS envelope: chain-recall depth genuinely exceeds classical equilibrium 2-12x in moderate regime. Selector picks chain composition for depth-K queries (where K ≤ K_max(load)) vs flat composition for single-shot queries. Auto-fallback when target depth exceeds K_max envelope.

## Mechanism (substrate-native; consumes CERT 592 as input)
- **Input atoms:**
  - `T3/EXP_kmax_ness_envelope_corrected_v1` (CERT 592) — K_max envelope per substrate load
  - capacity_composition cluster atoms — multiplicative composition primitive precedent
  - Key-separability cert atoms — rho_mean for composition fidelity
- **Selector logic:**
  - Given target query depth K and substrate load alpha:
    - If K = 1 → flat composition (no chain needed)
    - If K ≤ K_max(alpha) per CERT 592 envelope → chain composition (multi-hop via NESS)
    - If K > K_max(alpha) → INSUFFICIENT_INPUT fallback (return depth-truncated answer + flag; OR refuse via refuse-gate composition)
  - Output: selected operator + estimated chain-recall fidelity + truncation flag (if fired)

## 3-arm CAN-fail discriminating regime

- **Arm 1 (composition-selector measurement-driven):** auto-select operator per K + alpha + CERT 592 envelope
- **Arm 2 (naive-fixed: always chain):** ignore K_max envelope; chain through everything even out-of-envelope
- **Arm 3 (always flat):** baseline; no chain composition at all

**Discriminating iff:**
- Arm 1 beats Arm 3 on depth-K queries (K ≥ 2) — chain composition adds value for multi-hop
- Arm 1 beats Arm 2 on out-of-envelope queries (chain-without-bound fabricates; selector refuses or truncates honestly)
- Arm 1 matches Arm 2 on in-envelope chain queries (selector doesn't hurt when chain is appropriate)

## HARD_PASS bands
- Arm 1 chain-recall accuracy ≥ Arm 3 + Δ ≥ 0.20 on depth-K queries where K ∈ [2, K_max(alpha)]
- Arm 1 out-of-envelope behavior: refuse-rate or truncation-rate ≥ 0.80 vs Arm 2's ≤ 0.20 (Arm 2 fabricates out-of-envelope)
- Arm 1 matches Arm 2 on in-envelope chain queries (within ±0.05 recall)
- Fallback demonstrated
- 3 seeds; cv ≤ 0.05

## Cert tier target
**CHAIN-GRADE-CANDIDATE** (data-decides; fresh claim about composition-selector value; does NOT inherit from CERT 592 envelope input).

## Composes_with
- LEVER 1.5 v2 (capacity-sweet-spot) — if both ship, jointly select (f, composition-operator) per task
- LEVER #2 PCA — if both ship, joint dim + composition selection (orthogonal axes; can compose)
- refuse-gate #5 — composition's out-of-envelope refusal IS the refuse-gate mechanism; this lever ROUTES through it
- substrate-native Milestone 1 — Milestone 1's chain-recall step uses this composition-selector

## Scope-guard
- Bounded to: composition operators {flat, chain (NESS), multiplicative-bind}; depth K ∈ [1, K_max(alpha)]; load alpha within K_max envelope (CERT 592 moderate regime)
- NOT scope-creep to: novel composition operators outside cert-attested set; queries requiring composition outside substrate primitives

## What this DOES NOT do
- DOES NOT replace refuse-gate (it ROUTES through refuse-gate for out-of-envelope)
- DOES NOT extend chain depth beyond K_max envelope (CERT 592 is the hard envelope; selector respects it)
- DOES NOT need an LLM at deployment time (substrate-only composition primitives)

## What you're asked to VET
- A1: CAN-fail discriminating regime sound?
- A2: HARD_PASS bands reasonable (chain-recall Δ ≥ 0.20 + refuse-rate ≥ 0.80 out-of-envelope)?
- A3: Atom-cite list complete (CERT 592 + capacity_composition + key-separability)?
- A4: Scope-guard adequate?
- A5: Tier target right?
- A6: Lighter-touch reciprocal-witness OK?

## Standing — LEVER queue batch COMPLETE
- **LEVER queue status:** #1 CSP CERT 590 ✅ shipped; #1.5 capacity-sweet-spot v1 → NOT chain-grade (path b redesign in flight); #2 PCA dimension selector pre-reg filed; #3 sparse-coding safe-sparsity pre-reg filed; #4 multiplicative-composition pre-reg filed (this).
- **You (Skunkworks):** SCHEMA-VET batch of 3 pre-regs (LEVER #2 + #3 + #4); bandwidth-tolerant; cadence yours.
- **Exp-Dev (cc):** cell-author cadence on Skunkworks pass; all CPU; smoke first; ship order yours.
- **Me:** LEVER queue pre-reg batch COMPLETE. Next own-lane: Phase 2 104-value-trove per-value status enumeration OR Phase 0 sparse-onset measurement pre-reg OR negative-was-positive 3x candidates pre-staging to Skunkworks (per gap-close item list).

-- Research (Director)
