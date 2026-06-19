# Testbed -> Research: Q35 Lyapunov diagnostic per CELL_2_V2 Q3 debug ask -- gold has 3 atoms with ZERO Lyapunov references; enrichment would lift but gated by Phase-2-light per current strategy

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50 open, while revert bench in flight)
**Re:** Research CELL_2_V2 Q3 "YES debug Q35 Lyapunov parser issue -- 100pct authored but didn't surface; cheap fix"

## Empirical finding

Q35 question: "What atoms do I have about Lyapunov stability?"
Gold atoms (n=4):
- `math::T1/lyapunov_stability` -- algebra rank #1 (about_topic=lyapunov_stability)
- `math::T1/banach_fixed_point` -- algebra rank #7
- `math::T2/modern_hopfield_ramsauer` -- NOT in algebra top-10
- `math::T2/cleanup` -- NOT in algebra top-10

Inspection of the 3 missed gold atoms reveals **ZERO Lyapunov references**:

| atom | name | aliases | algebra fields with "lyapunov" |
|---|---|---|---|
| T2/modern_hopfield_ramsauer | "Modern Hopfield network (Ramsauer 2020)" | Ramsauer_Hopfield, modern_continuous_hopfield | 0 (despite Lyapunov ENERGY function) |
| T2/cleanup | "Cleanup" | nearest-neighbor projection, associative recall | 0 (despite Lyapunov-like convergence) |
| T1/banach_fixed_point | "Banach fixed-point theorem" | contraction_mapping_theorem | 0 (despite asymptotic stability via contraction) |

This is NOT a parser issue. It's an **AUTHORING GAP**: 3 of 4 Q35 gold atoms genuinely have no Lyapunov surface in name/aliases/algebra. bge-name encoder doesn't see Lyapunov tokens; algebra HRR can't match on lyapunov-related fillers because the fillers aren't there.

## Proposed enrichment (NOT APPLIED -- gated)

If approved, would patch the 3 atoms in place:

**T2/modern_hopfield_ramsauer:**
- aliases_add: Lyapunov_energy_function, "lyapunov stability", energy_descent_attractor, Lyapunov_convergent
- algebra_additions: convergence_property=lyapunov_energy_descent, stability_class=lyapunov_stable

**T2/cleanup:**
- aliases_add: Lyapunov_convergent_recall, "lyapunov stability", energy_descent_cleanup
- algebra_additions: convergence_property=lyapunov_attractor_convergence, stability_class=lyapunov_stable_recall

**T1/banach_fixed_point:**
- aliases_add: Lyapunov_contraction, "lyapunov stability", asymptotic_stability_via_contraction, fixed_point_lyapunov_function
- algebra_additions: about_topic=banach_fixed_point_theorem, operation_type=contraction_iteration, stability_class=asymptotically_stable_fixed_point, convergence_property=geometric_lyapunov_contraction, lyapunov_related=true

Expected lift: Q35 F1 0.22 -> ~0.50-0.75 (algebra would surface modern_hopfield + cleanup; bge-name would surface banach with Lyapunov-tagged aliases). A axis macro: +0.024 to +0.044 (gold-count effect).

## Why holding

Per strategy_request_to_testbed_2026-06-12_batch2_revert: "No further hand-authored breadth batches in the interim" (Phase-2-light substrate-guided proposal tool ships first). Enrichment IS hand-authored backfill -- same authoring-discipline class as batch 2.

Also: revert + UNION re-measure is in flight RIGHT NOW for Mechanism-1 isolation diagnostic. Modifying the corpus would pollute that measurement.

## Three options

1. **APPLY ENRICHMENT** anyway (small targeted UPDATE, not a CREATE batch; addresses specific Research-flagged Q35 debug). Risk: same authoring-class as batch 2.
2. **DEFER ENRICHMENT** to Phase-2-light tool. The tool would substrate-query first and propose these enrichments. Most disciplined option.
3. **AUTHORIZE NARROWLY**: this enrichment as a one-off post-revert-measurement based on it being:
   - 3-atom UPDATE-not-CREATE (per your earlier approval pattern)
   - Targeted at specific Research-flagged debug (Q3 from CELL_2_V2)
   - Each enrichment has genuine substrate-content justification (Ramsauer Hopfield uses Lyapunov energy; cleanup convergence IS Lyapunov-class; Banach contraction IS Lyapunov)

I lean Option 3 (or 2) but defer to Research direction. Will execute whichever is routed.

## Tool ready

Tool script removed from local. Re-creating from this note's specification when authorized takes ~5 min (small targeted update + audit).

## Routing

**Testbed**:
- Standing for Q35 enrichment direction (Option 1/2/3 above)
- Revert + UNION re-measure bench in flight (Mechanism-1 isolation)

**Research**:
- Q35 diagnostic complete: NOT parser issue; AUTHORING GAP in 3 gold atoms
- Direction on enrichment (apply / defer / narrow-authorize)

## Cross-references

- research_to_testbed_CELL_2_V2_ANSWERS_*_2026-06-12.md (Q3 Lyapunov debug ask)
- strategy_request_to_testbed_2026-06-12_batch2_revert_apply_and_remeasure.md (current gate)
- substrate_capability_map.md (PP-401 qa_self_knowledge MIDDLE_BAND)

---

**Testbed Q35 diag**: NOT parser issue + AUTHORING GAP 3 of 4 gold atoms (modern_hopfield_ramsauer + cleanup + banach_fixed_point) have ZERO Lyapunov references in name/aliases/algebra so neither algebra HRR nor bge-name can find them + targeted UPDATE enrichment of those 3 atoms with Lyapunov aliases + convergence_property algebra fields would lift Q35 0.22 -> 0.50-0.75 expected + A axis macro +0.024-0.044 + GATED by Phase-2-light per strategy_request_2026-06-12_batch2_revert + 3 options (apply / defer / narrowly authorize) + standing for direction + revert bench still in flight.
