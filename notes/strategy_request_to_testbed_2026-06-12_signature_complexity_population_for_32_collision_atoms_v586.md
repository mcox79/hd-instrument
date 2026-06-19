# strategy_request: Testbed signature+complexity field population for 32 collision atoms (PP-408 RESCUE-2)

**From:** verdict_handler (cap_map v586 cycle 248)
**To:** Testbed session (pick on own cadence per 4-session architecture)
**Date:** 2026-06-12
**Anchor:** substrate_codebook_near_duplicate_diagnostic_cpu_v1 (PP-408 HARD_PASS)

## Context

PP-408 v586 empirically vindicates the encoding-discriminability lever: dedup K=241->209 (32 atoms merged at cos>0.95) recovers cleanup F1 and F3 to PERFECT 1.0000 (F3 lift +0.1704 = 3.4x pre-reg HP bar). Root cause: `signature` and `complexity` fields are 0-populated on ALL 280 atoms; the algebra-HRR encoder has no field to express distinction between same-`algebra_category` atoms. Dedup is the DESTRUCTIVE upper-bound demonstration; signature/complexity field population is the NON-DESTRUCTIVE production fix.

## The 32 collision atoms (enumerated from PP-408 metrics)

49 near-duplicate pairs at cos>=0.99; key clusters:

1. **math::T1/probability_space <-> math::T1/measure_space** (cos=1.0 exact) -- distinct measure-theoretic concepts encoded identically.
2. **math::T1/matrix <-> math::T1/matrix_norms** (cos=1.0) -- object vs operator-on-object collision.
3. **math::T1/cauchy_sequence <-> math::T3/euclidean_distance** (cos=1.0) -- cross-tier collision (T1 algebra vs T3 metric).
4. **concept::MWP/ROLE_ARG0_agent <-> ROLE_ARG1_theme <-> ROLE_ARG2_recipient** (all 3 mutually cos=1.0) -- substrate CANNOT distinguish agent/theme/recipient via algebra-HRR retrieval.

Full pair list available in `data/exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1/metrics.json` under `per_seed[0].top_colliding_pairs`.

## Request

Design + ship a Testbed primitive that populates `signature` (and optionally `complexity`) fields on the 32 enumerated collision atoms, then re-measures cleanup F1+F3 on the previously-colliding subset.

### Minimal viable schema (suggested; Testbed owns final design)

- `signature` field: structural distinguisher derived from atom-content (e.g., operator-sequence-hash for math atoms; role-position-index for MWP role atoms).
- `complexity` field: nesting-depth or operator-count scalar.

These fields would be bound into the algebra-HRR vector alongside the existing role-filler bundle, expanding the encoded representation by 2 dimensions (or 2 bound-slots) that DIFFERENTIATE the 32 collision atoms while preserving the clustering geometry for genuinely-similar atoms.

### Pre-reg HP gate

- Cleanup F1 on the 32-collision-atom subset: >=0.95 (currently 0.8667 with 0-populated fields; dedup achieves 1.0000 upper bound).
- Cleanup F3 on the 32-collision-atom subset: >=0.93 (currently 0.8296; dedup achieves 1.0000).
- Honest reporting: per-pair cleanup pass/fail breakdown on the 49 cos>0.99 pairs (don't average over non-colliding atoms which already pass).

### Cross-axis confirmation (deferred to follow-on cell)

If RESCUE-2 PASSes, RESCUE-4 ships the same signature-populated atoms to:
- MWP operand-selection cell (HP role-disambiguation lift >=+0.10).
- A-axis retrieval cell (HP A-axis lift >=+0.05 toward PP-401 path-to-HP_v1 0.70).

## Sequencing note

This routing is INDEPENDENT of the v585 UNION-B/C ship routing (Testbed picks both on own cadence). RESCUE-2 + UNION-B/C are orthogonal interventions: encoding-discriminability operates at the per-atom encoding level; UNION operates at the retrieval-aggregation level. They compose multiplicatively but should be measured separately first.

## Cross-references

- cap_map v586 entry: PP-408 + PP-406/PP-407 mechanism-resolution annotation.
- v584 CSLS HARD_FAIL verdict: 1st appearance of encoding-not-rerank rule (negative refutation).
- v582 PP-406/PP-407: clustered-codebook ceiling positioning (this rescue closes the path-to-strict-HP).
- USER SHARES_MATH memory note 2026-06-12: architectural insight EMPIRICALLY VINDICATED by the 32 collision atoms.
- Free-probability drill (in flight): testable Gram-eigenvalue clumping prediction supplied by PP-408.

Status: routing written to disk; NOT auto-dispatched; Testbed picks on own cadence.
